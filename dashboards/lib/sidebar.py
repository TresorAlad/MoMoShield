from __future__ import annotations

import streamlit as st

NAV_ITEMS = (
    "Vue d'ensemble",
    "Alertes & scores",
    "Comportement des flux",
    "Qualité & supervision",
)


def _init_page() -> None:
    if "momoshield_page" not in st.session_state:
        st.session_state.momoshield_page = NAV_ITEMS[0]


def render_sidebar() -> str:
    _init_page()
    active = st.session_state.momoshield_page

    st.markdown("**MoMoShield**")
    st.caption("Surveillance fraude Mobile Money, Togo")

    for item in NAV_ITEMS:
        if st.button(
            item,
            key=f"nav_{item}",
            use_container_width=True,
            type="primary" if item == active else "secondary",
        ):
            st.session_state.momoshield_page = item
            st.rerun()

    return st.session_state.momoshield_page