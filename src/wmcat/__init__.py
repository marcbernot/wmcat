"""wmcat: browse and load watermark thermography files hosted on Zenodo."""

from .catalog import WatermarkCatalog, open_catalog
from .watermark import Watermark

__all__ = ["Watermark", "WatermarkCatalog", "open_catalog"]
__version__ = "0.0.1"
