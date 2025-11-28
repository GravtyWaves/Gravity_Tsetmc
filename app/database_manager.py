"""
Database Table Management System

A comprehensive utility for managing TSETMC database tables including:
- Listing tables and their contents
- Resetting specific tables
- Reloading data
- Bulk operations
"""

import sys
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy import inspect, text

from app.db import (
    SessionLocal, Base, engine, 
    Symbol, Index, Market, Sector, Panel,
    SymbolPrice, IndexPrice, RIData, ShareholdersInfo, UsdIrrPrice
)
from app.fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_ri_data,
    fetch_and_store_shareholders_info,
    fetch_and_store_usd_irr_prices
)
from app.list_fetcher import (
    fetch_and_store_symbol_list,
    fetch_and_store_index_list,
    fetch_and_store_market_list,
    fetch_and_store_panel_list,
    fetch_and_store_sector_list
)


class TableType(Enum):
    """Enumeration of database table types"""
    SYMBOL = "symbol"
    INDEX = "index"
    MARKET = "market"
    SECTOR = "sector"
    PANEL = "panel"
    SYMBOL_PRICE = "symbol_price"
    INDEX_PRICE = "index_price"
    RI_DATA = "ri_data"
    SHAREHOLDERS = "shareholders"
    USD_IRR = "usd_irr"


class TableManager:
    """Manager class for database table operations"""
    
    # Table configuration mapping
    TABLE_CONFIG = {
        TableType.SYMBOL: {
            'model': Symbol,
            'fetcher': fetch_and_store_symbol_list,
            'requires_reload': False
        },
        TableType.INDEX: {
            'model': Index,
            'fetcher': fetch_and_store_index_list,
            'requires_reload': False
        },
        TableType.MARKET: {
            'model': Market,
            'fetcher': fetch_and_store_market_list,
            'requires_reload': False
        },
        TableType.SECTOR: {
            'model': Sector,
            'fetcher': fetch_and_store_sector_list,
            'requires_reload': False
        },
        TableType.PANEL: {
            'model': Panel,
            'fetcher': fetch_and_store_panel_list,
            'requires_reload': False
        },
        TableType.SYMBOL_PRICE: {
            'model': SymbolPrice,
            'fetcher': fetch_and_store_symbol_prices,
            'requires_reload': True,
            'reload_args': {'adjust': True}
        },
        TableType.INDEX_PRICE: {
            'model': IndexPrice,
            'fetcher': fetch_and_store_index_prices,
            'requires_reload': True
        },
        TableType.RI_DATA: {
            'model': RIData,
            'fetcher': fetch_and_store_ri_data,
            'requires_reload': True
        },
        TableType.SHAREHOLDERS: {
            'model': ShareholdersInfo,
            'fetcher': fetch_and_store_shareholders_info,
            'requires_reload': True
        },
        TableType.USD_IRR: {
            'model': UsdIrrPrice,
            'fetcher': fetch_and_store_usd_irr_prices,
            'requires_reload': True
        }
    }
    
    def __init__(self):
        self.session = SessionLocal()
        self.inspector = inspect(engine)
    
    def __del__(self):
        """Ensure session is closed when object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def close_session(self):
        """Explicitly close the database session"""
        self.session.close()
    
    def get_table_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all tables.
        
        Returns:
            Dictionary with table statistics
        """
        stats = {}
        
        for table_type, config in self.TABLE_CONFIG.items():
            model = config['model']
            table_name = model.__tablename__
            
            try:
                record_count = self.session.query(model).count()
                exists = self.inspector.has_table(table_name)
                
                stats[table_name] = {
                    'table_type': table_type.value,
                    'exists': exists,
                    'record_count': record_count if exists else 0,
                    'model_class': model.__name__,
                    'requires_reload': config.get('requires_reload', False)
                }
            except Exception as e:
                stats[table_name] = {
                    'table_type': table_type.value,
                    'exists': False,
                    'record_count': 0,
                    'error': str(e)
                }
        
        return stats
    
    def list_table_contents(self, table_type: TableType, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List contents of a specific table.
        
        Args:
            table_type: Type of table to list
            limit: Maximum number of records to display
            
        Returns:
            List of table records
        """
        config = self.TABLE_CONFIG.get(table_type)
        if not config:
            raise ValueError(f"Unknown table type: {table_type}")
        
        model = config['model']
        records = self.session.query(model).limit(limit).all()
        
        result = []
        for record in records:
            record_dict = {}
            for column in model.__table__.columns:
                value = getattr(record, column.name)
                record_dict[column.name] = value
            result.append(record_dict)
        
        return result
    
    def reset_table(self, table_type: TableType, reload_data: bool = True) -> Dict[str, Any]:
        """
        Reset a specific table (drop and recreate).
        
        Args:
            table_type: Type of table to reset
            reload_data: Whether to reload data after reset
            
        Returns:
            Operation result
        """
        config = self.TABLE_CONFIG.get(table_type)
        if not config:
            raise ValueError(f"Unknown table type: {table_type}")
        
        model = config['model']
        table_name = model.__tablename__
        
        print(f"[RESET] Resetting table: {table_name}...")
        
        try:
            # Drop and recreate table
            with engine.connect() as conn:
                if self.inspector.has_table(table_name):
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                    conn.commit()
            
            model.__table__.create(bind=engine, checkfirst=True)
            
            result = {
                'table': table_name,
                'status': 'reset',
                'reloaded': False
            }
            
            # Reload data if requested and fetcher available
            if reload_data and config.get('fetcher'):
                print(f"[RELOAD] Reloading data for {table_name}...")
                fetcher = config['fetcher']
                reload_args = config.get('reload_args', {})
                
                if config.get('requires_reload', False):
                    # For tables that need data from other tables
                    if table_type == TableType.SYMBOL_PRICE:
                        symbols = [(s.symbol_fa, s.symbol_en) for s in self.session.query(Symbol).all()]
                        fetcher(symbols, **reload_args)
                    elif table_type == TableType.INDEX_PRICE:
                        indices = [idx.name for idx in self.session.query(Index).all()]
                        fetcher(indices, **reload_args)
                    else:
                        fetcher(**reload_args)
                else:
                    fetcher(**reload_args)
                
                result['reloaded'] = True
            
            print(f"[RESET] ✓ Table {table_name} reset successfully")
            return result
            
        except Exception as e:
            print(f"[RESET] ✗ Error resetting table {table_name}: {e}")
            return {
                'table': table_name,
                'status': 'error',
                'error': str(e)
            }
    
    def reset_multiple_tables(self, table_types: List[TableType], reload_data: bool = True) -> Dict[str, Any]:
        """
        Reset multiple tables at once.
        
        Args:
            table_types: List of table types to reset
            reload_data: Whether to reload data after reset
            
        Returns:
            Summary of operations
        """
        results = {}
        
        for table_type in table_types:
            results[table_type.value] = self.reset_table(table_type, reload_data)
        
        return {
            'operation': 'batch_reset',
            'tables_reset': len(table_types),
            'results': results
        }
    
    def reset_all_prices(self) -> Dict[str, Any]:
        """
        Reset all price-related tables.
        
        Returns:
            Summary of operations
        """
        price_tables = [
            TableType.SYMBOL_PRICE,
            TableType.INDEX_PRICE,
            TableType.USD_IRR
        ]
        
        return self.reset_multiple_tables(price_tables, reload_data=True)
    
    def reset_all_investor_data(self) -> Dict[str, Any]:
        """
        Reset all investor-related tables.
        
        Returns:
            Summary of operations
        """
        investor_tables = [
            TableType.RI_DATA,
            TableType.SHAREHOLDERS
        ]
        
        return self.reset_multiple_tables(investor_tables, reload_data=True)
    
    def reload_table_data(self, table_type: TableType) -> Dict[str, Any]:
        """
        Reload data for a specific table without resetting.
        
        Args:
            table_type: Type of table to reload
            
        Returns:
            Operation result
        """
        config = self.TABLE_CONFIG.get(table_type)
        if not config:
            raise ValueError(f"Unknown table type: {table_type}")
        
        fetcher = config.get('fetcher')
        if not fetcher:
            return {
                'table': table_type.value,
                'status': 'error',
                'error': 'No fetcher available for this table'
            }
        
        try:
            print(f"[RELOAD] Reloading data for {table_type.value}...")
            reload_args = config.get('reload_args', {})
            
            if config.get('requires_reload', False):
                if table_type == TableType.SYMBOL_PRICE:
                    symbols = [(s.symbol_fa, s.symbol_en) for s in self.session.query(Symbol).all()]
                    fetcher(symbols, **reload_args)
                elif table_type == TableType.INDEX_PRICE:
                    indices = [idx.name for idx in self.session.query(Index).all()]
                    fetcher(indices, **reload_args)
                else:
                    fetcher(**reload_args)
            else:
                fetcher(**reload_args)
            
            print(f"[RELOAD] ✓ Data reloaded for {table_type.value}")
            return {
                'table': table_type.value,
                'status': 'reloaded'
            }
            
        except Exception as e:
            print(f"[RELOAD] ✗ Error reloading {table_type.value}: {e}")
            return {
                'table': table_type.value,
                'status': 'error',
                'error': str(e)
            }


def display_table_stats(stats: Dict[str, Dict[str, Any]]) -> None:
    """Display table statistics in a formatted table"""
    if not stats:
        print("No table statistics available.")
        return
    
    print(f"\n{' DATABASE TABLE STATISTICS ':=^80}")
    print(f"{'Table Name':<20} | {'Type':<12} | {'Exists':<6} | {'Records':<8} | {'Reloadable':<10}")
    print('-' * 80)
    
    for table_name, table_stats in stats.items():
        exists = table_stats.get('exists', False)
        record_count = table_stats.get('record_count', 0)
        table_type = table_stats.get('table_type', 'unknown')
        requires_reload = table_stats.get('requires_reload', False)
        
        exists_str = "Yes" if exists else "No"
        reloadable_str = "Yes" if requires_reload else "No"
        
        print(f"{table_name:<20} | {table_type:<12} | {exists_str:<6} | {record_count:<8} | {reloadable_str:<10}")
    
    print('=' * 80)


def main():
    """Main function with interactive menu for table management"""
    manager = TableManager()
    
    try:
        while True:
            print("\n" + "="*60)
            print("DATABASE TABLE MANAGEMENT SYSTEM")
            print("="*60)
            print("1. Display Table Statistics")
            print("2. List Table Contents")
            print("3. Reset Single Table")
            print("4. Reset Multiple Tables")
            print("5. Reset All Price Tables")
            print("6. Reset All Investor Data Tables")
            print("7. Reload Table Data (Without Reset)")
            print("8. Exit")
            print("-"*60)
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                stats = manager.get_table_stats()
                display_table_stats(stats)
            
            elif choice == "2":
                print("\nAvailable Tables:")
                for i, table_type in enumerate(TableType, 1):
                    print(f"{i}. {table_type.value}")
                
                try:
                    table_choice = int(input("Select table: ")) - 1
                    if 0 <= table_choice < len(TableType):
                        selected_type = list(TableType)[table_choice]
                        limit = int(input("Record limit (default 10): ") or "10")
                        contents = manager.list_table_contents(selected_type, limit)
                        
                        print(f"\nContents of {selected_type.value} (first {limit} records):")
                        for record in contents:
                            print(record)
                    else:
                        print("Invalid table selection.")
                except (ValueError, IndexError):
                    print("Invalid input.")
            
            elif choice == "3":
                print("\nTables Available for Reset:")
                for i, table_type in enumerate(TableType, 1):
                    print(f"{i}. {table_type.value}")
                
                try:
                    table_choice = int(input("Select table to reset: ")) - 1
                    if 0 <= table_choice < len(TableType):
                        selected_type = list(TableType)[table_choice]
                        reload = input("Reload data after reset? (y/n): ").lower() == 'y'
                        result = manager.reset_table(selected_type, reload)
                        print(f"Result: {result}")
                    else:
                        print("Invalid table selection.")
                except (ValueError, IndexError):
                    print("Invalid input.")
            
            elif choice == "4":
                print("\nSelect tables to reset (comma-separated numbers):")
                for i, table_type in enumerate(TableType, 1):
                    print(f"{i}. {table_type.value}")
                
                try:
                    choices = input("Enter selections: ").strip()
                    selected_indices = [int(x.strip()) - 1 for x in choices.split(',')]
                    selected_types = [list(TableType)[i] for i in selected_indices 
                                    if 0 <= i < len(TableType)]
                    
                    if selected_types:
                        reload = input("Reload data after reset? (y/n): ").lower() == 'y'
                        result = manager.reset_multiple_tables(selected_types, reload)
                        print(f"Batch reset result: {result}")
                    else:
                        print("No valid tables selected.")
                except (ValueError, IndexError):
                    print("Invalid input.")
            
            elif choice == "5":
                confirm = input("Reset all price tables? (y/n): ").lower() == 'y'
                if confirm:
                    result = manager.reset_all_prices()
                    print(f"Price tables reset: {result}")
            
            elif choice == "6":
                confirm = input("Reset all investor data tables? (y/n): ").lower() == 'y'
                if confirm:
                    result = manager.reset_all_investor_data()
                    print(f"Investor data tables reset: {result}")
            
            elif choice == "7":
                print("\nTables Available for Reload:")
                reloadable_tables = [t for t in TableType 
                                  if manager.TABLE_CONFIG[t].get('fetcher')]
                for i, table_type in enumerate(reloadable_tables, 1):
                    print(f"{i}. {table_type.value}")
                
                try:
                    table_choice = int(input("Select table to reload: ")) - 1
                    if 0 <= table_choice < len(reloadable_tables):
                        selected_type = reloadable_tables[table_choice]
                        result = manager.reload_table_data(selected_type)
                        print(f"Reload result: {result}")
                    else:
                        print("Invalid table selection.")
                except (ValueError, IndexError):
                    print("Invalid input.")
            
            elif choice == "8":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    finally:
        manager.close_session()


if __name__ == "__main__":
    main()