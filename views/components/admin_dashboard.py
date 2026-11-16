from tkinter import messagebox

import customtkinter as ctk

from controllers.admin_controller import AdminController
from models.dto import SessionDTO
from views import ui_kit as ui

# Código en BD -> (texto visible, color de la etiqueta)
ROLES = {
    "MEDICO": ("Médico", ui.MINT),
    "ENFERMERO": ("Enfermero", "#CFE6FF"),
    "PSICOLOGO": ("Psicólogo", ui.LAVENDER),
    "ADMIN": ("Admin", ui.PINK),
}
ROL_POR_TEXTO = {v[0]: k for k, v in ROLES.items()}


def color_carga(fraccion: float) -> str:
    if fraccion >= 0.75:
        return "#FF3B3B"
    if fraccion >= 0.4:
        return "#FFD84D"
    return "#4ADE80"


class AdminDashboardView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = AdminController(session)

        ui.configurar_ventana(self, "CareGuard - Panel de Control Administrativo", 1180, 760)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self.shell = ui.Shell(self, session, "Administración general", self.cerrar_sesion)
        self.shell.agregar_pagina("Métricas", self._pagina_metricas,
                                  on_show=self._cargar_metricas)
        self.shell.agregar_pagina("Usuarios", self._pagina_usuarios,
                                  on_show=self._cargar_usuarios)
        self.shell.agregar_pagina("Evaluaciones", self._pagina_evaluaciones,
                                  on_show=self._cargar_evaluaciones)
        self.shell.iniciar()

    def _pagina_metricas(self, parent):
        card = ui.tarjeta(parent)
        card.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=22, pady=(18, 4))
        ui.etiqueta(cab, "Panel Institucional - Métricas Anonimizadas", size=17).pack(side="left")
        ui.boton(cab, "Actualizar", self._cargar_metricas, color=ui.GRAY,
                 texto_color=ui.INK, alto=32, ancho=100, size=12).pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color=ui.CARD_BORDER).pack(
            fill="x", padx=22, pady=(8, 14))

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=(14, 8), pady=(0, 10))

        kpis = ctk.CTkFrame(scroll, fg_color="transparent")
        kpis.pack(fill="x")
        kpis.grid_columnconfigure((0, 1, 2), weight=1, uniform="k")
        self.kpi_sat = ui.tarjeta_kpi(kpis, "Satisfacción pacientes", "—", color_valor="#B7791F")
        self.kpi_horas = ui.tarjeta_kpi(kpis, "Horas extra hospitalarias", "—")
        self.kpi_jornadas = ui.tarjeta_kpi(kpis, "Jornadas registradas", "—")
        for i, k in enumerate((self.kpi_sat, self.kpi_horas, self.kpi_jornadas)):
            k.grid(row=0, column=i, sticky="ew", padx=8)

        fila = ctk.CTkFrame(scroll, fg_color="transparent")
        fila.pack(fill="x", pady=(18, 0))
        fila.grid_columnconfigure((0, 1), weight=1, uniform="p")

        self.panel_roles = ctk.CTkFrame(fila, fg_color="transparent")
        self.panel_roles.grid(row=0, column=0, sticky="new", padx=8)
        ui.etiqueta(self.panel_roles, "CARGA LABORAL POR ROL (HORAS EXTRA · 30 DÍAS)",
                    size=12, anchor="w").pack(fill="x", pady=(0, 10))
        self.cont_roles = ctk.CTkFrame(self.panel_roles, fg_color="transparent")
        self.cont_roles.pack(fill="x")

        self.panel_alertas = ctk.CTkFrame(fila, fg_color="transparent")
        self.panel_alertas.grid(row=0, column=1, sticky="new", padx=8)
        ui.etiqueta(self.panel_alertas, "ESTADO DE LAS ALERTAS", size=12, anchor="w").pack(
            fill="x", pady=(0, 10))
        self.cont_alertas = ctk.CTkFrame(self.panel_alertas, fg_color="transparent")
        self.cont_alertas.pack(fill="x")

        ui.etiqueta(scroll, "PROMEDIO INSTITUCIONAL DE ESTRÉS (ÚLTIMOS 7 DÍAS CON REGISTROS)",
                    size=12, anchor="w").pack(fill="x", padx=8, pady=(10, 0))
        self.grafica = ui.GraficaEstres(scroll, [], bg=ui.CARD, alto=230)
        self.grafica.pack(fill="x", padx=8, pady=(4, 10))

    def _limpiar(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _cargar_metricas(self):
        try:
            m = self.controller.obtener_metricas_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las métricas.\n{e}", parent=self)
            return
        self.kpi_sat.lbl_valor.configure(text=f"{m['promedio_satisfaccion']:.1f} / 5.0  ★")
        self.kpi_horas.lbl_valor.configure(text=f"{m['total_horas_extra']:g} hrs")
        self.kpi_jornadas.lbl_valor.configure(text=f"{m['total_jornadas']:,} turnos")

        self._limpiar(self.cont_roles)
        filas = sorted(m["horas_extra_agregadas"], key=lambda r: -(r["total_horas_extra"] or 0))
        tope = max([(r["total_horas_extra"] or 0) for r in filas] or [1]) or 1
        if not filas:
            ui.etiqueta(self.cont_roles, "Sin jornadas en los últimos 30 días.", size=12,
                        weight="normal", color=ui.MUTED).pack(anchor="w")
        for r in filas:
            horas = r["total_horas_extra"] or 0
            nombre = ROLES.get(r["rol"], (r["rol"],))[0]
            ui.barra_progreso(self.cont_roles, nombre, f"{horas:.0f} hrs",
                              horas / tope, color_carga(horas / tope)).pack(fill="x")

        self._limpiar(self.cont_alertas)
        por_estado = m["alertas_por_estado"]
        total = sum(por_estado.values()) or 1
        for clave, nombre, color in (("PENDIENTE", "Pendientes", "#F43F5E"),
                                     ("EN_ATENCION", "En atención", "#FFC83D"),
                                     ("CERRADA", "Cerradas", "#4ADE80")):
            n = por_estado.get(clave, 0)
            ui.barra_progreso(self.cont_alertas, nombre, f"{n}", n / total,
                              color).pack(fill="x")

        datos = [((ui.parse_dt(d).strftime("%d/%m") if ui.parse_dt(d) else d), v)
                 for d, v in m["tendencia_estres"]]
        self.grafica.actualizar(datos)

    def _pagina_usuarios(self, parent):
        parent.grid_columnconfigure(0, weight=3, uniform="u")
        parent.grid_columnconfigure(1, weight=2, uniform="u")
        parent.grid_rowconfigure(0, weight=1)

        izq = ui.tarjeta(parent)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ui.titulo_tarjeta(izq, "ADMINISTRACIÓN DE CUENTAS DE USUARIO")
        self.tabla_usr = ui.Tabla(izq, [("Usuario", 1.6, "w"),
                                        ("Rol Asignado", 1.3, "center"),
                                        ("Estado", 1, "center")],
                                  vacio="No hay usuarios registrados.")
        self.tabla_usr.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        der = ui.tarjeta(parent)
        der.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ui.titulo_tarjeta(der, "ALTA DE USUARIO")
        form = ctk.CTkFrame(der, fg_color="transparent")
        form.pack(fill="x", padx=22)

        ui.etiqueta(form, "Nombre Completo*", anchor="w").pack(fill="x")
        self.entry_nom = ui.entrada(form)
        self.entry_nom.pack(fill="x", pady=(4, 10))
        ui.etiqueta(form, "Username*", anchor="w").pack(fill="x")
        self.entry_usr = ui.entrada(form)
        self.entry_usr.pack(fill="x", pady=(4, 10))
        ui.etiqueta(form, "Contraseña inicial*", anchor="w").pack(fill="x")
        self.entry_pwd = ui.entrada(form, show="*")
        self.entry_pwd.pack(fill="x", pady=(4, 10))
        ui.etiqueta(form, "Rol*", anchor="w").pack(fill="x")
        self.combo_rol = ui.desplegable(form, list(ROL_POR_TEXTO))
        self.combo_rol.set("Médico")
        self.combo_rol.pack(fill="x", pady=(4, 16))
        ui.boton(form, "Guardar Credenciales", self._registrar, color=ui.BLACK,
                 alto=46, size=14, corner_radius=12).pack(fill="x", padx=30)

    def _cargar_usuarios(self):
        try:
            usuarios = self.controller.listar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.tabla_usr.limpiar()
        if not usuarios:
            self.tabla_usr.mostrar_vacio()
            return
        for u in usuarios:
            texto_rol, color_rol = ROLES.get(u["rol"], (u["rol"], ui.GRAY))
            activo = u["estado"] == "ACTIVO"

            def celda_usuario(p, u=u):
                f = ctk.CTkFrame(p, fg_color="transparent")
                ui.etiqueta(f, u["usuario"], size=13, anchor="w").pack(anchor="w")
                ui.etiqueta(f, u["nombre"], size=11, weight="normal", color=ui.MUTED,
                            anchor="w").pack(anchor="w")
                return f

            self.tabla_usr.agregar_fila([
                celda_usuario,
                lambda p, t=texto_rol, c=color_rol: ui.pill(p, t, c, ancho=110),
                lambda p, a=activo: ui.etiqueta(
                    p, "Activo" if a else "Inactivo", size=13,
                    color="#047857" if a else "#B91C1C"),
            ], "#FFFFFF")

    def _registrar(self):
        nombre, usuario, pwd = (self.entry_nom.get().strip(),
                                self.entry_usr.get().strip(), self.entry_pwd.get())
        if not nombre or not usuario or not pwd:
            messagebox.showwarning("Atención", "Complete nombre, username y contraseña.",
                                   parent=self)
            return
        try:
            self.controller.registrar_usuario(
                nombre, usuario, pwd, ROL_POR_TEXTO[self.combo_rol.get()])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo("Éxito", "Usuario registrado correctamente.", parent=self)
        for e in (self.entry_nom, self.entry_usr, self.entry_pwd):
            e.delete(0, "end")
        self._cargar_usuarios()

    def _pagina_evaluaciones(self, parent):
        card = ui.tarjeta(parent)
        card.pack(fill="both", expand=True)
        ui.titulo_tarjeta(card, "EVALUACIONES DE PACIENTES", size=17)

        self.tabla_eval = ui.Tabla(card, [("Paciente", 1.2, "w"),
                                          ("Calificación", 1.7, "center"),
                                          ("Comentario", 2.6, "w")],
                                   vacio="Aún no hay evaluaciones.")
        self.tabla_eval.pack(fill="both", expand=True, padx=22, pady=(0, 6))

        pie = ctk.CTkFrame(card, fg_color="transparent")
        pie.pack(fill="x", padx=24, pady=(4, 18))
        ui.etiqueta(pie, "Satisfacción promedio", size=15).pack(side="left")
        self.lbl_prom = ui.etiqueta(pie, "—", size=18, color="#B7791F")
        self.lbl_prom.pack(side="left", padx=(16, 10))
        self.estrellas_prom = ui.Estrellas(pie, tam=22, valor=0, interactiva=False,
                                           bg=ui.CARD, espacio=4)
        self.estrellas_prom.pack(side="left")
        self.lbl_total = ui.etiqueta(pie, "", size=12, weight="normal", color=ui.MUTED)
        self.lbl_total.pack(side="right")

    def _cargar_evaluaciones(self):
        try:
            r = self.controller.listar_evaluaciones()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.lbl_prom.configure(text=f"{r['promedio']:.1f} / 5")
        self.estrellas_prom.set(int(round(r["promedio"])))
        self.lbl_total.configure(
            text=f"{r['total']} evaluaciones · mostrando las {len(r['evaluaciones'])} más recientes")
        self.tabla_eval.limpiar()
        if not r["evaluaciones"]:
            self.tabla_eval.mostrar_vacio()
            return
        for i, ev in enumerate(r["evaluaciones"], start=1):
            comentario = ev["comentario"] or "—"
            self.tabla_eval.agregar_fila([
                f"Paciente {i}",
                lambda p, v=ev["calificacion"], c="#FFFFFF": ui.Estrellas(
                    p, tam=22, valor=v, interactiva=False, bg=c, espacio=4),
                lambda p, t=comentario: ui.etiqueta(
                    p, t, size=13, weight="normal", anchor="w", justify="left",
                    wraplength=420),
            ], "#FFFFFF")

    def cerrar_sesion(self):
        ui.volver_a_login(self)

    def cerrar_aplicacion(self):
        self.parent.destroy()
