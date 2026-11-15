import pandas as pd


MOIS_FR = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

JOURS_FR = {
    0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi",
    4: "vendredi", 5: "samedi", 6: "dimanche"
}

SEGMENTS_NOMS = {
    0: "VIP et très fidèles",
    1: "Inactifs et occasionnels",
    2: "Récents à potentiel",
    3: "Intermédiaires à risque"
}


def build_dim_date(ventes: pd.DataFrame) -> pd.DataFrame:
    """Construit Dim_Date : calendrier continu du 01/12/2009 au 09/12/2011 (739 jours)."""
    dates_norm = ventes["InvoiceDate"].dt.normalize()
    jours = pd.date_range(dates_norm.min(), dates_norm.max(), freq="D")

    dim_date = pd.DataFrame({
        "DateKey": jours.strftime("%Y%m%d").astype(int),
        "Date": jours.date,
        "Année": jours.year,
        "Trimestre": jours.quarter,
        "Mois": jours.month,
        "NomMois": jours.month.map(MOIS_FR),
        "Semaine": jours.isocalendar().week.astype(int).values,
        "JourSemaine": jours.dayofweek.map(JOURS_FR)
    })
    return dim_date


def build_dim_produit(ventes: pd.DataFrame) -> pd.DataFrame:
    """Construit Dim_Produit avec une unique description (la plus fréquente) par StockCode."""
    dim_produit = (
        ventes.groupby("StockCode", as_index=False)["Description"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "")
        .sort_values("StockCode")
        .reset_index(drop=True)
    )
    dim_produit.insert(0, "ProductKey", range(1, len(dim_produit) + 1))
    return dim_produit[["ProductKey", "StockCode", "Description"]]


def build_dim_pays(ventes: pd.DataFrame) -> pd.DataFrame:
    """Construit Dim_Pays avec la hiérarchie Zone > Pays."""
    pays_uniques = sorted(ventes["Country"].unique())
    dim_pays = pd.DataFrame({
        "CountryKey": range(1, len(pays_uniques) + 1),
        "Pays": pays_uniques
    })
    dim_pays["Zone"] = dim_pays["Pays"].apply(
        lambda p: "Royaume-Uni" if p == "United Kingdom" else "Export"
    )
    return dim_pays[["CountryKey", "Pays", "Zone"]]


def build_dim_client(clients: pd.DataFrame) -> pd.DataFrame:
    """Construit Dim_Client avec CustomerKey entier et libellés de segments K-Means."""
    dim_client = clients.copy()
    dim_client["CustomerKey"] = dim_client["Customer ID"].astype(int)
    dim_client["Segment"] = dim_client["Cluster"].map(SEGMENTS_NOMS)

    if dim_client["Segment"].isna().any():
        raise ValueError("Certains clusters n'ont pas pu être associés à un nom de segment.")

    dim_client = dim_client.sort_values("CustomerKey").reset_index(drop=True)
    return dim_client[["CustomerKey", "Segment", "Recency", "Frequency", "Monetary"]]


def build_fait_ventes(
    ventes: pd.DataFrame,
    dim_produit: pd.DataFrame,
    dim_pays: pd.DataFrame
) -> pd.DataFrame:
    """Construit la table de faits centrale Fait_Ventes au grain ligne de facture."""
    fait = ventes.copy()
    fait["DateKey"] = fait["InvoiceDate"].dt.strftime("%Y%m%d").astype(int)
    fait["CustomerKey"] = fait["Customer ID"].astype(int)

    # Remplacement des attributs descriptifs par les clés de substitution
    fait = fait.merge(dim_produit[["ProductKey", "StockCode"]], on="StockCode", how="left")
    fait = fait.merge(dim_pays[["CountryKey", "Pays"]], left_on="Country", right_on="Pays", how="left")

    fait = fait.rename(columns={
        "Invoice": "InvoiceNo",
        "Price": "UnitPrice"
    })

    colonnes_finales = [
        "InvoiceNo", "DateKey", "ProductKey", "CustomerKey", "CountryKey",
        "Quantity", "UnitPrice", "Montant"
    ]
    return fait[colonnes_finales]


def transform_all(ventes: pd.DataFrame, clients: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Orchestre la création des 5 tables du schéma en étoile."""
    print("[TRANSFORM] Construction des dimensions...")
    dim_date = build_dim_date(ventes)
    dim_produit = build_dim_produit(ventes)
    dim_pays = build_dim_pays(ventes)
    dim_client = build_dim_client(clients)

    print("[TRANSFORM] Construction de la table de faits...")
    fait_ventes = build_fait_ventes(ventes, dim_produit, dim_pays)

    return {
        "Dim_Date": dim_date,
        "Dim_Produit": dim_produit,
        "Dim_Pays": dim_pays,
        "Dim_Client": dim_client,
        "Fait_Ventes": fait_ventes
    }