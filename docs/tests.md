# Testing

## Frameworks
- `pytest`
- `pytest-asyncio`
- `responses` (for mocking HTTP requests)

## Execution
Run the test suite using:
```bash
uv run pytest
```
Ensure new features are covered by tests in the `tests/` directory. Use `responses` to mock any external API calls (e.g., to CoinMarketCap).
