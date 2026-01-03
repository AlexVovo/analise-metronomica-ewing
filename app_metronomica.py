# =========================================================
# 📦 IMPORTS
# =========================================================
import os
from datetime import date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


# =========================================================
# ⚙️ CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Análise Metronômica – Sarcoma de Ewing",
    layout="wide"
)

st.title("📊 Análise Técnica — Metronômica no Sarcoma de Ewing")
st.caption(
    "Aplicação de análise exploratória e visualização técnica. "
    "Não implica autoria, validação clínica ou responsabilidade científica."
)


# =========================================================
# 📁 PATHS
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIOINFO_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

metro_file = os.path.join(BIOINFO_DIR, "planilha-metronomica-filtrada.xlsx")
baseline_file = os.path.join(BIOINFO_DIR, "1_202407_Baseline.xlsx")


# =========================================================
# 📂 LEITURA DOS DADOS
# =========================================================
@st.cache_data
def load_data():
    metro = pd.read_excel(metro_file) if os.path.exists(metro_file) else pd.DataFrame()
    baseline = pd.read_excel(baseline_file) if os.path.exists(baseline_file) else pd.DataFrame()
    return metro, baseline


metro, baseline = load_data()


# =========================================================
# 🧹 PADRONIZAÇÃO – METRONÔMICA
# =========================================================
if not metro.empty:
    metro.columns = (
        metro.columns.str.lower()
        .str.strip()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(" ", "_")
    )

    if "id_paciente" not in metro.columns:
        for c in metro.columns:
            if c.startswith("id"):
                metro.rename(columns={c: "id_paciente"}, inplace=True)
                break

    ciclo_col = next((c for c in metro.columns if "ciclo" in c), None)
    if ciclo_col is None:
        metro["ciclo"] = 1
        ciclo_col = "ciclo"
else:
    ciclo_col = "ciclo"


# =========================================================
# 🧹 TRATAMENTO – BASELINE
# =========================================================
def calcular_idade(d):
    try:
        d = pd.to_datetime(d)
        hoje = date.today()
        return hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))
    except Exception:
        return None


baseline_data = pd.DataFrame()

if not baseline.empty:
    baseline.columns = baseline.columns.str.lower().str.strip()

    if "data de nascimento" in baseline.columns:
        baseline["idade"] = (
            pd.to_datetime(baseline["data de nascimento"], errors="coerce")
            .apply(calcular_idade)
        )

    remover = [
        "nome", "sobrenome", "iniciais", "rg",
        "instituição", "registro hospitalar",
        "data de nascimento", "data tcle"
    ]

    baseline = baseline[[c for c in baseline.columns if c not in remover]]
    baseline.rename(columns={"id": "id_paciente"}, inplace=True)

    baseline_data = baseline.head(20)


# =========================================================
# 📊 VISUALIZAÇÃO — BASELINE
# =========================================================
st.subheader("📌 Baseline (20 primeiros registros — anonimizado)")
if not baseline_data.empty:
    st.dataframe(baseline_data, use_container_width=True)
else:
    st.info("Base de baseline não disponível.")


# =========================================================
# 📊 RESUMO POR PACIENTE
# =========================================================
def to_float(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return np.nan


for c in ["pesomt", "hemoglobinamt", "leucocitosmt"]:
    if c in metro.columns:
        metro[c] = metro[c].apply(to_float)

if not metro.empty:
    resumo = (
        metro.groupby("id_paciente")
        .agg(
            n_ciclos=("id_paciente", "count"),
            peso_medio=("pesomt", "mean"),
            hb_media=("hemoglobinamt", "mean"),
            leuco_medio=("leucocitosmt", "mean"),
        )
        .reset_index()
    )
else:
    resumo = pd.DataFrame()


st.subheader("🧾 Resumo por paciente")
if not resumo.empty:
    st.dataframe(resumo, use_container_width=True)
else:
    st.info("Dados metronômicos não disponíveis.")


# =========================================================
# 🩸 HEATMAPS DE TOXICIDADE
# =========================================================
st.subheader("🩸 Toxicidades por ciclo (heatmaps)")

tox_cols = [
    ("AnemiaHBMT", "anemiahbmt"),
    ("PlaquetopeniaMT", "plaquetopeniamt"),
    ("NeutropeniaMT", "neutropeniamt"),
    ("NeutropeniaFebreMT", "neutropeniafebremt"),
    ("NauseasMT", "nauseasmt"),
    ("VomitosMT", "vomitosmt"),
    ("MucositeMT", "mucositemt"),
    ("DiarreiaMT", "diarreiamt"),
    ("Renal_CreatinaMT", "renal_creatinamt"),
    ("Hepatica_BT_MT", "hepatica_bt_mt"),
    ("Hepatica_TGO_MT", "hepatica_tgo_mt"),
    ("Hepatica_TGP_MT", "hepatica_tgp_mt"),
]

sns.set(font_scale=0.6)

def grau(x):
    try:
        return int(str(x).split("-")[0])
    except Exception:
        return np.nan


for label, col in tox_cols:
    if col not in metro.columns:
        continue

    df = metro.copy()
    df[col] = df[col].apply(grau)

    tabela = df.pivot_table(
        index=ciclo_col,
        columns="id_paciente",
        values=col,
        aggfunc="max"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(tabela, cmap="Reds", ax=ax, cbar=True)

    ax.set_title(label)
    ax.set_xlabel("Paciente")
    ax.set_ylabel("Ciclo")

    st.pyplot(fig)
    plt.close(fig)


# =========================================================
# 📊 GRÁFICOS DE TOXICIDADE (RESUMO)
# =========================================================
st.subheader("📊 Distribuição dos graus máximos de toxicidade")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Toxicidades hematológicas**")
    tox_hema = pd.DataFrame(
        {
            "AnemiaHBMT": [53.1, 29.2, 11.5, 3.1, 0.0],
            "NeutropeniaMT": [5.2, 11.5, 10.4, 33.3, 36.5],
            "PlaquetopeniaMT": [57.3, 30.2, 2.1, 5.2, 2.1],
        },
        index=["Grau 0", "Grau 1", "Grau 2", "Grau 3", "Grau 4"]
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    tox_hema.T.plot(kind="bar", stacked=True, ax=ax, colormap="YlOrBr")
    ax.set_ylabel("% de pacientes")
    ax.set_xlabel("Toxicidade")
    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.markdown("**Toxicidades não hematológicas**")
    tox_nao_hema = pd.DataFrame(
        {
            "NauseasMT": [72.9, 18.8, 6.3, 2.0, 0.0],
            "VomitosMT": [79.2, 14.6, 4.2, 2.0, 0.0],
            "MucositeMT": [90.6, 6.3, 2.1, 1.0, 0.0],
            "DiarreiaMT": [88.5, 7.3, 3.1, 1.0, 0.0],
            "Renal_CreatinaMT": [95.8, 3.1, 1.0, 0.0, 0.0],
            "Hepatica_BT_MT": [85.4, 9.4, 3.1, 2.1, 0.0],
            "Hepatica_TGO_MT": [80.2, 12.5, 5.2, 2.1, 0.0],
            "Hepatica_TGP_MT": [82.3, 10.4, 5.2, 2.1, 0.0],
        },
        index=["Grau 0", "Grau 1", "Grau 2", "Grau 3", "Grau 4"]
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    tox_nao_hema.T.plot(kind="bar", stacked=True, ax=ax, colormap="YlOrBr")
    ax.set_ylabel("% de pacientes")
    ax.set_xlabel("Toxicidade")
    st.pyplot(fig)
    plt.close(fig)


# =========================================================
# ℹ️ RODAPÉ
# =========================================================
st.caption(
    "Análise técnica baseada nos dados fornecidos. "
    "A aplicação limita-se à organização, sumarização e visualização das informações."
)
