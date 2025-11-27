#!/usr/bin/env python
"""
Script to check and display empty tables in the TSETMC database.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import (
    Market, Sector, Panel, SymbolList, SymbolPrice, IndexPrice, Index,
    RIData, UsdIrrPrice, ShareholdersInfo, get_session
)

def check_empty_tables():
    """Check which tables are empty and display the results."""
    session = get_session()

    tables = [
        ("markets", Market),
        ("sectors", Sector),
        ("panels", Panel),
        ("symbol_list", SymbolList),
        ("symbol_prices", SymbolPrice),
        ("index_prices", IndexPrice),
        ("indices", Index),
        ("ri_data", RIData),
        ("usd_irr_prices", UsdIrrPrice),
        ("shareholders_info", ShareholdersInfo),
    ]

    empty_tables = []
    non_empty_tables = []

    print("Checking database tables for emptiness...\n")

    for table_name, model_class in tables:
        try:
            count = session.query(model_class).count()
            if count == 0:
                empty_tables.append((table_name, count))
                print(f"  {table_name}: EMPTY (0 rows)")
            else:
                non_empty_tables.append((table_name, count))
                print(f"  {table_name}: {count} rows")
        except Exception as e:
            print(f"  {table_name}: ERROR - {e}")

    session.close()

    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Empty tables: {len(empty_tables)}")
    for table, count in empty_tables:
        print(f"  - {table}")

    print(f"\nNon-empty tables: {len(non_empty_tables)}")
    for table, count in non_empty_tables:
        print(f"  - {table}: {count} rows")

if __name__ == "__main__":
    check_empty_tables()
