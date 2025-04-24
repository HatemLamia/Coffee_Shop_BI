import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ===============================
# CHEMINS D'ACCÈS
# ===============================
input_path  = Path("data/input")
output_path = Path("data/output")
output_path.mkdir(parents=True, exist_ok=True)

# ===============================
# EXTRACTION DES DONNÉES
# ===============================
sales_df = pd.read_excel(input_path / "Coffee Shop Sales.xlsx")

# Nouveau dataset météo : datetime, temp, humidity
meteo_df = pd.read_excel(input_path / "dataset_temperatures.xlsx")
meteo_df.columns = meteo_df.columns.str.strip()

# ===============================
# NETTOYAGE ET CONVERSION
# ===============================
# Sales
sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'], errors='coerce')
sales_df['transaction_qty']    = pd.to_numeric(sales_df['transaction_qty'], errors='coerce')
sales_df['unit_price']         = pd.to_numeric(sales_df['unit_price'], errors='coerce')

# Météo : on conserve 'datetime' tel quel
meteo_df['datetime'] = pd.to_datetime(
    meteo_df['datetime'],
    dayfirst=True,
    errors='coerce'
)
meteo_df['temp']     = pd.to_numeric(meteo_df['temp'], errors='coerce')
meteo_df['humidity'] = pd.to_numeric(meteo_df['humidity'], errors='coerce')

# ===============================
# DIMENSION DATE
# ===============================
dim_date = (
    sales_df[['transaction_date']]
    .drop_duplicates()
    .copy()
)
dim_date['jour']      = dim_date['transaction_date'].dt.day
dim_date['mois']      = dim_date['transaction_date'].dt.month
dim_date['annee']     = dim_date['transaction_date'].dt.year
dim_date['id_date']   = range(1, len(dim_date) + 1)
dim_date_final = dim_date[['id_date', 'jour', 'mois', 'annee']]

# ===============================
# DIMENSION PRODUIT
# ===============================
dim_produit = (
    sales_df[['product_id', 'product_category', 'product_type', 'product_detail']]
    .drop_duplicates()
    .copy()
)
dim_produit['id_produit'] = range(1, len(dim_produit) + 1)
dim_produit_final = dim_produit[['id_produit', 'product_category', 'product_type', 'product_detail']]

# ===============================
# DIMENSION MAGASIN
# ===============================
dim_magasin = (
    sales_df[['store_id', 'store_location']]
    .drop_duplicates()
    .copy()
)
dim_magasin['id_magasin'] = range(1, len(dim_magasin) + 1)
dim_magasin_final = dim_magasin[['id_magasin', 'store_location']]

# ===============================
# DIMENSION METEO
# ===============================
# On utilise datetime, temp et humidity
dim_meteo = (
    meteo_df[['datetime', 'temp', 'humidity']]
    .drop_duplicates()
    .copy()
)

# Fonctions de classification par quartiles
def classify_temp(t):
    if t < 5.5:
        return 'froid'
    elif t <= 17.6:
        return 'modéré'
    else:
        return 'chaud'

def classify_humidity(h):
    if h < 43.6:
        return 'sec'
    elif h <= 67.4:
        return 'confort'
    else:
        return 'humide'

# Application des classifications
dim_meteo['temp_cat']     = dim_meteo['temp'].apply(classify_temp)
dim_meteo['humidity_cat'] = dim_meteo['humidity'].apply(classify_humidity)

# Clé de la dimension
dim_meteo['id_meteo'] = range(1, len(dim_meteo) + 1)
dim_meteo_final = dim_meteo[
    ['id_meteo', 'temp', 'humidity', 'temp_cat', 'humidity_cat']
]

# ===============================
# TABLE DE FAITS
# ===============================
df = (
    sales_df
    .merge(dim_date[['id_date', 'transaction_date']],
           on='transaction_date', how='left')
    .merge(dim_produit, on=['product_id', 'product_category',
                            'product_type', 'product_detail'], how='left')
    .merge(dim_magasin, on=['store_id', 'store_location'], how='left')
    .merge(dim_meteo[['id_meteo', 'datetime']],
           left_on='transaction_date',
           right_on='datetime',
           how='left')
)

df['montant_total'] = df['transaction_qty'] * df['unit_price']

fait_ventes = df[[
    'id_magasin', 'id_produit', 'id_date', 'id_meteo',
    'transaction_qty', 'unit_price', 'montant_total'
]].dropna(subset=['id_magasin', 'id_produit', 'id_date', 'id_meteo'])

fait_ventes['id_fait'] = range(1, len(fait_ventes) + 1)
fait_ventes_final = fait_ventes[
    ['id_fait', 'id_magasin', 'id_produit', 'id_date', 'id_meteo',
     'transaction_qty', 'unit_price', 'montant_total']
]

# ===============================
# EXPORT CSV
# ===============================
sep = ';'
dim_date_final.to_csv(output_path / "Dimension_Date.csv", index=False, sep=sep)
dim_produit_final.to_csv(output_path / "Dimension_Produit.csv", index=False, sep=sep)
dim_magasin_final.to_csv(output_path / "Dimension_Magasin.csv", index=False, sep=sep)
dim_meteo_final.to_csv(output_path / "Dimension_Meteo.csv", index=False, sep=sep)
fait_ventes_final.to_csv(output_path / "Fait_Ventes.csv", index=False, sep=sep)

print("Données exportées dans le dossier : data/output/")

# ===============================
# EXPORT VERS BASE DE DONNÉES POSTGRESQL
# ===============================
user     = "postgres"
password = "odoo"
host     = "localhost"
port     = "5432"
# ← on pointe maintenant sur Coffe_shop_BI2
database = "Coffe_shop_BI2"

db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_url)

# Ces appels vont créer ou remplacer les tables dans Coffe_shop_BI2
dim_date_final.to_sql("dim_date", engine, if_exists="replace", index=False)
dim_produit_final.to_sql("dim_produit", engine, if_exists="replace", index=False)
dim_magasin_final.to_sql("dim_magasin", engine, if_exists="replace", index=False)
dim_meteo_final.to_sql("dim_meteo", engine, if_exists="replace", index=False)
fait_ventes_final.to_sql("fait_ventes", engine, if_exists="replace", index=False)

print("Données insérées dans la base PostgreSQL Coffe_shop_BI2.")
