sector_list = ['زراعت','ذغال سنگ','کانی فلزی','سایر معادن','منسوجات','محصولات چرمی','محصولات چوبی','محصولات کاغذی','انتشار و چاپ','فرآورده های نفتی','لاستیک',
               'فلزات اساسی','محصولات فلزی','ماشین آلات','دستگاه های برقی','وسایل ارتباطی','خودرو','قند و شکر','چند رشته ای','تامین آب، برق و گاز','غذایی',
               'دارویی','شیمیایی','خرده فروشی','کاشی و سرامیک','سیمان','کانی غیر فلزی','سرمایه گذاری','بانک','سایر مالی','حمل و نقل',
               'رادیویی','مالی','اداره بازارهای مالی','انبوه سازی','رایانه','اطلاعات و ارتباطات','فنی مهندسی','استخراج نفت','بیمه و بازنشستگی']
sector_web_id = [34408080767216529,19219679288446732,13235969998952202,62691002126902464,59288237226302898,69306841376553334,58440550086834602,30106839080444358,25766336681098389,
 12331083953323969,36469751685735891,32453344048876642,1123534346391630,11451389074113298,33878047680249697,24733701189547084,20213770409093165,21948907150049163,40355846462826897,
 54843635503648458,15508900928481581,3615666621538524,33626672012415176,65986638607018835,57616105980228781,70077233737515808,14651627750314021,34295935482222451,72002976013856737,
 25163959460949732,24187097921483699,41867092385281437,61247168213690670,61985386521682984,4654922806626448,8900726085939949,18780171241610744,47233872677452574,65675836323214668,
 59105676994811497]

def get_sector_webid_map():
    """
    Returns a dictionary mapping sector names to their WebID.
    """
    return dict(zip(sector_list, sector_web_id))

# Main indices (name, web_id)
main_indices = [
    {"name": "شاخص کل", "web_id": 32097828799138957},  # CWI
    {"name": "شاخص کل هم وزن", "web_id": 67130298613737946},  # EWI
]

def get_all_indices():
    """
    Returns a list of dicts: [{"name": ..., "web_id": ...}] for all sector and main indices.
    """
    sector_indices = [
        {"name": name, "web_id": web_id, "type": "sector"}
        for name, web_id in zip(sector_list, sector_web_id)
    ]
    main_indices_with_type = [
        dict(idx, type="main") for idx in main_indices
    ]
    return main_indices_with_type + sector_indices
# imports:
import pandas as pd
import numpy as np
import datetime
import time
import tracemalloc
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()
import aiohttp
import asyncio
from unsync import unsync
import jdatetime
import calendar
import re
from persiantools import characters
from IPython.display import clear_output
from typing import Optional, Dict, List
import logging

# Import utilities
from utils.logger import setup_logger
from utils.exceptions import (
    APIException, SymbolNotFoundException, DataValidationException
)

# Setup logger
logger = setup_logger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

class SymbolManager:
    @staticmethod
    def get_tse_webid(stock: str = 'پترول') -> pd.DataFrame:
        """
        Looks up symbol info using MarketWatch data. Returns DataFrame with WebID and info for all matches.
        Supports Persian and English names.
        """
        # Download MarketWatch data
        try:
            r = requests.get('http://old.tsetmc.com/tsev2/data/MarketWatchPlus.aspx', headers=HEADERS)
            main_text = r.text
            df = pd.DataFrame((main_text.split('@')[2]).split(';'))
            df = df[0].str.split(",", expand=True)
            df = df.iloc[:, :23]
            df.columns = ['WEB-ID','Ticker-Code','Ticker','Name','Time','Open','Final','Close','No','Volume','Value',
                          'Low','High','Y-Final','EPS','Base-Vol','Unknown1','Unknown2','Sector','Day_UL','Day_LL','Share-No','Mkt-ID']
            df['Ticker'] = df['Ticker'].apply(lambda x: characters.ar_to_fa(str(x).strip()))
            df['Name'] = df['Name'].apply(lambda x: characters.ar_to_fa(str(x).strip()))
        except Exception as e:
            print(f'[SymbolManager] MarketWatch fetch error: {e}')
            return None

        # Normalize input
        stock_norm = characters.ar_to_fa(str(stock).strip())
        stock_norm_no_space = ''.join(stock_norm.split())

        # Find matches by Ticker or Name (exact or normalized)
        matches = df[(df['Ticker'] == stock_norm) | (df['Name'] == stock_norm) |
                     (df['Ticker'].str.replace(' ', '') == stock_norm_no_space) |
                     (df['Name'].str.replace(' ', '') == stock_norm_no_space)]

        if matches.empty:
            return None
        # Return DataFrame with WEB-ID, Ticker, Name, Market
        matches = matches[['WEB-ID','Ticker','Name','Sector']]
        matches = matches.rename(columns={'WEB-ID':'WebID', 'Sector':'Market'})
        return matches.reset_index(drop=True)

class PriceHistoryManager:
    @staticmethod
    def get_price_history(stock:str = 'خودرو', 
                          start_date:str = '1400-01-01', 
                          end_date:str = '1401-01-01', 
                          ignore_date:bool = False, 
                          adjust_price:bool = False, 
                          show_weekday:bool = False, 
                          double_date:bool = False) -> pd.DataFrame:
        
      
     
        def get_price_data(ticker_no, ticker, name, market):
            r = requests.get(f'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ticker_no}/0', headers=HEADERS)
            df_history = pd.DataFrame(r.json()['closingPriceDaily'])
            columns=['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No']
            df_history = df_history[['dEven','priceMax','priceMin','pClosing','pDrCotVal','priceFirst','priceYesterday','qTotCap','qTotTran5J','zTotTran']]
            df_history.columns = ['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No']
            df_history['Date'] = df_history['Date'].apply(lambda x: str(x))
            df_history['Date'] = df_history['Date'].apply(lambda x: f'{x[:4]}-{x[4:6]}-{x[-2:]}')
            df_history['Date']=pd.to_datetime(df_history['Date'])
            df_history = df_history[df_history['No']!=0]
            df_history['Ticker'] = ticker
            df_history['Name'] = name
            df_history['Market'] = market
            df_history = df_history.set_index('Date')
            return df_history
        if(not ignore_date):
            start_date = GravityTSEManager.__Check_JDate_Validity__(start_date,key_word="'START'")
            if(start_date==None):
                return
            end_date = GravityTSEManager.__Check_JDate_Validity__(end_date,key_word="'END'")
            if(end_date==None):
                return
            start = jdatetime.date(year=int(start_date.split('-')[0]), month=int(start_date.split('-')[1]), day=int(start_date.split('-')[2]))
            end = jdatetime.date(year=int(end_date.split('-')[0]), month=int(end_date.split('-')[1]), day=int(end_date.split('-')[2]))
            if(start>end):
                print('Start date must be a day before end date!')
                return
        ticker_no_df = SymbolManager.get_tse_webid(stock)
        if(type(ticker_no_df)==bool or ticker_no_df is None):
            # Always return empty DataFrame if not found
            return pd.DataFrame()
        df_history = pd.DataFrame({},columns=['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No','Ticker','Name','Market']).set_index('Date')
        try:
            for index, row in (ticker_no_df.reset_index()).iterrows():
                try:
                    df_temp = get_price_data(ticker_no = row['WebID'],ticker = row['Ticker'],name = row['Name'],market = row['Market'])
                    df_history = pd.concat([df_history,df_temp])
                except Exception as e:
                    pass
            if df_history.empty:
                return pd.DataFrame()
            df_history = df_history.sort_index(ascending=True)
            df_history = df_history.reset_index()
            df_history['Weekday']=df_history['Date'].dt.weekday
            df_history['Weekday'] = df_history['Weekday'].apply(lambda x: calendar.day_name[x])
            df_history['J-Date']=df_history['Date'].apply(lambda x: str(jdatetime.date.fromgregorian(date=x.date())))
            df_history = df_history.set_index('J-Date')
            df_history=df_history[['Date','Weekday','Y-Final','Open','High','Low','Close','Final','Volume','Value','No','Ticker','Name','Market']]
            cols = ['Y-Final','Open','High','Low','Close','Final','Volume','No','Value']
            df_history[cols] = df_history[cols].apply(pd.to_numeric, axis=1)
            df_history['Final(+1)'] = df_history['Final'].shift(+1)          
            df_history['Market(+1)'] = df_history['Market'].shift(+1)        
            df_history['temp'] = df_history.apply(lambda x: x['Y-Final'] if((x['Y-Final']!=0)and(x['Y-Final']!=1000)) 
                                                  else (x['Y-Final'] if((x['Market(+1)']==x['Market'])or(pd.isnull(x['Final(+1)']))) 
                                                  else x['Final(+1)']),axis = 1)
            df_history['Y-Final'] = df_history['temp']
            df_history.drop(columns=['Final(+1)','temp','Market(+1)'],inplace=True)
            for col in cols:
                df_history[col] = df_history[col].apply(lambda x: int(x))
            if(adjust_price):
                df_history['COEF'] = (df_history['Y-Final'].shift(-1)/df_history['Final']).fillna(1.0)
                df_history['ADJ-COEF']=df_history.iloc[::-1]['COEF'].cumprod().iloc[::-1]
                df_history['Adj Open'] = (df_history['Open']*df_history['ADJ-COEF']).apply(lambda x: int(x))
                df_history['Adj High'] = (df_history['High']*df_history['ADJ-COEF']).apply(lambda x: int(x))
                df_history['Adj Low'] = (df_history['Low']*df_history['ADJ-COEF']).apply(lambda x: int(x))
                df_history['Adj Close'] = (df_history['Close']*df_history['ADJ-COEF']).apply(lambda x: int(x))
                df_history['Adj Final'] = (df_history['Final']*df_history['ADJ-COEF']).apply(lambda x: int(x))
                df_history.drop(columns=['COEF','ADJ-COEF'],inplace=True)
            if(not show_weekday):
                df_history.drop(columns=['Weekday'],inplace=True)
            if(not double_date):
                df_history.drop(columns=['Date'],inplace=True)
            df_history.drop(columns=['Y-Final'],inplace=True)
            if(not ignore_date):
                df_history = df_history[start_date:end_date]
            return df_history
        except Exception as e:
            # On any error, return empty DataFrame
            return pd.DataFrame()

    @staticmethod
    async def get_price_history_async(stocks, start_date='1400-01-01', end_date='1401-01-01'):
        """
        دریافت داده قیمت چند نماد به صورت موازی و سریع‌تر با aiohttp
        """
        import pandas as pd
        import jdatetime
        import calendar
        async def fetch_price(session, ticker_no, ticker, name, market):
            url = f'https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ticker_no}/0'
            async with session.get(url, headers=HEADERS) as resp:
                data = await resp.json()
                df_history = pd.DataFrame(data['closingPriceDaily'])
                df_history = df_history[['dEven','priceMax','priceMin','pClosing','pDrCotVal','priceFirst','priceYesterday','qTotCap','qTotTran5J','zTotTran']]
                df_history.columns = ['Date','High','Low','Final','Close','Open','Y-Final','Value','Volume','No']
                df_history['Date'] = df_history['Date'].apply(lambda x: str(x))
                df_history['Date'] = df_history['Date'].apply(lambda x: f'{x[:4]}-{x[4:6]}-{x[-2:]}')
                df_history['Date']=pd.to_datetime(df_history['Date'])
                df_history = df_history[df_history['No']!=0]
                df_history['Ticker'] = ticker
                df_history['Name'] = name
                df_history['Market'] = market
                df_history = df_history.set_index('Date')
                return df_history

        results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stock in stocks:
                ticker_no_df = SymbolManager.get_tse_webid(stock)
                if ticker_no_df is not None:
                    for _, row in ticker_no_df.iterrows():
                        tasks.append(fetch_price(session, row['WebID'], row['Ticker'], row['Name'], row['Market']))
            fetched = await asyncio.gather(*tasks, return_exceptions=True)
            for df in fetched:
                if isinstance(df, pd.DataFrame):
                    results.append(df)
        if results:
            return pd.concat(results)
        return pd.DataFrame()


class USDManager:
    @staticmethod
    def get_usd_irr_prices():
        """
        Fetches historical USD/IRR prices from tgju.org API.
        Returns DataFrame with usd_price and irr_price columns.
        """
        try:
            # Fetch data from tgju.org API
            url = "https://api.tgju.org/v1/market/price-history/dollar_rl"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code != 200:
                print("[USDManager] Error fetching data from tgju.org")
                return pd.DataFrame()

            data = resp.json()
            if not data or 'data' not in data:
                print("[USDManager] No data found in response")
                return pd.DataFrame()

            # Process the data
            records = []
            for item in data['data']:
                try:
                    # Convert timestamp to Jalali date
                    timestamp = item.get('created_at', {}).get('timestamp', 0)
                    if timestamp:
                        gregorian_date = datetime.datetime.fromtimestamp(timestamp)
                        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date.date())
                        date_str = str(jalali_date)
                    else:
                        continue

                    # Extract prices
                    usd_price = item.get('price', 0)
                    if usd_price:
                        records.append({
                            'Date': date_str,
                            'usd_price': float(usd_price),
                            'irr_price': float(usd_price)  # IRR price is same as USD in this context
                        })

                except Exception as e:
                    continue

            if records:
                df = pd.DataFrame(records)
                df = df.sort_values('Date').reset_index(drop=True)
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            print(f"[USDManager] Error fetching USD/IRR prices: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_latest_usd_irr():
        """
        Returns the latest USD/IRR exchange rate from tgju.org API.
        Returns a dict with 'date' and 'price' keys, or None if fetch fails.
        """
        try:
            url = "https://api.tgju.org/v1/market/price-history/dollar_rl"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                logger.warning(f"[USDManager] API returned status code {resp.status_code}")
                return None
            
            data = resp.json()
            if not data or 'data' not in data or len(data['data']) == 0:
                logger.warning("[USDManager] No data found in API response")
                return None
            
            latest_item = data['data'][0]
            timestamp = latest_item.get('created_at', {}).get('timestamp', 0)
            price = latest_item.get('price', 0)
            
            if timestamp and price:
                gregorian_date = datetime.datetime.fromtimestamp(timestamp)
                jalali_date = jdatetime.date.fromgregorian(date=gregorian_date.date())
                logger.info(f"[USDManager] Successfully fetched latest USD/IRR: {price}")
                return {
                    'date': str(jalali_date),
                    'price': float(price)
                }
            logger.warning("[USDManager] Invalid data in API response")
            return None
            
        except requests.exceptions.Timeout:
            logger.error("[USDManager] API request timed out")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[USDManager] Connection error: {e}")
            return None
        except Exception as e:
            logger.exception(f"[USDManager] Unexpected error fetching latest USD/IRR: {e}")
            return None




class Get_RI_History:
    @staticmethod
    def get_ri_history(stock: str) -> pd.DataFrame:
        """
        Fetches Real (Individual) and Institutional trading data for a stock.
        Returns DataFrame with RI data including buy/sell volumes and values.
        """
        try:
            ticker_no_df = SymbolManager.get_tse_webid(stock)
            if ticker_no_df is None or ticker_no_df.empty:
                logger.warning(f"Symbol '{stock}' not found")
                raise SymbolNotFoundException(f"Symbol '{stock}' not found in TSE market")
            
            # Extract WebID from the DataFrame
            web_id = ticker_no_df.iloc[0]['WebID']
            ticker = ticker_no_df.iloc[0]['Ticker']
            
            # Fetch RI history from TSE API
            url = f"https://service.tsetmc.com/tsev2/api/PersonalInvesting/{web_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                logger.error(f"Failed to fetch RI data for {stock} (status: {resp.status_code})")
                raise APIException(f"Failed to fetch RI data for {stock}")
            
            data = resp.json()
            if not data or 'ridata' not in data:
                logger.warning(f"No RI data found for {stock}")
                return pd.DataFrame()
            
            records = []
            for item in data.get('ridata', []):
                try:
                    # Convert date format if needed
                    date_str = item.get('dEven', '')
                    if date_str:
                        records.append({
                            'Date': date_str,
                            'No Buy Real': item.get('nBuyI', 0),
                            'No Sell Real': item.get('nSellI', 0),
                            'Vol Buy Real': item.get('vBuyI', 0),
                            'Vol Sell Real': item.get('vSellI', 0),
                            'Val Buy Real': item.get('qBuyI', 0),
                            'Val Sell Real': item.get('qSellI', 0),
                            'No Buy Inst': item.get('nBuyL', 0),
                            'No Sell Inst': item.get('nSellL', 0),
                            'Vol Buy Inst': item.get('vBuyL', 0),
                            'Vol Sell Inst': item.get('vSellL', 0),
                            'Val Buy Inst': item.get('qBuyL', 0),
                            'Val Sell Inst': item.get('qSellL', 0)
                        })
                except Exception as e:
                    logger.debug(f"Error processing RI data item: {e}")
                    continue
            
            if records:
                df = pd.DataFrame(records)
                logger.info(f"Successfully fetched {len(records)} RI records for {stock}")
                return df
            else:
                logger.warning(f"No valid RI records found for {stock}")
                return pd.DataFrame()
        
        except SymbolNotFoundException as e:
            logger.error(f"Symbol not found: {e}")
            return pd.DataFrame()
        except APIException as e:
            logger.error(f"API error: {e}")
            return pd.DataFrame()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching RI data for {stock}")
            return pd.DataFrame()
        except Exception as e:
            logger.exception(f"Unexpected error fetching RI history for {stock}: {e}")
            return pd.DataFrame()


class Get_ShareHoldersInfo:
    @staticmethod
    def get_shareholders_info(stock: str) -> pd.DataFrame:
        """
        Fetches shareholders information for a stock from TSE API.
        Returns DataFrame with shareholder data including holdings and percentages.
        """
        try:
            ticker_no_df = SymbolManager.get_tse_webid(stock)
            if ticker_no_df is None or ticker_no_df.empty:
                logger.warning(f"Symbol '{stock}' not found")
                raise SymbolNotFoundException(f"Symbol '{stock}' not found in TSE market")
            
            # Extract WebID from the DataFrame
            web_id = ticker_no_df.iloc[0]['WebID']
            ticker = ticker_no_df.iloc[0]['Ticker']
            
            # Fetch shareholders info from TSE API
            url = f"https://service.tsetmc.com/tsev2/api/ShareHolder/{web_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                logger.error(f"Failed to fetch shareholder data for {stock} (status: {resp.status_code})")
                raise APIException(f"Failed to fetch shareholder data for {stock}")
            
            data = resp.json()
            if not data or 'shareholder' not in data:
                logger.warning(f"No shareholder data found for {stock}")
                return pd.DataFrame()
            
            records = []
            for item in data.get('shareholder', []):
                try:
                    records.append({
                        'Date': item.get('dEven', ''),
                        'Holder Name': item.get('lName', ''),
                        'Shares': item.get('cEPS', 0),
                        'Shares Percent': item.get('per', 0),
                        'Holder Type': item.get('sGoal', ''),
                        'National ID': item.get('cIsin', ''),
                        'Change Percent': item.get('perChange', 0)
                    })
                except Exception as e:
                    logger.debug(f"Error processing shareholder data item: {e}")
                    continue
            
            if records:
                df = pd.DataFrame(records)
                logger.info(f"Successfully fetched {len(records)} shareholder records for {stock}")
                return df
            else:
                logger.warning(f"No valid shareholder records found for {stock}")
                return pd.DataFrame()
        
        except SymbolNotFoundException as e:
            logger.error(f"Symbol not found: {e}")
            return pd.DataFrame()
        except APIException as e:
            logger.error(f"API error: {e}")
            return pd.DataFrame()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching shareholder data for {stock}")
            return pd.DataFrame()
        except Exception as e:
            logger.exception(f"Unexpected error fetching shareholder info for {stock}: {e}")
            return pd.DataFrame()


class GravityTSEManager:
    @staticmethod
    def __Check_JDate_Validity__(date_str, key_word="'DATE'"):
        """
        Validates and returns a Jalali date string in YYYY-MM-DD format.
        """
        try:
            parts = date_str.split('-')
            if len(parts) != 3:
                raise ValueError
            year, month, day = map(int, parts)
            # Validate Jalali date
            jdatetime.date(year, month, day)
            return date_str
        except Exception:
            print(f'Invalid {key_word} date format: {date_str}. Expected YYYY-MM-DD.')
            return None
