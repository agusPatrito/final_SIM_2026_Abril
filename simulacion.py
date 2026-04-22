import random
import heapq

class SimulacionRapipago:
    def __init__(self, llegada_tel_media=100, llegada_tel_var=70, 
                 llegada_gas_media=80, llegada_gas_var=30,
                 atencion_media=45, atencion_var=20,
                 max_clientes=800):
        """
        Inicializa los parámetros de la simulación.
        Los tiempos están dados en segundos, distribuidos uniformemente U(media - var, media + var).
        """
        self.tel_min = llegada_tel_media - llegada_tel_var
        self.tel_max = llegada_tel_media + llegada_tel_var
        self.gas_min = llegada_gas_media - llegada_gas_var
        self.gas_max = llegada_gas_media + llegada_gas_var
        self.ate_min = atencion_media - atencion_var
        self.ate_max = atencion_media + atencion_var
        
        self.max_clientes_atendidos = max_clientes
        self.reset_estadisticas()

    def reset_estadisticas(self):
        # Estado del sistema
        self.tiempo_actual = 0.0
        self.servidor_ocupado = False
        self.cola = []  # Cola FIFO: list de dicts {'llegada': float, 'tipo': str}
        self.eventos = []  # HeapQ para procesar en orden de tiempo: (tiempo, tipo, cliente_tipo)
        
        # Cliente actualmente siendo atendido
        self.cliente_en_servicio = None
        
        # Estadísticas solicitadas
        self.longitud_maxima_cola = 0
        self.tiempo_espera_tel_total = 0.0
        self.clientes_tel_atendidos = 0
        self.tiempo_espera_gas_total = 0.0
        self.clientes_gas_atendidos = 0
        self.total_atendidos = 0
        self.tabla_eventos = []

    def get_tiempo_llegada_tel(self):
        return random.uniform(self.tel_min, self.tel_max)

    def get_tiempo_llegada_gas(self):
        return random.uniform(self.gas_min, self.gas_max)

    def get_tiempo_atencion(self):
        return random.uniform(self.ate_min, self.ate_max)

    def agregar_evento(self, tiempo, tipo, tipo_cliente=None):
        """Agrega un evento a la lista de eventos futuros ordenada por tiempo."""
        heapq.heappush(self.eventos, (tiempo, tipo, tipo_cliente))

    def procesar_llegada(self, tipo_cliente):
        """Lógica a ejecutar cuando llega un cliente."""
        # Siempre programamos la SÍGUIENTE llegada de este tipo
        prox_llegada = self.get_tiempo_llegada_tel() if tipo_cliente == 'telefono' else self.get_tiempo_llegada_gas()
        self.agregar_evento(self.tiempo_actual + prox_llegada, 'llegada', tipo_cliente)

        if self.servidor_ocupado:
            # Hay que hacer cola
            self.cola.append({'llegada': self.tiempo_actual, 'tipo': tipo_cliente})
            # Actualizamos estadística de tamaño máximo
            if len(self.cola) > self.longitud_maxima_cola:
                self.longitud_maxima_cola = len(self.cola)
        else:
            # El servidor está libre, pasa directo sin esperar
            self.servidor_ocupado = True
            self.cliente_en_servicio = {'llegada': self.tiempo_actual, 'tipo': tipo_cliente, 'espera': 0.0}
            
            # Programamos cuándo termina esta atención
            self.agregar_evento(self.tiempo_actual + self.get_tiempo_atencion(), 'fin_atencion')

    def procesar_fin_atencion(self):
        """Lógica a ejecutar cuando el servidor termina con un cliente."""
        # Se registra al cliente que acaba de finalizar
        if self.cliente_en_servicio:
            if self.cliente_en_servicio['tipo'] == 'telefono':
                self.tiempo_espera_tel_total += self.cliente_en_servicio['espera']
                self.clientes_tel_atendidos += 1
            else:
                self.tiempo_espera_gas_total += self.cliente_en_servicio['espera']
                self.clientes_gas_atendidos += 1
            
            self.total_atendidos += 1

        # ¿Hay gente esperando en la cola?
        if len(self.cola) > 0:
            # Sacamos al primero (FIFO)
            siguiente = self.cola.pop(0)
            tiempo_esperado = self.tiempo_actual - siguiente['llegada']
            
            # Se empieza a atender a este cliente
            self.cliente_en_servicio = {'llegada': siguiente['llegada'], 'tipo': siguiente['tipo'], 'espera': tiempo_esperado}
            
            # Programamos cuándo termina
            self.agregar_evento(self.tiempo_actual + self.get_tiempo_atencion(), 'fin_atencion')
        else:
            # No hay nadie más, el servidor queda libre
            self.servidor_ocupado = False
            self.cliente_en_servicio = None

    def ejecutar(self):
        """
        Motor principal de la simulación de eventos discretos.
        """
        self.reset_estadisticas()
        
        # Iniciar las semillas (primeras llegadas)
        self.agregar_evento(self.get_tiempo_llegada_tel(), 'llegada', 'telefono')
        self.agregar_evento(self.get_tiempo_llegada_gas(), 'llegada', 'gas')
        
        # Bucle principal: sacar el siguiente evento mientras no hayamos atendido a los 800
        while self.total_atendidos < self.max_clientes_atendidos:
            if not self.eventos:
                break # Por seguridad, aunque en teoría siempre hay eventos de llegada futuros
                
            tiempo_evento, tipo_evento, tipo_cliente = heapq.heappop(self.eventos)
            
            # Solo saltamos en el tiempo si el evento es futuro (por cómo modelamos, siempre debería ser >=)
            self.tiempo_actual = tiempo_evento
            
            if tipo_evento == 'llegada':
                self.procesar_llegada(tipo_cliente)
            elif tipo_evento == 'fin_atencion':
                self.procesar_fin_atencion()
                
            # Registrar vector de estado para mostrar la tabla
            prox_tel = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'telefono']
            prox_gas = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'gas']
            prox_fin = [ev[0] for ev in self.eventos if ev[1] == 'fin_atencion']
            
            self.tabla_eventos.append({
                'reloj': round(self.tiempo_actual, 2),
                'evento': f"{tipo_evento}_{tipo_cliente}" if tipo_cliente else tipo_evento,
                'prox_tel': round(min(prox_tel), 2) if prox_tel else "-",
                'prox_gas': round(min(prox_gas), 2) if prox_gas else "-",
                'prox_fin': round(min(prox_fin), 2) if prox_fin else "-",
                'estado_servidor': 'Ocupado' if self.servidor_ocupado else 'Libre',
                'cola': len(self.cola),
                'total_atendidos': self.total_atendidos
            })
                
        # Calculamos estadísticas finales
        promedio_espera_tel = self.tiempo_espera_tel_total / self.clientes_tel_atendidos if self.clientes_tel_atendidos > 0 else 0
        promedio_espera_gas = self.tiempo_espera_gas_total / self.clientes_gas_atendidos if self.clientes_gas_atendidos > 0 else 0
        
        # Devolver resultados encapsulados en un diccionario
        return {
            'max_cola': self.longitud_maxima_cola,
            'promedio_espera_tel': promedio_espera_tel,
            'promedio_espera_gas': promedio_espera_gas,
            'total_clientes': self.total_atendidos,
            'clientes_tel': self.clientes_tel_atendidos,
            'clientes_gas': self.clientes_gas_atendidos,
            'tiempo_simulado': self.tiempo_actual,
            'tabla': self.tabla_eventos
        }
