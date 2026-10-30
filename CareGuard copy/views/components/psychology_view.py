import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.psychology_controller import PsychologyController
from models.dto import SessionDTO
from tkcalendar import DateEntry


class PsychologyView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = PsychologyController(session)

        self.title("CareGuard - Panel de Psicología y Salud Mental")
        self.after(0, lambda: self.wm_state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#0F4C81",
                              height=60, corner_radius=0)
        header.pack(fill="x", side="top")

        ctk.CTkLabel(
            header,
            text=f"🧠 {self.session.nombre} [Psicología Clínico]",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="Cerrar Sesión",
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=120,
            command=self.cerrar_sesion
        ).pack(side="right", padx=20, pady=12)

        ctk.CTkLabel(
            self,
            text="Control de Alertas por Sobrecarga / Burnout",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)

        # Tabla Principal
        self.tree = ttk.Treeview(
            self,
            columns=("ID", "Profesional", "Fecha", "Tipo", "Estado", "Motivo"),
            show="headings"
        )
        cols = {
            "ID": 50,
            "Profesional": 180,
            "Fecha": 140,
            "Tipo": 100,
            "Estado": 110,
            "Motivo": 350
        }
        for col, w in cols.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Acciones
        f_acc = ctk.CTkFrame(self)
        f_acc.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(f_acc, text="Refrescar Bandeja",
                      command=self._cargar_alertas).pack(side="left", padx=10)
        ctk.CTkButton(f_acc, text="🔍 Ver Expediente Confidencial", fg_color="#0D9488",
                      command=self._ver_expediente_completo).pack(side="left", padx=10)
        ctk.CTkButton(f_acc, text="📅 Agendar Cita y Notificar", fg_color="#2563EB",
                      command=self._agendar_cita).pack(side="left", padx=10)

        self.combo_estado = ctk.CTkOptionMenu(
            f_acc, values=["EN_ATENCION", "CERRADA"])
        self.combo_estado.pack(side="left", padx=10)

        ctk.CTkButton(f_acc, text="Actualizar Estado",
                      command=self._actualizar_estado).pack(side="left", padx=10)

        self._cargar_alertas()

    def _cargar_alertas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for a in self.controller.consultar_bandeja_alertas():
            self.tree.insert("", "end", values=(
                a.id_alerta, a.nombre_profesional, a.fecha_generacion, a.tipo, a.estado, a.motivo
            ))

    def _ver_expediente_completo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "Atención", "Seleccione un registro de la lista.")
            return

        id_alerta = self.tree.item(sel[0])["values"][0]
        alerta = next((a for a in self.controller.consultar_bandeja_alertas(
        ) if a.id_alerta == id_alerta), None)

        if not alerta:
            return

        exp = self.controller.consultar_expediente_confidencial(
            alerta.id_usuario)

        # Ventana modal estructurada del expediente
        v_exp = ctk.CTkToplevel(self)
        v_exp.title(
            f"Expediente Emocional Confidencial - {exp['medico']['nombre']}")
        v_exp.geometry("700x500")
        v_exp.grab_set()

        ctk.CTkLabel(
            v_exp,
            text=f"Expediente Clínico: {exp['medico']['nombre']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        tabs_exp = ctk.CTkTabview(v_exp)
        tabs_exp.pack(fill="both", expand=True, padx=15, pady=10)

        t_emo = tabs_exp.add("Historial de Estrés")
        t_jor = tabs_exp.add("Historial de Horarios")

        # Tabla Emocional
        tree_e = ttk.Treeview(t_emo, columns=(
            "Fecha", "Nivel Estrés", "Ánimo", "Notas"), show="headings")
        for c in ("Fecha", "Nivel Estrés", "Ánimo", "Notas"):
            tree_e.heading(c, text=c)
            tree_e.column(c, anchor="center")
        tree_e.pack(fill="both", expand=True)

        for reg in exp["historial_emocional"]:
            tree_e.insert("", "end", values=(
                reg["fecha_registro"], f"{reg['nivel_estres']} / 10", reg["estado_animo"], reg["notas"]
            ))

        # Tabla Jornadas
        tree_j = ttk.Treeview(t_jor, columns=(
            "Fecha", "Horas Trab", "Horas Extra"), show="headings")
        for c in ("Fecha", "Horas Trab", "Horas Extra"):
            tree_j.heading(c, text=c)
            tree_j.column(c, anchor="center")
        tree_j.pack(fill="both", expand=True)

        for reg in exp["historial_jornadas"]:
            tree_j.insert("", "end", values=(
                reg["fecha"], reg["horas_trabajadas"], reg["horas_extra"]
            ))

    def _agendar_cita(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "Atención", "Seleccione un profesional de la lista.")
            return

        id_alerta = self.tree.item(sel[0])["values"][0]
        alerta = next((a for a in self.controller.consultar_bandeja_alertas(
        ) if a.id_alerta == id_alerta), None)

        if not alerta:
            return

        v_cita = ctk.CTkToplevel(self)
        v_cita.title("Agendar Cita")
        v_cita.geometry("450x380")
        v_cita.grab_set()

        ctk.CTkLabel(
            v_cita,
            text=f"Cita con: {alerta.nombre_profesional}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        # Seleccionar Fecha con Calendario
        f_fecha = ctk.CTkFrame(v_cita, fg_color="transparent")
        f_fecha.pack(pady=5)

        ctk.CTkLabel(f_fecha, text="Fecha:").pack(side="left", padx=5)

        cal = DateEntry(
            f_fecha,
            width=12,
            background='#0F4C81',
            foreground='white',
            bordercolor='#0F4C81',
            date_pattern='yyyy-mm-dd'
        )
        cal.pack(side="left", padx=5)

        # Seleccionar Hora y Minutos
        f_hora = ctk.CTkFrame(v_cita, fg_color="transparent")
        f_hora.pack(pady=10)

        ctk.CTkLabel(f_hora, text="Hora:").pack(side="left", padx=5)

        horas_vals = [f"{h:02d}" for h in range(7, 21)]
        combo_hora = ctk.CTkOptionMenu(f_hora, values=horas_vals, width=70)
        combo_hora.set("10")
        combo_hora.pack(side="left", padx=2)

        ctk.CTkLabel(f_hora, text=":").pack(side="left")

        mins_vals = ["00", "15", "30", "45"]
        combo_min = ctk.CTkOptionMenu(f_hora, values=mins_vals, width=70)
        combo_min.set("00")
        combo_min.pack(side="left", padx=2)

        # Campo Notas
        entry_n = ctk.CTkEntry(
            v_cita, placeholder_text="Notas o Motivo", width=300)
        entry_n.pack(pady=15)

        def confirmar():
            fecha_sel = cal.get_date().strftime("%Y-%m-%d")
            hora_sel = combo_hora.get()
            min_sel = combo_min.get()
            f_h = f"{fecha_sel} {hora_sel}:{min_sel}:00"

            notas = entry_n.get().strip()

            # Registrar Cita
            self.controller.db.ejecutar(
                "INSERT INTO citas (id_usuario, id_psicologo, fecha_hora, estado, notas) VALUES (?, ?, ?, 'PROGRAMADA', ?)",
                (alerta.id_usuario, self.session.id_usuario, f_h, notas)
            )

            # Notificar al médico
            self.controller.db.ejecutar(
                "INSERT INTO notificaciones (id_usuario, mensaje) VALUES (?, ?)",
                (alerta.id_usuario,
                 f"Se le ha agendado una cita de acompañamiento para el día {f_h}. Nota: {notas}")
            )

            messagebox.showinfo(
                "Éxito", f"Cita programada para {f_h} y notificación enviada al profesional.")
            v_cita.destroy()

        ctk.CTkButton(
            v_cita,
            text="Confirmar y Notificar",
            fg_color="#0F4C81",
            command=confirmar
        ).pack(pady=15)

    def _actualizar_estado(self):
        sel = self.tree.selection()
        if not sel:
            return
        id_alerta = self.tree.item(sel[0])["values"][0]
        self.controller.actualizar_estado_alerta(
            id_alerta, self.combo_estado.get(), "Actualizado desde panel"
        )
        self._cargar_alertas()

    def cerrar_sesion(self):
        self.destroy()
        self.parent.deiconify()

    def cerrar_aplicacion(self):
        self.parent.destroy()
