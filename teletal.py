#!bin/python
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

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
    # Normalize the input to unaccented form
    normalized_day_name = day_name.lower()
    # Look up the day number in the mapping
    return day_mapping.get(normalized_day_name, None)

def get_day_name(day_number):
    # Iterate over the mapping to find the first matching day number
    for day_name, number in day_mapping.items():
        if number == day_number:
            return day_name
    return None

# Function to scrape the URL and extract information
def scrape_url(ev, het, nap, kod):
    # Construct the URL with the parameters
    url = f"https://www.teletal.hu/ajax/kodinfo?ev={ev}&het={het}&tipus=1&nap={nap}&kod={kod}"

    # Fetch the HTML content
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = response.text
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html5lib')
        
        # Extract valuable information (example: all text inside <div> tags)
        data = []
        for div in soup.find_all(lambda tag: tag.has_attr('uk-grid') and tag.name == 'div'):
            for elem in div.find_all('script'):
                elem.decompose()
            elems = div.find_all()
            subdata = []
            if len(elems) >= 1:
                # print(elems[0].get_text(strip=True), ' ')
                subdata.append(elems[0].get_text(strip=True))
            if len(elems) > 1: 
                # print(elems[1].get_text(strip=True))
                subdata.append(elems[1].get_text(strip=True))
            if len(subdata):
                data.append(subdata)

        print(json.dumps(data))
    else:
        print(f"Failed to fetch the URL. Status code: {response.status_code}")

# Main function to handle command-line arguments
def main():
    # Get the current date for default values
    today = datetime.today()
    default_ev = today.year
    default_het = today.isocalendar()[1]  # ISO week number
    default_nap = get_day_name(today.isoweekday())      # Day of the week, 1=Monday

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Scrape food menu information from a URL.")
    parser.add_argument("--ev", type=int, default=default_ev, help="Year (default: current year)")
    parser.add_argument("--het", type=int, default=default_het, help="Week number (default: current week)")
    parser.add_argument("--nap", type=str, default=default_nap, help="Day of the week (default: current day)")
    parser.add_argument("--kod", type=str, required=True, help="Menu code (required)")

    # Parse the arguments
    args = parser.parse_args()

    # Call the scrape function with the parsed arguments
    scrape_url(args.ev, args.het, get_day_number(args.nap), args.kod)

# Entry point
if __name__ == "__main__":
    main()