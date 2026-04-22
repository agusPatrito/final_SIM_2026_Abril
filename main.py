import tkinter as tk
from tkinter import ttk, messagebox
from simulacion import SimulacionRapipago

class SimuladorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Simulador de Rapipago - Final Simulación")
        self.geometry("550x550")
        self.configure(padx=20, pady=20)
        self.resizable(False, False)

        # Style configuration
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=6)
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))

        self.crear_widgets()

    def crear_widgets(self):
        # Título
        lbl_titulo = ttk.Label(self, text="Parámetros de la Simulación", style='Title.TLabel')
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # --- Parámetros Llegadas ---
        frame_llegadas = ttk.LabelFrame(self, text="Tiempos de Llegada (Uniformes en seg)")
        frame_llegadas.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        frame_llegadas.columnconfigure(1, weight=1)
        frame_llegadas.columnconfigure(3, weight=1)

        ttk.Label(frame_llegadas, text="Teléfono: Media", style='Header.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.var_tel_media = tk.StringVar(value="100")
        ttk.Entry(frame_llegadas, textvariable=self.var_tel_media, width=8).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_llegadas, text="+/-").grid(row=0, column=2, padx=5, pady=5)
        self.var_tel_var = tk.StringVar(value="70")
        ttk.Entry(frame_llegadas, textvariable=self.var_tel_var, width=8).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_llegadas, text="Gas: Media", style='Header.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.var_gas_media = tk.StringVar(value="80")
        ttk.Entry(frame_llegadas, textvariable=self.var_gas_media, width=8).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_llegadas, text="+/-").grid(row=1, column=2, padx=5, pady=5)
        self.var_gas_var = tk.StringVar(value="30")
        ttk.Entry(frame_llegadas, textvariable=self.var_gas_var, width=8).grid(row=1, column=3, padx=5, pady=5)

        # --- Parámetros Atención ---
        frame_atencion = ttk.LabelFrame(self, text="Tiempos de Atención (Uniformes en seg)")
        frame_atencion.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        frame_atencion.columnconfigure(1, weight=1)
        frame_atencion.columnconfigure(3, weight=1)

        ttk.Label(frame_atencion, text="Atención: Media", style='Header.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.var_ate_media = tk.StringVar(value="45")
        ttk.Entry(frame_atencion, textvariable=self.var_ate_media, width=8).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_atencion, text="+/-").grid(row=0, column=2, padx=5, pady=5)
        self.var_ate_var = tk.StringVar(value="20")
        ttk.Entry(frame_atencion, textvariable=self.var_ate_var, width=8).grid(row=0, column=3, padx=5, pady=5)

        # --- Parámetros Fin ---
        frame_fin = ttk.Frame(self)
        frame_fin.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Label(frame_fin, text="Cantidad de personas a atender:", style='Header.TLabel').pack(side=tk.LEFT, padx=5)
        self.var_max_cli = tk.StringVar(value="800")
        ttk.Entry(frame_fin, textvariable=self.var_max_cli, width=10).pack(side=tk.LEFT, padx=5)

        # Botón Ejecutar
        btn_run = ttk.Button(self, text="EJECUTAR SIMULACIÓN", command=self.correr_simulacion)
        btn_run.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")

        # --- Resultados ---
        frame_res = ttk.LabelFrame(self, text="Resultados de la Simulación")
        frame_res.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10, padx=5)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(1, weight=1)

        self.lbl_v_max_cola = ttk.Label(frame_res, text="...", font=('Helvetica', 12, 'bold'), foreground="#2c3e50")
        self.lbl_v_pro_tel = ttk.Label(frame_res, text="...", font=('Helvetica', 12, 'bold'), foreground="#2c3e50")
        self.lbl_v_pro_gas = ttk.Label(frame_res, text="...", font=('Helvetica', 12, 'bold'), foreground="#2c3e50")
        self.lbl_v_extras = ttk.Label(frame_res, text="", font=('Helvetica', 9, 'italic'), foreground="#7f8c8d")

        ttk.Label(frame_res, text="Longitud máxima de la cola:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.lbl_v_max_cola.grid(row=0, column=1, sticky='e', padx=10, pady=8)

        ttk.Label(frame_res, text="Promedio espera - Teléfono:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.lbl_v_pro_tel.grid(row=1, column=1, sticky='e', padx=10, pady=8)

        ttk.Label(frame_res, text="Promedio espera - Gas:", style='Header.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.lbl_v_pro_gas.grid(row=2, column=1, sticky='e', padx=10, pady=8)

        self.lbl_v_extras.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=8)

    def correr_simulacion(self):
        try:
            # Obtener datos de interfaz
            tel_m = float(self.var_tel_media.get())
            tel_v = float(self.var_tel_var.get())
            gas_m = float(self.var_gas_media.get())
            gas_v = float(self.var_gas_var.get())
            ate_m = float(self.var_ate_media.get())
            ate_v = float(self.var_ate_var.get())
            m_cli = int(self.var_max_cli.get())

            # Validación básica
            if tel_m - tel_v < 0 or gas_m - gas_v < 0 or ate_m - ate_v < 0:
                messagebox.showwarning("Aviso", "Existen rangos de tiempo negativos en las distribuciones.")

            # Instanciar y correr
            sim = SimulacionRapipago(tel_m, tel_v, gas_m, gas_v, ate_m, ate_v, m_cli)
            resultados = sim.ejecutar()

            # Reflejar en la UI
            self.lbl_v_max_cola.config(text=f"{resultados['max_cola']} personas")
            self.lbl_v_pro_tel.config(text=f"{resultados['promedio_espera_tel']:.2f} segundos")
            self.lbl_v_pro_gas.config(text=f"{resultados['promedio_espera_gas']:.2f} segundos")

            t_hs = resultados['tiempo_simulado'] / 3600
            self.lbl_v_extras.config(text=f"Total clientes Atendidos: {resultados['total_clientes']} (Tel: {resultados['clientes_tel']}, Gas: {resultados['clientes_gas']})\nTiempo total simulado: {t_hs:.2f} horas")

        except ValueError:
            messagebox.showerror("Error", "¡Por favor, ingresa números válidos en todos los campos!")


if __name__ == "__main__":
    app = SimuladorGUI()
    app.mainloop()
