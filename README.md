# 📊 BI Project — Coffee Shop & Météo

Ce projet analyse l’impact de la météo sur les ventes de boissons dans des cafés à New York.

Objectif : créer un entrepôt de données (DW) et des rapports dans Power BI à partir de deux fichiers Excel.

---

## Structure du projet

BI-COFFEE-SHOP/
│
├── data/
│   ├── input/                        # Données sources (Excel)
│   │   ├── Coffee Shop Sales.xlsx
│   │   └── dataset_temperatures.xlsx
│   │
│   └── output/                       # Données transformées (CSV)
│       ├── Dimension_Date.csv
│       ├── Dimension_Magasin.csv
│       ├── Dimension_Meteo.csv
│       ├── Dimension_Produit.csv
│       └── Fait_Ventes.csv
│
├── etl_cafe.py                       # Script principal ETL
├── image.png                         # Schéma en étoile du modèle de données
├── README.md                         # Présentation du projet
└── requirements.txt                  # Dépendances Python


---

## Étapes ETL

1. **Extraction**
   - Données de ventes (`Coffee Shop Sales.xlsx`)
   - Données météo (`dataset_temperatures.xlsx`)

2. **Transformation**
   - Nettoyage des données
   - Construction des dimensions : `Date`, `Produit`, `Magasin`, `Météo`
   - Génération de la table de faits : `Fait_Ventes`
   - Jointures selon le schéma en étoile

3. **Chargement**
   - Export des tables en CSV dans `data/output/`
   - Insertion des données dans une base PostgreSQL

---

## Lancer le script

Assurez-vous d'avoir toutes les dépendances installées, puis lancez le script :

```bash
pip install -r requirements.txt
python etl_cafe.py 
```

---

## Modèle en étoile composé de :

1. **DimDate**

2. **DimProduit**

3. **DimMagasin**

4. **DimMeteo**

5. **FaitVentes**

---
Auteur
[HATEM Lamia] — M2 MIAGE — Projet EDD 2024-2025