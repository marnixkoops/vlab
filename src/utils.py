import io

import pandas as pd
import streamlit as st


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_session_state():
    return SessionState(mode=None)


def set_page_config() -> None:
    st.set_page_config(
        page_title="Team Visma | Lease a Bike Segment Analytics",
        page_icon="🚴‍♂️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def excel_download_button(
    df: pd.DataFrame, filename: str, label: str = "Download data"
):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False)
    writer.close()
    output.seek(0)
    button = st.download_button(
        label=label,
        data=output,
        file_name=f"{filename}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    return button
