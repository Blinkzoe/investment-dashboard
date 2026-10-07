from pathlib import Path
import re
from decimal import Decimal


SOURCE_FILE = Path("backend/scripts/Markdown(8).md")
OUTPUT_FILE = Path("backend/scripts/fixed_income_preview.csv")


ACCOUNT_NAMES = [
    "Mercado Pago",
    "CETES",
    "NU",
    "Ualá",
    "Stori 1",
    "Klar",
    "Finsus",
    "Didi",
    "Openbank",
    "Revolut",
    "Mifel",
    "Mifel — Jess",
    "Stori 2",
]


MONTHS = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}


def parse_money(value: str) -> Decimal | None:
    value = value.strip()
    if not value or value in {"<br>", "-", "—"}:
        return None

    value = value.replace("$", "").replace(" ", "")

    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1]

    value = value.replace(".", "").replace(",", ".")

    result = Decimal(value)
    return -result if negative else result


def split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def main():
    if not SOURCE_FILE.exists():
        raise SystemExit(
            f"No existe {SOURCE_FILE}. Copia ahí el histórico antes de continuar."
        )

    rows = SOURCE_FILE.read_text(encoding="utf-8").splitlines()

    saldo_rows = []

    for line in rows:
        if not line.lstrip().startswith("|"):
            continue

        parts = split_row(line)

        if len(parts) < 3:
            continue

        month = parts[0].lower()
        kind = parts[1].strip().lower()

        if kind != "saldo":
            continue

        match = re.fullmatch(r"(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)-(\d{2})", month)
        if not match:
            continue

        year = 2000 + int(match.group(2))
        month_number = MONTHS[match.group(1)]

        values = parts[2:]

        # Los productos están representados por pares:
        # saldo / valor de referencia.
        account_values = values[::2]

        if len(account_values) < len(ACCOUNT_NAMES):
            account_values += ["<br>"] * (len(ACCOUNT_NAMES) - len(account_values))

        account_values = account_values[:len(ACCOUNT_NAMES)]

        parsed = [parse_money(v) for v in account_values]

        total = sum((v for v in parsed if v is not None), Decimal("0"))

        saldo_rows.append(
            {
                "date": f"{year:04d}-{month_number:02d}-01",
                "month": f"{year:04d}-{month_number:02d}",
                "values": parsed,
                "total": total,
            }
        )

    saldo_rows.sort(key=lambda row: row["date"])

    if not saldo_rows:
        raise SystemExit("No encontré filas Saldo en el archivo.")

    header = ["month", *ACCOUNT_NAMES, "calculated_total"]

    lines = [",".join(header)]

    for row in saldo_rows:
        fields = [row["month"]]

        for value in row["values"]:
            fields.append("" if value is None else f"{value:.2f}")

        fields.append(f"{row['total']:.2f}")
        lines.append(",".join(fields))

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Meses encontrados: {len(saldo_rows)}")
    print(f"Archivo generado: {OUTPUT_FILE}")
    print()
    print("Últimos 5 meses:")

    for row in saldo_rows[-5:]:
        print(
            f"{row['month']}  "
            f"total={row['total']:,.2f}"
        )


if __name__ == "__main__":
    main()
