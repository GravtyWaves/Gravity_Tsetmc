# TODO: Fix Fetcher Field Mappings

## Completed Tasks
- [x] Update imports in app/fetcher.py to include Get_RI_History, Get_ShareHoldersInfo, USDManager, RIData, ShareholdersInfo, UsdIrrPrice
- [x] Implement fetch_and_store_ri_data function
- [x] Implement fetch_and_store_shareholders_info function
- [x] Implement fetch_and_store_usd_irr_prices function
- [x] Fix field mappings in fetch_and_store_symbol_prices for adjusted prices
- [x] Fix field mappings in fetch_and_store_ri_data to match RIData model
- [x] Fix field mappings in fetch_and_store_shareholders_info to match ShareholdersInfo model
- [x] Fix field mappings in fetch_and_store_usd_irr_prices to match UsdIrrPrice model
- [x] Add CLI commands for updating RI data and shareholders info
- [x] Update update-all command to include RI and shareholders updates
- [x] Update CLI examples to include new commands

## Summary
All fetcher functions have been updated to properly map fields to their respective database models. Adjusted prices are now correctly handled in SymbolPrice, and all other functions use the correct field names from the models.
