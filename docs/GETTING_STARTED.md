# Getting Started Guide - Gravity TSETMC

## Installation Steps

### 1. Prerequisites

- Python 3.9 or higher
- Git
- pip or conda package manager

### 2. Installation

```bash
# Clone repository
git clone https://github.com/GravtyWaves/Gravity_Tsetmc.git
cd Gravity_Tsetmc

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Default configuration works for most use cases
```

### 4. Database Setup

```bash
# Initialize database
python app/init_all.py
```

## Usage Examples

### Example 1: Fetch Stock Price Data

```python
from gravity_tse import SymbolManager, PriceHistoryManager

# Find stock symbol
symbol_df = SymbolManager.get_tse_webid('خودرو')
print(symbol_df)

# Get price history
prices = PriceHistoryManager.get_price_history(
    stock='خودرو',
    start_date='1402-01-01',
    end_date='1402-12-29'
)

print(f"Fetched {len(prices)} price records")
print(prices.head())
```

### Example 2: Track USD/IRR Exchange Rate

```python
from gravity_tse import USDManager

# Get latest rate
latest_rate = USDManager.get_latest_usd_irr()
print(f"Date: {latest_rate['date']}")
print(f"Rate: {latest_rate['price']} IRR/USD")

# Get historical data
rate_history = USDManager.get_usd_irr_prices()
print(f"Historical data points: {len(rate_history)}")
```

### Example 3: Analyze Real/Institutional Trading

```python
from gravity_tse import Get_RI_History

# Get RI data
ri_data = Get_RI_History.get_ri_history('خودرو')

# Analyze institutional buying
institutional_buy = ri_data['No Buy Inst'].sum()
individual_buy = ri_data['No Buy Real'].sum()

print(f"Institutional buy orders: {institutional_buy}")
print(f"Individual buy orders: {individual_buy}")
```

### Example 4: Monitor Shareholders

```python
from gravity_tse import Get_ShareHoldersInfo

# Get shareholders
shareholders = Get_ShareHoldersInfo.get_shareholders_info('خودرو')

# Filter major shareholders
major = shareholders[shareholders['Shares Percent'] > 5]
print("Major shareholders:")
print(major[['Holder Name', 'Shares Percent']])
```

## CLI Commands

### Initialize Data

```bash
# Full initialization
python cli.py init-all

# Initialize specific data
python cli.py init --symbols      # Initialize symbol list
python cli.py init --sectors      # Initialize sector list
python cli.py init --indices      # Initialize indices
```

### Update Data

```bash
# Update everything
python cli.py update-all

# Update specific symbols
python cli.py update --symbols KHRO FMLI PDRO

# Update indices
python cli.py update --indices "شاخص کل" "شاخص کل هم وزن"

# Update RI data
python cli.py update --ri KHRO FMLI

# Update shareholders
python cli.py update --shareholders KHRO FMLI

# Update USD/IRR
python cli.py update --usd
```

### Query and Reset

```bash
# Check empty tables
python app/check_index_prices.py

# List all sectors
python app/list_indices.py

# Reset specific data
python cli.py reset --symbol-prices
python cli.py reset --index-prices
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/test_unit.py -v

# Integration tests only
pytest tests/test_integration.py -v

# With coverage report
pytest tests/ --cov=gravity_tse --cov=app --cov-report=html
```

### Check Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy gravity_tse app --ignore-missing-imports

# Security check
bandit -r .
```

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Verify virtual environment is activated
# Install dependencies again
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.9+
```

### Issue: Database connection error

**Solution:**
```bash
# Reinitialize database
rm -f tsetmc.db
python app/init_all.py

# Check database permissions
ls -la tsetmc.db
```

### Issue: API timeout errors

**Solution:**
- Check internet connection
- Increase timeout in .env: `API_TIMEOUT=30`
- Reduce number of concurrent requests
- Check if TSE API is accessible

### Issue: Import errors with gravity_tse

**Solution:**
```bash
# Reinstall in development mode
pip install -e .

# Or add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Best Practices

### 1. Error Handling

```python
from gravity_tse import SymbolManager
from utils.exceptions import SymbolNotFoundException

try:
    prices = SymbolManager.get_tse_webid('خودرو')
except SymbolNotFoundException as e:
    print(f"Symbol not found: {e}")
```

### 2. Logging

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

try:
    data = fetch_data()
    logger.info("Data fetched successfully")
except Exception as e:
    logger.exception("Error fetching data")
```

### 3. Database Operations

```python
from app.db import SessionLocal, SymbolPrice

session = SessionLocal()
try:
    prices = session.query(SymbolPrice).filter_by(symbol='KHRO').all()
    session.commit()
finally:
    session.close()
```

### 4. Batch Processing

```python
# Process multiple symbols efficiently
symbols = ['خودرو', 'پترول', 'فمی لیزینگ']

for symbol in symbols:
    try:
        data = PriceHistoryManager.get_price_history(symbol)
        # Process data
    except Exception as e:
        logger.warning(f"Failed to fetch {symbol}: {e}")
        continue
```

## Performance Optimization

### 1. Enable Database Connection Pooling

```python
from config import get_config

config = get_config('production')
# Connection pooling automatically enabled
```

### 2. Use Async Operations

```python
from gravity_tse import PriceHistoryManager

# For async price fetching (async def)
prices = await PriceHistoryManager.get_price_history_async(
    ['خودرو', 'پترول'],
    start_date='1402-01-01'
)
```

### 3. Implement Caching

```python
from functools import lru_cache
from gravity_tse import USDManager

@lru_cache(maxsize=32)
def get_cached_usd_rate():
    return USDManager.get_latest_usd_irr()
```

## Additional Resources

- [API Documentation](./docs/api.md)
- [Database Schema](./docs/database_schema.md)
- [Type Hints Guide](./docs/type_hints_guide.py)
- [Contributing Guide](./CONTRIBUTING.md)

## Support

For issues or questions:

1. Check the [FAQ](./docs/faq.md)
2. Search existing [GitHub Issues](https://github.com/GravtyWaves/Gravity_Tsetmc/issues)
3. Create a new issue with detailed description
