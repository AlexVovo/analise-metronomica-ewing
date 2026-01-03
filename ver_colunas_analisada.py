import pandas as pd

df = pd.read_excel("metro-analisada.xlsx")

print("\nCOLUNAS DISPONÍVEIS EM metro-analisada.xlsx:")
for c in df.columns:
    print("-", c)
