"""Einheitlicher Abbildungsstil für alle Paper-Abbildungen (Vektor-PDF, serifenlose Beschriftung, dezentes Raster)."""


def apply_style():
    import matplotlib as mpl
    mpl.rcParams.update({"font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 7.5, "xtick.labelsize": 8,
                         "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "lines.linewidth": 1.4, "lines.markersize": 4, "savefig.bbox": "tight",
                         "pdf.fonttype": 42, "figure.dpi": 150, "legend.frameon": False})
