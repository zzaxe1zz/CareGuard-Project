import customtkinter as ctk
from tkinter import messagebox
from controllers.kiosk_controller import KioskController
from utils.reset_timer import InactivityTimer


class KioskView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.controller = KioskController()

        self.title("CareGuard - Kiosco de Evaluación Anónima")
        self.geometry("600x500")

        # Temporizador de inactividad de 30 segundos (RF-10)
        self.timer = InactivityTimer(
            timeout_seconds=30, on_timeout_callback=self._resetear_pantalla)
        self.timer.iniciar()

        self.bind("<Any-KeyPress>", lambda e: self.timer.registrar_actividad())
        self.bind("<Any-ButtonPress>",
                  lambda e: self.timer.registrar_actividad())

        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self._crear_interfaz()

    def _crear_interfaz(self):
        self.lbl_title = ctk.CTkLabel(
            self, text="¿Cómo evalúa la atención recibida hoy?", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_title.pack(pady=20)

        # Calificación por Estrellas
        self.slider_calificacion = ctk.CTkSlider(
            self, from_=1, to=5, number_of_steps=4)
        self.slider_calificacion.set(5)
        self.slider_calificacion.pack(pady=10, fill="x", padx=60)

        self.lbl_estrellas = ctk.CTkLabel(
            self, text="5 / 5 Estrellas", font=ctk.CTkFont(size=16))
        self.lbl_estrellas.pack(pady=5)
        self.slider_calificacion.configure(
            command=lambda val: self.lbl_estrellas.configure(text=f"{int(val)} / 5 Estrellas"))

        # Comentario Opcional
        ctk.CTkLabel(
            self, text="Comentario u observación opcional:").pack(pady=5)
        self.txt_comentario = ctk.CTkTextbox(self, width=400, height=120)
        self.txt_comentario.pack(pady=10)

        # Enviar
        self.btn_enviar = ctk.CTkButton(
            self, text="Enviar Evaluación Anónima", fg_color="green", height=45, command=self._enviar_evaluacion
        )
        self.btn_enviar.pack(pady=20)

    def _enviar_evaluacion(self):
        calificacion = int(self.slider_calificacion.get())
        comentario = self.txt_comentario.get("1.0", "end-1c")

        self.controller.registrar_evaluacion_anonima(calificacion, comentario)
        messagebox.showinfo(
            "Muchas Gracias", "Su evaluación ha sido registrada de forma anónima.")
        self._resetear_pantalla()

    def _resetear_pantalla(self):
        """Reinicio automático de interfaz (RF-10 / MT-02)."""
        self.slider_calificacion.set(5)
        self.lbl_estrellas.configure(text="5 / 5 Estrellas")
        self.txt_comentario.delete("1.0", "end")

    def cerrar_aplicacion(self):
        self.timer.detener()
        self.parent.destroy()
