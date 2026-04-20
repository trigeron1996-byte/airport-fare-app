import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


WORKDIR = Path(__file__).resolve().parent
DEFAULT_FARE_PDF = Path(
    "C:/Users/konoike/konoike Dropbox/貴志大地/ダウンロード（クラウド）/①料金表（帰省手当航空機利用者向け）.pdf"
)
DEFAULT_OUTPUT = WORKDIR / "app-data.js"

NAME_ALIASES = {
    "沖縄": "沖縄(那覇)",
    "中標津": "根室中標津",
    "福江": "五島福江",
    "萩・石見": "萩石見",
}

LOCATION_AIRPORT_OPTIONS = {
    "東京": ["羽田空港", "成田空港"],
    "札幌": ["新千歳空港"],
    "旭川": ["旭川空港"],
    "函館": ["函館空港"],
    "仙台": ["仙台空港"],
    "静岡": ["静岡空港"],
    "名古屋": ["中部空港"],
    "大阪": ["伊丹空港", "関西空港（第1ターミナル）", "神戸空港"],
    "南紀白浜": ["南紀白浜空港"],
    "広島": ["広島空港"],
    "福岡": ["福岡空港"],
    "北九州": ["北九州空港"],
    "熊本": ["熊本空港"],
    "沖縄(那覇)": ["那覇空港"],
}

PRIORITY_LOCATIONS = [
    "東京",
    "大阪",
    "名古屋",
    "札幌",
    "仙台",
    "福岡",
    "北九州",
    "長崎",
    "五島福江",
    "対馬",
    "壱岐",
    "熊本",
    "天草",
    "大分",
    "宮崎",
    "鹿児島",
    "種子島",
    "屋久島",
    "奄美大島",
    "喜界島",
    "徳之島",
    "沖永良部",
    "与論",
    "沖縄(那覇)",
    "宮古",
    "石垣",
    "久米島",
    "与那国",
    "北大東",
    "南大東",
    "多良間",
    "広島",
    "旭川",
    "函館",
    "静岡",
    "南紀白浜",
]

AIRPORT_FEES = {
    "新千歳空港": {
        "adult": 370,
        "adultLabel": "370円",
        "childLabel": "180円",
    },
    "旭川空港": {
        "adult": 360,
        "adultLabel": "360円",
        "childLabel": "180円",
    },
    "函館空港": {
        "adult": 430,
        "adultLabel": "430円",
        "childLabel": "210円",
    },
    "仙台空港": {
        "adult": 290,
        "adultLabel": "290円",
        "childLabel": "150円",
    },
    "羽田空港": {
        "adult": 370,
        "adultLabel": "370円（条件により450円）",
        "childLabel": "180円（条件により220円）",
    },
    "成田空港": {
        "adult": 450,
        "adultLabel": "450円",
        "childLabel": "220円",
    },
    "静岡空港": {
        "adult": 140,
        "adultLabel": "140円",
        "childLabel": "70円",
    },
    "中部空港": {
        "adult": 440,
        "adultLabel": "440円",
        "childLabel": "220円",
    },
    "伊丹空港": {
        "adult": 340,
        "adultLabel": "340円",
        "childLabel": "170円",
    },
    "関西空港（第1ターミナル）": {
        "adult": 440,
        "adultLabel": "440円（条件により560円）",
        "childLabel": "220円（条件により280円）",
    },
    "神戸空港": {
        "adult": 300,
        "adultLabel": "300円",
        "childLabel": "150円",
    },
    "南紀白浜空港": {
        "adult": 260,
        "adultLabel": "260円",
        "childLabel": "130円",
    },
    "広島空港": {
        "adult": 340,
        "adultLabel": "340円",
        "childLabel": "170円",
    },
    "福岡空港": {
        "adult": 110,
        "adultLabel": "110円",
        "childLabel": "50円",
    },
    "北九州空港": {
        "adult": 100,
        "adultLabel": "100円",
        "childLabel": "50円",
    },
    "熊本空港": {
        "adult": 200,
        "adultLabel": "200円（条件により320円）",
        "childLabel": "100円（条件により160円）",
    },
    "那覇空港": {
        "adult": 240,
        "adultLabel": "240円",
        "childLabel": "120円",
    },
}

NUM_RE = re.compile(r"^\d{1,3}(?:,\d{3})+$")


def normalize_name(name: str) -> str:
    value = name.strip().replace(" ", "")
    return NAME_ALIASES.get(value, value)


def route_key(a: str, b: str) -> str:
    points = sorted([normalize_name(a), normalize_name(b)])
    return "::".join(points)


def parse_jal_page(text: str) -> list[dict]:
    records = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(token in line for token in ["料金表", "適用期間", "経由地", "路線"]):
            continue
        parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
        if not any("=" in part for part in parts):
            continue

        index = 0
        while index < len(parts):
            if "=" not in parts[index]:
                index += 1
                continue

            route = parts[index]
            index += 1
            vias = []
            while index < len(parts) and not NUM_RE.match(parts[index]):
                if "=" in parts[index]:
                    break
                vias.append(normalize_name(parts[index]))
                index += 1

            if index >= len(parts) or not NUM_RE.match(parts[index]):
                continue

            fare = int(parts[index].replace(",", ""))
            index += 1
            departure, arrival = [normalize_name(x) for x in route.split("=")]
            records.append(
                {
                    "from": departure,
                    "to": arrival,
                    "fare": fare,
                    "via": vias,
                }
            )
    return records


def parse_ana_page(text: str) -> list[dict]:
    records = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(token in line for token in ["料金表", "適用期間", "路線"]):
            continue
        parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
        index = 0
        while index + 1 < len(parts):
            route = parts[index]
            fare = parts[index + 1]
            index += 2
            if "=" not in route or not NUM_RE.match(fare):
                continue
            departure, arrival = [normalize_name(x) for x in route.split("=")]
            records.append(
                {
                    "from": departure,
                    "to": arrival,
                    "fare": int(fare.replace(",", "")),
                    "via": [],
                }
            )
    return records


def load_fares(fare_pdf: Path) -> dict:
    reader = PdfReader(str(fare_pdf))

    jal_records = []
    for page_index in range(5):
        text = reader.pages[page_index].extract_text(extraction_mode="layout") or ""
        jal_records.extend(parse_jal_page(text))

    ana_records = []
    for page_index in [5, 6]:
        text = reader.pages[page_index].extract_text(extraction_mode="layout") or ""
        ana_records.extend(parse_ana_page(text))

    grouped = {"JAL": {}, "ANA": {}}
    locations = set()

    for airline, records in [("JAL", jal_records), ("ANA", ana_records)]:
        for record in records:
            key = route_key(record["from"], record["to"])
            current = grouped[airline].get(key)
            if current is None or record["fare"] < current["fare"]:
                grouped[airline][key] = record
            locations.add(record["from"])
            locations.add(record["to"])

    ordered_locations = sorted(
        locations,
        key=lambda name: (
            PRIORITY_LOCATIONS.index(name)
            if name in PRIORITY_LOCATIONS
            else len(PRIORITY_LOCATIONS),
            name,
        ),
    )

    return {
        "locations": ordered_locations,
        "airlines": grouped,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ANA/JALの料金表PDFからHTML用データを生成します。"
    )
    parser.add_argument(
        "--fare-pdf",
        type=Path,
        default=DEFAULT_FARE_PDF,
        help="運賃表PDFのパス",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="生成するapp-data.jsの出力先",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fare_pdf = args.fare_pdf.resolve()
    output = args.output.resolve()

    if not fare_pdf.exists():
        raise FileNotFoundError(f"運賃表PDFが見つかりません: {fare_pdf}")

    data = load_fares(fare_pdf)
    payload = {
        "meta": {
            "fareSource": str(fare_pdf),
            "feeSource": "②旅客施設使用料.pdf",
            "note": "運賃はANA/JALのPDFから最安値を抽出。空港使用料は大人料金の基本額を合計に使用し、条件付き増額はラベルで表示。",
        },
        "locations": data["locations"],
        "airlines": data["airlines"],
        "locationAirportOptions": LOCATION_AIRPORT_OPTIONS,
        "airportFees": AIRPORT_FEES,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "window.AIRPORT_APP_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
