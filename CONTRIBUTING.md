# Development Contribution Guidelines

## How to Contribute

Thank you for your interest in contributing to Gravity TSETMC! Follow these guidelines to ensure smooth collaboration.

## Code Standards

### 1. Code Style

We follow **PEP 8** with slight modifications:

- **Line Length**: 120 characters (Black default)
- **Formatter**: Black
- **Import Sorter**: isort with Black profile

### 2. Type Hints

All functions must have type hints:

```python
def fetch_data(symbol: str, timeout: int = 10) -> Optional[pd.DataFrame]:
    """Fetch stock data."""
    pass
```

### 3. Docstrings

Use Google-style docstrings:

```python
def calculate_returns(
    prices: pd.Series,
    periods: int = 1
) -> pd.Series:
    """
    Calculate returns for price series.
    
    Args:
        prices (pd.Series): Price data
        periods (int): Number of periods for return calculation
    
    Returns:
        pd.Series: Calculated returns
    
    Raises:
        ValueError: If prices is empty
    
    Example:
        >>> prices = pd.Series([100, 102, 105])
        >>> returns = calculate_returns(prices)
    """
    pass
```

### 4. Naming Conventions

- **Classes**: CamelCase (e.g., `SymbolManager`)
- **Functions**: snake_case (e.g., `fetch_symbol_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_TIMEOUT`)
- **Private**: Leading underscore (e.g., `_internal_method`)

### 5. Imports

Organize imports using isort:

```python
# Standard library
import json
from typing import Optional

# Third-party
import pandas as pd
import requests

# Local
from app.db import SessionLocal
from utils.logger import setup_logger
```

## Before Submitting

### 1. Format Code

```bash
# Auto-format with Black and isort
black .
isort .
```

### 2. Check Code Quality

```bash
# Run linting
flake8 .

# Type checking
mypy gravity_tse app --ignore-missing-imports

# Security check
bandit -r .
```

### 3. Write Tests

- Add tests for new features
- Ensure test coverage > 80%
- Follow naming: `test_<function_name>`

```python
def test_fetch_symbol_valid():
    """Test fetching valid symbol."""
    result = SymbolManager.get_tse_webid('خودرو')
    assert result is not None
    assert not result.empty

def test_fetch_symbol_invalid():
    """Test fetching invalid symbol."""
    result = SymbolManager.get_tse_webid('INVALID')
    assert result is None or result.empty
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=gravity_tse --cov=app --cov-report=html
```

### 5. Update Documentation

- Add docstrings to new functions
- Update relevant documentation files
- Add examples if applicable

## Git Workflow

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Commit frequently with clear messages
- Keep commits focused and logical

```bash
git add .
git commit -m "feat: add new feature description"
```

### 3. Push and Open PR

```bash
git push origin feature/your-feature-name
```

Open a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots if applicable

### 4. Respond to Reviews

- Address reviewer comments
- Update code as requested
- Resolve conversations

## Commit Message Format

Use conventional commits:

```
feat: add new symbol fetching
fix: resolve timeout issue
docs: update API documentation
test: add tests for price calculator
perf: optimize database queries
style: format code with black
refactor: reorganize import structure
chore: update dependencies
```

Format: `<type>: <description>`

## Pull Request Checklist

Before submitting PR, ensure:

- [ ] Code follows style guidelines
- [ ] Black formatting applied
- [ ] isort import order checked
- [ ] Type hints added
- [ ] Docstrings written
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No lint errors (flake8)
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No unnecessary dependencies added

## Code Review Process

1. **Automated Checks**: GitHub Actions runs tests and quality checks
2. **Review**: Maintainers review code
3. **Improvements**: Address feedback
4. **Approval**: PR approved by reviewers
5. **Merge**: PR merged to develop

## Common Issues

### Type Hint Issues

```python
# ❌ Wrong
def fetch_data(symbol):
    return data

# ✓ Correct
def fetch_data(symbol: str) -> pd.DataFrame:
    return data
```

### Missing Docstring

```python
# ❌ Wrong
def calculate(x, y):
    return x + y

# ✓ Correct
def calculate(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y
```

### Formatting Issues

```bash
# Check and fix
black .
isort .
flake8 .  # Check for remaining issues
```

## Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
@pytest.mark.unit
def test_validate_jalali_date_valid():
    from utils.date_utils import validate_jalali_date
    assert validate_jalali_date('1402-01-01') is True

@pytest.mark.unit
def test_validate_jalali_date_invalid():
    from utils.date_utils import validate_jalali_date
    assert validate_jalali_date('1402-13-01') is False
```

### Integration Tests

Test component interactions:

```python
@pytest.mark.integration
def test_fetch_and_store_prices():
    # Test complete workflow
    pass
```

### Mocking

Use mocks for external APIs:

```python
@patch('gravity_tse.requests.get')
def test_fetch_with_mock(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': []}
    mock_get.return_value = mock_response
    
    result = USDManager.get_latest_usd_irr()
    assert mock_get.called
```

## Documentation

### Docstring Template

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of function.
    
    Longer description if needed. Explain the purpose, behavior,
    and any important details.
    
    Args:
        param1 (Type1): Description of param1
        param2 (Type2): Description of param2
    
    Returns:
        ReturnType: Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    
    Example:
        >>> result = function_name('value1', 'value2')
        >>> print(result)
        expected_output
    """
    pass
```

## Performance Considerations

- Consider API rate limits
- Use batch operations when possible
- Implement caching for frequently accessed data
- Profile code for bottlenecks
- Use async operations for I/O-bound tasks

## Security

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate user input
- Use HTTPS for API calls
- Keep dependencies updated

## Questions?

- Check existing documentation in `docs/`
- Review similar implementations
- Ask in GitHub Discussions
- Open an issue for clarification

## Thank You!

Thank you for contributing to make Gravity TSETMC better! 🙏
