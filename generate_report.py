# =========================================================
# 📦 IMPORTS
# =========================================================
import os
import subprocess
from datetime import datetime, date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader


# =========================================================
# 📁 PATHS E DIRETÓRIOS
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIOINFO_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FIGS_DIR = os.path.join(OUTPUT_DIR, "figs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGS_DIR, exist_ok=True)


# =========================================================
# 1️⃣ EXECUÇÃO DO PIPELINE (OPCIONAL)
# =========================================================
script_path = os.path.join(BASE_DIR, "seg_metrogenomica.py")
if os.path.exists(script_path):
    print("⏳ Executando pipeline seg_metrogenomica.py...")
    subprocess.run(["python3", script_path])


# =========================================================
# 2️⃣ LEITURA DAS PLANILHAS
# =========================================================
metro_file = os.path.join(BIOINFO_DIR, "planilha-metronomica-filtrada.xlsx")
baseline_file = os.path.join(BIOINFO_DIR, "1_202407_Baseline.xlsx")

metro = pd.read_excel(metro_file) if os.path.exists(metro_file) else pd.DataFrame()
baseline = pd.read_excel(baseline_file) if os.path.exists(baseline_file) else pd.DataFrame()


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


baseline_data = []

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
    baseline_data = baseline.head(20).to_dict(orient="records")


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
        .to_dict(orient="records")
    )
else:
    resumo = []


# =========================================================
# 🩸 HEATMAPS DE TOXICIDADE (POR CICLO)
# =========================================================
tox_cols = [
    ("AnemiaHBMT", "anemiahbmt", "Hemoglobina baixa — queda de Hb."),
    ("PlaquetopeniaMT", "plaquetopeniamt", "Plaquetas reduzidas."),
    ("NeutropeniaMT", "neutropeniamt", "Neutrófilos reduzidos."),
    ("NeutropeniaFebreMT", "neutropeniafebremt", "Neutropenia + febre."),
    ("NauseasMT", "nauseasmt", "Náuseas."),
    ("VomitosMT", "vomitosmt", "Vômitos."),
    ("MucositeMT", "mucositemt", "Mucosite."),
    ("DiarreiaMT", "diarreiamt", "Diarreia."),
    ("Renal_CreatinaMT", "renal_creatinamt", "Creatinina."),
    ("Hepatica_BT_MT", "hepatica_bt_mt", "Bilirrubina total."),
    ("Hepatica_TGO_MT", "hepatica_tgo_mt", "TGO."),
    ("Hepatica_TGP_MT", "hepatica_tgp_mt", "TGP."),
]

heatmap_paths = []
heatmap_desc = {}

plt.ioff()
sns.set(font_scale=0.6)

print("🔥 Gerando heatmaps de toxicidade...")

for label, col, desc in tox_cols:
    if col not in metro.columns:
        continue

    df = metro.copy()

    def grau(x):
        try:
            return int(str(x).split("-")[0])
        except Exception:
            return np.nan

    df[col] = df[col].apply(grau)

    tabela = df.pivot_table(
        index=ciclo_col,
        columns="id_paciente",
        values=col,
        aggfunc="max"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4), dpi=120)
    sns.heatmap(tabela, cmap="Reds", cbar=True, ax=ax)

    ax.set_title(label, fontsize=10)
    ax.set_xlabel("Paciente")
    ax.set_ylabel("Ciclo")

    fig.tight_layout()

    fname = f"hm_{label}.png"
    fig.savefig(os.path.join(FIGS_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close()

    heatmap_paths.append(fname)
    heatmap_desc[label] = desc


# =========================================================
# 📊 GRÁFICO — TOXICIDADE HEMATOLÓGICA (GRAU MÁXIMO)
# =========================================================
print("📊 Gerando gráfico de toxicidade hematológica por paciente...")

tox_hema = pd.DataFrame(
    {
        "AnemiaHBMT": [53.1, 29.2, 11.5, 3.1, 0.0],
        "NeutropeniaMT": [5.2, 11.5, 10.4, 33.3, 36.5],
        "PlaquetopeniaMT": [57.3, 30.2, 2.1, 5.2, 2.1],
    },
    index=["Grau 0", "Grau 1", "Grau 2", "Grau 3", "Grau 4"]
)

fig, ax = plt.subplots(figsize=(8, 5), dpi=120)

tox_hema.T.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    colormap="YlOrBr"
)

ax.set_title("Distribuição dos Graus Máximos de Toxicidades Hematológicas", fontsize=11)
ax.set_ylabel("Porcentagem de pacientes")
ax.set_xlabel("Tipo de toxicidade")
ax.legend(title="Grau de Toxicidade", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig(
    os.path.join(FIGS_DIR, "toxicidade_hematologica_grau_max.png"),
    dpi=150,
    bbox_inches="tight"
)
plt.close()

# =========================================================
# 📊 GRÁFICO — TOXICIDADE NÃO HEMATOLÓGICA (GRAU MÁXIMO)
# =========================================================
print("📊 Gerando gráfico de toxicidade não hematológica por paciente...")

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

fig, ax = plt.subplots(figsize=(9, 5), dpi=120)

tox_nao_hema.T.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    colormap="YlOrBr"
)

ax.set_title(
    "Distribuição dos Graus Máximos de Toxicidades Não Hematológicas",
    fontsize=11
)
ax.set_ylabel("Porcentagem de pacientes")
ax.set_xlabel("Tipo de toxicidade")
ax.legend(
    title="Grau de Toxicidade",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()
plt.savefig(
    os.path.join(FIGS_DIR, "toxicidade_nao_hematologica_grau_max.png"),
    dpi=150,
    bbox_inches="tight"
)
plt.close()


# =========================================================
# 🧾 RENDERIZAÇÃO HTML + PDF
# =========================================================
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("template.html")

html = template.render(
    titulo="Relatório Técnico – Metronômica no Ewing",
    subtitulo="Resultados laboratoriais e toxicidade",
    data_execucao=datetime.now().strftime("%d/%m/%Y %H:%M"),
    baseline_data=baseline_data,
    resumo=resumo,
    heatmaps=heatmap_paths,
    heatmap_desc=heatmap_desc,
    base_url=f"file://{TEMPLATE_DIR}",
    figs_url=f"file://{FIGS_DIR}",
)

html_path = os.path.join(OUTPUT_DIR, "relatorio.html")
with open(html_path, "w") as f:
    f.write(html)

print(f"📄 HTML gerado → {html_path}")

print("📌 Gerando PDF...")
pdf_path = os.path.join(OUTPUT_DIR, "relatorio.pdf")
os.system(
    f'weasyprint "{html_path}" "{pdf_path}" --base-url "{OUTPUT_DIR}"'
)


print(f"✅ PDF gerado → {pdf_path}")
