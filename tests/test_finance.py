import pytest
from decimal import Decimal

def test_decimal_math(): assert Decimal("10.10") + Decimal("0.90") == Decimal("11.00")
@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_invalid_topup_amount(amount): assert amount <= 0
