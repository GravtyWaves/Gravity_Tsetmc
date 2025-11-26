#!/usr/bin/env python
"""
Professional CLI for Gravity TSETMC Database Management
"""

import argparse
import sys
from app.db import Base, engine, SessionLocal, init_db
from app.list_fetcher import fetch_and_store_symbol_list, fetch_and_store_market_list, fetch_and_store_sector_list, fetch_and_store_panel_list, fetch_and_store_index_list
from app.fetcher import fetch_and_store_symbol_prices, fetch_and_store_index_prices
from app.usd_fetcher import fetch_and_store_usd_irr_prices
from gravity_tse import SymbolManager

# Configure stdout for UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def cmd_init_db():
    """Initialize database and create all tables"""
    print("[✓] Initializing database...")
    try:
        init_db()
        print("[✓] Database initialized successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error initializing database: {e}")
        return 1


def cmd_init_symbols():
    """Fetch and store initial symbol list data"""
    print("[✓] Fetching symbol list...")
    try:
        fetch_and_store_symbol_list()
        print("[✓] Symbol list stored successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error fetching symbol list: {e}")
        return 1


def cmd_init_markets():
    """Fetch and store market data"""
    print("[✓] Fetching market list...")
    try:
        fetch_and_store_market_list()
        print("[✓] Market list stored successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error fetching market list: {e}")
        return 1


def cmd_init_sectors():
    """Fetch and store sector data"""
    print("[✓] Fetching sector list...")
    try:
        fetch_and_store_sector_list()
        print("[✓] Sector list stored successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error fetching sector list: {e}")
        return 1


def cmd_init_panels():
    """Fetch and store panel data"""
    print("[✓] Fetching panel list...")
    try:
        fetch_and_store_panel_list()
        print("[✓] Panel list stored successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error fetching panel list: {e}")
        return 1


def cmd_init_indices():
    """Fetch and store index data"""
    print("[✓] Fetching index list...")
    try:
        fetch_and_store_index_list()
        print("[✓] Index list stored successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error fetching index list: {e}")
        return 1


def cmd_init_all():
    """Professional full initialization of database and all initial data"""
    print("\n" + "="*60)
    print("  GRAVITY TSETMC - Professional Database Initialization")
    print("="*60 + "\n")
    
    steps = [
        ("Database", cmd_init_db),
        ("Markets", cmd_init_markets),
        ("Sectors", cmd_init_sectors),
        ("Panels", cmd_init_panels),
        ("Symbols", cmd_init_symbols),
        ("Indices", cmd_init_indices),
    ]
    
    total_steps = len(steps)
    failed = []
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        print(f"\n[{i}/{total_steps}] {step_name}...")
        print("-" * 40)
        result = step_func()
        if result != 0:
            failed.append(step_name)
    
    print("\n" + "="*60)
    if failed:
        print(f"[✗] Initialization completed with {len(failed)} error(s):")
        for step in failed:
            print(f"    - {step}")
        print("="*60 + "\n")
        return 1
    else:
        print("[✓] All initialization steps completed successfully!")
        print("="*60 + "\n")
        return 0


def cmd_update_symbols(symbols=None):
    """Update symbol prices"""
    print(f"[✓] Updating symbol prices...")
    try:
        if symbols:
            print(f"    Symbols: {', '.join(symbols)}")
        fetch_and_store_symbol_prices(symbols or [])
        print("[✓] Symbol prices updated successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error updating symbol prices: {e}")
        return 1


def cmd_update_indices(indices=None):
    """Update index prices"""
    print(f"[✓] Updating index prices...")
    try:
        if indices:
            print(f"    Indices: {', '.join(indices)}")
        fetch_and_store_index_prices(indices or [])
        print("[✓] Index prices updated successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error updating index prices: {e}")
        return 1


def cmd_update_usd():
    """Update USD/IRR prices"""
    print("[✓] Updating USD/IRR prices...")
    try:
        fetch_and_store_usd_irr_prices()
        print("[✓] USD/IRR prices updated successfully!")
        return 0
    except Exception as e:
        print(f"[✗] Error updating USD/IRR prices: {e}")
        return 1


def cmd_update_all():
    """Update all data (symbols, indices, USD)"""
    print("\n" + "="*60)
    print("  GRAVITY TSETMC - Update All Data")
    print("="*60 + "\n")
    
    updates = [
        ("Symbol Prices", lambda: cmd_update_symbols()),
        ("Index Prices", lambda: cmd_update_indices()),
        ("USD/IRR Prices", cmd_update_usd),
    ]
    
    total_updates = len(updates)
    failed = []
    
    for i, (update_name, update_func) in enumerate(updates, 1):
        print(f"\n[{i}/{total_updates}] {update_name}...")
        print("-" * 40)
        result = update_func()
        if result != 0:
            failed.append(update_name)
    
    print("\n" + "="*60)
    if failed:
        print(f"[✗] Updates completed with {len(failed)} error(s):")
        for update in failed:
            print(f"    - {update}")
        print("="*60 + "\n")
        return 1
    else:
        print("[✓] All updates completed successfully!")
        print("="*60 + "\n")
        return 0


def cmd_check_webid(symbols):
    """Check and print WebID lookup result for given symbols"""
    print("[✓] Checking WebID for symbols...")
    for symbol in symbols:
        print(f"Symbol: {symbol}")
        try:
            result = SymbolManager.get_tse_webid(symbol)
            if result is None or (isinstance(result, bool) and not result):
                print("  [✗] No WebID found.")
            else:
                print(f"  [✓] WebID lookup result:")
                print(result)
        except Exception as e:
            print(f"  [✗] Error: {e}")
    print("[✓] Done.")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Gravity TSETMC - Professional Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py init-all              # Full initialization
  python cli.py update-all            # Update all data
  python cli.py init --symbols        # Initialize only symbols
  python cli.py update --symbols KHRO FMLI  # Update specific symbols
  python cli.py update --indices "شاخص کل" # Update specific index
  python cli.py update --usd          # Update USD/IRR prices
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Initialize commands
    init_parser = subparsers.add_parser("init", help="Initialize database data")
    init_parser.add_argument("--db", action="store_true", help="Initialize database tables only")
    init_parser.add_argument("--markets", action="store_true", help="Initialize markets only")
    init_parser.add_argument("--sectors", action="store_true", help="Initialize sectors only")
    init_parser.add_argument("--panels", action="store_true", help="Initialize panels only")
    init_parser.add_argument("--symbols", action="store_true", help="Initialize symbols only")
    init_parser.add_argument("--indices", action="store_true", help="Initialize indices only")
    
    subparsers.add_parser("init-all", help="Full professional initialization (all data)")
    
    # Update commands
    update_parser = subparsers.add_parser("update", help="Update database data")
    update_parser.add_argument("--symbols", nargs="*", metavar="SYMBOL", help="Update specific symbols (leave empty for all)")
    update_parser.add_argument("--indices", nargs="*", metavar="INDEX", help="Update specific indices (leave empty for all)")
    update_parser.add_argument("--usd", action="store_true", help="Update USD/IRR prices")

    subparsers.add_parser("update-all", help="Update all data")

    # Diagnostic: check-webid command
    check_webid_parser = subparsers.add_parser("check-webid", help="Check WebID lookup for symbols")
    check_webid_parser.add_argument("--symbols", nargs="+", metavar="SYMBOL", required=True, help="Symbols to check WebID for")
    
    # Reset commands
    reset_parser = subparsers.add_parser("reset", help="Reset and reload database")
    reset_parser.add_argument("--all", action="store_true", help="Reset all tables")
    reset_parser.add_argument("--symbol-prices", action="store_true", help="Reset symbol prices")
    reset_parser.add_argument("--index-prices", action="store_true", help="Reset index prices")
    
    # Status command
    subparsers.add_parser("status", help="Show database status")
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "init":
        if not any([args.db, args.markets, args.sectors, args.panels, args.symbols, args.indices]):
            # Initialize all if nothing specified
            return cmd_init_all()
        
        code = 0
        if args.db:
            code |= cmd_init_db()
        if args.markets:
            code |= cmd_init_markets()
        if args.sectors:
            code |= cmd_init_sectors()
        if args.panels:
            code |= cmd_init_panels()
        if args.symbols:
            code |= cmd_init_symbols()
        if args.indices:
            code |= cmd_init_indices()
        return code
    
    elif args.command == "init-all":
        return cmd_init_all()
    
    elif args.command == "update":
        if not any([args.symbols is not None, args.indices is not None, args.usd]):
            # Update all if nothing specified
            return cmd_update_all()
        
        code = 0
        if args.symbols is not None:
            code |= cmd_update_symbols(args.symbols if args.symbols else None)
        if args.indices is not None:
            code |= cmd_update_indices(args.indices if args.indices else None)
        if args.usd:
            code |= cmd_update_usd()
        return code
    
    elif args.command == "update-all":
        return cmd_update_all()
    
    elif args.command == "check-webid":
        return cmd_check_webid(args.symbols)
    
    elif args.command == "reset":
        print("[!] Reset functionality not yet implemented")
        return 1
    
    elif args.command == "status":
        print("[!] Status functionality not yet implemented")
        return 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
