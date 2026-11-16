import os
import sys

# Permite ejecutar desde cualquier carpeta (VS Code, doble clic, terminal).
RAIZ = os.path.dirname(os.path.abspath(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

try:
    import customtkinter as ctk
    from tkinter import messagebox
except ModuleNotFoundError as err:
    print("\n[CareGuard] Falta instalar una dependencia:", err.name)
    print("Ejecute en la terminal:  pip install -r requirements.txt\n")
    raise SystemExit(1)

from controllers.auth_controller import AuthController
from database.db_adapter import DatabaseAdapter
from database.seed import sembrar_datos_completos
from views import ui_kit as ui
from views.components.admin_dashboard import AdminDashboardView
from views.components.kiosk_view import KioskView
from views.components.medical_view import MedicalView
from views.components.psychology_view import PsychologyView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

ROL_TEXTO = {
    "MEDICO": "Médico",
    "ENFERMERO": "Enfermero",
    "PSICOLOGO": "Psicólogo",
    "ADMIN": "Administrador",
}


def asegurar_datos_iniciales():
    """Si la base de datos está vacía (primera ejecución) la llena con datos de prueba."""
    db = DatabaseAdapter()
    fila = db.obtener_uno("SELECT COUNT(*) AS n FROM usuarios")
    if not fila or fila["n"] == 0:
        sembrar_datos_completos()


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ui.configurar_ventana(self, "CareGuard - Plataforma de Monitoreo Clínico",
                              980, 700, minimo=(760, 620))
        self.auth_controller = AuthController()

        card = ui.tarjeta(self, corner_radius=18)
        card.place(relx=0.5, rely=0.5, anchor="center")

        cuerpo = ctk.CTkFrame(card, fg_color="transparent")
        cuerpo.pack(padx=46, pady=34)

        ui.insignia_avatar(cuerpo, 72, bg=ui.CARD).pack()
        ui.etiqueta(cuerpo, "Bienvenido a CareGuard", size=24).pack(pady=(12, 0))
        ui.etiqueta(cuerpo, "Gestión de Salud Mental y Carga Laboral Hospitalaria",
                    size=12, weight="normal", color=ui.MUTED).pack(pady=(2, 20))

        ui.etiqueta(cuerpo, "Usuario / Código*", anchor="w").pack(fill="x")
        self.entry_usuario = ui.entrada(cuerpo, "Usuario o código institucional", width=360)
        self.entry_usuario.pack(pady=(4, 12))

        ui.etiqueta(cuerpo, "Contraseña*", anchor="w").pack(fill="x")
        self.entry_password = ui.entrada(cuerpo, "Contraseña", show="*", width=360)
        self.entry_password.pack(pady=(4, 4))

        self.chk_ver = ctk.CTkCheckBox(
            cuerpo, text="Mostrar contraseña", command=self._alternar_password,
            font=ui.font(12), text_color=ui.MUTED, fg_color=ui.BLUE,
            hover_color=ui.BLUE_HOVER, border_color=ui.INPUT_BORDER,
            corner_radius=5, checkbox_width=18, checkbox_height=18)
        self.chk_ver.pack(anchor="w", pady=(0, 12))

        self.lbl_ayuda = ui.etiqueta(
            cuerpo, "Su rol (Médico, Enfermero, Psicólogo o Administrador) se detecta "
            "automáticamente al iniciar sesión.", size=11, weight="normal",
            color=ui.MUTED, wraplength=360)
        self.lbl_ayuda.pack(pady=(0, 10))

        self.btn_login = ui.boton(cuerpo, "Ingresar al Sistema", self.procesar_login,
                                  color=ui.BLUE, ancho=260, alto=44, size=14)
        self.btn_login.pack(pady=(6, 0))

        self.btn_kiosco = ui.boton(cuerpo, "Soy paciente · Abrir Kiosco de Evaluación",
                                   self.abrir_kiosco, color=ui.GRAY, texto_color=ui.INK,
                                   ancho=260, alto=36, size=12)
        self.btn_kiosco.pack(pady=(10, 0))

        self.bind("<Return>", lambda _e: self.procesar_login())
        self.entry_usuario.focus_set()

    def _alternar_password(self):
        self.entry_password.configure(show="" if self.chk_ver.get() else "*")

    def mostrar(self):
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.deiconify()
        self.lift()
        self.entry_usuario.focus_set()

    def procesar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        if not usuario or not password:
            messagebox.showwarning("Atención", "Ingrese sus credenciales de acceso.")
            return

        session = self.auth_controller.login(usuario, password)
        if not session:
            messagebox.showerror("Error", "Credenciales institucionales incorrectas.")
            return

        # El rol viene de la base de datos: no hace falta seleccionarlo.
        self.withdraw()
        if session.rol in ("MEDICO", "ENFERMERO"):
            MedicalView(self, session)
        elif session.rol == "PSICOLOGO":
            PsychologyView(self, session)
        elif session.rol == "ADMIN":
            AdminDashboardView(self, session)
        else:
            self.deiconify()
            messagebox.showerror("Rol no reconocido",
                                 f"El rol «{ROL_TEXTO.get(session.rol, session.rol)}» no tiene acceso.")

    def abrir_kiosco(self):
        self.withdraw()
        KioskView(self)


if __name__ == "__main__":
    asegurar_datos_iniciales()
    app = LoginWindow()
    app.mainloop()
