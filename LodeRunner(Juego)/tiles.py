import csv       # Para leer los archivos CSV que definen la disposición de los tiles
import util      # Módulo con funciones auxiliares (p.ej. util.index para convertir coordenadas)
import os        # Para manejar rutas de archivos (os.path.join al cargar niveles)
from drawable import Drawable  # Clase base que define cómo dibujar y mover objetos en pantalla


class Tile(Drawable):
    # Mapa 2D del nivel almacenado como lista plana
    level = []

    # Asociar cada valor de CSV a la clase correspondiente
    tile_map = {
        # '0': Empty,
        # '1': Brick,
        # '2': Ladder,
        # '3': Rope,
        # '4': Gold,
        # '5': HiddenLadder
    }

    _hidden_tiles = []  # Lista de tiles ocultos (p.ej. escaleras ocultas)

    @staticmethod
    def load_level(num):
        """
        Carga el nivel número `num` desde un archivo CSV.
        Cada celda del CSV se convierte en un objeto Tile según tile_map.
        """
        path = os.path.join('levels', f'level{num}.csv')
        with open(path) as file_data:
            Tile.level = []
            row_num = 0
            for row in csv.reader(file_data):
                # Para cada elemento en la fila, instancia el tile correspondiente
                Tile.level.extend([
                    Tile.tile_map[elem]((index, row_num)) 
                    if elem in Tile.tile_map 
                    else Empty((index, row_num))  # Por defecto, Empty si no está en tile_map
                    for index, elem in enumerate(row)
                ])
                row_num += 1

    @staticmethod
    def query(coord, property):
        """
        Devuelve el valor de `property` para el tile en coordenada `coord`.
        Utiliza util.index(x, y) para convertir coordenadas 2D a índice en la lista.
        """
        tile = Tile.level[util.index(*coord)]
        return tile.properties[property]

    @staticmethod
    def tile_at(coord):
        """
        Retorna el tile (objeto) que se encuentra en la coordenada `coord`.
        """
        return Tile.level[util.index(*coord)]

    @staticmethod
    def clear(coord):
        """
        Elimina (undraw) el tile en `coord` y lo reemplaza por un Empty.
        Usado, por ejemplo, cuando el jugador cava un ladrillo o toma una moneda.
        """
        idx = util.index(*coord)
        Tile.level[idx].undraw()
        Tile.level[idx] = Empty(coord)

    def __init__(self, coord, img_path=None, properties={}, hidden=False):
        """
        Constructor base de Tile. Recibe:
        - coord: tupla (x, y) de la posición en la cuadrícula.
        - img_path: ruta a la imagen (PNG) que representa este tile.
        - properties: diccionario con propiedades (passable, standable, etc.).
        - hidden: si True, el tile se crea pero no se dibuja hasta que se muestre.
        """
        super(Tile, self).__init__(coord, img_path)
        if not hidden:
            self.draw()  # Dibuja en pantalla si no está oculto

        # Propiedades por defecto de un tile
        self.properties = {
            'passable':  True,
            'takable':   False,
            'standable': False,
            'climbable': False,
            'grabbable': False,
            'diggable':  False
        }

        # Sobreescribe solo las propiedades definidas en el argumento
        for key in properties:
            if key in self.properties:
                self.properties[key] = properties[key]

        self.coord = coord  # Guarda coordenada en la cuadrícula

        if hidden:
            self.hide()  # Si se pide oculto, se oculta inmediatamente

    def hide(self):
       
        self.hidden_properties = self.properties
        # Al ocultar, el tile deja de impactar en la jugabilidad salvo como pasable
        self.properties = {
            'passable':  True,
            'takable':   False,
            'standable': False,
            'climbable': False,
            'grabbable': False,
            'diggable':  False
        }
        self.undraw()

    def show(self):
        """
        Muestra el tile previamente oculto: vuelve a dibujarlo y
        restituye las propiedades que tenía antes de ocultarse.
        """
        self.draw()
        self.properties = self.hidden_properties

    def take(self):
        # Método genérico para tomar/usar el tile; se sobreescribe en subclases (p.ej. Gold).
        pass


class Empty(Tile):
  
    def __init__(self, coord):
        super(Empty, self).__init__(coord)
        # No se pasa img_path ni properties, hereda comportamientos neutros


class Brick(Tile):
    """
    Ladrillo que bloquea el paso, se puede pararse sobre él y se puede cavar (diggable).
    """
    def __init__(self, coord):
        properties = {
            'passable':   False,  # No se puede atravesar
            'standable':  True,   # El jugador puede pararse encima
            'diggable':   True    # Se puede cavar (y convertir en Empty)
        }
        super(Brick, self).__init__(coord, 'brick.png', properties)


class Ladder(Tile):
    """
    Escalera: permite que el jugador suba o baje. También se puede “agarrar”.
    Puede crearse oculta (p.ej. HiddenLadder hereda de esta clase con hidden=True).
    """
    def __init__(self, coord, hidden=False):
        properties = {
            'standable':  True,   # El jugador puede pararse en la parte superior
            'climbable':  True,   # Se puede subir/bajar por ella
            'grabbable': True     # Interacción de agarrar cuerda/escalera (si aplica)
        }
        super(Ladder, self).__init__(coord, 'ladder.png', properties, hidden)


class Rope(Tile):
    """
    Cuerda: el jugador puede agarrarse (grabbable), pero no se para sobre ella.
    """
    def __init__(self, coord):
        properties = {
            'grabbable': True  # Única propiedad relevante
        }
        super(Rope, self).__init__(coord, 'rope.png', properties)


class Gold(Tile):
    """
    Moneda de oro: el jugador puede recogerla. Lleva un contador
    global _num_gold para saber cuántas quedan en el nivel.
    """
    _num_gold = 0  # Contador estático de monedas restantes

    @staticmethod
    def all_taken():
        """
        Devuelve True si ya no quedan monedas en el nivel.
        """
        return Gold._num_gold <= 0

    def __init__(self, coord):
        Gold._num_gold += 1  # Incrementa contador al crearse
        properties = {
            'takable': True  # Se puede recoger
        }
        super(Gold, self).__init__(coord, 'gold.png', properties)

    def take(self):
        """
        Lógica de recolección: si la moneda es 'takable', la borra
        (se convierte en Empty), decrementa el contador y devuelve True.
        """
        if self.properties['takable']:
            Gold._num_gold -= 1
            Tile.clear(self.coord)
            return True
        return False  # No se pudo tomar (si ya no era takable por alguna razón)


class HiddenLadder(Ladder):
    """
    Escalera que inicia oculta y se guarda en la lista _hidden.
    Puede mostrarse todas juntas usando showAll().
    """
    _hidden = []

    @staticmethod
    def showAll():
        """
        Muestra todas las escaleras ocultas del nivel,
        restaurando sus propiedades originales.
        """
        for ladder in HiddenLadder._hidden:
            ladder.show()
        HiddenLadder._hidden = []

    def __init__(self, coord):
        super(HiddenLadder, self).__init__(coord, hidden=True)
        HiddenLadder._hidden.append(self)  # Se registra en la lista de ocultos


# Se define el diccionario tile_map al final para que las clases ya existan
Tile.tile_map = {
    '0': Empty,
    '1': Brick,
    '2': Ladder,
    '3': Rope,
    '4': Gold,
    '5': HiddenLadder
}


if __name__ == "__main__":
    # Prueba rápida: cargar el nivel 1 
    Tile.load_level(1)