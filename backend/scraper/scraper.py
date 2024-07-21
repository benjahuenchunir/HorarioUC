import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from backend.database.tables import CourseDTO, SectionDTO
import global_constants as c
import json
from icecream import ic

class Scraper:
    def __init__(self):
        super().__init__()

    def find_course_info(self, course_id, year, period) -> tuple[CourseDTO, list[SectionDTO]] | None:
        url = f"https://buscacursos.uc.cl/?cxml_semestre={year}-{period}&cxml_sigla={course_id}&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
        courses_dict = self.parse_url(url)
        return courses_dict.get(course_id, None)

    def parse_url(self, url) -> dict[str,  tuple[CourseDTO, list]]:
        courses: dict[str, tuple[CourseDTO, list]] = {}
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find(
            "table",
            attrs={
                "width": "100%",
                "cellpadding": "3",
                "cellspacing": "1",
                "border": "0",
            },
        )

        if table is None:
            return courses
        rows = table.find_all("tr", class_=["resultadosRowImpar", "resultadosRowPar"])

        for row in rows:
            cells = row.find_all("td")
            nrc = int(cells[0].text.strip())
            sigla = cells[1].text.strip()
            en_ingles = c.STRING_TO_BOOL[cells[3].text.strip()]
            section = int(cells[4].text.strip())
            formato = cells[7].text.strip()
            name = cells[9].text.strip()
            teacher = cells[10].text.strip()
            campus = cells[11].text.strip()
            schedules = cells[16].table.find_all("tr")
            schedule_data = {tipo: defaultdict(list) for tipo in c.TIPOS_CLASES}
            for schedule in schedules:
                schedule_cells = schedule.find_all("td")
                tipo = schedule_cells[1].text.strip()
                horario = schedule_cells[0].text.strip()
                dias, modulos_ = horario.split(":")
                if dias == "" or modulos_ == "":
                    continue
                for dia in dias.split("-"):
                    modulos = map(int, modulos_.split(","))
                    if tipo in c.TIPOS_CLASES:
                        schedule_data[tipo][dia].extend(modulos)
                    else:
                        # TODO raise error
                        print(sigla)
                        print(tipo)
            if sigla not in courses:
                permite_retiro = c.STRING_TO_BOOL[cells[2].text.strip()]
                aprob_especial = c.STRING_TO_BOOL[cells[5].text.strip()]
                area = cells[6].text.strip()
                creditos = int(cells[12].text.strip())
                ajax_url = 'https://buscacursos.uc.cl/' + cells[1].get('rel')
                ajax_response = requests.get(ajax_url)
                tooltip_soup = BeautifulSoup(ajax_response.text, "html.parser")
                tooltip = tooltip_soup.find("div", style="height:116px;overflow:auto;")
                courses[sigla] = (CourseDTO(
                    id=-1,
                    sigla=sigla,
                    nombre=name,
                    aprob_especial=aprob_especial,
                    permite_retiro=permite_retiro,
                    area=area,
                    creditos=creditos,
                    descripcion=tooltip.text.strip(),
                ), [])
            courses[sigla][-1].append(
                SectionDTO(
                    id_curso=-1,
                    seccion=section,
                    nrc=nrc,
                    profesor=teacher,
                    campus=campus,
                    en_ingles=en_ingles,
                    horario=json.dumps(schedule_data),
                    formato=formato,
                )
            )
        return courses
    
    def download_course_program_and_requirements(self, sigla):
        requisitos_response = requests.get(f"https://catalogo.uc.cl/index.php?tmpl=component&option=com_catalogo&view=requisitos&sigla={sigla}")
        programa_response = requests.get(f"https://catalogo.uc.cl/index.php?tmpl=component&option=com_catalogo&view=programa&sigla={sigla}")

        # Parse requisitos
        soup = BeautifulSoup(requisitos_response.text, 'html.parser')
        table = soup.find('table', attrs={'class':'tablesorter tablesorter-blue'})
        rows = table.find_all('tr')

        data = {}
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data[cols[0]] = cols[1]

        with open(f"{c.PATH_REQUISITOS}/{sigla}.txt", "w", encoding='utf-8') as f:
            for key, value in data.items():
                f.write(f"{key}: {value}\n")

        # Parse programa
        soup = BeautifulSoup(programa_response.text, 'html.parser')
        pre_text = soup.find('pre').get_text()

        # Split the text by double newlines to separate the sections
        sections = pre_text.split('\n\n')

        info = sections[0]
        description = "\n".join(sections[1:])

        with open(f"{c.PATH_PROGRAMAS}/{sigla}.txt", "w", encoding='utf-8') as f:
            f.write(f"{info}\n\n {description}")
        
if __name__ == "__main__":
    l = Scraper()
    print(l.find_course_info("MAT1630"))
    
