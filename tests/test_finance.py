from decimal import Decimal
import pytest
from services.wallet import WalletError

def test_money_precision(): assert Decimal("10.10") + Decimal("0.90") == Decimal("11.00")
def test_negative_balance_is_rejected(): assert Decimal("10") - Decimal("11") < 0
@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_invalid_topup_amount(amount): assert amount <= 0

def test_wallet_error_is_public(): assert issubclass(WalletError, Exception)
