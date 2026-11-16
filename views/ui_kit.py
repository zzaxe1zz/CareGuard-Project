import math
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

BG = "#E9EEF1"
CARD = "#F8F8F9"
CARD_BORDER = "#D3D6DB"
WHITE = "#FFFFFF"
INK = "#14171C"
MUTED = "#5B6470"
INPUT = "#E1DFE0"
INPUT_BORDER = "#B5B3B5"

BLUE = "#0B4DB0"
BLUE_HOVER = "#093F91"
BLUE_SOFT = "#BFD7FB"
MINT = "#CFF7E1"
MINT_HOVER = "#B5EDCE"
PINK = "#FDE2EC"
PINK_HOVER = "#FBC9DC"
YELLOW = "#FFF08A"
YELLOW_HOVER = "#FFE55C"
GRAY = "#DAD8D9"
GRAY_HOVER = "#C8C6C7"
LAVENDER = "#D5CBFB"
LAVENDER_HOVER = "#C1B3F8"
RED = "#B8304A"
RED_HOVER = "#9C2640"
PURPLE = "#6A1FB0"
PURPLE_HOVER = "#571894"
GOLD = "#B8780F"
GOLD_HOVER = "#9A6409"
BLACK = "#0D0D0D"
BLACK_HOVER = "#2A2A2A"
ORANGE = "#F59E0B"

ROW_MINT = "#D3F8E4"
ROW_AMBER = "#FFF1BF"
ROW_PINK = "#FFD6E0"
HEADER_LAV = "#F0E4FD"

FONT = "Segoe UI"

_HOVER = {
    BLUE: BLUE_HOVER, MINT: MINT_HOVER, PINK: PINK_HOVER, YELLOW: YELLOW_HOVER,
    GRAY: GRAY_HOVER, LAVENDER: LAVENDER_HOVER, RED: RED_HOVER,
    PURPLE: PURPLE_HOVER, GOLD: GOLD_HOVER, BLACK: BLACK_HOVER,
}


def font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT, size=size, weight=weight)


MESES_CORTOS = ["ene", "feb", "mar", "abr", "may", "jun",
                "jul", "ago", "sep", "oct", "nov", "dic"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def parse_dt(valor):
    if not valor:
        return None
    texto = str(valor).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    return None


def fecha_larga(valor) -> str:
    dt = parse_dt(valor)
    if not dt:
        return str(valor or "—")
    return f"{dt.day:02d}/{MESES_CORTOS[dt.month - 1].capitalize()}/{dt.year}"


def fecha_hora(valor) -> str:
    dt = parse_dt(valor)
    if not dt:
        return str(valor or "—")
    return dt.strftime("%d/%m/%Y - %H:%M")


def hora(valor) -> str:
    dt = parse_dt(valor)
    return dt.strftime("%H:%M") if dt else "—"


def color_estres(v: float) -> str:
    if v <= 4:
        return "#4ADE80"
    if v <= 6:
        return "#FBBF24"
    if v <= 7:
        return "#FB923C"
    return "#F43F5E"


def etiqueta_estres(v: float) -> str:
    if v <= 3:
        return "Bajo"
    if v <= 6:
        return "Moderado"
    return "Alto"


def color_texto_estres(v: float) -> str:
    if v <= 3:
        return "#15803D"
    if v <= 6:
        return "#B45309"
    return "#C2410C"


def _escala(win) -> float:
    try:
        return float(win._get_window_scaling())
    except Exception:
        return 1.0


def configurar_ventana(win, titulo, ancho, alto, minimo=None, centro_en=None):
    win.title(titulo)
    try:
        win.configure(fg_color=BG)
    except Exception:
        pass
    esc = _escala(win)
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    ancho = int(min(ancho, sw / esc - 30))
    alto = int(min(alto, sh / esc - 90))
    if centro_en is not None:
        try:
            cx = centro_en.winfo_rootx() + centro_en.winfo_width() // 2
            cy = centro_en.winfo_rooty() + centro_en.winfo_height() // 2
            x = int(cx - ancho * esc / 2)
            y = int(cy - alto * esc / 2)
        except tk.TclError:
            centro_en = None
    if centro_en is None:
        x = int((sw - ancho * esc) / 2)
        y = int((sh - alto * esc) / 2 - 20)
    x, y = max(0, x), max(0, y)
    win.geometry(f"{ancho}x{alto}+{x}+{y}")
    mw, mh = minimo or (min(ancho, 940), min(alto, 600))
    win.minsize(min(mw, ancho), min(mh, alto))


class Modal(ctk.CTkToplevel):

    def __init__(self, parent, titulo, ancho, alto):
        super().__init__(parent)
        self.padre = parent
        configurar_ventana(self, titulo, ancho, alto,
                           minimo=(ancho, alto), centro_en=parent)
        self.resizable(False, False)
        try:
            self.transient(parent.winfo_toplevel())
        except tk.TclError:
            pass
        # grab_set antes de que la ventana sea visible falla en Linux/macOS
        self.after(150, self._activar)

    def _activar(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
        except tk.TclError:
            pass


def volver_a_login(ventana):
    padre = ventana.parent
    ventana.destroy()
    if hasattr(padre, "mostrar"):
        padre.mostrar()
    else:
        padre.deiconify()


def tarjeta(parent, **kw):
    base = dict(fg_color=CARD, corner_radius=16,
                border_width=1, border_color=CARD_BORDER)
    base.update(kw)
    return ctk.CTkFrame(parent, **base)


def etiqueta(parent, texto, size=13, weight="bold", color=INK, **kw):
    return ctk.CTkLabel(parent, text=texto, font=font(size, weight),
                        text_color=color, **kw)


def titulo_tarjeta(parent, texto, size=15):
    etiqueta(parent, texto, size=size, anchor="w").pack(
        fill="x", padx=22, pady=(18, 4))
    ctk.CTkFrame(parent, height=1, fg_color=CARD_BORDER).pack(
        fill="x", padx=22, pady=(4, 12))


def boton(parent, texto, comando=None, color=BLUE, texto_color="white",
          ancho=None, alto=40, size=13, **kw):
    args = dict(text=texto, command=comando, fg_color=color,
                hover_color=_HOVER.get(color, color), text_color=texto_color,
                text_color_disabled="#9AA0A8", corner_radius=10, height=alto,
                font=font(size, "bold"))
    if ancho:
        args["width"] = ancho
    args.update(kw)
    btn = ctk.CTkButton(parent, **args)
    btn._cg_color = color
    return btn


def activar_boton(btn, activo: bool):
    btn.configure(state="normal" if activo else "disabled",
                  fg_color=btn._cg_color if activo else "#E4E5E8")


def entrada(parent, placeholder="", show=None, alto=40, **kw):
    return ctk.CTkEntry(parent, placeholder_text=placeholder, show=show,
                        height=alto, corner_radius=10, fg_color=INPUT,
                        border_color=INPUT_BORDER, border_width=1,
                        text_color=INK, placeholder_text_color="#6B6F76",
                        font=font(13), **kw)


def desplegable(parent, valores, comando=None, anchor="w", alto=40, **kw):
    return ctk.CTkOptionMenu(parent, values=valores, command=comando,
                             height=alto, corner_radius=10, fg_color=INPUT,
                             button_color=INPUT, button_hover_color=GRAY_HOVER,
                             text_color=INK, dropdown_fg_color=WHITE,
                             dropdown_text_color=INK,
                             dropdown_hover_color="#E8EDF5",
                             font=font(13, "bold"), dropdown_font=font(13),
                             anchor=anchor, dynamic_resizing=False, **kw)


def caja_texto(parent, alto=90, **kw):
    return ctk.CTkTextbox(parent, height=alto, corner_radius=10, fg_color=INPUT,
                          border_color=INPUT_BORDER, border_width=1,
                          text_color=INK, font=font(13), wrap="word", **kw)


def pill(parent, texto, fondo, color_texto=INK, ancho=110, alto=24, size=12):
    return ctk.CTkLabel(parent, text=texto, fg_color=fondo,
                        text_color=color_texto, corner_radius=alto // 2,
                        width=ancho, height=alto, font=font(size, "bold"))


def tarjeta_kpi(parent, titulo, valor, color_valor=INK):
    f = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=12,
                     border_width=1, border_color=CARD_BORDER)
    etiqueta(f, titulo.upper(), size=11, weight="normal",
             color=MUTED).pack(pady=(14, 2), padx=10)
    f.lbl_valor = etiqueta(f, valor, size=22, color=color_valor)
    f.lbl_valor.pack(pady=(0, 14), padx=10)
    return f


def barra_progreso(parent, nombre, valor_texto, fraccion, color):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    fila = ctk.CTkFrame(f, fg_color="transparent")
    fila.pack(fill="x")
    etiqueta(fila, nombre, size=13, weight="normal").pack(side="left")
    etiqueta(fila, valor_texto, size=13, weight="bold").pack(side="right")
    barra = ctk.CTkProgressBar(f, height=16, corner_radius=8, fg_color="#E3E5EA",
                               progress_color=color, border_width=0)
    barra.pack(fill="x", pady=(4, 12))
    barra.set(max(0.0, min(1.0, fraccion)))
    return f


class Tabla(ctk.CTkFrame):
    """columnas = [(titulo, peso, 'w'|'center'), ...]. Las celdas pueden ser texto
    o una función que recibe la fila y devuelve un widget."""

    def __init__(self, master, columnas, header_bg="transparent",
                 vacio="Sin registros", **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.columnas = columnas
        self.vacio = vacio
        self.header = ctk.CTkFrame(self, fg_color=header_bg, corner_radius=10)
        self.header.pack(fill="x", padx=(0, 16), pady=(0, 6))
        self._columnas(self.header)
        for i, (titulo, _, anc) in enumerate(columnas):
            ctk.CTkLabel(self.header, text=titulo, font=font(13, "bold"),
                         text_color=INK, anchor=anc).grid(
                row=0, column=i, sticky="ew", padx=8, pady=9)
        self.cuerpo = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                             corner_radius=0)
        self.cuerpo.pack(fill="both", expand=True)

    def _columnas(self, frame):
        for i, (_, peso, _) in enumerate(self.columnas):
            frame.grid_columnconfigure(i, weight=int(peso * 10),
                                       uniform=f"t{id(self)}")

    def limpiar(self):
        for w in self.cuerpo.winfo_children():
            w.destroy()

    def agregar_fila(self, celdas, fondo=ROW_MINT):
        fila = ctk.CTkFrame(self.cuerpo, fg_color=fondo, corner_radius=10)
        fila.pack(fill="x", pady=3, padx=(0, 2))
        self._columnas(fila)
        for i, celda in enumerate(celdas):
            anc = self.columnas[i][2]
            if callable(celda):
                w = celda(fila)
                w.grid(row=0, column=i, padx=8, pady=7,
                       sticky="w" if anc == "w" else "")
            else:
                ctk.CTkLabel(fila, text=str(celda), font=font(13),
                             text_color=INK, anchor=anc, justify="left"
                             if anc == "w" else "center", wraplength=0).grid(
                    row=0, column=i, sticky="ew", padx=8, pady=11)
        return fila

    def mostrar_vacio(self, texto=None):
        etiqueta(self.cuerpo, texto or self.vacio, size=13, weight="normal",
                 color=MUTED).pack(pady=40)


class Cara(tk.Canvas):

    AMARILLO = "#F7D154"
    ROJO = "#E25C5C"

    def __init__(self, master, estado, tam=52, bg=CARD, comando=None):
        super().__init__(master, width=tam, height=tam, bg=bg,
                         highlightthickness=0, bd=0,
                         cursor="hand2" if comando else "")
        self.estado = estado
        self.tam = tam
        self.comando = comando
        self.seleccionada = False
        self.habilitada = True
        self._dibujar()
        if comando:
            self.bind("<Button-1>", self._click)

    def _click(self, _e):
        if self.habilitada and self.comando:
            self.comando(self.estado)

    def seleccionar(self, valor: bool):
        self.seleccionada = valor
        self._dibujar()

    def habilitar(self, valor: bool):
        self.habilitada = valor
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        s = self.tam / 100.0

        def P(*v):
            return [x * s for x in v]

        rojo = self.estado == "Muy Estresado"
        relleno = self.ROJO if rojo else self.AMARILLO
        borde = "#9E3333" if rojo else "#B58A12"
        tinta = "#4A1010" if rojo else "#4A3500"
        if not self.habilitada:
            relleno = "#E3E5E8"
            borde = "#B9BDC3"
            tinta = "#8D939B"
        if self.seleccionada:
            self.create_oval(*P(3, 3, 97, 97), outline=BLUE, width=3)
        self.create_oval(*P(11, 11, 89, 89), fill=relleno, outline=borde, width=2)

        if self.estado == "Muy Estresado":
            self.create_line(*P(27, 33, 44, 42), fill=tinta, width=max(2, 4 * s), capstyle="round")
            self.create_line(*P(73, 33, 56, 42), fill=tinta, width=max(2, 4 * s), capstyle="round")
            self.create_oval(*P(35, 46, 43, 55), fill=tinta, outline="")
            self.create_oval(*P(57, 46, 65, 55), fill=tinta, outline="")
            self.create_arc(*P(34, 62, 66, 88), start=20, extent=140,
                            style="arc", outline=tinta, width=max(2, 3 * s))
        elif self.estado == "Agotado":
            self.create_arc(*P(30, 42, 44, 56), start=0, extent=180,
                            style="arc", outline=tinta, width=max(2, 3 * s))
            self.create_arc(*P(56, 42, 70, 56), start=0, extent=180,
                            style="arc", outline=tinta, width=max(2, 3 * s))
            self.create_arc(*P(34, 62, 66, 88), start=20, extent=140,
                            style="arc", outline=tinta, width=max(2, 3 * s))
            if self.habilitada:
                self.create_oval(*P(62, 56, 70, 72), fill="#4DA3FF", outline="")
        elif self.estado == "Estable":
            self.create_oval(*P(33, 40, 41, 50), fill=tinta, outline="")
            self.create_oval(*P(59, 40, 67, 50), fill=tinta, outline="")
            self.create_line(*P(36, 66, 64, 66), fill=tinta, width=max(2, 3 * s), capstyle="round")
        else:
            self.create_oval(*P(33, 40, 41, 50), fill=tinta, outline="")
            self.create_oval(*P(59, 40, 67, 50), fill=tinta, outline="")
            self.create_arc(*P(32, 44, 68, 80), start=200, extent=140,
                            style="arc", outline=tinta, width=max(2, 3 * s))


def _puntos_estrella(cx, cy, radio):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = radio if i % 2 == 0 else radio * 0.45
        pts += [cx + r * math.cos(ang), cy + r * math.sin(ang)]
    return pts


class Estrellas(tk.Canvas):

    ACTIVA = "#FFE24A"
    VACIA = "#ECEFF1"

    def __init__(self, master, tam=40, valor=0, interactiva=True, bg=CARD,
                 comando=None, espacio=8):
        self.tam = tam
        self.espacio = espacio
        ancho = 5 * tam + 4 * espacio + 4
        super().__init__(master, width=ancho, height=tam + 4, bg=bg,
                         highlightthickness=0, bd=0,
                         cursor="hand2" if interactiva else "")
        self.valor = valor
        self.interactiva = interactiva
        self.comando = comando
        self._dibujar()
        if interactiva:
            self.bind("<Button-1>", self._click)
            self.bind("<Motion>", self._hover)
            self.bind("<Leave>", lambda _e: self._dibujar())

    def _indice(self, x):
        i = int(x // (self.tam + self.espacio)) + 1
        return max(1, min(5, i))

    def _click(self, e):
        self.set(self._indice(e.x))
        if self.comando:
            self.comando(self.valor)

    def _hover(self, e):
        self._dibujar(self._indice(e.x))

    def set(self, valor):
        self.valor = int(valor)
        self._dibujar()

    def get(self):
        return self.valor

    def _dibujar(self, hover=None):
        self.delete("all")
        activo = hover if hover else self.valor
        for i in range(5):
            cx = 2 + i * (self.tam + self.espacio) + self.tam / 2
            cy = 2 + self.tam / 2
            self.create_polygon(_puntos_estrella(cx, cy, self.tam / 2),
                                fill=self.ACTIVA if i < activo else self.VACIA,
                                outline="#2B2B2B", width=1, joinstyle="round")


def insignia_estrella(parent, tam=92, bg=CARD):
    c = tk.Canvas(parent, width=tam, height=tam, bg=bg, highlightthickness=0, bd=0)
    c.create_oval(2, 2, tam - 2, tam - 2, fill="#FFF08A", outline="")
    c.create_polygon(_puntos_estrella(tam / 2, tam / 2 + 2, tam * 0.36),
                     fill="#AA8A3C", outline="#7A6020", width=1, joinstyle="round")
    return c


def insignia_avatar(parent, tam=70, bg=CARD):
    c = tk.Canvas(parent, width=tam, height=tam, bg=bg, highlightthickness=0, bd=0)
    s = tam / 64.0
    c.create_oval(3 * s, 3 * s, 61 * s, 61 * s, fill=WHITE, outline=INK, width=3)
    c.create_oval(22 * s, 13 * s, 42 * s, 33 * s, fill=INK, outline=INK)
    c.create_arc(15 * s, 36 * s, 49 * s, 76 * s, start=0, extent=180,
                 fill=INK, outline=INK)
    c.create_oval(3 * s, 3 * s, 61 * s, 61 * s, outline=INK, width=3)
    return c


def _rect_redondo(canvas, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class GraficaEstres(tk.Canvas):

    def __init__(self, master, datos=None, bg=CARD, alto=230, umbral=7, **kw):
        super().__init__(master, height=alto, bg=bg, highlightthickness=0, bd=0, **kw)
        self.datos = datos or []
        self.umbral = umbral
        self.bind("<Configure>", lambda _e: self.dibujar())

    def actualizar(self, datos):
        self.datos = datos
        self.dibujar()

    def dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60 or h < 60:
            return
        if not self.datos:
            self.create_text(w / 2, h / 2, text="Sin registros emocionales",
                             fill=MUTED, font=(FONT, 12))
            return
        mi, ms, mf, md = 34, 22, 34, 66
        area_h = h - ms - mf
        area_w = w - mi - md
        base = ms + area_h
        for v in (0, 5, 10):
            y = ms + area_h * (1 - v / 10)
            self.create_line(mi, y, w - md + 4, y, fill="#E1E4E8")
            self.create_text(mi - 8, y, text=str(v), anchor="e",
                             fill=MUTED, font=(FONT, 9))
        yu = ms + area_h * (1 - self.umbral / 10)
        self.create_line(mi, yu, w - md + 4, yu, fill="#E11D48", dash=(4, 3))
        self.create_text(w - md + 8, yu, text=f"umbral {self.umbral}",
                         anchor="w", fill="#E11D48", font=(FONT, 9))
        n = len(self.datos)
        slot = area_w / n
        ancho = min(56, slot * 0.55)
        for i, (etiqueta_x, valor) in enumerate(self.datos):
            cx = mi + slot * (i + 0.5)
            alto_b = max(6, area_h * (valor / 10.0))
            y1 = base - alto_b
            _rect_redondo(self, cx - ancho / 2, y1, cx + ancho / 2, base,
                          min(16, ancho / 2), fill=color_estres(valor), outline="")
            self.create_text(cx, y1 - 10, text=f"{valor:g}", fill=INK,
                             font=(FONT, 10, "bold"))
            self.create_text(cx, base + 16, text=etiqueta_x, fill=MUTED,
                             font=(FONT, 9))


def _logo(parent, tam=38, bg=WHITE):
    c = tk.Canvas(parent, width=tam, height=tam, bg=bg, highlightthickness=0, bd=0)
    c.create_oval(1, 1, tam - 1, tam - 1, fill=BLUE, outline="")
    m, g = tam / 2, tam * 0.11
    c.create_rectangle(m - g, tam * 0.24, m + g, tam * 0.76, fill="white", outline="")
    c.create_rectangle(tam * 0.24, m - g, tam * 0.76, m + g, fill="white", outline="")
    return c


class Shell(ctk.CTkFrame):

    def __init__(self, master, session, rol_texto, on_logout):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.pack(fill="both", expand=True)
        self.paginas = {}
        self.nav = None

        barra = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=66)
        barra.pack(fill="x")
        barra.pack_propagate(False)
        ctk.CTkFrame(self, height=1, fg_color=CARD_BORDER,
                     corner_radius=0).pack(fill="x")
        self.barra = barra

        marca = ctk.CTkFrame(barra, fg_color="transparent")
        marca.pack(side="left", padx=(22, 0))
        _logo(marca).pack(side="left")
        etiqueta(marca, "CareGuard", size=18, color=BLUE).pack(side="left", padx=(10, 0))

        der = ctk.CTkFrame(barra, fg_color="transparent")
        der.pack(side="right", padx=(0, 22))
        boton(der, "Cerrar sesión", on_logout, color="#FFFFFF", texto_color=RED,
              alto=36, ancho=120, border_width=1, border_color=RED,
              hover_color="#FDECEF").pack(side="right")
        datos = ctk.CTkFrame(der, fg_color="transparent")
        datos.pack(side="right", padx=(0, 16))
        etiqueta(datos, session.nombre, size=13, anchor="e").pack(anchor="e")
        etiqueta(datos, rol_texto, size=11, weight="normal", color=MUTED,
                 anchor="e").pack(anchor="e")

        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.pack(fill="both", expand=True, padx=26, pady=20)

    def agregar_pagina(self, nombre, constructor, on_show=None):
        frame = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        constructor(frame)
        self.paginas[nombre] = (frame, on_show)
        return frame

    def iniciar(self, inicial=None):
        nombres = list(self.paginas)
        if len(nombres) > 1:
            self.nav = ctk.CTkSegmentedButton(
                self.barra, values=nombres, command=self.mostrar, height=36,
                corner_radius=10, fg_color="#DCE3EA", selected_color=BLUE,
                selected_hover_color=BLUE_HOVER, unselected_color="#DCE3EA",
                unselected_hover_color="#CBD5DF", text_color=INK,
                font=font(13, "bold"))
            self.nav.place(relx=0.5, rely=0.5, anchor="center")
        self.mostrar(inicial or nombres[0])

    def mostrar(self, nombre):
        for frame, _ in self.paginas.values():
            frame.pack_forget()
        frame, al_mostrar = self.paginas[nombre]
        frame.pack(fill="both", expand=True)
        if self.nav is not None:
            self.nav.set(nombre)
        if al_mostrar:
            al_mostrar()
