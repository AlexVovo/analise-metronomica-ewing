# =========================================================
# IMPORTS
# =========================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(layout="wide")

st.title("Relatório da análise de dados demográficos e toxicidade")

# =========================================================
# DADOS DEMOGRÁFICOS
# =========================================================

st.header("Dados demográficos")

st.markdown("""
A tabela abaixo mostra a porcentagem de cada variável relaciada aos pacientes analisados no estudo.  
Cada porcentagem foi calculada baseada no número de pacientes (n) que aderiram a metronômica (n=96), não aderiram (n=138).  
Também foi calculado para toda a coorte (n=234).
""")

data_demo = {

"Variável":[
"Gênero (Masculino)",
"Gênero (Feminino)",
"Local (Pélvico)",
"Local (Não pélvico)",
"Tamanho do tumor (> 8 cm)",
"Tamanho do tumor (≤ 8 cm)",
"Idade (≥14 anos)",
"Idade (<14 anos)",
"Range",
"Média",
"Mediana"
],

"Metronômica (sim) - n=96":[
"58 (60.42%)",
"38 (39.58%)",
"19 (19.79%)",
"77 (80.21%)",
"46 (47.92%)",
"50 (52.08%)",
"26 (27.08%)",
"70 (72.92%)",
"1.06 - 26.75",
"11.17",
"11.56"
],

"Metronômica (não) - n=138":[
"77 (55.8%)",
"61 (44.2%)",
"23 (16.67%)",
"115 (83.33%)",
"71 (51.45%)",
"67 (48.55%)",
"42 (30.43%)",
"96 (69.57%)",
"0.16 - 19.06",
"10.6",
"10.85"
],

"Total - n=234":[
"135 (57.69%)",
"99 (42.31%)",
"42 (17.95%)",
"192 (82.05%)",
"117 (50%)",
"117 (50%)",
"68 (29.06%)",
"166 (70.94%)",
"0.16 - 26.75",
"10.83",
"11.17"
]

}

df_demo = pd.DataFrame(data_demo)

st.subheader("Distribuição dos pacientes por características")
st.table(df_demo)

# =========================================================
# TEXTO TOXICIDADE
# =========================================================

st.header("Toxicidade por ciclo")

st.markdown("""
Os gráficos abaixo avaliam a toxicidade de pacientes por ciclo.  
Foram considerados pacientes com **grau ≥ 3** para o cálculo da porcentagem de eventos por ciclo para cada toxicidade.
""")

# =========================================================
# DADOS PARA GRÁFICOS
# =========================================================

ciclos = list(range(1,13))

n_pacientes = [96,93,90,88,82,74,71,71,69,68,66,62]

# Hematológicos
anemia = [6.74,5.81,4.71,7.23,6.58,4.05,1.47,2.86,4.48,6.06,3.12,5.00]
neutropenia = [44.94,35.63,32.94,28.40,26.32,21.92,31.34,24.29,17.65,15.15,17.19,16.67]
plaquetopenia = [4.44,1.18,0,0,1.32,0,3.03,1.45,1.52,0,1.59,3.33]

# Não hematológicos
febril = [6.45,5.56,6.74,4.71,1.23,1.35,1.41,1.45,1.47,4.41,0,0]
tgo = [1.20,2.56,1.32,1.35,1.49,1.56,1.69,3.45,1.82,0,1.82,0]
tgp = [3.57,2.50,1.33,1.28,2.90,1.56,1.75,1.75,1.85,0,1.82,0]

labels = [f"{c} ({n})" for c,n in zip(ciclos,n_pacientes)]

# =========================================================
# GRÁFICO HEMATOLÓGICO
# =========================================================

st.subheader("Hematological toxicities across treatment cycles")

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(ciclos, anemia, marker="o", label="Anemia")
ax.plot(ciclos, neutropenia, marker="o", label="Neutropenia")
ax.plot(ciclos, plaquetopenia, marker="o", label="Thrombocytopenia")

ax.set_xticks(ciclos)
ax.set_xticklabels(labels, rotation=45)

ax.set_ylabel("% of patients with grade ≥3")
ax.set_xlabel("Cycle")

ax.grid(True)
ax.legend(title="Hematological toxicity")

st.pyplot(fig)

# =========================================================
# GRÁFICO NÃO HEMATOLÓGICO
# =========================================================

st.subheader("Non-hematological toxicities across treatment cycles")

fig2, ax2 = plt.subplots(figsize=(10,5))

ax2.plot(ciclos, febril, marker="o", label="Febrile Neutropenia")
ax2.plot(ciclos, tgo, marker="o", label="Hepatica tgo")
ax2.plot(ciclos, tgp, marker="o", label="Hepatica tgp")

ax2.set_xticks(ciclos)
ax2.set_xticklabels(labels, rotation=45)

ax2.set_ylabel("% of patients with grade ≥3")
ax2.set_xlabel("Cycle")

ax2.grid(True)
ax2.legend(title="Non-hematological toxicity")

st.pyplot(fig2)

# =========================================================
# TABELA COMPLETA
# =========================================================

st.header("Número de pacientes avaliados por ciclo")

st.markdown("""
Evento representa o número de pacientes com toxicidade **grau ≥3**.
Os percentuais foram calculados considerando apenas pacientes avaliados em cada ciclo.
""")

dados = {
"Metric":[
"N_pacientes",
"AnemiaHBMT - eventos",
"AnemiaHBMT - Não avaliado",
"DiarreiaMT - eventos",
"DiarreiaMT - Não avaliado",
"Hepatica_BT_MT - eventos",
"Hepatica_BT_MT - Não avaliado",
"Hepatica_TGO_MT - eventos",
"Hepatica_TGO_MT - Não avaliado",
"Hepatica_TGP_MT - eventos",
"Hepatica_TGP_MT - Não avaliado",
"MucositeMT - eventos",
"MucositeMT - Não avaliado",
"NauseasMT - eventos",
"NauseasMT - Não avaliado",
"NeutropeniaFebreMT - eventos",
"NeutropeniaFebreMT - Não avaliado",
"NeutropeniaMT - eventos",
"NeutropeniaMT - Não avaliado",
"PerdaDePesoMT - eventos",
"PerdaDePesoMT - Não avaliado",
"PlaquetopeniaMT - eventos",
"PlaquetopeniaMT - Não avaliado",
"Renal_CreatinaMT - eventos",
"Renal_CreatinaMT - Não avaliado",
"VomitosMT - eventos",
"VomitosMT - Não avaliado"
],

"Ciclo_1":[
96,"6 (6.74%)",7,"0 (0.00%)",4,"0 (0.00%)",12,"1 (1.20%)",13,"3 (3.57%)",12,"0 (0.00%)",4,"0 (0.00%)",4,"6 (6.45%)",3,"40 (44.94%)",7,"0 (0.00%)",4,"4 (4.44%)",6,"0 (0.00%)",10,"0 (0.00%)",4
],

"Ciclo_2":[
93,"5 (5.81%)",7,"0 (0.00%)",3,"0 (0.00%)",14,"2 (2.56%)",15,"2 (2.50%)",13,"0 (0.00%)",4,"0 (0.00%)",3,"5 (5.56%)",3,"31 (35.63%)",6,"0 (0.00%)",5,"1 (1.18%)",8,"0 (0.00%)",12,"0 (0.00%)",3
],

"Ciclo_3":[
90,"4 (4.71%)",5,"0 (0.00%)",1,"0 (0.00%)",14,"1 (1.32%)",14,"1 (1.33%)",15,"0 (0.00%)",1,"0 (0.00%)",1,"6 (6.74%)",1,"28 (32.94%)",5,"0 (0.00%)",3,"0 (0.00%)",6,"0 (0.00%)",10,"0 (0.00%)",2
],

"Ciclo_4":[
88,"6 (7.23%)",5,"0 (0.00%)",3,"0 (0.00%)",12,"1 (1.35%)",14,"1 (1.28%)",10,"0 (0.00%)",3,"0 (0.00%)",3,"4 (4.71%)",3,"23 (28.40%)",7,"0 (0.00%)",5,"0 (0.00%)",5,"0 (0.00%)",9,"0 (0.00%)",3
],

"Ciclo_5":[
82,"5 (6.58%)",6,"0 (0.00%)",1,"1 (1.47%)",14,"1 (1.49%)",15,"2 (2.90%)",13,"0 (0.00%)",2,"0 (0.00%)",1,"1 (1.23%)",1,"20 (26.32%)",6,"0 (0.00%)",3,"1 (1.32%)",6,"1 (1.41%)",11,"0 (0.00%)",1
],

"Ciclo_6":[
74,"3 (4.05%)",0,"0 (0.00%)",0,"0 (0.00%)",12,"1 (1.56%)",10,"1 (1.56%)",10,"0 (0.00%)",1,"0 (0.00%)",0,"1 (1.35%)",0,"16 (21.92%)",1,"0 (0.00%)",2,"0 (0.00%)",1,"0 (0.00%)",10,"0 (0.00%)",0
],

"Ciclo_7":[
71,"1 (1.47%)",3,"0 (0.00%)",0,"0 (0.00%)",13,"1 (1.69%)",12,"1 (1.75%)",14,"0 (0.00%)",0,"0 (0.00%)",0,"1 (1.41%)",0,"21 (31.34%)",4,"0 (0.00%)",2,"2 (3.03%)",5,"0 (0.00%)",13,"0 (0.00%)",0
],

"Ciclo_8":[
71,"2 (2.86%)",1,"0 (0.00%)",2,"0 (0.00%)",16,"2 (3.45%)",13,"1 (1.75%)",14,"0 (0.00%)",2,"0 (0.00%)",2,"1 (1.45%)",2,"17 (24.29%)",1,"0 (0.00%)",3,"1 (1.45%)",2,"0 (0.00%)",12,"0 (0.00%)",2
],

"Ciclo_9":[
69,"3 (4.48%)",2,"0 (0.00%)",1,"0 (0.00%)",15,"1 (1.82%)",14,"1 (1.85%)",15,"0 (0.00%)",1,"0 (0.00%)",1,"1 (1.47%)",1,"12 (17.65%)",1,"0 (0.00%)",2,"1 (1.52%)",3,"0 (0.00%)",16,"0 (0.00%)",1
],

"Ciclo_10":[
68,"4 (6.06%)",2,"0 (0.00%)",0,"0 (0.00%)",13,"0 (0.00%)",14,"0 (0.00%)",13,"0 (0.00%)",0,"0 (0.00%)",0,"3 (4.41%)",0,"10 (15.15%)",2,"0 (0.00%)",2,"0 (0.00%)",2,"0 (0.00%)",12,"0 (0.00%)",0
],

"Ciclo_11":[
66,"2 (3.12%)",2,"0 (0.00%)",0,"0 (0.00%)",12,"1 (1.82%)",11,"1 (1.82%)",11,"0 (0.00%)",0,"0 (0.00%)",0,"0 (0.00%)",0,"11 (17.19%)",2,"0 (0.00%)",1,"1 (1.59%)",3,"0 (0.00%)",10,"0 (0.00%)",0
],

"Ciclo_12":[
62,"3 (5.00%)",2,"0 (0.00%)",1,"0 (0.00%)",13,"0 (0.00%)",13,"0 (0.00%)",14,"0 (0.00%)",1,"0 (0.00%)",1,"0 (0.00%)",2,"10 (16.67%)",2,"0 (0.00%)",2,"2 (3.33%)",2,"0 (0.00%)",12,"0 (0.00%)",1
],

"Media_Prob":[
"NA","4.84%","NA","0.00%","NA","0.12%","NA","1.52%","NA","1.69%","NA","0.00%","NA","0.00%","NA","2.90%","NA","26.04%","NA","0.00%","NA","1.49%","NA","0.12%","NA","0.00%","NA"
]
}

df_toxicidade = pd.DataFrame(dados)

st.dataframe(df_toxicidade, width="stretch")