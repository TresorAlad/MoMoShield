from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboards.lib.design_tokens import INK, PLOTLY_COLORWAY, PLOTLY_FONT

PLOTLY_LAYOUT = dict(
    font=dict(family=PLOTLY_FONT, color=INK, size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=52, b=20),
    colorway=PLOTLY_COLORWAY,
)

_THEME_PATH = Path(__file__).resolve().parents[1] / "theme.css"
_THEME_SESSION_KEY = "_momoshield_theme_v2"


def inject_theme() -> None:
    if st.session_state.get(_THEME_SESSION_KEY):
        return
    css = _THEME_PATH.read_text(encoding="utf-8")
    st.html(
        f"""<script>
        (function() {{
          var s = document.createElement("style");
          s.textContent = {json.dumps(css)};
          document.head.appendChild(s);
        }})();
        </script>""",
        unsafe_allow_javascript=True,
    )
    st.session_state[_THEME_SESSION_KEY] = True


def kpi_card(label: str, value: str, hint: str = "", tone: str = "default") -> None:
    from dashboards.lib.components import kpi_strip

    kpi_strip([{"label": label, "value": value, "hint": hint or None}])


def apply_plotly(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0", zeroline=False)
    return fig