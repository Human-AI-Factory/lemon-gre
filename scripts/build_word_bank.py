#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_XLSX = ROOT / "words_bank_raw" / "GRE_3000_Vocabularies" / "3000.xlsx"
OUTPUT_JS = ROOT / "data" / "gre3000-bank.js"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"a": MAIN_NS}


def load_shared_strings(archive: ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    shared = []
    for item in root.findall("a:si", NS):
        shared.append("".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")))
    return shared


def cell_column(reference: str) -> str:
    return "".join(char for char in reference if char.isalpha())


def normalize_phonetic(value: str) -> str:
    return value.strip().strip("[]/ ")


def parse_words() -> list[list[str]]:
    if not SOURCE_XLSX.exists():
        raise SystemExit(f"source xlsx not found: {SOURCE_XLSX}")

    with ZipFile(SOURCE_XLSX) as archive:
        shared_strings = load_shared_strings(archive)
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = sheet.find("a:sheetData", NS)
        if rows is None:
            return []

        items: list[list[str]] = []
        for row in rows.findall("a:row", NS)[1:]:
            values: dict[str, str] = {}
            for cell in row.findall("a:c", NS):
                value_node = cell.find("a:v", NS)
                if value_node is None:
                    continue

                value = value_node.text or ""
                if cell.attrib.get("t") == "s":
                    value = shared_strings[int(value)]

                values[cell_column(cell.attrib.get("r", ""))] = value

            word = values.get("I", "").strip()
            meaning = values.get("L", "").strip()
            phonetic = normalize_phonetic(values.get("J", ""))

            if word and meaning:
                items.append([word, meaning, phonetic])

        return items


def build_payload() -> list[dict[str, object]]:
    items = parse_words()
    return [
        {
            "id": "gre-3000-vocabularies",
            "name": "GRE 3000",
            "total": len(items),
            "sourceNote": "再要你命 3000",
            "sourcePath": str(SOURCE_XLSX.relative_to(ROOT)),
            "items": items,
        }
    ]


def main() -> None:
    payload = build_payload()
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JS.write_text(
        "window.GRE_WORD_BANKS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"generated {OUTPUT_JS.relative_to(ROOT)} with {payload[0]['total']} items")


if __name__ == "__main__":
    main()
