import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # pasta Segunda Análise_python
BIOINFO_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # sobe nível → BioInfo

print("COLHENDO DADOS METRONÔMICA...")

file_mt = os.path.join(BIOINFO_DIR, "9_202407_Metronomica.xlsx")
file_out = os.path.join(BASE_DIR, "planilha-metronomica-filtrada.xlsx")

if not os.path.exists(file_mt):
    print("⚠️ Arquivo original 9_202407_Metronomica.xlsx não encontrado!")
else:
    df = pd.read_excel(file_mt)
    print("COLUNAS:", df.columns.tolist())
    df.to_excel(file_out, index=False)
    print("✔️ SALVO:", file_out)
