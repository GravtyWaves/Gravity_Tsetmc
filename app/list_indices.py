"""
Index Listing and Management Module

This module provides comprehensive functionality for listing, analyzing,
and managing stock market indices in the TSETMC database.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import func
from app.db import SessionLocal, Index, IndexPrice, Sector


class IndexManager:
    """Manager class for index-related operations"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def __del__(self):
        """Ensure session is closed when object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def close_session(self):
        """Explicitly close the database session"""
        self.session.close()
    
    def get_all_indices(self, active_only: bool = True) -> List[Index]:
        """
        Retrieve all indices from the database.
        
        Args:
            active_only: If True, only return active indices
            
        Returns:
            List of Index objects
        """
        query = self.session.query(Index)
        if active_only:
            query = query.filter(Index.is_active == True)
        
        return query.order_by(Index.type, Index.name).all()
    
    def get_indices_by_type(self, index_type: str, active_only: bool = True) -> List[Index]:
        """
        Retrieve indices filtered by type.
        
        Args:
            index_type: Type of indices to retrieve (market, sector, etc.)
            active_only: If True, only return active indices
            
        Returns:
            List of Index objects matching the type
        """
        query = self.session.query(Index).filter(Index.type == index_type)
        if active_only:
            query = query.filter(Index.is_active == True)
        
        return query.order_by(Index.name).all()
    
    def get_index_stats(self, index_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific index.
        
        Args:
            index_id: ID of the index
            
        Returns:
            Dictionary containing index statistics
        """
        index = self.session.query(Index).filter(Index.id == index_id).first()
        if not index:
            return {}
        
        # Count price records
        price_count = self.session.query(IndexPrice).filter(
            IndexPrice.index_id == index_id
        ).count()
        
        # Get latest price date
        latest_date = self.session.query(
            func.max(IndexPrice.date)
        ).filter(IndexPrice.index_id == index_id).scalar()
        
        return {
            'index': index,
            'price_record_count': price_count,
            'latest_price_date': latest_date,
            'has_prices': price_count > 0
        }
    
    def search_indices(self, search_term: str, active_only: bool = True) -> List[Index]:
        """
        Search indices by name or description.
        
        Args:
            search_term: Term to search for in name and description
            active_only: If True, only search active indices
            
        Returns:
            List of matching Index objects
        """
        query = self.session.query(Index).filter(
            (Index.name.contains(search_term)) | 
            (Index.name_en.contains(search_term)) |
            (Index.description.contains(search_term))
        )
        
        if active_only:
            query = query.filter(Index.is_active == True)
        
        return query.order_by(Index.name).all()


def display_indices_table(indices: List[Index], show_stats: bool = False) -> None:
    """
    Display indices in a formatted table.
    
    Args:
        indices: List of Index objects to display
        show_stats: If True, include price statistics
    """
    if not indices:
        print("No indices found.")
        return
    
    # Table headers
    if show_stats:
        headers = f"{'ID':<4} | {'Farsi Name':<30} | {'English Name':<30} | {'WebID':<20} | {'Type':<12} | {'Prices':<8} | {'Status':<8}"
        separator = '-' * 140
    else:
        headers = f"{'ID':<4} | {'Farsi Name':<30} | {'English Name':<30} | {'WebID':<20} | {'Type':<12} | {'Status':<8}"
        separator = '-' * 120
    
    print(headers)
    print(separator)
    
    manager = IndexManager()
    
    for idx in indices:
        status = "Active" if idx.is_active else "Inactive"
        english_name = idx.name_en or idx.description or '-'
        
        if show_stats:
            stats = manager.get_index_stats(idx.id)
            price_count = stats.get('price_record_count', 0)
            price_status = f"{price_count:>6}" if price_count > 0 else "No Data"
            
            print(f"{idx.id:<4} | {idx.name:<30} | {english_name:<30} | {idx.web_id or '-':<20} | {idx.type or '-':<12} | {price_status:<8} | {status:<8}")
        else:
            print(f"{idx.id:<4} | {idx.name:<30} | {english_name:<30} | {idx.web_id or '-':<20} | {idx.type or '-':<12} | {status:<8}")
    
    manager.close_session()


def list_all_indices(active_only: bool = True, show_stats: bool = False) -> None:
    """
    List all indices in the database.
    
    Args:
        active_only: If True, only show active indices
        show_stats: If True, include price statistics
    """
    manager = IndexManager()
    try:
        indices = manager.get_all_indices(active_only=active_only)
        
        print(f"\n{' INDICES LIST ':=^120}")
        print(f"Total indices found: {len(indices)}")
        if active_only:
            print("Showing active indices only")
        print()
        
        display_indices_table(indices, show_stats=show_stats)
        
    finally:
        manager.close_session()


def list_indices_by_type(index_type: str, active_only: bool = True, show_stats: bool = False) -> None:
    """
    List indices filtered by type.
    
    Args:
        index_type: Type of indices to display
        active_only: If True, only show active indices
        show_stats: If True, include price statistics
    """
    manager = IndexManager()
    try:
        indices = manager.get_indices_by_type(index_type, active_only=active_only)
        
        print(f"\n{' INDICES BY TYPE ':=^120}")
        print(f"Type: {index_type}")
        print(f"Total indices found: {len(indices)}")
        print()
        
        display_indices_table(indices, show_stats=show_stats)
        
    finally:
        manager.close_session()


def show_index_detail(index_id: int) -> None:
    """
    Display detailed information for a specific index.
    
    Args:
        index_id: ID of the index to display
    """
    manager = IndexManager()
    try:
        stats = manager.get_index_stats(index_id)
        
        if not stats or 'index' not in stats:
            print(f"Index with ID {index_id} not found.")
            return
        
        index = stats['index']
        
        print(f"\n{' INDEX DETAILS ':=^80}")
        print(f"ID: {index.id}")
        print(f"Farsi Name: {index.name}")
        print(f"English Name: {index.name_en or 'N/A'}")
        print(f"Web ID: {index.web_id or 'N/A'}")
        print(f"Type: {index.type or 'N/A'}")
        print(f"Description: {index.description or 'N/A'}")
        print(f"Status: {'Active' if index.is_active else 'Inactive'}")
        print(f"Created: {index.created_at}")
        print(f"Updated: {index.updated_at}")
        
        if index.sector_id:
            sector = manager.session.query(Sector).filter(Sector.sector_id == index.sector_id).first()
            if sector:
                print(f"Sector: {sector.sector_name} (ID: {sector.sector_id})")
        
        print(f"\nPrice Statistics:")
        print(f"Total Price Records: {stats['price_record_count']}")
        print(f"Latest Price Date: {stats['latest_price_date'] or 'N/A'}")
        print(f"Has Price Data: {'Yes' if stats['has_prices'] else 'No'}")
        print("=" * 80)
        
    finally:
        manager.close_session()


def search_and_display_indices(search_term: str, active_only: bool = True, show_stats: bool = False) -> None:
    """
    Search for indices and display results.
    
    Args:
        search_term: Term to search for
        active_only: If True, only search active indices
        show_stats: If True, include price statistics
    """
    manager = IndexManager()
    try:
        indices = manager.search_indices(search_term, active_only=active_only)
        
        print(f"\n{' SEARCH RESULTS ':=^120}")
        print(f"Search term: '{search_term}'")
        print(f"Total indices found: {len(indices)}")
        print()
        
        display_indices_table(indices, show_stats=show_stats)
        
    finally:
        manager.close_session()


def export_indices_to_csv(filename: str = "indices_export.csv", active_only: bool = True) -> None:
    """
    Export indices data to CSV file.
    
    Args:
        filename: Output CSV filename
        active_only: If True, only export active indices
    """
    import csv
    from datetime import datetime
    
    manager = IndexManager()
    try:
        indices = manager.get_all_indices(active_only=active_only)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'name_en', 'web_id', 'type', 'description', 'is_active', 'sector_id', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for index in indices:
                writer.writerow({
                    'id': index.id,
                    'name': index.name,
                    'name_en': index.name_en or '',
                    'web_id': index.web_id or '',
                    'type': index.type or '',
                    'description': index.description or '',
                    'is_active': index.is_active,
                    'sector_id': index.sector_id or '',
                    'created_at': index.created_at.isoformat() if index.created_at else ''
                })
        
        print(f"Exported {len(indices)} indices to {filename}")
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
    finally:
        manager.close_session()


def main():
    """Main function with interactive menu for index management."""
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1]
        
        if command == "list":
            active_only = "--all" not in sys.argv
            show_stats = "--stats" in sys.argv
            list_all_indices(active_only=active_only, show_stats=show_stats)
        
        elif command == "type" and len(sys.argv) > 2:
            index_type = sys.argv[2]
            active_only = "--all" not in sys.argv
            show_stats = "--stats" in sys.argv
            list_indices_by_type(index_type, active_only=active_only, show_stats=show_stats)
        
        elif command == "detail" and len(sys.argv) > 2:
            try:
                index_id = int(sys.argv[2])
                show_index_detail(index_id)
            except ValueError:
                print("Error: Index ID must be a number")
        
        elif command == "search" and len(sys.argv) > 2:
            search_term = sys.argv[2]
            active_only = "--all" not in sys.argv
            show_stats = "--stats" in sys.argv
            search_and_display_indices(search_term, active_only=active_only, show_stats=show_stats)
        
        elif command == "export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "indices_export.csv"
            active_only = "--all" not in sys.argv
            export_indices_to_csv(filename, active_only=active_only)
        
        elif command == "help":
            print_help()
        
        else:
            print("Invalid command. Use 'help' for usage information.")
    
    else:
        # Interactive mode
        while True:
            print("\n" + "="*50)
            print("INDEX MANAGEMENT SYSTEM")
            print("="*50)
            print("1. List all indices")
            print("2. List indices by type")
            print("3. Show index details")
            print("4. Search indices")
            print("5. Export to CSV")
            print("6. Help")
            print("7. Exit")
            print("-"*50)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                active_only = input("Show only active indices? (y/n): ").lower() != 'n'
                show_stats = input("Show price statistics? (y/n): ").lower() == 'y'
                list_all_indices(active_only=active_only, show_stats=show_stats)
            
            elif choice == "2":
                index_type = input("Enter index type (market/sector): ").strip()
                active_only = input("Show only active indices? (y/n): ").lower() != 'n'
                show_stats = input("Show price statistics? (y/n): ").lower() == 'y'
                list_indices_by_type(index_type, active_only=active_only, show_stats=show_stats)
            
            elif choice == "3":
                try:
                    index_id = int(input("Enter index ID: "))
                    show_index_detail(index_id)
                except ValueError:
                    print("Error: Index ID must be a number")
            
            elif choice == "4":
                search_term = input("Enter search term: ").strip()
                active_only = input("Search only active indices? (y/n): ").lower() != 'n'
                show_stats = input("Show price statistics? (y/n): ").lower() == 'y'
                search_and_display_indices(search_term, active_only=active_only, show_stats=show_stats)
            
            elif choice == "5":
                filename = input("Enter CSV filename (default: indices_export.csv): ").strip()
                if not filename:
                    filename = "indices_export.csv"
                active_only = input("Export only active indices? (y/n): ").lower() != 'n'
                export_indices_to_csv(filename, active_only=active_only)
            
            elif choice == "6":
                print_help()
            
            elif choice == "7":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")


def print_help():
    """Print help information for command line usage."""
    help_text = """
INDEX MANAGEMENT SYSTEM - USAGE

Command Line Usage:
    python list_indices.py list [--all] [--stats]
    python list_indices.py type <type> [--all] [--stats]
    python list_indices.py detail <index_id>
    python list_indices.py search <term> [--all] [--stats]
    python list_indices.py export [filename] [--all]
    python list_indices.py help

Options:
    --all    : Include inactive indices
    --stats  : Show price statistics

Examples:
    python list_indices.py list
    python list_indices.py type market --stats
    python list_indices.py detail 5
    python list_indices.py search "شاخص کل"
    python list_indices.py export my_indices.csv
    """
    print(help_text)


if __name__ == "__main__":
    main()