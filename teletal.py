"""Teletal.hu étlap lekérdező modul.

Ez a modul lehetővé teszi a Teletal.hu oldalról való étlap lekérdezést
adott dátumra és étterem kódra.
"""
import json
from datetime import datetime
import argparse

import requests
from bs4 import BeautifulSoup

day_mapping = {
    "hetfo": 1, "hétfő": 1,
    "kedd": 2,
    "szerda": 3,
    "csutortok": 4, "csütörtök": 4,
    "pentek": 5, "péntek": 5,
    "szombat": 6,
    "vasarnap": 7, "vasárnap": 7
}

def get_day_number(day_name):
    """Visszaadja a hét napjának számát a neve alapján.

    Args:
        day_name (str): A hét napjának neve

    Returns:
        int: A nap sorszáma (1-7)
    """
    normalized_day_name = day_name.lower()
    return day_mapping.get(normalized_day_name, None)

def get_day_name(day_number):
    """Visszaadja a hét napjának nevét a szám alapján.

    Args:
        day_number (int): A nap sorszáma (1-7)

    Returns:
        str: A nap neve
    """
    for day_name, number in day_mapping.items():
        if number == day_number:
            return day_name
    return None

def scrape_url(ev, het, nap, kod):
    """Lekéri és feldolgozza az étlap adatait a Teletal.hu oldalról.

    Args:
        ev (int): Év
        het (int): Hét száma
        nap (int): Nap száma (1-7)
        kod (str): Éttermi kód
    """
    url = f"https://www.teletal.hu/ajax/kodinfo?ev={ev}&het={het}&tipus=1&nap={nap}&kod={kod}"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html5lib')
        menu_data = {}

        for div in soup.find_all(lambda tag: tag.has_attr('uk-grid') and tag.name == 'div'):
            for elem in div.find_all('script'):
                elem.decompose()
            elems = div.find_all()
            if len(elems) >= 1:
                key = elems[0].get_text(strip=True)
                value = elems[1].get_text(strip=True) if len(elems) > 1 else ""

                if key == "":
                    key = "Energia tartalom"
                if key == "Az étkezéshez adott összes étel:":
                    break
                if key == "amelyből":
                    continue
                if key == "cukor":
                    key = "amelyből cukor"
                if key == "Energia tartalom" and value.endswith("KJ"):
                    continue

                menu_data[key] = value

        print(json.dumps(menu_data, indent=2, ensure_ascii=False))
    else:
        print(f"Failed to fetch the URL. Status code: {response.status_code}")

def main():
    """Fő program belépési pont."""
    today = datetime.today()
    default_ev = today.year
    default_het = today.isocalendar()[1]
    default_nap = get_day_name(today.isoweekday())

    parser = argparse.ArgumentParser(
        description="Scrape food menu information from a URL."
    )
    parser.add_argument(
        "--ev",
        type=int,
        default=default_ev,
        help="Year (default: current year)"
    )
    parser.add_argument(
        "--het",
        type=int,
        default=default_het,
        help="Week number (default: current week)"
    )
    parser.add_argument(
        "--nap",
        type=str,
        default=default_nap,
        help="Day of the week (default: current day)"
    )
    parser.add_argument(
        "--kod",
        type=str,
        required=True,
        help="Menu code (required)"
    )

    args = parser.parse_args()
    scrape_url(args.ev, args.het, get_day_number(args.nap), args.kod)

if __name__ == "__main__":
    main()
