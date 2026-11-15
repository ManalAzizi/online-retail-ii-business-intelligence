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
```

---

## 2. Extraction des données (`extract.py`)

Le pipeline consomme deux fichiers au format Parquet issus du projet ML, stockés dans `data/processed/` :
- `online_retail_II_cleaned.parquet` : **777 622 lignes** d'achats nettoyées (clients identifiés, quantités et prix strictement positifs, hors annulations et frais de port).
- `customer_rfm_clusters.parquet` : **5 877 clients** distincts accompagnés de leurs indicateurs RFM (*Recency*, *Frequency*, *Monetary*) et de leur numéro de cluster K-Means (`0` à `3`).

Avant toute transformation, la fonction `extract_data()` vérifie l'existence physique des fichiers et contrôle que l'ensemble des colonnes indispensables sont présentes.

---

## 3. Règles de transformation (`transform.py`)

### 3.1 Construction des dimensions

1. **`Dim_Date` (739 lignes)**
   - Génération d'un calendrier continu sans interruption (`freq="D"`) couvrant la période du **1er décembre 2009 au 9 décembre 2011**, incluant les 135 jours sans transaction afin d'assurer le bon fonctionnement des fonctions temporelles DAX (`SAMEPERIODLASTYEAR`) dans Power BI.
   - Création de la clé primaire `DateKey` au format entier `AAAAMMJJ` (ex. `20110115`).
   - Extraction des attributs hiérarchiques (`Année`, `Trimestre`, `Mois`, `Semaine` ISO) et traduction explicite des noms de mois (`NomMois`) et de jours (`JourSemaine`) en **français** via des dictionnaires dédiés afin de s'affranchir de la configuration régionale du système d'exploitation.

2. **`Dim_Produit` (4 630 lignes)**
   - Regroupement par `StockCode` unique.
   - Comme 624 codes produits possèdent entre 2 et 4 descriptions différentes dans les données d'origine, seule la description la plus fréquente (`.mode()`) est conservée pour éviter toute duplication de lignes lors des jointures.
   - Attribution d'une clé de substitution séquentielle `ProductKey` (entier de `1` à `4 630`).

3. **`Dim_Pays` (41 lignes)**
   - Extraction des 41 pays distincts triés par ordre alphabétique et attribution d'une clé de substitution `CountryKey` (`1` à `41`).
   - Création de l'attribut hiérarchique **`Zone`** : valeur `"Royaume-Uni"` pour `United Kingdom` et `"Export"` pour les 40 autres pays.

4. **`Dim_Client` (5 877 lignes)**
   - Conversion explicite de `Customer ID` (initialement stocké en flottant dans le fichier ML) en entier (`CustomerKey`) afin de garantir l'exactitude des jointures.
   - Remplacement des identifiants numériques de clusters par leurs libellés métier issus de l'analyse K-Means :
     - `0` $\rightarrow$ *VIP et très fidèles*
     - `1` $\rightarrow$ *Inactifs et occasionnels*
     - `2` $\rightarrow$ *Récents à potentiel*
     - `3` $\rightarrow$ *Intermédiaires à risque*

### 3.2 Construction de la table de faits (`Fait_Ventes`)

- Conservation du grain le plus fin : **1 ligne = 1 ligne de facture** (777 622 lignes).
- Dérivation de `DateKey` depuis `InvoiceDate` et de `CustomerKey` depuis `Customer ID`.
- Jointures à gauche (`how="left"`) avec `Dim_Produit` et `Dim_Pays` pour substituer les attributs descriptifs (`StockCode`, `Country`) par leurs clés étrangères (`ProductKey`, `CountryKey`).
- Renommage des colonnes conformément au contrat de données : `Invoice` $\rightarrow$ `InvoiceNo` (dimension dégénérée) et `Price` $\rightarrow$ `UnitPrice`.

---

## 4. Contrôles qualité et chargement (`load.py`)

### 4.1 Validation automatisée

Avant toute écriture sur disque, la fonction `validate_star_schema()` exécute une série d'assertions bloquantes (`assert`) comparant les agrégats de la table de faits aux chiffres de référence établis en phase 1.

Résultats obtenus lors de l'exécution du pipeline :

| Contrôle effectué | Valeur attendue | Valeur obtenue | Statut |
|---|---|---|---|
| Nombre de lignes dans `Fait_Ventes` | 777 622 | **777 622** | Validé |
| Nombre de clients distincts | 5 877 | **5 877** | Validé |
| Nombre de factures distinctes | 36 859 | **36 859** | Validé |
| Chiffre d'affaires total (`Montant`) | 17 250 156,23 £ | **17 250 156,23 £** | Validé |
| Ventes sans segment client | 0 | **0** | Validé |
| Clés étrangères manquantes (`NA`) | 0 | **0** | Validé |
| Cardinalité `Dim_Date` | 739 | **739** | Validé |
| Cardinalité `Dim_Produit` | 4 630 | **4 630** | Validé |
| Cardinalité `Dim_Client` | 5 877 | **5 877** | Validé |
| Cardinalité `Dim_Pays` | 41 | **41** | Validé |

Ces résultats démontrent qu'aucune ligne n'a été perdue ni dupliquée lors des jointures et que l'intégrité référentielle entre la table de faits et les quatre dimensions est totale.

### 4.2 Exportation des livrables

Une fois les contrôles validés, les 5 tables sont exportées dans le répertoire `data/warehouse/` au format **CSV** (séparateur virgule, sans index, encodage **UTF-8**) :
- `data/warehouse/Dim_Date.csv` (739 lignes)
- `data/warehouse/Dim_Produit.csv` (4 630 lignes)
- `data/warehouse/Dim_Pays.csv` (41 lignes)
- `data/warehouse/Dim_Client.csv` (5 877 lignes)
- `data/warehouse/Fait_Ventes.csv` (777 622 lignes)

---

## 5. Conclusion de la phase 3

Le pipeline ETL est opérationnel, reproductible et validé par des tests automatisés. Les cinq fichiers CSV générés respectent le contrat de données convenu et sont prêts à être chargés dans Power BI pour la modélisation OLAP et la création des tableaux de bord (phases 4 et 5).