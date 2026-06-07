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

        self.panel_izq = ctk.CTkFrame(self, width=450)
        self.panel_izq.pack(side="left", fill="y", padx=20, pady=20)
        self.panel_der = ctk.CTkFrame(self)
        self.panel_der.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(self.panel_izq, text="Resolución Algorítmica", font=("Arial", 22, "bold")).pack(pady=15)
        
        self.ent_func = ctk.CTkEntry(self.panel_izq, placeholder_text="Función f(x) Ej: sin(x)/x", width=400)
        self.ent_func.pack(padx=20, pady=10)
        
        self.ent_h = ctk.CTkEntry(self.panel_izq, placeholder_text="Valor h Ej: 0", width=400)
        self.ent_h.pack(padx=20, pady=10)

        self.op_lat = ctk.CTkOptionMenu(self.panel_izq, values=["Bilateral", "Izquierda (-)", "Derecha (+)"], width=400)
        self.op_lat.pack(padx=20, pady=10)

        ctk.CTkButton(self.panel_izq, text="Ejecutar Algoritmo", command=self.procesar_limite, height=40).pack(pady=15)

        self.caja_res = ctk.CTkTextbox(self.panel_izq, width=400, height=350, font=("Consolas", 12))
        self.caja_res.pack(padx=20, pady=5)

        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def procesar_limite(self):
        try:
            x = sp.Symbol('x')
            f_sym = sp.sympify(self.ent_func.get())
            h_sym = sp.sympify(self.ent_h.get())
            
            d_sym = '-' if "Izq" in self.op_lat.get() else '+' if "Der" in self.op_lat.get() else '+-'
            
            texto = f"Analizando: Lim f(x)={f_sym} cuando x->{h_sym}\n\n[ETAPA 1] APROXIMACIÓN (Ciclo FOR)\n"

            if h_sym.is_finite:
                for d in [0.1, 0.01, 0.001]:
                    izq = f_sym.subs(x, h_sym - d).evalf(4)
                    der = f_sym.subs(x, h_sym + d).evalf(4)
                    texto += f" x={h_sym-d:.3f} -> {izq} | x={h_sym+d:.3f} -> {der}\n"
            else:
                for v in ([10, 100, 1000] if h_sym == sp.oo else [-10, -100, -1000]):
                    texto += f" x={v} -> {f_sym.subs(x, v).evalf(4)}\n"

            texto += "\n[ETAPA 2] RESOLUCIÓN ANALÍTICA\n"
            resultado, pasos = self.algoritmo_matematico(f_sym, x, h_sym, d_sym)
            
            self.actualizar_texto(texto + pasos + f"\n>>> RESULTADO FINAL: L = {resultado} <<<\n")
            self.graficar(f_sym, h_sym, x, resultado)

        except Exception as e:
            self.actualizar_texto(f"ERROR DE SINTAXIS:\n{e}")

    def algoritmo_matematico(self, f, x, h, d_sym):
        ev = f.subs(x, h)
        pasos = f"1. Evaluación Directa: f({h}) = {ev}\n"

        if ev not in [sp.nan, sp.zoo] and not ev.has(sp.oo, -sp.oo):
            return ev, pasos + "-> Límite determinado.\n"
            
        if ev == sp.zoo or ev.has(sp.oo, -sp.oo):
            return sp.limit(f, x, h, dir=d_sym), pasos + "-> Asíntota detectada.\n"

        pasos += "-> ¡Indeterminación! Aplicando álgebra...\n\n"
        f_simp = sp.cancel(f) 
        
        if f_simp != f:
            ev_simp = f_simp.subs(x, h)
            pasos += f"2. Factorización: {f_simp}\n   Evaluación: {ev_simp}\n"
            if ev_simp not in [sp.nan, sp.zoo]: return ev_simp, pasos + "-> Resuelto.\n"

        pasos += "3. Algoritmo Iterativo L'Hôpital (Ciclo While)\n"
        num, den = sp.fraction(sp.together(f_simp))
        
        if den != 1:
            i = 1
            while i <= 3:
                num, den = sp.diff(num, x), sp.diff(den, x)
                f_hop = num / den
                ev_hop = f_hop.subs(x, h)
                pasos += f"  [Iter {i}] Derivando: {f_hop} -> Eval: {ev_hop}\n"
                
                if ev_hop not in [sp.nan, sp.zoo] and not ev_hop.has(sp.oo, -sp.oo):
                    return ev_hop, pasos + "-> Resuelto por L'Hôpital.\n"
                i += 1

        return sp.limit(f, x, h, dir=d_sym), pasos + "4. Motor simbólico de respaldo.\n"

    def graficar(self, f_sym, h_val, x_sym, res):
        self.ax.clear()
        
        inicio, fin = (0, 20) if h_val == sp.oo else (-20, 0) if h_val == -sp.oo else (float(h_val)-5, float(h_val)+5)
        paso = (fin - inicio) / 500
        p_x, p_y = [], []
        
        f_py = sp.lambdify(x_sym, f_sym, modules=['math'])

        for i in range(501):
            px = inicio + i * paso
            p_x.append(px)
            try:
                py = f_py(px)
                p_y.append(math.nan if abs(py) > 50 else py)
            except:
                p_y.append(math.nan)

        self.ax.plot(p_x, p_y, color="#2FA572", lw=2, label="f(x)")
        self.ax.axhline(0, color='white', lw=0.8, alpha=0.5)
        self.ax.axvline(0, color='white', lw=0.8, alpha=0.5)

        if h_val.is_finite and res.is_finite:
            self.ax.scatter([float(h_val)], [float(res)], color="red", zorder=5)

        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, ls='--', alpha=0.2)
        self.canvas.draw()

    def actualizar_texto(self, txt):
        self.caja_res.configure(state="normal")
        self.caja_res.delete("1.0", "end")
        self.caja_res.insert("1.0", txt)
        self.caja_res.configure(state="disabled")

if __name__ == "__main__":
    AppLimites().mainloop()
