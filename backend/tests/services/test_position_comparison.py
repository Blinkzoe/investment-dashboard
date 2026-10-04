from datetime import datetime
from decimal import Decimal

import pytest

from app.models.account_position import AccountPosition
from app.services.position_comparison import PositionComparisonService


SNAPSHOT_AT = datetime(2026, 10, 3, 21, 0)


def make_position(
    *,
    asset_id: int,
    quantity: str,
    source: str,
) -> AccountPosition:
    return AccountPosition(
        account_id=1,
        asset_id=asset_id,
        snapshot_at=SNAPSHOT_AT,
        quantity=Decimal(quantity),
        market_price=None,
        market_value=None,
        currency="USD",
        source=source,
    )


def test_compare_matching_positions() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="GBM",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
            source="GBM",
        ),
    ]

    reconstructed = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="RECONSTRUCTED",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
            source="RECONSTRUCTED",
        ),
    ]

    result = service.compare(
        official_positions=official,
        reconstructed_positions=reconstructed,
    )

    assert len(result) == 2

    assert result[0].asset_id == 15
    assert result[0].official_quantity == Decimal("0.14")
    assert result[0].reconstructed_quantity == Decimal("0.14")
    assert result[0].difference == Decimal("0")
    assert result[0].status == "MATCH"

    assert result[1].asset_id == 16
    assert result[1].official_quantity == Decimal("9.94")
    assert result[1].reconstructed_quantity == Decimal("9.94")
    assert result[1].difference == Decimal("0")
    assert result[1].status == "MATCH"


def test_compare_detects_quantity_difference() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=16,
            quantity="9.94",
            source="GBM",
        ),
    ]

    reconstructed = [
        make_position(
            asset_id=16,
            quantity="10.00",
            source="RECONSTRUCTED",
        ),
    ]

    result = service.compare(
        official_positions=official,
        reconstructed_positions=reconstructed,
    )

    assert result[0].asset_id == 16
    assert result[0].official_quantity == Decimal("9.94")
    assert result[0].reconstructed_quantity == Decimal("10.00")
    assert result[0].difference == Decimal("0.06")
    assert result[0].status == "DIFFERENCE"


def test_compare_detects_missing_reconstructed_position() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="GBM",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
            source="GBM",
        ),
    ]

    reconstructed = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="RECONSTRUCTED",
        ),
    ]

    result = service.compare(
        official_positions=official,
        reconstructed_positions=reconstructed,
    )

    assert len(result) == 2

    missing = result[1]

    assert missing.asset_id == 16
    assert missing.official_quantity == Decimal("9.94")
    assert missing.reconstructed_quantity is None
    assert missing.difference is None
    assert missing.status == "MISSING_RECONSTRUCTED"


def test_compare_detects_extra_reconstructed_position() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="GBM",
        ),
    ]

    reconstructed = [
        make_position(
            asset_id=15,
            quantity="0.14",
            source="RECONSTRUCTED",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
            source="RECONSTRUCTED",
        ),
    ]

    result = service.compare(
        official_positions=official,
        reconstructed_positions=reconstructed,
    )

    assert len(result) == 2

    extra = result[1]

    assert extra.asset_id == 16
    assert extra.official_quantity is None
    assert extra.reconstructed_quantity == Decimal("9.94")
    assert extra.difference is None
    assert extra.status == "MISSING_OFFICIAL"


def test_compare_rejects_reconstructed_positions_with_wrong_source() -> None:
    service = PositionComparisonService()

    reconstructed = [
        make_position(
            asset_id=16,
            quantity="9.94",
            source="GBM",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Reconstructed positions must use source RECONSTRUCTED",
    ):
        service.compare(
            official_positions=[],
            reconstructed_positions=reconstructed,
        )


def test_compare_rejects_official_reconstructed_source() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=16,
            quantity="9.94",
            source="RECONSTRUCTED",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Official positions cannot use source RECONSTRUCTED",
    ):
        service.compare(
            official_positions=official,
            reconstructed_positions=[],
        )


def test_compare_rejects_duplicate_asset_positions() -> None:
    service = PositionComparisonService()

    official = [
        make_position(
            asset_id=16,
            quantity="9.94",
            source="GBM",
        ),
        make_position(
            asset_id=16,
            quantity="1.00",
            source="GBM",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate position for asset 16",
    ):
        service.compare(
            official_positions=official,
            reconstructed_positions=[],
        )


def test_compare_does_not_use_market_value() -> None:
    service = PositionComparisonService()

    official = [
        AccountPosition(
            account_id=1,
            asset_id=16,
            snapshot_at=SNAPSHOT_AT,
            quantity=Decimal("9.94"),
            market_price=Decimal("61.80"),
            market_value=Decimal("613.88"),
            currency="USD",
            source="GBM",
        ),
    ]

    reconstructed = [
        AccountPosition(
            account_id=1,
            asset_id=16,
            snapshot_at=SNAPSHOT_AT,
            quantity=Decimal("9.94"),
            market_price=None,
            market_value=None,
            currency="USD",
            source="RECONSTRUCTED",
        ),
    ]

    result = service.compare(
        official_positions=official,
        reconstructed_positions=reconstructed,
    )

    assert result[0].status == "MATCH"
    assert result[0].difference == Decimal("0")
