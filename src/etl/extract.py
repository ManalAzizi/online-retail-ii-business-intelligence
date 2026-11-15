from pathlib import Path
import pandas as pd


def extract_data(processed_dir: Path = Path("data/processed")) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrait les données nettoyées des ventes et les clusters RFM depuis data/processed/.
    """
    ventes_path = processed_dir / "online_retail_II_cleaned.parquet"
    clients_path = processed_dir / "customer_rfm_clusters.parquet"

    if not ventes_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {ventes_path}")
    if not clients_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {clients_path}")

    ventes = pd.read_parquet(ventes_path)
    clients = pd.read_parquet(clients_path)

    # Vérification des colonnes minimales requises
    req_ventes = {"Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country", "Montant"}
    req_clients = {"Customer ID", "Recency", "Frequency", "Monetary", "Cluster"}

    if not req_ventes.issubset(ventes.columns):
        raise ValueError(f"Colonnes manquantes dans ventes : {req_ventes - set(ventes.columns)}")
    if not req_clients.issubset(clients.columns):
        raise ValueError(f"Colonnes manquantes dans clients : {req_clients - set(clients.columns)}")

    print(f"[EXTRACT] Ventes extraites : {len(ventes):,} lignes")
    print(f"[EXTRACT] Clients extraits : {len(clients):,} lignes")

    return ventes, clients