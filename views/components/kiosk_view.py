import customtkinter as ctk
from tkinter import messagebox

from controllers.kiosk_controller import KioskController
from utils.reset_timer import InactivityTimer
from views import ui_kit as ui

SIN_INDICAR = "Prefiero no indicar"
BG_TRANSPARENT = "transparent"
TEXTO_ESTRELLAS = {0: "Toque una estrella para calificar", 1: "Muy mala", 2: "Mala",
                   3: "Regular", 4: "Buena", 5: "Excelente"}


class KioskView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.controller = KioskController()

        ui.configurar_ventana(self, "CareGuard - Kiosco de Evaluación Anónima", 860, 760,
                              minimo=(760, 700))
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        # Reinicio automático tras 30 s sin actividad (RF-10 / MT-02)
        self.timer = InactivityTimer(timeout_seconds=30,
                                     on_timeout_callback=self._resetear_pantalla,
                                     widget=self)
        self.timer.iniciar()
        for evento in ("<Any-KeyPress>", "<Any-ButtonPress>", "<Motion>"):
            self.bind(evento, lambda _e: self.timer.registrar_actividad(), add="+")
        self._id_gracias = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        self.card = ui.tarjeta(self, corner_radius=18)
        self.card.pack(fill="both", expand=True, padx=40, pady=(30, 8))

        ui.insignia_estrella(self.card, 96, bg=ui.CARD).pack(pady=(26, 6))

        self.form = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form.pack(fill="both", expand=True)

        ui.etiqueta(self.form, "¿Cómo fue su atención el día de hoy?", size=24).pack(pady=(4, 18))

        fila = ctk.CTkFrame(self.form, fg_color="transparent")
        fila.pack(fill="x", padx=70)
        ui.etiqueta(fila, "Personal Médico:", size=15).pack(side="left")
        ui.etiqueta(fila, "(opcional)", size=12, weight="normal",
                    color=ui.MUTED).pack(side="left", padx=8)
        try:
            personal = [SIN_INDICAR] + self.controller.listar_personal()
        except Exception:
            personal = [SIN_INDICAR]
        self.combo_personal = ui.desplegable(self.form, personal, anchor="w")
        self.combo_personal.set(SIN_INDICAR)
        self.combo_personal.pack(fill="x", padx=70, pady=(6, 20))

        self.estrellas = ui.Estrellas(self.form, tam=54, valor=0, bg=ui.CARD,
                                      comando=self._calificacion_cambiada, espacio=12)
        self.estrellas.pack()
        self.lbl_estrellas = ui.etiqueta(self.form, TEXTO_ESTRELLAS[0], size=14,
                                         weight="normal", color=ui.MUTED)
        self.lbl_estrellas.pack(pady=(6, 18))

        self.entry_comentario = ui.entrada(
            self.form, "Comentario opcional sobre el servicio…", alto=48)
        self.entry_comentario.pack(fill="x", padx=70)

        self.btn_enviar = ui.boton(self.form, "Enviar Evaluación Anónima",
                                   self._enviar_evaluacion, color=ui.GOLD,
                                   alto=50, size=15, corner_radius=14)
        self.btn_enviar.pack(fill="x", padx=150, pady=(22, 10))
        ui.etiqueta(self.form, "Su evaluación es anónima: no se guarda ningún dato personal.",
                    size=11, weight="normal", color=ui.MUTED).pack(pady=(0, 10))

        self.gracias = ctk.CTkFrame(self.card, fg_color="transparent")
        ui.etiqueta(self.gracias, "¡Muchas gracias!", size=30, color=ui.GOLD).pack(pady=(40, 8))
        ui.etiqueta(self.gracias, "Su evaluación fue registrada de forma anónima.",
                    size=16, weight="normal").pack()
        ui.etiqueta(self.gracias, "Esta pantalla se reiniciará automáticamente.",
                    size=12, weight="normal", color=ui.MUTED).pack(pady=(10, 0))

        ui.boton(self, "← Volver al inicio", self.volver_inicio, color=BG_TRANSPARENT,
                 texto_color=ui.MUTED, alto=30, ancho=150, size=12,
                 hover_color="#DCE3EA").pack(pady=(0, 10))

    def _calificacion_cambiada(self, valor):
        self.lbl_estrellas.configure(text=TEXTO_ESTRELLAS.get(valor, ""),
                                     text_color=ui.INK)

    def _enviar_evaluacion(self):
        calificacion = self.estrellas.get()
        if calificacion < 1:
            messagebox.showwarning("Falta calificación",
                                   "Por favor seleccione de 1 a 5 estrellas.", parent=self)
            return
        personal = self.combo_personal.get()
        if personal == SIN_INDICAR:
            personal = ""
        try:
            self.controller.registrar_evaluacion_anonima(
                calificacion, self.entry_comentario.get(), personal)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.form.pack_forget()
        self.gracias.pack(fill="both", expand=True)
        self._id_gracias = self.after(4000, self._resetear_pantalla)

    def _resetear_pantalla(self):
        if self._id_gracias is not None:
            try:
                self.after_cancel(self._id_gracias)
            except Exception:
                pass
            self._id_gracias = None
        self.gracias.pack_forget()
        if not self.form.winfo_ismapped():
            self.form.pack(fill="both", expand=True)
        self.estrellas.set(0)
        self.lbl_estrellas.configure(text=TEXTO_ESTRELLAS[0], text_color=ui.MUTED)
        self.combo_personal.set(SIN_INDICAR)
        self.entry_comentario.delete(0, "end")

    def volver_inicio(self):
        self.timer.detener()
        ui.volver_a_login(self)

    def cerrar_aplicacion(self):
        self.timer.detener()
        self.parent.destroy()
