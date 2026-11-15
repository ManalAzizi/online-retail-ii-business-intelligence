# Dictionnaire de données — modèle en étoile Online Retail II

Les tables sont produites par l'ETL (phase 3) et stockées en CSV dans `data/warehouse/`. Toutes les valeurs monétaires sont en livres sterling (£).

## Fait_Ventes

Grain : une ligne de facture (un produit sur une facture). Lignes attendues : 777 622.

| Colonne | Type | Rôle | Description |
|---|---|---|---|
| `InvoiceNo` | Texte | Dimension dégénérée | Numéro de facture. Non unique : une facture compte plusieurs lignes. Sert à compter les factures |
| `DateKey` | Entier | Clé étrangère | Date de la facture, au format AAAAMMJJ. Référence `Dim_Date` |
| `ProductKey` | Entier | Clé étrangère | Produit vendu. Référence `Dim_Produit` |
| `CustomerKey` | Entier | Clé étrangère | Client. Référence `Dim_Client` |
| `CountryKey` | Entier | Clé étrangère | Pays de la facture. Référence `Dim_Pays` |
| `Quantity` | Entier | Mesure (additive) | Quantité achetée sur la ligne ; toujours strictement positive |
| `UnitPrice` | Décimal | Mesure (non additive) | Prix unitaire en £ ; toujours strictement positif |
| `Montant` | Décimal | Mesure (additive) | `Quantity × UnitPrice`, montant de la ligne en £ |

## Dim_Date

Grain : un jour calendaire, du 1er décembre 2009 au 9 décembre 2011 (739 lignes, sans trou).

| Colonne | Type | Rôle | Description | Exemple |
|---|---|---|---|---|
| `DateKey` | Entier | Clé primaire | Date au format AAAAMMJJ | 20110115 |
| `Date` | Date | Attribut | Date calendaire | 2011-01-15 |
| `Année` | Entier | Attribut (niveau 1) | Année | 2011 |
| `Trimestre` | Entier | Attribut (niveau 2) | Trimestre de l'année, de 1 à 4 | 1 |
| `Mois` | Entier | Attribut (niveau 3) | Numéro du mois, de 1 à 12 ; sert à trier `NomMois` | 1 |
| `NomMois` | Texte | Attribut | Nom du mois en français | janvier |
| `Semaine` | Entier | Attribut | Numéro de semaine ISO | 2 |
| `JourSemaine` | Texte | Attribut | Nom du jour en français | samedi |

Hiérarchie : Année > Trimestre > Mois > Jour.

## Dim_Produit

Grain : un code produit. Lignes attendues : 4 630.

| Colonne | Type | Rôle | Description |
|---|---|---|---|
| `ProductKey` | Entier | Clé primaire | Clé de substitution créée par l'ETL |
| `StockCode` | Texte | Attribut | Code produit d'origine (peut contenir des lettres) |
| `Description` | Texte | Attribut | Description la plus fréquente associée au code (624 codes en ont plusieurs dans le fichier d'origine) |

Pas de hiérarchie : le jeu de données ne contient pas de catégorie de produits.

## Dim_Client

Grain : un client identifié. Lignes attendues : 5 877.

| Colonne | Type | Rôle | Description | Exemple |
|---|---|---|---|---|
| `CustomerKey` | Entier | Clé primaire | Identifiant client (`Customer ID` du fichier d'origine, converti en entier) | 12346 |
| `Segment` | Texte | Attribut | Segment issu du K-Means (k = 4) : VIP et très fidèles, Intermédiaires à risque, Récents à potentiel, Inactifs et occasionnels | VIP et très fidèles |
| `Recency` | Entier | Attribut | Jours écoulés entre le dernier achat et la date de référence du 10 décembre 2011 | 326 |
| `Frequency` | Entier | Attribut | Nombre de factures distinctes du client | 12 |
| `Monetary` | Décimal | Attribut | Montant total dépensé par le client, en £ | 77556.46 |

Hiérarchie : Segment > Client. Les valeurs sont un instantané à la date de référence du projet ML.

## Dim_Pays

Grain : un pays. Lignes attendues : 41.

| Colonne | Type | Rôle | Description | Exemple |
|---|---|---|---|---|
| `CountryKey` | Entier | Clé primaire | Clé de substitution créée par l'ETL | 1 |
| `Pays` | Texte | Attribut | Nom du pays tel qu'il figure dans le fichier d'origine | United Kingdom |
| `Zone` | Texte | Attribut | Regroupement : « Royaume-Uni » ou « Export » | Royaume-Uni |

Hiérarchie : Zone > Pays.