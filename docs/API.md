# API Documentation - Gravity TSETMC

## Core Managers

### SymbolManager

Manager for stock symbol lookup and information retrieval.

#### Methods

##### `get_tse_webid(stock: str) -> pd.DataFrame`

Lookup symbol information using MarketWatch data.

**Parameters:**
- `stock` (str): Stock name or ticker in Persian (e.g., 'خودرو')

**Returns:**
- `pd.DataFrame`: Multi-index DataFrame containing:
  - `WebID`: Unique identifier for the symbol
  - `Ticker`: 4-character ticker code
  - `Name`: Full company name
  - `Name(EN)`: English company name
  - `Market`: Market type (1st, 2nd, or OTC)
  - `Panel`: Market panel

**Example:**
```python
from gravity_tse import SymbolManager
df = SymbolManager.get_tse_webid('خودرو')
print(df)
```

---

### PriceHistoryManager

Manager for historical price data retrieval.

#### Methods

##### `get_price_history(stock: str, start_date: str, end_date: str, adjust_price: bool, ignore_date: bool) -> pd.DataFrame`

Fetch historical price data for a stock.

**Parameters:**
- `stock` (str): Stock name in Persian
- `start_date` (str): Start date in YYYY-MM-DD format (Jalali)
- `end_date` (str): End date in YYYY-MM-DD format (Jalali)
- `adjust_price` (bool): Whether to adjust for splits/dividends (default: False)
- `ignore_date` (bool): Whether to ignore date validation (default: False)

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `Date`: Trading date
  - `Open`: Opening price
  - `High`: Highest price
  - `Low`: Lowest price
  - `Close`: Closing price
  - `Volume`: Trading volume
  - `Value`: Trading value
  - `Weekday`: Day of week

**Example:**
```python
from gravity_tse import PriceHistoryManager
df = PriceHistoryManager.get_price_history(
    'خودرو',
    start_date='1402-01-01',
    end_date='1402-12-29'
)
```

##### `get_price_history_async(stocks: List[str], start_date: str, end_date: str) -> List[pd.DataFrame]`

Async version for fetching multiple stocks concurrently.

**Parameters:**
- `stocks` (List[str]): List of stock names
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:**
- `List[pd.DataFrame]`: List of DataFrames, one per stock

---

### USDManager

Manager for USD/IRR exchange rate data.

#### Methods

##### `get_usd_irr_prices() -> pd.DataFrame`

Fetch historical USD/IRR prices.

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `Date`: Date in Jalali format
  - `usd_price`: USD/IRR exchange rate
  - `irr_price`: Same as usd_price in this context

**Example:**
```python
from gravity_tse import USDManager
df = USDManager.get_usd_irr_prices()
```

##### `get_latest_usd_irr() -> Optional[Dict[str, Union[str, float]]]`

Get the latest USD/IRR exchange rate.

**Returns:**
- `Dict` with keys:
  - `date`: Date in Jalali format (YYYY-MM-DD)
  - `price`: Exchange rate (IRR per USD)
- `None` if fetch fails

**Example:**
```python
from gravity_tse import USDManager
rate = USDManager.get_latest_usd_irr()
if rate:
    print(f"1 USD = {rate['price']} IRR on {rate['date']}")
```

---

### Get_RI_History

Manager for Real (Individual) and Institutional trading data.

#### Methods

##### `get_ri_history(stock: str) -> pd.DataFrame`

Fetch Real/Institutional trading data.

**Parameters:**
- `stock` (str): Stock name in Persian

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `Date`: Trading date
  - `No Buy Real`: Number of individual buy orders
  - `No Sell Real`: Number of individual sell orders
  - `Vol Buy Real`: Volume of individual buy orders
  - `Vol Sell Real`: Volume of individual sell orders
  - `Val Buy Real`: Value of individual buy orders
  - `Val Sell Real`: Value of individual sell orders
  - `No Buy Inst`: Number of institutional buy orders
  - `No Sell Inst`: Number of institutional sell orders
  - `Vol Buy Inst`: Volume of institutional buy orders
  - `Vol Sell Inst`: Volume of institutional sell orders
  - `Val Buy Inst`: Value of institutional buy orders
  - `Val Sell Inst`: Value of institutional sell orders

**Example:**
```python
from gravity_tse import Get_RI_History
df = Get_RI_History.get_ri_history('خودرو')
# Analyze institutional activity
inst_buys = df['No Buy Inst'].sum()
```

---

### Get_ShareHoldersInfo

Manager for shareholder information.

#### Methods

##### `get_shareholders_info(stock: str) -> pd.DataFrame`

Fetch shareholder data.

**Parameters:**
- `stock` (str): Stock name in Persian

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `Date`: Date of information
  - `Holder Name`: Name of shareholder
  - `Shares`: Number of shares held
  - `Shares Percent`: Ownership percentage
  - `Holder Type`: Type (Individual/Institution/Government)
  - `National ID`: National/Company ID
  - `Change Percent`: Change from previous period

**Example:**
```python
from gravity_tse import Get_ShareHoldersInfo
df = Get_ShareHoldersInfo.get_shareholders_info('خودرو')
# Get major shareholders
major = df[df['Shares Percent'] > 5].sort_values('Shares Percent', ascending=False)
```

---

## Utility Functions

### Date Utilities

#### `validate_jalali_date(date_str: str) -> bool`

Validate if string is valid Jalali date.

```python
from utils.date_utils import validate_jalali_date
is_valid = validate_jalali_date('1402-01-01')  # True
is_valid = validate_jalali_date('1402-13-01')  # False (invalid month)
```

#### `jalali_to_gregorian(jalali_str: str) -> Optional[datetime.date]`

Convert Jalali date to Gregorian.

```python
from utils.date_utils import jalali_to_gregorian
gregorian = jalali_to_gregorian('1402-01-01')
print(gregorian)  # 2023-03-21
```

#### `gregorian_to_jalali(gregorian_date: datetime.date) -> str`

Convert Gregorian date to Jalali.

```python
from utils.date_utils import gregorian_to_jalali
import datetime
jalali = gregorian_to_jalali(datetime.date(2023, 3, 21))
print(jalali)  # 1402-01-01
```

---

### Logging

#### `setup_logger(name: str, log_dir: str = 'logs', level=logging.INFO) -> logging.Logger`

Setup logger with file and console handlers.

```python
from utils.logger import setup_logger
logger = setup_logger(__name__)
logger.info("Application started")
logger.error("An error occurred")
```

---

## Database Models

### SymbolPrice

Stores daily price data for symbols.

**Fields:**
- `id`: Primary key
- `symbol`: Stock ticker
- `date`: Trading date (Jalali)
- `gregorian_date`: Trading date (Gregorian)
- `open`: Opening price
- `high`: High price
- `low`: Low price
- `close`: Closing price
- `volume`: Trading volume
- `value`: Trading value
- `count`: Number of trades
- `adj_close`: Adjusted close price

### RIData

Stores Real/Institutional trading data.

**Fields:**
- `id`: Primary key
- `symbol`: Stock ticker
- `date`: Trading date
- `no_buy_real`: Individual buy order count
- `no_sell_real`: Individual sell order count
- `vol_buy_real`: Individual buy volume
- `vol_sell_real`: Individual sell volume
- And similar for institutional data

### ShareholdersInfo

Stores shareholder information.

**Fields:**
- `id`: Primary key
- `symbol`: Stock ticker
- `date`: Information date
- `holder_name`: Shareholder name
- `shares`: Share count
- `percent`: Ownership percentage
- `holder_type`: Individual/Institution/Government

---

## Configuration

### Config Objects

```python
from config import get_config

# Get environment-specific config
config = get_config('development')  # or 'production', 'testing'

# Access settings
print(config.DATABASE_URL)
print(config.API_TIMEOUT)
print(config.LOG_LEVEL)
```

---

## Error Handling

### Custom Exceptions

```python
from utils.exceptions import (
    SymbolNotFoundException,
    APIException,
    DataValidationException,
    DatabaseException
)

try:
    prices = SymbolManager.get_tse_webid('invalid_symbol')
except SymbolNotFoundException as e:
    print(f"Symbol error: {e}")
except APIException as e:
    print(f"API error: {e}")
```

---

## Complete Example

```python
import pandas as pd
from gravity_tse import (
    SymbolManager, 
    PriceHistoryManager, 
    Get_RI_History,
    USDManager
)
from utils.logger import setup_logger
from utils.exceptions import SymbolNotFoundException

logger = setup_logger(__name__)

def analyze_stock(symbol: str):
    """Complete stock analysis example"""
    try:
        # Get symbol info
        logger.info(f"Analyzing {symbol}...")
        symbol_info = SymbolManager.get_tse_webid(symbol)
        
        # Get prices
        prices = PriceHistoryManager.get_price_history(
            symbol,
            start_date='1402-01-01',
            end_date='1402-12-29'
        )
        
        # Get RI data
        ri_data = Get_RI_History.get_ri_history(symbol)
        
        # Get USD rate for analysis
        usd_rate = USDManager.get_latest_usd_irr()
        
        logger.info(f"Successfully fetched data for {symbol}")
        return {
            'symbol_info': symbol_info,
            'prices': prices,
            'ri_data': ri_data,
            'usd_rate': usd_rate
        }
        
    except SymbolNotFoundException as e:
        logger.error(f"Symbol not found: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return None

# Usage
result = analyze_stock('خودرو')
if result:
    print(f"Price records: {len(result['prices'])}")
    print(f"RI records: {len(result['ri_data'])}")
```

For more examples, see `docs/GETTING_STARTED.md`
