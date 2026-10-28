"""Sin mojibake en el backend: detecta doble-codificacion UTF-8.

Solo caza secuencias tipicas de mojibake (no tildes validas): el resto del
repo usa UTF-8 con tildes y este test no debe romperlo.
"""
import re
from pathlib import Path

# Secuencias de doble-codificacion: UTF-8 leido como latin-1 y regrabado.
# Se escribe con escapes para que este mismo archivo solo tenga ASCII.
MOJIBAKE_RE = re.compile("\u00c3.|\u00c2[\u20ac\u201a\u0192\u201e\u2026]|\ufffd|\u00e2\u0080")

# Raiz del backend (este archivo vive en tests/unit/).
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _py_files():
    # Solo codigo versionado: se excluyen entornos y caches locales.
    for base in (BACKEND_ROOT / "app", BACKEND_ROOT / "tests"):
        yield from sorted(base.rglob("*.py"))


def test_sin_mojibake_en_backend():
    hallazgos = []
    for path in _py_files():
        # Lectura estricta: si el archivo no es UTF-8 valido, tambien es hallazgo.
        try:
            texto = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            hallazgos.append(f"{path.relative_to(BACKEND_ROOT)}: no es UTF-8 valido")
            continue
        # Este detector se autoexcluye: su propio patron usa escapes ASCII.
        if path.name == "test_encoding.py":
            continue
        for nro, linea in enumerate(texto.splitlines(), start=1):
            # Se revisa linea por linea para reportar file:linea exactos.
            if MOJIBAKE_RE.search(linea):
                hallazgos.append(f"{path.relative_to(BACKEND_ROOT)}:{nro}")
    assert not hallazgos, "mojibake detectado:\n" + "\n".join(hallazgos)
