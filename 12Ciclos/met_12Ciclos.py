# =========================================================
# IMPORTS
# =========================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path
from io import BytesIO

# =========================================================
# FUNÇÃO EXTRAI GRAU
# =========================================================
def extrair_grau(x):

    if pd.isna(x):
        return np.nan

    try:
        return int(str(x).split("-")[0])

    except:
        return np.nan

# =========================================================
# CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Relatório Técnico – Metronômica no Ewing",
    layout="wide"
)

st.title("Relatório Técnico – Toxicidade Metronômica no Sarcoma de Ewing")

# =========================================================
# ESTILO VISUAL
# =========================================================
st.markdown("""
<style>

h1 {font-size:40px;font-weight:700;}
h2 {font-size:30px;margin-top:35px;}

.styled-table {
border-collapse: collapse;
margin-top: 20px;
font-size: 16px;
width: 100%;
}

.styled-table thead tr {
background-color: #1f4e79;
color: white;
text-align: center;
}

.styled-table th,
.styled-table td {
padding: 10px;
border: 1px solid #ddd;
text-align: center;
}

.styled-table tbody tr:nth-child(even) {
background-color: #f2f2f2;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOCALIZAÇÃO DOS ARQUIVOS
# =========================================================
ROOT = Path(__file__).parent

def find_file(name):
    files = list(ROOT.rglob(name))
    if not files:
        st.error(f"Arquivo '{name}' não encontrado")
        st.stop()
    return files[0]

METRO_FILE = find_file("9_202407_Metronomica.xlsx")
BASELINE_FILE = find_file("1_202407_Baseline.xlsx")
DEMOG_FILE = find_file("Tabela-ewing_estatistico-22-ago-25.xlsx")

st.write("Arquivos encontrados:")
st.write(METRO_FILE)
st.write(BASELINE_FILE)
st.write(DEMOG_FILE)

# =========================================================
# LEITURA DOS DADOS
# =========================================================
@st.cache_data
def load():
    metro = pd.read_excel(METRO_FILE)
    baseline = pd.read_excel(BASELINE_FILE)
    demo = pd.read_excel(DEMOG_FILE)
    return metro, baseline, demo

metro, baseline, demo = load()

# =========================================================
# NORMALIZAR COLUNAS
# =========================================================
def normalizar_colunas(df):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

metro = normalizar_colunas(metro)
baseline = normalizar_colunas(baseline)
demo = normalizar_colunas(demo)

# =========================================================
# DETECTAR ID PACIENTE
# =========================================================
def detectar_coluna_id(df):

    candidatos = [
        "id_paciente",
        "id",
        "idpaciente",
        "id_pac",
        "paciente_id"
    ]

    for c in candidatos:
        if c in df.columns:
            return c

    return None

col_id_demo = detectar_coluna_id(demo)
col_id_metro = detectar_coluna_id(metro)

if col_id_demo is None or col_id_metro is None:
    st.error("Não foi possível identificar a coluna de ID.")
    st.stop()

ids_validos = demo[col_id_demo].unique()
metro = metro[metro[col_id_metro].isin(ids_validos)]

# =========================================================
# CRIAR CICLOS
# =========================================================

metro = metro.sort_values([col_id_metro, "data_1_dia_mt"])

metro["ciclo"] = (
    metro.groupby(col_id_metro)
    .cumcount() + 1
)

metro = metro[metro["ciclo"] <= 12]

# =========================================================
# GARANTIR PIOR GRAU POR PACIENTE EM CADA CICLO
# =========================================================

tox_cols = {
"AnemiaHBMT":"anemiahbmt",
"DiarreiaMT":"diarreiamt",
"Hepatica_BT_MT":"hepatica_bt_mt",
"Hepatica_TGO_MT":"hepatica_tgo_mt",
"Hepatica_TGP_MT":"hepatica_tgp_mt",
"MucositeMT":"mucositemt",
"NauseasMT":"nauseasmt",
"NeutropeniaFebreMT":"neutropeniafebremt",
"NeutropeniaMT":"neutropeniamt",
"PerdaDePesoMT":"perdadepesomt",
"PlaquetopeniaMT":"plaquetopeniamt",
"Renal_CreatinaMT":"renal_creatinamt",
"VomitosMT":"vomitosmt"
}

for col in tox_cols.values():

    if col in metro.columns:

        metro[col+"_grau"] = metro[col].apply(extrair_grau)

      
# manter apenas uma linha por paciente-ciclo
metro = metro.drop_duplicates(subset=[col_id_metro, "ciclo"])

# metro = metro.sort_values([col_id_metro, "data_1_dia_mt"])

# metro["ciclo"] = (
#    metro.groupby(col_id_metro)
#    .cumcount() + 1
#)

# metro = metro[metro["ciclo"] <= 12]

# 🔴 remover duplicações paciente-ciclo
# metro = metro.drop_duplicates(subset=[col_id_metro, "ciclo"])

# =========================================================
# PACIENTES POR CICLO
# =========================================================
pacientes_por_ciclo = (
    metro.groupby("ciclo")[col_id_metro]
    .nunique()
)

st.subheader("Pacientes avaliados por ciclo")
st.table(pacientes_por_ciclo)

# =========================================================
# DETECTAR COLUNAS DE DATA
# =========================================================
def detectar_coluna(df, candidatos):
    for c in candidatos:
        if c in df.columns:
            return c
    return None

col_data_tcle = detectar_coluna(
    baseline,
    ["data_tcle","tcle_data","data_tcle_assinatura"]
)

col_data_nasc = detectar_coluna(
    baseline,
    ["data_nascimento","data_de_nascimento","nascimento","dt_nascimento"]
)

if col_data_tcle is None or col_data_nasc is None:
    st.error("Colunas de data não encontradas")
    st.stop()

# =========================================================
# CALCULAR IDADE
# =========================================================
baseline[col_data_tcle] = pd.to_datetime(baseline[col_data_tcle], errors="coerce")
baseline[col_data_nasc] = pd.to_datetime(baseline[col_data_nasc], errors="coerce")

baseline["idade"] = (
    baseline[col_data_tcle] -
    baseline[col_data_nasc]
).dt.days / 365.25

idade = baseline["idade"].dropna()

st.header("Tabela 1 – Dados demográficos")

st.write("Range:",round(idade.min(),1),"-",round(idade.max(),1))
st.write("Média:",round(idade.mean(),1))
st.write("Mediana:",round(idade.median(),1))

# =========================================================
# TABELA DEMOGRÁFICA
# =========================================================
tabela_demo = pd.DataFrame({
"Variável":[
"Idade média",
"Idade mediana",
"Idade mínima",
"Idade máxima"
],
"Valor":[
round(idade.mean(),2),
round(idade.median(),2),
round(idade.min(),2),
round(idade.max(),2)
]
})

st.table(tabela_demo)

# =========================================================
# FUNÇÃO EXTRAI GRAU
# =========================================================
def extrair_grau(x):

    if pd.isna(x):
        return np.nan

    try:
        return int(str(x).split("-")[0])

    except:
        return np.nan

# =========================================================
# TOXICIDADES HEMATOLÓGICAS
# =========================================================
tox_hema = {
"Anemia":"anemiahbmt",
"Thrombocytopenia":"plaquetopeniamt",
"Neutropenia":"neutropeniamt"
}

for t in tox_hema.values():
    if t in metro.columns:
        metro[t+"_grau"] = metro[t].apply(extrair_grau)

# =========================================================
# CALCULAR EVENTOS (primeira ocorrência ≥3 por paciente)
# =========================================================
resultados = []

for nome, col in tox_hema.items():

    if col+"_grau" not in metro.columns:
        continue

    # primeiro ciclo com grau ≥3 por paciente
    primeiros_eventos = (
        metro[metro[col+"_grau"] >= 3]
        .groupby(col_id_metro)["ciclo"]
        .min()
    )

    for ciclo in range(1,13):

        eventos = (primeiros_eventos == ciclo).sum()

        avaliados = pacientes_por_ciclo.get(ciclo,0)

        pct = eventos/avaliados*100 if avaliados>0 else np.nan

        resultados.append({
            "ciclo": ciclo,
            "toxicidade": nome,
            "eventos": eventos,
            "avaliados": avaliados,
            "percentual": pct
        })

tabela2 = pd.DataFrame(resultados)

st.header("Tabela 2 – Eventos ≥ grau 3 por ciclo")
st.table(tabela2)

# =========================================================
# MATRIZ POR CICLO
# =========================================================
tabela_matriz = tabela2.pivot_table(
index="toxicidade",
columns="ciclo",
values="percentual"
).round(2)

st.subheader("Matriz de eventos")
st.table(tabela_matriz)

# =========================================================
# EXPORTAR TABELAS
# =========================================================
buffer=BytesIO()

with pd.ExcelWriter(buffer,engine="xlsxwriter") as writer:
    tabela2.to_excel(writer,sheet_name="Eventos")
    tabela_matriz.to_excel(writer,sheet_name="Matriz")

st.download_button(
"Baixar tabelas em Excel",
buffer.getvalue(),
file_name="resultados_metronomica.xlsx"
)

# =========================================================
# GRÁFICO HEMATOLÓGICO
# =========================================================
st.header("Gráfico – Toxicidades hematológicas")

fig,ax=plt.subplots(figsize=(12,6))

for tox in tox_hema.keys():

    df=tabela2[tabela2["toxicidade"]==tox]

    ax.plot(
    df["ciclo"],
    df["percentual"],
    marker="o",
    linewidth=3,
    markersize=8,
    label=tox
    )

labels=[f"{c} ({pacientes_por_ciclo.get(c,0)})" for c in range(1,13)]

ax.set_xticks(range(1,13))
ax.set_xticklabels(labels,rotation=45)

ax.set_xlabel("Cycle")
ax.set_ylabel("% of patients with grade ≥3")

ax.grid(True,linestyle="--",alpha=0.4)

ax.legend()

st.pyplot(fig)

# =========================================================
# EXPORTAR FIGURA 300 DPI
# =========================================================
buf=BytesIO()
fig.savefig(buf,dpi=300,bbox_inches="tight")

st.download_button(
"Baixar gráfico (300dpi)",
buf.getvalue(),
file_name="grafico_toxicidade.png"
)

st.write("Colunas disponíveis no arquivo:")
st.write(metro.columns)
# =========================================================
# TOXICIDADES NÃO HEMATOLÓGICAS
# =========================================================

tox_nao = {
    "Febrile Neutropenia": "neutropeniafebremt",
    "Hepatica tgo": "hepatica_tgo_mt",
    "Hepatica tgp": "hepatica_tgp_mt"
}

for t in tox_nao.values():
    if t in metro.columns:
        metro[t + "_grau"] = metro[t].apply(extrair_grau)

resultados2 = []

for ciclo in range(1,13):

    df = metro[metro["ciclo"] == ciclo]

    for nome,col in tox_nao.items():

        if col + "_grau" not in df.columns:
            continue

        grau = df[col + "_grau"]

        eventos = df.loc[grau >= 3, col_id_metro].nunique()
        avaliados = len(df)

        pct = eventos / avaliados * 100 if avaliados > 0 else np.nan

        resultados2.append({
            "ciclo": ciclo,
            "tox": nome,
            "percentual": pct
        })

tox_nao_df = pd.DataFrame(resultados2)
st.header("Non-hematological toxicities across treatment cycles")

fig, ax = plt.subplots(figsize=(12,6))

cores = {
    "Febrile Neutropenia": "#6b4f2a",
    "Hepatica tgo": "#8a00ff",
    "Hepatica tgp": "#00a7a7"
}

for tox in tox_nao_df["tox"].unique():

    df = tox_nao_df[tox_nao_df["tox"] == tox]

    ax.plot(
        df["ciclo"],
        df["percentual"],
        marker="o",
        linewidth=3,
        markersize=8,
        linestyle="-",
        label=tox,
        color=cores.get(tox)
    )

labels = [f"{c} ({pacientes_por_ciclo.get(c,0)})" for c in range(1,13)]

ax.set_xticks(range(1,13))
ax.set_xticklabels(labels, rotation=45)

ax.set_xlabel("Cycle")
ax.set_ylabel("% of patients with grade ≥3")

ax.grid(True, linestyle="--", alpha=0.4)

ax.legend(title="Non-hematological toxicity")

st.pyplot(fig)

# =========================================================
# TABELA COMPLETA DE TOXICIDADES POR CICLO
# =========================================================

