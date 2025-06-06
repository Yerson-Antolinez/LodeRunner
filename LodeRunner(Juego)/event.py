class Event:
    """
    Clase para gestionar eventos temporizados basados en frames.
    Permite programar funciones para que se ejecuten después de un número específico de frames,
    con soporte para eventos recurrentes.
    """

    _queue = {}  # Diccionario que almacena listas de eventos programados para cada frame futuro
    _frame = 0   # Contador del frame actual

    @staticmethod
    def _enqueue(obj):
        """
        Agrega un evento a la cola para ser ejecutado en un frame futuro.

        :param obj: Instancia de Event a encolar.
        """
        # Calcula el frame en el que el evento debe ejecutarse sumando el frame actual y el delay en frames
        target_frame = Event._frame + obj.frames
        if target_frame in Event._queue:
            # Si ya hay eventos para ese frame, agrega el nuevo evento a la lista
            Event._queue[target_frame].append(obj)
        else:
            # Si no hay eventos para ese frame, crea una nueva lista con el evento
            Event._queue[target_frame] = [obj]

    @staticmethod
    def update():
        """
        Procesa los eventos programados para el frame actual y avanza el contador de frames.
        """
        if Event._frame in Event._queue:
            # Obtiene la lista de eventos para el frame actual
            for event in Event._queue[Event._frame]:
                # Ejecuta el evento y obtiene un posible nuevo evento (para recurrencia)
                new_event = event.execute()
                if new_event:
                    # Si hay un nuevo evento (recurrente), lo vuelve a encolar
                    Event._enqueue(new_event)
            # Elimina la entrada del frame actual de la cola
            del Event._queue[Event._frame]
        # Avanza al siguiente frame
        Event._frame += 1

    @staticmethod
    def delete(event):
        """
        Elimina un evento específico de la cola de eventos.

        :param event: Instancia de Event a eliminar.
        """
        # Busca el evento en todas las listas de la cola
        for event_list in Event._queue.values():
            if event in event_list:
                # Si encuentra el evento, lo elimina de la lista
                event_list.remove(event)

    def __init__(self, func, frames, args=[], recurring=None):
        """
        Inicializa un nuevo evento.

        :param func: Función a ejecutar cuando el evento se dispare.
        :param frames: Número de frames después del cual se ejecutará el evento.
        :param args: Lista de argumentos para pasar a la función.
        :param recurring: Si es True, el evento se repetirá indefinidamente.
                          Si es un entero, especifica el número de repeticiones.
                          Por defecto, None (no recurrente).
        """
        self.func = func          # Función a llamar
        self.args = args          # Argumentos para la función
        self.frames = frames      # Delay en frames antes de la ejecución
        if recurring:
            # Si es recurrente, guarda la instancia del evento para reenviarlo
            self.recurring = self
        else:
            self.recurring = None
        # Agrega el evento a la cola inmediatamente
        Event._enqueue(self)

    def execute(self):
        """
        Ejecuta la función asociada al evento y maneja la recurrencia.

        :return: El evento recurrente si corresponde, de lo contrario None.
        """
        # Llama a la función con los argumentos proporcionados
        self.func(*self.args)
        # Devuelve el evento recurrente si está configurado
        return self.recurring