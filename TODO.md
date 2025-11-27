<<<<<<< HEAD
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
=======
# Refactoring gravity_tse/__init__.py

## Steps to Complete
- [ ] Read gravity_tse/__init__.py to confirm current structure
- [ ] Identify and remove duplicate GravityTSEManager definition
- [ ] Move symbol-related functions to SymbolManager as @staticmethod
- [ ] Move index-related functions to IndexManager as @staticmethod
- [ ] Move USD-related functions to USDManager as @staticmethod
- [ ] Move general TSE functions to GravityTSEManager as @staticmethod
- [ ] Remove original standalone function definitions
- [ ] Verify the refactored code for syntax and logic preservation
>>>>>>> 5489f53c21f43bc57a9de23edc6ccf15f223d306
