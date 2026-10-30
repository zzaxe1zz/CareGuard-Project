import customtkinter as ctk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from controllers.admin_controller import AdminController
from models.dto import SessionDTO


class AdminDashboardView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = AdminController(session)

        self.title("CareGuard - Panel de Control Administrativo")
        self.after(0, lambda: self.wm_state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#0F4C81",
                              height=60, corner_radius=0)
        header.pack(fill="x", side="top")

        ctk.CTkLabel(header, text=f"🛠️ {self.session.nombre} [Administración General]", font=ctk.CTkFont(
            size=16, weight="bold"), text_color="white").pack(side="left", padx=20)
        ctk.CTkButton(header, text="Cerrar Sesión", fg_color="#EF4444", hover_color="#DC2626",
                      width=120, command=self.cerrar_sesion).pack(side="right", padx=20, pady=12)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_metrics = self.tabs.add("Métricas y Análisis Institucional")
        self.tab_users = self.tabs.add("Gestión de Usuarios y Personal")

        self._configurar_tab_metrics()
        self._configurar_tab_users()

    def _configurar_tab_metrics(self):
        metricas = self.controller.obtener_metricas_dashboard()

        # KPIs
        f_kpi = ctk.CTkFrame(self.tab_metrics)
        f_kpi.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(f_kpi, text=f" Satisfacción de Pacientes: {metricas['promedio_satisfaccion']} / 5.0 ⭐", font=ctk.CTkFont(
            size=15, weight="bold")).pack(side="left", padx=30, pady=10)
        ctk.CTkLabel(f_kpi, text=f" Total Evaluaciones Recibidas: {metricas['total_evaluaciones']}", font=ctk.CTkFont(
            size=15, weight="bold")).pack(side="right", padx=30, pady=10)

        # Gráficos de Matplotlib
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4), dpi=90)
        fig.patch.set_facecolor('#F8FAFC')

        # 1. Horas Extra
        roles = [i["rol"]
                 for i in metricas["horas_extra_agregadas"]] or ["Sin Datos"]
        horas = [i["total_horas_extra"]
                 for i in metricas["horas_extra_agregadas"]] or [0]
        ax1.bar(roles, horas, color="#0F4C81")
        ax1.set_title("Horas Extra por Rol (30 días)")

        # 2. Distribución de Alertas por Estado
        alertas_est = self.controller.db.obtener_todos(
            "SELECT estado, COUNT(*) as cant FROM alertas GROUP BY estado")
        est_lbls = [a["estado"] for a in alertas_est] or ["Sin Alertas"]
        est_vals = [a["cant"] for a in alertas_est] or [1]
        ax2.pie(est_vals, labels=est_lbls, autopct='%1.1f%%',
                colors=["#F59E0B", "#10B981", "#EF4444"])
        ax2.set_title("Estado de Alertas")

        # 3. Tendencia de Estrés
        estres_trend = self.controller.db.obtener_todos(
            "SELECT strftime('%m-%d', fecha_registro) as dia, AVG(nivel_estres) as prom FROM estados_emocionales GROUP BY dia ORDER BY dia LIMIT 10")
        dias = [e["dia"] for e in estres_trend] or ["Hoy"]
        proms = [e["prom"] for e in estres_trend] or [0]
        ax3.plot(dias, proms, marker='o', color="#DC2626")
        ax3.set_title("Promedio de Estrés Reciente")

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.tab_metrics)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _configurar_tab_users(self):
        f_form = ctk.CTkFrame(self.tab_users)
        f_form.pack(padx=30, pady=30)

        ctk.CTkLabel(f_form, text="Alta de Cuentas Institucionales",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        self.entry_nom = ctk.CTkEntry(
            f_form, placeholder_text="Nombre Completo", width=320)
        self.entry_nom.pack(pady=8)

        self.entry_usr = ctk.CTkEntry(
            f_form, placeholder_text="Nombre de Usuario / Código", width=320)
        self.entry_usr.pack(pady=8)

        self.entry_pwd = ctk.CTkEntry(
            f_form, placeholder_text="Contraseña Inicial", show="*", width=320)
        self.entry_pwd.pack(pady=8)

        self.combo_rol = ctk.CTkOptionMenu(
            f_form, values=["MEDICO", "ENFERMERO", "PSICOLOGO", "ADMIN"], width=320)
        self.combo_rol.pack(pady=8)

        ctk.CTkButton(f_form, text="Registrar Usuario",
                      fg_color="#0F4C81", command=self._registrar).pack(pady=20)

    def _registrar(self):
        try:
            self.controller.registrar_usuario(self.entry_nom.get(
            ), self.entry_usr.get(), self.entry_pwd.get(), self.combo_rol.get())
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.entry_nom.delete(0, "end")
            self.entry_usr.delete(0, "end")
            self.entry_pwd.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cerrar_sesion(self):
        self.destroy()
        self.parent.deiconify()

    def cerrar_aplicacion(self):
        self.parent.destroy()
