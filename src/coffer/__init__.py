from importlib.metadata import PackageNotFoundError, version

from coffer._config import CofferError, Config

try:
    __version__ = version("coffer-config")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["CofferError", "Config", "__version__"]
