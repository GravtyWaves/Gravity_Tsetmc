# Code Quality and Formatting Tools

This project uses several tools to maintain high code quality standards.

## Setup

### Install Development Tools

```bash
pip install -r requirements-dev.txt
```

### Install Pre-commit Hooks

Pre-commit hooks automatically check code quality before commits:

```bash
pip install pre-commit
pre-commit install
```

## Tools and Usage

### 1. Black - Code Formatting

Automatic Python code formatter.

```bash
# Format all Python files
black .

# Check formatting without changes
black --check .

# Format specific file
black app/db.py
```

### 2. isort - Import Sorting

Sorts and organizes imports automatically.

```bash
# Sort imports in all files
isort .

# Check without making changes
isort --check-only .

# Sort specific file
isort gravity_tse/__init__.py
```

### 3. Flake8 - Linting

Checks for PEP 8 compliance and common errors.

```bash
# Check all files
flake8 .

# Check specific directory
flake8 gravity_tse/

# Generate report
flake8 . --format=json > flake8-report.json
```

### 4. Pylint - Code Analysis

Advanced code analysis for errors and improvements.

```bash
# Analyze all files
pylint gravity_tse app

# Analyze specific file
pylint gravity_tse/__init__.py

# Generate report
pylint gravity_tse --output-format=json > pylint-report.json
```

### 5. mypy - Type Checking

Static type checker for Python.

```bash
# Check all files
mypy gravity_tse app --ignore-missing-imports

# Check specific file
mypy gravity_tse/__init__.py

# Generate report
mypy gravity_tse --html report/
```

### 6. bandit - Security Check

Scans for common security issues.

```bash
# Security check
bandit -r .

# Generate report
bandit -r . -f json -o bandit-report.json
```

### 7. safety - Dependency Check

Checks for known security vulnerabilities in dependencies.

```bash
# Check dependencies
safety check

# Generate report
safety check --json
```

## Running All Checks

### Quick Format and Lint

```bash
# Format code
black .
isort .

# Check quality
flake8 .
pylint gravity_tse app
```

### Full Quality Check

```bash
# Run all quality checks
bash scripts/quality_check.sh
```

### Before Committing

```bash
# Pre-commit hook runs automatically, or manually:
pre-commit run --all-files
```

## IDE Integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=120"],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=120"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Go to Settings → Editor → Code Style
2. Set Line length to 120
3. Enable "Optimize imports" on save
4. Install and enable Black formatter
5. Configure as Python Formatter

## Configuration Files

### `.flake8`

Flake8 configuration - defines rules and exceptions.

### `setup.cfg`

Central configuration for multiple tools:
- flake8 settings
- isort profile and settings
- mypy type checking options

### `.pre-commit-config.yaml`

Pre-commit hooks that run before each commit.

### `pyproject.toml` (optional)

Modern Python project configuration (can be added for tool coordination).

## Continuous Integration

These tools run automatically in CI/CD pipelines:

- **GitHub Actions**: `.github/workflows/tests.yml`
- **GitLab CI**: `.gitlab-ci.yml`

Both check code quality and run tests automatically on push and pull requests.

## Best Practices

### 1. Format Before Committing

```bash
black .
isort .
git add .
git commit -m "Feature: add new functionality"
```

### 2. Fix Issues Early

```bash
flake8 .  # Identify issues
black .   # Auto-fix formatting
# Manually fix remaining issues
```

### 3. Check Types During Development

```python
# Add type hints as you code
def fetch_data(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch data with type hints"""
    pass
```

### 4. Use IDE Features

- Enable auto-format on save
- Use IDE's built-in linting
- Fix issues as they appear

## Troubleshooting

### Issue: "Line too long" errors

**Solution:**
- Use black to format: `black .`
- Or refactor code to be more concise
- Update `max-line-length` in settings if 120 is too strict

### Issue: Import ordering conflicts

**Solution:**
```bash
# Run isort to fix automatically
isort .

# Or configure isort profile in setup.cfg
```

### Issue: Type checking too strict

**Solution:**
- Use `# type: ignore` for specific lines
- Gradually add type hints
- Adjust mypy settings in `setup.cfg`

### Issue: Pre-commit hook failing

**Solution:**
```bash
# Skip hooks temporarily
git commit --no-verify

# Or fix issues and retry
pre-commit run --all-files
git add .
git commit -m "Fix code quality issues"
```

## Recommended Workflow

1. **Write code** with IDE support
2. **Before commit**: Run `black . && isort .`
3. **Let pre-commit run**: Automatic checks
4. **Fix any errors**: Address flake8/pylint issues
5. **Commit**: Once all checks pass
6. **CI/CD**: Automated checks on push
7. **Code review**: Check quality in PR

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## Summary

| Tool | Purpose | Usage |
|------|---------|-------|
| Black | Code formatting | `black .` |
| isort | Import sorting | `isort .` |
| Flake8 | Linting | `flake8 .` |
| Pylint | Code analysis | `pylint gravity_tse` |
| mypy | Type checking | `mypy gravity_tse` |
| Bandit | Security check | `bandit -r .` |
| Safety | Dependency check | `safety check` |
