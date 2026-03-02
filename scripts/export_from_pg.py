"""
Export data from PostgreSQL to CSV for offline analysis.
Usage: python scripts/export_from_pg.py [--table TABLE_NAME] [--output PATH]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_from_postgres, discover_schema, get_pg_engine


def main():
    parser = argparse.ArgumentParser(description="Export Telegram data from PostgreSQL to CSV")
    parser.add_argument("--table", type=str, default=None, help="Table name (auto-detected if omitted)")
    parser.add_argument("--output", type=str, default="data/messages.csv", help="Output CSV path")
    parser.add_argument("--query", type=str, default=None, help="Custom SQL query")
    parser.add_argument("--schema-only", action="store_true", help="Only show schema, don't export")
    args = parser.parse_args()

    engine = get_pg_engine()
    schema = discover_schema(engine)

    print("=== Database Schema ===")
    for table, columns in schema.items():
        print(f"\n📋 {table}:")
        for col in columns:
            print(f"   - {col}")

    if args.schema_only:
        return

    print(f"\nExporting data...")
    df = load_from_postgres(table_name=args.table, query=args.query)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")

    if "date" in df.columns:
        print(f"Date range: {df['date'].min()} — {df['date'].max()}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✅ Exported to {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
