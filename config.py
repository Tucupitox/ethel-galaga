import os

# Solución definitiva para las rutas de los archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filepath):
    # Asegura que siempre busque dentro de la carpeta del proyecto
    return os.path.join(BASE_DIR, filepath)

W = 800
H = 600

FONDOS_NIVELES = [get_path("imagenes/galaxia.jpg"), get_path("imagenes/tierra.png"), get_path("imagenes/marte.png")]

GATOS_DISPONIBLES = [
    get_path("imagenes/ethel.png"), 
    get_path("imagenes/vaquita.png"), 
    get_path("imagenes/naranja.png"), 
    get_path("imagenes/solecito.png"),
    get_path("imagenes/vladimiro.png")
]

NOMBRES_GATOS = [
    "ETHEL", 
    "VAQUITA", 
    "NARANJA", 
    "SOLECITO", 
    "VLADIMIRO"
]

# ESTADOS DEL JUEGO
MENU_PRINCIPAL = 0
SELECCION_GATO = 1
JUEGO = 2
GAME_OVER = 3
MENU_NIVELES = 4
PAUSA = 5  
NIVEL_COMPLETADO = 6