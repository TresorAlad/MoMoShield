from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboards.lib.style import apply_plotly
from dashboards.lib.togo_geo import figure_carte_points, prepare_geo_enriched


def show_carte_togo(
    df,
    *,
    title: str,
    color_col: str = "nb_alertes",
    color_label: str = "Alertes",
) -> None:
    from dashboards.lib.components import section_title

    section_title(title)
    geo = prepare_geo_enriched(df, color_col=color_col)
    if geo.empty:
        st.info("Aucune ville géolocalisée pour cette période.")
        return

    st.plotly_chart(
        apply_plotly(figure_carte_points(df, title="", color_col=color_col)),
        use_container_width=True,
        key=f"carte_{color_col}_{title}",
    )
    st.caption(
        f"Uniquement les **points** par ville, couleur selon {color_label.lower()}. "
        "Survolez un point pour le détail."
    )

    tri = geo.sort_values(color_col, ascending=True)
    fig = apply_plotly(
        px.bar(
            tri,
            x=color_col,
            y="ville_affichee",
            orientation="h",
            title=f"Classement des villes : {color_label.lower()}",
            labels={color_col: color_label, "ville_affichee": "Ville"},
            color=color_col,
            color_continuous_scale=["#99f6e4", "#fcd34d", "#fca5a5"],
            text=color_col,
        )
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=max(260, 40 * len(tri)))
    st.plotly_chart(fig, use_container_width=True, key=f"bar_{color_col}_{title}")