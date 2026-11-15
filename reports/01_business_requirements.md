# Phase 1 — Cadrage métier et besoins décisionnels

## 1. Contexte du projet

Dans un environnement e-commerce, les données transactionnelles représentent une source importante d'informations pour comprendre les performances commerciales et le comportement des clients.

Le projet consiste à exploiter le dataset **Online Retail II**, qui contient les transactions d'une entreprise britannique de vente en ligne entre le 1er décembre 2009 et le 9 décembre 2011, afin de construire une solution de Business Intelligence permettant d'analyser les ventes selon plusieurs axes : temporel, géographique, commercial et comportemental.

Le projet BI réutilise la base nettoyée et les segments de clients obtenus lors du projet de Machine Learning par l'algorithme K-Means. Ces segments permettent d'enrichir l'analyse commerciale par une dimension comportementale.

## 2. Problématique métier

Comment exploiter les données transactionnelles d'une plateforme e-commerce afin de suivre les performances commerciales, comprendre le poids des différents segments de clients, identifier les produits et les marchés les plus performants et faciliter la prise de décision ?

## 3. Objectifs du système décisionnel

Le système de Business Intelligence vise à :

- Suivre l'évolution du chiffre d'affaires dans le temps.
- Identifier les pays contribuant le plus aux ventes.
- Analyser les performances commerciales des produits.
- Mesurer le panier moyen par commande.
- Évaluer la contribution des différents segments de clients.
- Comparer les performances commerciales d'une année à l'autre, sur des périodes comparables.
- Faciliter l'exploration des données à travers des tableaux de bord interactifs.

## 4. Utilisateurs cibles

Profils types de décideurs auxquels s'adresse le tableau de bord :

| Utilisateur | Besoin décisionnel |
|---|---|
| Directeur commercial | Suivre les performances globales des ventes |
| Responsable marketing | Analyser les segments de clients |
| Responsable produits | Identifier les produits les plus performants |
| Responsable e-commerce | Suivre l'évolution de l'activité commerciale |

## 5. Périmètre de l'analyse

| Inclus | Exclus |
|---|---|
| Les achats des clients identifiés (`Customer ID` renseigné) | Les retours et annulations (factures préfixées `C`) |
| La période du 1er décembre 2009 au 9 décembre 2011 | Les lignes sans identifiant client |
| Les produits vendus | Les lignes de frais de livraison (`POST`) et les prix nuls |
| Le segment K-Means de chaque client | Les marges et les coûts (absents du jeu de données) |

Le projet analyse donc les ventes réalisées, sans étudier les retours ni les annulations. Ce périmètre est celui de la base nettoyée du projet ML : **777 622 lignes d'achats et 5 877 clients**.

## 6. Questions métier et indicateurs de performance

| Question métier | KPI | Axes d'analyse |
|---|---|---|
| Comment évolue le chiffre d'affaires, notamment en novembre ? | Chiffre d'affaires | Année, trimestre, mois |
| Quels pays génèrent le plus de chiffre d'affaires ? | CA, nombre de clients | Pays |
| Comment le chiffre d'affaires se répartit-il entre le Royaume-Uni et l'export ? | CA, part du CA | Pays |
| Quels produits se vendent le mieux ? | CA, quantités vendues | Produit |
| Combien dépense un client en moyenne par commande, et ce panier est-il représentatif ? | Panier moyen (complété par le panier médian) | Temps, segment |
| Quelle est la contribution de chaque segment au chiffre d'affaires ? | Part du CA par segment | Segment |
| Les ventes progressent-elles d'une année à l'autre ? | CA de la période précédente, évolution annuelle | Année |

## 7. Définition des KPI

Les mesures DAX correspondantes seront écrites lors de l'implémentation Power BI (phase 5).

### 7.1 Chiffre d'affaires

Somme des montants des lignes d'achat.

Formule : CA = Σ (Quantity × Price)

### 7.2 Nombre de factures

Nombre de numéros de facture distincts parmi les achats du périmètre.

Formule : Nombre de factures = nombre de `InvoiceNo` distincts

### 7.3 Nombre de clients

Nombre de clients distincts ayant effectué des achats.

Formule : Nombre de clients = nombre de `CustomerKey` distincts

### 7.4 Quantité vendue

Somme des quantités des lignes d'achat.

Formule : Quantité vendue = Σ Quantity

### 7.5 Panier moyen

Montant moyen dépensé par facture.

Formule : Panier moyen = Chiffre d'affaires / Nombre de factures

Le panier moyen est tiré vers le haut par quelques gros clients : le **panier médian** (montant au milieu de la distribution des factures) est utilisé comme indicateur complémentaire.
Panier médian : médiane des montants totaux des factures, chaque facture étant calculée comme la somme des montants de ses lignes d'achat.

### 7.6 Part du chiffre d'affaires par segment

Pourcentage du chiffre d'affaires total généré par un segment de clients.

Formule : Part du CA = (CA du segment / CA total) × 100

### 7.7 Chiffre d'affaires de la période précédente

Chiffre d'affaires réalisé sur la même période un an plus tôt, utilisé pour comparer les performances annuelles.

### 7.8 Évolution annuelle du chiffre d'affaires

Variation du chiffre d'affaires par rapport à la même période de l'année précédente.

Formule : Évolution annuelle (%) = ((CA année N - CA année N-1) / CA année N-1) × 100

La comparaison n'a de sens que sur des périodes équivalentes : 2009 ne contient que décembre et 2011 s'arrête le 9 décembre (voir section 9).

## 8. Chiffres de référence

Ces valeurs, calculées sur la base nettoyée (notebook `01_data_exploration`), servent de repère pour vérifier l'ETL (phase 3) et le modèle Power BI (phase 5).

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires total | 17 250 156,23 £ |
| Nombre de factures | 36 859 |
| Nombre de clients | 5 877 |
| Quantité vendue | 10 508 717 |
| Panier moyen | 468,00 £ |
| Panier médian | 302,46 £ |
| Ventes sans segment | 0 |

Le nombre de factures (36 859) ne concerne que les achats de clients identifiés ; il diffère du total brut de 53 628 factures, qui inclut aussi les annulations et les lignes sans identifiant client.

**Chiffre d'affaires par année**

| Année | CA | Remarque |
|---|---|---|
| 2009 | 680 601,01 £ | Décembre uniquement |
| 2010 | 8 326 143,01 £ | Année complète |
| 2011 | 8 243 412,20 £ | Jusqu'au 9 décembre |

**Comparaison à période égale (janvier à novembre)**

| Année | CA janvier–novembre |
|---|---|
| 2010 | 7 760 150,28 £ |
| 2011 | 7 728 981,76 £ |

À période égale, le chiffre d'affaires est quasi stable (environ -0,4 % entre 2010 et 2011).

**Chiffre d'affaires par pays (5 premiers)**

| Pays | CA | Part du CA |
|---|---|---|
| United Kingdom | 14 379 924,62 £ | 83,4 % |
| EIRE | 616 570,54 £ | 3,6 % |
| Netherlands | 549 970,09 £ | 3,2 % |
| Germany | 386 490,51 £ | 2,2 % |
| France | 324 368,96 £ | 1,9 % |

Les cinq premiers pays représentent 94,2 % du chiffre d'affaires ; le Royaume-Uni à lui seul en réalise 83,4 %.

**Chiffre d'affaires par segment**

| Segment | CA | Part du CA |
|---|---|---|
| VIP et très fidèles | 12 690 244,49 £ | 73,6 % |
| Intermédiaires à risque | 2 879 620,02 £ | 16,7 % |
| Récents à potentiel | 1 052 647,48 £ | 6,1 % |
| Inactifs et occasionnels | 627 644,24 £ | 3,6 % |

## 9. Contraintes et limites des données

- Le dataset ne contient pas les coûts d'achat ni les marges : il n'est pas possible de mesurer la rentabilité réelle, uniquement le chiffre d'affaires.
- Les données couvrent une période historique limitée, de décembre 2009 à décembre 2011.
- Les années ne sont pas comparables telles quelles : 2009 ne contient que le mois de décembre et les données de décembre 2011 s'arrêtent au 9 décembre. La comparaison annuelle se fait sur la période de janvier à novembre.
- Les lignes sans identifiant client (22,8 % des lignes brutes) sont exclues du périmètre : le chiffre d'affaires réel de l'entreprise est donc supérieur à celui analysé ici.
- Les retours et annulations ne sont pas analysés : un achat annulé reste comptabilisé comme une vente dans le chiffre d'affaires du client.
- Les segments de clients issus de K-Means constituent une segmentation à une date de référence (10 décembre 2011) et ne représentent pas un historique des changements de comportement.
- Le jeu de données ne contient pas de catégorie de produits : il n'existe pas de hiérarchie naturelle sur la dimension produit.
- Les résultats doivent être interprétés dans le périmètre de la base nettoyée retenue pour le projet.

## 10. Conclusion du cadrage métier

Cette phase a permis d'identifier les besoins décisionnels, de définir les questions métier et de sélectionner les KPI nécessaires au pilotage de l'activité e-commerce. Les chiffres de référence calculés sur la base nettoyée serviront à valider les phases suivantes.

Les axes d'analyse identifiés — temps, produit, client (avec son segment) et pays — serviront de base à la prochaine phase : la modélisation multidimensionnelle et la conception du schéma en étoile.
