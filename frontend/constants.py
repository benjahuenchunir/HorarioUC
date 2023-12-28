from global_constants import SIGLA_CATEDRA, SIGLA_LAB, SIGLA_AYUDANTIA, SIGLA_TALLER, SIGLA_PRACTICA

DIAS = {"L": 0, "M": 1, "W": 2, "J": 3, "V": 4, "S": 5}
H_LABELS_HORARIO = [
    "8:20",
    "9:40",
    "11:00",
    "12:20",
    "Almuerzo",
    "14:50",
    "16:10",
    "17:30",
    "18:50",
]
COLORES = {
    SIGLA_CATEDRA: "#FBC575",
    SIGLA_LAB: "#B3D4F5",
    SIGLA_AYUDANTIA: "#99CC99",
    SIGLA_TALLER: "#C7C2F8",
    SIGLA_PRACTICA: "#CCCC99",
}

TODOS = "TODOS"
SAN_JOAQUIN = "San+Joaquín"
CASA_CENTRAL = "Casa+Central"
CREDITOS_10 = 10
CREDITOS_5 = 5

CAMPUS = [TODOS, SAN_JOAQUIN, CASA_CENTRAL]
CREDITOS = [TODOS, CREDITOS_10, CREDITOS_5]

BOOL_TO_STR = {1: "Si", 0: "No"}

LIGHT_MODE = """
            QWidget {
                font-family: Arial;
                font-size: 12px;
                background-color: #F0F0F0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                border: 2px solid gray;
                border-radius: 10px;
                padding: 0 8px;
                background: white;
                selection-background-color: darkgray;
            }
            QListWidget {
                background: white;
                border: 2px solid gray;
                border-radius: 10px;
            }
            QTableWidget {
                background: white;
                border: 2px solid gray;
                border-radius: 10px;
            }
            
        """

DARK_MODE = """
            QWidget {
                font-family: Arial;
                font-size: 12px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #5a5a5a;
            }
            QLineEdit {
                border: 2px solid #5a5a5a;
                border-radius: 5px;
                padding: 0 8px;
                background: #3a3a3a;
                color: #ffffff;
                selection-background-color: #6a6a6a;
            }
            QListWidget {
                background: #3a3a3a;
                border: 2px solid #5a5a5a;
                border-radius: 10px;
                color: #ffffff;
            }
            QTableWidget {
                background: #3a3a3a;
                border: 2px solid #5a5a5a;
                border-radius: 10px;
                color: #ffffff;
            }
            QLabel {
                background-color: #3a3a3a;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                padding: 4px;
            }
            QTableCornerButton::section {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
            }
            QAbstractItemView {
                background-color: #3a3a3a;
                color: #ffffff;
                selection-background-color: #5a5a5a;
            }
            QToolBar {
                background-color: #000;
            }
        """
        
PATH_ASSETS = "frontend/assets/"
PATH_BACK_ICON = PATH_ASSETS + "back_icon.png"
PATH_FILTER_ICON = PATH_ASSETS + "filter_icon.png"
PATH_MENU_ICON = PATH_ASSETS + "menu_icon.png"
PATH_LOAD_ICON = PATH_ASSETS + "load_icon.png"
PATH_DELETE_ICON = PATH_ASSETS + "delete_icon.png"