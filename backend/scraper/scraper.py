import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from icecream import ic
from backend.database.tables import CourseDTO, SectionDTO
import global_constants as c
import backend.scraper.constants as p
import json


class Scraper:
    def __init__(self):
        super().__init__()

    def find_course_info(self, course_id) -> tuple[CourseDTO, list[SectionDTO]] | None:
        url = f"https://buscacursos.uc.cl/?cxml_semestre=2023-2&cxml_sigla={course_id}&cxml_nrc=&cxml_nombre=&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados"
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
        # TODO creo que esto falla si no hay cursos
        rows = table.find_all("tr", class_=["resultadosRowImpar", "resultadosRowPar"])

        for row in rows:
            cells = row.find_all("td")
            nrc = int(cells[0].text.strip())
            sigla = cells[1].text.strip()
            permite_retiro = p.STRING_TO_BOOL[cells[2].text.strip()]
            en_ingles = p.STRING_TO_BOOL[cells[3].text.strip()]
            section = int(cells[4].text.strip())
            aprob_especial = p.STRING_TO_BOOL[cells[5].text.strip()]
            area = cells[6].text.strip()
            formato = cells[7].text.strip()
            name = cells[9].text.strip()
            teacher = cells[10].text.strip()
            campus = cells[11].text.strip()
            creditos = int(cells[12].text.strip())
            schedules = cells[16].table.find_all("tr")
            catedra = defaultdict(list)
            ayudantia = defaultdict(list)
            lab = defaultdict(list)
            taller = defaultdict(list)
            for schedule in schedules:
                schedule_cells = schedule.find_all("td")
                tipo = schedule_cells[1].text.strip()
                horario = schedule_cells[0].text.strip()
                dias, modulos_ = horario.split(":")
                if dias == "" or modulos_ == "":
                    continue
                for dia in dias.split("-"):
                    modulos = map(int, modulos_.split(","))
                    if tipo == c.SIGLA_CATEDRA:
                        catedra[dia].extend(modulos)
                    elif tipo == c.SIGLA_LAB:
                        lab[dia].extend(modulos)
                    elif tipo == c.SIGLA_AYUDANTIA:
                        ayudantia[dia].extend(modulos)
                    elif tipo == c.SIGLA_TALLER:
                        taller[dia].extend(modulos)
                    else:
                        print(sigla)
                        print(tipo)
            if sigla not in courses:
                courses[sigla] = (CourseDTO(
                    id=-1,
                    sigla=sigla,
                    nombre=name,
                    aprob_especial=aprob_especial,
                    permite_retiro=permite_retiro,
                    area=area,
                    creditos=creditos,
                    descripcion="",
                ), [])
            courses[sigla][-1].append(
                SectionDTO(
                    id_curso=-1,
                    seccion=section,
                    nrc=nrc,
                    profesor=teacher,
                    campus=campus,
                    en_ingles=en_ingles,
                    horario=json.dumps({
                        c.SIGLA_CATEDRA: catedra,
                        c.SIGLA_LAB: lab,
                        c.SIGLA_AYUDANTIA: ayudantia,
                        c.SIGLA_TALLER: taller
                    }),
                    formato=formato,
                )
            )
        return courses


if __name__ == "__main__":
    l = Scraper()
    l.find_course_info("MAT1630")
