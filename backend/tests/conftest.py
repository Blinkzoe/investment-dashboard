import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.account import Account
from app.models.asset import Asset
from app.models.base import Base


def get_test_database_url() -> str:
    url = make_url(settings.database_url)
    return url.set(database="investments_test").render_as_string(
        hide_password=False
    )


@pytest.fixture
def db_session():
    engine = create_engine(get_test_database_url())

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        try:
            account = Account(
                institution="TEST",
                name="TEST GBM Trading MX",
                account_type="TRADING",
                base_currency="MXN",
            )

            asset = Asset(
                symbol="TEST-ASSET",
                name="Test Asset",
                asset_type="STOCK",
                currency="MXN",
                exchange="TEST",
            )

            session.add_all([account, asset])
            session.commit()

            yield session

        finally:
            session.rollback()

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
