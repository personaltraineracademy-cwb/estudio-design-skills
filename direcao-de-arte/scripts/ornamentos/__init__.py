"""Biblioteca de ELEMENTOS GRÁFICOS (peças, sites, artes). Contrato em nucleo.py; catálogo: python -m ornamentos.catalogo
(rodar de <raiz da skill>/scripts). Cada módulo de família registra amostras com @nucleo.amostra."""
import importlib
import pkgutil
import os
import sys

from .nucleo import Ficha, Elemento, REGISTRO, amostra, ficha_exemplo  # noqa: F401


def carregar_tudo(so=None):
    """Importa os módulos de família (registra as amostras). `so` = nome do módulo/família: carrega só ele (e o que
    ele importa). Um módulo quebrado não derruba os outros: o erro é impresso e a carga segue."""
    nomes = [m.name for m in pkgutil.iter_modules([os.path.dirname(__file__)])
             if m.name not in ("nucleo", "catalogo") and not m.name.startswith("_")]
    if so and so in nomes:
        nomes = [so]
    for n in nomes:
        try:
            importlib.import_module(f"{__name__}.{n}")
        except Exception as e:  # noqa: BLE001
            print(f"AVISO: módulo {n} não carregou: {e!r}", file=sys.stderr)
    return REGISTRO
