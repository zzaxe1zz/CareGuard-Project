import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

import customtkinter as ctk

from controllers.medical_controller import MedicalController
from models.dto import SessionDTO
from views import ui_kit as ui

FMT = "%Y-%m-%d %H:%M:%S"
ANIMOS = [("Muy Estresado", "Muy\nestresado"), ("Agotado", "Agotado"),
          ("Estable", "Estable"), ("Excelente", "Excelente")]


def nombre_turno(dt: datetime) -> str:
    if 7 <= dt.hour < 15:
        return "Matutino (07:00 - 15:00)"
    if 15 <= dt.hour < 23:
        return "Vespertino (15:00 - 23:00)"
    return "Nocturno (23:00 - 07:00)"


class MedicalView(ctk.CTkToplevel):
    def __init__(self, parent, session: SessionDTO):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.controller = MedicalController(session)

        self.id_jornada_activa = None
        self.entrada_dt = None
        self.receso_inicio = None
        self.salida_solicitada = False
        self.animo_sel = None
        self._tick_id = None

        ui.configurar_ventana(self, "CareGuard - Estación de Trabajo Médica", 1180, 740)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        rol = "Enfermería" if session.rol == "ENFERMERO" else "Médico"
        self.shell = ui.Shell(self, session, rol, self.cerrar_sesion)
        self.shell.agregar_pagina("Jornada laboral", self._pagina_jornada)
        self.shell.agregar_pagina("Mi historial", self._pagina_historial,
                                  on_show=self._cargar_historial)
        self.shell.iniciar()

        self._recuperar_jornada()
        self._refrescar_estado()
        self._tick()
        self.after(600, self._mostrar_notificaciones)

    def _pagina_jornada(self, parent):
        parent.grid_columnconfigure((0, 1), weight=1, uniform="cols")
        parent.grid_rowconfigure(0, weight=1)
        izq = ui.tarjeta(parent)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        der = ui.tarjeta(parent)
        der.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._panel_control(izq)
        self._panel_evaluacion(der)

    def _panel_control(self, card):
        ui.titulo_tarjeta(card, "CONTROL DE JORNADA LABORAL")

        banda = ctk.CTkFrame(card, fg_color=ui.BLUE_SOFT, corner_radius=14)
        banda.pack(fill="x", padx=22, pady=(0, 18))
        izq = ctk.CTkFrame(banda, fg_color="transparent")
        izq.pack(side="left", padx=18, pady=14)
        ui.etiqueta(izq, "Turno Activo", size=12, weight="normal",
                    anchor="w").pack(anchor="w")
        self.lbl_turno = ui.etiqueta(izq, "Sin turno iniciado", size=16, anchor="w")
        self.lbl_turno.pack(anchor="w")
        self.lbl_crono = ui.etiqueta(izq, "Tiempo en turno: 00:00:00", size=12,
                                     weight="normal", color="#1E3A8A", anchor="w")
        self.lbl_crono.pack(anchor="w", pady=(2, 0))
        self.chip = ui.pill(banda, "SIN INICIAR", ui.GRAY, ancho=150, alto=28, size=12)
        self.chip.pack(side="right", padx=18)

        fila1 = ctk.CTkFrame(card, fg_color="transparent")
        fila1.pack(fill="x", padx=22)
        fila1.grid_columnconfigure((0, 1), weight=1, uniform="b")
        self.btn_entrada = ui.boton(fila1, "Entrada", self._registrar_entrada,
                                    color=ui.MINT, texto_color=ui.INK, alto=50, size=14)
        self.btn_entrada.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.btn_salida = ui.boton(fila1, "Salida", self._solicitar_salida,
                                   color=ui.PINK, texto_color=ui.INK, alto=50, size=14)
        self.btn_salida.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ui.etiqueta(card, "Registro de pausas activas", size=12, weight="normal",
                    anchor="w").pack(fill="x", padx=24, pady=(20, 6))
        fila2 = ctk.CTkFrame(card, fg_color="transparent")
        fila2.pack(fill="x", padx=22)
        fila2.grid_columnconfigure((0, 1), weight=1, uniform="b")
        self.btn_receso = ui.boton(fila2, "Receso", self._iniciar_receso,
                                   color=ui.YELLOW, texto_color=ui.INK, alto=50, size=14)
        self.btn_receso.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.btn_fin_receso = ui.boton(fila2, "Fin Receso", self._finalizar_receso,
                                       color=ui.GRAY, texto_color=ui.INK, alto=50, size=14)
        self.btn_fin_receso.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ui.boton(card, "Solicitar Apoyo Voluntario (Confidencial)", self._solicitar_apoyo,
                 color=ui.LAVENDER, texto_color=ui.INK, alto=46, size=13).pack(
            fill="x", padx=22, pady=(24, 10))

        self.lbl_msg = ui.etiqueta(card, "", size=12, weight="normal", color=ui.MUTED,
                                   anchor="w", justify="left", wraplength=420)
        self.lbl_msg.pack(fill="x", padx=24, pady=(4, 12))

    def _panel_evaluacion(self, card):
        ui.titulo_tarjeta(card, "EVALUACIÓN EMOCIONAL · CIERRE")

        ui.etiqueta(card, "Estado de Ánimo Hoy", size=14, anchor="w").pack(
            fill="x", padx=24, pady=(0, 6))
        caras = ctk.CTkFrame(card, fg_color="transparent")
        caras.pack(fill="x", padx=22)
        caras.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="f")
        self.caras = {}
        for i, (clave, texto) in enumerate(ANIMOS):
            col = ctk.CTkFrame(caras, fg_color="transparent")
            col.grid(row=0, column=i)
            cara = ui.Cara(col, clave, tam=58, bg=ui.CARD, comando=self._elegir_animo)
            cara.pack()
            ui.etiqueta(col, texto, size=11, weight="normal", color=ui.MUTED,
                        justify="center").pack(pady=(2, 0))
            self.caras[clave] = cara

        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=24, pady=(18, 0))
        ui.etiqueta(fila, "Nivel de Estrés", size=14).pack(side="left")
        self.lbl_valor_estres = ui.etiqueta(fila, "", size=13, color=ui.ORANGE)
        self.lbl_valor_estres.pack(side="right")

        self.slider_estres = ctk.CTkSlider(
            card, from_=1, to=10, number_of_steps=9, command=self._actualizar_estres,
            progress_color=ui.ORANGE, button_color=ui.ORANGE,
            button_hover_color="#D98305", fg_color="#3F4650", height=18)
        self.slider_estres.set(5)
        self.slider_estres.pack(fill="x", padx=24, pady=(8, 0))
        escala = ctk.CTkFrame(card, fg_color="transparent")
        escala.pack(fill="x", padx=24)
        ui.etiqueta(escala, "1 · Bajo", size=11, weight="normal",
                    color=ui.MUTED).pack(side="left")
        ui.etiqueta(escala, "10 · Alto", size=11, weight="normal",
                    color=ui.MUTED).pack(side="right")

        ui.etiqueta(card, "Notas Personales (Opcional)", size=14, anchor="w").pack(
            fill="x", padx=24, pady=(14, 6))
        self.txt_notas = ui.caja_texto(card, alto=84)
        self.txt_notas.pack(fill="x", padx=22)

        self.btn_guardar = ui.boton(card, "Guardar Registro de Turno",
                                    self._guardar_registro, color=ui.RED,
                                    alto=46, size=14)
        self.btn_guardar.pack(fill="x", padx=60, pady=(18, 8))
        self.lbl_bloqueo = ui.etiqueta(
            card, "Presione «Salida» para habilitar la evaluación de cierre.",
            size=12, weight="normal", color=ui.MUTED)
        self.lbl_bloqueo.pack(pady=(0, 12))
        self._actualizar_estres(5)

    def _refrescar_estado(self):
        activa = self.id_jornada_activa is not None
        en_receso = self.receso_inicio is not None
        cerrando = self.salida_solicitada

        if not activa:
            texto, fondo = "SIN INICIAR", ui.GRAY
            self.lbl_turno.configure(text="Sin turno iniciado")
        elif cerrando:
            texto, fondo = "CIERRE DE TURNO", ui.PINK
        elif en_receso:
            texto, fondo = "EN RECESO", ui.YELLOW
        else:
            texto, fondo = "EN PROGRESO", ui.MINT
        self.chip.configure(text=texto, fg_color=fondo)

        if activa and self.entrada_dt:
            self.lbl_turno.configure(text=nombre_turno(self.entrada_dt))

        ui.activar_boton(self.btn_entrada, not activa)
        ui.activar_boton(self.btn_salida, activa and not en_receso and not cerrando)
        ui.activar_boton(self.btn_receso, activa and not en_receso and not cerrando)
        ui.activar_boton(self.btn_fin_receso, activa and en_receso)
        self._bloquear_evaluacion(not cerrando)

    def _bloquear_evaluacion(self, bloqueada: bool):
        estado = "disabled" if bloqueada else "normal"
        self.slider_estres.configure(state=estado)
        self.txt_notas.configure(state=estado)
        ui.activar_boton(self.btn_guardar, not bloqueada)
        for cara in self.caras.values():
            cara.habilitar(not bloqueada)
        if bloqueada:
            self.lbl_bloqueo.pack(pady=(0, 12))
        else:
            self.lbl_bloqueo.pack_forget()

    def _msg(self, texto):
        self.lbl_msg.configure(text=texto)

    def _tick(self):
        try:
            if self.entrada_dt is not None and self.id_jornada_activa is not None:
                seg = int((datetime.now() - self.entrada_dt).total_seconds())
                h, r = divmod(max(seg, 0), 3600)
                m, s = divmod(r, 60)
                self.lbl_crono.configure(text=f"Tiempo en turno: {h:02d}:{m:02d}:{s:02d}")
            else:
                self.lbl_crono.configure(text="Tiempo en turno: 00:00:00")
            self._tick_id = self.after(1000, self._tick)
        except tk.TclError:
            pass

    def destroy(self):
        if self._tick_id is not None:
            try:
                self.after_cancel(self._tick_id)
            except Exception:
                pass
            self._tick_id = None
        super().destroy()

    def _recuperar_jornada(self):
        """Retoma un turno abierto; si es de hace más de 16 h lo cierra sin horas."""
        olvidada = self.controller.cerrar_jornada_olvidada()
        if olvidada:
            self._msg(f"Se cerró automáticamente un turno anterior sin salida "
                      f"({ui.fecha_hora(olvidada)}), sin horas registradas.")
        abierta = self.controller.obtener_jornada_abierta()
        if abierta:
            self.id_jornada_activa = abierta["id_jornada"]
            self.entrada_dt = ui.parse_dt(abierta["hora_entrada"]) or datetime.now()
            self._msg(f"Se retomó su turno iniciado a las {self.entrada_dt:%H:%M}.")

    def _mostrar_notificaciones(self):
        try:
            for n in self.controller.obtener_notificaciones_pendientes():
                messagebox.showinfo("Notificación de Psicología", n["mensaje"], parent=self)
                self.controller.marcar_notificacion_leida(n["id_notificacion"])
        except tk.TclError:
            pass

    def _registrar_entrada(self):
        try:
            self.id_jornada_activa = self.controller.iniciar_jornada()
        except Exception as e:
            messagebox.showerror("No se pudo registrar la entrada", str(e), parent=self)
            return
        self.entrada_dt = datetime.now()
        self.salida_solicitada = False
        self._refrescar_estado()
        self._msg(f"Entrada registrada a las {self.entrada_dt:%H:%M}. ¡Buen turno!")

    def _iniciar_receso(self):
        self.receso_inicio = datetime.now()
        self._refrescar_estado()
        self._msg(f"Receso iniciado a las {self.receso_inicio:%H:%M}. "
                  "Presione «Fin Receso» al regresar.")

    def _finalizar_receso(self):
        inicio = self.receso_inicio.replace(microsecond=0)
        fin = datetime.now().replace(microsecond=0)
        if fin <= inicio:
            fin = inicio + timedelta(seconds=1)
        try:
            self.controller.registrar_descanso(
                self.id_jornada_activa, inicio.strftime(FMT), fin.strftime(FMT))
        except Exception as e:
            messagebox.showerror("Error al registrar el receso", str(e), parent=self)
            return
        total = int((fin - inicio).total_seconds())
        self.receso_inicio = None
        self._refrescar_estado()
        self._msg(f"Receso registrado ({total // 60} min {total % 60} s).")

    def _solicitar_salida(self):
        if not messagebox.askyesno(
                "Registrar salida",
                "¿Desea registrar su salida y cerrar el turno?\n"
                "A continuación deberá completar la evaluación emocional.", parent=self):
            return
        self.salida_solicitada = True
        self._refrescar_estado()
        self._msg("Complete la evaluación emocional y presione «Guardar Registro de Turno».")

    def _elegir_animo(self, clave):
        self.animo_sel = clave
        for k, cara in self.caras.items():
            cara.seleccionar(k == clave)

    def _actualizar_estres(self, valor):
        v = int(round(float(valor)))
        self.lbl_valor_estres.configure(
            text=f"{v} / 10 ({ui.etiqueta_estres(v)})",
            text_color=ui.color_texto_estres(v))

    def _guardar_registro(self):
        if not self.salida_solicitada or self.id_jornada_activa is None:
            return
        if not self.animo_sel:
            messagebox.showwarning("Atención", "Seleccione cómo fue su estado de ánimo hoy.",
                                   parent=self)
            return
        try:
            res = self.controller.finalizar_jornada_y_evaluar(
                self.id_jornada_activa, int(round(self.slider_estres.get())),
                self.animo_sel, self.txt_notas.get("1.0", "end-1c"))
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e), parent=self)
            return

        j = res["resumen_jornada"]
        msg = (f"Turno cerrado.\nHoras trabajadas: {j['horas_trabajadas']}\n"
               f"Horas extra: {j['horas_extra']}")
        if res["alerta_generada"]:
            msg += ("\n\nSe emitió una alerta automática de sobrecarga preventiva "
                    "hacia Psicología.")
        messagebox.showinfo("Registro exitoso", msg, parent=self)

        self.id_jornada_activa = None
        self.entrada_dt = None
        self.receso_inicio = None
        self.salida_solicitada = False
        self.animo_sel = None
        for cara in self.caras.values():
            cara.seleccionar(False)
        self.slider_estres.set(5)
        self._actualizar_estres(5)
        self._bloquear_evaluacion(False)
        self.txt_notas.delete("1.0", "end")
        self._refrescar_estado()
        self._msg("Registro guardado. Puede consultar su historial en «Mi historial».")

    def _solicitar_apoyo(self):
        ApoyoWindow(self, self._enviar_apoyo)

    def _enviar_apoyo(self, comentario: str, ventana) -> None:
        try:
            self.controller.solicitar_apoyo_psicologico(
                comentario or "Solicitud voluntaria desde panel médico.")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=ventana)
            return
        ventana.destroy()
        messagebox.showinfo("Confirmación",
                            "Su solicitud ha sido enviada confidencialmente a Psicología.",
                            parent=self)

    def _pagina_historial(self, parent):
        card = ui.tarjeta(parent)
        card.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=22, pady=(18, 4))
        ui.etiqueta(cab, f"Mi Historial Personal - {self.session.nombre}", size=17).pack(side="left")
        ui.boton(cab, "Actualizar", self._cargar_historial, color=ui.GRAY,
                 texto_color=ui.INK, alto=32, ancho=100, size=12).pack(side="right")
        ctk.CTkFrame(card, height=1, fg_color=ui.CARD_BORDER).pack(
            fill="x", padx=22, pady=(8, 14))

        kpis = ctk.CTkFrame(card, fg_color="transparent")
        kpis.pack(fill="x", padx=22)
        kpis.grid_columnconfigure((0, 1, 2), weight=1, uniform="k")
        self.kpi_horas = ui.tarjeta_kpi(kpis, "Horas trabajadas (semana)", "—")
        self.kpi_estres = ui.tarjeta_kpi(kpis, "Promedio estrés", "—")
        self.kpi_pausas = ui.tarjeta_kpi(kpis, "Pausas completadas", "—")
        for i, k in enumerate((self.kpi_horas, self.kpi_estres, self.kpi_pausas)):
            k.grid(row=0, column=i, sticky="ew", padx=6)

        self.tabla = ui.Tabla(card, [
            ("Fecha", 1.3, "center"), ("Entrada / Salida", 1.6, "center"),
            ("Horas Extra", 1, "center"), ("Ánimo", 0.9, "center"),
            ("Estrés", 1, "center")], vacio="Aún no hay jornadas en los últimos 7 días.")
        self.tabla.pack(fill="both", expand=True, padx=22, pady=(18, 18))

    def _cargar_historial(self):
        try:
            r = self.controller.consultar_resumen_semanal()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial.\n{e}", parent=self)
            return
        self.kpi_horas.lbl_valor.configure(text=f"{r['horas_semana']:g} hrs")
        prom = r["promedio_estres"]
        self.kpi_estres.lbl_valor.configure(
            text="—" if prom is None else f"{prom:g} / 10")
        self.kpi_pausas.lbl_valor.configure(text=f"{r['pausas']} recesos")

        self.tabla.limpiar()
        if not r["filas"]:
            self.tabla.mostrar_vacio()
            return
        for f in r["filas"]:
            estres = f["nivel_estres"]
            if estres is None:
                fondo = ui.ROW_MINT
            elif estres >= 8:
                fondo = ui.ROW_PINK
            elif estres >= 5:
                fondo = ui.ROW_AMBER
            else:
                fondo = ui.ROW_MINT
            salida = ui.hora(f["hora_salida"]) if f["hora_salida"] else "En curso"
            extra = f["horas_extra"] or 0
            animo = f["estado_animo"]
            celda_animo = (
                (lambda p, a=animo, c=fondo: ui.Cara(p, a, tam=30, bg=c))
                if animo else "—")
            celda_estres = (
                (lambda p, e=estres: ui.pill(p, f"{e}/10", ui.color_estres(e),
                                             ancho=70, alto=24))
                if estres is not None else "—")
            self.tabla.agregar_fila(
                [ui.fecha_larga(f["fecha"]),
                 f"{ui.hora(f['hora_entrada'])} - {salida}",
                 f"+{extra:g} h", celda_animo, celda_estres], fondo)

    def cerrar_sesion(self):
        ui.volver_a_login(self)

    def cerrar_aplicacion(self):
        self.parent.destroy()


class ApoyoWindow(ui.Modal):
    MAX_CARACTERES = 500

    def __init__(self, parent, al_enviar):
        super().__init__(parent, "Apoyo Voluntario", 520, 430)
        self.al_enviar = al_enviar

        card = ui.tarjeta(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ui.titulo_tarjeta(card, "SOLICITAR APOYO VOLUNTARIO", size=15)
        ui.etiqueta(card, "Se enviará una solicitud confidencial al área de Psicología.",
                    size=12, weight="normal", color=ui.MUTED, anchor="w").pack(
            fill="x", padx=24, pady=(0, 10))

        ui.etiqueta(card, "Comentario (opcional)", size=13, anchor="w").pack(fill="x", padx=24)
        self.txt = ui.caja_texto(card, alto=140)
        self.txt.pack(fill="x", padx=22, pady=(4, 4))
        self.lbl_cont = ui.etiqueta(card, f"0 / {self.MAX_CARACTERES}", size=11,
                                    weight="normal", color=ui.MUTED, anchor="e")
        self.lbl_cont.pack(fill="x", padx=24, pady=(0, 10))
        self.txt.bind("<KeyRelease>", lambda _e: self._contar())

        ui.boton(card, "Enviar solicitud", self._enviar, color=ui.PURPLE,
                 alto=44, size=14).pack(fill="x", padx=50, pady=(4, 8))
        ui.boton(card, "Cancelar", self.destroy, color=ui.GRAY, texto_color=ui.INK,
                 alto=36).pack(padx=50)

    def _contar(self):
        texto = self.txt.get("1.0", "end-1c")
        if len(texto) > self.MAX_CARACTERES:
            self.txt.delete("1.0", "end")
            self.txt.insert("1.0", texto[:self.MAX_CARACTERES])
            texto = texto[:self.MAX_CARACTERES]
        self.lbl_cont.configure(text=f"{len(texto)} / {self.MAX_CARACTERES}")

    def _enviar(self):
        self.al_enviar(self.txt.get("1.0", "end-1c").strip(), self)
