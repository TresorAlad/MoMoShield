from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboards.lib.design_tokens import ALERT, AMBER, PRIMARY
from dashboards.lib.style import apply_plotly


def _jour_label(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.strftime("%d %b %Y")


def chart_volume_fraude_jour(df: pd.DataFrame, title: str) -> go.Figure:
    """Barres groupées, lisibles même avec une seule journée."""
    if df.empty:
        return go.Figure(layout=dict(title=title))

    plot = df.copy()
    plot["jour_label"] = _jour_label(plot["jour"])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Transactions",
            x=plot["jour_label"],
            y=plot["nb_transactions"],
            marker_color=PRIMARY,
            text=plot["nb_transactions"],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Fraude référence",
            x=plot["jour_label"],
            y=plot["nb_fraude"],
            marker_color="#e11d48",
            text=plot["nb_fraude"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=title,
        barmode="group",
        xaxis_title="Jour",
        yaxis_title="Nombre",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        bargap=0.25,
    )
    return apply_plotly(fig)


def chart_completude_jour(df: pd.DataFrame, title: str) -> go.Figure:
    if df.empty:
        return go.Figure(layout=dict(title=title))

    plot = df.copy()
    plot["jour_label"] = _jour_label(plot["jour"])
    plot["taux_sans_dest_pct"] = plot["taux_sans_dest"].astype(float) * 100

    fig = px.bar(
        plot,
        x="jour_label",
        y="taux_sans_dest_pct",
        title=title,
        labels={"jour_label": "Jour", "taux_sans_dest_pct": "Sans destinataire (%)"},
        color_discrete_sequence=[AMBER],
        text="taux_sans_dest_pct",
    )
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig.update_layout(yaxis=dict(range=[0, max(100, plot["taux_sans_dest_pct"].max() * 1.15)]))
    return apply_plotly(fig)


def chart_volume_heure(df: pd.DataFrame, title: str) -> go.Figure:
    if df.empty:
        return go.Figure(layout=dict(title=title))

    plot = df.copy()
    plot["heure_label"] = pd.to_datetime(plot["heure"]).dt.strftime("%Hh")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot["heure_label"],
            y=plot["nb_transactions"],
            name="Opérations",
            marker_color=PRIMARY,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=plot["heure_label"],
            y=plot["nb_fraude"],
            name="Fraude réf.",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=ALERT, width=2),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Heure (UTC)",
        yaxis=dict(title="Opérations"),
        yaxis2=dict(title="Fraude", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.08),
    )
    return apply_plotly(fig)