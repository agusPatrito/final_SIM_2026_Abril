import random
import heapq

class SimulacionRapipago:
    def __init__(self, llegada_tel_media=100, llegada_tel_var=70,
                 llegada_gas_media=80, llegada_gas_var=30,
                 atencion_media=45, atencion_var=20,
                 max_clientes=800):

        self.tel_min = llegada_tel_media - llegada_tel_var
        self.tel_max = llegada_tel_media + llegada_tel_var
        self.gas_min = llegada_gas_media - llegada_gas_var
        self.gas_max = llegada_gas_media + llegada_gas_var
        self.ate_min = atencion_media - atencion_var
        self.ate_max = atencion_media + atencion_var

        self.max_clientes_atendidos = max_clientes
        self.reset_estadisticas()

    def reset_estadisticas(self):
        self.tiempo_actual = 0.0
        self.servidor_ocupado = False
        self.cola = []       # [{'id', 'llegada', 'tipo'}]
        self.eventos = []    # heap (tiempo, tipo, cliente_tipo)

        self.cliente_en_servicio = None   # {'id', 'llegada', 'tipo', 'espera'}

        # Objetos temporales de clientes
        self.contador_clientes = 0
        self.clientes_activos = {}   # id -> {'id', 'tipo', 'llegada', 'estado'}

        # Estadísticas
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
        heapq.heappush(self.eventos, (tiempo, tipo, tipo_cliente))


    def _snapshot_clientes(self):
        """En atención primero, luego cola en orden de llegada."""
        orden = {'En atención': 0, 'En cola': 1}
        return sorted(
            [dict(c) for c in self.clientes_activos.values()],
            key=lambda c: (orden.get(c['estado'], 9), c['llegada'])
        )


    def procesar_llegada(self, tipo_cliente):

        self.contador_clientes += 1
        id_c = self.contador_clientes


        prox = (self.get_tiempo_llegada_tel() if tipo_cliente == 'telefono'
                else self.get_tiempo_llegada_gas())
        self.agregar_evento(self.tiempo_actual + prox, 'llegada', tipo_cliente)

        if self.servidor_ocupado:
            self.clientes_activos[id_c] = {
                'id': id_c, 'tipo': tipo_cliente,
                'llegada': round(self.tiempo_actual, 2), 'estado': 'En cola'
            }
            self.cola.append({'id': id_c, 'llegada': self.tiempo_actual, 'tipo': tipo_cliente})
            if len(self.cola) > self.longitud_maxima_cola:
                self.longitud_maxima_cola = len(self.cola)
        else:
            self.clientes_activos[id_c] = {
                'id': id_c, 'tipo': tipo_cliente,
                'llegada': round(self.tiempo_actual, 2), 'estado': 'En atención'
            }
            self.servidor_ocupado = True
            self.cliente_en_servicio = {
                'id': id_c, 'llegada': self.tiempo_actual,
                'tipo': tipo_cliente, 'espera': 0.0
            }
            self.agregar_evento(self.tiempo_actual + self.get_tiempo_atencion(), 'fin_atencion')

    def procesar_fin_atencion(self):
        if self.cliente_en_servicio:
            c = self.cliente_en_servicio
            if c['tipo'] == 'telefono':
                self.tiempo_espera_tel_total += c['espera']
                self.clientes_tel_atendidos += 1
            else:
                self.tiempo_espera_gas_total += c['espera']
                self.clientes_gas_atendidos += 1
            self.total_atendidos += 1
            # Remover objeto temporal del cliente atendido
            self.clientes_activos.pop(c['id'], None)

        if self.cola:
            siguiente = self.cola.pop(0)
            espera = self.tiempo_actual - siguiente['llegada']
            self.cliente_en_servicio = {
                'id': siguiente['id'], 'llegada': siguiente['llegada'],
                'tipo': siguiente['tipo'], 'espera': espera
            }
            # Actualizar estado del objeto temporal
            self.clientes_activos[siguiente['id']]['estado'] = 'En atención'
            self.agregar_evento(self.tiempo_actual + self.get_tiempo_atencion(), 'fin_atencion')
        else:
            self.servidor_ocupado = False
            self.cliente_en_servicio = None


    def ejecutar(self):
        self.reset_estadisticas()

        self.agregar_evento(self.get_tiempo_llegada_tel(), 'llegada', 'telefono')
        self.agregar_evento(self.get_tiempo_llegada_gas(), 'llegada', 'gas')

        prox_tel_init = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'telefono']
        prox_gas_init = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'gas']
        self.tabla_eventos.append({
            'reloj': 0,
            'evento': 'inicializacion',
            'prox_tel': round(min(prox_tel_init), 2) if prox_tel_init else '-',
            'prox_gas': round(min(prox_gas_init), 2) if prox_gas_init else '-',
            'prox_fin': '-',
            'estado_servidor': 'Libre',
            'cola': 0,
            'total_atendidos': 0,
            'clientes': [],
        })

        while self.total_atendidos < self.max_clientes_atendidos:
            if not self.eventos:
                break

            tiempo_evento, tipo_evento, tipo_cliente = heapq.heappop(self.eventos)
            self.tiempo_actual = tiempo_evento

            if tipo_evento == 'llegada':
                self.procesar_llegada(tipo_cliente)
            elif tipo_evento == 'fin_atencion':
                self.procesar_fin_atencion()

            prox_tel = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'telefono']
            prox_gas = [ev[0] for ev in self.eventos if ev[1] == 'llegada' and ev[2] == 'gas']
            prox_fin = [ev[0] for ev in self.eventos if ev[1] == 'fin_atencion']

            self.tabla_eventos.append({
                'reloj': round(self.tiempo_actual, 2),
                'evento': f"{tipo_evento}_{tipo_cliente}" if tipo_cliente else tipo_evento,
                'prox_tel': round(min(prox_tel), 2) if prox_tel else '-',
                'prox_gas': round(min(prox_gas), 2) if prox_gas else '-',
                'prox_fin': round(min(prox_fin), 2) if prox_fin else '-',
                'estado_servidor': 'Ocupado' if self.servidor_ocupado else 'Libre',
                'cola': len(self.cola),
                'total_atendidos': self.total_atendidos,
                'clientes': self._snapshot_clientes(),
            })

        promedio_espera_tel = (self.tiempo_espera_tel_total / self.clientes_tel_atendidos
                               if self.clientes_tel_atendidos > 0 else 0)
        promedio_espera_gas = (self.tiempo_espera_gas_total / self.clientes_gas_atendidos
                               if self.clientes_gas_atendidos > 0 else 0)

        return {
            'max_cola': self.longitud_maxima_cola,
            'promedio_espera_tel': promedio_espera_tel,
            'promedio_espera_gas': promedio_espera_gas,
            'total_clientes': self.total_atendidos,
            'clientes_tel': self.clientes_tel_atendidos,
            'clientes_gas': self.clientes_gas_atendidos,
            'tiempo_simulado': self.tiempo_actual,
            'tabla': self.tabla_eventos,
        }
