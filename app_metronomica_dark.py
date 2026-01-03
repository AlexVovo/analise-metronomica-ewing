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
# 📁 PATHS — ROBUSTO PARA DEPLOY
# =========================================================
PROJECT_ROOT = os.getcwd()

METRO_FILE = os.path.join(PROJECT_ROOT, "planilha-metronomica-filtrada.xlsx")
BASELINE_FILE = os.path.join(PROJECT_ROOT, "1_202407_Baseline.xlsx")

# =========================================================
# 📁 PATHS
# =========================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# METRO_FILE = os.path.join(BASE_DIR, "planilha-metronomica-filtrada.xlsx")
# BASELINE_FILE = os.path.join(BASE_DIR, "1_202407_Baseline.xlsx")


# =========================================================
# 🌙 CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Relatório Técnico – Metronômica no Ewing",
    layout="wide"
)

# =========================================================
# 📌 TÍTULO
# =========================================================
st.title("📊 Relatório Técnico – Tratamento Metronômico no Sarcoma de Ewing")
st.caption(
    "Análise técnica descritiva dos dados clínicos e laboratoriais • "
    "Documento exploratório sem atribuição de autoria científica"
)

# =========================================================
# 📊 DADOS DEMOGRÁFICOS
# =========================================================
st.header("📊 Dados demográficos")

st.markdown("""
<p style="text-align: justify;">
A tabela abaixo mostra a porcentagem de cada variável relacionada aos pacientes analisados
no estudo. Cada porcentagem foi calculada baseada no número de pacientes (n) que aderiram
à metronômica (n=96), não aderiram (n=138). Também foi calculado para toda a coorte (n=234).
</p>
""", unsafe_allow_html=True)

demo_df = pd.DataFrame({
    "Variável": [
        "Gênero (Masculino)",
        "Gênero (Feminino)",
        "Local (Pélvico)",
        "Local (Não pélvico)",
        "Tamanho do tumor (> 8 cm)",
        "Tamanho do tumor (< 8 cm)",
        "Idade (> 14 anos)",
        "Idade (< 14 anos)",
        "Range",
        "Média",
    ],
    "Metronômica (sim) - n=96": [
        "58 (60.4%)",
        "38 (39.6%)",
        "19 (19.8%)",
        "77 (80.2%)",
        "46 (47.9%)",
        "50 (52.1%)",
        "26 (27.1%)",
        "70 (72.9%)",
        "1.06 – 26.75",
        "11.17",
    ],
    "Metronômica (não) - n=138": [
        "77 (55.8%)",
        "61 (44.2%)",
        "23 (16.7%)",
        "115 (83.3%)",
        "71 (51.4%)",
        "67 (48.6%)",
        "42 (30.4%)",
        "96 (69.6%)",
        "0.16 – 19.06",
        "10.60",
    ],
    "Total - n=234": [
        "135 (57.7%)",
        "99 (42.3%)",
        "42 (17.9%)",
        "192 (82.1%)",
        "117 (50.0%)",
        "117 (50.0%)",
        "68 (29.1%)",
        "166 (70.9%)",
        "0.16 – 26.75",
        "10.83",
    ],
})

st.subheader("Distribuição dos pacientes por características")
st.dataframe(demo_df, use_container_width=True)

st.divider()


# =========================================================
# 🌑 DARK MODE (CSS)
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0f2233;
    color: #e6eef5;
}
h1, h2, h3, h4 {
    color: #7fd6a4;
}
.block-container {
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] {
    background-color: #0c1c2b;
    border-left: 3px solid #2e7d5b;
}
[data-testid="stDataFrame"] {
    background-color: #12293d;
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

baseline.columns = (
    baseline.columns.str.lower()
    .str.strip()
)

# Garantir id_paciente
if "id_paciente" not in metro.columns:
    for c in metro.columns:
        if c.startswith("id"):
            metro.rename(columns={c: "id_paciente"}, inplace=True)
            break

# Garantir ciclo
metro = metro.sort_values("id_paciente")
metro["ciclo"] = metro.groupby("id_paciente").cumcount() + 1

# =========================================================
# 📂 LEITURA DOS DADOS
# =========================================================
# @st.cache_data
# def load_data():
  #  metro = pd.read_excel(METRO_FILE) if os.path.exists(METRO_FILE) else pd.DataFrame()
   # baseline = pd.read_excel(BASELINE_FILE) if os.path.exists(BASELINE_FILE) else pd.DataFrame()
    #return metro, baseline

#metro, baseline = load_data()

# =========================================================
# 🚨 VERIFICAÇÃO DE ARQUIVOS (DEPLOY SAFE)
# =========================================================
PROJECT_ROOT = os.getcwd()

METRO_FILE = os.path.join(PROJECT_ROOT, "planilha-metronomica-filtrada.xlsx")
BASELINE_FILE = os.path.join(PROJECT_ROOT, "1_202407_Baseline.xlsx")

if not os.path.exists(METRO_FILE):
    st.error(
        "❌ Arquivo planilha-metronomica-filtrada.xlsx não encontrado.\n\n"
        f"📂 Diretório atual: {PROJECT_ROOT}\n\n"
        f"📄 Arquivos disponíveis:\n{os.listdir(PROJECT_ROOT)}"
    )
    st.stop()

if not os.path.exists(BASELINE_FILE):
    st.error(
        "❌ Arquivo 1_202407_Baseline.xlsx não encontrado.\n\n"
        f"📂 Diretório atual: {PROJECT_ROOT}\n\n"
        f"📄 Arquivos disponíveis:\n{os.listdir(PROJECT_ROOT)}"
    )
    st.stop()

    


# =========================================================
# 🚨 VERIFICAÇÃO
# =========================================================
# if metro.empty:
  #  st.error(
   #     "❌ Arquivo planilha-metronomica-filtrada.xlsx não encontrado ou vazio.\n\n"
    #    f"Esperado em: {BASE_DIR}"
    # )
    # st.stop()


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

# =========================================================
# 🔧 GARANTIA DE id_paciente
# =========================================================
if "id_paciente" not in metro.columns:
    for c in metro.columns:
        if c.startswith("id"):
            metro.rename(columns={c: "id_paciente"}, inplace=True)
            break

if "id_paciente" not in metro.columns:
    st.error("❌ Coluna de identificação do paciente não encontrada.")
    st.stop()

# =========================================================
# 🔧 GARANTIA ÚNICA DE CICLO
# =========================================================
metro = metro.sort_values("id_paciente")
metro["ciclo"] = metro.groupby("id_paciente").cumcount() + 1
ciclo_col = "ciclo"


# =========================================================
# 📌 BASELINE
# =========================================================
def calcular_idade(d):
    try:
        d = pd.to_datetime(d)
        hoje = date.today()
        return hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))
    except:
        return None

baseline_view = pd.DataFrame()

if not baseline.empty:
    baseline.columns = baseline.columns.str.lower().str.strip()
    if "data de nascimento" in baseline.columns:
        baseline["idade"] = pd.to_datetime(
            baseline["data de nascimento"], errors="coerce"
        ).apply(calcular_idade)

    remover = [
        "nome","sobrenome","iniciais","rg",
        "instituição","registro hospitalar",
        "data de nascimento","data tcle"
    ]

    baseline = baseline[[c for c in baseline.columns if c not in remover]]
    baseline.rename(columns={"id": "id_paciente"}, inplace=True)
    baseline_view = baseline.head(20)

st.header("📌 Baseline (20 primeiros registros — anonimizado)")
st.dataframe(baseline_view, use_container_width=True)
st.divider()


# =========================================================
# 🧾 Nº DE CICLOS POR PACIENTE
# =========================================================


cycles_df = pd.DataFrame(
    [["N_pacientes", 96,93,90,88,82,74,71,71,69,68,66,62,35,15,4,2,1,1,1]],
    columns=["Métrica"] + [f"Ciclo_{i}" for i in range(1, 20)]
)

st.subheader("🧾 Número de pacientes por ciclo")
st.dataframe(cycles_df, use_container_width=True)


# =========================================================
# 🧾 HEATMAP — PRESENÇA DE CICLOS
# =========================================================
st.subheader("🧾 Heatmap — Presença de ciclos por paciente")

df_presenca = metro[["id_paciente", "ciclo"]].copy()
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

st.markdown("""
<p style="text-align: justify;">
O número de ciclos por paciente foi quantificado para avaliar a permanência dos pacientes
em tratamento ao longo do tempo. Observa-se uma redução progressiva do número de pacientes
avaliados em ciclos mais avançados, refletindo descontinuação, término de tratamento ou
ausência de dados.
</p>
""", unsafe_allow_html=True)


# =========================================================
# 📊 RESUMO POR PACIENTE
# =========================================================
def to_float(x):
    try:
        return float(str(x).replace(",", "."))
    except:
        return np.nan

for col in ["pesomt", "hemoglobinamt", "leucocitosmt"]:
    if col in metro.columns:
        metro[col] = metro[col].apply(to_float)

resumo_df = (
    metro.groupby("id_paciente")
    .agg(
        n_ciclos=("id_paciente", "count"),
        peso_medio=("pesomt", "mean"),
        hb_media=("hemoglobinamt", "mean"),
        leuco_medio=("leucocitosmt", "mean"),
    )
    .reset_index()
    .sort_values("n_ciclos", ascending=False)
)

st.subheader("📊 Resumo por paciente")
st.dataframe(resumo_df, use_container_width=True)

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
# 🩸 HEATMAPS DE TOXICIDADE (2 POR LINHA)
# =========================================================
st.header("🩸 Toxicidade — Heatmaps por ciclo")

tox_cols = [
    ("AnemiaHBMT", "anemiahbmt", "Hemoglobina baixa — queda de Hb."),
    ("PlaquetopeniaMT", "plaquetopeniamt", "Plaquetas reduzidas."),
    ("NeutropeniaMT", "neutropeniamt", "Neutrófilos reduzidos."),
    ("NeutropeniaFebreMT", "neutropeniafebremt", "Neutropenia associada à febre."),
    ("NauseasMT", "nauseasmt", "Náuseas durante o tratamento."),
    ("VomitosMT", "vomitosmt", "Vômitos."),
    ("MucositeMT", "mucositemt", "Inflamação da mucosa oral."),
    ("DiarreiaMT", "diarreiamt", "Diarreia."),
    ("Renal_CreatinaMT", "renal_creatinamt", "Alterações de creatinina."),
    ("Hepatica_BT_MT", "hepatica_bt_mt", "Bilirrubina total."),
    ("Hepatica_TGO_MT", "hepatica_tgo_mt", "Alterações de TGO."),
    ("Hepatica_TGP_MT", "hepatica_tgp_mt", "Alterações de TGP."),
]

def grau(x):
    try:
        return int(str(x).split("-")[0])
    except:
        return np.nan

# processar heatmaps em pares
for i in range(0, len(tox_cols), 2):
    cols = st.columns(2)

    for j, (label, col, descricao) in enumerate(tox_cols[i:i+2]):
        with cols[j]:
            if col not in metro.columns:
                st.warning(f"Coluna {label} não encontrada.")
                continue

            df = metro.copy()
            df[col] = df[col].apply(grau)

            tabela = (
                df.pivot_table(
                    index="ciclo",
                    columns="id_paciente",
                    values=col,
                    aggfunc="max"
                )
                .fillna(0)
            )

            fig, ax = plt.subplots(figsize=(7, 4))
            sns.heatmap(tabela, cmap="Reds", ax=ax, cbar=True)
            ax.set_title(label)
            ax.set_xlabel("Paciente")
            ax.set_ylabel("Ciclo")

            st.pyplot(fig)
            plt.close(fig)

            st.caption(descricao)

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
