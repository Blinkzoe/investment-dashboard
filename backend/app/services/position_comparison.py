from dataclasses import dataclass
from decimal import Decimal

from app.models.account_position import AccountPosition


@dataclass(frozen=True)
class PositionComparison:
    asset_id: int
    official_quantity: Decimal | None
    reconstructed_quantity: Decimal | None
    difference: Decimal | None
    status: str


class PositionComparisonService:
    RECONSTRUCTED_SOURCE = "RECONSTRUCTED"

    def compare(
        self,
        *,
        official_positions: list[AccountPosition],
        reconstructed_positions: list[AccountPosition],
    ) -> list[PositionComparison]:
        self._validate_sources(
            official_positions=official_positions,
            reconstructed_positions=reconstructed_positions,
        )

        official_by_asset = self._index_positions(official_positions)
        reconstructed_by_asset = self._index_positions(
            reconstructed_positions
        )

        asset_ids = sorted(
            set(official_by_asset) | set(reconstructed_by_asset)
        )

        comparisons: list[PositionComparison] = []

        for asset_id in asset_ids:
            official = official_by_asset.get(asset_id)
            reconstructed = reconstructed_by_asset.get(asset_id)

            if official is None:
                comparisons.append(
                    PositionComparison(
                        asset_id=asset_id,
                        official_quantity=None,
                        reconstructed_quantity=reconstructed.quantity,
                        difference=None,
                        status="MISSING_OFFICIAL",
                    )
                )
                continue

            if reconstructed is None:
                comparisons.append(
                    PositionComparison(
                        asset_id=asset_id,
                        official_quantity=official.quantity,
                        reconstructed_quantity=None,
                        difference=None,
                        status="MISSING_RECONSTRUCTED",
                    )
                )
                continue

            difference = (
                reconstructed.quantity - official.quantity
            )

            comparisons.append(
                PositionComparison(
                    asset_id=asset_id,
                    official_quantity=official.quantity,
                    reconstructed_quantity=reconstructed.quantity,
                    difference=difference,
                    status=(
                        "MATCH"
                        if difference == Decimal("0")
                        else "DIFFERENCE"
                    ),
                )
            )

        return comparisons

    def _validate_sources(
        self,
        *,
        official_positions: list[AccountPosition],
        reconstructed_positions: list[AccountPosition],
    ) -> None:
        reconstructed_sources = {
            position.source for position in reconstructed_positions
        }

        if reconstructed_sources - {self.RECONSTRUCTED_SOURCE}:
            raise ValueError(
                "Reconstructed positions must use source "
                f"{self.RECONSTRUCTED_SOURCE}"
            )

        if any(
            position.source == self.RECONSTRUCTED_SOURCE
            for position in official_positions
        ):
            raise ValueError(
                "Official positions cannot use source "
                f"{self.RECONSTRUCTED_SOURCE}"
            )

    def _index_positions(
        self,
        positions: list[AccountPosition],
    ) -> dict[int, AccountPosition]:
        indexed: dict[int, AccountPosition] = {}

        for position in positions:
            if position.asset_id in indexed:
                raise ValueError(
                    f"Duplicate position for asset {position.asset_id}"
                )

            indexed[position.asset_id] = position

        return indexed
