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

### Component Testing
The project includes a happy path component test suite (`tests/test_component.py`) that tests the primary workflows (single coin lookup, multi-coin, ratio, news, AI fallback, and AI summary). It integrates all internal modules by manually feeding `Update` objects into the dispatcher, but mocks the external HTTP boundaries with `responses` and `unittest.mock`.
