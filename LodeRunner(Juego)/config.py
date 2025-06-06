import os, csv  # Importa los módulos os y csv para operaciones del sistema y lectura de CSV

class Config:
    """
    Clase que contiene configuraciones estáticas para el juego, como dimensiones del nivel y de la ventana.
    """

    LEVEL_WIDTH = 35  # Ancho predeterminado del nivel en número de celdas
    LEVEL_HEIGHT = 21  # Alto predeterminado del nivel en número de celdas

    CELL_SIZE = 35  # Tamaño en píxeles de cada celda

    WINDOW_WIDTH = CELL_SIZE * LEVEL_WIDTH  # Ancho de la ventana del juego en píxeles
    WINDOW_HEIGHT = CELL_SIZE * LEVEL_HEIGHT  # Alto de la ventana del juego en píxeles

    hidden_flag = False  # Bandera para controlar alguna funcionalidad de visibilidad, inicializada en False

    @staticmethod
    def config_level(num):
        """
        Configura las dimensiones del nivel y de la ventana basadas en el archivo CSV del nivel especificado.

        :param num: Número del nivel a cargar (por ejemplo, 1 para 'level1.csv')
        """
        # Construye la ruta al archivo CSV del nivel
        with open(os.path.join('levels', 'level{}.csv').format(num)) as file_data:
            row_num = 0  # Contador de filas
            for row in csv.reader(file_data):
                # Actualiza el ancho del nivel con la longitud de la fila
                # Nota: Esto asume que todas las filas tienen el mismo número de columnas
                Config.LEVEL_WIDTH = len(row)
                row_num += 1  # Incrementa el contador de filas
            Config.LEVEL_HEIGHT = row_num  # Establece el alto del nivel como el número de filas

        # Recalcula las dimensiones de la ventana basadas en el nuevo tamaño del nivel
        Config.WINDOW_WIDTH = Config.CELL_SIZE * Config.LEVEL_WIDTH
        Config.WINDOW_HEIGHT = Config.CELL_SIZE * Config.LEVEL_HEIGHT
        Config.hidden_flag = False  # Restablece la bandera a False