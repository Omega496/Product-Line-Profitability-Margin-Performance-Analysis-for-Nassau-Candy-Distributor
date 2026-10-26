from src.data_loader import load_and_clean_data


def main() -> None:
    print("Executing Nassau Candy Distributor data pipeline...")
    df = load_and_clean_data()
    print(f"Data pipeline complete. Loaded and validated {len(df):,} records.")

