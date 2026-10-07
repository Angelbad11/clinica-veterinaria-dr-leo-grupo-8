import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageTk

from services.clinica_service import ClinicaService


class AppVeterinaria:
    COLORES = {
        "azul_oscuro": "#17384A",
        "azul": "#285D73",
        "celeste": "#5EAFC0",
        "verde": "#278C80",
        "fondo": "#F1F6F6",
        "panel": "#ffffff",
        "borde": "#DCE7E8",
        "texto": "#263A43",
        "gris": "#71818A",
        "advertencia": "#D99052",
        "verde_claro": "#E6F3F0",
        "azul_claro": "#E8F2F5",
        "sombra": "#E9F0F1",
    }

    def __init__(self):
        self.servicio = ClinicaService()
        self.paginas = {}
        self.botones_menu = {}
        self.seccion_actual = None
        self.indice_propietario_editando = None
        self.indices_propietarios = []
        self.indices_mascotas = []
        self.indices_citas = []
        self.indices_pagos = []
        self.indices_atenciones = []

        self.ventana = tk.Tk()
        self.ventana.title("Clínica veterinaria Dr. Leo | Grupo 8")
        self.ventana.geometry("1100x730")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg=self.COLORES["fondo"])

        self.configurar_estilos()
        self.cargar_fondo()
        self.crear_interfaz()

    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Vertical.TScrollbar",
            background=self.COLORES["sombra"],
            troughcolor=self.COLORES["fondo"],
            bordercolor=self.COLORES["fondo"],
            arrowcolor=self.COLORES["gris"],
        )
        estilo.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground=self.COLORES["texto"],
            bordercolor=self.COLORES["borde"],
            lightcolor=self.COLORES["borde"],
            darkcolor=self.COLORES["borde"],
            arrowsize=13,
            padding=6,
            font=("Segoe UI", 10),
        )
        estilo.map(
            "TCombobox",
            fieldbackground=[("readonly", "#ffffff")],
            selectbackground=[("readonly", "#ffffff")],
            selectforeground=[("readonly", self.COLORES["texto"])],
        )

    def cargar_fondo(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_fondo = os.path.join(base_dir, "assets", "fondo.png")

        if os.path.exists(ruta_fondo):
            imagen = Image.open(ruta_fondo)
            imagen = imagen.resize((1100, 730))
            self.imagen_fondo = ImageTk.PhotoImage(imagen)

            self.etiqueta_fondo = tk.Label(self.ventana, image=self.imagen_fondo)
            self.etiqueta_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.ventana.configure(bg=self.COLORES["fondo"])

    def crear_interfaz(self):
        self.contenedor = tk.Frame(
            self.ventana,
            bg=self.COLORES["panel"],
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
        )
        self.contenedor.place(x=20, y=16, width=1060, height=698)

        self.crear_menu_lateral()
        self.crear_area_principal()

        self.tab_inicio = self.crear_pagina("Inicio")
        self.tab_propietarios = self.crear_pagina("Propietarios")
        self.tab_mascotas = self.crear_pagina("Mascotas")
        self.tab_citas = self.crear_pagina("Citas")
        self.tab_atenciones = self.crear_pagina("Consultas")
        self.tab_pagos = self.crear_pagina("Pagos")
        self.tab_historial = self.crear_pagina("Historial")
        self.tab_recordatorios = self.crear_pagina("Recordatorios")
        self.tab_reportes = self.crear_pagina("Reportes")

        self.crear_tab_inicio()
        self.crear_tab_propietarios()
        self.crear_tab_mascotas()
        self.crear_tab_citas()
        self.crear_tab_atenciones()
        self.crear_tab_pagos()
        self.crear_tab_historial()
        self.crear_tab_recordatorios()
        self.crear_tab_reportes()

        self.actualizar_todo()
        self.mostrar_seccion("Inicio")

    def crear_menu_lateral(self):
        self.menu_lateral = tk.Frame(self.contenedor, bg=self.COLORES["azul_oscuro"])
        self.menu_lateral.place(x=0, y=0, width=220, height=698)

        tk.Label(
            self.menu_lateral,
            text="Dr. Leo",
            bg=self.COLORES["azul_oscuro"],
            fg="#ffffff",
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w", padx=22, pady=(24, 0))

        tk.Label(
            self.menu_lateral,
            text="Gestión veterinaria",
            bg=self.COLORES["azul_oscuro"],
            fg="#b9d7e6",
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=24, pady=(2, 17))

        tk.Frame(
            self.menu_lateral,
            bg="#355769",
            height=1,
        ).pack(fill="x", padx=18, pady=(0, 14))

        tk.Label(
            self.menu_lateral,
            text="MENÚ PRINCIPAL",
            bg=self.COLORES["azul_oscuro"],
            fg="#91B1BD",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=23, pady=(0, 6))

        opciones = [
            ("Inicio", "Inicio"),
            ("Propietarios", "Propietarios"),
            ("Mascotas", "Mascotas"),
            ("Citas", "Citas"),
            ("Consultas", "Consultas"),
            ("Pagos", "Pagos"),
            ("Historial", "Historial"),
            ("Recordatorios", "Recordatorios"),
            ("Reportes", "Reportes"),
        ]

        for texto, pagina in opciones:
            boton = tk.Button(
                self.menu_lateral,
                text=texto,
                command=lambda nombre=pagina: self.mostrar_seccion(nombre),
                font=("Segoe UI", 10, "bold"),
                bg=self.COLORES["azul_oscuro"],
                fg="#dff3f8",
                activebackground=self.COLORES["azul"],
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                anchor="w",
                padx=18,
                pady=8,
                cursor="hand2",
            )
            boton.pack(fill="x", padx=10, pady=2)
            boton.bind(
                "<Enter>",
                lambda evento, nombre=pagina: self._hover_menu(nombre, True),
            )
            boton.bind(
                "<Leave>",
                lambda evento, nombre=pagina: self._hover_menu(nombre, False),
            )
            self.botones_menu[pagina] = boton

        tk.Label(
            self.menu_lateral,
            text="Grupo 8 | Proyecto académico",
            bg=self.COLORES["azul_oscuro"],
            fg="#9dc3d4",
            font=("Segoe UI", 9),
        ).pack(side="bottom", anchor="w", padx=22, pady=16)

    def crear_area_principal(self):
        self.area_principal = tk.Frame(self.contenedor, bg=self.COLORES["fondo"])
        self.area_principal.place(x=220, y=0, width=840, height=698)

        encabezado = tk.Frame(self.area_principal, bg=self.COLORES["fondo"])
        encabezado.pack(fill="x", padx=24, pady=(18, 11))

        fila_encabezado = tk.Frame(encabezado, bg=self.COLORES["fondo"])
        fila_encabezado.pack(fill="x")

        bloque_titulo = tk.Frame(fila_encabezado, bg=self.COLORES["fondo"])
        bloque_titulo.pack(side="left", fill="x", expand=True)

        tk.Label(
            bloque_titulo,
            text="CLÍNICA VETERINARIA",
            bg=self.COLORES["fondo"],
            fg=self.COLORES["verde"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 1))

        self.titulo_seccion = tk.Label(
            bloque_titulo,
            text="Inicio",
            bg=self.COLORES["fondo"],
            fg=self.COLORES["azul_oscuro"],
            font=("Segoe UI", 19, "bold"),
        )
        self.titulo_seccion.pack(anchor="w")

        tk.Label(
            fila_encabezado,
            text="GRUPO 8",
            bg=self.COLORES["verde_claro"],
            fg=self.COLORES["verde"],
            font=("Segoe UI", 8, "bold"),
            padx=11,
            pady=6,
        ).pack(side="right", anchor="n", pady=(5, 0))

        self.descripcion_seccion = tk.Label(
            encabezado,
            text="Resumen de la actividad de la clínica",
            bg=self.COLORES["fondo"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9),
        )
        self.descripcion_seccion.pack(anchor="w", pady=(3, 0))

        tk.Frame(encabezado, bg=self.COLORES["borde"], height=1).pack(
            fill="x", pady=(12, 0)
        )

        self.contenido = tk.Frame(self.area_principal, bg=self.COLORES["fondo"])
        self.contenido.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        self.contenido.grid_rowconfigure(0, weight=1)
        self.contenido.grid_columnconfigure(0, weight=1)

    def crear_pagina(self, nombre):
        pagina = tk.Frame(self.contenido, bg=self.COLORES["fondo"])
        pagina.grid(row=0, column=0, sticky="nsew")
        pagina.grid_rowconfigure(0, weight=1)
        pagina.grid_columnconfigure(1, weight=1)
        self.paginas[nombre] = pagina
        return pagina

    def mostrar_seccion(self, nombre):
        for pagina in self.paginas.values():
            pagina.grid_remove()

        self.paginas[nombre].grid()
        self.seccion_actual = nombre
        self.titulo_seccion.config(text=nombre)
        descripciones = {
            "Inicio": "Resumen de la actividad de la clínica",
            "Propietarios": "Administra los datos de contacto de los propietarios",
            "Mascotas": "Registra y organiza las mascotas atendidas",
            "Citas": "Agenda, actualiza y consulta las citas",
            "Consultas": "Registra diagnósticos, tratamientos y vacunas",
            "Pagos": "Controla los cobros y los ingresos confirmados",
            "Historial": "Revisa las consultas y vacunas de cada mascota",
            "Recordatorios": "Prepara mensajes para recordar las citas",
            "Reportes": "Consulta y exporta la información de gestión",
        }
        self.descripcion_seccion.config(text=descripciones.get(nombre, ""))

        for texto, boton in self.botones_menu.items():
            if texto == nombre:
                boton.config(bg=self.COLORES["verde"], fg="#ffffff")
            else:
                boton.config(bg=self.COLORES["azul_oscuro"], fg="#dff3f8")

        if nombre == "Inicio":
            self.actualizar_dashboard()
        elif nombre == "Historial":
            self.actualizar_lista_mascotas()

    def _hover_menu(self, nombre, entrando):
        boton = self.botones_menu.get(nombre)
        if boton is None or nombre == self.seccion_actual:
            return
        boton.config(
            bg=self.COLORES["azul"] if entrando else self.COLORES["azul_oscuro"]
        )

    def crear_panel(self, padre, titulo, columna, ancho=260):
        panel = tk.Frame(
            padre,
            bg=self.COLORES["panel"],
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
        )
        panel.grid(
            row=0,
            column=columna,
            sticky="nsew",
            padx=(0, 14) if columna == 0 else 0,
        )
        panel.grid_propagate(False)
        panel.config(width=ancho)

        tk.Label(
            panel,
            text=titulo,
            bg=self.COLORES["panel"],
            fg=self.COLORES["azul_oscuro"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Frame(panel, bg=self.COLORES["borde"], height=1).pack(
            fill="x", padx=16, pady=(0, 8)
        )

        return panel

    def crear_campo(self, padre, texto, ancho=28):
        tk.Label(
            padre,
            text=texto,
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(8, 2))

        entrada = tk.Entry(
            padre,
            width=ancho,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg=self.COLORES["texto"],
            relief="flat",
            highlightbackground=self.COLORES["borde"],
            highlightcolor=self.COLORES["celeste"],
            highlightthickness=1,
            insertbackground=self.COLORES["azul_oscuro"],
        )
        entrada.pack(anchor="w", padx=16, ipady=6)
        return entrada

    def crear_combo(self, padre, texto, ancho=25, valores=None):
        tk.Label(
            padre,
            text=texto,
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(8, 2))

        combo = ttk.Combobox(
            padre,
            width=ancho,
            state="readonly",
            values=valores if valores else [],
        )
        combo.pack(anchor="w", padx=16, ipady=3)
        return combo

    def crear_boton_accion(self, padre, texto, comando, color=None):
        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color if color else self.COLORES["verde"],
            fg="#ffffff",
            activebackground=self.COLORES["azul"],
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        )
        boton.pack(anchor="w", padx=16, pady=14)
        self._agregar_hover_boton(boton, boton.cget("bg"))
        return boton

    def _agregar_hover_boton(self, boton, color_base):
        boton.bind(
            "<Enter>",
            lambda evento: boton.config(bg=self.COLORES["azul"]),
        )
        boton.bind(
            "<Leave>",
            lambda evento: boton.config(bg=color_base),
        )

    def crear_listbox(self, padre, ancho=54, alto=20):
        contenedor = tk.Frame(padre, bg=self.COLORES["panel"])
        contenedor.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        barra = ttk.Scrollbar(contenedor)
        barra.pack(side="right", fill="y")

        lista = tk.Listbox(
            contenedor,
            width=ancho,
            height=alto,
            bg="#FCFEFE",
            fg=self.COLORES["texto"],
            selectbackground=self.COLORES["verde"],
            selectforeground="#ffffff",
            font=("Segoe UI", 9),
            activestyle="none",
            relief="flat",
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
            yscrollcommand=barra.set,
        )
        lista.pack(side="left", fill="both", expand=True)
        barra.config(command=lista.yview)
        return lista

    def crear_barra_lista(self, padre, acciones):
        barra = tk.Frame(padre, bg=self.COLORES["panel"])
        barra.pack(fill="x", padx=16, pady=(0, 8))

        for texto, comando, color in acciones:
            boton = tk.Button(
                barra,
                text=texto,
                command=comando,
                bg=color,
                fg="#ffffff",
                activebackground=self.COLORES["azul"],
                activeforeground="#ffffff",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                bd=0,
                padx=7,
                pady=5,
                cursor="hand2",
            )
            boton.pack(side="left", padx=(0, 5))
            self._agregar_hover_boton(boton, color)

        return barra

    def crear_texto(self, padre, ancho=62, alto=22):
        contenedor = tk.Frame(padre, bg=self.COLORES["panel"])
        contenedor.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        barra = ttk.Scrollbar(contenedor)
        barra.pack(side="right", fill="y")

        texto = tk.Text(
            contenedor,
            width=ancho,
            height=alto,
            bg="#FCFEFE",
            fg=self.COLORES["texto"],
            font=("Segoe UI", 10),
            relief="flat",
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
            wrap="word",
            yscrollcommand=barra.set,
        )
        texto.pack(side="left", fill="both", expand=True)
        barra.config(command=texto.yview)
        return texto

    def crear_tab_inicio(self):
        self.tab_inicio.grid_columnconfigure(0, weight=1)
        self.tab_inicio.grid_columnconfigure(1, weight=1)
        self.tab_inicio.grid_columnconfigure(2, weight=1)
        self.tab_inicio.grid_rowconfigure(3, weight=1)

        tk.Label(
            self.tab_inicio,
            text="Actividad de la clínica",
            bg=self.COLORES["fondo"],
            fg=self.COLORES["azul_oscuro"],
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(4, 14))

        self.valor_propietarios = self.crear_tarjeta(
            self.tab_inicio,
            "Propietarios",
            0,
            1,
            self.COLORES["verde"],
        )
        self.valor_mascotas = self.crear_tarjeta(
            self.tab_inicio,
            "Mascotas",
            1,
            1,
            self.COLORES["celeste"],
        )
        self.valor_citas = self.crear_tarjeta(
            self.tab_inicio,
            "Citas",
            2,
            1,
            self.COLORES["advertencia"],
        )
        self.valor_pagos_inicio = self.crear_tarjeta(
            self.tab_inicio,
            "Total confirmado",
            0,
            2,
            self.COLORES["azul"],
        )
        self.valor_atenciones_inicio = self.crear_tarjeta(
            self.tab_inicio,
            "Consultas",
            1,
            2,
            self.COLORES["verde"],
        )
        self.valor_pendientes_inicio = self.crear_tarjeta(
            self.tab_inicio,
            "Citas pendientes",
            2,
            2,
            self.COLORES["celeste"],
        )

        panel = tk.Frame(
            self.tab_inicio,
            bg=self.COLORES["panel"],
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
        )
        panel.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(14, 0))

        tk.Label(
            panel,
            text="Flujo de trabajo",
            bg=self.COLORES["panel"],
            fg=self.COLORES["azul_oscuro"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 4))

        pasos = [
            "1. Registra primero al propietario.",
            "2. Registra la mascota y relaciónala con su dueño.",
            "3. Agenda la cita de la mascota.",
            "4. Registra la consulta con diagnóstico, tratamiento y vacuna.",
            "5. Registra el pago con concepto, monto, método y estado.",
            "6. Revisa historial, recordatorios y reporte diario.",
        ]

        for paso in pasos:
            tk.Label(
                panel,
                text=paso,
                bg=self.COLORES["panel"],
                fg=self.COLORES["texto"],
                font=("Segoe UI", 10),
            ).pack(anchor="w", padx=22, pady=3)

    def crear_tarjeta(self, padre, titulo, columna, fila, color):
        tarjeta = tk.Frame(
            padre,
            bg=self.COLORES["panel"],
            highlightbackground=self.COLORES["borde"],
            highlightthickness=1,
        )
        tarjeta.grid(row=fila, column=columna, sticky="ew", padx=(0, 12), ipady=10)

        tk.Frame(tarjeta, bg=color, height=3).pack(fill="x")

        tk.Label(
            tarjeta,
            text=titulo,
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 2))

        valor = tk.Label(
            tarjeta,
            text="0",
            bg=self.COLORES["panel"],
            fg=color,
            font=("Segoe UI", 21, "bold"),
        )
        valor.pack(anchor="w", padx=14, pady=(0, 8))
        return valor

    def crear_tab_propietarios(self):
        formulario = self.crear_panel(self.tab_propietarios, "Nuevo propietario", 0, ancho=270)
        listado = self.crear_panel(self.tab_propietarios, "Propietarios registrados", 1, ancho=470)

        self.entrada_nombre_propietario = self.crear_campo(formulario, "Nombre del propietario")
        self.entrada_dni_propietario = self.crear_campo(formulario, "DNI")
        self.entrada_telefono_propietario = self.crear_campo(formulario, "Teléfono")
        self.crear_boton_accion(formulario, "Registrar propietario", self.registrar_propietario)
        self.crear_boton_accion(
            formulario,
            "Cargar seleccionado",
            self.cargar_propietario_para_editar,
            color=self.COLORES["azul"],
        )
        self.crear_boton_accion(
            formulario,
            "Guardar cambios",
            self.guardar_cambios_propietario,
            color=self.COLORES["advertencia"],
        )
        self.crear_boton_accion(
            formulario,
            "Cancelar edición",
            self.limpiar_formulario_propietario,
            color=self.COLORES["gris"],
        )

        self.etiqueta_modo_propietario = tk.Label(
            formulario,
            text="Modo: nuevo propietario",
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "italic"),
        )
        self.etiqueta_modo_propietario.pack(anchor="w", padx=16, pady=(0, 10))

        self.crear_barra_lista(
            listado,
            [
                ("Buscar", self.filtrar_propietarios_dialogo, self.COLORES["azul"]),
                ("Todos", self.mostrar_todos_propietarios, self.COLORES["gris"]),
                ("Eliminar", self.eliminar_propietario, self.COLORES["advertencia"]),
            ],
        )
        self.lista_propietarios = self.crear_listbox(listado, ancho=58, alto=24)
        self.lista_propietarios.bind(
            "<Double-Button-1>",
            lambda evento: self.cargar_propietario_para_editar(),
        )

    def crear_tab_mascotas(self):
        formulario = self.crear_panel(self.tab_mascotas, "Nueva mascota", 0, ancho=270)
        listado = self.crear_panel(self.tab_mascotas, "Mascotas registradas", 1, ancho=470)

        self.entrada_nombre_mascota = self.crear_campo(formulario, "Nombre de la mascota")
        self.entrada_especie_mascota = self.crear_campo(formulario, "Especie")
        self.entrada_edad_mascota = self.crear_campo(formulario, "Edad")
        self.combo_sexo_mascota = self.crear_combo(
            formulario,
            "Sexo",
            valores=["No especificado", "Macho", "Hembra"],
        )
        self.combo_sexo_mascota.current(0)
        self.combo_esterilizado_mascota = self.crear_combo(
            formulario,
            "Esterilizado",
            valores=["No especificado", "Sí", "No"],
        )
        self.combo_esterilizado_mascota.current(0)
        self.combo_propietarios = self.crear_combo(formulario, "Propietario")
        self.crear_boton_accion(formulario, "Registrar mascota", self.registrar_mascota)

        self.crear_barra_lista(
            listado,
            [
                ("Editar", self.editar_mascota, self.COLORES["azul"]),
                ("Eliminar", self.eliminar_mascota, self.COLORES["advertencia"]),
                ("Buscar", self.filtrar_mascotas_dialogo, self.COLORES["verde"]),
                ("Todos", self.mostrar_todas_mascotas, self.COLORES["gris"]),
            ],
        )
        self.lista_mascotas = self.crear_listbox(listado, ancho=58, alto=24)

    def crear_tab_citas(self):
        formulario = self.crear_panel(self.tab_citas, "Nueva cita", 0, ancho=270)
        listado = self.crear_panel(self.tab_citas, "Citas programadas", 1, ancho=470)

        self.combo_mascotas = self.crear_combo(formulario, "Mascota", ancho=25)
        self.entrada_fecha_cita = self.crear_campo(formulario, "Fecha de la cita")
        self.entrada_fecha_cita.insert(0, "06/10/2026")
        self.entrada_hora_cita = self.crear_campo(formulario, "Hora")
        self.entrada_hora_cita.insert(0, "10:30")
        self.entrada_motivo_cita = self.crear_campo(formulario, "Motivo")
        self.combo_estado_cita = self.crear_combo(
            formulario,
            "Estado",
            valores=["Pendiente", "Atendida", "Cancelada"],
        )
        self.combo_estado_cita.current(0)
        self.crear_boton_accion(formulario, "Registrar cita", self.registrar_cita)

        self.crear_barra_lista(
            listado,
            [
                ("Editar/reprogramar", self.editar_cita, self.COLORES["azul"]),
                ("Eliminar", self.eliminar_cita, self.COLORES["advertencia"]),
                ("Filtrar", self.filtrar_citas_dialogo, self.COLORES["verde"]),
                ("Todas", self.mostrar_todas_citas, self.COLORES["gris"]),
            ],
        )
        self.lista_citas = self.crear_listbox(listado, ancho=58, alto=24)

    def crear_tab_pagos(self):
        formulario = self.crear_panel(self.tab_pagos, "Nuevo pago", 0, ancho=270)
        listado = self.crear_panel(self.tab_pagos, "Pagos registrados", 1, ancho=470)

        self.entrada_concepto_pago = self.crear_campo(formulario, "Concepto del pago")
        self.entrada_monto_pago = self.crear_campo(formulario, "Monto")
        self.combo_metodo_pago = self.crear_combo(
            formulario,
            "Método de pago",
            valores=["Efectivo", "Yape", "Plin", "POS", "Transferencia"],
        )
        self.combo_estado_pago = self.crear_combo(
            formulario,
            "Estado",
            valores=["Pendiente", "Confirmado", "Anulado"],
        )
        self.crear_boton_accion(formulario, "Registrar pago", self.registrar_pago)

        self.etiqueta_total_pagos = tk.Label(
            listado,
            text="Total confirmado: S/ 0.00",
            bg=self.COLORES["panel"],
            fg=self.COLORES["verde"],
            font=("Segoe UI", 12, "bold"),
        )
        self.etiqueta_total_pagos.pack(anchor="w", padx=16, pady=(0, 10))

        self.crear_barra_lista(
            listado,
            [
                ("Editar", self.editar_pago, self.COLORES["azul"]),
                ("Eliminar", self.eliminar_pago, self.COLORES["advertencia"]),
                ("Filtrar", self.filtrar_pagos_dialogo, self.COLORES["verde"]),
                ("Todos", self.mostrar_todos_pagos, self.COLORES["gris"]),
            ],
        )
        self.lista_pagos = self.crear_listbox(listado, ancho=58, alto=21)

    def crear_tab_atenciones(self):
        formulario = self.crear_panel(self.tab_atenciones, "Nueva consulta", 0, ancho=270)
        listado = self.crear_panel(self.tab_atenciones, "Consultas registradas", 1, ancho=470)

        self.combo_mascotas_atencion = self.crear_combo(formulario, "Mascota", ancho=25)
        self.entrada_fecha_atencion = self.crear_campo(formulario, "Fecha de consulta")
        self.entrada_fecha_atencion.insert(0, "06/10/2026")
        self.entrada_diagnostico = self.crear_campo(formulario, "Diagnóstico")
        self.entrada_tratamiento = self.crear_campo(formulario, "Tratamiento")
        self.entrada_vacuna = self.crear_campo(formulario, "Vacuna aplicada")
        self.crear_boton_accion(formulario, "Registrar consulta", self.registrar_atencion)

        self.crear_barra_lista(
            listado,
            [
                ("Editar", self.editar_atencion, self.COLORES["azul"]),
                ("Eliminar", self.eliminar_atencion, self.COLORES["advertencia"]),
                ("Filtrar", self.filtrar_atenciones_dialogo, self.COLORES["verde"]),
                ("Todas", self.mostrar_todas_atenciones, self.COLORES["gris"]),
            ],
        )
        self.lista_atenciones = self.crear_listbox(listado, ancho=58, alto=24)

    def crear_tab_reportes(self):
        self.tab_reportes.grid_columnconfigure(0, weight=1)
        panel = self.crear_panel(self.tab_reportes, "Reporte diario de consultas e ingresos", 0, ancho=740)

        botones = tk.Frame(panel, bg=self.COLORES["panel"])
        botones.pack(fill="x", padx=16, pady=(0, 12))

        tk.Button(
            botones,
            text="Generar reporte diario",
            command=self.generar_reporte_diario,
            bg=self.COLORES["verde"],
            fg="#ffffff",
            activebackground=self.COLORES["azul"],
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            botones,
            text="Exportar reporte a TXT",
            command=self.exportar_reporte_diario,
            bg=self.COLORES["azul"],
            fg="#ffffff",
            activebackground=self.COLORES["verde"],
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            botones,
            text="Exportar datos CSV",
            command=self.exportar_datos_csv,
            bg=self.COLORES["advertencia"],
            fg="#ffffff",
            activebackground=self.COLORES["azul"],
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(8, 0))

        tk.Button(
            botones,
            text="Importar propietarios CSV",
            command=self.importar_propietarios_csv,
            bg=self.COLORES["gris"],
            fg="#ffffff",
            activebackground=self.COLORES["azul"],
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(8, 0))

        self.texto_reporte = self.crear_texto(panel, ancho=80, alto=24)

    def crear_tab_recordatorios(self):
        self.tab_recordatorios.grid_columnconfigure(0, weight=1)
        panel = self.crear_panel(self.tab_recordatorios, "Recordatorio para WhatsApp", 0, ancho=740)

        self.combo_citas_recordatorio = self.crear_combo(panel, "Selecciona una cita", ancho=70)
        self.crear_boton_accion(panel, "Generar mensaje", self.generar_recordatorio)
        self.texto_recordatorio = self.crear_texto(panel, ancho=80, alto=15)

        tk.Label(
            panel,
            text="El sistema solo prepara el mensaje. El envío se realiza manualmente.",
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "italic"),
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def crear_tab_historial(self):
        self.tab_historial.grid_columnconfigure(0, weight=1)
        panel = self.crear_panel(self.tab_historial, "Historial clínico ordenado por mascota", 0, ancho=740)

        self.combo_mascotas_historial = self.crear_combo(panel, "Selecciona una mascota", ancho=45)
        self.crear_boton_accion(panel, "Generar historial", self.generar_historial_mascota)
        self.texto_historial = self.crear_texto(panel, ancho=80, alto=20)

    def registrar_propietario(self):
        if self.indice_propietario_editando is not None:
            messagebox.showwarning(
                "Edición activa",
                "Guarda los cambios o cancela la edición antes de registrar otro propietario.",
            )
            return

        nombre = self.entrada_nombre_propietario.get().strip()
        dni = self.entrada_dni_propietario.get().strip()
        telefono = self.entrada_telefono_propietario.get().strip()

        if nombre == "" or dni == "" or telefono == "":
            messagebox.showwarning("Datos incompletos", "Completa nombre, DNI y teléfono.")
            return

        if not dni.isdigit() or len(dni) != 8:
            messagebox.showerror("DNI inválido", "El DNI debe tener 8 números.")
            return

        try:
            self.servicio.registrar_propietario(nombre, dni, telefono)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return

        self.limpiar_formulario_propietario()

        self.actualizar_todo()
        messagebox.showinfo("Registro exitoso", "Propietario registrado correctamente.")

    def cargar_propietario_para_editar(self):
        seleccion = self.lista_propietarios.curselection()

        if len(seleccion) == 0:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona un propietario de la lista para editar.",
            )
            return

        posicion = seleccion[0]
        if posicion >= len(self.indices_propietarios):
            messagebox.showwarning("Selección inválida", "Actualiza la lista e inténtalo nuevamente.")
            return
        indice = self.indices_propietarios[posicion]
        propietario = self.servicio.listar_propietarios()[indice]

        self.entrada_nombre_propietario.delete(0, tk.END)
        self.entrada_dni_propietario.delete(0, tk.END)
        self.entrada_telefono_propietario.delete(0, tk.END)

        self.entrada_nombre_propietario.insert(0, propietario.nombre)
        self.entrada_dni_propietario.insert(0, propietario.dni)
        self.entrada_telefono_propietario.insert(0, propietario.telefono)

        self.indice_propietario_editando = indice
        self.etiqueta_modo_propietario.config(
            text=f"Modo: editando a {propietario.nombre}",
            fg=self.COLORES["azul"],
        )

    def guardar_cambios_propietario(self):
        if self.indice_propietario_editando is None:
            messagebox.showwarning(
                "Sin edición",
                "Primero selecciona un propietario y pulsa Cargar seleccionado.",
            )
            return

        nombre = self.entrada_nombre_propietario.get().strip()
        dni = self.entrada_dni_propietario.get().strip()
        telefono = self.entrada_telefono_propietario.get().strip()

        try:
            self.servicio.actualizar_propietario(
                self.indice_propietario_editando,
                nombre,
                dni,
                telefono,
            )
        except ValueError as error:
            messagebox.showerror("No se pudo actualizar", str(error))
            return

        self.limpiar_formulario_propietario()
        self.actualizar_todo()
        messagebox.showinfo("Datos actualizados", "Propietario actualizado correctamente.")

    def limpiar_formulario_propietario(self):
        self.indice_propietario_editando = None
        self.entrada_nombre_propietario.delete(0, tk.END)
        self.entrada_dni_propietario.delete(0, tk.END)
        self.entrada_telefono_propietario.delete(0, tk.END)
        self.etiqueta_modo_propietario.config(
            text="Modo: nuevo propietario",
            fg=self.COLORES["gris"],
        )

    def registrar_mascota(self):
        nombre = self.entrada_nombre_mascota.get().strip()
        especie = self.entrada_especie_mascota.get().strip()
        edad = self.entrada_edad_mascota.get().strip()
        sexo = self.combo_sexo_mascota.get()
        esterilizado = self.combo_esterilizado_mascota.get()
        indice_propietario = self.combo_propietarios.current()

        if nombre == "" or especie == "" or edad == "":
            messagebox.showwarning(
                "Datos incompletos",
                "Completa todos los datos de la mascota.",
            )
            return

        if indice_propietario == -1:
            messagebox.showwarning("Sin propietario", "Primero selecciona un propietario.")
            return

        propietarios = self.servicio.listar_propietarios()
        propietario = propietarios[indice_propietario]

        try:
            self.servicio.registrar_mascota(
                nombre,
                especie,
                edad,
                propietario,
                sexo,
                esterilizado,
            )
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return

        self.entrada_nombre_mascota.delete(0, tk.END)
        self.entrada_especie_mascota.delete(0, tk.END)
        self.entrada_edad_mascota.delete(0, tk.END)
        self.combo_sexo_mascota.current(0)
        self.combo_esterilizado_mascota.current(0)

        self.actualizar_todo()
        messagebox.showinfo("Registro exitoso", "Mascota registrada correctamente.")

    def registrar_cita(self):
        indice_mascota = self.combo_mascotas.current()
        fecha = self.entrada_fecha_cita.get().strip()
        hora = self.entrada_hora_cita.get().strip()
        motivo = self.entrada_motivo_cita.get().strip()
        estado = self.combo_estado_cita.get()

        if indice_mascota == -1:
            messagebox.showwarning("Sin mascota", "Primero selecciona una mascota.")
            return

        if fecha == "" or hora == "" or motivo == "" or estado == "":
            messagebox.showwarning("Datos incompletos", "Completa fecha, hora y motivo.")
            return

        mascotas = self.servicio.listar_mascotas()
        mascota = mascotas[indice_mascota]

        try:
            self.servicio.registrar_cita(mascota, fecha, hora, motivo, estado)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return

        self.entrada_fecha_cita.delete(0, tk.END)
        self.entrada_hora_cita.delete(0, tk.END)
        self.entrada_motivo_cita.delete(0, tk.END)
        self.combo_estado_cita.current(0)

        self.actualizar_todo()
        messagebox.showinfo("Registro exitoso", "Cita registrada correctamente.")

    def registrar_pago(self):
        concepto = self.entrada_concepto_pago.get().strip()
        monto = self.entrada_monto_pago.get().strip()
        metodo = self.combo_metodo_pago.get()
        estado = self.combo_estado_pago.get()

        if concepto == "" or monto == "" or metodo == "" or estado == "":
            messagebox.showwarning(
                "Datos incompletos",
                "Completa todos los datos del pago.",
            )
            return

        try:
            self.servicio.registrar_pago(concepto, monto, metodo, estado)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return

        self.entrada_concepto_pago.delete(0, tk.END)
        self.entrada_monto_pago.delete(0, tk.END)
        self.combo_metodo_pago.set("")
        self.combo_estado_pago.set("")

        self.actualizar_todo()
        messagebox.showinfo("Registro exitoso", "Pago registrado correctamente.")

    def registrar_atencion(self):
        indice_mascota = self.combo_mascotas_atencion.current()
        fecha = self.entrada_fecha_atencion.get().strip()
        diagnostico = self.entrada_diagnostico.get().strip()
        tratamiento = self.entrada_tratamiento.get().strip()
        vacuna = self.entrada_vacuna.get().strip()

        if indice_mascota == -1:
            messagebox.showwarning("Sin mascota", "Primero selecciona una mascota.")
            return

        if fecha == "" or diagnostico == "" or tratamiento == "" or vacuna == "":
            messagebox.showwarning(
                "Datos incompletos",
                "Completa todos los datos de la consulta.",
            )
            return

        mascotas = self.servicio.listar_mascotas()
        mascota = mascotas[indice_mascota]

        try:
            self.servicio.registrar_atencion(
                mascota,
                fecha,
                diagnostico,
                tratamiento,
                vacuna,
            )
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return

        self.entrada_fecha_atencion.delete(0, tk.END)
        self.entrada_diagnostico.delete(0, tk.END)
        self.entrada_tratamiento.delete(0, tk.END)
        self.entrada_vacuna.delete(0, tk.END)

        self.actualizar_todo()
        messagebox.showinfo(
            "Registro exitoso",
            "Consulta registrada correctamente.",
        )

    def generar_reporte_diario(self):
        reporte = self.servicio.generar_reporte_diario()

        self.texto_reporte.delete("1.0", tk.END)
        self.texto_reporte.insert(tk.END, reporte)

    def exportar_reporte_diario(self):
        ruta_reporte = self.servicio.exportar_reporte_diario()

        messagebox.showinfo(
            "Reporte exportado",
            f"El reporte fue guardado en:\n{ruta_reporte}",
        )

    def generar_recordatorio(self):
        indice_cita = self.combo_citas_recordatorio.current()

        if indice_cita == -1:
            messagebox.showwarning("Sin cita", "Primero selecciona una cita.")
            return

        mensaje = self.servicio.preparar_recordatorio_cita(indice_cita)

        self.texto_recordatorio.delete("1.0", tk.END)
        self.texto_recordatorio.insert(tk.END, mensaje)

    def generar_historial_mascota(self):
        indice_mascota = self.combo_mascotas_historial.current()

        if indice_mascota == -1:
            messagebox.showwarning("Sin mascota", "Primero selecciona una mascota.")
            return

        historial = self.servicio.generar_historial_mascota(indice_mascota)

        self.texto_historial.delete("1.0", tk.END)
        self.texto_historial.insert(tk.END, historial)

    def actualizar_lista_propietarios(self, propietarios=None):
        self.lista_propietarios.delete(0, tk.END)
        propietarios = (
            self.servicio.listar_propietarios()
            if propietarios is None
            else propietarios
        )
        self.indices_propietarios = [
            self.servicio.listar_propietarios().index(propietario)
            for propietario in propietarios
        ]
        for propietario in propietarios:
            self.lista_propietarios.insert(tk.END, str(propietario))

        todos = self.servicio.listar_propietarios()
        nombres = [propietario.nombre for propietario in todos]
        self.combo_propietarios["values"] = nombres
        if nombres and self.combo_propietarios.current() == -1:
            self.combo_propietarios.current(0)
        if not nombres:
            self.combo_propietarios.set("")

    def actualizar_lista_mascotas(self, mascotas=None):
        self.lista_mascotas.delete(0, tk.END)
        mascotas = (
            self.servicio.listar_mascotas() if mascotas is None else mascotas
        )
        todos = self.servicio.listar_mascotas()
        self.indices_mascotas = [todos.index(mascota) for mascota in mascotas]
        for mascota in mascotas:
            self.lista_mascotas.insert(tk.END, str(mascota))

        nombres_mascotas = [mascota.nombre for mascota in todos]
        self.combo_mascotas["values"] = nombres_mascotas
        self.combo_mascotas_atencion["values"] = nombres_mascotas
        self.combo_mascotas_historial["values"] = nombres_mascotas
        for combo in (
            self.combo_mascotas,
            self.combo_mascotas_atencion,
            self.combo_mascotas_historial,
        ):
            if nombres_mascotas and combo.current() == -1:
                combo.current(0)
            if not nombres_mascotas:
                combo.set("")

    def actualizar_lista_citas(self, citas=None):
        self.lista_citas.delete(0, tk.END)
        citas = self.servicio.listar_citas() if citas is None else citas
        todos = self.servicio.listar_citas()
        self.indices_citas = [todos.index(cita) for cita in citas]
        citas_texto = []
        for cita in citas:
            texto_cita = str(cita)
            self.lista_citas.insert(tk.END, texto_cita)
            citas_texto.append(texto_cita)

        todas_las_citas = [str(cita) for cita in todos]
        self.combo_citas_recordatorio["values"] = todas_las_citas
        if todas_las_citas and self.combo_citas_recordatorio.current() == -1:
            self.combo_citas_recordatorio.current(0)
        if not todas_las_citas:
            self.combo_citas_recordatorio.set("")

    def actualizar_lista_pagos(self, pagos=None):
        self.lista_pagos.delete(0, tk.END)
        pagos = self.servicio.listar_pagos() if pagos is None else pagos
        todos = self.servicio.listar_pagos()
        self.indices_pagos = [todos.index(pago) for pago in pagos]
        for pago in pagos:
            self.lista_pagos.insert(tk.END, str(pago))

        total = self.servicio.calcular_total_confirmado()
        self.etiqueta_total_pagos.config(text=f"Total confirmado: S/ {total:.2f}")

    def actualizar_lista_atenciones(self, atenciones=None):
        self.lista_atenciones.delete(0, tk.END)
        atenciones = (
            self.servicio.listar_atenciones() if atenciones is None else atenciones
        )
        todos = self.servicio.listar_atenciones()
        self.indices_atenciones = [todos.index(atencion) for atencion in atenciones]
        for atencion in atenciones:
            self.lista_atenciones.insert(tk.END, str(atencion))

    def _indice_seleccionado(self, lista, indices, mensaje):
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Sin selección", mensaje)
            return None
        posicion = seleccion[0]
        if posicion >= len(indices):
            messagebox.showwarning("Selección inválida", "Actualiza la lista e inténtalo nuevamente.")
            return None
        return indices[posicion]

    def filtrar_propietarios_dialogo(self):
        termino = simpledialog.askstring(
            "Buscar propietario",
            "Escribe nombre, DNI o teléfono:",
            parent=self.ventana,
        )
        if termino is None:
            return
        self.actualizar_lista_propietarios(self.servicio.buscar_propietarios(termino))

    def mostrar_todos_propietarios(self):
        self.actualizar_lista_propietarios()

    def eliminar_propietario(self):
        indice = self._indice_seleccionado(
            self.lista_propietarios,
            self.indices_propietarios,
            "Selecciona un propietario para eliminar.",
        )
        if indice is None:
            return
        propietario = self.servicio.listar_propietarios()[indice]
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar a {propietario.nombre}?",
        ):
            return
        try:
            self.servicio.eliminar_propietario(indice)
        except ValueError as error:
            messagebox.showerror("No se puede eliminar", str(error))
            return
        self.actualizar_todo()

    def filtrar_mascotas_dialogo(self):
        termino = simpledialog.askstring(
            "Buscar mascota",
            "Escribe nombre, especie o propietario:",
            parent=self.ventana,
        )
        if termino is None:
            return
        self.actualizar_lista_mascotas(self.servicio.buscar_mascotas(termino))

    def mostrar_todas_mascotas(self):
        self.actualizar_lista_mascotas()

    def eliminar_mascota(self):
        indice = self._indice_seleccionado(
            self.lista_mascotas,
            self.indices_mascotas,
            "Selecciona una mascota para eliminar.",
        )
        if indice is None:
            return
        mascota = self.servicio.listar_mascotas()[indice]
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar a {mascota.nombre} y sus citas y consultas vinculadas?",
        ):
            return
        self.servicio.eliminar_mascota(indice)
        self.actualizar_todo()

    def filtrar_citas_dialogo(self):
        estado = simpledialog.askstring(
            "Filtrar citas",
            "Estado (Pendiente, Atendida, Cancelada) o déjalo vacío:",
            parent=self.ventana,
        )
        if estado is None:
            return
        estado = estado.strip().title()
        if estado not in ("", "Pendiente", "Atendida", "Cancelada"):
            messagebox.showwarning("Estado inválido", "Usa Pendiente, Atendida o Cancelada.")
            return
        fecha = simpledialog.askstring(
            "Filtrar citas",
            "Fecha exacta o parte de la fecha (opcional):",
            parent=self.ventana,
        )
        if fecha is None:
            return
        self.actualizar_lista_citas(self.servicio.filtrar_citas(estado, fecha.strip()))

    def mostrar_todas_citas(self):
        self.actualizar_lista_citas()

    def eliminar_cita(self):
        indice = self._indice_seleccionado(
            self.lista_citas,
            self.indices_citas,
            "Selecciona una cita para eliminar.",
        )
        if indice is None:
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Eliminar la cita seleccionada?"):
            return
        self.servicio.eliminar_cita(indice)
        self.actualizar_todo()

    def filtrar_pagos_dialogo(self):
        metodo = simpledialog.askstring(
            "Filtrar pagos",
            "Método (Efectivo, Yape, Plin, POS, Transferencia) o vacío:",
            parent=self.ventana,
        )
        if metodo is None:
            return
        estado = simpledialog.askstring(
            "Filtrar pagos",
            "Estado (Pendiente, Confirmado, Anulado) o vacío:",
            parent=self.ventana,
        )
        if estado is None:
            return
        self.actualizar_lista_pagos(
            self.servicio.filtrar_pagos(metodo.strip(), estado.strip().title())
        )

    def mostrar_todos_pagos(self):
        self.actualizar_lista_pagos()

    def eliminar_pago(self):
        indice = self._indice_seleccionado(
            self.lista_pagos,
            self.indices_pagos,
            "Selecciona un pago para eliminar.",
        )
        if indice is None:
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Eliminar el pago seleccionado?"):
            return
        self.servicio.eliminar_pago(indice)
        self.actualizar_todo()

    def filtrar_atenciones_dialogo(self):
        mascota = simpledialog.askstring(
            "Filtrar consultas",
            "Nombre de mascota o vacío:",
            parent=self.ventana,
        )
        if mascota is None:
            return
        vacuna = simpledialog.askstring(
            "Filtrar consultas",
            "Vacuna o vacío:",
            parent=self.ventana,
        )
        if vacuna is None:
            return
        desde = simpledialog.askstring(
            "Filtrar consultas",
            "Fecha desde (dd/mm/aaaa) o vacío:",
            parent=self.ventana,
        )
        if desde is None:
            return
        hasta = simpledialog.askstring(
            "Filtrar consultas",
            "Fecha hasta (dd/mm/aaaa) o vacío:",
            parent=self.ventana,
        )
        if hasta is None:
            return
        self.actualizar_lista_atenciones(
            self.servicio.filtrar_atenciones(
                mascota,
                vacuna,
                desde,
                hasta,
            )
        )

    def mostrar_todas_atenciones(self):
        self.actualizar_lista_atenciones()

    def eliminar_atencion(self):
        indice = self._indice_seleccionado(
            self.lista_atenciones,
            self.indices_atenciones,
            "Selecciona una consulta para eliminar.",
        )
        if indice is None:
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Eliminar la consulta seleccionada?"):
            return
        self.servicio.eliminar_atencion(indice)
        self.actualizar_todo()

    def _entrada_dialogo(self, padre, texto, valor="", ancho=30):
        tk.Label(
            padre,
            text=texto,
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(7, 2))
        entrada = tk.Entry(padre, width=ancho, font=("Segoe UI", 10))
        entrada.pack(anchor="w", padx=16, ipady=4)
        entrada.insert(0, str(valor or ""))
        return entrada

    def _combo_dialogo(self, padre, texto, valores, indice=0):
        tk.Label(
            padre,
            text=texto,
            bg=self.COLORES["panel"],
            fg=self.COLORES["gris"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(7, 2))
        combo = ttk.Combobox(padre, state="readonly", values=valores, width=27)
        combo.pack(anchor="w", padx=16, ipady=3)
        if valores:
            combo.current(max(0, min(indice, len(valores) - 1)))
        return combo

    def _ventana_edicion(self, titulo):
        ventana = tk.Toplevel(self.ventana)
        ventana.title(titulo)
        ventana.configure(bg=self.COLORES["panel"])
        ventana.resizable(False, False)
        ventana.transient(self.ventana)
        ventana.grab_set()
        return ventana

    def editar_mascota(self):
        indice = self._indice_seleccionado(
            self.lista_mascotas,
            self.indices_mascotas,
            "Selecciona una mascota para editar.",
        )
        if indice is None:
            return
        mascota = self.servicio.listar_mascotas()[indice]
        ventana = self._ventana_edicion("Editar mascota")
        ventana.geometry("360x450")
        nombre = self._entrada_dialogo(ventana, "Nombre", mascota.nombre)
        especie = self._entrada_dialogo(ventana, "Especie", mascota.especie)
        edad = self._entrada_dialogo(ventana, "Edad", mascota.edad)
        opciones_sexo = ["No especificado", "Macho", "Hembra"]
        opciones_esterilizado = ["No especificado", "Sí", "No"]
        sexo = self._combo_dialogo(
            ventana,
            "Sexo",
            opciones_sexo,
            opciones_sexo.index(mascota.sexo)
            if mascota.sexo in opciones_sexo
            else 0,
        )
        esterilizado = self._combo_dialogo(
            ventana,
            "Esterilizado",
            opciones_esterilizado,
            opciones_esterilizado.index(mascota.esterilizado)
            if mascota.esterilizado in opciones_esterilizado
            else 0,
        )
        propietarios = self.servicio.listar_propietarios()
        propietario_actual = propietarios.index(mascota.propietario)
        propietario = self._combo_dialogo(
            ventana,
            "Propietario",
            [item.nombre for item in propietarios],
            propietario_actual,
        )

        def guardar():
            try:
                self.servicio.actualizar_mascota(
                    indice,
                    nombre.get(),
                    especie.get(),
                    edad.get(),
                    propietarios[propietario.current()],
                    sexo.get(),
                    esterilizado.get(),
                )
            except (ValueError, IndexError) as error:
                messagebox.showerror("No se pudo actualizar", str(error), parent=ventana)
                return
            ventana.destroy()
            self.actualizar_todo()

        tk.Button(
            ventana,
            text="Guardar cambios",
            command=guardar,
            bg=self.COLORES["verde"],
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7,
        ).pack(anchor="w", padx=16, pady=16)

    def editar_cita(self):
        indice = self._indice_seleccionado(
            self.lista_citas,
            self.indices_citas,
            "Selecciona una cita para editar o reprogramar.",
        )
        if indice is None:
            return
        cita = self.servicio.listar_citas()[indice]
        ventana = self._ventana_edicion("Editar o reprogramar cita")
        ventana.geometry("350x390")
        mascotas = self.servicio.listar_mascotas()
        mascota = self._combo_dialogo(
            ventana,
            "Mascota",
            [item.nombre for item in mascotas],
            mascotas.index(cita.mascota),
        )
        fecha = self._entrada_dialogo(ventana, "Fecha", cita.fecha)
        hora = self._entrada_dialogo(ventana, "Hora", cita.hora)
        motivo = self._entrada_dialogo(ventana, "Motivo", cita.motivo)
        estados = ["Pendiente", "Atendida", "Cancelada"]
        estado = self._combo_dialogo(
            ventana,
            "Estado",
            estados,
            estados.index(cita.estado) if cita.estado in estados else 0,
        )

        def guardar():
            try:
                self.servicio.actualizar_cita(
                    indice,
                    mascotas[mascota.current()],
                    fecha.get(),
                    hora.get(),
                    motivo.get(),
                    estado.get(),
                )
            except (ValueError, IndexError) as error:
                messagebox.showerror("No se pudo actualizar", str(error), parent=ventana)
                return
            ventana.destroy()
            self.actualizar_todo()

        tk.Button(
            ventana,
            text="Guardar cita",
            command=guardar,
            bg=self.COLORES["verde"],
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7,
        ).pack(anchor="w", padx=16, pady=16)

    def editar_pago(self):
        indice = self._indice_seleccionado(
            self.lista_pagos,
            self.indices_pagos,
            "Selecciona un pago para editar.",
        )
        if indice is None:
            return
        pago = self.servicio.listar_pagos()[indice]
        ventana = self._ventana_edicion("Editar pago")
        ventana.geometry("340x350")
        concepto = self._entrada_dialogo(ventana, "Concepto", pago.concepto)
        monto = self._entrada_dialogo(ventana, "Monto", pago.monto)
        metodos = ["Efectivo", "Yape", "Plin", "POS", "Transferencia"]
        metodo = self._combo_dialogo(
            ventana,
            "Método",
            metodos,
            metodos.index(pago.metodo) if pago.metodo in metodos else 0,
        )
        estados = ["Pendiente", "Confirmado", "Anulado"]
        estado = self._combo_dialogo(
            ventana,
            "Estado",
            estados,
            estados.index(pago.estado) if pago.estado in estados else 0,
        )

        def guardar():
            try:
                self.servicio.actualizar_pago(
                    indice,
                    concepto.get(),
                    monto.get(),
                    metodo.get(),
                    estado.get(),
                )
            except (ValueError, IndexError) as error:
                messagebox.showerror("No se pudo actualizar", str(error), parent=ventana)
                return
            ventana.destroy()
            self.actualizar_todo()

        tk.Button(
            ventana,
            text="Guardar pago",
            command=guardar,
            bg=self.COLORES["verde"],
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7,
        ).pack(anchor="w", padx=16, pady=16)

    def editar_atencion(self):
        indice = self._indice_seleccionado(
            self.lista_atenciones,
            self.indices_atenciones,
            "Selecciona una consulta para editar.",
        )
        if indice is None:
            return
        atencion = self.servicio.listar_atenciones()[indice]
        ventana = self._ventana_edicion("Editar consulta")
        ventana.geometry("350x410")
        mascotas = self.servicio.listar_mascotas()
        mascota = self._combo_dialogo(
            ventana,
            "Mascota",
            [item.nombre for item in mascotas],
            mascotas.index(atencion.mascota),
        )
        fecha = self._entrada_dialogo(ventana, "Fecha", atencion.fecha)
        diagnostico = self._entrada_dialogo(ventana, "Diagnóstico", atencion.diagnostico)
        tratamiento = self._entrada_dialogo(ventana, "Tratamiento", atencion.tratamiento)
        vacuna = self._entrada_dialogo(ventana, "Vacuna", atencion.vacuna)

        def guardar():
            try:
                self.servicio.actualizar_atencion(
                    indice,
                    mascotas[mascota.current()],
                    fecha.get(),
                    diagnostico.get(),
                    tratamiento.get(),
                    vacuna.get(),
                )
            except (ValueError, IndexError) as error:
                messagebox.showerror("No se pudo actualizar", str(error), parent=ventana)
                return
            ventana.destroy()
            self.actualizar_todo()

        tk.Button(
            ventana,
            text="Guardar consulta",
            command=guardar,
            bg=self.COLORES["verde"],
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7,
        ).pack(anchor="w", padx=16, pady=16)

    def exportar_datos_csv(self):
        carpeta, _ = self.servicio.exportar_datos_csv()
        messagebox.showinfo(
            "Exportación completada",
            f"Los archivos CSV fueron guardados en:\n{carpeta}",
        )

    def importar_propietarios_csv(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un CSV de propietarios",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            cantidad = self.servicio.importar_propietarios_csv(ruta)
        except (OSError, ValueError) as error:
            messagebox.showerror("No se pudo importar", str(error))
            return
        self.actualizar_todo()
        messagebox.showinfo("Importación completada", f"Propietarios agregados: {cantidad}")

    def actualizar_dashboard(self):
        propietarios = len(self.servicio.listar_propietarios())
        mascotas = len(self.servicio.listar_mascotas())
        citas = len(self.servicio.listar_citas())
        atenciones = len(self.servicio.listar_atenciones())
        citas_pendientes = len(
            [
                cita
                for cita in self.servicio.listar_citas()
                if cita.estado == "Pendiente"
            ]
        )
        total = self.servicio.calcular_total_confirmado()

        self.valor_propietarios.config(text=str(propietarios))
        self.valor_mascotas.config(text=str(mascotas))
        self.valor_citas.config(text=str(citas))
        self.valor_pagos_inicio.config(text=f"S/ {total:.2f}")
        self.valor_atenciones_inicio.config(text=str(atenciones))
        self.valor_pendientes_inicio.config(text=str(citas_pendientes))

    def actualizar_todo(self):
        self.actualizar_lista_propietarios()
        self.actualizar_lista_mascotas()
        self.actualizar_lista_citas()
        self.actualizar_lista_pagos()
        self.actualizar_lista_atenciones()
        self.actualizar_dashboard()

    def ejecutar(self):
        self.ventana.mainloop()


def iniciar_app():
    app = AppVeterinaria()
    app.ejecutar()
