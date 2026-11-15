from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboards.lib import data
from dashboards.lib.components import kpi_strip, page_header, section_title
from dashboards.lib.style import apply_plotly, inject_theme
from dashboards.lib.charts import (
    chart_completude_jour,
    chart_volume_fraude_jour,
    chart_volume_heure,
)
from dashboards.lib.map_ui import show_carte_togo
from dashboards.lib.sidebar import render_sidebar

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    st.error("Dépendances graphiques manquantes. Relancez `make bootstrap`.")
    st.stop()

st.set_page_config(
    page_title="MoMoShield",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

with st.sidebar:
    page = render_sidebar()


@st.cache_data(ttl=45, show_spinner=False)
def load_kpis():
    return data.kpi_summary()


def empty_state():
    page_header(
        "En attente de données",
        "Aucune transaction en base. Relancez l’alimentation des données, puis actualisez.",
    )


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return "n/d"


def fmt_fcfa(n) -> str:
    try:
        return f"{float(n):,.0f} FCFA".replace(",", " ")
    except (TypeError, ValueError):
        return "n/d"


if not data.has_data():
    empty_state()
    st.stop()

kpis = load_kpis()

if page == "Vue d'ensemble":
    page_header(
        "Vue d'ensemble",
        "Activité agrégée, volumes et signaux de fraude sur la période chargée.",
    )
    fraicheur = kpis.get("fraicheur_heures")
    fraicheur_hint = f"Dernière op. il y a {fraicheur:.1f} h" if fraicheur is not None else ""
    kpi_strip(
        [
            {"label": "Transactions", "value": fmt_int(kpis["nb_transactions"])},
            {"label": "Montant total", "value": fmt_fcfa(kpis["montant_total"])},
            {
                "label": "Alertes",
                "value": fmt_int(kpis["nb_alertes"]),
                "hint": f"{kpis['taux_alerte_pct']:.1f} % des opérations",
            },
            {
                "label": "Fraude référence",
                "value": fmt_int(kpis["nb_fraude_label"]),
                "hint": f"{kpis['taux_fraude_pct']:.2f} % du flux",
            },
            {"label": "Villes couvertes", "value": fmt_int(kpis["nb_villes"]), "hint": fraicheur_hint},
        ]
    )

    carte = data.carte_villes()
    if not carte.empty:
        show_carte_togo(
            carte,
            title="Carte du Togo : opérations et alertes par ville",
            color_col="nb_alertes",
            color_label="Alertes",
        )

    vol_h = data.volume_par_heure()
    if not vol_h.empty:
        st.plotly_chart(
            chart_volume_heure(
                vol_h,
                title="Activité par heure : volume et fraude référence",
            ),
            use_container_width=True,
        )

    op = data.par_operateur()
    if not op.empty:
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "domain"}, {"type": "xy"}]],
            subplot_titles=("Part du volume par opérateur", "Montant moyen par opérateur"),
        )
        fig.add_trace(
            go.Pie(
                labels=op["operateur"],
                values=op["nb_transactions"],
                hole=0.45,
                marker=dict(colors=px.colors.qualitative.Set2),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                x=op["operateur"],
                y=op["montant_moyen"],
                marker_color="#0d9488",
                name="Moyenne",
            ),
            row=1,
            col=2,
        )
        fig.update_layout(showlegend=False, height=380)
        apply_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Alertes & scores":
    page_header(
        "Alertes et scores",
        "Règles de détection, intensité des scores et comptes les plus exposés.",
    )

    scores = data.alertes_scores()
    regles = data.alertes_par_regle()
    croise = data.alertes_croisees()

    if regles.empty:
        st.warning("Aucune alerte enregistrée pour cette période.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            fig = apply_plotly(
                px.bar(
                    regles,
                    x="regle",
                    y="nb_alertes",
                    title="Volume d'alertes par règle",
                    labels={"regle": "Règle", "nb_alertes": "Nombre d'alertes"},
                    color="score_moyen",
                    color_continuous_scale="Tealrose",
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if not scores.empty:
                fig = apply_plotly(
                    px.histogram(
                        scores,
                        x="score",
                        color="regle",
                        nbins=40,
                        histnorm="probability density",
                        barmode="overlay",
                        opacity=0.65,
                        title="Densité des scores de risque par règle",
                        marginal="box",
                        labels={"score": "Score", "regle": "Règle"},
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

        if not croise.empty:
            pivot = croise.pivot(index="regle", columns="operateur", values="nb_alertes").fillna(0)
            fig = apply_plotly(
                px.imshow(
                    pivot,
                    title="Carte de chaleur : alertes (règle × opérateur)",
                    labels=dict(color="Alertes"),
                    color_continuous_scale="YlOrRd",
                    aspect="auto",
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        if not scores.empty and len(scores) > 5:
            fig = apply_plotly(
                px.density_heatmap(
                    scores,
                    x="amount_fcfa",
                    y="score",
                    nbinsx=35,
                    nbinsy=35,
                    title="Densité montant × score (zones à risque)",
                    labels={"amount_fcfa": "Montant (FCFA)", "score": "Score"},
                    color_continuous_scale="Magma",
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        section_title("Comptes les plus sollicités par les règles")
        risque = data.comptes_a_risque(20)
        if not risque.empty:
            fig = apply_plotly(
                px.scatter(
                    risque,
                    x="nb_transactions",
                    y="nb_alertes",
                    size="montant_total",
                    color="score_max",
                    hover_name="compte",
                    title="Transactions vs alertes (taille = montant total)",
                    labels={
                        "nb_transactions": "Transactions",
                        "nb_alertes": "Alertes",
                        "score_max": "Score max",
                    },
                    color_continuous_scale="Turbo",
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        recent = data.alerts().head(50)
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True,
            column_config={
                "score": st.column_config.ProgressColumn(
                    "Score", min_value=0, max_value=1, format="%.2f"
                ),
            },
        )

elif page == "Comportement des flux":
    page_header(
        "Comportement des flux",
        "Montants, géographie et types d’opération.",
    )

    tx = data.transactions()
    types_df = data.par_type()
    villes = data.par_ville()
    heat = data.heatmap_ville_operateur()
    mart = data.mart_fraude_dims()
    carte = data.carte_villes()

    if not carte.empty:
        show_carte_togo(
            carte,
            title="Répartition nationale : alertes par ville",
            color_col="nb_alertes",
            color_label="Alertes",
        )
        show_carte_togo(
            carte,
            title="Répartition nationale : fraude référence par ville",
            color_col="nb_fraude",
            color_label="Fraude référence",
        )

    col1, col2 = st.columns(2)
    with col1:
        if not tx.empty:
            fig = apply_plotly(
                px.histogram(
                    tx,
                    x="amount_fcfa",
                    color="is_fraud_label",
                    nbins=50,
                    histnorm="probability density",
                    barmode="overlay",
                    opacity=0.55,
                    title="Densité des montants : fraude vs flux normal",
                    labels={"amount_fcfa": "Montant (FCFA)", "is_fraud_label": "Fraude"},
                    marginal="violin",
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not types_df.empty:
            fig = apply_plotly(
                px.box(
                    tx,
                    x="type",
                    y="amount_fcfa",
                    color="type",
                    title="Distribution des montants par type d'opération",
                    labels={"type": "Type", "amount_fcfa": "Montant (FCFA)"},
                    points="outliers",
                )
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    if not villes.empty:
        villes = villes.sort_values("nb_transactions", ascending=True).tail(15)
        fig = apply_plotly(
            px.bar(
                villes,
                x="nb_transactions",
                y="ville",
                orientation="h",
                color="nb_fraude",
                title="Top villes : volume et cas fraude référence",
                labels={"ville": "Ville", "nb_transactions": "Transactions", "nb_fraude": "Fraude"},
                color_continuous_scale="Reds",
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    if not heat.empty:
        pivot_geo = heat.pivot(index="ville", columns="operateur", values="nb").fillna(0)
        top_villes = heat.groupby("ville")["nb"].sum().nlargest(12).index
        pivot_geo = pivot_geo.loc[pivot_geo.index.intersection(top_villes)]
        fig = apply_plotly(
            px.imshow(
                pivot_geo,
                title="Intensité d'activité ville × opérateur",
                color_continuous_scale="Teal",
                aspect="auto",
                labels=dict(color="Opérations"),
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    if not mart.empty:
        section_title("Synthèse par dimensions")
        date_col = next((c for c in mart.columns if "date" in c.lower()), mart.columns[0])
        count_col = next(
            (c for c in mart.columns if "nombre" in c.lower() or "count" in c.lower()),
            mart.columns[-1],
        )
        agg = mart.groupby(date_col)[count_col].sum().reset_index()
        fig = apply_plotly(
            px.line(
                agg,
                x=date_col,
                y=count_col,
                markers=True,
                title="Évolution du volume (mart consolidé)",
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        vcol = next((c for c in mart.columns if "ville" in c.lower()), None)
        if vcol and count_col in mart.columns:
            top = mart.groupby(vcol)[count_col].sum().nlargest(10).reset_index()
            fig = apply_plotly(
                px.treemap(
                    top,
                    path=[vcol],
                    values=count_col,
                    title="Poids des villes dans le volume (treemap)",
                )
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Qualité & supervision":
    page_header(
        "Qualité et supervision",
        "Fraîcheur, complétude et écarts entre signaux automatiques et vérité terrain.",
    )

    evol = data.evolution_jour()
    vol_h = data.volume_par_heure()
    fraicheur = kpis.get("fraicheur_heures")
    fraicheur_txt = f"{fraicheur:.1f} h" if fraicheur is not None else "n/d"
    kpi_strip(
        [
            {"label": "Fraîcheur", "value": fraicheur_txt, "hint": "Objectif : moins de 24 h"},
            {"label": "Taux d'alerte", "value": f"{kpis['taux_alerte_pct']:.2f} %"},
            {"label": "Fraude référence", "value": f"{kpis['taux_fraude_pct']:.2f} %"},
        ]
    )

    if len(evol) <= 2 and not vol_h.empty:
        st.caption(
            "Une seule journée agrégée en base : le détail horaire ci-dessous complète la lecture."
        )
        st.plotly_chart(
            chart_volume_heure(vol_h, title="Détail horaire : opérations et fraude"),
            use_container_width=True,
        )

    if not evol.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                chart_volume_fraude_jour(
                    evol, title="Volume quotidien : opérations et fraude référence"
                ),
                use_container_width=True,
            )
        with col_b:
            st.plotly_chart(
                chart_completude_jour(
                    evol,
                    title="Part des opérations sans destinataire (complétude)",
                ),
                use_container_width=True,
            )

        fig = go.Figure()
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=float(kpis["taux_alerte_pct"]),
                title={"text": "Couverture détection (% op. avec alerte)"},
                gauge={
                    "axis": {"range": [0, 50]},
                    "bar": {"color": "#0d9488"},
                    "steps": [
                        {"range": [0, 5], "color": "#ecfdf5"},
                        {"range": [5, 20], "color": "#fef3c7"},
                        {"range": [20, 50], "color": "#fee2e2"},
                    ],
                },
            )
        )
        fig.update_layout(height=320)
        apply_plotly(fig)
        st.plotly_chart(fig, use_container_width=True)

    tx = data.transactions()
    if "note_transformation" in tx.columns:
        notes = tx["note_transformation"].notna().mean() * 100
        kpi_strip(
            [
                {
                    "label": "Traçabilité des transformations",
                    "value": f"{notes:.1f} %",
                    "hint": "Opérations avec note métier",
                }
            ]
        )

    section_title("Écarts à surveiller")
    compare = data.query(
        """
        SELECT
            sum(CASE WHEN is_fraud_label THEN 1 ELSE 0 END) AS fraude_label,
            (SELECT count(DISTINCT tx_id) FROM staging.stg_alerts) AS txs_avec_alerte
        FROM staging.stg_transactions
        """
    ).iloc[0]
    comparaison = pd.DataFrame(
        {
            "signal": [
                "Fraude référence (labels)",
                "Transactions avec alerte moteur",
            ],
            "nombre": [int(compare["fraude_label"]), int(compare["txs_avec_alerte"])],
        }
    )
    fig_cmp = px.bar(
        comparaison,
        x="signal",
        y="nombre",
        title="Comparaison signaux : label vs moteur de règles",
        color="signal",
        text="nombre",
        color_discrete_sequence=["#e11d48", "#0d9488"],
    )
    fig_cmp.update_traces(textposition="outside")
    fig_cmp.update_layout(showlegend=False, xaxis_title="", yaxis_title="Nombre")
    st.plotly_chart(apply_plotly(fig_cmp), use_container_width=True)