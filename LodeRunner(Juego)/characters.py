# Archivo: characters.py

# Archivo: characters.py

from drawable import Drawable 
from tiles import Tile, Empty
from event import Event
import csv, os
from config import Config

# Defino la clase base para los personajes del juego
class Character (Drawable):
    char_map = {}  # Diccionario para mapear caracteres del CSV a clases (como 'P' para Player)

    @staticmethod
    def load_characters(num):
        # Método estático para cargar personajes desde un archivo CSV que representa el nivel
        # 'num' es el número del nivel, por ejemplo, 'level1.csv'

        # Si ya existe un Player.main de un nivel anterior, quiero mantener sus vidas
        # pero resetear su posición para el nuevo nivel
        for baddie in list(Baddie.baddies):  # Hago una copia de la lista para poder modificarla mientras itero
            baddie.die()  # Elimino todos los baddies existentes
        Baddie.baddies = []  # Me aseguro de que la lista de baddies esté vacía

        player_loaded_this_level = False  # Bandera para evitar cargar múltiples jugadores en el mismo nivel

        # Abro el archivo CSV correspondiente al nivel
        with open(os.path.join('levels', 'level{}.csv').format(num)) as file_data:
            row_num = 0  # Contador de filas
            for row in csv.reader(file_data):  # Leo cada fila del CSV
                for col, value in enumerate(row):  # Itero sobre cada columna de la fila
                    if value in char_map_definition:  # Si el valor está en el diccionario de mapeo
                        if value == 'P':  # Si encuentro un 'P', es el jugador
                            if not player_loaded_this_level:  # Solo cargo un jugador por nivel
                                if Player.main is None:  # Si es el primer nivel o no hay jugador aún
                                    char_map_definition[value](col, row_num, is_initial_load=True)  # Creo un nuevo Player
                                else:  # Si el jugador ya existe (de un nivel anterior)
                                    Player.main.set_initial_pos(col, row_num)  # Actualizo su posición inicial
                                    Player.main.respawn(force_redraw_lives=True)  # Lo hago reaparecer en la nueva posición
                                player_loaded_this_level = True  # Marco que ya cargué al jugador
                        else:  # Si no es 'P', es otro personaje como un Baddie
                            char_map_definition[value](col, row_num)  # Creo la instancia correspondiente
                row_num += 1  # Incremento el contador de filas

        # Verifico si se cargó un jugador; si no, aviso que falta en el nivel
        if not Player.main:
            print(f"ADVERTENCIA: No se encontró 'P' (Player) en el archivo de nivel level{num}.csv")

    def __init__(self, x, y, img_path=None):
        # Inicializo un personaje en las coordenadas (x, y) con una imagen opcional
        super(Character, self).__init__((x, y), img_path)  # Llamo al constructor de Drawable
        self._x = x  # Guardo la posición x
        self._y = y  # Guardo la posición y
        # Nota: El dibujo lo manejan las subclases Player y Baddie después de su configuración

    def pos(self):
        # Devuelvo la posición actual del personaje como una tupla (x, y)
        return self._x, self._y

    def same_loc(self, x, y):
        # Compruebo si el personaje está en las coordenadas dadas
        return (self._x == x and self._y == y)

    def move(self, dx, dy):
        # Intento mover al personaje en la dirección (dx, dy)
        tx = self._x + dx  # Calculo la nueva posición x
        ty = self._y + dy  # Calculo la nueva posición y
        next_pos = (tx, ty)  # Posición tentativa

        # Verifico que la nueva posición esté dentro de los límites del nivel
        if 0 <= tx < Config.LEVEL_WIDTH and 0 <= ty < Config.LEVEL_HEIGHT:
            if Tile.query(next_pos, 'passable'):  # Chequeo si el tile destino es transitable
                # Si intento subir (dy < 0), necesito estar en un tile escalable o agarrable
                if dy < 0 and not (Tile.query(self.pos(), 'climbable') or Tile.query(self.pos(), 'grabbable')):
                    return  # No puedo subir, salgo sin moverme
                self.apply_move(dx, dy)  # Aplico el movimiento si todo está bien

    def apply_move(self, dx, dy):
        # Aplico el movimiento actualizando las coordenadas
        self._x += dx  # Actualizo x
        self._y += dy  # Actualizo y
        self.move_img(dx, dy)  # Muevo la imagen gráfica en la pantalla
        if self._y + 1 < Config.LEVEL_HEIGHT:  # Si no estoy en la última fila
            self.fall()  # Chequeo si debo caer después de moverme

    def fall(self):
        # Hago que el personaje caiga si no hay soporte debajo
        if self._y + 1 < Config.LEVEL_HEIGHT:  # Aseguro que haya un tile debajo
            next_pos_down = (self._x, self._y + 1)  # Posición justo debajo
            # Caigo si no hay algo donde pararme y no estoy agarrado a algo
            if not Tile.query(next_pos_down, 'standable') and not Tile.query(self.pos(), 'grabbable'):
                self.apply_move(0, 1)  # Caigo una posición hacia abajo

    def redraw(self):
        # Redibujo el personaje: primero lo borro y luego lo dibujo de nuevo
        self.undraw()
        self.draw()

# Defino la clase para el jugador, que hereda de Character
class Player (Character):
    main = None  # Variable estática para guardar la instancia principal del jugador
    INITIAL_LIVES = 3  # Número inicial de vidas

    def __init__(self, x, y, img_path='t_android.png', is_initial_load=False):
        # Inicializo al jugador con una imagen por defecto
        super(Player, self).__init__(x, y, img_path)
        self._coins_collected = 0  # Contador de monedas recolectadas

        # Lógica para manejar si es la primera vez que creo al jugador o si ya existe
        if Player.main is None:  # Si no hay jugador principal aún
            Player.main = self  # Este será el jugador principal
            self.initial_x = x  # Guardo su posición inicial x
            self.initial_y = y  # Guardo su posición inicial y
            self.lives = Player.INITIAL_LIVES  # Le doy las vidas iniciales
            print(f"Player.main CREADO en ({x},{y}) con {self.lives} vidas.")
            Drawable.update_lives_display(self.lives)  # Actualizo la pantalla con las vidas
        elif is_initial_load:  # Si es una carga inicial explícita (nuevo juego)
            Player.main = self
            self.initial_x = x
            self.initial_y = y
            self.lives = Player.INITIAL_LIVES
            print(f"Player.main REINICIALIZADO en ({x},{y}) con {self.lives} vidas.")
            Drawable.update_lives_display(self.lives)
        else:  # Si ya existe Player.main y no es una carga inicial
            if not hasattr(self, 'initial_x'): self.initial_x = x  # Salvaguarda por si acaso
            if not hasattr(self, 'initial_y'): self.initial_y = y  # Salvaguarda por si acaso
            if not hasattr(self, 'lives'): self.lives = Player.main.lives if Player.main else Player.INITIAL_LIVES
            print(f"Nueva instancia de Player creada, pero Player.main ya existe. Vidas: {self.lives}")

        self.draw()  # Dibujo al jugador una vez que todo está configurado

    def set_initial_pos(self, x, y):
        # Método para actualizar la posición inicial del jugador (para nuevos niveles)
        self.initial_x = x
        self.initial_y = y
        print(f"Player.main: Nueva posición inicial establecida a ({x},{y})")

    def lose_life(self):
        # Hago que el jugador pierda una vida
        if self.lives > 0:  # Solo si tiene vidas
            self.lives -= 1  # Reduzco las vidas
            print(f"Player perdió una vida. Vidas restantes: {self.lives}")
            Drawable.update_lives_display(self.lives)  # Actualizo la pantalla

        if self.lives > 0:  # Si aún le quedan vidas
            self.respawn()  # Lo hago reaparecer
        else:  # Si no quedan vidas
            print("Player sin vidas. Game Over.")
            Drawable.lost()  # Muestro el mensaje de fin del juego

    def respawn(self, force_redraw_lives=False):
        # Reaparezco al jugador en su posición inicial
        print(f"Player respawneando en ({self.initial_x}, {self.initial_y}). Vidas: {self.lives}")
        self.undraw()  # Borro su imagen actual

        dx_to_respawn = self.initial_x - self._x  # Calculo cuánto mover en x
        dy_to_respawn = self.initial_y - self._y  # Calculo cuánto mover en y

        if dx_to_respawn != 0 or dy_to_respawn != 0:  # Solo muevo si es necesario
            self.move_img(dx_to_respawn, dy_to_respawn)  # Muevo la imagen

        self._x = self.initial_x  # Actualizo la posición x
        self._y = self.initial_y  # Actualizo la posición y
        self.draw()  # Redibujo al jugador

        if force_redraw_lives:  # Si se fuerza, actualizo las vidas en pantalla
            Drawable.update_lives_display(self.lives)

        if self._y + 1 < Config.LEVEL_HEIGHT:  # Si no estoy en la última fila
            self.fall()  # Chequeo si debe caer

    def at_exit(self):
        # Compruebo si el jugador está en la salida (fila 0)
        return (self._y == 0)

    def apply_move(self, dx, dy):
        # Aplico el movimiento y chequeo interacciones específicas del jugador
        super(Player, self).apply_move(dx, dy)  # Llamo al método de la clase base
        current_tile = Tile.tile_at(self.pos())  # Obtengo el tile donde estoy
        # Si el tile tiene un método 'take' (como una moneda), lo intento tomar
        if hasattr(current_tile, 'take') and callable(getattr(current_tile, 'take')):
            if current_tile.take():  # Si se tomó algo (ej. moneda)
                self._coins_collected += 1  # Incremento el contador
                Drawable.draw_coin_counter(self._coins_collected)  # Actualizo el contador en pantalla
        # Chequeo colisiones con baddies
        for baddie in Baddie.baddies:
            if baddie.pos() == self.pos():  # Si estoy en la misma posición que un baddie
                self.lose_life()  # Pierdo una vida
                return  # Salgo para no procesar más este turno

    def get_coins_collected(self):
        # Devuelvo la cantidad de monedas recolectadas
        return self._coins_collected

    def dig(self, direction):
        # Método para cavar un tile a la izquierda (-1) o derecha (1) del jugador
        def refill(tile_dug):
            # Función que se ejecutará para rellenar el tile cavado después de un tiempo
            tile_dug.show()  # Restauro el tile
            if Player.main and Player.main.pos() == tile_dug.coord:  # Si estoy sobre el tile al rellenarse
                Player.main.lose_life()  # Pierdo una vida
            for baddie in Baddie.baddies:  # Chequeo si hay baddies en el tile
                if baddie.pos() == tile_dug.coord:
                    baddie.die()  # Elimino al baddie

        dig_x = self._x + direction  # Calculo la posición x del tile a cavar
        dig_y = self._y + 1  # El tile a cavar está justo debajo

        if self._y < Config.LEVEL_HEIGHT - 1:  # No cavo si estoy en la última fila
            current_tile_player_is_on = Tile.tile_at(self.pos())  # Tile donde estoy parado
            # Solo puedo cavar si no estoy en una escalera o cuerda
            can_dig_from_current_pos = not (current_tile_player_is_on.properties.get('climbable') or \
                                            current_tile_player_is_on.properties.get('grabbable'))

            # Chequeo si el tile a cavar es 'diggable' y si puedo cavar desde mi posición
            if Tile.query((dig_x, dig_y), 'diggable') and can_dig_from_current_pos:
                tile_to_dig_obj = Tile.tile_at((dig_x, dig_y))  # Obtengo el objeto del tile
                tile_to_dig_obj.hide()  # Lo hago desaparecer (se convierte en pasable)
                Event(refill, 120, args=[tile_to_dig_obj])  # Programo que se rellene después de 120 ticks

                if Player.main: Player.main.fall()  # Chequeo si caigo tras cavar
                for baddie in Baddie.baddies: 
                    baddie.fall()  # Chequeo si los baddies caen

# Defino la clase para los enemigos, que también heredan de Character
class Baddie (Character):
    baddies = []  # Lista estática para guardar todos los baddies

    def __init__(self, x, y, img_path='t_red.png', is_initial_load=False):
        # Inicializo un baddie con una imagen por defecto
        super(Baddie, self).__init__(x, y, img_path)
        self.initial_x = x  # Guardo su posición inicial x
        self.initial_y = y  # Guardo su posición inicial y
        self.move_event = Event(self.move_action, 30, recurring=True)  # Creo un evento para que se mueva cada 30 ticks
        Baddie.baddies.append(self)  # Lo añado a la lista de baddies
        self.draw()  # Lo dibujo en pantalla

    def move_action(self):
        # Acción que realiza el baddie cada vez que se dispara el evento de movimiento
        if not Player.main or not Player.main.lives > 0:  # No me muevo si no hay jugador o está muerto
            return
        move_coords_delta = PathFinder.run(self.pos())  # Busco el próximo movimiento hacia el jugador
        if move_coords_delta:  # Si hay un movimiento válido
            super(Baddie, self).move(*move_coords_delta)  # Me muevo en esa dirección
        if Player.main and self.pos() == Player.main.pos():  # Si alcanzo al jugador
            Player.main.lose_life()  # Hago que pierda una vida

    def die(self):
        # Elimino al baddie cuando muere
        self.undraw()  # Borro su imagen
        Event.delete(self.move_event)  # Cancelo su evento de movimiento
        if self in Baddie.baddies: 
            Baddie.baddies.remove(self)  # Lo quito de la lista

# Defino el mapeo de caracteres a clases antes de usar load_characters
char_map_definition = {
    'P': Player,  # 'P' representa al jugador
    'B': Baddie   # 'B' representa a un enemigo
}
Character.char_map = char_map_definition  # Asigno el diccionario a la clase Character

# Clase para encontrar caminos, usada por los baddies para perseguir al jugador
class PathFinder:
    tiles = None  # Matriz para marcar tiles visitados durante la búsqueda

    @staticmethod
    def valid_tile(pos, last_pos):
        # Chequeo si un tile es válido para que un baddie se mueva allí
        x, y = pos
        if not (0 <= x < Config.LEVEL_WIDTH and 0 <= y < Config.LEVEL_HEIGHT):  # Fuera de límites
            return False
        if PathFinder.tiles[x][y]:  # Ya visitado en esta búsqueda
            return False
        if Tile.query(pos, 'passable'):  # Si es transitable
            under = (x, y + 1)  # Posición debajo
            is_on_grabbable = Tile.query(pos, 'grabbable')  # Chequeo si puedo agarrarme
            is_supported_below = False
            if y + 1 < Config.LEVEL_HEIGHT:  # Si hay tile debajo
                is_supported_below = Tile.query(under, 'standable')  # Chequeo si me sostiene
            else:  # Si estoy en la última fila
                is_supported_below = Tile.query(pos, 'standable')
            return is_on_grabbable or is_supported_below  # Válido si estoy agarrado o soportado
        return False

    @staticmethod
    def run(start_pos):
        # Implemento un BFS para encontrar el próximo movimiento hacia el jugador
        if not Player.main:  # Si no hay jugador, no hago nada
            return None
        PathFinder.tiles = [[False for _ in range(Config.LEVEL_HEIGHT)] for _ in range(Config.LEVEL_WIDTH)]  # Reinicio la matriz
        queue = []  # Cola para el BFS

        # Exploro los movimientos iniciales desde mi posición
        for dx_dy, neighbor_pos in PathFinder.get_valid_initial_moves(start_pos):
            if neighbor_pos == Player.main.pos():  # Si ya estoy al lado del jugador
                return dx_dy  # Devuelvo el movimiento directo
            PathFinder.tiles[neighbor_pos[0]][neighbor_pos[1]] = True  # Marco como visitado
            queue.append((neighbor_pos, [dx_dy]))  # Añado a la cola con el primer movimiento

        # Proceso la cola hasta encontrar al jugador
        while queue:
            current_pos, path_taken = queue.pop(0)  # Tomo el primer elemento (FIFO)
            for dx_dy_next, next_neighbor_pos in PathFinder.get_valid_initial_moves(current_pos):
                if next_neighbor_pos == Player.main.pos():  # Encontré al jugador
                    return path_taken[0]  # Devuelvo el primer paso del camino
                if not PathFinder.tiles[next_neighbor_pos[0]][next_neighbor_pos[1]]:  # Si no lo visité
                    PathFinder.tiles[next_neighbor_pos[0]][next_neighbor_pos[1]] = True  # Lo marco
                    new_path = list(path_taken)  # Copio el camino
                    queue.append((next_neighbor_pos, new_path))  # Añado a la cola
        return None  # No encontré camino

    @staticmethod
    def get_valid_initial_moves(pos_from):
        # Genero una lista de movimientos válidos desde mi posición
        x, y = pos_from
        valid_moves = []
        potential_deltas = [(-1, 0), (1, 0), (0, 1), (0, -1)]  # Izquierda, derecha, abajo, arriba

        for dx, dy in potential_deltas:
            next_x, next_y = x + dx, y + dy
            if dy < 0:  # Si intento subir
                if not (Tile.query(pos_from, 'climbable') or Tile.query(pos_from, 'grabbable')):
                    continue  # No puedo subir si no estoy en algo escalable
            if PathFinder.is_tile_navigable_for_baddie((next_x, next_y)):  # Si el tile es navegable
                valid_moves.append(((dx, dy), (next_x, next_y)))  # Lo añado a la lista
        return valid_moves

    @staticmethod
    def is_tile_navigable_for_baddie(pos):
        # Chequeo si un tile es navegable sin modificar la matriz de visitados
        x, y = pos
        if not (0 <= x < Config.LEVEL_WIDTH and 0 <= y < Config.LEVEL_HEIGHT):
            return False
        if Tile.query(pos, 'passable'):
            under = (x, y + 1)
            is_on_grabbable = Tile.query(pos, 'grabbable')
            is_supported_below = False
            if y + 1 < Config.LEVEL_HEIGHT:
                is_supported_below = Tile.query(under, 'standable')
            else:
                is_supported_below = Tile.query(pos, 'standable')
            return is_on_grabbable or is_supported_below
        return False