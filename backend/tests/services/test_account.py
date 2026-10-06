from app.models.account import Account
from app.schemas.account import AccountCreate
from app.services.account import AccountService


def test_account_service_lists_accounts(db_session) -> None:
    db_session.add(
        Account(
            institution="TEST",
            name="Cuenta Test",
            account_type="BROKERAGE",
            base_currency="MXN",
        )
    )
    db_session.flush()

    service = AccountService(db_session)
    accounts = service.list_all()

    test_accounts = [
        account
        for account in accounts
        if account.name == "Cuenta Test"
    ]

    assert len(test_accounts) == 1
    assert test_accounts[0].institution == "TEST"

def test_account_service_get_by_id(db_session) -> None:
    account = Account(
        institution="TEST",
        name="Cuenta Test",
        account_type="BROKERAGE",
        base_currency="MXN",
    )
    db_session.add(account)
    db_session.flush()

    service = AccountService(db_session)

    result = service.get_by_id(account.id)

    assert result is not None
    assert result.id == account.id


def test_account_service_create(db_session) -> None:
    service = AccountService(db_session)

    account = service.create(
        AccountCreate(
            institution="TEST",
            name="Nueva Cuenta",
            account_type="BROKERAGE",
            base_currency="MXN",
            external_id="TEST-SERVICE-001",
        )
    )

    assert account.id is not None
    assert account.name == "Nueva Cuenta"
    assert account.base_currency == "MXN"
