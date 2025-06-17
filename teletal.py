#!bin/python
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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

        print(data)
    else:
        print(f"Failed to fetch the URL. Status code: {response.status_code}")

# Main function to handle command-line arguments
def main():
    # Get the current date for default values
    today = datetime.today()
    default_ev = today.year
    default_het = today.isocalendar()[1]  # ISO week number
    default_nap = today.isoweekday()      # Day of the week (1=Monday, 7=Sunday)

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Scrape food menu information from a URL.")
    parser.add_argument("--ev", type=int, default=default_ev, help="Year (default: current year)")
    parser.add_argument("--het", type=int, default=default_het, help="Week number (default: current week)")
    parser.add_argument("--nap", type=int, default=default_nap, help="Day of the week (default: current day)")
    parser.add_argument("--kod", type=str, required=True, help="Menu code (required)")

    # Parse the arguments
    args = parser.parse_args()

    # Call the scrape function with the parsed arguments
    scrape_url(args.ev, args.het, args.nap, args.kod)

# Entry point
if __name__ == "__main__":
    main()