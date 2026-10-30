import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from views.components.medical_view import MedicalView
from views.components.psychology_view import PsychologyView
from views.components.admin_dashboard import AdminDashboardView
from views.components.kiosk_view import KioskView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CareGuard - Plataforma de Monitoreo Clínico")

        # Inicio en modo pantalla completa / maximizado
        self.after(0, lambda: self.wm_state('zoomed'))

        self.auth_controller = AuthController()

        # Contenedor central
        self.frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#F8FAFC")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.frame, text="🏥 CareGuard", font=ctk.CTkFont(
            size=32, weight="bold"), text_color="#0F4C81").pack(padx=60, pady=(40, 5))
        ctk.CTkLabel(self.frame, text="Gestión de Salud Mental y Carga Laboral Hospitalaria",
                     font=ctk.CTkFont(size=13), text_color="#64748B").pack(pady=(0, 25))

        self.entry_usuario = ctk.CTkEntry(
            self.frame, placeholder_text="Usuario o Código Institucional", width=320, height=45)
        self.entry_usuario.pack(pady=10)

        self.entry_password = ctk.CTkEntry(
            self.frame, placeholder_text="Contraseña", show="*", width=320, height=45)
        self.entry_password.pack(pady=10)

        self.btn_login = ctk.CTkButton(self.frame, text="Iniciar Sesión", fg_color="#0F4C81",
                                       hover_color="#1B65A6", width=320, height=45, command=self.procesar_login)
        self.btn_login.pack(pady=(20, 10))

        self.btn_kiosco = ctk.CTkButton(self.frame, text="Acceder a Kiosco Público (Pacientes)",
                                        fg_color="#475569", hover_color="#334155", width=320, height=35, command=self.abrir_kiosco)
        self.btn_kiosco.pack(pady=(0, 30))

    def procesar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            messagebox.showwarning(
                "Atención", "Ingrese sus credenciales de acceso.")
            return

        session = self.auth_controller.login(usuario, password)

        if not session:
            messagebox.showerror(
                "Error", "Credenciales institucionales incorrectas.")
            return

        self.withdraw()

        if session.rol in ["MEDICO", "ENFERMERO"]:
            MedicalView(self, session)
        elif session.rol == "PSICOLOGO":
            PsychologyView(self, session)
        elif session.rol == "ADMIN":
            AdminDashboardView(self, session)

    def abrir_kiosco(self):
        self.withdraw()
        KioskView(self)


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
