import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import List, Optional

from backend import RepositorioJSON
from business_logic import FORMATO_FECHA, ServicioAPPV


class InterfazGraficaAPPV(tk.Tk):
    """Capa de presentación gráfica (Tkinter) para la cadena de videoclubs APPV."""

    def __init__(self, servicio: ServicioAPPV):
        super().__init__()
        self.servicio = servicio

        self.title("APPV - Sistema de Gestión de Cadena de Videoclubs")
        self.geometry("1180x700")
        self.minsize(1050, 620)

        # Estado de selección para edición
        self._vc_editando_id: Optional[int] = None
        self._pel_editando_id: Optional[int] = None
        self._soc_editando_id: Optional[int] = None
        self._alq_seleccionado_id: Optional[int] = None
        self._adm_editando_id: Optional[int] = None

        # Mapas auxiliares para Combobox y Listbox
        self._mapa_vc_combo: dict[str, int] = {}
        self._mapa_soc_combo: dict[str, int] = {}
        self._mapa_adm_combo: dict[str, int] = {}
        self._codigos_peliculas_listbox: List[int] = []

        self._configurar_estilos()
        self._construir_ui()
        self._refrescar_todo()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Titulo.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Subtitulo.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Total.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1b5e20")

    def _construir_ui(self) -> None:
        cabecera = ttk.Frame(self, padding=(12, 10))
        cabecera.pack(fill=tk.X)
        ttk.Label(
            cabecera,
            text="CADENA DE VIDEOCLUBS APPV — PANEL DE GESTIÓN",
            style="Titulo.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Label(
            cabecera,
            text="Nota: Todas las fechas se introducen manualmente (DD/MM/AAAA)",
            foreground="#555555",
        ).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tab_videoclubs = ttk.Frame(self.notebook, padding=10)
        self.tab_peliculas = ttk.Frame(self.notebook, padding=10)
        self.tab_socios = ttk.Frame(self.notebook, padding=10)
        self.tab_alquileres = ttk.Frame(self.notebook, padding=10)
        self.tab_admin_stats = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_videoclubs, text="  Videoclubs  ")
        self.notebook.add(self.tab_peliculas, text="  Películas  ")
        self.notebook.add(self.tab_socios, text="  Socios  ")
        self.notebook.add(self.tab_alquileres, text="  Alquileres  ")
        self.notebook.add(self.tab_admin_stats, text="  Administradores y Estadísticas  ")

        self._construir_tab_videoclubs()
        self._construir_tab_peliculas()
        self._construir_tab_socios()
        self._construir_tab_alquileres()
        self._construir_tab_admin_stats()

    # ==========================================
    # UTILIDADES DE VALIDACIÓN Y TABLAS
    # ==========================================

    @staticmethod
    def _parsear_fecha(texto: str, nombre_campo: str) -> datetime:
        valor = texto.strip()
        if not valor:
            raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
        try:
            return datetime.strptime(valor, FORMATO_FECHA)
        except ValueError as exc:
            raise ValueError(
                f"Formato incorrecto en '{nombre_campo}'. Usa DD/MM/AAAA (ej. 19/11/2026)."
            ) from exc

    @staticmethod
    def _parsear_entero(texto: str, nombre_campo: str) -> int:
        valor = texto.strip()
        if not valor:
            raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
        try:
            return int(valor)
        except ValueError as exc:
            raise ValueError(f"El campo '{nombre_campo}' debe ser un número entero.") from exc

    @staticmethod
    def _parsear_real(texto: str, nombre_campo: str) -> float:
        valor = texto.strip().replace(",", ".")
        if not valor:
            raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
        try:
            return float(valor)
        except ValueError as exc:
            raise ValueError(f"El campo '{nombre_campo}' debe ser un número decimal válido.") from exc

    @staticmethod
    def _crear_treeview(contenedor: ttk.Frame, columnas: tuple, anchos: tuple) -> ttk.Treeview:
        frame_tabla = ttk.Frame(contenedor)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")
        for col, ancho in zip(columnas, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor=tk.W)

        scroll_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll_y.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ==========================================
    # PESTAÑA 1: VIDEOCLUBS
    # ==========================================

    def _construir_tab_videoclubs(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_videoclubs, text="Datos del Videoclub", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_vc_modo = ttk.Label(panel_izq, text="Modo: Nuevo Videoclub", style="Subtitulo.TLabel")
        self.lbl_vc_modo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(panel_izq, text="Gerente (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_vc_gerente = ttk.Entry(panel_izq, width=28)
        self.ent_vc_gerente.grid(row=1, column=1, pady=4)

        ttk.Label(panel_izq, text="Ciudad (*):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_vc_ciudad = ttk.Entry(panel_izq, width=28)
        self.ent_vc_ciudad.grid(row=2, column=1, pady=4)

        ttk.Label(panel_izq, text="Calle (*):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.ent_vc_calle = ttk.Entry(panel_izq, width=28)
        self.ent_vc_calle.grid(row=3, column=1, pady=4)

        ttk.Label(panel_izq, text="Código Postal (5 car.) (*):").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.ent_vc_cp = ttk.Entry(panel_izq, width=28)
        self.ent_vc_cp.grid(row=4, column=1, pady=4)

        botones = ttk.Frame(panel_izq)
        botones.grid(row=5, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(botones, text="Guardar Videoclub", command=self._guardar_videoclub).pack(side=tk.LEFT, padx=4)
        ttk.Button(botones, text="Limpiar / Nuevo", command=self._limpiar_form_videoclub).pack(side=tk.LEFT, padx=4)

        panel_der = ttk.LabelFrame(self.tab_videoclubs, text="Listado de Videoclubs (Haz clic para editar)", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_vc = self._crear_treeview(
            panel_der,
            ("Código", "Gerente", "Ciudad", "Calle", "C.P."),
            (70, 170, 140, 200, 80),
        )
        self.tree_vc.bind("<<TreeviewSelect>>", self._seleccionar_videoclub)

    def _guardar_videoclub(self) -> None:
        try:
            gerente = self.ent_vc_gerente.get()
            ciudad = self.ent_vc_ciudad.get()
            calle = self.ent_vc_calle.get()
            cp = self.ent_vc_cp.get()

            if self._vc_editando_id is None:
                vc = self.servicio.crear_videoclub(gerente, ciudad, calle, cp)
                messagebox.showinfo("Éxito", f"Videoclub creado con código VC-{vc.codigo}.")
            else:
                vc = self.servicio.editar_videoclub(self._vc_editando_id, gerente, ciudad, calle, cp)
                messagebox.showinfo("Éxito", f"Videoclub VC-{vc.codigo} actualizado.")

            self._limpiar_form_videoclub()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    def _seleccionar_videoclub(self, _event) -> None:
        sel = self.tree_vc.selection()
        if not sel:
            return
        valores = self.tree_vc.item(sel[0], "values")
        self._vc_editando_id = int(valores[0])
        self.lbl_vc_modo.config(text=f"Modo: Editando VC-{self._vc_editando_id}")

        self.ent_vc_gerente.delete(0, tk.END)
        self.ent_vc_gerente.insert(0, valores[1])
        self.ent_vc_ciudad.delete(0, tk.END)
        self.ent_vc_ciudad.insert(0, valores[2])
        self.ent_vc_calle.delete(0, tk.END)
        self.ent_vc_calle.insert(0, valores[3])
        self.ent_vc_cp.delete(0, tk.END)
        self.ent_vc_cp.insert(0, valores[4])

    def _limpiar_form_videoclub(self) -> None:
        self._vc_editando_id = None
        self.lbl_vc_modo.config(text="Modo: Nuevo Videoclub")
        for ent in (self.ent_vc_gerente, self.ent_vc_ciudad, self.ent_vc_calle, self.ent_vc_cp):
            ent.delete(0, tk.END)
        self.tree_vc.selection_remove(self.tree_vc.selection())

    # ==========================================
    # PESTAÑA 2: PELÍCULAS
    # ==========================================

    def _construir_tab_peliculas(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_peliculas, text="Datos de la Película", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_pel_modo = ttk.Label(panel_izq, text="Modo: Nueva Película", style="Subtitulo.TLabel")
        self.lbl_pel_modo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(panel_izq, text="Videoclub (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_pel_vc = ttk.Combobox(panel_izq, width=26, state="readonly")
        self.cmb_pel_vc.grid(row=1, column=1, pady=4)

        ttk.Label(panel_izq, text="Nombre (*):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_pel_nombre = ttk.Entry(panel_izq, width=29)
        self.ent_pel_nombre.grid(row=2, column=1, pady=4)

        ttk.Label(panel_izq, text="Director (opcional):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.ent_pel_director = ttk.Entry(panel_izq, width=29)
        self.ent_pel_director.grid(row=3, column=1, pady=4)

        ttk.Label(panel_izq, text="Estreno (DD/MM/AAAA) (*):").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.ent_pel_estreno = ttk.Entry(panel_izq, width=29)
        self.ent_pel_estreno.grid(row=4, column=1, pady=4)

        ttk.Label(panel_izq, text="Precio Alquiler (€) (*):").grid(row=5, column=0, sticky=tk.W, pady=4)
        self.ent_pel_precio = ttk.Entry(panel_izq, width=29)
        self.ent_pel_precio.grid(row=5, column=1, pady=4)

        botones = ttk.Frame(panel_izq)
        botones.grid(row=6, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(botones, text="Guardar Película", command=self._guardar_pelicula).pack(side=tk.LEFT, padx=4)
        ttk.Button(botones, text="Limpiar / Nueva", command=self._limpiar_form_pelicula).pack(side=tk.LEFT, padx=4)

        panel_der = ttk.LabelFrame(self.tab_peliculas, text="Catálogo de Películas por Videoclub (Haz clic para editar)", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_pel = self._crear_treeview(
            panel_der,
            ("Código", "Nombre", "Director", "Estreno", "Precio (€)", "Videoclub"),
            (65, 175, 145, 95, 80, 175),
        )
        self.tree_pel.bind("<<TreeviewSelect>>", self._seleccionar_pelicula)

    def _guardar_pelicula(self) -> None:
        try:
            nombre = self.ent_pel_nombre.get()
            director_raw = self.ent_pel_director.get().strip()
            fecha_estreno = self._parsear_fecha(self.ent_pel_estreno.get(), "Fecha de estreno")
            precio = self._parsear_real(self.ent_pel_precio.get(), "Precio de alquiler")

            if self._pel_editando_id is None:
                vc_texto = self.cmb_pel_vc.get()
                if vc_texto not in self._mapa_vc_combo:
                    raise ValueError("Debes seleccionar un videoclub para asignar la película.")
                vc_codigo = self._mapa_vc_combo[vc_texto]
                pel = self.servicio.crear_pelicula(
                    vc_codigo, nombre, fecha_estreno, precio, director_raw or None
                )
                messagebox.showinfo("Éxito", f"Película creada con código PEL-{pel.codigo}.")
            else:
                limpiar_dir = director_raw == ""
                pel = self.servicio.editar_pelicula(
                    codigo=self._pel_editando_id,
                    nombre=nombre,
                    director=director_raw if not limpiar_dir else None,
                    limpiar_director=limpiar_dir,
                    fecha_estreno=fecha_estreno,
                    precio_alquiler=precio,
                )
                messagebox.showinfo("Éxito", f"Película PEL-{pel.codigo} actualizada.")

            self._limpiar_form_pelicula()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    def _seleccionar_pelicula(self, _event) -> None:
        sel = self.tree_pel.selection()
        if not sel:
            return
        valores = self.tree_pel.item(sel[0], "values")
        self._pel_editando_id = int(valores[0])
        self.lbl_pel_modo.config(text=f"Modo: Editando PEL-{self._pel_editando_id}")

        self.cmb_pel_vc.set(valores[5])
        self.cmb_pel_vc.config(state="disabled")

        self.ent_pel_nombre.delete(0, tk.END)
        self.ent_pel_nombre.insert(0, valores[1])

        self.ent_pel_director.delete(0, tk.END)
        if valores[2] != "—":
            self.ent_pel_director.insert(0, valores[2])

        self.ent_pel_estreno.delete(0, tk.END)
        self.ent_pel_estreno.insert(0, valores[3])

        self.ent_pel_precio.delete(0, tk.END)
        self.ent_pel_precio.insert(0, valores[4])

    def _limpiar_form_pelicula(self) -> None:
        self._pel_editando_id = None
        self.lbl_pel_modo.config(text="Modo: Nueva Película")
        self.cmb_pel_vc.config(state="readonly")
        self.cmb_pel_vc.set("")
        for ent in (self.ent_pel_nombre, self.ent_pel_director, self.ent_pel_estreno, self.ent_pel_precio):
            ent.delete(0, tk.END)
        self.tree_pel.selection_remove(self.tree_pel.selection())

    # ==========================================
    # PESTAÑA 3: SOCIOS
    # ==========================================

    def _construir_tab_socios(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_socios, text="Datos del Socio", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_soc_modo = ttk.Label(panel_izq, text="Modo: Nuevo Socio", style="Subtitulo.TLabel")
        self.lbl_soc_modo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(panel_izq, text="Nombre Completo (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_soc_nombre = ttk.Entry(panel_izq, width=28)
        self.ent_soc_nombre.grid(row=1, column=1, pady=4)

        ttk.Label(panel_izq, text="Edad (*):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_soc_edad = ttk.Entry(panel_izq, width=28)
        self.ent_soc_edad.grid(row=2, column=1, pady=4)

        botones = ttk.Frame(panel_izq)
        botones.grid(row=3, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(botones, text="Guardar Socio", command=self._guardar_socio).pack(side=tk.LEFT, padx=4)
        ttk.Button(botones, text="Limpiar / Nuevo", command=self._limpiar_form_socio).pack(side=tk.LEFT, padx=4)

        panel_der = ttk.LabelFrame(
            self.tab_socios,
            text="Socios Registrados (Válidos en toda la cadena APPV — Clic para editar)",
            padding=10,
        )
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_soc = self._crear_treeview(
            panel_der,
            ("Código", "Nombre", "Edad"),
            (80, 320, 100),
        )
        self.tree_soc.bind("<<TreeviewSelect>>", self._seleccionar_socio)

    def _guardar_socio(self) -> None:
        try:
            nombre = self.ent_soc_nombre.get()
            edad = self._parsear_entero(self.ent_soc_edad.get(), "Edad")

            if self._soc_editando_id is None:
                socio = self.servicio.crear_socio(nombre, edad)
                messagebox.showinfo("Éxito", f"Socio registrado con código SOC-{socio.codigo}.")
            else:
                socio = self.servicio.editar_socio(self._soc_editando_id, nombre, edad)
                messagebox.showinfo("Éxito", f"Socio SOC-{socio.codigo} actualizado.")

            self._limpiar_form_socio()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    def _seleccionar_socio(self, _event) -> None:
        sel = self.tree_soc.selection()
        if not sel:
            return
        valores = self.tree_soc.item(sel[0], "values")
        self._soc_editando_id = int(valores[0])
        self.lbl_soc_modo.config(text=f"Modo: Editando SOC-{self._soc_editando_id}")

        self.ent_soc_nombre.delete(0, tk.END)
        self.ent_soc_nombre.insert(0, valores[1])
        self.ent_soc_edad.delete(0, tk.END)
        self.ent_soc_edad.insert(0, valores[2])

    def _limpiar_form_socio(self) -> None:
        self._soc_editando_id = None
        self.lbl_soc_modo.config(text="Modo: Nuevo Socio")
        self.ent_soc_nombre.delete(0, tk.END)
        self.ent_soc_edad.delete(0, tk.END)
        self.tree_soc.selection_remove(self.tree_soc.selection())

    # ==========================================
    # PESTAÑA 4: ALQUILERES
    # ==========================================

    def _construir_tab_alquileres(self) -> None:
        panel_izq = ttk.Frame(self.tab_alquileres)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Bloque Superior: Registrar nuevo alquiler
        box_nuevo = ttk.LabelFrame(panel_izq, text="Registrar Nuevo Alquiler", padding=10)
        box_nuevo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(box_nuevo, text="Socio (*):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cmb_alq_socio = ttk.Combobox(box_nuevo, width=32, state="readonly")
        self.cmb_alq_socio.grid(row=0, column=1, pady=3)

        ttk.Label(box_nuevo, text="Películas (clic para marcar/desmarcar) (*):").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(6, 2)
        )
        frame_list = ttk.Frame(box_nuevo)
        frame_list.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        self.lst_alq_peliculas = tk.Listbox(
            frame_list, selectmode=tk.MULTIPLE, height=6, width=46, exportselection=False
        )
        scroll_lst = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.lst_alq_peliculas.yview)
        self.lst_alq_peliculas.configure(yscrollcommand=scroll_lst.set)
        self.lst_alq_peliculas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_lst.pack(side=tk.RIGHT, fill=tk.Y)
        self.lst_alq_peliculas.bind("<<ListboxSelect>>", self._actualizar_preview_total_alquiler)

        self.lbl_alq_total_preview = ttk.Label(
            box_nuevo, text="Total derivado a pagar: 0.00 €", style="Total.TLabel"
        )
        self.lbl_alq_total_preview.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(6, 4))

        ttk.Label(box_nuevo, text="Fecha Recogida (DD/MM/AAAA) (*):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.ent_alq_recogida = ttk.Entry(box_nuevo, width=20)
        self.ent_alq_recogida.grid(row=4, column=1, sticky=tk.W, pady=3)

        ttk.Label(box_nuevo, text="Fecha Devolución (DD/MM/AAAA) (*):").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.ent_alq_devolucion = ttk.Entry(box_nuevo, width=20)
        self.ent_alq_devolucion.grid(row=5, column=1, sticky=tk.W, pady=3)

        ttk.Button(box_nuevo, text="Registrar Alquiler", command=self._registrar_alquiler).grid(
            row=6, column=0, columnspan=2, pady=(10, 2)
        )

        # Bloque Inferior: Editar fecha de devolución de un alquiler existente
        box_editar = ttk.LabelFrame(
            panel_izq, text="Modificar Fecha de Devolución (Selecciona en la tabla)", padding=10
        )
        box_editar.pack(fill=tk.X)

        self.lbl_alq_edit_sel = ttk.Label(box_editar, text="Alquiler seleccionado: Ninguno", style="Subtitulo.TLabel")
        self.lbl_alq_edit_sel.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

        ttk.Label(box_editar, text="Fecha Actual Manual (DD/MM/AAAA) (*):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_alq_edit_actual = ttk.Entry(box_editar, width=20)
        self.ent_alq_edit_actual.grid(row=1, column=1, sticky=tk.W, pady=3)

        ttk.Label(box_editar, text="Nueva Devolución (DD/MM/AAAA) (*):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ent_alq_edit_nueva = ttk.Entry(box_editar, width=20)
        self.ent_alq_edit_nueva.grid(row=2, column=1, sticky=tk.W, pady=3)

        ttk.Button(box_editar, text="Actualizar Fecha Devolución", command=self._actualizar_devolucion).grid(
            row=3, column=0, columnspan=2, pady=(8, 2)
        )

        # Panel Derecho: Historial de alquileres
        panel_der = ttk.LabelFrame(self.tab_alquileres, text="Historial de Alquileres", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_alq = self._crear_treeview(
            panel_der,
            ("Código", "Socio", "Películas Incluidas", "Recogida", "Devolución", "Total (€)"),
            (60, 140, 230, 90, 90, 75),
        )
        self.tree_alq.bind("<<TreeviewSelect>>", self._seleccionar_alquiler)

    def _actualizar_preview_total_alquiler(self, _event=None) -> None:
        indices = self.lst_alq_peliculas.curselection()
        total = 0.0
        for idx in indices:
            cod = self._codigos_peliculas_listbox[idx]
            pel = self.servicio.obtener_pelicula(cod)
            if pel:
                total += pel.precio_alquiler
        self.lbl_alq_total_preview.config(text=f"Total derivado a pagar: {total:.2f} €")

    def _registrar_alquiler(self) -> None:
        try:
            socio_txt = self.cmb_alq_socio.get()
            if socio_txt not in self._mapa_soc_combo:
                raise ValueError("Debes seleccionar un socio.")
            socio_cod = self._mapa_soc_combo[socio_txt]

            indices = self.lst_alq_peliculas.curselection()
            if not indices:
                raise ValueError("Debes seleccionar al menos una película.")
            codigos_pel = [self._codigos_peliculas_listbox[i] for i in indices]

            f_recogida = self._parsear_fecha(self.ent_alq_recogida.get(), "Fecha de recogida")
            f_devolucion = self._parsear_fecha(self.ent_alq_devolucion.get(), "Fecha de devolución")

            alq = self.servicio.registrar_alquiler(socio_cod, codigos_pel, f_recogida, f_devolucion)
            messagebox.showinfo(
                "Alquiler Registrado",
                f"Alquiler ALQ-{alq.codigo} creado.\nTotal a pagar: {alq.total_a_pagar:.2f} €",
            )

            self.cmb_alq_socio.set("")
            self.lst_alq_peliculas.selection_clear(0, tk.END)
            self._actualizar_preview_total_alquiler()
            self.ent_alq_recogida.delete(0, tk.END)
            self.ent_alq_devolucion.delete(0, tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    def _seleccionar_alquiler(self, _event) -> None:
        sel = self.tree_alq.selection()
        if not sel:
            return
        valores = self.tree_alq.item(sel[0], "values")
        self._alq_seleccionado_id = int(valores[0])
        self.lbl_alq_edit_sel.config(
            text=f"Alquiler seleccionado: ALQ-{self._alq_seleccionado_id} (Dev. actual: {valores[4]})"
        )

    def _actualizar_devolucion(self) -> None:
        try:
            if self._alq_seleccionado_id is None:
                raise ValueError("Selecciona primero un alquiler en la tabla de la derecha.")
            f_actual = self._parsear_fecha(self.ent_alq_edit_actual.get(), "Fecha actual manual")
            f_nueva = self._parsear_fecha(self.ent_alq_edit_nueva.get(), "Nueva fecha de devolución")

            alq = self.servicio.modificar_fecha_devolucion(self._alq_seleccionado_id, f_nueva, f_actual)
            messagebox.showinfo(
                "Éxito",
                f"Fecha de devolución de ALQ-{alq.codigo} actualizada a {alq.fecha_devolucion.strftime(FORMATO_FECHA)}.",
            )

            self._alq_seleccionado_id = None
            self.lbl_alq_edit_sel.config(text="Alquiler seleccionado: Ninguno")
            self.ent_alq_edit_actual.delete(0, tk.END)
            self.ent_alq_edit_nueva.delete(0, tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    # ==========================================
    # PESTAÑA 5: ADMINISTRADORES Y ESTADÍSTICAS
    # ==========================================

    def _construir_tab_admin_stats(self) -> None:
        panel_izq = ttk.Frame(self.tab_admin_stats)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Bloque Superior: Administradores
        box_adm = ttk.LabelFrame(panel_izq, text="Gestión de Administradores", padding=10)
        box_adm.pack(fill=tk.X, pady=(0, 10))

        self.lbl_adm_modo = ttk.Label(box_adm, text="Modo: Nuevo Administrador", style="Subtitulo.TLabel")
        self.lbl_adm_modo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

        ttk.Label(box_adm, text="Nombre (*):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_adm_nombre = ttk.Entry(box_adm, width=28)
        self.ent_adm_nombre.grid(row=1, column=1, pady=3)

        btns_adm = ttk.Frame(box_adm)
        btns_adm.grid(row=2, column=0, columnspan=2, pady=6)
        ttk.Button(btns_adm, text="Guardar Admin", command=self._guardar_admin).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns_adm, text="Limpiar", command=self._limpiar_form_admin).pack(side=tk.LEFT, padx=4)

        frame_tree_adm = ttk.Frame(box_adm, height=110)
        frame_tree_adm.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(4, 0))
        frame_tree_adm.pack_propagate(False)
        self.tree_adm = self._crear_treeview(frame_tree_adm, ("Código", "Nombre Administrador"), (80, 240))
        self.tree_adm.bind("<<TreeviewSelect>>", self._seleccionar_admin)

        # Bloque Inferior: Cálculo Estadístico Mensual por Socio
        box_est = ttk.LabelFrame(panel_izq, text="Calcular Estadística Mensual por Socio", padding=10)
        box_est.pack(fill=tk.X)

        ttk.Label(box_est, text="Administrador (*):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cmb_est_admin = ttk.Combobox(box_est, width=26, state="readonly")
        self.cmb_est_admin.grid(row=0, column=1, pady=3)

        ttk.Label(box_est, text="Socio a analizar (*):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.cmb_est_socio = ttk.Combobox(box_est, width=26, state="readonly")
        self.cmb_est_socio.grid(row=1, column=1, pady=3)

        ttk.Label(box_est, text="Mes (1-12) (*):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ent_est_mes = ttk.Entry(box_est, width=29)
        self.ent_est_mes.grid(row=2, column=1, pady=3)

        ttk.Label(box_est, text="Año (AAAA) (*):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.ent_est_anio = ttk.Entry(box_est, width=29)
        self.ent_est_anio.grid(row=3, column=1, pady=3)

        ttk.Label(box_est, text="Fecha Creación (DD/MM/AAAA) (*):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.ent_est_creacion = ttk.Entry(box_est, width=29)
        self.ent_est_creacion.grid(row=4, column=1, pady=3)

        ttk.Button(box_est, text="Generar Estadística Mensual", command=self._generar_estadistica).grid(
            row=5, column=0, columnspan=2, pady=(10, 2)
        )

        # Panel Derecho: Historial de Estadísticas
        panel_der = ttk.LabelFrame(
            self.tab_admin_stats,
            text="Estadísticas Mensuales Almacenadas (Máx. 1 por socio y mes)",
            padding=10,
        )
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_est = self._crear_treeview(
            panel_der,
            ("Código", "Socio", "Periodo", "Fecha Creación", "Total Gastado (€)"),
            (70, 200, 90, 120, 120),
        )

    def _guardar_admin(self) -> None:
        try:
            nombre = self.ent_adm_nombre.get()
            if self._adm_editando_id is None:
                adm = self.servicio.crear_administrador(nombre)
                messagebox.showinfo("Éxito", f"Administrador ADM-{adm.codigo} creado.")
            else:
                adm = self.servicio.editar_administrador(self._adm_editando_id, nombre)
                messagebox.showinfo("Éxito", f"Administrador ADM-{adm.codigo} actualizado.")
            self._limpiar_form_admin()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    def _seleccionar_admin(self, _event) -> None:
        sel = self.tree_adm.selection()
        if not sel:
            return
        valores = self.tree_adm.item(sel[0], "values")
        self._adm_editando_id = int(valores[0])
        self.lbl_adm_modo.config(text=f"Modo: Editando ADM-{self._adm_editando_id}")
        self.ent_adm_nombre.delete(0, tk.END)
        self.ent_adm_nombre.insert(0, valores[1])

    def _limpiar_form_admin(self) -> None:
        self._adm_editando_id = None
        self.lbl_adm_modo.config(text="Modo: Nuevo Administrador")
        self.ent_adm_nombre.delete(0, tk.END)
        self.tree_adm.selection_remove(self.tree_adm.selection())

    def _generar_estadistica(self) -> None:
        try:
            adm_txt = self.cmb_est_admin.get()
            if adm_txt not in self._mapa_adm_combo:
                raise ValueError("Debes seleccionar un administrador.")
            adm_cod = self._mapa_adm_combo[adm_txt]

            soc_txt = self.cmb_est_socio.get()
            if soc_txt not in self._mapa_soc_combo:
                raise ValueError("Debes seleccionar un socio.")
            soc_cod = self._mapa_soc_combo[soc_txt]

            mes = self._parsear_entero(self.ent_est_mes.get(), "Mes")
            anio = self._parsear_entero(self.ent_est_anio.get(), "Año")
            if anio < 1900 or anio > 9999:
                raise ValueError("Introduce un año válido de 4 dígitos (ej. 2026).")
            f_creacion = self._parsear_fecha(self.ent_est_creacion.get(), "Fecha de creación")

            est = self.servicio.generar_estadistica_mensual(adm_cod, soc_cod, mes, anio, f_creacion)
            messagebox.showinfo(
                "Estadística Generada",
                f"Estadística EST-{est.codigo} registrada.\nTotal gastado en {est.mes:02d}/{est.anio}: {est.total_gastado:.2f} €",
            )

            self.ent_est_mes.delete(0, tk.END)
            self.ent_est_anio.delete(0, tk.END)
            self.ent_est_creacion.delete(0, tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error de validación", str(err))

    # ==========================================
    # SINCRONIZACIÓN DE TODAS LAS VISTAS
    # ==========================================

    def _refrescar_todo(self) -> None:
        # 1. Videoclubs
        self.tree_vc.delete(*self.tree_vc.get_children())
        self._mapa_vc_combo.clear()
        for v in self.servicio.videoclubs:
            self.tree_vc.insert("", tk.END, values=(v.codigo, v.gerente, v.ciudad, v.calle, v.codigo_postal))
            etiqueta = f"VC-{v.codigo} | {v.ciudad} ({v.calle})"
            self._mapa_vc_combo[etiqueta] = v.codigo
        self.cmb_pel_vc["values"] = list(self._mapa_vc_combo.keys())

        # 2. Películas
        self.tree_pel.delete(*self.tree_pel.get_children())
        self.lst_alq_peliculas.delete(0, tk.END)
        self._codigos_peliculas_listbox.clear()
        for p in self.servicio.peliculas:
            vc_label = f"VC-{p.videoclub.codigo} | {p.videoclub.ciudad}"
            self.tree_pel.insert(
                "",
                tk.END,
                values=(
                    p.codigo,
                    p.nombre,
                    p.director or "—",
                    p.fecha_estreno.strftime(FORMATO_FECHA),
                    f"{p.precio_alquiler:.2f}",
                    vc_label,
                ),
            )
            self.lst_alq_peliculas.insert(
                tk.END,
                f"[PEL-{p.codigo}] {p.nombre} ({p.videoclub.ciudad}) - {p.precio_alquiler:.2f} €",
            )
            self._codigos_peliculas_listbox.append(p.codigo)

        # 3. Socios
        self.tree_soc.delete(*self.tree_soc.get_children())
        self._mapa_soc_combo.clear()
        for s in self.servicio.socios:
            self.tree_soc.insert("", tk.END, values=(s.codigo, s.nombre, s.edad))
            etiqueta = f"SOC-{s.codigo} | {s.nombre}"
            self._mapa_soc_combo[etiqueta] = s.codigo
        valores_socios = list(self._mapa_soc_combo.keys())
        self.cmb_alq_socio["values"] = valores_socios
        self.cmb_est_socio["values"] = valores_socios

        # 4. Alquileres
        self.tree_alq.delete(*self.tree_alq.get_children())
        for a in self.servicio.alquileres:
            titulos = ", ".join(f"{p.nombre} (PEL-{p.codigo})" for p in a.peliculas)
            self.tree_alq.insert(
                "",
                tk.END,
                values=(
                    a.codigo,
                    f"{a.socio.nombre} (SOC-{a.socio.codigo})",
                    titulos,
                    a.fecha_recogida.strftime(FORMATO_FECHA),
                    a.fecha_devolucion.strftime(FORMATO_FECHA),
                    f"{a.total_a_pagar:.2f}",
                ),
            )

        # 5. Administradores
        self.tree_adm.delete(*self.tree_adm.get_children())
        self._mapa_adm_combo.clear()
        for ad in self.servicio.administradores:
            self.tree_adm.insert("", tk.END, values=(ad.codigo, ad.nombre))
            etiqueta = f"ADM-{ad.codigo} | {ad.nombre}"
            self._mapa_adm_combo[etiqueta] = ad.codigo
        self.cmb_est_admin["values"] = list(self._mapa_adm_combo.keys())

        # 6. Estadísticas
        self.tree_est.delete(*self.tree_est.get_children())
        for e in self.servicio.estadisticas:
            self.tree_est.insert(
                "",
                tk.END,
                values=(
                    e.codigo,
                    f"{e.socio.nombre} (SOC-{e.socio.codigo})",
                    f"{e.mes:02d}/{e.anio}",
                    e.fecha_creacion.strftime(FORMATO_FECHA),
                    f"{e.total_gastado:.2f}",
                ),
            )


def main() -> None:
    try:
        repositorio = RepositorioJSON("datos_appv.json")
        servicio = ServicioAPPV(repositorio)
        app = InterfazGraficaAPPV(servicio)
        app.mainloop()
    except RuntimeError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error crítico", f"No se pudo iniciar la aplicación:\n{exc}")


if __name__ == "__main__":
    main()