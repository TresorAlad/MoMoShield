from __future__ import annotations

import unicodedata

import pandas as pd

VILLES_TOGO: dict[str, tuple[float, float]] = {
    "Lomé": (6.1256, 1.2254),
    "Kara": (9.5511, 1.1861),
    "Sokodé": (8.9833, 1.1333),
    "Kpalimé": (6.9000, 0.6333),
    "Atakpamé": (7.5333, 1.1333),
    "Tsévié": (6.4264, 1.2133),
    "Dapaong": (10.8625, 0.2078),
    "Mango": (10.3592, 0.4708),
}

TOGO_OUTLINE_LON = [
    0.77, 0.90, 1.05, 1.50, 1.78, 1.75, 1.55, 1.35, 1.15, 0.95, 0.80, 0.77,
]
TOGO_OUTLINE_LAT = [
    6.35, 6.55, 6.90, 9.25, 10.75, 11.05, 11.10, 10.95, 10.40, 7.80, 6.50, 6.35,
]


def _normalize(name: str) -> str:
    if not isinstance(name, str):
        return ""
    nf = unicodedata.normalize("NFD", name.strip())
    return "".join(c for c in nf if unicodedata.category(c) != "Mn").lower()


_LOOKUP = {_normalize(k): (k, lat, lon) for k, (lat, lon) in VILLES_TOGO.items()}


def _fmt_int(n: float | int) -> str:
    return f"{int(n):,}".replace(",", "\u202f")


def attach_coords(df: pd.DataFrame, ville_col: str = "ville") -> pd.DataFrame:
    if df.empty or ville_col not in df.columns:
        return df.copy()

    out = df.copy()
    lats: list[float | None] = []
    lons: list[float | None] = []
    labels: list[str] = []
    for raw in out[ville_col]:
        key = _normalize(str(raw))
        if key in _LOOKUP:
            label, lat, lon = _LOOKUP[key]
            lats.append(lat)
            lons.append(lon)
            labels.append(label)
        else:
            lats.append(None)
            lons.append(None)
            labels.append(str(raw))
    out["ville_affichee"] = labels
    out["lat"] = lats
    out["lon"] = lons
    return out.dropna(subset=["lat", "lon"])


def _marker_fill(value: float, vmax: float) -> str:
    if vmax <= 0:
        return "#14b8a6"
    t = min(max(value / vmax, 0.0), 1.0)
    if t < 0.34:
        return "#2dd4bf"
    if t < 0.67:
        return "#fbbf24"
    return "#f87171"


def prepare_geo_enriched(
    df: pd.DataFrame,
    color_col: str = "nb_alertes",
) -> pd.DataFrame:
    geo = attach_coords(df)
    if geo.empty:
        return geo
    if color_col not in geo.columns:
        color_col = "nb_transactions"
    vmax = float(geo[color_col].max() or 1)
    geo = geo.copy()
    geo["couleur_point"] = geo[color_col].apply(lambda v: _marker_fill(float(v), vmax))
    geo["etiquette"] = geo.apply(
        lambda r: (
            f"{r['ville_affichee']}\n"
            f"{_fmt_int(r['nb_transactions'])} op. · {_fmt_int(r['nb_alertes'])} alertes"
        ),
        axis=1,
    )
    return geo


def figure_carte_points(
    df: pd.DataFrame,
    *,
    title: str,
    color_col: str = "nb_alertes",
):
    """Carte 2D : points fixes + étiquettes (aucun bâton 3D)."""
    import plotly.graph_objects as go

    from dashboards.lib.style import PLOTLY_LAYOUT

    geo = prepare_geo_enriched(df, color_col=color_col)
    fig = go.Figure()
    if geo.empty:
        fig.update_layout(title=title, **PLOTLY_LAYOUT)
        return fig

    hover_lines = [
        (
            f"<b>{row['ville_affichee']}</b><br>"
            f"Opérations : {_fmt_int(row['nb_transactions'])}<br>"
            f"Alertes : {_fmt_int(row['nb_alertes'])}<br>"
            f"Montant : {_fmt_int(row['montant_total'])} FCFA<br>"
            f"Fraude réf. : {_fmt_int(row['nb_fraude'])}<extra></extra>"
        )
        for _, row in geo.iterrows()
    ]

    fig.add_trace(
        go.Scattermap(
            mode="markers+text",
            lat=geo["lat"],
            lon=geo["lon"],
            text=geo["etiquette"],
            textposition="top center",
            textfont=dict(size=11, color="#134e4a"),
            marker=dict(
                size=13,
                color=geo["couleur_point"].tolist(),
                opacity=0.92,
            ),
            hovertemplate=hover_lines,
            name="Villes",
        )
    )

    layout = {**PLOTLY_LAYOUT, "margin": dict(l=0, r=0, t=48, b=0)}
    fig.update_layout(
        title=title,
        height=480,
        map=dict(
            style="carto-positron",
            center=dict(lat=8.58, lon=1.02),
            zoom=6.55,
        ),
        **layout,
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig