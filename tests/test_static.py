from decimal import Decimal
from pathlib import Path
import ast

def test_financial_decimal_precision(): assert Decimal("10.10") + Decimal("0.90") == Decimal("11.00")
def test_no_runtime_secrets_in_source():
    forbidden=("123456:ABC", "sk_live_", "password=")
    for path in Path(".").rglob("*.py"):
        assert not any(token in path.read_text() for token in forbidden)
def test_source_compiles():
    for path in Path(".").rglob("*.py"): ast.parse(path.read_text())
