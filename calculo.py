import customtkinter as ctk
import sympy as sp
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AppLimites(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Límites - Proyecto EID")
        self.geometry("1100x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.panel_izquierdo = ctk.CTkFrame(self, width=350)
        self.panel_izquierdo.pack(side="left", fill="y", padx=20, pady=20)

        self.panel_derecho = ctk.CTkFrame(self)
        self.panel_derecho.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(self.panel_izquierdo, text="Análisis de Límites", font=("Arial", 24, "bold")).pack(pady=(20, 10))

        ctk.CTkLabel(self.panel_izquierdo, text="Función f(x):").pack(anchor="w", padx=20)
        self.entrada_funcion = ctk.CTkEntry(self.panel_izquierdo, placeholder_text="Ej: (x**2 - 4)/(x - 2)", width=300)
        self.entrada_funcion.pack(padx=20, pady=5)
        
        ayuda_texto = "Sintaxis: usar ** para potencias, sqrt(x) para raíces,\n sin(x), cos(x), exp(x), oo para infinito."
        ctk.CTkLabel(self.panel_izquierdo, text=ayuda_texto, font=("Arial", 11), text_color="gray").pack(padx=20)

        ctk.CTkLabel(self.panel_izquierdo, text="Valor al que tiende x (h):").pack(anchor="w", padx=20, pady=(15, 0))
        self.entrada_h = ctk.CTkEntry(self.panel_izquierdo, placeholder_text="Ej: 2, 0, oo, -oo", width=300)
        self.entrada_h.pack(padx=20, pady=5)

        ctk.CTkLabel(self.panel_izquierdo, text="Tipo de límite:").pack(anchor="w", padx=20, pady=(15, 0))
        self.opcion_lateralidad = ctk.CTkOptionMenu(
            self.panel_izquierdo, 
            values=["Bilateral (Normal)", "Izquierda (-)", "Derecha (+)"],
            width=300
        )
        self.opcion_lateralidad.pack(padx=20, pady=5)

        self.boton_calcular = ctk.CTkButton(
            self.panel_izquierdo, 
            text="Calcular y Graficar", 
            command=self.procesar_limite,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.boton_calcular.pack(pady=25)

        self.caja_resultado = ctk.CTkTextbox(self.panel_izquierdo, width=300, height=200, font=("Arial", 14))
        self.caja_resultado.pack(padx=20, pady=5)
        self.caja_resultado.insert("1.0", "Los resultados aparecerán aquí...")
        self.caja_resultado.configure(state="disabled") 

        self.figura = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.panel_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def procesar_limite(self):
        str_funcion = self.entrada_funcion.get()
        str_h = self.entrada_h.get()
        tipo_lim = self.opcion_lateralidad.get()

        try:
            x = sp.Symbol('x')

            funcion_sympy = sp.sympify(str_funcion)
            h_val = sp.sympify(str_h)

            dir_limite = '+-' 
            if tipo_lim == "Izquierda (-)":
                dir_limite = '-'
            elif tipo_lim == "Derecha (+)":
                dir_limite = '+'

            resultado_limite = sp.limit(funcion_sympy, x, h_val, dir=dir_limite)

            texto_res = f"Función ingresada:\nf(x) = {funcion_sympy}\n\n"
            texto_res += f"Evaluando cuando x -> {h_val}\n"
            texto_res += f"Dirección: {tipo_lim}\n\n"
            texto_res += f"RESULTADO DEL LÍMITE:\nL = {resultado_limite}"
            
            self.actualizar_texto(texto_res)

            self.graficar_funcion(funcion_sympy, h_val, x, resultado_limite)

        except Exception as e:
            self.actualizar_texto(f"ERROR EN EL INGRESO:\nVerifique la sintaxis matemática.\nDetalle: {e}")

    def graficar_funcion(self, funcion_sympy, h_val, simbolo_x, resultado_limite):
        self.ax.clear()


        if h_val == sp.oo:
            inicio_x, fin_x = 0, 20
        elif h_val == -sp.oo:
            inicio_x, fin_x = -20, 0
        else:
            h_num = float(h_val)
            inicio_x, fin_x = h_num - 5, h_num + 5

        puntos_x = []
        puntos_y = []
        cantidad_puntos = 500
        paso = (fin_x - inicio_x) / cantidad_puntos

        f_evaluable = sp.lambdify(simbolo_x, funcion_sympy, modules=['math'])

        for i in range(cantidad_puntos + 1):
            x_actual = inicio_x + i * paso
            puntos_x.append(x_actual)
            
            try:
                y_actual = f_evaluable(x_actual)
                if abs(y_actual) > 50: 
                    puntos_y.append(math.nan)
                else:
                    puntos_y.append(y_actual)
            except:
                puntos_y.append(math.nan)

        self.ax.plot(puntos_x, puntos_y, color="blue", label=f"f(x)")

        self.ax.axhline(0, color='black', linewidth=1)
        self.ax.axvline(0, color='black', linewidth=1)

        if h_val.is_finite and resultado_limite.is_finite:
            self.ax.scatter([float(h_val)], [float(resultado_limite)], color="red", zorder=5, label="Punto Límite")
            self.ax.axvline(float(h_val), color='red', linestyle='--', alpha=0.5)
            self.ax.axhline(float(resultado_limite), color='red', linestyle='--', alpha=0.5)

        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend()
        self.ax.set_title("Visualización del Límite")
        self.ax.set_xlabel("Eje x")
        self.ax.set_ylabel("f(x)")

        self.canvas.draw()

    def actualizar_texto(self, texto):
        self.caja_resultado.configure(state="normal")
        self.caja_resultado.delete("1.0", "end")
        self.caja_resultado.insert("1.0", texto)
        self.caja_resultado.configure(state="disabled")

if __name__ == "__main__":
    app = AppLimites()
    app.mainloop()