"""The Watermark object returned by the catalog loaders."""

from __future__ import annotations

import io
from dataclasses import dataclass, field

import numpy as np


def _struct_to_dict(s) -> dict:
    """Convert a MATLAB struct (loaded with squeeze_me=True) to a plain dict."""
    if s is None or not getattr(s, "dtype", None) or not s.dtype.names:
        return {}
    return {name: s[name].item() if s[name].ndim == 0 else s[name] for name in s.dtype.names}


@dataclass
class Watermark:
    """One thermography recording.

    data: the MATLAB variables. ``data["Images"]`` is the raw frame stack (H, W, frames),
          ``data["Metadata"]`` the Watermark Imager settings as a dict.
    meta: the catalog row (DOI, shelfmark, ...).
    """

    data: dict
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_bytes(cls, raw: bytes, meta: dict | None = None) -> Watermark:
        from scipy.io import loadmat

        mat = loadmat(io.BytesIO(raw), squeeze_me=True)
        data = {k: v for k, v in mat.items() if not k.startswith("__")}
        data["Metadata"] = _struct_to_dict(data.get("Metadata"))
        return cls(data=data, meta=dict(meta or {}))

    @property
    def frames(self) -> np.ndarray:
        """Raw frame stack, shape (H, W, n_frames), uint16."""
        im = self.data["Images"]
        return im if im.ndim == 3 else im[..., np.newaxis]

    def image(self, correct: bool = True) -> np.ndarray:
        """A single 2D image for display: mean over frames, optionally corrected.

        Correction (rough approximation of the Watermark Imager pipeline):
        two-point NUC with Ref1/Ref2 when present, then subtraction of a Gaussian-blurred
        background (sigma = GaussKorrSigma when GaussKorr is on).
        """
        img = self.frames.mean(axis=2, dtype=np.float32)
        if not correct:
            return img
        md = self.data.get("Metadata", {})
        r1, r2 = md.get("Ref1"), md.get("Ref2")
        if (
            isinstance(r1, np.ndarray)
            and isinstance(r2, np.ndarray)
            and r1.shape == img.shape == r2.shape
        ):
            img = (img - r1) / np.where(r2 != r1, r2.astype(np.float32) - r1, 1.0)
        if md.get("GaussKorr"):
            from scipy.ndimage import gaussian_filter

            img = img - gaussian_filter(img, float(md.get("GaussKorrSigma", 14)))
        return img

    def show(self, correct: bool = True, ax=None, cmap: str = "gray"):
        """Display the watermark with a 1-99 percentile contrast stretch."""
        import matplotlib.pyplot as plt

        img = self.image(correct=correct)
        lo, hi = np.nanpercentile(img, [1, 99])
        own_fig = ax is None
        if own_fig:
            _, ax = plt.subplots(figsize=(7, 6))
        ax.imshow(img, cmap=cmap, vmin=lo, vmax=hi)
        ax.set_title(f"{self.meta.get('shelfmark', '')} — {self.meta.get('motif', '')}")
        ax.set_axis_off()
        if own_fig:
            plt.show()  # the Pyodide kernel does not flush figures at cell end
        return ax

    def __repr__(self) -> str:
        shape = getattr(self.data.get("Images"), "shape", None)
        return f"Watermark({self.meta.get('filename', '?')}, Images{shape})"
