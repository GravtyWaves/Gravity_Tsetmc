"""
Central script for database table creation, initial data loading, and updating all tables.

This module provides functions to initialize the database, load initial data,
and update all market data including symbols, indices, and USD/IRR rates.
"""

from typing import List, Tuple
import logging

from gravity_tse import Get_ShareHoldersInfo, get_all_indices

from .db import Base, engine, SessionLocal, Symbol, Sector, Market, Panel
from .fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_ri_data,
    fetch_and_store_shareholders_info,
    fetch_and_store_usd_irr_prices,
    initialize_all_lists,
    fetch_all_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(message)s'
)


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Creates all database tables defined in the SQLAlchemy models.
    """
    print("[INIT] Creating all database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[INIT] ✓ All tables created successfully.")
    except Exception as e:
        print(f"[INIT] ✗ Error creating tables: {e}")
        raise


def load_initial_data() -> None:
    """
    Load initial data for all market structures.

    Fetches and stores initial data for markets, panels, sectors,
    symbols, and indices from JSON files.
    """
    print("[INIT] Loading initial market data...")
    try:
        initialize_all_lists()
        print("[INIT] ✓ Initial data loaded for all tables.")
    except Exception as e:
        print(f"[INIT] ✗ Error loading initial data: {e}")
        raise


def update_prices() -> None:
    """
    Update all price data including symbols and indices.
    """
    print("[UPDATE] Updating symbol prices...")
    try:
        fetch_and_store_symbol_prices(adjust=True)
        print("[UPDATE] ✓ Symbol prices updated.")
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating symbol prices: {e}")

    print("[UPDATE] Updating index prices...")
    try:
        # Get all indices including main and sector indices
        indices = get_all_indices()
        fetch_and_store_index_prices(indices=indices, adjust=True)
        print("[UPDATE] ✓ Index prices updated.")
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating index prices: {e}")


def update_investor_data() -> None:
    """
    Update investor-related data including RI data and shareholder information.
    """
    print("[UPDATE] Updating retail/institutional data...")
    try:
        fetch_and_store_ri_data()
        print("[UPDATE] ✓ Retail/institutional data updated.")
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating RI data: {e}")

    print("[UPDATE] Updating shareholder information...")
    try:
        fetch_and_store_shareholders_info()
        print("[UPDATE] ✓ Shareholder information updated.")
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating shareholder information: {e}")


def update_currency_data() -> None:
    """
    Update currency exchange rates.
    """
    print("[UPDATE] Updating USD/IRR prices...")
    try:
        fetch_and_store_usd_irr_prices()
        print("[UPDATE] ✓ USD/IRR prices updated.")
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating USD/IRR prices: {e}")


def update_all() -> None:
    """
    Update all market data including prices and investor information.

    Updates symbol prices, index prices, USD/IRR rates,
    retail/institutional data, and shareholder information.
    """
    print("[UPDATE] Starting comprehensive data update...")
    
    # Update price data
    update_prices()
    
    # Update investor data
    update_investor_data()
    
    # Update currency data
    update_currency_data()
    
    print("[UPDATE] ✓ All data update operations completed.")


def update_selected_symbols(symbols: List[str]) -> None:
    """
    Update data for selected symbols only.

    Args:
        symbols: List of symbol codes to update
    """
    if not symbols:
        print("[UPDATE] No symbols provided for update.")
        return

    print(f"[UPDATE] Updating data for {len(symbols)} selected symbols...")
    
    session = SessionLocal()
    try:
        # Get symbol pairs from database
        symbol_pairs = []
        for symbol_code in symbols:
            symbol = session.query(Symbol).filter_by(symbol_en=symbol_code).first()
            if symbol:
                symbol_pairs.append((symbol.symbol_fa, symbol.symbol_en))
            else:
                print(f"[UPDATE] ✗ Symbol '{symbol_code}' not found in database")
        
        if not symbol_pairs:
            print("[UPDATE] No valid symbols found to update.")
            return

        # Update symbol prices
        print("[UPDATE] Updating selected symbol prices...")
        fetch_and_store_symbol_prices(symbols=symbol_pairs, adjust=True)
        
        # Update RI data
        print("[UPDATE] Updating selected RI data...")
        fetch_and_store_ri_data(symbols=symbol_pairs)
        
        # Update shareholder info
        print("[UPDATE] Updating selected shareholder information...")
        fetch_and_store_shareholders_info(symbols=symbol_pairs)
        
        print(f"[UPDATE] ✓ Selected symbols update completed for {len(symbol_pairs)} symbols.")
        
    except Exception as e:
        print(f"[UPDATE] ✗ Error updating selected symbols: {e}")
    finally:
        session.close()


def reset_and_reload() -> None:
    """
    Reset the database and reload all data from scratch.
    
    Warning: This will delete all existing data!
    """
    print("[RESET] WARNING: This will delete all existing data!")
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() != 'yes':
        print("[RESET] Operation cancelled.")
        return
    
    print("[RESET] Resetting database...")
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("[RESET] ✓ All tables dropped.")
        
        # Recreate tables
        init_db()
        
        # Reload all data
        load_initial_data()
        update_all()
        
        print("[RESET] ✓ Database reset and reload completed successfully.")
        
    except Exception as e:
        print(f"[RESET] ✗ Error during reset: {e}")
        raise


def check_database_status() -> None:
    """
    Check the current status of the database including record counts.
    """
    session = SessionLocal()
    try:
        print("[STATUS] Database Status Report:")
        print("-" * 40)
        
        # Count records in each table
        markets_count = session.query(Market).count()
        panels_count = session.query(Panel).count()
        sectors_count = session.query(Sector).count()
        symbols_count = session.query(Symbol).count()
        symbol_prices_count = session.query(Symbol).count()
        indices_count = session.query(Sector).count()  # This should be Index table
        
        print(f"Markets: {markets_count}")
        print(f"Panels: {panels_count}")
        print(f"Sectors: {sectors_count}")
        print(f"Symbols: {symbols_count}")
        print(f"Symbol Prices: {symbol_prices_count}")
        print(f"Indices: {indices_count}")
        
        # Check for active symbols
        active_symbols = session.query(Symbol).filter_by(is_active=1).count()
        print(f"Active Symbols: {active_symbols}")
        
        print("-" * 40)
        print("[STATUS] Status check completed.")
        
    except Exception as e:
        print(f"[STATUS] ✗ Error checking database status: {e}")
    finally:
        session.close()


def main() -> None:
    """
    Main function with interactive menu for database operations.
    """
    import sys
    
    print("=" * 50)
    print("TSETMC Database Management System")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1]
        if command == "init":
            init_db()
        elif command == "load":
            load_initial_data()
        elif command == "update":
            update_all()
        elif command == "reset":
            reset_and_reload()
        elif command == "status":
            check_database_status()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, load, update, reset, status")
    else:
        # Interactive mode
        while True:
            print("\nAvailable Operations:")
            print("1. Initialize Database (Create Tables)")
            print("2. Load Initial Data")
            print("3. Update All Data")
            print("4. Update Selected Symbols")
            print("5. Reset and Reload Everything")
            print("6. Check Database Status")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                init_db()
            elif choice == "2":
                load_initial_data()
            elif choice == "3":
                update_all()
            elif choice == "4":
                symbols_input = input("Enter symbol codes (comma-separated): ").strip()
                symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
                update_selected_symbols(symbols)
            elif choice == "5":
                reset_and_reload()
            elif choice == "6":
                check_database_status()
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()