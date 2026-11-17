from datetime import datetime
from typing import List, Optional


# ==========================================
# UTILIDADES DE VALIDACIÓN Y ENTRADA
# ==========================================

def leer_texto(mensaje: str, obligatorio: bool = True, longitud_exacta: Optional[int] = None) -> Optional[str]:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            if obligatorio:
                print("❌ Error: Este campo es obligatorio.")
                continue
            return None
        if longitud_exacta and len(valor) != longitud_exacta:
            print(f"❌ Error: Debe tener exactamente {longitud_exacta} caracteres.")
            continue
        return valor


def leer_entero(mensaje: str, minimo: int = 1) -> int:
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"❌ Error: El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("❌ Error: Introduce un número entero válido.")


def leer_real(mensaje: str, minimo: float = 0.0) -> float:
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
            if valor < minimo:
                print(f"❌ Error: El valor debe ser mayor o igual a {minimo}.")
                continue
            return round(valor, 2)
        except ValueError:
            print("❌ Error: Introduce un número decimal válido.")


def leer_fecha(mensaje: str) -> datetime:
    """Pide una fecha manualmente por pantalla (sin usar la fecha del sistema)."""
    while True:
        texto = input(f"{mensaje} (DD/MM/AAAA): ").strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            print("❌ Error: Formato de fecha incorrecto. Usa DD/MM/AAAA (ej. 15/11/2026).")


def leer_mes_anio(mensaje: str) -> tuple[int, int]:
    """Pide mes y año manualmente para estadísticas."""
    while True:
        texto = input(f"{mensaje} (MM/AAAA): ").strip()
        try:
            fecha = datetime.strptime(texto, "%m/%Y")
            return fecha.month, fecha.year
        except ValueError:
            print("❌ Error: Formato incorrecto. Usa MM/AAAA (ej. 11/2026).")


# ==========================================
# CLASES DEL MODELO DE DOMINIO
# ==========================================

class Videoclub:
    _contador = 1

    def __init__(self, gerente: str, ciudad: str, calle: str, codigo_postal: str):
        self.__codigo = Videoclub._contador
        Videoclub._contador += 1
        self.gerente = gerente
        self.ciudad = ciudad
        self.calle = calle
        self.codigo_postal = codigo_postal

    @property
    def codigo(self) -> int:
        return self.__codigo

    def __str__(self) -> str:
        return f"[VC-{self.codigo}] {self.ciudad} - C/ {self.calle} ({self.codigo_postal}) | Gerente: {self.gerente}"


class Pelicula:
    _contador = 1

    def __init__(self, nombre: str, fecha_estreno: datetime, precio_alquiler: float,
                 videoclub: Videoclub, director: Optional[str] = None):
        self.__codigo = Pelicula._contador
        Pelicula._contador += 1
        self.nombre = nombre
        self.director = director
        self.fecha_estreno = fecha_estreno
        self.precio_alquiler = precio_alquiler
        self.videoclub = videoclub

    @property
    def codigo(self) -> int:
        return self.__codigo

    def __str__(self) -> str:
        dir_str = self.director if self.director else "No especificado"
        estreno_str = self.fecha_estreno.strftime("%d/%m/%Y")
        return (f"[PEL-{self.codigo}] '{self.nombre}' | Dir: {dir_str} | "
                f"Estreno: {estreno_str} | Precio: {self.precio_alquiler:.2f}€ | "
                f"Videoclub: {self.videoclub.ciudad} (VC-{self.videoclub.codigo})")


class Socio:
    _contador = 1

    def __init__(self, nombre: str, edad: int):
        self.__codigo = Socio._contador
        Socio._contador += 1
        self.nombre = nombre
        self.edad = edad

    @property
    def codigo(self) -> int:
        return self.__codigo

    def __str__(self) -> str:
        return f"[SOC-{self.codigo}] {self.nombre} ({self.edad} años)"


class Alquiler:
    _contador = 1

    def __init__(self, socio: Socio, peliculas: List[Pelicula],
                 fecha_recogida: datetime, fecha_devolucion: datetime):
        self.__codigo = Alquiler._contador
        Alquiler._contador += 1
        self.socio = socio
        self.peliculas = peliculas
        # Fecha de recogida obligatoria y NO editable
        self.__fecha_recogida = fecha_recogida
        # Fecha de devolución obligatoria y editable
        self.__fecha_devolucion = fecha_devolucion

    @property
    def codigo(self) -> int:
        return self.__codigo

    @property
    def fecha_recogida(self) -> datetime:
        return self.__fecha_recogida

    @property
    def fecha_devolucion(self) -> datetime:
        return self.__fecha_devolucion

    def actualizar_fecha_devolucion(self, nueva_fecha: datetime, fecha_actual_manual: datetime) -> bool:
        """Solo permite poner una fecha posterior a la fecha actual introducida por el usuario."""
        if nueva_fecha <= fecha_actual_manual:
            return False
        self.__fecha_devolucion = nueva_fecha
        return True

    @property
    def total_a_pagar(self) -> float:
        """Atributo derivado: suma de los precios de las películas del alquiler."""
        return round(sum(p.precio_alquiler for p in self.peliculas), 2)

    def __str__(self) -> str:
        titulos = ", ".join(f"{p.nombre} (PEL-{p.codigo})" for p in self.peliculas)
        return (f"[ALQ-{self.codigo}] Socio: {self.socio.nombre} | "
                f"Recogida: {self.fecha_recogida.strftime('%d/%m/%Y')} | "
                f"Devolución: {self.fecha_devolucion.strftime('%d/%m/%Y')} | "
                f"Total: {self.total_a_pagar:.2f}€\n   Películas: {titulos}")


class EstadisticaSocio:
    _contador = 1

    def __init__(self, socio: Socio, mes: int, anio: int,
                 fecha_creacion: datetime, total_gastado: float):
        self.__codigo = EstadisticaSocio._contador
        EstadisticaSocio._contador += 1
        self.socio = socio
        self.mes = mes
        self.anio = anio
        # Obligatorio y NO editable
        self.__fecha_creacion = fecha_creacion
        # Obligatorio y derivado
        self.__total_gastado = round(total_gastado, 2)

    @property
    def codigo(self) -> int:
        return self.__codigo

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @property
    def total_gastado(self) -> float:
        return self.__total_gastado

    def __str__(self) -> str:
        return (f"[EST-{self.codigo}] Socio: {self.socio.nombre} (SOC-{self.socio.codigo}) | "
                f"Periodo: {self.mes:02d}/{self.anio} | "
                f"Creada el: {self.fecha_creacion.strftime('%d/%m/%Y')} | "
                f"Total gastado: {self.total_gastado:.2f}€")


class Administrador:
    _contador = 1

    def __init__(self, nombre: str):
        self.__codigo = Administrador._contador
        Administrador._contador += 1
        self.nombre = nombre

    @property
    def codigo(self) -> int:
        return self.__codigo

    def __str__(self) -> str:
        return f"[ADM-{self.codigo}] {self.nombre}"


# ==========================================
# GESTOR CENTRAL DE LA CADENA APPV
# ==========================================

class SistemaAPPV:
    def __init__(self):
        self.videoclubs: List[Videoclub] = []
        self.peliculas: List[Pelicula] = []
        self.socios: List[Socio] = []
        self.alquileres: List[Alquiler] = []
        self.estadisticas: List[EstadisticaSocio] = []
        self.administradores: List[Administrador] = []

    # --- Búsquedas auxiliares ---
    def buscar_videoclub(self, codigo: int) -> Optional[Videoclub]:
        return next((v for v in self.videoclubs if v.codigo == codigo), None)

    def buscar_pelicula(self, codigo: int) -> Optional[Pelicula]:
        return next((p for p in self.peliculas if p.codigo == codigo), None)

    def buscar_socio(self, codigo: int) -> Optional[Socio]:
        return next((s for s in self.socios if s.codigo == codigo), None)

    def buscar_alquiler(self, codigo: int) -> Optional[Alquiler]:
        return next((a for a in self.alquileres if a.codigo == codigo), None)

    def buscar_admin(self, codigo: int) -> Optional[Administrador]:
        return next((ad for ad in self.administradores if ad.codigo == codigo), None)

    # --- 1. Gestión de Videoclubs ---
    def alta_videoclub(self):
        print("\n--- ALTA DE VIDEOCLUB ---")
        gerente = leer_texto("Nombre del gerente: ")
        ciudad = leer_texto("Ciudad: ")
        calle = leer_texto("Calle: ")
        cp = leer_texto("Código postal (5 caracteres): ", obligatorio=True, longitud_exacta=5)
        vc = Videoclub(gerente, ciudad, calle, cp)
        self.videoclubs.append(vc)
        print(f"✅ Videoclub creado: {vc}")

    def editar_videoclub(self):
        if not self.videoclubs:
            print("⚠️ No hay videoclubs registrados.")
            return
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Código del videoclub a editar: "))
        if not vc:
            print("❌ Videoclub no encontrado.")
            return
        print("Dejar en blanco para mantener el valor actual:")
        nuevo_gerente = leer_texto(f"Gerente ({vc.gerente}): ", obligatorio=False)
        nueva_ciudad = leer_texto(f"Ciudad ({vc.ciudad}): ", obligatorio=False)
        nueva_calle = leer_texto(f"Calle ({vc.calle}): ", obligatorio=False)
        nuevo_cp = leer_texto(f"Código postal ({vc.codigo_postal}): ", obligatorio=False, longitud_exacta=5)

        if nuevo_gerente:
            vc.gerente = nuevo_gerente
        if nueva_ciudad:
            vc.ciudad = nueva_ciudad
        if nueva_calle:
            vc.calle = nueva_calle
        if nuevo_cp:
            vc.codigo_postal = nuevo_cp
        print(f"✅ Videoclub actualizado: {vc}")

    # --- 2. Gestión de Películas ---
    def alta_pelicula(self):
        if not self.videoclubs:
            print("⚠️ Debes crear al menos un videoclub antes de dar de alta películas.")
            return
        print("\n--- ALTA DE PELÍCULA ---")
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Código del videoclub al que asignar la película: "))
        if not vc:
            print("❌ Videoclub no encontrado.")
            return

        nombre = leer_texto("Nombre de la película: ")
        director = leer_texto("Director (opcional, Enter para omitir): ", obligatorio=False)
        estreno = leer_fecha("Fecha de estreno")
        precio = leer_real("Precio de alquiler (€): ", minimo=0.01)

        pelicula = Pelicula(nombre, estreno, precio, vc, director)
        self.peliculas.append(pelicula)
        print(f"✅ Película creada: {pelicula}")

    def editar_pelicula(self):
        if not self.peliculas:
            print("⚠️ No hay películas registradas.")
            return
        for p in self.peliculas:
            print(p)
        pel = self.buscar_pelicula(leer_entero("Código de la película a editar: "))
        if not pel:
            print("❌ Película no encontrada.")
            return

        print("Dejar en blanco para mantener el valor actual:")
        nuevo_nombre = leer_texto(f"Nombre ({pel.nombre}): ", obligatorio=False)
        nuevo_dir = leer_texto(f"Director ({pel.director or 'Ninguno'}): ", obligatorio=False)
        if input("¿Modificar fecha de estreno? (s/n): ").strip().lower() == "s":
            pel.fecha_estreno = leer_fecha("Nueva fecha de estreno")
        if input("¿Modificar precio de alquiler? (s/n): ").strip().lower() == "s":
            pel.precio_alquiler = leer_real("Nuevo precio (€): ", minimo=0.01)

        if nuevo_nombre:
            pel.nombre = nuevo_nombre
        if nuevo_dir:
            pel.director = nuevo_dir
        print(f"✅ Película actualizada: {pel}")

    # --- 3. Gestión de Socios ---
    def alta_socio(self):
        print("\n--- ALTA DE SOCIO ---")
        nombre = leer_texto("Nombre completo del socio: ")
        edad = leer_entero("Edad: ", minimo=1)
        socio = Socio(nombre, edad)
        self.socios.append(socio)
        print(f"✅ Socio registrado (válido en toda la cadena APPV): {socio}")

    def editar_socio(self):
        if not self.socios:
            print("⚠️ No hay socios registrados.")
            return
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio a editar: "))
        if not socio:
            print("❌ Socio no encontrado.")
            return
        nuevo_nombre = leer_texto(f"Nombre ({socio.nombre}): ", obligatorio=False)
        if input("¿Modificar edad? (s/n): ").strip().lower() == "s":
            socio.edad = leer_entero("Nueva edad: ", minimo=1)
        if nuevo_nombre:
            socio.nombre = nuevo_nombre
        print(f"✅ Socio actualizado: {socio}")

    # --- 4. Gestión de Alquileres ---
    def registrar_alquiler(self):
        if not self.socios or not self.peliculas:
            print("⚠️ Se necesita al menos un socio y una película en el sistema.")
            return
        print("\n--- NUEVO ALQUILER ---")
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio: "))
        if not socio:
            print("❌ Socio no encontrado.")
            return

        print("\nPelículas disponibles en la cadena:")
        for p in self.peliculas:
            print(p)

        seleccionadas: List[Pelicula] = []
        while True:
            cod_pel = leer_entero("Introduce el código de una película a incluir: ")
            pel = self.buscar_pelicula(cod_pel)
            if not pel:
                print("❌ Película no encontrada.")
            elif pel in seleccionadas:
                print("⚠️ Esa película ya está incluida en este alquiler.")
            else:
                seleccionadas.append(pel)
                print(f"➕ Añadida: {pel.nombre} ({pel.precio_alquiler:.2f}€)")

            if seleccionadas and input("¿Añadir otra película al mismo alquiler? (s/n): ").strip().lower() != "s":
                break

        fecha_recogida = leer_fecha("Fecha de recogida")
        while True:
            fecha_devolucion = leer_fecha("Fecha de devolución")
            if fecha_devolucion > fecha_recogida:
                break
            print("❌ La fecha de devolución debe ser posterior a la de recogida.")

        alquiler = Alquiler(socio, seleccionadas, fecha_recogida, fecha_devolucion)
        self.alquileres.append(alquiler)
        print(f"✅ Alquiler registrado correctamente:\n{alquiler}")

    def editar_fecha_devolucion_alquiler(self):
        if not self.alquileres:
            print("⚠️ No hay alquileres registrados.")
            return
        print("\n--- MODIFICAR FECHA DE DEVOLUCIÓN ---")
        for a in self.alquileres:
            print(a)
        alq = self.buscar_alquiler(leer_entero("Código del alquiler a modificar: "))
        if not alq:
            print("❌ Alquiler no encontrado.")
            return

        # Regla: NO usar fecha del sistema; pedir al usuario la fecha actual y la nueva fecha
        fecha_actual = leer_fecha("Introduce la fecha actual")
        nueva_devolucion = leer_fecha("Introduce la nueva fecha de devolución")

        if alq.actualizar_fecha_devolucion(nueva_devolucion, fecha_actual):
            print(f"✅ Fecha de devolución actualizada:\n{alq}")
        else:
            print("❌ Error: La nueva fecha de devolución debe ser estrictamente posterior a la fecha actual.")

    # --- 5. Administradores y Estadísticas Mensuales ---
    def alta_administrador(self):
        print("\n--- ALTA DE ADMINISTRADOR ---")
        nombre = leer_texto("Nombre del administrador: ")
        admin = Administrador(nombre)
        self.administradores.append(admin)
        print(f"✅ Administrador creado: {admin}")

    def editar_administrador(self):
        if not self.administradores:
            print("⚠️ No hay administradores registrados.")
            return
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Código del administrador a editar: "))
        if not admin:
            print("❌ Administrador no encontrado.")
            return
        nuevo_nombre = leer_texto(f"Nombre ({admin.nombre}): ", obligatorio=False)
        if nuevo_nombre:
            admin.nombre = nuevo_nombre
        print(f"✅ Administrador actualizado: {admin}")

    def generar_estadistica_mensual(self):
        if not self.administradores:
            print("⚠️ Debe existir al menos un administrador para generar estadísticas.")
            return
        if not self.socios:
            print("⚠️ No hay socios registrados.")
            return

        print("\n--- CÁLCULO DE ESTADÍSTICA MENSUAL POR SOCIO ---")
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Código del administrador que realiza el cálculo: "))
        if not admin:
            print("❌ Administrador no encontrado.")
            return

        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio a analizar: "))
        if not socio:
            print("❌ Socio no encontrado.")
            return

        mes, anio = leer_mes_anio("Mes y año a consultar")

        # Validación: En un mes no se puede almacenar más de un dato estadístico por socio
        ya_existe = any(
            e.socio.codigo == socio.codigo and e.mes == mes and e.anio == anio
            for e in self.estadisticas
        )
        if ya_existe:
            print(f"❌ Error: Ya existe una estadística registrada para {socio.nombre} en {mes:02d}/{anio}.")
            return

        fecha_creacion = leer_fecha("Fecha de creación de la estadística")

        # Cálculo derivado: suma de alquileres del socio en ese mes/año (según fecha de recogida)
        total_gastado = sum(
            a.total_a_pagar
            for a in self.alquileres
            if a.socio.codigo == socio.codigo
            and a.fecha_recogida.month == mes
            and a.fecha_recogida.year == anio
        )

        est = EstadisticaSocio(socio, mes, anio, fecha_creacion, total_gastado)
        self.estadisticas.append(est)
        print(f"✅ Estadística generada por {admin.nombre}:\n{est}")


# ==========================================
# MENÚ PRINCIPAL INTERACTIVO
# ==========================================

def ejecutar_app():
    sistema = SistemaAPPV()

    while True:
        print("\n==========================================")
        print("       GESTIÓN CADENA VIDEOCLUBS APPV     ")
        print("==========================================")
        print("1. Alta de Videoclub")
        print("2. Editar Videoclub")
        print("3. Alta de Película")
        print("4. Editar Película")
        print("5. Alta de Socio")
        print("6. Editar Socio")
        print("7. Registrar Alquiler")
        print("8. Modificar Fecha de Devolución de Alquiler")
        print("9. Alta / Edición de Administrador")
        print("10. Generar Estadística Mensual por Socio")
        print("11. Listar Resumen General del Sistema")
        print("0. Salir")
        print("==========================================")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            sistema.alta_videoclub()
        elif opcion == "2":
            sistema.editar_videoclub()
        elif opcion == "3":
            sistema.alta_pelicula()
        elif opcion == "4":
            sistema.editar_pelicula()
        elif opcion == "5":
            sistema.alta_socio()
        elif opcion == "6":
            sistema.editar_socio()
        elif opcion == "7":
            sistema.registrar_alquiler()
        elif opcion == "8":
            sistema.editar_fecha_devolucion_alquiler()
        elif opcion == "9":
            sub = input("1. Nuevo Administrador | 2. Editar Administrador: ").strip()
            if sub == "1":
                sistema.alta_administrador()
            elif sub == "2":
                sistema.editar_administrador()
        elif opcion == "10":
            sistema.generar_estadistica_mensual()
        elif opcion == "11":
            print("\n--- VIDEOCLUBS ---")
            print("\n".join(str(x) for x in sistema.videoclubs) or "Sin registros")
            print("\n--- PELÍCULAS ---")
            print("\n".join(str(x) for x in sistema.peliculas) or "Sin registros")
            print("\n--- SOCIOS ---")
            print("\n".join(str(x) for x in sistema.socios) or "Sin registros")
            print("\n--- ALQUILERES ---")
            print("\n".join(str(x) for x in sistema.alquileres) or "Sin registros")
            print("\n--- ADMINISTRADORES ---")
            print("\n".join(str(x) for x in sistema.administradores) or "Sin registros")
            print("\n--- ESTADÍSTICAS ---")
            print("\n".join(str(x) for x in sistema.estadisticas) or "Sin registros")
        elif opcion == "0":
            print("Saliendo del sistema APPV...")
            break
        else:
            print("❌ Opción no válida.")


if __name__ == "__main__":
    ejecutar_app()