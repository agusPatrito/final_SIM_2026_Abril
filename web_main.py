import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from simulacion import SimulacionRapipago

class SimHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Servir la interfaz gráfica HTML
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # HTML simple con CSS embebido y un poco de JS para llamar a la simulación
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simulador Rapipago - Final</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; color: #333;}
                    .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                    h1 { text-align: center; color: #2c3e50; }
                    .group { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
                    .group h3 { margin-top: 0; color: #34495e; font-size: 16px; }
                    .row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
                    .row label { flex: 1; font-weight: bold;}
                    .row input { width: 80px; padding: 6px; border: 1px solid #ccc; border-radius: 4px; text-align: center; }
                    .btn-run { display: block; width: 100%; padding: 12px; background: #3498db; color: white; border: none; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: 0.3s; }
                    .btn-run:hover { background: #2980b9; }
                    .results { margin-top: 20px; padding: 20px; background: #ecf0f1; border-radius: 8px; display: none;}
                    .res-item { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                    .val { font-weight: bold; color: #2c3e50; }
                    .small-info { font-size: 12px; color: #7f8c8d; margin-top: 15px; text-align: center; }
                    /* Estilos para la tabla */
                    .table-container { max-height: 400px; overflow-y: auto; margin-top: 25px; display: none; border-radius: 8px; border: 1px solid #ddd; }
                    table { width: 100%; border-collapse: collapse; font-size: 12px; }
                    th, td { border-bottom: 1px solid #ddd; padding: 8px; text-align: center; }
                    th { background-color: #2c3e50; color: white; position: sticky; top: 0; z-index: 10;}
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    tr:hover { background-color: #f1f1f1; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Simulador de Colas - Rapipago</h1>
                    
                    <div class="group">
                        <h3>Llegada de Clientes (Uniformes en seg.)</h3>
                        <div class="row">
                            <label>Teléfono (Media +/- Var):</label>
                            <div><input type="number" id="t_med" value="100"> +/- <input type="number" id="t_var" value="70"></div>
                        </div>
                        <div class="row">
                            <label>Gas (Media +/- Var):</label>
                            <div><input type="number" id="g_med" value="80"> +/- <input type="number" id="g_var" value="30"></div>
                        </div>
                    </div>
                    
                    <div class="group">
                        <h3>Tiempo de Atención del Servidor</h3>
                        <div class="row">
                            <label>Atención (Media +/- Var):</label>
                            <div><input type="number" id="a_med" value="45"> +/- <input type="number" id="a_var" value="20"></div>
                        </div>
                    </div>
                    
                    <div class="group">
                        <h3>Condición de Fin</h3>
                        <div class="row">
                            <label>Atenciones completadas:</label>
                            <input type="number" id="clientes" value="800">
                        </div>
                    </div>

                    <button class="btn-run" onclick="correr()">EJECUTAR SIMULACIÓN</button>

                    <div id="aviso" style="display:none; margin-top:12px; padding:10px 14px;
                         border-left:4px solid #c0392b; background:#fdecea; color:#c0392b;
                         border-radius:4px; font-size:13px; white-space:pre-line;"></div>
                    
                    <div class="results" id="res_box">
                        <div class="res-item"><span>Max. personas en cola:</span> <span class="val" id="r_cola"></span></div>
                        <div class="res-item"><span>Promedio espera Teléfono:</span> <span class="val" id="r_tel"></span></div>
                        <div class="res-item"><span>Promedio espera Gas:</span> <span class="val" id="r_gas"></span></div>
                        <div class="small-info" id="r_extra"></div>
                    </div>
                    
                    <div class="table-container" id="tabla_box">
                        <table>
                            <thead><tr><th>Reloj</th><th>Evento</th><th>P. L. Tel</th><th>P. L. Gas</th><th>P. Fin Ate</th><th>Servidor</th><th>Cola</th><th>Atendidos</th></tr></thead>
                            <tbody id="tabla_body"></tbody>
                        </table>
                    </div>
                </div>
                
                <script>
                    function mostrarAviso(msg) {
                        const d = document.getElementById('aviso');
                        d.style.display = 'block';
                        d.innerText = msg;
                    }
                    function ocultarAviso() {
                        document.getElementById('aviso').style.display = 'none';
                    }

                    function correr() {
                        ocultarAviso();

                        const campos = [
                            { id: 't_med', nombre: 'Media Teléfono', max: 86400 },
                            { id: 't_var', nombre: 'Var Teléfono',   max: 86400 },
                            { id: 'g_med', nombre: 'Media Gas',      max: 86400 },
                            { id: 'g_var', nombre: 'Var Gas',        max: 86400 },
                            { id: 'a_med', nombre: 'Media Atención', max: 86400 },
                            { id: 'a_var', nombre: 'Var Atención',   max: 86400 },
                            { id: 'clientes', nombre: 'Cant. personas', max: 10000 },
                        ];

                        const errores = [];
                        const vals = {};

                        for (const c of campos) {
                            const txt = document.getElementById(c.id).value.trim();
                            const n   = parseFloat(txt);
                            if (txt === '' || isNaN(n)) {
                                errores.push('\u2717 "' + c.nombre + '": solo se permiten números.');
                            } else if (n < 0) {
                                errores.push('\u2717 "' + c.nombre + '": no se permiten negativos (recibido: ' + n + ').');
                            } else if (n > c.max) {
                                errores.push('\u2717 "' + c.nombre + '": valor demasiado grande. Máximo permitido: ' + c.max + '.');
                            } else {
                                vals[c.id] = n;
                            }
                        }

                        if (errores.length > 0) {
                            mostrarAviso(errores.join('\\n'));
                            return;
                        }

                        const params = {
                            tm: vals['t_med'], tv: vals['t_var'],
                            gm: vals['g_med'], gv: vals['g_var'],
                            am: vals['a_med'], av: vals['a_var'],
                            cli: vals['clientes']
                        };

                        fetch('/simular', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(params)
                        })
                        .then(r => r.json().then(d => ({ ok: r.ok, data: d })))
                        .then(({ ok, data }) => {
                            if (!ok) { mostrarAviso('\u2717 Error: ' + (data.error || 'Error desconocido.')); return; }
                            document.getElementById('res_box').style.display = 'block';
                            document.getElementById('r_cola').innerText = data.max_cola + " personas";
                            document.getElementById('r_tel').innerText = parseFloat(data.promedio_espera_tel).toFixed(2) + " seg.";
                            document.getElementById('r_gas').innerText = parseFloat(data.promedio_espera_gas).toFixed(2) + " seg.";
                            const hs = (data.tiempo_simulado / 3600).toFixed(2);
                            document.getElementById('r_extra').innerText = `Total atendidos: ${data.total_clientes} (Tel: ${data.clientes_tel}, Gas: ${data.clientes_gas}) | Reloj: ${hs} hrs simuladas.`;
                            document.getElementById('tabla_box').style.display = 'block';
                            const tbody = document.getElementById('tabla_body');
                            tbody.innerHTML = '';
                            data.tabla.forEach(fila => {
                                const tr = document.createElement('tr');
                                tr.innerHTML = `<td>${fila.reloj}</td><td>${fila.evento}</td><td>${fila.prox_tel}</td><td>${fila.prox_gas}</td><td>${fila.prox_fin}</td><td>${fila.estado_servidor}</td><td>${fila.cola}</td><td>${fila.total_atendidos}</td>`;
                                tbody.appendChild(tr);
                            });
                        })
                        .catch(() => mostrarAviso('\u2717 No se pudo conectar con el servidor.'));
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        if self.path == '/simular':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data)
            
            try:
                tm, tv = float(params['tm']), float(params['tv'])
                gm, gv = float(params['gm']), float(params['gv'])
                am, av = float(params['am']), float(params['av'])
                cli    = int(float(params['cli']))

                # Validación: negativos y rangos inválidos
                errores = []
                for nombre, val in [('Media Tel',tm),('Var Tel',tv),('Media Gas',gm),('Var Gas',gv),('Media Ate',am),('Var Ate',av)]:
                    if val < 0:     errores.append(f'{nombre} no puede ser negativo ({val})')
                    if val > 86400: errores.append(f'{nombre} excede el máximo permitido de 86400 seg')
                if tm - tv < 0: errores.append(f'Rango Teléfono negativo: {tm}-{tv}={tm-tv:.1f}')
                if gm - gv < 0: errores.append(f'Rango Gas negativo: {gm}-{gv}={gm-gv:.1f}')
                if am - av < 0: errores.append(f'Rango Atención negativo: {am}-{av}={am-av:.1f}')
                if cli <= 0:      errores.append('La cantidad de personas debe ser > 0')
                if cli > 10000:   errores.append(f'Máximo de personas permitido: 10000 (recibido: {cli})')

                if errores:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': ' | '.join(errores)}).encode('utf-8'))
                    return

                sim = SimulacionRapipago(
                    llegada_tel_media=tm, llegada_tel_var=tv,
                    llegada_gas_media=gm, llegada_gas_var=gv,
                    atencion_media=am, atencion_var=av,
                    max_clientes=cli
                )
                resultados = sim.ejecutar()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resultados).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print("Error en simulación:", e)

def run():
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimHandler)
    print(f"==========================================")
    print(f"Servidor WEB iniciado en http://localhost:{port}")
    print(f"==========================================")
    
    # Intenta abrir el navegador automáticamente
    try:
        webbrowser.open(f'http://localhost:{port}')
    except:
        pass
        
    httpd.serve_forever()

if __name__ == '__main__':
    run()
