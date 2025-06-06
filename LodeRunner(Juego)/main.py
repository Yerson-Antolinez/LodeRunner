import time                # Para usar funciones de tiempo, como time.sleep() o medir intervalos
from config import Config  # Importa la clase Config definida en config.py para cargar parámetros de configuración
from graphics import *     # Importa todas las clases y funciones del módulo graphics (p.ej. GraphWin, Point, Rectangle, etc.)


 # GraphWin, Point, etc. graphics.py ya maneja tk
from drawable import Drawable
from tiles import Tile, Gold, HiddenLadder
from characters import Player, Baddie, Character # Importar Player y Baddie explícitamente
from event import Event


# La función load_level la definiremos dentro de main o antes, para que tenga acceso a Player, etc.
# Ya no necesitamos una función load_level global aquí si la integramos en el bucle de main.

move_cooldown = 0.15  # segundos entre movimientos
last_move_time = 0

KEYMAP = {
    'Left':     lambda: Player.main.move(-1, 0) if Player.main else None, # ### MODIFICADO ###
    'Right':    lambda: Player.main.move(1, 0) if Player.main else None,  # ### MODIFICADO ###
    'Up':       lambda: Player.main.move(0, -1) if Player.main else None,  # ### MODIFICADO ###
    'Down':     lambda: Player.main.move(0, 1) if Player.main else None,   # ### MODIFICADO ###
    'z':        lambda: Player.main.dig(-1) if Player.main else None,     # ### MODIFICADO ###
    'c':        lambda: Player.main.dig(1) if Player.main else None,      # ### MODIFICADO ###
    'q':        lambda: exit_game(), # ### MODIFICADO ###
    # 'escape':   lambda: exit_game() 
}

LEVELS = [1, 2] 

# ### NUEVA FUNCIÓN ###
def exit_game():
    if Drawable._window and not Drawable._window.isClosed():
        Drawable._window.close()
    exit(0)

def main_game_loop():
    global last_move_time
    frame_duration = 1.0/60.0 # Apunta a 60 FPS
    

    # Inicialización de la ventana la primera vez
    
    
    # El jugador mantiene sus vidas entre niveles en esta implementación
    # Player.main se crea en Character.load_characters
    # Nos aseguraremos de que las vidas se inicialicen correctamente la primera vez.

    current_player_lives = Player.INITIAL_LIVES # Se usará para la primera creación del jugador

    for level_num in LEVELS:
        print(f"Loading level {level_num}...")
        # Configurar y cargar el nivel
        Config.config_level(level_num)
        Drawable.recreateWindow() # Esto crea/recrea la ventana
        Tile.load_level(level_num)
        
        # Cargar personajes. Player.main se creará o actualizará aquí.
        # Si Player.main ya existe de un nivel anterior, sus vidas se mantienen.
        # Si es la primera vez, se inicializarán.
        Character.load_characters(level_num)

        if not Player.main:
            print("Error: Player.main no fue creado después de load_characters.")
            return # Salir si no hay jugador

        # Si es el primer nivel, o si queremos resetear las vidas al inicio de cada nivel (opcional):
        # if level_num == LEVELS[0]: # O simplemente siempre al cargar nivel
        # Player.main.lives = Player.INITIAL_LIVES # Esto ya se maneja en Player.__init__ con is_initial_load

        print(f"Starting level {level_num} with {Player.main.lives} lives.")

        level_running = True
        while level_running: # Bucle para el nivel actual, permite reintentos si se pierde una vida
            
            if Player.main.lives <= 0: # Si el jugador se quedó sin vidas en un intento anterior
                print("Game Over - No lives left.")
                Drawable.lost() # Esto llamará a la pantalla de Game Over y saldrá
                return # Salir de la función main_game_loop

            # Mostrar vidas al inicio del intento de nivel o después de respawn
            Drawable.update_lives_display(Player.main.lives)

            # Bucle principal del juego para el intento actual del nivel
            while not Player.main.at_exit():
                frame_start_time = time.time()

                if Drawable._window.isClosed(): # Si la ventana se cierra externamente
                    print("Window closed, exiting game.")
                    return

                key = Drawable._window.checkKey()

                now = time.time()
                if key in KEYMAP and (now - last_move_time) > move_cooldown:
                     KEYMAP[key]()

                     last_move_time = now
 # Llamar a la lambda

                Event.update() # Actualizar eventos programados (movimiento de baddies, relleno de hoyos)

                # Lógica de HiddenLadder y redraws
                if not Config.hidden_flag:
                    if Gold.all_taken():
                        HiddenLadder.showAll()
                        if Player.main: Player.main.redraw() # Redibujar jugador
                        for baddie in Baddie.baddies: # Redibujar baddies
                            baddie.redraw()
                        Config.hidden_flag = True
                
                # Comprobar si el jugador ha perdido una vida
                # La lógica de perder vida ya está en Player y Baddie,
                # y Player.lose_life() maneja el respawn o Drawable.lost()
                # Necesitamos una forma de romper este bucle interno si el jugador
                # pierde una vida para reiniciar el intento del nivel (respawn).
                # La función Player.lose_life() llama a respawn() o Drawable.lost().
                # Si llama a respawn(), el juego continúa en este mismo bucle.
                # Si llama a Drawable.lost(), el juego termina.
                
                # Si el jugador se quedó sin vidas, Player.lose_life() habrá llamado a Drawable.lost(),
                # lo que termina el juego. Así que no necesitamos un chequeo explícito aquí para eso.

                # Si el jugador fue "muerto" (ej. por un baddie o cayendo en hoyo rellenado),
                # el método lose_life() del Player ya habrá sido llamado.
                # Si tenía vidas, habrá llamado a respawn(). El juego sigue.
                # Si no tenía vidas, Drawable.lost() habrá terminado el juego.

                # Actualizar display de vidas en cada frame, por si cambia
                # (aunque solo cambia cuando se pierde una vida)
                # Es más eficiente llamarlo solo cuando `player.lives` cambia,
                # pero para simplificar, lo podemos llamar aquí.
                # O, mejor aún, Player.lose_life() podría encargarse de llamar a update_lives_display.
                # Drawable.update_lives_display(Player.main.lives) # Ya lo hace Player.lose_life/respawn

                frame_time = time.time() - frame_start_time
                if frame_time < frame_duration:
                    time.sleep(frame_duration - frame_time)
                
                # Si el jugador se quedó sin vidas y Drawable.lost() fue llamado, el programa ya habrá salido.
                # Si el jugador perdió una vida y respawneó, el bucle continúa.
                # Si el jugador llegó a la salida, el bucle `while not Player.main.at_exit()` termina.

            # Si salimos del bucle `while not Player.main.at_exit()`:
            if Player.main.at_exit():
                print(f"Level {level_num} completed!")
                level_running = False # Salir del bucle del nivel actual para pasar al siguiente
                if level_num == LEVELS[-1]: # Si es el último nivel
                    Drawable.won() # Mostrar pantalla de victoria final
                    # Esperar un poco antes de cerrar o permitir que el jugador cierre
                    time.sleep(2)
                    exit_game() 
                else:
                    temp_text = Text(Point(Config.WINDOW_WIDTH/2+10, Config.WINDOW_HEIGHT/2+10), f'1 Superado')
                    temp_text.setSize(24)
                    temp_text.setTextColor('Red')
                    if Drawable._window and not Drawable._window.isClosed():
                        temp_text.draw(Drawable._window)
                        Drawable._window.update()
                        time.sleep(2) # Mostrar mensaje por 2 segundos
                        temp_text.undraw()
            # else: # Si no está en la salida, implica que perdió todas las vidas y Drawable.lost() ya manejó

    # Si el bucle de niveles termina (porque se completaron todos)
    print("Ganaste.")
    # Drawable.won() ya se llamó si fue el último nivel.
    # Si no hubo niveles, o por alguna otra razón, asegurar cierre limpio.
    if Drawable._window and not Drawable._window.isClosed():
       
        pass

# Punto de entrada
if __name__ == '__main__':
    try:
        main_game_loop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Asegurarse de que la ventana se cierre si no se hizo ya
        if Drawable._window and not Drawable._window.isClosed():
            Drawable._window.close()
        print("Game exited.")