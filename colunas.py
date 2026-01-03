import pandas as pd

df = pd.read_excel("planilha-metronomica-filtrada.xlsx")

print("\nCOLUNAS DISPONÍVEIS:")
for c in df.columns:
    print("-", c)
