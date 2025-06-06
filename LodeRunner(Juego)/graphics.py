# graphics.py

import time, os, sys  # Importa módulos básicos: 'time' para pausas, 'os' para operaciones del sistema y 'sys' para compatibilidad.

try:  # Intenta importar 'tkinter' según la versión de Python (2.x o 3.x).
   import tkinter as tk  # Para Python 3.x, usa 'tkinter'.
except:
   import Tkinter as tk  # Para Python 2.x, usa 'Tkinter'.



class GraphicsError(Exception):  # Define una clase de excepción personalizada para errores gráficos.
    """Generic error class for graphics module exceptions."""
    pass

# Define constantes para mensajes de error específicos.
OBJ_ALREADY_DRAWN = "Object currently drawn"  # Error cuando un objeto ya está dibujado.
UNSUPPORTED_METHOD = "Object doesn't support operation"  # Error para métodos no soportados.
BAD_OPTION = "Illegal option value"  # Error por valores de opción inválidos.
DEAD_THREAD = "Graphics thread quit unexpectedly"  # Error si el hilo gráfico termina inesperadamente.

_root = tk.Tk()  # Crea la ventana raíz de Tkinter, base para todas las ventanas gráficas.
_root.withdraw()  # Oculta la ventana raíz para que no sea visible al usuario.

def update():  # Función global para actualizar la interfaz gráfica.
    _root.update()  # Llama al método 'update' de Tkinter para refrescar la ventana raíz.

        
class GraphWin(tk.Canvas):  # Clase para crear una ventana gráfica, hereda de 'tk.Canvas'.



    def __init__(self, title="Graphics Window", width=200, height=200, autoflush=True):  # Constructor de la ventana.
        master = tk.Toplevel(_root)  # Crea una ventana secundaria (toplevel) sobre la raíz.
        master.protocol("WM_DELETE_WINDOW", self.close)  # Asocia el cierre de la ventana al método 'close'.
        tk.Canvas.__init__(self, master, width=width, height=height)  # Inicializa el lienzo con dimensiones dadas.
        self.master.title(title)  # Establece el título de la ventana.
        self.pack()  # Empaqueta el lienzo en la ventana para que sea visible.
        master.resizable(0,0)  # Impide redimensionar la ventana.
        self.foreground = "black"  # Color por defecto para dibujar (negro).
        self.items = []  # Lista para almacenar objetos dibujados en la ventana.
        self.mouseX = None  # Coordenada X del último clic del mouse (inicialmente nula).
        self.mouseY = None  # Coordenada Y del último clic del mouse (inicialmente nula).
        self.bind("<Button-1>", self._onClick)  # Vincula el clic izquierdo del mouse al método '_onClick'.
        self.bind_all("<Key>", self._onKey)  # Vincula cualquier tecla presionada al método '_onKey'.
        self.height = height  # Almacena la altura de la ventana.
        self.width = width  # Almacena el ancho de la ventana.
        self.autoflush = autoflush  # Bandera para actualizar automáticamente la ventana tras cambios.
        self._mouseCallback = None  # Función callback para manejar clics del mouse (inicialmente nula).
        self.trans = None  # Objeto de transformación de coordenadas (inicialmente nulo).
        self.closed = False  # Bandera que indica si la ventana está cerrada (inicialmente falso).
        master.lift()  # Eleva la ventana para que esté visible sobre otras.
        self.lastKey = ""  # Almacena la última tecla presionada (inicialmente vacía).
        if autoflush: _root.update()  # Si 'autoflush' es True, actualiza la ventana al crearla.
    
    def __checkOpen(self):  # Método privado para verificar si la ventana está abierta.
        if self.closed:  # Si está cerrada...
            raise GraphicsError("window is closed")  # Lanza una excepción.

    def _onKey(self, evnt):  # Método privado que maneja eventos de teclado.
        self.lastKey = evnt.keysym  # Almacena el símbolo de la tecla presionada (ej. "a", "Return").

    def setBackground(self, color):  # Establece el color de fondo de la ventana.
        
        self.__checkOpen()  # Verifica que la ventana esté abierta.
        self.config(bg=color)  # Configura el color de fondo del lienzo.
        self.__autoflush()  # Actualiza la ventana si 'autoflush' está activado.
        
    def setCoords(self, x1, y1, x2, y2):  # Define un sistema de coordenadas personalizado.
        """Set coordinates of window to run from (x1,y1) in the
        lower-left corner to (x2,y2) in the upper-right corner."""
        self.trans = Transform(self.width, self.height, x1, y1, x2, y2)  # Crea un objeto Transform para la conversión.
        self.redraw()  # Redibuja todos los objetos con las nuevas coordenadas.

    def close(self):  # Cierra la ventana gráfica.
        """Close the window"""
        if self.closed: return  # Si ya está cerrada, no hace nada.
        self.closed = True  # Marca la ventana como cerrada.
        self.master.destroy()  # Destruye la ventana secundaria.
        self.__autoflush()  # Actualiza la interfaz si 'autoflush' está activado.

    def isClosed(self):  # Verifica si la ventana está cerrada.
        return self.closed  # Devuelve el estado de 'closed'.

    def isOpen(self):  # Verifica si la ventana está abierta.
        return not self.closed  # Devuelve lo opuesto a 'closed'.

    def __autoflush(self):  # Método privado para actualizar la ventana si 'autoflush' está activado.
        if self.autoflush:  # Si 'autoflush' es True...
            _root.update()  # Actualiza la interfaz gráfica.

    def plot(self, x, y, color="black"):  # Dibuja un píxel en coordenadas del usuario.
        """Set pixel (x,y) to the given color"""
        self.__checkOpen()  # Verifica que la ventana esté abierta.
        xs, ys = self.toScreen(x, y)  # Convierte las coordenadas del usuario a coordenadas de pantalla.
        self.create_line(xs, ys, xs+1, ys, fill=color)  # Dibuja una línea de un píxel con el color especificado.
        self.__autoflush()  # Actualiza la ventana si 'autoflush' está activado.
        
    def plotPixel(self, x, y, color="black"):  # Dibuja un píxel en coordenadas crudas de pantalla.
       
        self.__checkOpen()  # Verifica que la ventana esté abierta.
        self.create_line(x, y, x+1, y, fill=color)  # Dibuja una línea de un píxel directamente en la pantalla.
        self.__autoflush()  # Actualiza la ventana si 'autoflush' está activado.
      
    def flush(self):  # Fuerza una actualización de la ventana.
        """Update drawing to the window"""
        self.__checkOpen()  # Verifica que la ventana esté abierta.
        self.update_idletasks()  # Actualiza las tareas pendientes del lienzo.
        
    def getMouse(self):  # Espera un clic del mouse y devuelve un objeto Point con las coordenadas.
        
        self.update()  # Limpia cualquier clic previo.
        self.mouseX = None  # Reinicia la coordenada X del mouse.
        self.mouseY = None  # Reinicia la coordenada Y del mouse.
        while self.mouseX == None or self.mouseY == None:  # Espera hasta que se registre un clic.
            self.update()  # Actualiza la ventana para capturar eventos.
            if self.isClosed(): raise GraphicsError("getMouse in closed window")  # Error si la ventana se cierra.
            time.sleep(.1)  # Pausa breve para no sobrecargar el hilo.
        x, y = self.toWorld(self.mouseX, self.mouseY)  # Convierte las coordenadas de pantalla a coordenadas del usuario.
        self.mouseX = None  # Reinicia la coordenada X.
        self.mouseY = None  # Reinicia la coordenada Y.
        return Point(x, y)  # Devuelve un objeto Point con las coordenadas.

    def checkMouse(self):  # Devuelve el último clic del mouse o None si no hay clic nuevo.
       
        if self.isClosed():  # Verifica si la ventana está cerrada.
            raise GraphicsError("checkMouse in closed window")  # Lanza error si está cerrada.
        self.update()  # Actualiza para capturar eventos recientes.
        if self.mouseX != None and self.mouseY != None:  # Si hay un clic registrado...
            x, y = self.toWorld(self.mouseX, self.mouseY)  # Convierte a coordenadas del usuario.
            self.mouseX = None  # Reinicia la coordenada X.
            self.mouseY = None  # Reinicia la coordenada Y.
            return Point(x, y)  # Devuelve el punto del clic.
        else:
            return None  # Devuelve None si no hay clic.

    def getKey(self):  # Espera a que el usuario presione una tecla y la devuelve como string.
        
        self.lastKey = ""  # Reinicia la última tecla presionada.
        while self.lastKey == "":  # Espera hasta que se presione una tecla.
            self.update()  # Actualiza para capturar eventos.
            if self.isClosed(): raise GraphicsError("getKey in closed window")  # Error si la ventana se cierra.
            time.sleep(.1)  # Pausa breve para no sobrecargar el hilo.
        key = self.lastKey  # Almacena la tecla presionada.
        self.lastKey = ""  # Reinicia la variable.
        return key  # Devuelve la tecla como string.

    def checkKey(self):  # Devuelve la última tecla presionada o None si no hay tecla nueva.
     
        if self.isClosed():  # Verifica si la ventana está cerrada.
            raise GraphicsError("checkKey in closed window")  # Lanza error si está cerrada.
        self.update()  # Actualiza para capturar eventos recientes.
        key = self.lastKey  # Toma la última tecla presionada.
        self.lastKey = ""  # Reinicia la variable.
        return key  # Devuelve la tecla o None si no hay ninguna.

    def getHeight(self):  # Devuelve la altura de la ventana.
  
        return self.height  # Retorna el valor almacenado en 'height'.
        
    def getWidth(self):  # Devuelve el ancho de la ventana.
        
        return self.width  # Retorna el valor almacenado en 'width'.
    
    def toScreen(self, x, y):  # Convierte coordenadas del usuario a coordenadas de pantalla.
        trans = self.trans  # Obtiene el objeto de transformación.
        if trans:  # Si existe un sistema de coordenadas personalizado...
            return self.trans.screen(x, y)  # Usa el método 'screen' de Transform.
        else:
            return x, y  # Devuelve las coordenadas sin cambios si no hay transformación.
                      
    def toWorld(self, x, y):  # Convierte coordenadas de pantalla a coordenadas del usuario.
        trans = self.trans  # Obtiene el objeto de transformación.
        if trans:  # Si existe un sistema de coordenadas personalizado...
            return self.trans.world(x, y)  # Usa el método 'world' de Transform.
        else:
            return x, y  # Devuelve las coordenadas sin cambios si no hay transformación.
        
    def setMouseHandler(self, func):  # Establece una función callback para manejar clics del mouse.
        self._mouseCallback = func  # Asigna la función proporcionada.
        
    def _onClick(self, e):  # Método privado que maneja el evento de clic del mouse.
        self.mouseX = e.x  # Almacena la coordenada X del clic.
        self.mouseY = e.y  # Almacena la coordenada Y del clic.
        if self._mouseCallback:  # Si hay una función callback definida...
            self._mouseCallback(Point(e.x, e.y))  # Llama a la función con un objeto Point.

    def addItem(self, item):  # Agrega un objeto gráfico a la lista de ítems.
        self.items.append(item)  # Añade el ítem a la lista.

    def delItem(self, item):  # Elimina un objeto gráfico de la lista de ítems.
        self.items.remove(item)  # Remueve el ítem de la lista.

    def redraw(self):  # Redibuja todos los objetos en la ventana.
        for item in self.items[:]:  # Itera sobre una copia de la lista de ítems.
            item.undraw()  # Borra el ítem actual.
            item.draw(self)  # Vuelve a dibujar el ítem en la ventana.
        self.update()  # Actualiza la ventana para reflejar los cambios.
        
class Transform:  # Clase para manejar transformaciones de coordenadas 2D.


    
    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):  # Constructor de Transform.
        # w, h son el ancho y alto de la ventana.
        # (xlow, ylow) son las coordenadas de la esquina inferior izquierda en el sistema del usuario.
        # (xhigh, yhigh) son las coordenadas de la esquina superior derecha en el sistema del usuario.
        xspan = (xhigh - xlow)  # Calcula el rango en X del sistema del usuario.
        yspan = (yhigh - ylow)  # Calcula el rango en Y del sistema del usuario.
        self.xbase = xlow  # Almacena la coordenada X base (inferior izquierda).
        self.ybase = yhigh  # Almacena la coordenada Y base (superior derecha).
        self.xscale = xspan / float(w - 1)  # Escala para convertir X del usuario a pantalla.
        self.yscale = yspan / float(h - 1)  # Escala para convertir Y del usuario a pantalla.
        
    def screen(self, x, y):  # Convierte coordenadas del usuario a coordenadas de pantalla.
        # Devuelve x, y en coordenadas de pantalla (ventana).
        xs = (x - self.xbase) / self.xscale  # Calcula la coordenada X en pantalla.
        ys = (self.ybase - y) / self.yscale  # Calcula la coordenada Y en pantalla (invierte Y).
        return int(xs + 0.5), int(ys + 0.5)  # Devuelve valores enteros redondeados.
        
    def world(self, xs, ys):  # Convierte coordenadas de pantalla a coordenadas del usuario.
        # Devuelve xs, ys en coordenadas del mundo (usuario).
        x = xs * self.xscale + self.xbase  # Calcula la coordenada X del usuario.
        y = self.ybase - ys * self.yscale  # Calcula la coordenada Y del usuario (invierte Y).
        return x, y  # Devuelve las coordenadas transformadas.

# Valores por defecto para opciones de configuración de ítems gráficos.
DEFAULT_CONFIG = {"fill": "",  # Color de relleno (vacío por defecto).
      "outline": "black",  # Color del contorno (negro por defecto).
      "width": "1",  # Grosor de la línea (1 por defecto).
      "arrow": "none",  # Tipo de flecha (ninguna por defecto).
      "text": "",  # Texto asociado (vacío por defecto).
      "justify": "center",  # Justificación del texto (centrado por defecto).
      "font": ("helvetica", 12, "normal")}  # Fuente por defecto (Helvetica, tamaño 12, normal).

class GraphicsObject:  # Clase base para todos los objetos dibujables.


    # Las subclases deben sobrescribir los métodos '_draw' y '_move'.
    
    def __init__(self, options):  # Constructor de GraphicsObject.
        # 'options' es una lista de opciones válidas para este objeto.
        self.canvas = None  # Referencia al lienzo donde se dibujará (inicialmente nulo).
        self.id = None  # Identificador del objeto en Tkinter (inicialmente nulo).
        config = {}  # Diccionario para almacenar la configuración del objeto.
        for option in options:  # Para cada opción válida...
            config[option] = DEFAULT_CONFIG[option]  # Asigna el valor por defecto.
        self.config = config  # Almacena el diccionario de configuración.
        
    def setFill(self, color):  # Establece el color de relleno del objeto.
    
        self._reconfig("fill", color)  # Actualiza la configuración con el nuevo color.
        
    def setOutline(self, color):  # Establece el color del contorno del objeto.
        
        self._reconfig("outline", color)  # Actualiza la configuración con el nuevo color.
        
    def setWidth(self, width):  # Establece el grosor de la línea del objeto.
        
        self._reconfig("width", width)  # Actualiza la configuración con el nuevo grosor.

    def draw(self, graphwin):  # Dibuja el objeto en una ventana gráfica.
     
        if self.canvas and not self.canvas.isClosed():  # Si ya está dibujado en un lienzo abierto...
            raise GraphicsError(OBJ_ALREADY_DRAWN)  # Lanza error por objeto ya dibujado.
        if graphwin.isClosed():  # Si la ventana está cerrada...
            raise GraphicsError("Can't draw to closed window")  # Lanza error.
        self.canvas = graphwin  # Asocia el objeto al lienzo de la ventana.
        self.id = self._draw(graphwin, self.config)  # Llama al método '_draw' específico del objeto.
        graphwin.addItem(self)  # Agrega el objeto a la lista de ítems de la ventana.
        if graphwin.autoflush:  # Si 'autoflush' está activado...
            _root.update()  # Actualiza la interfaz gráfica.

    def undraw(self):  # Borra el objeto de la ventana.
   
        if not self.canvas: return  # Si no está dibujado, no hace nada.
        if not self.canvas.isClosed():  # Si el lienzo está abierto...
            self.canvas.delete(self.id)  # Elimina el objeto del lienzo usando su ID.
            self.canvas.delItem(self)  # Remueve el objeto de la lista de ítems.
            if self.canvas.autoflush:  # Si 'autoflush' está activado...
                _root.update()  # Actualiza la interfaz gráfica.
        self.canvas = None  # Reinicia la referencia al lienzo.
        self.id = None  # Reinicia el identificador.

    def move(self, dx, dy):  # Mueve el objeto en la ventana.
 
        self._move(dx, dy)  # Llama al método '_move' específico del objeto.
        canvas = self.canvas  # Obtiene el lienzo asociado.
        if canvas and not canvas.isClosed():  # Si el lienzo existe y está abierto...
            trans = canvas.trans  # Obtiene el objeto de transformación del lienzo.
            if trans:  # Si hay un sistema de coordenadas personalizado...
                x = dx / trans.xscale  # Ajusta el desplazamiento en X según la escala.
                y = -dy / trans.yscale  # Ajusta el desplazamiento en Y (invierte dirección).
            else:
                x = dx  # Usa el desplazamiento sin ajustar si no hay transformación.
                y = dy  # Usa el desplazamiento sin ajustar.
            self.canvas.move(self.id, x, y)  # Mueve el objeto en el lienzo.
            if canvas.autoflush:  # Si 'autoflush' está activado...
                _root.update()  # Actualiza la interfaz gráfica.
           
    def _reconfig(self, option, setting):  # Método privado para cambiar la configuración del objeto.
        # Lanza un error si la opción no es válida para este objeto.
        if option not in self.config:  # Si la opción no está en el diccionario de configuración...
            raise GraphicsError(UNSUPPORTED_METHOD)  # Lanza error por método no soportado.
        options = self.config  # Obtiene el diccionario de configuración.
        options[option] = setting  # Actualiza el valor de la opción.
        if self.canvas and not self.canvas.isClosed():  # Si el objeto está dibujado y el lienzo abierto...
            self.canvas.itemconfig(self.id, options)  # Aplica la nueva configuración al objeto en el lienzo.
            if self.canvas.autoflush:  # Si 'autoflush' está activado...
                _root.update()  # Actualiza la interfaz gráfica.
                
    def _draw(self, canvas, options):
    # Método base para dibujar en el canvas; se implementa en cada subclase
     pass


    def _move(self, dx, dy):
    # Método base para mover el objeto; se implementa en cada subclase
        pass


class Point(GraphicsObject):
    """
    Representa un punto en coordenadas (x, y).
    Hereda de GraphicsObject para poder dibujarse y moverse en el canvas.
    """
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline  # Para uniformidad: fill y outline usan el mismo método
        self.x = x
        self.y = y

    def _draw(self, canvas, options):
        # Convierte coordenadas del mundo a coordenadas de pantalla y dibuja un rectángulo mínimo (1x1 píxel)
        x, y = canvas.toScreen(self.x, self.y)
        return canvas.create_rectangle(x, y, x + 1, y + 1, options)

    def _move(self, dx, dy):
        # Simplemente actualiza las coordenadas del punto
        self.x = self.x + dx
        self.y = self.y + dy

    def clone(self):
        # Devuelve una copia independiente del punto, copiando también la configuración gráfica
        other = Point(self.x, self.y)
        other.config = self.config.copy()
        return other

    def getX(self):
        return self.x

    def getY(self):
        return self.y


class _BBox(GraphicsObject):
    """
    Clase interna para cajas delimitadoras (bounding boxes).
    No se dibuja directamente; sus subclases (Rectangle, Oval, Line, etc.) implementan _draw.
    """
    def __init__(self, p1, p2, options=["outline", "width", "fill"]):
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()  # Punto superior-izquierdo o similar
        self.p2 = p2.clone()  # Punto inferior-derecho o similar

    def _move(self, dx, dy):
        # Mueve ambos puntos que definen la caja
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y + dy

    def getP1(self):
        # Devuelve una copia de p1
        return self.p1.clone()

    def getP2(self):
        # Devuelve una copia de p2
        return self.p2.clone()

    def getCenter(self):
        # Calcula el punto central de la caja
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)


class Rectangle(_BBox):
    """
    Rectángulo definido por dos puntos (p1 y p2).
    Hereda de _BBox para manejar la posición y tamaño.
    """
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def _draw(self, canvas, options):
        # Obtiene coordenadas en pantalla y dibuja el rectángulo
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_rectangle(x1, y1, x2, y2, options)

    def clone(self):
        # Crea una copia independiente del rectángulo, incluyendo configuración
        other = Rectangle(self.p1, self.p2)
        other.config = self.config.copy()
        return other


class Oval(_BBox):
    """
    Óvalo inscrito en la caja definida por p1 y p2.
    Similar a Rectangle pero dibuja un óvalo.
    """
    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def clone(self):
        other = Oval(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        # Convierte a coordenadas de pantalla y dibuja el óvalo
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_oval(x1, y1, x2, y2, options)


class Circle(Oval):
    """
    Círculo definido por un centro y un radio. Internamente se construye como un Oval cuyos extremos
    corresponden al cuadrado circunscrito alrededor del círculo.
    """
    def __init__(self, center, radius):
        # Calcula los puntos opuestos de la caja circunscrita
        p1 = Point(center.x - radius, center.y - radius)
        p2 = Point(center.x + radius, center.y + radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def clone(self):
        # Clona el círculo replicando centro y radio
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other

    def getRadius(self):
        return self.radius


class Line(_BBox):
    """
    Línea entre dos puntos p1 y p2. Permite configurar flechas en los extremos.
    Hereda de _BBox para manejar posiciones, pero dibuja un segmento de línea.
    """
    def __init__(self, p1, p2):
        # Opción 'arrow' además de 'fill' y 'width' para especificar flechas
        _BBox.__init__(self, p1, p2, ["arrow", "fill", "width"])
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill  # Alias para uniformidad

    def clone(self):
        other = Line(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        # Dibuja una línea en pantalla entre las coordenadas calculadas
        p1 = self.p1
        p2 = self.p2
        x1, y1 = canvas.toScreen(p1.x, p1.y)
        x2, y2 = canvas.toScreen(p2.x, p2.y)
        return canvas.create_line(x1, y1, x2, y2, options)

    def setArrow(self, option):
        # Permite configurar si la línea tendrá flechas en comienzo/fin/ambos/no
        if not option in ["first", "last", "both", "none"]:
            raise GraphicsError(BAD_OPTION)
        self._reconfig("arrow", option)


class Polygon(GraphicsObject):
    """
    Polígono definido por una lista de puntos arbitrarios.
    Hereda de GraphicsObject para dibujarse y moverse.
    """
    def __init__(self, *points):
        # Si pasan una única lista como argumento, la desenvuelve
        if len(points) == 1 and type(points[0]) == type([]):
            points = points[0]
        self.points = list(map(Point.clone, points))
        GraphicsObject.__init__(self, ["outline", "width", "fill"])

    def clone(self):
        other = Polygon(*self.points)
        other.config = self.config.copy()
        return other

    def getPoints(self):
        # Devuelve copias de los puntos que conforman el polígono
        return list(map(Point.clone, self.points))

    def _move(self, dx, dy):
        # Mueve todos los vértices del polígono
        for p in self.points:
            p.move(dx, dy)

    def _draw(self, canvas, options):
        # Construye una lista de coordenadas en pantalla y crea el polígono
        args = [canvas]
        for p in self.points:
            x, y = canvas.toScreen(p.x, p.y)
            args.append(x)
            args.append(y)
        args.append(options)
        return GraphWin.create_polygon(*args)


class Text(GraphicsObject):
    """
    Texto que se dibuja anclado en un punto (anchor).
    Permite configurar fuente, tamaño, estilo y color.
    """
    def __init__(self, p, text):
        GraphicsObject.__init__(self, ["justify", "fill", "text", "font"])
        self.setText(text)
        self.anchor = p.clone()
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill  # Alias para uniformidad

    def _draw(self, canvas, options):
        # Convierte coordenadas y dibuja el texto en la posición especificada
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        return canvas.create_text(x, y, options)

    def _move(self, dx, dy):
        # Mueve el punto ancla que define la posición del texto
        self.anchor.move(dx, dy)

    def clone(self):
        # Clona el objeto Text, copiando texto, fuente y configuración
        other = Text(self.anchor, self.config['text'])
        other.config = self.config.copy()
        return other

    def setText(self, text):
        self._reconfig("text", text)

    def getText(self):
        return self.config["text"]

    def getAnchor(self):
        return self.anchor.clone()

    def setFace(self, face):
        # Cambia la fuente, si es válida
        if face in ['helvetica', 'arial', 'courier', 'times roman']:
            f, s, b = self.config['font']
            self._reconfig("font", (face, s, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        # Ajusta tamaño de fuente dentro de rango permitido
        if 5 <= size <= 36:
            f, s, b = self.config['font']
            self._reconfig("font", (f, size, b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        # Cambia estilo de fuente (normal, bold, italic, etc.)
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            f, s, b = self.config['font']
            self._reconfig("font", (f, s, style))
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        # Alias para setFill
        self.setFill(color)


class Entry(GraphicsObject):
    """
    Campo de entrada de texto interactivo (widget de Tkinter).
    Permite ingresar texto dentro del canvas.
    """
    def __init__(self, p, width):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        self.width = width
        self.text = tk.StringVar(_root)
        self.text.set("")
        self.fill = "gray"
        self.color = "black"
        self.font = DEFAULT_CONFIG['font']
        self.entry = None  # Se inicializa al dibujarse

    def _draw(self, canvas, options):
        # Crea un Frame y dentro un Entry de Tkinter, luego lo coloca en el canvas
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        frm = tk.Frame(canvas.master)
        self.entry = tk.Entry(
            frm,
            width=self.width,
            textvariable=self.text,
            bg=self.fill,
            fg=self.color,
            font=self.font
        )
        self.entry.pack()
        return canvas.create_window(x, y, window=frm)

    def getText(self):
        return self.text.get()

    def _move(self, dx, dy):
        # Mueve el campo de entrada ajustando su ancla
        self.anchor.move(dx, dy)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        # Clona el Entry copiando estado, texto y configuración gráfica
        other = Entry(self.anchor, self.width)
        other.config = self.config.copy()
        other.text = tk.StringVar()
        other.text.set(self.text.get())
        other.fill = self.fill
        return other

    def setText(self, t):
        self.text.set(t)

    def setFill(self, color):
        # Cambia el color de fondo del Entry (si ya está dibujado, actualiza el widget)
        self.fill = color
        if self.entry:
            self.entry.config(bg=color)

    def _setFontComponent(self, which, value):
        # Auxiliar para cambiar un componente de la tupla (font family, size o style)
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.entry:
            self.entry.config(font=self.font)

    def setFace(self, face):
        if face in ['helvetica', 'arial', 'courier', 'times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1, size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold', 'normal', 'italic', 'bold italic']:
            self._setFontComponent(2, style)
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.color = color
        if self.entry:
            self.entry.config(fg=color)


class Image(GraphicsObject):
    """
    Representa una imagen (PhotoImage de Tkinter) anclada en un punto.
    Soporta operaciones como dibujar, mover, obtener píxeles y guardarla en disco.
    """
    idCount = 0
    imageCache = {}  # Mantiene una referencia para evitar que el garbage collector elimine la imagen

    def __init__(self, p, *pixmap):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        self.imageId = Image.idCount
        Image.idCount = Image.idCount + 1
        if len(pixmap) == 1:  # Si se pasa un nombre de archivo
            self.img = tk.PhotoImage(file=pixmap[0], master=_root)
        else:  # Si se pasan ancho y alto para crear imagen en blanco
            width, height = pixmap
            self.img = tk.PhotoImage(master=_root, width=width, height=height)

    def _draw(self, canvas, options):
        # Dibuja la imagen en las coordenadas convertidas
        p = self.anchor
        x, y = canvas.toScreen(p.x, p.y)
        self.imageCache[self.imageId] = self.img  # Guarda referencia
        return canvas.create_image(x, y, image=self.img)

    def _move(self, dx, dy):
        # Ajusta el ancla para mover la imagen
        self.anchor.move(dx, dy)

    def undraw(self):
        # Elimina la referencia para permitir que Python libere la memoria de la imagen
        try:
            del self.imageCache[self.imageId]
        except KeyError:
            pass
        GraphicsObject.undraw(self)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        # Clona la imagen copiando el PhotoImage y la posición
        other = Image(Point(0, 0), 0, 0)
        other.img = self.img.copy()
        other.anchor = self.anchor.clone()
        other.config = self.config.copy()
        return other

    def getWidth(self):
        """Devuelve el ancho de la imagen en píxeles."""
        return self.img.width()

    def getHeight(self):
        """Devuelve el alto de la imagen en píxeles."""
        return self.img.height()

    def getPixel(self, x, y):
        """
        Retorna una lista [r, g, b] con los valores RGB del píxel (x, y).
        Dependiendo del tipo de valor obtenido, lo formatea apropiadamente.
        """
        value = self.img.get(x, y)
        if type(value) == type(0):
            return [value, value, value]  # Escala de grises
        elif type(value) == type((0, 0, 0)):
            return list(value)  # Tupla RGB
        else:
            # A veces devuelve cadena, p.ej. "255 128 0"
            return list(map(int, value.split()))

    def setPixel(self, x, y, color):
        """Establece el píxel (x, y) al color dado en formato hexadecimal o nombre."""
        self.img.put("{" + color + "}", (x, y))

    def save(self, filename):
        """
        Guarda la imagen en disco. El formato se deduce de la extensión del nombre de archivo.
        (p.ej. ".png", ".gif", etc.)
        """
        path, name = os.path.split(filename)
        ext = name.split(".")[-1]
        self.img.write(filename, format=ext)


def color_rgb(r, g, b):
    """
    Convierte tres valores enteros (0-255) de rojo, verde y azul a una cadena
    hexadecimal que Tkinter entiende, e.g. "#FFA500" para naranja.
    """
    return "#%02x%02x%02x" % (r, g, b)


def test():
    """
    Función de prueba que crea una ventana, dibuja varios objetos,
    interactúa con el usuario y muestra cómo funcionan los métodos.
    """
    win = GraphWin()
    win.setCoords(0, 0, 10, 10)

    # Texto centrado
    t = Text(Point(5, 5), "Centered Text")
    t.draw(win)

    # Polígono simple
    p = Polygon(Point(1, 1), Point(5, 3), Point(2, 7))
    p.draw(win)

    # Campo de entrada
    e = Entry(Point(5, 6), 10)
    e.draw(win)

    win.getMouse()  # Espera clic antes de continuar

    # Cambia color de relleno y contorno del polígono
    p.setFill("red")
    p.setOutline("blue")
    p.setWidth(2)

    # Construye cadena con coordenadas de vértices
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())

    t.setText(e.getText())  # Muestra en el texto lo ingresado en el Entry
    e.setFill("green")
    e.setText("Spam!")
    e.move(2, 0)

    win.getMouse()

    # Mueve el polígono y actualiza texto con nuevas coordenadas
    p.move(2, 3)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(s)

    win.getMouse()
    p.undraw()
    e.undraw()

    # Cambia estilos de texto secuencialmente
    t.setStyle("bold")
    win.getMouse()
    t.setStyle("normal")
    win.getMouse()
    t.setStyle("italic")
    win.getMouse()
    t.setStyle("bold italic")
    win.getMouse()

    # Ajusta tamaño y fuente del texto
    t.setSize(14)
    win.getMouse()
    t.setFace("arial")
    t.setSize(20)
    win.getMouse()

    win.close()


if __name__ == "__main__":
    test()

