import customtkinter as ctk
import sympy as sp
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppLimites(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Límites - Proyecto EID")
        self.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.panel_izq = ctk.CTkFrame(self, width=450)
        self.panel_izq.pack(side="left", fill="y", padx=20, pady=20)

        self.panel_der = ctk.CTkFrame(self)
        self.panel_der.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(self.panel_izq, text="Resolución Algorítmica", font=("Arial", 22, "bold")).pack(pady=(15, 5))

        ctk.CTkLabel(self.panel_izq, text="Función f(x):").pack(anchor="w", padx=20)
        self.entrada_funcion = ctk.CTkEntry(self.panel_izq, placeholder_text="Ej: sin(x)/x", width=400)
        self.entrada_funcion.pack(padx=20, pady=5)
        
        ctk.CTkLabel(self.panel_izq, text="Valor al que tiende x (h):").pack(anchor="w", padx=20, pady=(10, 0))
        self.entrada_h = ctk.CTkEntry(self.panel_izq, placeholder_text="Ej: 0", width=400)
        self.entrada_h.pack(padx=20, pady=5)

        ctk.CTkLabel(self.panel_izq, text="Tipo de límite:").pack(anchor="w", padx=20, pady=(10, 0))
        self.opcion_lateralidad = ctk.CTkOptionMenu(
            self.panel_izq, 
            values=["Bilateral (Normal)", "Izquierda (-)", "Derecha (+)"], width=400
        )
        self.opcion_lateralidad.pack(padx=20, pady=5)

        self.boton_calcular = ctk.CTkButton(
            self.panel_izq, text="Ejecutar Algoritmo", command=self.procesar_limite,
            font=("Arial", 14, "bold"), height=40
        )
        self.boton_calcular.pack(pady=20)

        self.caja_resultado = ctk.CTkTextbox(self.panel_izq, width=400, height=350, font=("Consolas", 12))
        self.caja_resultado.pack(padx=20, pady=5)
        self.caja_resultado.insert("1.0", "El desarrollo algorítmico aparecerá aquí...")
        self.caja_resultado.configure(state="disabled")

        self.figura = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.panel_der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def formatear_num(self, valor):
        try:
            return f"{float(valor):.4f}"
        except:
            return str(valor)

    def procesar_limite(self):
        try:
            x = sp.Symbol('x')
            f_sym = sp.sympify(self.entrada_funcion.get())
            h_sym = sp.sympify(self.entrada_h.get())
            tipo_lim = self.opcion_lateralidad.get()

            dir_sym = '+-'
            if tipo_lim == "Izquierda (-)": dir_sym = '-'
            elif tipo_lim == "Derecha (+)": dir_sym = '+'

            texto_res = f"Analizando: Límite de {f_sym} cuando x -> {h_sym}\n\n"

            texto_res += "[ETAPA 1] APROXIMACIÓN NUMÉRICA (Ciclo FOR)\n"
            if h_sym.is_finite:
                deltas = [0.1, 0.01, 0.001]
                for d in deltas:
                    v_izq = self.formatear_num(f_sym.subs(x, h_sym - d))
                    v_der = self.formatear_num(f_sym.subs(x, h_sym + d))
                    texto_res += f" x = {h_sym - d:.3f} -> f(x) = {v_izq} | x = {h_sym + d:.3f} -> f(x) = {v_der}\n"
            else:
                valores = [10, 100, 1000] if h_sym == sp.oo else [-10, -100, -1000]
                for v in valores:
                    v_eval = self.formatear_num(f_sym.subs(x, v))
                    texto_res += f" x = {v} -> f(x) = {v_eval}\n"
            texto_res += "\n"

            texto_res += "[ETAPA 2] RESOLUCIÓN ANALÍTICA\n"
            resultado_final, pasos_algoritmo = self.ejecutar_algoritmo_propio(f_sym, x, h_sym, dir_sym)
            texto_res += pasos_algoritmo

            texto_res += f"\n>>> RESULTADO FINAL: L = {resultado_final} <<<\n"
            self.actualizar_texto(texto_res)
            self.graficar_funcion(f_sym, h_sym, x, resultado_final)

        except Exception as e:
            self.actualizar_texto(f"ERROR DE SINTAXIS:\n{e}")

    def ejecutar_algoritmo_propio(self, f, x, h, dir_sym):
        pasos = ""
        eval_directa = f.subs(x, h)
        pasos += f"1. Evaluación Directa: f({h}) = {eval_directa}\n"

        if eval_directa != sp.nan and eval_directa != sp.zoo and not eval_directa.has(sp.oo, -sp.oo):
            pasos += "-> El límite es determinado.\n"
            return eval_directa, pasos

        if eval_directa == sp.zoo or eval_directa.has(sp.oo, -sp.oo):
            pasos += "-> Asíntota detectada. Evaluando límite lateral...\n"
            return sp.limit(f, x, h, dir=dir_sym), pasos

        pasos += "-> ¡Indeterminación detectada! Aplicando métodos algebraicos...\n\n"

        f_simp = sp.cancel(f)
        if f_simp != f:
            pasos += f"2. Simplificación Algebraica:\n   Función reducida a: {f_simp}\n"
            eval_simp = f_simp.subs(x, h)
            pasos += f"   Nueva Evaluación: f({h}) = {eval_simp}\n"
            if eval_simp != sp.nan and eval_simp != sp.zoo:
                pasos += "-> Límite resuelto por factorización.\n"
                return eval_simp, pasos
            pasos += "\n"
        else:
            pasos += "2. La función no es simplificable por factorización.\n\n"

        pasos += "3. Algoritmo Iterativo: Regla de L'Hôpital (Ciclo While)\n"
        num, den = sp.fraction(sp.together(f_simp))
        
        if den != 1:
            iteracion = 1
            while iteracion <= 3:
                num = sp.diff(num, x)
                den = sp.diff(den, x)
                f_hop = num / den
                
                pasos += f"   [Iteración {iteracion}]\n"
                pasos += f"   Derivando -> f(x) = {f_hop}\n"
                eval_hop = f_hop.subs(x, h)
                pasos += f"   Evaluando -> {eval_hop}\n"

                if eval_hop != sp.nan and eval_hop != sp.zoo and not eval_hop.has(sp.oo, -sp.oo):
                    pasos += "-> Límite resuelto exitosamente por L'Hôpital.\n"
                    return eval_hop, pasos
                iteracion += 1
            pasos += "   Límite de iteraciones alcanzado.\n\n"
        else:
            pasos += "   No cumple estructura fraccionaria para L'Hôpital.\n\n"

        pasos += "4. Límite de alta complejidad. Usando motor simbólico.\n"
        return sp.limit(f, x, h, dir=dir_sym), pasos

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
        for text in legend.get_texts(): text.set_color('white')

        self.ax.set_title("Visualización Gráfica (Sin NumPy)")
        self.canvas.draw()

    def actualizar_texto(self, texto):
        self.caja_resultado.configure(state="normal")
        self.caja_resultado.delete("1.0", "end")
        self.caja_resultado.insert("1.0", texto)
        self.caja_resultado.configure(state="disabled")

if __name__ == "__main__":
    app = AppLimites()
    app.mainloop()
