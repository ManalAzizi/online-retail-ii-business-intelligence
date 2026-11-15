from pathlib import Path
import pandas as pd

from src.etl.extract import extract_data
from src.etl.transform import transform_all


def validate_star_schema(tables: dict[str, pd.DataFrame]) -> None:
    """
    Vérifie l'intégrité référentielle et les chiffres de référence issus de la phase 1.
    Lève une AssertionError si une anomalie est détectée.
    """
    fait = tables["Fait_Ventes"]
    dim_date = tables["Dim_Date"]
    dim_produit = tables["Dim_Produit"]
    dim_client = tables["Dim_Client"]
    dim_pays = tables["Dim_Pays"]

    nb_lignes = len(fait)
    nb_clients = fait["CustomerKey"].nunique()
    nb_factures = fait["InvoiceNo"].nunique()
    montant_total = round(fait["Montant"].sum(), 2)
    sans_segment = (~fait["CustomerKey"].isin(dim_client["CustomerKey"])).sum()
    cles_nulles = fait[["DateKey", "ProductKey", "CustomerKey", "CountryKey"]].isna().sum().sum()

    print("\n--- CONTRÔLES QUALITÉ ETL ---")
    print(f"Lignes Fait_Ventes  : {nb_lignes} (attendu : 777622)")
    print(f"Clients distincts   : {nb_clients} (attendu : 5877)")
    print(f"Factures distinctes : {nb_factures} (attendu : 36859)")
    print(f"Montant total (£)   : {montant_total} (attendu : 17250156.23)")
    print(f"Ventes sans segment : {sans_segment} (attendu : 0)")
    print(f"Clés étrangères NA  : {cles_nulles} (attendu : 0)")
    print(f"Taille Dim_Date     : {len(dim_date)} (attendu : 739)")
    print(f"Taille Dim_Produit  : {len(dim_produit)} (attendu : 4630)")
    print(f"Taille Dim_Client   : {len(dim_client)} (attendu : 5877)")
    print(f"Taille Dim_Pays     : {len(dim_pays)} (attendu : 41)")

    assert nb_lignes == 777_622, f"Erreur grain : {nb_lignes} lignes au lieu de 777 622"
    assert nb_clients == 5_877, f"Erreur clients : {nb_clients} au lieu de 5 877"
    assert nb_factures == 36_859, f"Erreur factures : {nb_factures} au lieu de 36 859"
    assert montant_total == 17_250_156.23, f"Erreur CA : {montant_total} au lieu de 17 250 156.23"
    assert sans_segment == 0, f"{sans_segment} ventes n'ont pas de correspondance dans Dim_Client"
    assert cles_nulles == 0, "Des clés étrangères sont nulles dans Fait_Ventes"
    assert len(dim_date) == 739, f"Dim_Date contient {len(dim_date)} lignes au lieu de 739"
    assert len(dim_produit) == 4_630, f"Dim_Produit contient {len(dim_produit)} lignes au lieu de 4 630"
    assert len(dim_pays) == 41, f"Dim_Pays contient {len(dim_pays)} lignes au lieu de 41"

    print("[VALIDATE] Tous les contrôles ont réussi avec succès.\n")


def load_to_csv(tables: dict[str, pd.DataFrame], output_dir: Path = Path("data/warehouse")) -> None:
    """Exporte les 5 tables en CSV (séparateur virgule, encodage UTF-8)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_name, df in tables.items():
        file_path = output_dir / f"{table_name}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
        print(f"[LOAD] Exporté : {file_path} ({len(df):,} lignes)")


def run_pipeline() -> None:
    """Exécute le pipeline ETL complet."""
    ventes, clients = extract_data(Path("data/processed"))
    tables = transform_all(ventes, clients)
    validate_star_schema(tables)
    load_to_csv(tables, Path("data/warehouse"))


if __name__ == "__main__":
    run_pipeline()