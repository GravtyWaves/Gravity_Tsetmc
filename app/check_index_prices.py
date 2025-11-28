import sys
from sqlalchemy import func
from app.db import SessionLocal, Index, IndexPrice

def check_indices_and_prices():
    """
    Display all indices and their related price counts
    """
    session = SessionLocal()
    try:
        # Get all indices
        indices = session.query(Index).all()
        
        # Check if no indices found
        if not indices:
            print("No indices found in the database.")
            return
        
        # Print table header
        print(f"{'ID':<4} | {'Name':<30} | {'Type':<10} | {'WebID':<20} | {'Has Prices?':<12} | {'Price Count':<12}")
        print('-' * 100)
        
        # Display each index information
        for idx in indices:
            # Count related prices
            price_count = session.query(IndexPrice).filter_by(index_id=idx.id).count()
            has_prices = 'Yes' if price_count > 0 else 'No'
            
            print(f"{idx.id:<4} | {idx.name:<30} | {idx.type or '-':<10} | {idx.web_id or '-':<20} | {has_prices:<12} | {price_count:<12}")
        
        # Display summary statistics
        total_indices = len(indices)
        indices_with_prices = sum(1 for idx in indices if session.query(IndexPrice).filter_by(index_id=idx.id).count() > 0)
        
        print('-' * 100)
        print(f"Summary: {total_indices} indices | {indices_with_prices} with prices | {total_indices - indices_with_prices} without prices")
        
    except Exception as e:
        print(f"Error executing script: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure session is closed
        session.close()

if __name__ == "__main__":
    check_indices_and_prices()