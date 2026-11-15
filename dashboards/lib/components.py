from __future__ import annotations

import streamlit as st


def page_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def section_title(title: str) -> None:
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)


def kpi_strip(items: list[dict]) -> None:
    cols = st.columns(len(items))
    for col, item in zip(cols, items, strict=False):
        with col:
            delta = item.get("hint")
            st.metric(item["label"], item["value"], delta=delta)