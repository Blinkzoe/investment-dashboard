from app.models.account import Account
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate


def test_account_repository_lists_accounts(db_session) -> None:
    db_session.add_all(
        [
            Account(
                institution="TEST-B",
                name="Cuenta B",
                account_type="BROKERAGE",
                base_currency="MXN",
            ),
            Account(
                institution="TEST-A",
                name="Cuenta A",
                account_type="BROKERAGE",
                base_currency="MXN",
            ),
        ]
    )
    db_session.flush()

    repository = AccountRepository(db_session)
    accounts = repository.list_all()

    test_accounts = [
        account
        for account in accounts
        if account.name in {"Cuenta A", "Cuenta B"}
    ]

    assert [account.id for account in test_accounts] == sorted(
        account.id for account in test_accounts
    )
    assert {account.institution for account in test_accounts} == {
        "TEST-A",
        "TEST-B",
    }

def test_account_repository_get_by_id(db_session) -> None:
    account = Account(
        institution="TEST",
        name="Cuenta Test",
        account_type="BROKERAGE",
        base_currency="MXN",
        external_id="TEST-ACCOUNT-001",
    )
    db_session.add(account)
    db_session.flush()

    repository = AccountRepository(db_session)

    result = repository.get_by_id(account.id)

    assert result is not None
    assert result.id == account.id
    assert result.external_id == "TEST-ACCOUNT-001"


def test_account_repository_create(db_session) -> None:
    repository = AccountRepository(db_session)

    account = repository.create(
        AccountCreate(
            institution="TEST",
            name="Nueva Cuenta",
            account_type="BROKERAGE",
            base_currency="MXN",
            external_id="TEST-ACCOUNT-CREATE-001",
        )
    )

    assert account.id is not None
    assert account.institution == "TEST"
    assert account.name == "Nueva Cuenta"
    assert account.external_id == "TEST-ACCOUNT-CREATE-001"
