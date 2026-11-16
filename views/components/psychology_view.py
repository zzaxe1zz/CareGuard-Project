from datetime import datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk

from controllers.psychology_controller import PsychologyController
from models.dto import SessionDTO
from services.burnout_engine import BurnoutEngine
from views import ui_kit as ui

ESTADOS = {
    "PENDIENTE": ("Pendiente", "#F7B6CE", ui.ROW_PINK),
    "EN_ATENCION": ("En Atención", "#E3B8F7", ui.ROW_AMBER),
    "CERRADA": ("Cerrada", "#9BE3BF", ui.ROW_MINT),
}
FILTROS = {"Todas": None, "Pendientes": "PENDIENTE",
           "En atención": "EN_ATENCION", "Cerradas": "CERRADA"}


def texto_tipo(tipo: str) -> str:
    return "Algoritmo (Sobrecarga)" if tipo == "ALGORITMO" else "VOLUNTARIO"


class PsychologyView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = PsychologyController(session)
        self.alertas = {}

        ui.configurar_ventana(self, "CareGuard - Panel de Psicología y Salud Mental", 1180, 740)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self.shell = ui.Shell(self, session, "Psicología clínica", self.cerrar_sesion)
        self.shell.agregar_pagina("Alertas de Burnout", self._pagina_alertas,
                                  on_show=self._cargar_alertas)
        self.shell.agregar_pagina("Historial de Pacientes", self._pagina_pacientes,
                                  on_show=self._cargar_pacientes)
        self.shell.iniciar()

    def _pagina_alertas(self, parent):
        card = ui.tarjeta(parent)
        card.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=22, pady=(18, 4))
        ui.etiqueta(cab, "Control de Alertas de Burnout - Módulo Psicología", size=17).pack(side="left")
        ui.boton(cab, "Actualizar", self._cargar_alertas, color=ui.GRAY,
                 texto_color=ui.INK, alto=32, ancho=100, size=12).pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color=ui.CARD_BORDER).pack(
            fill="x", padx=22, pady=(8, 12))

        barra = ctk.CTkFrame(card, fg_color="transparent")
        barra.pack(fill="x", padx=22, pady=(0, 10))
        self.filtro = ctk.CTkSegmentedButton(
            barra, values=list(FILTROS), command=lambda _v: self._pintar_alertas(),
            height=32, corner_radius=10, fg_color="#E3E7EC", selected_color=ui.PURPLE,
            selected_hover_color=ui.PURPLE_HOVER, unselected_color="#E3E7EC",
            unselected_hover_color="#D3D9E0", text_color=ui.INK, font=ui.font(12, "bold"))
        self.filtro.set("Todas")
        self.filtro.pack(side="left")
        self.lbl_resumen = ui.etiqueta(barra, "", size=12, weight="normal", color=ui.MUTED)
        self.lbl_resumen.pack(side="right")

        self.tabla = ui.Tabla(card, [
            ("ID Alerta", 0.8, "center"), ("Motivo", 1.7, "center"),
            ("Personal Médico", 2.0, "center"), ("Fecha/Hora", 1.7, "center"),
            ("Estado", 1.3, "center"), ("Acción", 1.1, "center")],
            header_bg=ui.HEADER_LAV, vacio="No hay alertas con este filtro.")
        self.tabla.pack(fill="both", expand=True, padx=22, pady=(0, 18))

    def _cargar_alertas(self):
        try:
            lista = self.controller.consultar_bandeja_alertas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la bandeja.\n{e}", parent=self)
            return
        self.alertas = {a.id_alerta: a for a in lista}
        self._pintar_alertas()

    def _pintar_alertas(self):
        todas = list(self.alertas.values())
        pendientes = sum(1 for a in todas if a.estado == "PENDIENTE")
        self.lbl_resumen.configure(
            text=f"{len(todas)} alertas · {pendientes} pendientes")

        quiere = FILTROS[self.filtro.get()]
        self.tabla.limpiar()
        visibles = [a for a in todas if quiere is None or a.estado == quiere]
        if not visibles:
            self.tabla.mostrar_vacio()
            return
        for a in visibles:
            nombre_est, color_pill, fondo = ESTADOS.get(a.estado, (a.estado, ui.GRAY, ui.ROW_PINK))
            if a.estado == "PENDIENTE":
                accion = ("Atender", lambda i=a.id_alerta: self._atender(i))
            elif a.estado == "EN_ATENCION":
                accion = ("Notas", lambda i=a.id_alerta: self._abrir_notas(i))
            else:
                accion = ("Ver", lambda i=a.id_alerta: self._abrir_expediente(i))
            self.tabla.agregar_fila([
                f"{a.id_alerta:05d}", texto_tipo(a.tipo), a.nombre_profesional,
                ui.fecha_hora(a.fecha_generacion),
                lambda p, t=nombre_est, c=color_pill: ui.pill(p, t, c, ancho=110),
                lambda p, ac=accion: ui.boton(
                    p, ac[0], ac[1], color="#E3B8F7", texto_color=ui.INK,
                    ancho=96, alto=26, size=12, corner_radius=13),
            ], fondo)

    def _atender(self, id_alerta):
        # La alerta sigue PENDIENTE hasta que se confirme una fecha de cita
        # (ver CitaWindow); solo abrir el expediente no la cambia a «En Atención».
        self._abrir_expediente(id_alerta)

    def _abrir_expediente(self, id_alerta):
        alerta = self.alertas.get(id_alerta)
        if alerta:
            ExpedienteWindow(self, self.controller, alerta, self._abrir_cita)

    def _abrir_cita(self, alerta):
        CitaWindow(self, self.controller, alerta, al_agendar=self._cita_agendada)

    def _cita_agendada(self):
        self._cargar_alertas()
        self._cargar_pacientes()

    def _pagina_pacientes(self, parent):
        card = ui.tarjeta(parent)
        card.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=22, pady=(18, 4))
        ui.etiqueta(cab, "Historial de Pacientes - Módulo Psicología", size=17).pack(side="left")
        ui.boton(cab, "Actualizar", self._cargar_pacientes, color=ui.GRAY,
                 texto_color=ui.INK, alto=32, ancho=100, size=12).pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color=ui.CARD_BORDER).pack(
            fill="x", padx=22, pady=(8, 12))

        self.tabla_pacientes = ui.Tabla(card, [
            ("Paciente", 2.2, "w"), ("Rol", 1.2, "center"),
            ("Alertas (abiertas/total)", 1.6, "center"),
            ("Próxima cita", 1.7, "center"), ("Acción", 1.3, "center")],
            header_bg=ui.HEADER_LAV, vacio="No hay pacientes registrados.")
        self.tabla_pacientes.pack(fill="both", expand=True, padx=22, pady=(0, 18))

    def _cargar_pacientes(self):
        try:
            pacientes = self.controller.listar_pacientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el listado.\n{e}", parent=self)
            return
        self.tabla_pacientes.limpiar()
        if not pacientes:
            self.tabla_pacientes.mostrar_vacio()
            return
        for p in pacientes:
            rol = "Enfermería" if p["rol"] == "ENFERMERO" else "Médico"
            fondo = ui.ROW_AMBER if p["alertas_abiertas"] else ui.ROW_MINT
            self.tabla_pacientes.agregar_fila([
                p["nombre"], rol, f"{p['alertas_abiertas']} / {p['total_alertas']}",
                ui.fecha_hora(p["proxima_cita"]) if p["proxima_cita"] else "Sin cita",
                lambda f, i=p["id_usuario"]: ui.boton(
                    f, "Ver historial", lambda: self._abrir_historial(i),
                    color="#E3B8F7", texto_color=ui.INK, ancho=110, alto=26,
                    size=12, corner_radius=13),
            ], fondo)

    def _abrir_historial(self, id_usuario):
        HistorialPacienteWindow(self, self.controller, id_usuario)

    def _abrir_notas(self, id_alerta):
        alerta = self.alertas.get(id_alerta)
        if alerta:
            NotasWindow(self, self.controller, alerta,
                        al_guardar=self._cargar_alertas,
                        ver_expediente=lambda: self._abrir_expediente(id_alerta))

    def cerrar_sesion(self):
        ui.volver_a_login(self)

    def cerrar_aplicacion(self):
        self.parent.destroy()


class ExpedienteWindow(ui.Modal):
    def __init__(self, parent, controller, alerta, on_agendar):
        super().__init__(parent, f"Expediente Emocional - {alerta.nombre_profesional}", 780, 640)
        try:
            exp = controller.consultar_expediente_confidencial(alerta.id_usuario)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=parent)
            self.after(10, self.destroy)
            return

        card = ui.tarjeta(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ui.titulo_tarjeta(card, f"Expediente Emocional - {exp['medico']['nombre']}", size=16)

        motivo = ctk.CTkFrame(card, fg_color=ui.ROW_PINK, corner_radius=12)
        motivo.pack(fill="x", padx=22, pady=(0, 14))
        ui.etiqueta(motivo, f"Alerta {alerta.id_alerta:05d} · {texto_tipo(alerta.tipo)}",
                    size=12, anchor="w").pack(fill="x", padx=14, pady=(10, 0))
        ui.etiqueta(motivo, alerta.motivo, size=12, weight="normal", anchor="w",
                    justify="left", wraplength=640).pack(fill="x", padx=14, pady=(0, 10))

        if alerta.estado == "PENDIENTE":
            ui.etiqueta(card, "La alerta pasará a «En Atención» al confirmar la fecha de una cita.",
                        size=11, weight="normal", color=ui.MUTED, anchor="w").pack(
                fill="x", padx=24, pady=(0, 8))

        ui.etiqueta(card, "HISTORIAL ESTRÉS (7 DÍAS)", size=13, anchor="w").pack(
            fill="x", padx=24, pady=(0, 4))
        # historial_emocional viene del más reciente al más antiguo
        ultimos = list(reversed(exp["historial_emocional"][:7]))
        datos = []
        for r in ultimos:
            dt = ui.parse_dt(r["fecha_registro"])
            etiqueta_x = dt.strftime("%d/%m") if dt else "—"
            datos.append((etiqueta_x, r["nivel_estres"]))
        grafica = ui.GraficaEstres(card, datos, bg=ui.CARD, alto=230)
        grafica.pack(fill="x", padx=22, pady=(0, 8))

        diag = self._diagnostico(exp)
        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=24, pady=(4, 0))
        ui.etiqueta(fila, "Diagnóstico Algoritmo: ", size=13).pack(side="left", anchor="n")
        ui.etiqueta(fila, diag, size=13, weight="normal", justify="left",
                    wraplength=520, anchor="w").pack(side="left", anchor="n")

        pie = ctk.CTkFrame(card, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=22, pady=18)
        ui.boton(pie, "Agendar cita de cuidado", lambda: on_agendar(alerta),
                 color=ui.PURPLE, alto=42, ancho=220).pack(side="left")
        ui.boton(pie, "Cerrar", self.destroy, color=ui.GRAY, texto_color=ui.INK,
                 alto=42, ancho=110).pack(side="right")

    @staticmethod
    def _diagnostico(exp) -> str:
        jornadas = exp["historial_jornadas"][:7]
        horas_extra = sum((j["horas_extra"] or 0.0) for j in jornadas)
        niveles = [r["nivel_estres"] for r in exp["historial_emocional"][:7]]
        promedio = sum(niveles) / len(niveles) if niveles else 0.0
        riesgo = ("ALTO" if horas_extra > BurnoutEngine.UMBRAL_HORAS_EXTRA_SEMANAL
                  or promedio >= BurnoutEngine.UMBRAL_ESTRES_ALTO
                  else "MODERADO" if promedio >= 5 else "BAJO")
        return (f"{horas_extra:.1f} horas extra acumuladas (últimos 7 turnos) + "
                f"estrés promedio {promedio:.1f}/10. Riesgo {riesgo}.")


class NotasWindow(ui.Modal):
    def __init__(self, parent, controller, alerta, al_guardar, ver_expediente):
        super().__init__(parent, f"Notas de Seguimiento - Alerta {alerta.id_alerta:05d}", 620, 640)
        self.controller = controller
        self.alerta = alerta
        self.al_guardar = al_guardar

        card = ui.tarjeta(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ui.titulo_tarjeta(card, "NOTAS DE SEGUIMIENTO", size=15)
        ui.etiqueta(card, f"{alerta.nombre_profesional} · {texto_tipo(alerta.tipo)}",
                    size=12, weight="normal", color=ui.MUTED, anchor="w").pack(
            fill="x", padx=24, pady=(0, 8))

        ui.etiqueta(card, "Bitácora anterior", size=13, anchor="w").pack(fill="x", padx=24)
        lista = ctk.CTkScrollableFrame(card, fg_color="#EFF1F4", corner_radius=10, height=150)
        lista.pack(fill="x", padx=22, pady=(4, 12))
        notas = controller.consultar_notas(alerta.id_alerta)
        if not notas:
            ui.etiqueta(lista, "Aún no hay notas para esta alerta.", size=12,
                        weight="normal", color=ui.MUTED).pack(pady=14)
        for n in notas:
            ui.etiqueta(lista, ui.fecha_hora(n["fecha_registro"]), size=11,
                        color=ui.MUTED, anchor="w").pack(fill="x", padx=10, pady=(8, 0))
            ui.etiqueta(lista, n["observacion"], size=12, weight="normal", anchor="w",
                        justify="left", wraplength=500).pack(fill="x", padx=10)

        ui.etiqueta(card, "Nueva nota*", size=13, anchor="w").pack(fill="x", padx=24)
        self.txt = ui.caja_texto(card, alto=80)
        self.txt.pack(fill="x", padx=22, pady=(4, 10))

        ui.etiqueta(card, "Estado de la alerta", size=13, anchor="w").pack(fill="x", padx=24)
        self.combo = ui.desplegable(card, ["En Atención", "Cerrada"])
        self.combo.set("En Atención" if alerta.estado != "CERRADA" else "Cerrada")
        self.combo.pack(fill="x", padx=22, pady=(4, 10))

        pie = ctk.CTkFrame(card, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=22, pady=16)
        ui.boton(pie, "Guardar nota", self._guardar, color=ui.PURPLE,
                 alto=42, ancho=150).pack(side="left")
        ui.boton(pie, "Ver expediente", lambda: (self.destroy(), ver_expediente()),
                 color=ui.LAVENDER, texto_color=ui.INK, alto=42, ancho=150).pack(
            side="left", padx=10)
        ui.boton(pie, "Cerrar", self.destroy, color=ui.GRAY, texto_color=ui.INK,
                 alto=42, ancho=90).pack(side="right")

    def _guardar(self):
        nota = self.txt.get("1.0", "end-1c").strip()
        estado = "CERRADA" if self.combo.get() == "Cerrada" else "EN_ATENCION"
        if not nota and estado == self.alerta.estado:
            messagebox.showwarning("Atención", "Escriba una nota o cambie el estado.", parent=self)
            return
        try:
            self.controller.actualizar_estado_alerta(self.alerta.id_alerta, estado, nota)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo("Guardado", "Seguimiento registrado correctamente.", parent=self)
        self.destroy()
        self.al_guardar()


class CitaWindow(ui.Modal):
    def __init__(self, parent, controller, alerta, al_agendar=None):
        super().__init__(parent, "Agendar Cita de Cuidado", 560, 560)
        self.controller = controller
        self.alerta = alerta
        self.al_agendar = al_agendar

        card = ui.tarjeta(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ui.titulo_tarjeta(card, "AGENDAR CITA DE CUIDADO", size=15)
        ui.etiqueta(card, f"Profesional: {alerta.nombre_profesional}", size=12,
                    weight="normal", color=ui.MUTED, anchor="w").pack(fill="x", padx=24, pady=(0, 10))

        manana = datetime.now() + timedelta(days=1)

        ui.etiqueta(card, "Fecha Propuesta*", size=13, anchor="w").pack(fill="x", padx=24)
        f_fecha = ctk.CTkFrame(card, fg_color="transparent")
        f_fecha.pack(fill="x", padx=22, pady=(4, 12))
        f_fecha.grid_columnconfigure(0, weight=2, uniform="d")
        f_fecha.grid_columnconfigure(1, weight=4, uniform="d")
        f_fecha.grid_columnconfigure(2, weight=3, uniform="d")
        self.cb_dia = ui.desplegable(f_fecha, [f"{d:02d}" for d in range(1, 32)])
        self.cb_dia.set(f"{manana.day:02d}")
        self.cb_dia.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cb_mes = ui.desplegable(f_fecha, ui.MESES)
        self.cb_mes.set(ui.MESES[manana.month - 1])
        self.cb_mes.grid(row=0, column=1, sticky="ew", padx=6)
        anios = [str(manana.year), str(manana.year + 1)]
        self.cb_anio = ui.desplegable(f_fecha, sorted(set(anios)))
        self.cb_anio.set(str(manana.year))
        self.cb_anio.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        ui.etiqueta(card, "Horario Sugerido*", size=13, anchor="w").pack(fill="x", padx=24)
        f_hora = ctk.CTkFrame(card, fg_color="transparent")
        f_hora.pack(fill="x", padx=22, pady=(4, 12))
        f_hora.grid_columnconfigure((0, 1), weight=1, uniform="h")
        self.cb_hora = ui.desplegable(f_hora, [f"{h:02d}" for h in range(7, 21)])
        self.cb_hora.set("11")
        self.cb_hora.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cb_min = ui.desplegable(f_hora, ["00", "15", "30", "45"])
        self.cb_min.set("00")
        self.cb_min.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ui.etiqueta(card, "Notas de Seguimiento", size=13, anchor="w").pack(fill="x", padx=24)
        self.txt = ui.caja_texto(card, alto=90)
        self.txt.pack(fill="x", padx=22, pady=(4, 14))

        ui.boton(card, "Confirmar Agendamiento", self._confirmar, color=ui.PURPLE,
                 alto=46, size=14).pack(fill="x", padx=50, pady=(4, 8))
        ui.boton(card, "Cancelar", self.destroy, color=ui.GRAY, texto_color=ui.INK,
                 alto=36).pack(padx=50)

    def _confirmar(self):
        try:
            mes = ui.MESES.index(self.cb_mes.get()) + 1
            fecha = datetime(int(self.cb_anio.get()), mes, int(self.cb_dia.get()),
                             int(self.cb_hora.get()), int(self.cb_min.get()))
        except ValueError:
            messagebox.showerror("Fecha inválida",
                                 "La fecha elegida no existe (revise día y mes).", parent=self)
            return
        try:
            self.controller.agendar_cita(
                self.alerta.id_usuario, fecha.strftime("%Y-%m-%d %H:%M:%S"),
                self.txt.get("1.0", "end-1c"), id_alerta=self.alerta.id_alerta)
        except ValueError as e:
            messagebox.showerror("No se pudo agendar", str(e), parent=self)
            return
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo(
            "Cita programada",
            f"Cita programada para {fecha:%d/%m/%Y a las %H:%M} y notificación enviada al profesional.",
            parent=self)
        self.destroy()
        if self.al_agendar:
            self.al_agendar()


class HistorialPacienteWindow(ui.Modal):
    def __init__(self, parent, controller, id_usuario):
        super().__init__(parent, "Historial del Paciente", 820, 700)
        try:
            h = controller.consultar_historial_paciente(id_usuario)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=parent)
            self.after(10, self.destroy)
            return

        rol = "Enfermería" if h["medico"].get("rol") == "ENFERMERO" else "Médico"
        card = ui.tarjeta(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ui.titulo_tarjeta(card, f"Historial - {h['medico']['nombre']} ({rol})", size=16)

        pie = ctk.CTkFrame(card, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=22, pady=14)
        ui.boton(pie, "Cerrar", self.destroy, color=ui.GRAY, texto_color=ui.INK,
                 alto=40, ancho=110).pack(side="right")

        cuerpo = ctk.CTkScrollableFrame(card, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        self._seccion(cuerpo, "ESTRÉS RECIENTE")
        ultimos = list(reversed(h["historial_emocional"][:10]))
        if ultimos:
            datos = []
            for r in ultimos:
                dt = ui.parse_dt(r["fecha_registro"])
                datos.append((dt.strftime("%d/%m") if dt else "—", r["nivel_estres"]))
            ui.GraficaEstres(cuerpo, datos, bg=ui.CARD, alto=200).pack(fill="x", padx=10)
        else:
            self._vacio(cuerpo, "Sin evaluaciones emocionales.")

        self._seccion(cuerpo, "ALERTAS")
        for a in h["alertas"]:
            nombre_est = ESTADOS.get(a["estado"], (a["estado"],))[0]
            self._item(cuerpo, f"{ui.fecha_hora(a['fecha_generacion'])} · "
                       f"{texto_tipo(a['tipo'])} · {nombre_est}", a["motivo"])
        if not h["alertas"]:
            self._vacio(cuerpo, "Sin alertas registradas.")

        self._seccion(cuerpo, "CITAS DE CUIDADO")
        for c in h["citas"]:
            self._item(cuerpo, f"{ui.fecha_hora(c['fecha_hora'])} · {c['estado'].capitalize()}"
                       f" · {c['psicologo']}", c["notas"])
        if not h["citas"]:
            self._vacio(cuerpo, "Sin citas agendadas.")

        self._seccion(cuerpo, "NOTAS DE SEGUIMIENTO")
        for n in h["notas"]:
            self._item(cuerpo, f"{ui.fecha_hora(n['fecha_registro'])} · Alerta "
                       f"{n['id_alerta']:05d} · {n['psicologo']}", n["observacion"])
        if not h["notas"]:
            self._vacio(cuerpo, "Sin notas de seguimiento.")

        self._seccion(cuerpo, "JORNADAS (ÚLTIMAS 10)")
        for j in h["historial_jornadas"][:10]:
            self._item(cuerpo, ui.fecha_hora(j["fecha"]).split(" - ")[0],
                       f"{(j['horas_trabajadas'] or 0):.1f} h trabajadas · "
                       f"{(j['horas_extra'] or 0):.1f} h extra")
        if not h["historial_jornadas"]:
            self._vacio(cuerpo, "Sin jornadas registradas.")

    @staticmethod
    def _seccion(parent, texto):
        ui.etiqueta(parent, texto, size=13, anchor="w").pack(fill="x", padx=12, pady=(14, 4))

    @staticmethod
    def _vacio(parent, texto):
        ui.etiqueta(parent, texto, size=12, weight="normal", color=ui.MUTED,
                    anchor="w").pack(fill="x", padx=12)

    @staticmethod
    def _item(parent, titulo, detalle=""):
        f = ctk.CTkFrame(parent, fg_color=ui.ROW_PINK, corner_radius=10)
        f.pack(fill="x", padx=10, pady=3)
        ui.etiqueta(f, titulo, size=12, anchor="w").pack(fill="x", padx=12, pady=(8, 0 if detalle else 8))
        if detalle:
            ui.etiqueta(f, detalle, size=12, weight="normal", anchor="w", justify="left",
                        wraplength=680).pack(fill="x", padx=12, pady=(0, 8))
