import requests
from bs4 import BeautifulSoup
import parametros as p
from collections import defaultdict
from itertools import product, groupby
from operator import attrgetter
from PyQt5.QtCore import QObject, pyqtSignal


class Course:
    def __init__(self, id):
        self.id = id
        self.sections = []

    def __repr__(self) -> str:
        return f"Sigla: {self.id}, Catedra: {self.catedra}, Ayudantia: {self.ayudantia}, Lab: {self.lab}"


class Section:
    def __init__(
        self,
        nrc,
        section,
        name,
        teacher,
        catedra: defaultdict,
        ayudantia: defaultdict,
        lab: defaultdict,
    ):
        self.nrc = nrc
        self.section = section
        self.name = name
        self.teacher = teacher
        self.catedra = dict(catedra)
        self.ayudantia = dict(ayudantia)
        self.lab = lab


class GroupedSection:
    def __init__(
        self, id, name, catedra: defaultdict, ayudantia: defaultdict, lab: defaultdict
    ) -> None:
        self.id = id
        self.name = name
        self.nrcs = []
        self.sections = []
        self.teachers = []
        self.catedra = dict(catedra)
        self.ayudantia = dict(ayudantia)
        self.lab = lab


class Logic(QObject):
    senal_add_course = pyqtSignal(object)
    senal_update_schedule = pyqtSignal(list)
    senal_borrar_curso = pyqtSignal(str)
    senal_update_ofgs = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.courses = {}
        self.ofgs = {}
        self.sections = {}
        self.tope_lab = False # TODO 
        self.tope_ayudantia = True
        self.current_combination = []

    def find_course_info(self, course_id):
        course = self.scrape_course_schedule(course_id)
        grouped_sections = self.group_courses_by_dict(course)
        self.courses[course_id] = grouped_sections
        self.sections[course_id] = p.TODAS
        self.senal_add_course.emit(course)
        self.update_schedule()

    def update_schedule(self):
        self.senal_update_schedule.emit(self.generate_course_combinations(self.courses.values()))

    def scrape_course_schedule(self, course_id):
        course = Course(course_id)
        url = f"https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla={course_id}&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find(
            "table",
            attrs={"width": "100%", "cellpadding": "3", "cellspacing": "1", "border": "0"},
        )
        rows = table.find_all("tr", class_=["resultadosRowImpar", "resultadosRowPar"])

        for row in rows:
            cells = row.find_all("td")
            nrc = cells[0].text.strip()
            section = cells[4].text.strip()
            name = cells[9].text.strip()
            teacher = cells[10].text.strip()
            schedules = cells[16].table.find_all("tr")
            catedra = defaultdict(list)
            ayudantia = defaultdict(list)
            lab = defaultdict(list)
            for schedule in schedules:
                schedule_cells = schedule.find_all("td")
                tipo = schedule_cells[1].text.strip()
                horario = schedule_cells[0].text.strip()
                dias, modulos_ = horario.split(":")
                for dia in dias.split("-"):
                    modulos = map(int, modulos_.split(","))
                    if tipo == p.CATEDRA:
                        catedra[dia].extend(modulos)
                    elif tipo == p.LAB:
                        lab[dia].extend(modulos)
                    elif tipo == p.AYUDANTIA:
                        ayudantia[dia].extend(modulos)
            course.sections.append(
                Section(
                    nrc,
                    section,
                    name,
                    teacher,
                    catedra.copy(),
                    ayudantia.copy(),
                    lab.copy(),
                )
            )
        return course

    def section_key(self, section):
        catedra = tuple(sorted(section.catedra.items()))
        ayudantia = tuple(sorted(section.ayudantia.items()))
        lab = tuple(sorted(section.lab.items()))
        return (catedra, ayudantia, lab)

    def group_courses_by_dict(self, course):
        course.sections.sort(key=self.section_key)

        final_list = []
        for key, courses in groupby(
            course.sections, key=attrgetter("catedra", "ayudantia", "lab")
        ):
            grouped_section = GroupedSection(course.id, course.sections[0].name, key[0], key[1], key[2])
            for section in courses:
                grouped_section.nrcs.append(section.nrc)
                grouped_section.sections.append(section.section)
                grouped_section.teachers.append(section.teacher)
            final_list.append(grouped_section)
        return final_list.copy()

    def are_courses_valid(self, combination):
        schedule_per_day = {}
        for course in combination:  # Catedra con catedra
            for key, value in course.catedra.items():
                if key not in schedule_per_day:
                    schedule_per_day[key] = value.copy()
                else:
                    if any(val in schedule_per_day[key] for val in value):
                        return False
                    else:
                        schedule_per_day[key].extend(value.copy())
        if not self.tope_lab:
            for i, course in enumerate(combination):  # Catedra con lab
                for key, modules in course.catedra.items():
                    for j, other_course in enumerate(combination):
                        if i != j and key in other_course.lab and any(val in other_course.lab[key] for val in modules):
                            return False
        if not self.tope_ayudantia:
            for i, course in enumerate(combination):  # Catedra con ayudantia
                for key, modules in course.catedra.items():
                    for j, other_course in enumerate(combination):
                        if i != j and key in other_course.ayudantia and any(val in other_course.ayudantia[key] for val in modules):
                            return False
        return True

    def generate_course_combinations(self, courses):
        # Convert the dictionary values to lists of courses
        filtered_courses = []
        for grouped_sections in courses:
            filtered_section = self.sections.get(grouped_sections[0].id, None)
            if filtered_section == p.TODAS or filtered_section == None:
                filtered_courses.append(grouped_sections)
            else:
                for section in grouped_sections:
                    if str(filtered_section) in section.sections:
                        filtered_courses.append([section])
                        break
        # print(course_lists)

        # Generate all possible combinations of courses
        all_combinations = product(*filtered_courses)

        # Filter out the valid combinations
        valid_combinations = [
            combination
            for combination in all_combinations
            if self.are_courses_valid(combination)
        ]

        return valid_combinations

    def delete_course(self, course_id):
        del self.courses[course_id]
        del self.sections[course_id]
        self.senal_borrar_curso.emit(course_id)
        self.update_schedule()

    def filter_course_section(self, course_id, index):
        self.sections[course_id] = index
        self.update_schedule()

    def change_ofg_area(self, area):
        combinaciones_final = []
        self.search_ofgs(area)
        for key, course in self.ofgs.items():
            self.ofgs[key] = self.group_courses_by_dict(course)
        for id, grouped_sections in self.ofgs.items():
            combinations = self.generate_course_combinations(self.current_combination + [grouped_sections])
            if combinations:
                combinaciones_final.append((id, combinations))
        self.senal_update_ofgs.emit(combinaciones_final)

    def search_ofgs(self, area):
        self.ofgs.clear()
        print(area)
        url = f"https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla=&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg={p.OFG[area]}&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find(
            "table",
            attrs={"width": "100%", "cellpadding": "3", "cellspacing": "1", "border": "0"},
        )
        rows = table.find_all("tr", class_=["resultadosRowImpar", "resultadosRowPar"])

        for row in rows:
            cells = row.find_all("td")
            sigla = cells[1].text.strip()
            nrc = cells[0].text.strip()
            section = cells[4].text.strip()
            name = cells[9].text.strip()
            teacher = cells[10].text.strip()
            schedules = cells[16].table.find_all("tr")
            catedra = defaultdict(list)
            ayudantia = defaultdict(list)
            lab = defaultdict(list)
            for schedule in schedules:
                schedule_cells = schedule.find_all("td")
                tipo = schedule_cells[1].text.strip()
                horario = schedule_cells[0].text.strip()
                dias, modulos_ = horario.split(":")
                for dia in dias.split("-"):
                    modulos = map(int, modulos_.split(","))
                    if tipo == p.CATEDRA:
                        catedra[dia].extend(modulos)
                    elif tipo == p.LAB:
                        lab[dia].extend(modulos)
                    elif tipo == p.AYUDANTIA:
                        ayudantia[dia].extend(modulos)
            final_section = Section(
                    nrc,
                    section,
                    name,
                    teacher,
                    catedra.copy(),
                    ayudantia.copy(),
                    lab.copy(),
                )
            if sigla not in self.ofgs:
                self.ofgs[sigla] = Course(sigla)
            self.ofgs[sigla].sections.append(final_section)


if __name__ == "__main__":
    """programacion = scrape_course_schedule("IIC1103")
    edo = scrape_course_schedule("MAT1640")
    dic = {"IIC1103": programacion, "MAT1640": edo}
    combinations = generate_course_combinations(dic)
    for combinacion in combinations:
        print(combinacion)
    print(len(combinations))"""
    ...
