import pandas as pd
from pathlib import Path
from fpdf import FPDF

# =========================
# 1. LEITURA DOS DADOS
# =========================
heme = pd.read_csv("toxicidades_hematologicas_n_perc.csv")
outras = pd.read_csv("outras_toxicidades_n_perc.csv")

# =========================
# 2. PADRONIZAÇÃO
# =========================
for df in [heme, outras]:
    df.columns = df.columns.str.strip().str.replace("_", " ").str.title()

# =========================
# 3. HTML FINAL
# =========================
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Relatório de Toxicidades</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
}}
h1, h2 {{
    color: #2c3e50;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 40px;
}}
th, td {{
    border: 1px solid #ccc;
    padding: 8px;
    text-align: center;
}}
th {{
    background-color: #f4f6f7;
}}
</style>
</head>
<body>

<h1>Relatório de Análise de Toxicidades</h1>

<h2>Toxicidades Hematológicas</h2>
{heme.to_html(index=False)}

<h2>Outras Toxicidades</h2>
{outras.to_html(index=False)}

<p><em>Relatório gerado automaticamente a partir das tabelas consolidadas.</em></p>

</body>
</html>
"""

Path("Relatorio_Final.html").write_text(html, encoding="utf-8")

print("✔ HTML gerado: Relatorio_Final.html")

# =========================
# 4. PDF FINAL
# =========================
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Relatorio de Analise de Toxicidades", ln=True)

def tabela_pdf(pdf, df, titulo):
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, titulo, ln=True)
    pdf.set_font("Arial", size=9)

    col_width = pdf.w / (len(df.columns) + 1)

    for col in df.columns:
        pdf.cell(col_width, 8, col, border=1)
    pdf.ln()

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 8, str(item), border=1)
        pdf.ln()

tabela_pdf(pdf, heme, "Toxicidades Hematologicas")
tabela_pdf(pdf, outras, "Outras Toxicidades")

pdf.output("Relatorio_Final.pdf")
print("✔ PDF gerado: Relatorio_Final.pdf")
