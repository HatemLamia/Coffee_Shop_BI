# 📊 BI Project — Coffee Shop & Météo

Ce projet analyse l’impact de la météo sur les ventes de boissons dans des cafés à New York.

Objectif : créer un entrepôt de données (DW) et des rapports dans Power BI à partir de deux fichiers Excel.

---

## Structure du projet

BI-coffee-shop/                 
│
├── data/
│   ├── input/                        # Données sources (raw)
│   │   ├── Coffee Shop Sales.xlsx
│   │   └── dataset_temperatures.xlsx
│   │          
│   │
│   └── output/                       # Données transformées
│       └── Dimensions.xlsx
        └── fait.xlsx
│                         
├── etl_cafe.py                        # Script principal ETL modulaire
└── requirements.txt                        # Dépendances Python
└── README.md                              # Présentation rapide du projet
    

---

## Étapes ETL

1. **Extraction** : ventes + météo (Excel)
2. **Transformation** :
   - Fusion par date
   - Création de dimensions : Date, Produit, Localisation, Météo
   - Table des faits : `F_Ventes`
3. **Export** : fichier Excel avec toutes les tables

---

## Lancer le script

```bash
cd data/input
python etl_coffee_shop.py

---
Auteur
[HATEM Lamia] — M2 MIAGE — Projet EDD 2024-2025