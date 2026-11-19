from datetime import datetime
from typing import List, Optional

from backend import RepositorioJSON

FORMATO_FECHA = "%d/%m/%Y"


# ==========================================
# ENTIDADES DEL MODELO DE DOMINIO
# ==========================================

class Videoclub:
    _contador = 1

    def __init__(self, gerente: str, ciudad: str, calle: str, codigo_postal: str,
                 codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = Videoclub._contador
            Videoclub._contador += 1
        else:
            self.__codigo = codigo
            Videoclub._contador = max(Videoclub._contador, codigo + 1)

        self.gerente = gerente
        self.ciudad = ciudad
        self.calle = calle
        self.codigo_postal = codigo_postal

    @property
    def codigo(self) -> int:
        return self.__codigo

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "gerente": self.gerente,
            "ciudad": self.ciudad,
            "calle": self.calle,
            "codigo_postal": self.codigo_postal,
        }

    def __str__(self) -> str:
        return f"[VC-{self.codigo}] {self.ciudad} - C/ {self.calle} ({self.codigo_postal}) | Gerente: {self.gerente}"


class Pelicula:
    _contador = 1

    def __init__(self, nombre: str, fecha_estreno: datetime, precio_alquiler: float,
                 videoclub: Videoclub, director: Optional[str] = None,
                 codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = Pelicula._contador
            Pelicula._contador += 1
        else:
            self.__codigo = codigo
            Pelicula._contador = max(Pelicula._contador, codigo + 1)

        self.nombre = nombre
        self.director = director
        self.fecha_estreno = fecha_estreno
        self.precio_alquiler = round(precio_alquiler, 2)
        self.videoclub = videoclub

    @property
    def codigo(self) -> int:
        return self.__codigo

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "director": self.director,
            "fecha_estreno": self.fecha_estreno.strftime(FORMATO_FECHA),
            "precio_alquiler": self.precio_alquiler,
            "videoclub_codigo": self.videoclub.codigo,
        }

    def __str__(self) -> str:
        dir_str = self.director if self.director else "No especificado"
        estreno_str = self.fecha_estreno.strftime(FORMATO_FECHA)
        return (
            f"[PEL-{self.codigo}] '{self.nombre}' | Dir: {dir_str} | "
            f"Estreno: {estreno_str} | Precio: {self.precio_alquiler:.2f}€ | "
            f"Videoclub: {self.videoclub.ciudad} (VC-{self.videoclub.codigo})"
        )


class Socio:
    _contador = 1

    def __init__(self, nombre: str, edad: int, codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = Socio._contador
            Socio._contador += 1
        else:
            self.__codigo = codigo
            Socio._contador = max(Socio._contador, codigo + 1)

        self.nombre = nombre
        self.edad = edad

    @property
    def codigo(self) -> int:
        return self.__codigo

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "edad": self.edad,
        }

    def __str__(self) -> str:
        return f"[SOC-{self.codigo}] {self.nombre} ({self.edad} años)"


class Alquiler:
    _contador = 1

    def __init__(self, socio: Socio, peliculas: List[Pelicula],
                 fecha_recogida: datetime, fecha_devolucion: datetime,
                 codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = Alquiler._contador
            Alquiler._contador += 1
        else:
            self.__codigo = codigo
            Alquiler._contador = max(Alquiler._contador, codigo + 1)

        self.socio = socio
        self.peliculas = peliculas
        # Obligatoria y NO editable
        self.__fecha_recogida = fecha_recogida
        # Obligatoria y editable
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

    def actualizar_fecha_devolucion(self, nueva_fecha: datetime, fecha_actual_manual: datetime) -> None:
        if nueva_fecha <= fecha_actual_manual:
            raise ValueError("La nueva fecha de devolución debe ser estrictamente posterior a la fecha actual.")
        self.__fecha_devolucion = nueva_fecha

    @property
    def total_a_pagar(self) -> float:
        """Atributo derivado: suma de los precios de las películas del alquiler."""
        return round(sum(p.precio_alquiler for p in self.peliculas), 2)

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "socio_codigo": self.socio.codigo,
            "peliculas_codigos": [p.codigo for p in self.peliculas],
            "fecha_recogida": self.fecha_recogida.strftime(FORMATO_FECHA),
            "fecha_devolucion": self.fecha_devolucion.strftime(FORMATO_FECHA),
        }

    def __str__(self) -> str:
        titulos = ", ".join(f"{p.nombre} (PEL-{p.codigo})" for p in self.peliculas)
        return (
            f"[ALQ-{self.codigo}] Socio: {self.socio.nombre} | "
            f"Recogida: {self.fecha_recogida.strftime(FORMATO_FECHA)} | "
            f"Devolución: {self.fecha_devolucion.strftime(FORMATO_FECHA)} | "
            f"Total: {self.total_a_pagar:.2f}€\n   Películas: {titulos}"
        )


class EstadisticaSocio:
    _contador = 1

    def __init__(self, socio: Socio, mes: int, anio: int,
                 fecha_creacion: datetime, total_gastado: float,
                 codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = EstadisticaSocio._contador
            EstadisticaSocio._contador += 1
        else:
            self.__codigo = codigo
            EstadisticaSocio._contador = max(EstadisticaSocio._contador, codigo + 1)

        self.socio = socio
        self.mes = mes
        self.anio = anio
        # Obligatoria y NO editable
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

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "socio_codigo": self.socio.codigo,
            "mes": self.mes,
            "anio": self.anio,
            "fecha_creacion": self.fecha_creacion.strftime(FORMATO_FECHA),
            "total_gastado": self.total_gastado,
        }

    def __str__(self) -> str:
        return (
            f"[EST-{self.codigo}] Socio: {self.socio.nombre} (SOC-{self.socio.codigo}) | "
            f"Periodo: {self.mes:02d}/{self.anio} | "
            f"Creada el: {self.fecha_creacion.strftime(FORMATO_FECHA)} | "
            f"Total gastado: {self.total_gastado:.2f}€"
        )


class Administrador:
    _contador = 1

    def __init__(self, nombre: str, codigo: Optional[int] = None):
        if codigo is None:
            self.__codigo = Administrador._contador
            Administrador._contador += 1
        else:
            self.__codigo = codigo
            Administrador._contador = max(Administrador._contador, codigo + 1)

        self.nombre = nombre

    @property
    def codigo(self) -> int:
        return self.__codigo

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
        }

    def __str__(self) -> str:
        return f"[ADM-{self.codigo}] {self.nombre}"


# ==========================================
# SERVICIO DE LÓGICA DE NEGOCIO
# ==========================================

class ServicioAPPV:
    """Capa de lógica de negocio: aplica reglas del dominio y coordina el repositorio."""

    def __init__(self, repositorio: RepositorioJSON):
        self._repo = repositorio
        self.videoclubs: List[Videoclub] = []
        self.peliculas: List[Pelicula] = []
        self.socios: List[Socio] = []
        self.alquileres: List[Alquiler] = []
        self.administradores: List[Administrador] = []
        self.estadisticas: List[EstadisticaSocio] = []
        self._cargar_estado()

    # --- Sincronización con Backend ---
    def _cargar_estado(self) -> None:
        datos = self._repo.cargar()

        for item in datos["videoclubs"]:
            self.videoclubs.append(
                Videoclub(
                    gerente=item["gerente"],
                    ciudad=item["ciudad"],
                    calle=item["calle"],
                    codigo_postal=item["codigo_postal"],
                    codigo=item["codigo"],
                )
            )

        for item in datos["peliculas"]:
            vc = self.obtener_videoclub(item["videoclub_codigo"])
            if vc:
                self.peliculas.append(
                    Pelicula(
                        nombre=item["nombre"],
                        fecha_estreno=datetime.strptime(item["fecha_estreno"], FORMATO_FECHA),
                        precio_alquiler=item["precio_alquiler"],
                        videoclub=vc,
                        director=item.get("director"),
                        codigo=item["codigo"],
                    )
                )

        for item in datos["socios"]:
            self.socios.append(
                Socio(
                    nombre=item["nombre"],
                    edad=item["edad"],
                    codigo=item["codigo"],
                )
            )

        for item in datos["alquileres"]:
            socio = self.obtener_socio(item["socio_codigo"])
            peliculas_alq = [
                p for cod in item.get("peliculas_codigos", [])
                if (p := self.obtener_pelicula(cod)) is not None
            ]
            if socio and peliculas_alq:
                self.alquileres.append(
                    Alquiler(
                        socio=socio,
                        peliculas=peliculas_alq,
                        fecha_recogida=datetime.strptime(item["fecha_recogida"], FORMATO_FECHA),
                        fecha_devolucion=datetime.strptime(item["fecha_devolucion"], FORMATO_FECHA),
                        codigo=item["codigo"],
                    )
                )

        for item in datos["administradores"]:
            self.administradores.append(
                Administrador(
                    nombre=item["nombre"],
                    codigo=item["codigo"],
                )
            )

        for item in datos["estadisticas"]:
            socio = self.obtener_socio(item["socio_codigo"])
            if socio:
                self.estadisticas.append(
                    EstadisticaSocio(
                        socio=socio,
                        mes=item["mes"],
                        anio=item["anio"],
                        fecha_creacion=datetime.strptime(item["fecha_creacion"], FORMATO_FECHA),
                        total_gastado=item["total_gastado"],
                        codigo=item["codigo"],
                    )
                )

    def _guardar_estado(self) -> None:
        self._repo.guardar({
            "videoclubs": [v.to_dict() for v in self.videoclubs],
            "peliculas": [p.to_dict() for p in self.peliculas],
            "socios": [s.to_dict() for s in self.socios],
            "alquileres": [a.to_dict() for a in self.alquileres],
            "administradores": [ad.to_dict() for ad in self.administradores],
            "estadisticas": [e.to_dict() for e in self.estadisticas],
        })

    # --- Validaciones internas ---
    @staticmethod
    def _validar_cadena_obligatoria(valor: str, campo: str) -> str:
        if not valor or not valor.strip():
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        return valor.strip()

    @staticmethod
    def _validar_codigo_postal(cp: str) -> str:
        cp_limpio = ServicioAPPV._validar_cadena_obligatoria(cp, "código postal")
        if len(cp_limpio) != 5:
            raise ValueError("El código postal debe tener exactamente 5 caracteres.")
        return cp_limpio

    # --- Consultas por código ---
    def obtener_videoclub(self, codigo: int) -> Optional[Videoclub]:
        return next((v for v in self.videoclubs if v.codigo == codigo), None)

    def obtener_pelicula(self, codigo: int) -> Optional[Pelicula]:
        return next((p for p in self.peliculas if p.codigo == codigo), None)

    def obtener_socio(self, codigo: int) -> Optional[Socio]:
        return next((s for s in self.socios if s.codigo == codigo), None)

    def obtener_alquiler(self, codigo: int) -> Optional[Alquiler]:
        return next((a for a in self.alquileres if a.codigo == codigo), None)

    def obtener_administrador(self, codigo: int) -> Optional[Administrador]:
        return next((ad for ad in self.administradores if ad.codigo == codigo), None)

    # --- Casos de uso: Videoclubs ---
    def crear_videoclub(self, gerente: str, ciudad: str, calle: str, codigo_postal: str) -> Videoclub:
        vc = Videoclub(
            gerente=self._validar_cadena_obligatoria(gerente, "gerente"),
            ciudad=self._validar_cadena_obligatoria(ciudad, "ciudad"),
            calle=self._validar_cadena_obligatoria(calle, "calle"),
            codigo_postal=self._validar_codigo_postal(codigo_postal),
        )
        self.videoclubs.append(vc)
        self._guardar_estado()
        return vc

    def editar_videoclub(self, codigo: int, gerente: Optional[str] = None,
                         ciudad: Optional[str] = None, calle: Optional[str] = None,
                         codigo_postal: Optional[str] = None) -> Videoclub:
        vc = self.obtener_videoclub(codigo)
        if not vc:
            raise ValueError(f"No existe ningún videoclub con código {codigo}.")

        if gerente is not None:
            vc.gerente = self._validar_cadena_obligatoria(gerente, "gerente")
        if ciudad is not None:
            vc.ciudad = self._validar_cadena_obligatoria(ciudad, "ciudad")
        if calle is not None:
            vc.calle = self._validar_cadena_obligatoria(calle, "calle")
        if codigo_postal is not None:
            vc.codigo_postal = self._validar_codigo_postal(codigo_postal)

        self._guardar_estado()
        return vc

    # --- Casos de uso: Películas ---
    def crear_pelicula(self, videoclub_codigo: int, nombre: str, fecha_estreno: datetime,
                       precio_alquiler: float, director: Optional[str] = None) -> Pelicula:
        vc = self.obtener_videoclub(videoclub_codigo)
        if not vc:
            raise ValueError(f"No existe ningún videoclub con código {videoclub_codigo}.")
        if precio_alquiler <= 0:
            raise ValueError("El precio de alquiler debe ser mayor que 0.")

        dir_limpio = director.strip() if director and director.strip() else None
        pel = Pelicula(
            nombre=self._validar_cadena_obligatoria(nombre, "nombre"),
            fecha_estreno=fecha_estreno,
            precio_alquiler=precio_alquiler,
            videoclub=vc,
            director=dir_limpio,
        )
        self.peliculas.append(pel)
        self._guardar_estado()
        return pel

    def editar_pelicula(self, codigo: int, nombre: Optional[str] = None,
                        director: Optional[str] = None, limpiar_director: bool = False,
                        fecha_estreno: Optional[datetime] = None,
                        precio_alquiler: Optional[float] = None) -> Pelicula:
        pel = self.obtener_pelicula(codigo)
        if not pel:
            raise ValueError(f"No existe ninguna película con código {codigo}.")

        if nombre is not None:
            pel.nombre = self._validar_cadena_obligatoria(nombre, "nombre")
        if limpiar_director:
            pel.director = None
        elif director is not None and director.strip():
            pel.director = director.strip()
        if fecha_estreno is not None:
            pel.fecha_estreno = fecha_estreno
        if precio_alquiler is not None:
            if precio_alquiler <= 0:
                raise ValueError("El precio de alquiler debe ser mayor que 0.")
            pel.precio_alquiler = round(precio_alquiler, 2)

        self._guardar_estado()
        return pel

    # --- Casos de uso: Socios ---
    def crear_socio(self, nombre: str, edad: int) -> Socio:
        if edad <= 0:
            raise ValueError("La edad del socio debe ser un entero positivo.")
        socio = Socio(
            nombre=self._validar_cadena_obligatoria(nombre, "nombre"),
            edad=edad,
        )
        self.socios.append(socio)
        self._guardar_estado()
        return socio

    def editar_socio(self, codigo: int, nombre: Optional[str] = None,
                     edad: Optional[int] = None) -> Socio:
        socio = self.obtener_socio(codigo)
        if not socio:
            raise ValueError(f"No existe ningún socio con código {codigo}.")

        if nombre is not None:
            socio.nombre = self._validar_cadena_obligatoria(nombre, "nombre")
        if edad is not None:
            if edad <= 0:
                raise ValueError("La edad del socio debe ser un entero positivo.")
            socio.edad = edad

        self._guardar_estado()
        return socio

    # --- Casos de uso: Alquileres ---
    def registrar_alquiler(self, socio_codigo: int, peliculas_codigos: List[int],
                           fecha_recogida: datetime, fecha_devolucion: datetime) -> Alquiler:
        socio = self.obtener_socio(socio_codigo)
        if not socio:
            raise ValueError(f"No existe ningún socio con código {socio_codigo}.")
        if not peliculas_codigos:
            raise ValueError("Un alquiler debe incluir al menos una película.")
        if fecha_devolucion <= fecha_recogida:
            raise ValueError("La fecha de devolución debe ser posterior a la fecha de recogida.")

        peliculas_unicas: List[Pelicula] = []
        for cod in peliculas_codigos:
            pel = self.obtener_pelicula(cod)
            if not pel:
                raise ValueError(f"No existe ninguna película con código {cod}.")
            if pel in peliculas_unicas:
                raise ValueError(f"La película con código {cod} está duplicada en el alquiler.")
            peliculas_unicas.append(pel)

        alquiler = Alquiler(socio, peliculas_unicas, fecha_recogida, fecha_devolucion)
        self.alquileres.append(alquiler)
        self._guardar_estado()
        return alquiler

    def modificar_fecha_devolucion(self, alquiler_codigo: int,
                                   nueva_fecha_devolucion: datetime,
                                   fecha_actual_manual: datetime) -> Alquiler:
        alquiler = self.obtener_alquiler(alquiler_codigo)
        if not alquiler:
            raise ValueError(f"No existe ningún alquiler con código {alquiler_codigo}.")

        alquiler.actualizar_fecha_devolucion(nueva_fecha_devolucion, fecha_actual_manual)
        self._guardar_estado()
        return alquiler

    # --- Casos de uso: Administradores y Estadísticas ---
    def crear_administrador(self, nombre: str) -> Administrador:
        admin = Administrador(nombre=self._validar_cadena_obligatoria(nombre, "nombre"))
        self.administradores.append(admin)
        self._guardar_estado()
        return admin

    def editar_administrador(self, codigo: int, nombre: str) -> Administrador:
        admin = self.obtener_administrador(codigo)
        if not admin:
            raise ValueError(f"No existe ningún administrador con código {codigo}.")
        admin.nombre = self._validar_cadena_obligatoria(nombre, "nombre")
        self._guardar_estado()
        return admin

    def generar_estadistica_mensual(self, admin_codigo: int, socio_codigo: int,
                                    mes: int, anio: int,
                                    fecha_creacion: datetime) -> EstadisticaSocio:
        if not self.obtener_administrador(admin_codigo):
            raise ValueError(f"No existe ningún administrador con código {admin_codigo}.")
        socio = self.obtener_socio(socio_codigo)
        if not socio:
            raise ValueError(f"No existe ningún socio con código {socio_codigo}.")
        if not (1 <= mes <= 12):
            raise ValueError("El mes debe estar comprendido entre 1 y 12.")

        ya_existe = any(
            e.socio.codigo == socio_codigo and e.mes == mes and e.anio == anio
            for e in self.estadisticas
        )
        if ya_existe:
            raise ValueError(
                f"Ya existe una estadística almacenada para {socio.nombre} en {mes:02d}/{anio}."
            )

        total_gastado = sum(
            a.total_a_pagar
            for a in self.alquileres
            if a.socio.codigo == socio_codigo
            and a.fecha_recogida.month == mes
            and a.fecha_recogida.year == anio
        )

        estadistica = EstadisticaSocio(socio, mes, anio, fecha_creacion, total_gastado)
        self.estadisticas.append(estadistica)
        self._guardar_estado()
        return estadistica