import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ===============================
# CHEMINS D'ACCÈS
# ===============================
input_path = Path("data/input")
output_path = Path("data/output")
output_path.mkdir(parents=True, exist_ok=True)

# ===============================
# EXTRACTION DES DONNÉES
# ===============================
sales_df = pd.read_excel(input_path / "Coffee Shop Sales.xlsx")
meteo_df = pd.read_excel(input_path / "dataset_temperatures.xlsx")
meteo_df.columns = meteo_df.columns.str.strip()
meteo_df.rename(columns={"datetime": "date"}, inplace=True)

# ===============================
# NETTOYAGE
# ===============================
sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
sales_df['transaction_qty'] = pd.to_numeric(sales_df['transaction_qty'], errors='coerce')
sales_df['unit_price'] = pd.to_numeric(sales_df['unit_price'], errors='coerce')
meteo_df['date'] = pd.to_datetime(meteo_df['date'])

# ===============================
# DIMENSION DATE
# ===============================
dim_date = sales_df[['transaction_date']].drop_duplicates().copy()
dim_date['jour'] = dim_date['transaction_date'].dt.day
dim_date['mois'] = dim_date['transaction_date'].dt.month
dim_date['annee'] = dim_date['transaction_date'].dt.year
dim_date['id_date'] = range(1, len(dim_date) + 1)
dim_date_final = dim_date[['id_date', 'jour', 'mois', 'annee']]

# ===============================
# DIMENSION PRODUIT
# ===============================
dim_produit = sales_df[['product_id', 'product_category', 'product_type', 'product_detail']].drop_duplicates().copy()
dim_produit['id_produit'] = range(1, len(dim_produit) + 1)
dim_produit_final = dim_produit[['id_produit', 'product_category', 'product_type', 'product_detail']]

# ===============================
# DIMENSION MAGASIN
# ===============================
dim_magasin = sales_df[['store_id', 'store_location']].drop_duplicates().copy()
dim_magasin['id_magasin'] = range(1, len(dim_magasin) + 1)
dim_magasin_final = dim_magasin[['id_magasin', 'store_location']]

# ===============================
# DIMENSION METEO
# ===============================
dim_meteo = meteo_df[['date', 'tempmax', 'tempmin', 'temp']].drop_duplicates().copy()
dim_meteo['id_meteo'] = range(1, len(dim_meteo) + 1)
dim_meteo_final = dim_meteo[['id_meteo', 'tempmax', 'tempmin', 'temp']]

# ===============================
# TABLE DE FAITS
# ===============================
df = sales_df.merge(dim_date[['id_date', 'transaction_date']], on='transaction_date', how='left')
df = df.merge(dim_produit, on=['product_id', 'product_category', 'product_type', 'product_detail'], how='left')
df = df.merge(dim_magasin, on=['store_id', 'store_location'], how='left')
df = df.merge(dim_meteo[['id_meteo', 'date']], left_on='transaction_date', right_on='date', how='left')

df['montant_total'] = df['transaction_qty'] * df['unit_price']
fait_ventes = df[['id_magasin', 'id_produit', 'id_date', 'id_meteo',
                  'transaction_qty', 'unit_price', 'montant_total']]
fait_ventes = fait_ventes.dropna(subset=['id_magasin', 'id_produit', 'id_date', 'id_meteo'])
fait_ventes['id_fait'] = range(1, len(fait_ventes) + 1)
fait_ventes_final = fait_ventes[['id_fait', 'id_magasin', 'id_produit', 'id_date', 'id_meteo',
                                 'transaction_qty', 'unit_price', 'montant_total']]

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
user = "postgres"
password = "odoo"
host = "localhost"
port = "5432"
database = "Coffe_shop_BI"

db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_url)

dim_date_final.to_sql("dim_date", engine, if_exists="replace", index=False)
dim_produit_final.to_sql("dim_produit", engine, if_exists="replace", index=False)
dim_magasin_final.to_sql("dim_magasin", engine, if_exists="replace", index=False)
dim_meteo_final.to_sql("dim_meteo", engine, if_exists="replace", index=False)
fait_ventes_final.to_sql("fait_ventes", engine, if_exists="replace", index=False)

print("Données insérées dans la base PostgreSQL.")
