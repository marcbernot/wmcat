"""The catalog: a thin wrapper over a pandas DataFrame."""

from __future__ import annotations

import io
import sys
from importlib import resources
from pathlib import Path

import pandas as pd

from .watermark import Watermark

IN_PYODIDE = sys.platform == "emscripten"


def open_catalog(path: str | Path | None = None) -> WatermarkCatalog:
    """Open a catalog CSV. Default: the sample catalog bundled with the package."""
    if path is None:
        path = io.StringIO(
            (resources.files("wmcat") / "data" / "sample_catalog.csv").read_text("utf-8")
        )
    return WatermarkCatalog(pd.read_csv(path, dtype=str, keep_default_na=False))


class WatermarkCatalog:
    """A filtered view over the catalog. The DataFrame (``.df``) *is* the catalog."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)

    def search(self, exact: bool = False, **filters) -> WatermarkCatalog:
        """Filter rows. ``search(motif="lily")`` is a case-insensitive substring match;
        ``search(wm_type="01f", exact=True)`` matches the whole value only
        (so ``01f`` does not match ``01f+02f``)."""
        mask = pd.Series(True, index=self.df.index)
        for col, value in filters.items():
            if col not in self.df.columns:
                raise KeyError(f"unknown column {col!r}; columns: {list(self.df.columns)}")
            s = self.df[col].astype(str)
            if exact:
                mask &= s == str(value)
            else:
                mask &= s.str.contains(str(value), case=False, regex=False)
        return WatermarkCatalog(self.df[mask])

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, i: int) -> pd.Series:
        return self.df.iloc[i]

    def __repr__(self) -> str:
        cols = ["holding_institution", "shelfmark", "wm_type", "motif"]
        cols = [c for c in cols if c in self.df.columns]
        return f"WatermarkCatalog: {len(self)} watermarks\n{self.df[cols].head(10).to_string()}"

    def _repr_html_(self) -> str:
        return (
            f"<p><b>WatermarkCatalog</b>: {len(self)} watermarks</p>" + self.df.head(10).to_html()
        )

    # --- loading -------------------------------------------------------------------------

    def load(self, i: int = 0) -> Watermark:
        """Download (cached with pooch) and read watermark ``i``. Desktop only."""
        if IN_PYODIDE:
            raise RuntimeError("In the browser, use `w = await cat.aload(i)` instead of load().")
        import pooch

        row = self[i]
        path = pooch.retrieve(
            row["url"], known_hash=None, fname=row["filename"], path=pooch.os_cache("wmcat")
        )
        return Watermark.from_bytes(Path(path).read_bytes(), meta=row.to_dict())

    async def aload(self, i: int = 0) -> Watermark:
        """Load watermark ``i``. Works in JupyterLite (fetch, in memory) and on desktop."""
        row = self[i]
        if IN_PYODIDE:
            from pyodide.http import pyfetch

            resp = await pyfetch(row["url"])
            if not resp.ok:
                raise OSError(f"HTTP {resp.status} fetching {row['url']}")
            return Watermark.from_bytes(await resp.bytes(), meta=row.to_dict())
        import asyncio

        return await asyncio.to_thread(self.load, i)
