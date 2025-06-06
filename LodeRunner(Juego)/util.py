from config import Config  # Importa la configuración global del juego (ancho de nivel, tamaño de celda, etc.)

def index(x, y):
    """
    Convierte coordenadas (x, y) de la cuadrícula a un índice en la lista lineal del nivel.
    Fórmula: índice = x + (y * LEVEL_WIDTH)
    """
    return x + (y * Config.LEVEL_WIDTH)

def coord(index):
    """
    Convierte un índice en la lista lineal del nivel a coordenadas (x, y) en la cuadrícula.
    - x = índice % LEVEL_WIDTH
    - y = índice // LEVEL_WIDTH
    """
    return index % Config.LEVEL_WIDTH, index // Config.LEVEL_WIDTH

def screen_pos(x, y):
    """
    Calcula la posición en píxeles en la ventana gráfica a partir de coordenadas de celda.
    Cada celda mide CELL_SIZE píxeles, y se añade un offset de 10 píxeles para el borde.
    Retorna una tupla (px, py).
    """
    return (x * Config.CELL_SIZE + 10, y * Config.CELL_SIZE + 10)

def screen_pos_index(index):
    """
    Dado un índice en la lista lineal del nivel, convierte primero a coordenadas (x, y)
    y luego devuelve la posición en píxeles en la ventana gráfica.
    """
    x = index % Config.LEVEL_WIDTH
    y = (index - x) // Config.LEVEL_WIDTH
    return screen_pos(x, y)