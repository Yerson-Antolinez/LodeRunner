# Archivo: drawable.py

import os                # Módulo para operaciones del sistema de archivos (rutas, existencia de archivos, etc.)
import time              # Para usar funciones de tiempo, como time.sleep() o medir intervalos
from config import Config  # Importa la clase Config desde config.py, que carga parámetros de configuración del juego
from graphics import Image, Point, GraphWin, Text, GraphicsError  


class Drawable(object):
    _window = None  # Mi ventana gráfica donde se dibuja todo el juego
    _lives_text_item = None  # El texto que muestra las vidas, lo guardo para actualizarlo después
    _coin_counter_text = None  # El texto del contador de monedas, también lo guardo para modificarlo

    @staticmethod
    def recreateWindow():
        """
        Creo o recreo la ventana del juego desde cero cuando sea necesario.
        """
        if Drawable._window:
            try:
                Drawable._window.close()  # Si ya hay una ventana, la cierro primero
            except:
                pass  # No me preocupo si ya estaba cerrada o algo falla
        # Hago una ventana nueva con el tamaño que definí en Config, más un pequeño margen
        Drawable._window = GraphWin("LodeRunner", Config.WINDOW_WIDTH + 20, Config.WINDOW_HEIGHT + 20)
        Drawable._window.setBackground('lightcyan')  # Le pongo un fondo claro y bonito
        Drawable._lives_text_item = None  # Reseteo el texto de las vidas
        Drawable._coin_counter_text = None  # Reseteo el contador de monedas

    @staticmethod
    def lost():
        """
        Muestro un mensaje de derrota y cierro el juego cuando pierdo.
        """
        if not Drawable._window or Drawable._window.isClosed():
            print("Quise mostrar 'PERDISTE' pero no hay ventana, así que chau.")
            exit(0)  # Si no hay ventana, termino el programa directamente

        try:
            # Pongo un mensaje grande y rojo en el medio de la pantalla
            t = Text(Point(Config.WINDOW_WIDTH / 2 + 10, Config.WINDOW_HEIGHT / 2 + 10), 'PERDISTE!')
            t.setSize(36)  # Que sea bien grande para que se note
            t.setTextColor('red')  # Rojo para el drama
            t.draw(Drawable._window)  # Lo dibujo en la ventana
            Drawable._window.update()  # Refresco la pantalla para que se vea
            Drawable._window.getKey()  # Espero a que toquen una tecla antes de cerrar
        except Exception as e:
            print(f"Algo salió mal mostrando 'PERDISTE': {e}")
        finally:
            if Drawable._window and not Drawable._window.isClosed():
                Drawable._window.close()  # Cierro la ventana al final
            exit(0)  # Termino el programa pase lo que pase

    @staticmethod
    def won():
        
        if not Drawable._window or Drawable._window.isClosed():
            print("Quise decir 'GANASTE' pero no hay ventana, qué lástima.")
            return  # No hago nada si la ventana no está

        try:
            # Escribo un mensaje divertido y lo centro en la pantalla
            t = Text(Point(Config.WINDOW_WIDTH / 2 + 10, Config.WINDOW_HEIGHT / 2 + 10), 'Ganaste. No fue amor, pero cuenta')
            t.setSize(36)  # Grande para celebrar
            t.setTextColor('green')  # Verde para la victoria
            t.draw(Drawable._window)  # Lo muestro en la ventana
            Drawable._window.update()  # Actualizo la pantalla
            time.sleep(2)  # Dejo que se vea un par de segundos
        except Exception as e:
            print(f"No pude mostrar 'GANASTE' por este error: {e}")

    @staticmethod
    def draw_text_utility(message, x, y, size=12, color='black'):
        """
        Una función útil que uso para dibujar texto donde quiera.
        Devuelve el objeto Text por si lo necesito después.
        """
        if not Drawable._window or Drawable._window.isClosed():
            return None  # No dibujo si no hay ventana

        try:
            text_item = Text(Point(x, y), message)  # Creo el texto en la posición que quiero
            text_item.setSize(size)  # Le doy el tamaño que pedí
            text_item.setTextColor(color)  # Y el color que elegí
            text_item.draw(Drawable._window)  # Lo dibujo en mi ventana
            return text_item  # Lo devuelvo por si quiero usarlo después
        except Exception as e:
            print(f"No pude dibujar el texto '{message}' por: {e}")
            return None

    @staticmethod
    def update_lives_display(lives_count):
        """
        Actualizo el texto que muestra cuántas vidas me quedan.
        """
        if not Drawable._window or Drawable._window.isClosed():
            return  # No hago nada si la ventana no está

        message = f"Vidas: {lives_count}"  # El mensaje con las vidas actuales
        text_x = 55  # Donde quiero que aparezca en x
        text_y = 15  # Donde quiero que aparezca en y

        try:
            if Drawable._lives_text_item:  # Si ya tengo un texto de vidas
                if Drawable._lives_text_item.canvas and not Drawable._lives_text_item.canvas.isClosed():
                    try:
                        Drawable._lives_text_item.setText(message)  # Solo cambio el mensaje
                    except:
                        Drawable._lives_text_item.undraw()  # Si falla, lo borro
                        Drawable._lives_text_item = Drawable.draw_text_utility(message, text_x, text_y, size=23, color='darkorange')
                else:
                    Drawable._lives_text_item = Drawable.draw_text_utility(message, text_x, text_y, size=23, color='darkorange')
            else:
                # Si no había texto, lo creo desde cero
                Drawable._lives_text_item = Drawable.draw_text_utility(message, text_x, text_y, size=23, color='darkorange')

            if Drawable._window.autoflush:
                Drawable._window.update()  # Refresco la pantalla si está en modo automático
        except Exception as e:
            print(f"Error actualizando las vidas: {e}")
            if Drawable._lives_text_item:
                try:
                    Drawable._lives_text_item.undraw()  # Borro el texto si algo falla
                except:
                    pass
            Drawable._lives_text_item = None

    @staticmethod
    def draw_coin_counter(coins):
        """
        Muestro o actualizo el contador de monedas en la pantalla.
        """
        if not Drawable._coin_counter_text:
            # Si no existe el contador, lo creo
            Drawable._coin_counter_text = Text(Point(80, 40), f"Monedas: {coins}")
            Drawable._coin_counter_text.setSize(23)  # Tamaño grande para que se vea
            Drawable._coin_counter_text.setTextColor('darkorange')  # Naranja para que combine
            Drawable._coin_counter_text.draw(Drawable._window)  # Lo dibujo
        else:
            # Si ya existe, solo cambio el número
            Drawable._coin_counter_text.setText(f"Monedas: {coins}")

    def __init__(self, coords, img_path=None):
        """
        Creo un objeto que se puede dibujar, con una imagen si me dan una ruta.
        """
        if img_path:
            # Calculo dónde va a estar el centro de la imagen en la pantalla
            screen_x = coords[0] * Config.CELL_SIZE + (Config.CELL_SIZE / 2) + 10
            screen_y = coords[1] * Config.CELL_SIZE + (Config.CELL_SIZE / 2) + 10

            try:
                # Cargo la imagen desde la carpeta 'graphics'
                self._img = Image(Point(screen_x, screen_y), os.path.join('graphics', img_path))
            except Exception as e:
                print(f"No pude cargar la imagen {img_path}: {e}")
                self._img = None  # Si falla, no hay imagen
        else:
            self._img = None  # Sin ruta, no hay imagen

    def draw(self):
        """
        Dibujo la imagen del objeto en la ventana si tengo una.
        """
        if self._img and Drawable._window and not Drawable._window.isClosed():
            try:
                self._img.draw(Drawable._window)  # Pongo la imagen en la ventana
            except GraphicsError as e:
                if "Object currently drawn" in str(e):
                    pass  # No me preocupo si ya está dibujada
                else:
                    print(f"Error gráfico dibujando {self._img}: {e}")
            except Exception as e:
                print(f"Algo raro pasó dibujando {self._img}: {e}")

    def move_img(self, dx, dy):
        """
        Muevo la imagen del objeto según las celdas del juego.
        """
        if self._img and Drawable._window and not Drawable._window.isClosed():
            try:
                # Muevo la imagen usando el tamaño de las celdas
                self._img.move(dx * Config.CELL_SIZE, dy * Config.CELL_SIZE)
            except Exception as e:
                print(f"No pude mover la imagen: {e}")

    def undraw(self):
        """
        Borro la imagen de la ventana si existe.
        """
        if self._img and Drawable._window and not Drawable._window.isClosed():
            try:
                self._img.undraw()  # Quito la imagen de la pantalla
            except Exception as e:
                print(f"Error borrando la imagen: {e}")