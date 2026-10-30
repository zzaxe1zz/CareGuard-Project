import customtkinter as ctk
from tkinter import messagebox, ttk
from controllers.medical_controller import MedicalController
from models.dto import SessionDTO


class MedicalView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = MedicalController(session)
        self.id_jornada_activa = None

        self.title("CareGuard - Estación de Trabajo Médica")
        self.after(0, lambda: self.wm_state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Header Institucional con Cierre de Sesión
        header = ctk.CTkFrame(self, fg_color="#0F4C81",
                              height=60, corner_radius=0)
        header.pack(fill="x", side="top")

        ctk.CTkLabel(header, text=f"👨‍⚕️ {self.session.nombre} [{self.session.rol}]", font=ctk.CTkFont(
            size=16, weight="bold"), text_color="white").pack(side="left", padx=20)
        ctk.CTkButton(header, text="Cerrar Sesión", fg_color="#EF4444", hover_color="#DC2626",
                      width=120, command=self.cerrar_sesion).pack(side="right", padx=20, pady=12)

        # Notificaciones activas
        self._verificar_notificaciones()

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_jornada = self.tabs.add("Gestión de Turno y Estrés")
        self.tab_historial = self.tabs.add("Mi Historial de Carga Laboral")

        self._configurar_tab_jornada()
        self._configurar_tab_historial()

    def _verificar_notificaciones(self):
        query = "SELECT id_notificacion, mensaje FROM notificaciones WHERE id_usuario = ? AND leido = 0"
        notifs = self.controller.db.obtener_todos(
            query, (self.session.id_usuario,))
        for n in notifs:
            messagebox.showinfo("📌 Notificación de Psicología", n["mensaje"])
            self.controller.db.ejecutar(
                "UPDATE notificaciones SET leido = 1 WHERE id_notificacion = ?", (n["id_notificacion"],))

    def _configurar_tab_jornada(self):
        f_turno = ctk.CTkFrame(self.tab_jornada)
        f_turno.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(f_turno, text="Registro de Horario Laboral",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=10)

        self.btn_entrada = ctk.CTkButton(
            f_turno, text="Registrar Entrada", fg_color="#10B981", hover_color="#059669", command=self._registrar_entrada)
        self.btn_entrada.pack(side="left", padx=20, pady=15)

        self.btn_descanso = ctk.CTkButton(
            f_turno, text="Registrar Descanso (Pausa)", command=self._abrir_modal_descanso, state="disabled")
        self.btn_descanso.pack(side="left", padx=10, pady=15)

        # Registro de Estrés con Barra graduada 1-10
        f_emo = ctk.CTkFrame(self.tab_jornada)
        f_emo.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(f_emo, text="Evaluación de Cierre de Turno",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=10)

        self.lbl_valor_estres = ctk.CTkLabel(
            f_emo, text="Nivel de Estrés: 5 / 10", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_valor_estres.pack(pady=5)

        # Regla con marcas numéricas
        f_escala = ctk.CTkFrame(f_emo, fg_color="transparent")
        f_escala.pack(fill="x", padx=60)
        for num in range(1, 11):
            ctk.CTkLabel(f_escala, text=str(num), font=ctk.CTkFont(
                size=11)).pack(side="left", expand=True)

        self.slider_estres = ctk.CTkSlider(
            f_emo, from_=1, to=10, number_of_steps=9, command=self._actualizar_lbl_estres)
        self.slider_estres.set(5)
        self.slider_estres.pack(fill="x", padx=60, pady=5)

        ctk.CTkLabel(f_emo, text="Estado de Ánimo Predominante:").pack(pady=5)
        self.combo_animo = ctk.CTkOptionMenu(
            f_emo, values=["Excelente", "Estable", "Agotado", "Muy Estresado"])
        self.combo_animo.pack(pady=5)

        self.txt_notas = ctk.CTkTextbox(f_emo, height=60, width=450)
        self.txt_notas.pack(pady=10)

        self.btn_salida = ctk.CTkButton(f_emo, text="Cerrar Turno y Guardar Registro",
                                        fg_color="#0F4C81", command=self._registrar_salida, state="disabled")
        self.btn_salida.pack(pady=10)

        ctk.CTkButton(self.tab_jornada, text="Solicitar Apoyo Psicológico Confidencial",
                      fg_color="#DC2626", hover_color="#B91C1C", command=self._solicitar_apoyo).pack(pady=10)

    def _actualizar_lbl_estres(self, val):
        self.lbl_valor_estres.configure(
            text=f"Nivel de Estrés: {int(val)} / 10")

    def _abrir_modal_descanso(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Registro de Descanso")
        modal.geometry("380x280")
        modal.grab_set()

        ctk.CTkLabel(modal, text="Registro de Pausa o Comida",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        entry_i = ctk.CTkEntry(
            modal, placeholder_text="Hora Inicio (HH:MM:SS)")
        entry_i.pack(pady=10)
        entry_f = ctk.CTkEntry(modal, placeholder_text="Hora Fin (HH:MM:SS)")
        entry_f.pack(pady=10)

        def guardar():
            try:
                fecha_hoy = self.controller.workday_manager.db.obtener_uno(
                    "SELECT fecha FROM jornadas WHERE id_jornada = ?", (self.id_jornada_activa,))["fecha"]
                h_i = f"{fecha_hoy} {entry_i.get().strip()}"
                h_f = f"{fecha_hoy} {entry_f.get().strip()}"
                self.controller.registrar_descanso(
                    self.id_jornada_activa, h_i, h_f)
                messagebox.showinfo(
                    "Éxito", "Descanso registrado correctamente.")
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Guardar Descanso",
                      command=guardar).pack(pady=15)

    def _configurar_tab_historial(self):
        ctk.CTkButton(self.tab_historial, text="Cargar Historial",
                      command=self._cargar_historial).pack(pady=10)
        self.tree = ttk.Treeview(self.tab_historial, columns=(
            "Fecha", "Entrada", "Salida", "Horas Trab", "Horas Extra"), show="headings")
        for c in ("Fecha", "Entrada", "Salida", "Horas Trab", "Horas Extra"):
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

    def _registrar_entrada(self):
        self.id_jornada_activa = self.controller.iniciar_jornada()
        messagebox.showinfo(
            "Éxito", f"Jornada iniciada ID #{self.id_jornada_activa}")
        self.btn_entrada.configure(state="disabled")
        self.btn_descanso.configure(state="normal")
        self.btn_salida.configure(state="normal")

    def _registrar_salida(self):
        res = self.controller.finalizar_jornada_y_evaluar(self.id_jornada_activa, int(
            self.slider_estres.get()), self.combo_animo.get(), self.txt_notas.get("1.0", "end-1c"))
        msg = f"Turno Cerrado.\nHoras Trabajadas: {res['resumen_jornada']['horas_trabajadas']}\nHoras Extra: {res['resumen_jornada']['horas_extra']}"
        if res['alerta_generada']:
            msg += "\n\nSe ha emitido una alerta automática de sobrecarga preventiva hacia Psicología."
        messagebox.showinfo("Registro Exitoso", msg)
        self.id_jornada_activa = None
        self.btn_entrada.configure(state="normal")
        self.btn_descanso.configure(state="disabled")
        self.btn_salida.configure(state="disabled")

    def _solicitar_apoyo(self):
        self.controller.solicitar_apoyo_psicologico(
            "Solicitud voluntaria desde panel médico.")
        messagebox.showinfo(
            "Confirmación", "Su solicitud ha sido enviada confidencialmente a Psicología.")

    def _cargar_historial(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for f in self.controller.consultar_historial_propio():
            self.tree.insert("", "end", values=(
                f["fecha"], f["hora_entrada"], f["hora_salida"] or "En Curso", f["horas_trabajadas"], f["horas_extra"]))

    def cerrar_sesion(self):
        self.destroy()
        self.parent.deiconify()

    def cerrar_aplicacion(self):
        self.parent.destroy()
