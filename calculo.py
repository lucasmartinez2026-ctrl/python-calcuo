import customtkinter as ctk
import sympy as sp
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppLimites(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Límites - Proyecto EID")
        self.geometry("1150x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.panel_izq = ctk.CTkFrame(self, width=400)
        self.panel_izq.pack(side="left", fill="y", padx=20, pady=20)

        self.panel_der = ctk.CTkFrame(self)
        self.panel_der.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(self.panel_izq, text="Límites Paso a Paso", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        ctk.CTkLabel(self.panel_izq, text="Función f(x):").pack(anchor="w", padx=20)
        self.entrada_funcion = ctk.CTkEntry(self.panel_izq, placeholder_text="Ej: (x**2 - 4)/(x - 2)", width=350)
        self.entrada_funcion.pack(padx=20, pady=5)
        
        ayuda_texto = "Usa: ** (potencia), sqrt(x) (raíz), sin(x), oo (infinito)"
        ctk.CTkLabel(self.panel_izq, text=ayuda_texto, font=("Arial", 11), text_color="gray").pack(padx=20)

        ctk.CTkLabel(self.panel_izq, text="Valor al que tiende x (h):").pack(anchor="w", padx=20, pady=(10, 0))
        self.entrada_h = ctk.CTkEntry(self.panel_izq, placeholder_text="Ej: 2, 0, oo", width=350)
        self.entrada_h.pack(padx=20, pady=5)

        ctk.CTkLabel(self.panel_izq, text="Tipo de límite:").pack(anchor="w", padx=20, pady=(10, 0))
        self.opcion_lateralidad = ctk.CTkOptionMenu(
            self.panel_izq, 
            values=["Bilateral (Normal)", "Izquierda (-)", "Derecha (+)"], width=350
        )
        self.opcion_lateralidad.pack(padx=20, pady=5)

        self.boton_calcular = ctk.CTkButton(
            self.panel_izq, text="Calcular y Graficar", command=self.procesar_limite,
            font=("Arial", 14, "bold"), height=40
        )
        self.boton_calcular.pack(pady=20)

        self.caja_resultado = ctk.CTkTextbox(self.panel_izq, width=350, height=250, font=("Consolas", 13))
        self.caja_resultado.pack(padx=20, pady=5)
        self.caja_resultado.insert("1.0", "El paso a paso aparecerá aquí...")
        self.caja_resultado.configure(state="disabled")

        self.figura = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.panel_der)
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
            signo_dir = ""
            if tipo_lim == "Izquierda (-)":
                dir_limite = '-'
                signo_dir = "^-"
            elif tipo_lim == "Derecha (+)":
                dir_limite = '+'
                signo_dir = "^+"

            texto_res = f"--- PASO 1: PLANTEAMIENTO ---\n"
            texto_res += f"Lim  f(x) = {funcion_sympy}\n"
            texto_res += f"x->{h_val}{signo_dir}\n\n"

            texto_res += f"--- PASO 2: EVALUACIÓN DIRECTA ---\n"
            eval_directa = funcion_sympy.subs(x, h_val)
            texto_res += f"Reemplazando x = {h_val}:\n"
            texto_res += f"f({h_val}) = {eval_directa}\n\n"

            if eval_directa == sp.nan:
                texto_res += "¡Atención! Forma indeterminada (0/0 o ∞/∞).\n"
                texto_res += "Se debe factorizar, racionalizar o \naplicar propiedades trigonométricas.\n\n"
            elif eval_directa == sp.zoo:
                texto_res += "División por cero. El límite tiende a infinito.\n\n"
            else:
                texto_res += "El límite se calcula por evaluación directa.\n\n"

            texto_res += f"--- PASO 3: RESULTADO FINAL ---\n"
            resultado_limite = sp.limit(funcion_sympy, x, h_val, dir=dir_limite)
            texto_res += f"Aplicando propiedades, el límite es:\n"
            texto_res += f"L = {resultado_limite}"

            self.actualizar_texto(texto_res)
            self.graficar_funcion(funcion_sympy, h_val, x, resultado_limite)

        except Exception as e:
            self.actualizar_texto(f"ERROR: Revise la sintaxis.\n{e}")

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
        paso = (fin_x - inicio_x) / 500

        f_evaluable = sp.lambdify(simbolo_x, funcion_sympy, modules=['math'])

        for i in range(501):
            x_act = inicio_x + i * paso
            puntos_x.append(x_act)
            try:
                y_act = f_evaluable(x_act)
                if abs(y_act) > 50: 
                    puntos_y.append(math.nan)
                else:
                    puntos_y.append(y_act)
            except:
                puntos_y.append(math.nan)

        self.ax.plot(puntos_x, puntos_y, color="#2FA572", linewidth=2, label=f"f(x)")
        self.ax.axhline(0, color='white', linewidth=0.8, alpha=0.5)
        self.ax.axvline(0, color='white', linewidth=0.8, alpha=0.5)

        if h_val.is_finite and resultado_limite.is_finite:
            self.ax.scatter([float(h_val)], [float(resultado_limite)], color="red", zorder=5, s=60, label="Punto Límite")
            self.ax.axvline(float(h_val), color='red', linestyle='--', alpha=0.5)
            self.ax.axhline(float(resultado_limite), color='red', linestyle='--', alpha=0.5)

        self.figura.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.grid(True, linestyle='--', alpha=0.2)
        
        legend = self.ax.legend(facecolor='#2b2b2b', edgecolor='white')
        for text in legend.get_texts():
            text.set_color('white')

        self.ax.set_title("Visualización del Límite")
        self.canvas.draw()

    def actualizar_texto(self, texto):
        self.caja_resultado.configure(state="normal")
        self.caja_resultado.delete("1.0", "end")
        self.caja_resultado.insert("1.0", texto)
        self.caja_resultado.configure(state="disabled")

if __name__ == "__main__":
    app = AppLimites()
    app.mainloop()
