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
# 🌙 CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Relatório Técnico – Metronômica no Ewing",
    layout="wide"
)

# =========================================================
# 📌 TÍTULO PRINCIPAL
# =========================================================
st.title("📊 Relatório Técnico – Tratamento Metronômico no Sarcoma de Ewing")
st.caption(
    "Análise técnica descritiva dos dados clínicos e laboratoriais • "
    "Documento exploratório sem atribuição de autoria científica"
)

# =========================================================
# 🌑 DARK MODE (CSS – BASE + TABELAS)
# =========================================================
st.markdown("""
<style>

/* ===== BASE ===== */
html, body, [class*="css"] {
    background-color: #0f2233 !important;
    color: #e6eef5 !important;
}

/* ===== TÍTULOS ===== */
h1, h2, h3, h4 {
    color: #7fd6a4 !important;
}

/* ===== TEXTO ===== */
p, span, li, label {
    color: #e6eef5 !important;
}

/* ===== CONTAINER ===== */
.block-container {
    padding-top: 1.5rem;
    background-color: #0f2233 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: #0c1c2b !important;
    border-left: 3px solid #2e7d5b;
}
[data-testid="stSidebar"] * {
    color: #e6eef5 !important;
}

/* =========================================================
   🟦 DATAFRAMES – DARK MODE REAL
   ========================================================= */

/* container */
[data-testid="stDataFrame"], 
[data-testid="stTable"] {
    background-color: #12293d !important;
}

/* header */
[data-testid="stDataFrame"] thead tr th {
    background-color: #16344f !important;
    color: #9fe0bd !important;
    border-bottom: 1px solid #2e7d5b !important;
}

/* body cells */
[data-testid="stDataFrame"] tbody tr td {
    background-color: #12293d !important;
    color: #e6eef5 !important;
    border-bottom: 1px solid #1f3a52 !important;
}

/* hover */
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #1a3a55 !important;
}

/* index column */
[data-testid="stDataFrame"] tbody tr th {
    background-color: #12293d !important;
    color: #9fe0bd !important;
}

/* scrollbar */
[data-testid="stDataFrame"] ::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}
[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
    background-color: #2e7d5b;
    border-radius: 4px;
}

/* ===== INPUTS ===== */
input, textarea, select {
    background-color: #12293d !important;
    color: #e6eef5 !important;
    border: 1px solid #2e7d5b !important;
}

/* ===== BOTÕES ===== */
button {
    background-color: #1f6f54 !important;
    color: #ffffff !important;
    border-radius: 6px;
}
button:hover {
    background-color: #2e7d5b !important;
}

/* ===== CHECKBOX / RADIO ===== */
input[type="checkbox"], input[type="radio"] {
    accent-color: #7fd6a4;
}

/* ===== GRÁFICOS ===== */
figure, svg {
    background-color: #0f2233 !important;
}

</style>
""", unsafe_allow_html=True)


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
# 🧹 BASELINE
# =========================================================
def calcular_idade(d):
    try:
        d = pd.to_datetime(d)
        hoje = date.today()
        return hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))
    except Exception:
        return None

baseline_view = pd.DataFrame()

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
    baseline_view = baseline.head(20)


# =========================================================
# 🧾 Nº DE CICLOS POR PACIENTE
# =========================================================
st.header("🧾 Nº de ciclos por paciente")

st.markdown("""
<p style="text-align: justify;">
O número de ciclos por paciente foi quantificado para avaliar a permanência dos pacientes
em tratamento ao longo do tempo. Observa-se uma redução progressiva do número de pacientes
avaliados em ciclos mais avançados, refletindo descontinuação, término de tratamento ou
ausência de dados.
</p>
""", unsafe_allow_html=True)

cycles_df = pd.DataFrame(
    [["N_pacientes", 96,93,90,88,82,74,71,71,69,68,66,62,35,15,4,2,1,1,1]],
    columns=[
        "Metric",
        "Ciclo_1","Ciclo_2","Ciclo_3","Ciclo_4","Ciclo_5",
        "Ciclo_6","Ciclo_7","Ciclo_8","Ciclo_9","Ciclo_10",
        "Ciclo_11","Ciclo_12","Ciclo_13","Ciclo_14","Ciclo_15",
        "Ciclo_16","Ciclo_17","Ciclo_18","Ciclo_19"
    ]
)

st.dataframe(cycles_df, use_container_width=True)


# =========================================================
# 📋 Nº DE PACIENTES AVALIADOS POR CICLO E TOXICIDADE
# =========================================================
st.header("📋 Número de pacientes avaliados por ciclo e toxicidade")

st.markdown("""
<p style="text-align: justify;">
A tabela abaixo mostra o número de pacientes avaliados em cada ciclo de tratamento
para diferentes tipos de toxicidade. A linha <b>N_pacientes</b> indica o total de
pacientes disponíveis em cada ciclo, enquanto <b>eventos</b> representa a ocorrência
da toxicidade e <b>Não avaliado</b> indica ausência de avaliação no ciclo.
</p>
""", unsafe_allow_html=True)

tox_ciclo_df = pd.DataFrame([
    ["N_pacientes", 96,93,90,88,82,74,71,71,69,68,66,62,35,15,4,2,1,1,1],
    ["AnemiaHBMT - eventos", 30,16,16,14,12,9,13,13,10,11,10,8,5,1,0,0,0,0,0],
    ["AnemiaHBMT - Não avaliado", 7,7,5,5,6,0,3,1,2,2,2,2,1,0,1,0,0,0,0],
    ["DiarreiaMT - eventos", 1,0,2,4,1,0,2,2,2,4,2,1,0,0,0,0,0,0,0],
    ["DiarreiaMT - Não avaliado", 4,3,1,3,1,0,0,2,1,0,0,1,1,0,0,0,0,0,0],
    ["Hepatica_BT_MT - eventos", 3,4,2,2,2,1,1,1,1,0,1,0,0,0,0,0,0,0,0],
    ["Hepatica_BT_MT - Não avaliado", 12,14,14,12,14,12,13,16,15,13,12,13,4,3,1,1,1,1,1],
    ["Hepatica_TGO_MT - eventos", 7,6,3,3,2,4,1,4,1,0,3,1,1,0,0,0,0,0,0],
    ["Hepatica_TGO_MT - Não avaliado", 13,15,14,14,15,10,12,13,14,14,11,13,4,3,1,1,1,1,1],
    ["Hepatica_TGP_MT - eventos", 10,12,6,4,6,4,6,6,5,1,4,3,4,1,0,0,0,0,0],
    ["Hepatica_TGP_MT - Não avaliado", 12,13,15,10,13,10,14,14,15,13,11,14,4,3,1,1,1,1,1],
], columns=cycles_df.columns)

st.dataframe(tox_ciclo_df, use_container_width=True)

st.markdown("""
<p style="text-align: justify;">
Cada gráfico representa a intensidade máxima de toxicidade observada por paciente
em cada ciclo de tratamento. Cores mais intensas indicam maior gravidade ou maior
frequência de eventos.
</p>
""", unsafe_allow_html=True)


# =========================================================
# 📊 DADOS DEMOGRÁFICOS
# =========================================================
st.header("📊 Dados demográficos")

demo = pd.DataFrame({
    "Variável": ["Gênero (Masculino)", "Gênero (Feminino)"],
    "Metronômica (sim)": ["58 (60.4%)", "38 (39.6%)"],
    "Metronômica (não)": ["77 (55.8%)", "61 (44.2%)"],
    "Total": ["135 (57.7%)", "99 (42.3%)"]
})

st.dataframe(demo, use_container_width=True)


# =========================================================
# 📌 BASELINE
# =========================================================
st.header("📌 Baseline (20 primeiros registros — anonimizado)")
st.dataframe(baseline_view, use_container_width=True)


# =========================================================
# 🩸 HEATMAPS DE TOXICIDADE
# =========================================================
st.header("🩸 Toxicidade — Heatmaps por ciclo")

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
    sns.heatmap(tabela, cmap="Reds", ax=ax)
    ax.set_title(label)
    ax.set_xlabel("Paciente")
    ax.set_ylabel("Ciclo")

    st.pyplot(fig)

    descricao = {
        "AnemiaHBMT": "Hemoglobina baixa — queda de Hb.",
        "PlaquetopeniaMT": "Plaquetas reduzidas.",
        "NeutropeniaMT": "Neutrófilos reduzidos.",
        "NeutropeniaFebreMT": "Neutropenia associada à febre.",
        "NauseasMT": "Náuseas durante o tratamento.",
        "VomitosMT": "Vômitos.",
        "MucositeMT": "Inflamação da mucosa oral.",
        "DiarreiaMT": "Diarreia.",
        "Renal_CreatinaMT": "Alterações de creatinina.",
        "Hepatica_BT_MT": "Bilirrubina total.",
        "Hepatica_TGO_MT": "Alterações de TGO.",
        "Hepatica_TGP_MT": "Alterações de TGP.",
    }

    st.caption(descricao.get(label, ""))
    plt.close(fig)


# =========================================================
# 📊 DISTRIBUIÇÃO DOS GRAUS
# =========================================================
st.header("📊 Distribuição dos graus máximos de toxicidade")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Toxicidades hematológicas")
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
    ax.set_xlabel("Toxicidade")
    ax.set_ylabel("Percentual de pacientes (%)")

    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("Toxicidades não hematológicas")
    tox_nao_hema = pd.DataFrame(
        {
            "NauseasMT": [76.0, 16.7, 5.2, 0.0, 0.0],
            "VomitosMT": [80.2, 9.4, 8.3, 0.0, 0.0],
            "MucositeMT": [89.6, 3.1, 5.2, 0.0, 0.0],
            "DiarreiaMT": [84.4, 11.5, 2.1, 0.0, 0.0],
            "Renal_CreatinaMT": [90.6, 5.2, 0.0, 1.0, 0.0],
            "Hepatica_BT_MT": [90.6, 3.1, 1.0, 0.0, 1.0],
            "Hepatica_TGO_MT": [82.3, 10.4, 1.0, 2.1, 1.0],
            "Hepatica_TGP_MT": [77.1, 11.5, 3.1, 2.1, 3.1],
        },
        index=["Grau 0", "Grau 1", "Grau 2", "Grau 3", "Grau 4"]
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    tox_nao_hema.T.plot(kind="bar", stacked=True, ax=ax, colormap="YlOrBr")

    # 🔽 ADICIONE ESTAS DUAS LINHAS
    ax.set_xlabel("Toxicidade")
    ax.set_ylabel("Percentual de pacientes (%)")

    st.pyplot(fig)


# =========================================================
# 📋 TABELAS DE TOXICIDADE
# =========================================================
st.header("📋 Tabela de toxicidade por paciente (hematológicas)")

st.dataframe(pd.DataFrame([
    ["AnemiaHBMT", 96, "51 (53.1%)", "28 (29.2%)", "11 (11.5%)", "3 (3.1%)", "0 (0.0%)", "3 (3.1%)"],
    ["NeutropeniaMT", 96, "5 (5.2%)", "11 (11.5%)", "10 (10.4%)", "32 (33.3%)", "35 (36.5%)", "3 (3.1%)"],
    ["PlaquetopeniaMT", 96, "55 (57.3%)", "29 (30.2%)", "2 (2.1%)", "5 (5.2%)", "2 (2.1%)", "3 (3.1%)"],
], columns=[
    "Toxicidade", "N pacientes", "Grau 0", "Grau 1",
    "Grau 2", "Grau 3", "Grau 4", "Não avaliado"
]), use_container_width=True)


st.header("📋 Tabela de toxicidade por paciente (não hematológicas)")

st.dataframe(pd.DataFrame([
    ["DiarreiaMT", 96, "81 (84.4%)", "11 (11.5%)", "2 (2.1%)", "0 (0.0%)", "0 (0.0%)", "2 (2.1%)"],
    ["Hepatica_BT_MT", 96, "87 (90.6%)", "3 (3.1%)", "1 (1.0%)", "0 (0.0%)", "1 (1.0%)", "4 (4.2%)"],
    ["Hepatica_TGO_MT", 96, "79 (82.3%)", "10 (10.4%)", "1 (1.0%)", "2 (2.1%)", "1 (1.0%)", "3 (3.1%)"],
    ["Hepatica_TGP_MT", 96, "74 (77.1%)", "11 (11.5%)", "3 (3.1%)", "2 (2.1%)", "3 (3.1%)", "3 (3.1%)"],
    ["MucositeMT", 96, "86 (89.6%)", "3 (3.1%)", "5 (5.2%)", "0 (0.0%)", "0 (0.0%)", "2 (2.1%)"],
    ["NauseasMT", 96, "73 (76.0%)", "16 (16.7%)", "5 (5.2%)", "0 (0.0%)", "0 (0.0%)", "2 (2.1%)"],
    ["NeutropeniaFebreMT", 96, "73 (76.0%)", "0 (0.0%)", "0 (0.0%)", "19 (19.8%)", "2 (2.1%)", "2 (2.1%)"],
    ["PerdaDePesoMT", 96, "86 (89.6%)", "6 (6.2%)", "1 (1.0%)", "0 (0.0%)", "0 (0.0%)", "3 (3.1%)"],
    ["Renal_CreatinaMT", 96, "87 (90.6%)", "5 (5.2%)", "0 (0.0%)", "1 (1.0%)", "0 (0.0%)", "3 (3.1%)"],
    ["VomitosMT", 96, "77 (80.2%)", "9 (9.4%)", "8 (8.3%)", "0 (0.0%)", "0 (0.0%)", "2 (2.1%)"],
], columns=[
    "Toxicidade", "N pacientes", "Grau 0", "Grau 1",
    "Grau 2", "Grau 3", "Grau 4", "Não avaliado"
]), use_container_width=True)


# =========================================================
# 📄 RELATÓRIO GERAL — TEXTO COMPLETO
# =========================================================
st.header("📄 Relatório Geral — Análise Técnica")

st.markdown("""
<p style="text-align: justify;">
Este relatório apresenta uma análise detalhada dos dados clínicos e laboratoriais
de pacientes submetidos ao tratamento metronômico no contexto do Sarcoma de Ewing,
com foco na caracterização demográfica, avaliação basal, acompanhamento por ciclos
e análise de toxicidades hematológicas e não hematológicas.
</p>

<h3>🔧 Descrição do processamento dos dados</h3>
<p style="text-align: justify;">
Os dados utilizados neste relatório foram obtidos a partir de planilhas estruturadas
contendo informações clínicas, laboratoriais e de toxicidade por paciente.
O script executa inicialmente a padronização dos nomes de colunas, tratamento de valores
ausentes, anonimização de dados sensíveis e consolidação das informações por paciente
e por ciclo de tratamento.
</p>

<h3>📊 Dados demográficos</h3>
<p style="text-align: justify;">
A análise demográfica descreve a distribuição dos pacientes segundo sexo e adesão
ao tratamento metronômico, permitindo uma visão geral da composição da coorte avaliada.
Esses dados servem como base para contextualização dos resultados clínicos subsequentes.
</p>

<h3>📌 Avaliação Baseline</h3>
<p style="text-align: justify;">
A tabela de baseline apresenta os primeiros registros disponíveis, de forma anonimizada,
contemplando características clínicas iniciais, dados diagnósticos e informações relevantes
para o acompanhamento longitudinal dos pacientes.
</p>

<h3>🔁 Análise por ciclos</h3>
<p style="text-align: justify;">
O número de ciclos por paciente foi quantificado para avaliar a permanência dos pacientes
em tratamento ao longo do tempo. Observa-se uma redução progressiva do número de pacientes
avaliados em ciclos mais avançados, refletindo descontinuação, término de tratamento ou
ausência de dados.
</p>

<h3>🩸 Toxicidades hematológicas</h3>
<p style="text-align: justify;">
As toxicidades hematológicas foram avaliadas considerando o grau máximo apresentado por
cada paciente ao longo do tratamento. Os resultados indicam maior prevalência de eventos
moderados a graves para neutropenia, enquanto anemia e plaquetopenia apresentaram, em sua
maioria, graus leves ou ausência de toxicidade significativa.
</p>

<h3>🧪 Toxicidades não hematológicas</h3>
<p style="text-align: justify;">
As toxicidades não hematológicas foram analisadas de forma semelhante, com destaque para
eventos gastrointestinais e alterações hepáticas. A maioria dos pacientes apresentou
ausência de toxicidade ou eventos de baixo grau, sendo eventos de grau elevado menos
frequentes.
</p>

<h3>📌 Considerações finais</h3>
<p style="text-align: justify;">
De forma geral, os resultados sugerem que o tratamento metronômico apresenta um perfil
de toxicidade predominantemente leve a moderado, com eventos graves ocorrendo em uma
proporção limitada da coorte. Este relatório fornece uma base descritiva robusta para
análises futuras e interpretações clínicas mais aprofundadas.
</p>
""", unsafe_allow_html=True)
