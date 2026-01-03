library(haven)
library(readxl)
library(dplyr)
library(openxlsx)

setwd('planilha metronomica helen/')

dados <- read_sav("Tabela-ewing_estatistico-22-ago-25.sav")

metro <- read_excel('9_202407_Metronomica(1).xlsx')

table(as.numeric(metro$`ID Paciente`) %in% as.numeric(dados$ID))

metro_f <- metro[as.numeric(metro$`ID Paciente`) %in% as.numeric(dados$ID),]

write.xlsx(metro_f, 'planilha-metronomica-filtrada.xlsx')




###################################  5/12/205 ###################################


library(tidyverse)
library(janitor)
library(lubridate)
library(skimr)


setwd('planilha metronomica helen/')

dados <- read_sav("Tabela-ewing_estatistico-22-ago-25.sav")
metro <- read_excel('planilha-metronomica-filtrada.xlsx')

# Limpar nomes das colunas (tira espaços, acentos, etc.)
metro <- metro %>%
  clean_names()

# Veja como ficaram os nomes
names(metro)


# Criar número de ciclo por paciente, ordenando pela data_1_dia_mt
metro <- metro %>%
  arrange(id_paciente, data_1_dia_mt) %>%
  group_by(id_paciente) %>%
  mutate(ciclo_mt = row_number()) %>%
  ungroup()

# Reordenar
metro <- metro[order(as.numeric(metro$id_paciente)),]


# Descritiva por paciente (peso, altura, SC, nº de ciclos)
resumo_paciente <- metro %>%
  group_by(id_paciente) %>%
  summarise(
    n_ciclos = n(),
    peso_medio = mean(peso_mt, na.rm = TRUE),
    altura_media = mean(altura_mt, na.rm = TRUE),
    sc_media = mean(superficie_corporal_mt, na.rm = TRUE)
  )

resumo_paciente <- resumo_paciente[order(as.numeric(resumo_paciente$id_paciente)),]


# Descritiva dos exames laboratoriais (geral e por ciclo)
labs_vars <- c("leucocitos_mt", "neutrofilos_mt", "hemoglobina_mt", "plaquetas_mt",
               "creatina_mt", "tgomt", "tgpmt", "btmt")  # ajuste nomes

labs_resumo_geral <- metro %>%
  select(all_of(c("id_paciente", "ciclo_mt", labs_vars))) %>%
  skim()

labs_resumo_geral



# Estatísticas por ciclo
labs_resumo_ciclo <- metro %>%
  group_by(ciclo_mt) %>%
  summarise(
    n_ciclos = n(),
    leucocitos_med = mean(leucocitos_mt, na.rm = TRUE),
    leucocitos_sd  = sd(leucocitos_mt, na.rm = TRUE),
    neutrofilos_med = mean(neutrofilos_mt, na.rm = TRUE),
    neutrofilos_sd  = sd(neutrofilos_mt, na.rm = TRUE),
    hb_med = mean(hemoglobina_mt, na.rm = TRUE),
    hb_sd  = sd(hemoglobina_mt, na.rm = TRUE),
    plaquetas_med = mean(plaquetas_mt, na.rm = TRUE),
    plaquetas_sd  = sd(plaquetas_mt, na.rm = TRUE),
    creatina_med = mean(creatina_mt, na.rm = TRUE),
    creatina_sd  = sd(creatina_mt, na.rm = TRUE)
  )

labs_resumo_ciclo

# ======================================
# 🩸 Toxicidades Hematológicas (% por ciclo)
# ======================================

def normalize_anemia(x):
    try:
        return max(int(x) - 1, 0)
    except:
        return None

# aplica regra da anemia
metro["anemia_norm"] = metro["anemiahbmt"].apply(normalize_anemia)

tox_cols = {
    "anemia": "anemia_norm",
    "plaquetopenia": "plaquetopeniamt",
    "neutropenia": "neutropeniamt"
}

tox_tables = {}

for nome, col in tox_cols.items():
    df = (metro.groupby("ciclo_mt")[col]
          .value_counts(normalize=True)
          .unstack()
          .fillna(0) * 100
          ).round(1)
    tox_tables[nome] = df

# salva
import json
with open("tox_hematologicas.json", "w") as f:
    json.dump({k: v.to_dict() for k,v in tox_tables.items()}, f)

print("\n=== SALVO: tox_hematologicas.json ===")



