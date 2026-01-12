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
from pathlib import Path

# =========================================================
# 🌙 CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Relatório Técnico – Metronômica no Ewing",
    layout="wide"
)

# =========================================================
# 📁 LOCALIZAÇÃO ROBUSTA DOS ARQUIVOS
# =========================================================
PROJECT_ROOT = Path.cwd()

def find_file(filename: str) -> Path:
    matches = list(PROJECT_ROOT.rglob(filename))
    if not matches:
        st.error(
            f"❌ Arquivo '{filename}' não encontrado.\n\n"
            f"Diretório base: {PROJECT_ROOT}"
        )
        st.stop()
    return matches[0]

METRO_FILE = find_file("planilha-metronomica-filtrada.xlsx")
BASELINE_FILE = find_file("1_202407_Baseline.xlsx")

# =========================================================
# 📌 TÍTULO
# =========================================================
st.title("📊 Relatório Técnico – Tratamento Metronômico no Sarcoma de Ewing")
st.caption(
    "Análise técnica descritiva dos dados clínicos e laboratoriais • "
    "Unidade de análise: ciclos de tratamento (limitados a 12 ciclos clínicos)"
)

# =========================================================
# 🌑 DARK MODE
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0f2233;
    color: #e6eef5;
}
h1, h2, h3 {
    color: #7fd6a4;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 📂 LEITURA DOS DADOS
# =========================================================
@st.cache_data
def load_data():
    metro = pd.read_excel(METRO_FILE)
    baseline = pd.read_excel(BASELINE_FILE)
    return metro, baseline

metro, baseline = load_data()

# =========================================================
# 🧹 PADRONIZAÇÃO DAS COLUNAS
# =========================================================
metro.columns = (
    metro.columns.str.lower()
    .str.strip()
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    .str.replace(" ", "_")
)

baseline.columns = baseline.columns.str.lower().str.strip()

# =========================================================
# 🔧 GARANTIA DE id_paciente
# =========================================================
if "id_paciente" not in metro.columns:
    for c in metro.columns:
        if c.startswith("id"):
            metro.rename(columns={c: "id_paciente"}, inplace=True)
            break

if "id_paciente" not in metro.columns:
    st.error("❌ Coluna id_paciente não encontrada.")
    st.stop()

# =========================================================
# 🔧 CRIAÇÃO DO CICLO (SEQUENCIAL POR PACIENTE)
# =========================================================
metro = metro.sort_values(["id_paciente"])
metro["ciclo"] = metro.groupby("id_paciente").cumcount() + 1

# =========================================================
# 🔴 CORTE CLÍNICO: LIMITE DE 12 CICLOS
# =========================================================
metro = metro[metro["ciclo"] <= 12]

# =========================================================
# 👀 VISUALIZAÇÃO EXPLÍCITA DO NÚMERO DE CICLOS
# =========================================================
st.metric(
    "🔁 Número máximo de ciclos considerados na análise",
    int(metro["ciclo"].max())
)

st.markdown("""
<p style="text-align: justify;">
Embora alguns pacientes apresentem registros longitudinais além do 12º ponto de acompanhamento,
a análise foi deliberadamente limitada aos <b>12 ciclos clínicos previstos em protocolo</b>,
de modo a garantir comparabilidade temporal entre os pacientes e coerência metodológica.
</p>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# 📌 BASELINE (VISUALIZAÇÃO)
# =========================================================
st.header("📌 Baseline (20 primeiros registros – anonimizado)")

baseline_view = baseline.head(20) if not baseline.empty else pd.DataFrame()
st.dataframe(baseline_view, use_container_width=True)

st.divider()

# =========================================================
# 🧾 NÚMERO DE PACIENTES POR CICLO
# =========================================================
cycles_df = (
    metro.groupby("ciclo")["id_paciente"]
    .nunique()
    .reset_index(name="N_pacientes")
)

st.subheader("🧾 Número de pacientes por ciclo")
st.dataframe(cycles_df, use_container_width=True)

# =========================================================
# 🔥 HEATMAP — PRESENÇA DE CICLOS
# =========================================================
st.subheader("🧾 Heatmap — Presença de ciclos")

df_presenca = metro.copy()
df_presenca["presente"] = 1

hm_presenca = (
    df_presenca
    .pivot_table(
        index="ciclo",
        columns="id_paciente",
        values="presente",
        aggfunc="max"
    )
    .fillna(0)
)

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(hm_presenca, cmap="Blues", ax=ax)
ax.set_xlabel("Paciente")
ax.set_ylabel("Ciclo")
st.pyplot(fig)
plt.close(fig)

st.divider()

# =========================================================
# 📊 RESUMO CLÍNICO POR CICLO
# =========================================================
def to_float(x):
    try:
        return float(str(x).replace(",", "."))
    except:
        return np.nan

for col in ["pesomt", "hemoglobinamt", "leucocitosmt"]:
    if col in metro.columns:
        metro[col] = metro[col].apply(to_float)

resumo_ciclo_df = (
    metro.groupby("ciclo")
    .agg(
        n_registros=("id_paciente", "count"),
        peso_medio=("pesomt", "mean"),
        hb_media=("hemoglobinamt", "mean"),
        leuco_medio=("leucocitosmt", "mean"),
    )
    .reset_index()
)

st.subheader("📊 Resumo clínico por ciclo")
st.dataframe(resumo_ciclo_df, use_container_width=True)

# =========================================================
# 🧪 FUNÇÃO DE GRAU
# =========================================================
def grau(x):
    try:
        return int(str(x).split("-")[0])
    except:
        return np.nan

# =========================================================
# 🩸 DISTRIBUIÇÃO DE TOXICIDADE POR CICLO
# =========================================================
st.header("🩸 Distribuição de toxicidades por ciclo")

tox_cols = [
    ("AnemiaHBMT", "anemiahbmt"),
    ("NeutropeniaMT", "neutropeniamt"),
    ("PlaquetopeniaMT", "plaquetopeniamt"),
    ("NauseasMT", "nauseasmt"),
    ("VomitosMT", "vomitosmt"),
    ("MucositeMT", "mucositemt"),
    ("DiarreiaMT", "diarreiamt"),
    ("Renal_CreatinaMT", "renal_creatinamt"),
    ("Hepatica_TGO_MT", "hepatica_tgo_mt"),
    ("Hepatica_TGP_MT", "hepatica_tgp_mt"),
]

for label, col in tox_cols:
    if col not in metro.columns:
        continue

    df = metro.copy()
    df["grau"] = df[col].apply(grau)

    dist = (
        df.groupby(["ciclo", "grau"])
        .size()
        .unstack(fill_value=0)
    )

    dist_pct = dist.div(dist.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 4))
    dist_pct.plot(kind="bar", stacked=True, ax=ax, colormap="Reds")

    ax.set_title(f"{label} — Distribuição por ciclo")
    ax.set_xlabel("Ciclo")
    ax.set_ylabel("Percentual de ciclos (%)")

    st.pyplot(fig)
    plt.close(fig)

# =========================================================
# 🔥 HEATMAP — TOXICIDADE MÉDIA POR CICLO
# =========================================================
st.header("🔥 Heatmaps — Intensidade média por ciclo")

for label, col in tox_cols:
    if col not in metro.columns:
        continue

    heat = (
        metro.copy()
        .assign(grau=lambda d: d[col].apply(grau))
        .groupby("ciclo")["grau"]
        .mean()
        .to_frame()
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(heat, cmap="Reds", annot=True, ax=ax)

    ax.set_title(label)
    ax.set_ylabel("Ciclo")

    st.pyplot(fig)
    plt.close(fig)

# =========================================================
# 📄 RELATÓRIO FINAL
# =========================================================
st.header("📄 Relatório Geral — Análise por ciclos")

st.markdown("""
<p style="text-align: justify;">
Este relatório apresenta uma análise técnica descritiva dos dados clínicos e laboratoriais
de pacientes submetidos ao tratamento metronômico no Sarcoma de Ewing, considerando como
unidade de análise os ciclos de tratamento, limitados aos 12 ciclos clínicos previstos
em protocolo.
</p>

<p style="text-align: justify;">
A análise por ciclos permite avaliar a evolução temporal das toxicidades e parâmetros
laboratoriais, identificando padrões de aparecimento precoce ou tardio de eventos adversos,
bem como variações ao longo do tratamento.
</p>

<p style="text-align: justify;">
De forma geral, observa-se predominância de toxicidades leves a moderadas, com eventos
graves concentrando-se em ciclos específicos, especialmente para toxicidades hematológicas.
</p>

<p style="text-align: justify;">
Este relatório fornece uma base sólida para análises clínicas mais aprofundadas e
interpretação científica do perfil de segurança do tratamento metronômico.
</p>
""", unsafe_allow_html=True)
