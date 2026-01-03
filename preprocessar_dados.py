import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "dados"

# Arquivos de entrada
FILE_DEMO = BASE / "Tabela-ewing_estatistico-22-ago-25.xlsx"
FILE_BASELINE = BASE / "1_202407_Baseline.xlsx"
FILE_TOX = BASE / "9_202407_Metronomica.xlsx"

# Saída
OUT = Path(__file__).resolve().parents[1] / "dados" / "dataset_unificado.csv"

def normalizar(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# -------------------------
# 1) CARREGAR DADOS
# -------------------------
demo = pd.read_excel(FILE_DEMO)
baseline = pd.read_excel(FILE_BASELINE)
tox = pd.read_excel(FILE_TOX)

demo = normalizar(demo)
baseline = normalizar(baseline)
tox = normalizar(tox)

# -------------------------
# 2) CALCULAR IDADE
# -------------------------
# baseline deve conter: id , data_tcle / data_nasc
col_id_demo = "id"
col_id_base = "id"
col_birth = "data_de_na"  # confirmado via print
col_tcle = "data_do_ev"   # ajuste pode ser necessário

try:
    baseline["idade"] = (
        pd.to_datetime(baseline[col_tcle], errors="coerce")
        - pd.to_datetime(baseline[col_birth], errors="coerce")
    ).dt.days // 365
except:
    baseline["idade"] = np.nan

# -------------------------
# 3) UNIFICAR
# -------------------------
df = tox.merge(demo, left_on="id", right_on="id", how="left")
df = df.merge(baseline[["id", "idade"]], on="id", how="left")

# ordenar por ciclo
if "ciclo_mt" in df.columns:
    df = df.sort_values(["id", "ciclo_mt"])

df.to_csv(OUT, index=False)

print(f"✔ Arquivo salvo → {OUT}")
