# TODO: Fix Gravity TSETMC Project Issues

## Critical Issues (Priority 1)

- [x] **Create requirements.txt file**
  - Analyze all imports in the project
  - Create comprehensive requirements.txt with all dependencies
  - Include versions for stability

- [x] **Fix duplicate init_db function in app/db.py**
  - Remove the duplicate function at the end of the file
  - Keep only one properly implemented init_db function

- [x] **Create missing app/usd_fetcher.py file**
  - Implement fetch_and_store_usd_irr_prices function
  - Add proper USD/IRR API integration
  - Handle data fetching and storage

- [x] **Create missing app/main.py file**
  - Implement main application logic
  - Add proper entry point for the application

## Major Issues (Priority 2)

- [ ] **Implement real API calls in gravity_tse/__init__.py**
  - Replace placeholder implementations in Get_RI_History
  - Replace placeholder implementations in Get_ShareHoldersInfo
  - Implement actual USD/IRR data fetching in USDManager

- [ ] **Replace test.py with proper test suite**
  - Remove current test.py (JSON manipulation script)
  - Create proper unit tests for core functionality
  - Add integration tests for database operations

- [ ] **Fix hardcoded paths**
  - Make BasicTseInformation/ path configurable
  - Use proper path handling in all files
  - Add configuration management

## Minor Issues (Priority 3)

- [ ] **Improve error handling and logging**
  - Add comprehensive exception handling
  - Implement proper logging throughout the application
  - Add meaningful error messages

- [ ] **Code organization improvements**
  - Reorganize imports in gravity_tse/__init__.py
  - Break down long functions into smaller ones
  - Improve code readability

- [ ] **Add documentation and type hints**
  - Add comprehensive docstrings to all functions
  - Implement type hints throughout the codebase
  - Create API documentation

- [ ] **Clean up project structure**
  - Move unnecessary files from root directory
  - Organize scripts/ directory properly
  - Remove duplicate/unused files

## Testing and Validation (Priority 4)

- [ ] **Test all fixes**
  - Verify requirements.txt works correctly
  - Test database initialization
  - Test data fetching functions
  - Run CLI commands to ensure they work

- [ ] **Performance optimization**
  - Review database queries for efficiency
  - Optimize data processing functions
  - Add proper indexing where needed
