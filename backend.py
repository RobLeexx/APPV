import json
from pathlib import Path
from typing import Any, Dict


class RepositorioJSON:
    """Capa de persistencia: lee y guarda el estado serializado en formato JSON."""

    CLAVES_COLECCIONES = (
        "videoclubs",
        "peliculas",
        "socios",
        "alquileres",
        "administradores",
        "estadisticas",
    )

    def __init__(self, ruta_archivo: str = "datos_appv.json"):
        self.archivo = Path(ruta_archivo)

    def _estructura_vacia(self) -> Dict[str, list]:
        return {clave: [] for clave in self.CLAVES_COLECCIONES}

    def cargar(self) -> Dict[str, Any]:
        """Recupera los datos desde el fichero JSON o devuelve una estructura vacía si no existe."""
        if not self.archivo.exists():
            return self._estructura_vacia()

        try:
            with self.archivo.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            if not isinstance(datos, dict):
                raise RuntimeError("El formato raíz del fichero JSON no es válido.")

            resultado = self._estructura_vacia()
            for clave in self.CLAVES_COLECCIONES:
                if clave in datos and isinstance(datos[clave], list):
                    resultado[clave] = datos[clave]
            return resultado
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Error al leer el almacenamiento ({self.archivo}): {exc}") from exc

    def guardar(self, datos: Dict[str, Any]) -> None:
        """Persiste el diccionario completo en el fichero JSON."""
        try:
            with self.archivo.open("w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            raise RuntimeError(f"Error al guardar en el almacenamiento ({self.archivo}): {exc}") from exc