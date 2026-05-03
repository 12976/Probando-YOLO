#!/usr/bin/env python3
"""Extract expiration dates from PDF certificates and save them to an Excel file."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import pdfplumber

DATE_PATTERNS = [
    re.compile(r"\b(?:expir(?:a|e)(?:tion)?\s*date|valid\s*until|expires?\s*on)\s*[:\-]?\s*([0-3]?\d[\/\-][0-1]?\d[\/\-](?:\d{2}|\d{4}))", re.IGNORECASE),
    re.compile(r"\b([0-1]?\d[\/\-][0-3]?\d[\/\-](?:\d{2}|\d{4}))\b"),
    re.compile(r"\b([0-3]?\d\s+[A-Za-z]{3,9}\s+\d{4})\b"),
    re.compile(r"\b([A-Za-z]{3,9}\s+[0-3]?\d,\s*\d{4})\b"),
]

DATE_FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%m-%d-%Y",
    "%m-%d-%y",
    "%d %B %Y",
    "%d %b %Y",
    "%B %d, %Y",
    "%b %d, %Y",
]


def extract_text_from_pdf(pdf_path: Path) -> str:
    chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)
    return "\n".join(chunks)


def parse_date(date_text: str) -> Optional[datetime]:
    candidate = re.sub(r"\s+", " ", date_text.strip())
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    return None


def find_expiration_date(text: str) -> tuple[Optional[str], Optional[str]]:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            raw = match.group(1)
            parsed = parse_date(raw)
            if parsed:
                return raw, parsed.strftime("%Y-%m-%d")
    return None, None


def process_certificates(input_dir: Path) -> pd.DataFrame:
    records: list[dict[str, Optional[str]]] = []
    for pdf_path in sorted(input_dir.glob("*.pdf")):
        text = extract_text_from_pdf(pdf_path)
        raw_date, iso_date = find_expiration_date(text)
        status = "found" if iso_date else "not found"
        records.append(
            {
                "file_name": pdf_path.name,
                "raw_expiration_date": raw_date,
                "expiration_date": iso_date,
                "status": status,
            }
        )
    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read PDF certificates, extract expiration dates, and export to Excel."
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing PDF certificate files.",
    )
    parser.add_argument(
        "output_xlsx",
        type=Path,
        help="Path of the resulting Excel file (.xlsx).",
    )
    args = parser.parse_args()

    if not args.input_dir.exists() or not args.input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist or is not a directory: {args.input_dir}")

    df = process_certificates(args.input_dir)
    args.output_xlsx.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(args.output_xlsx, index=False)

    print(f"Processed {len(df)} PDF file(s).")
    print(f"Excel file saved to: {args.output_xlsx}")


if __name__ == "__main__":
    main()
