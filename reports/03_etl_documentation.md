# Phase 3 — Documentation du pipeline ETL

## 1. Objectif et architecture du pipeline

La phase 3 consiste à transformer les données issues du projet de Machine Learning en un entrepôt de données structuré selon le schéma en étoile défini en phase 2. 

Pour garantir la maintenabilité, la lisibilité et la réutilisabilité du code, le pipeline ETL (*Extract, Transform, Load*) est découpé en trois modules Python situés dans `src/etl/` :

| Module | Rôle principal | Entrées / Sorties |
|---|---|---|
| `src/etl/extract.py` | Lecture des sources Parquet et vérification de la présence des colonnes requises | Lit `data/processed/*.parquet` |
| `src/etl/transform.py` | Construction des 4 tables de dimensions et de la table de faits centrale | Génère les 5 `DataFrame` en mémoire |
| `src/etl/load.py` | Contrôles qualité automatisés (assertions) et exportation en CSV UTF-8 | Écrit dans `data/warehouse/*.csv` |

L'exécution complète du pipeline s'effectue depuis la racine du projet via la commande :
```bash
python -m src.etl.load