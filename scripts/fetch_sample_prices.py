#!/usr/bin/env python
# Small runner to fetch prices for first N symbols and store them
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, SymbolList
from app.fetcher import fetch_and_store_symbol_prices

N = 5
session = SessionLocal()
symbols = session.query(SymbolList).limit(N).all()
if not symbols:
    print('No symbols found in DB. Run cli.py init to populate symbol_list.')
    session.close()
    exit(1)

pairs = [(s.symbol_fa, s.symbol_en) for s in symbols]
session.close()
print(f'Fetching prices for {len(pairs)} sample symbols: {[p[1] for p in pairs]}')

# Test with known working symbols first
working_symbols = [('خودرو', 'KHODRO'), ('فملی', 'FMLI'), ('شپنا', 'SHAPNA')]
fetch_and_store_symbol_prices(working_symbols, adjust=False)
print('Done.')
