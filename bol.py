import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
from datetime import datetime
from io import BytesIO

def scrape_bol():
    url = 'https://www.bol.com/nl/nl/s/?searchtext=laptops'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        listings_data = []

        while True:
            listings = soup.find_all('li', class_='product-item--row')

            for listing in listings:
                title_element = listing.find('a', class_='product-title')
                price_element = listing.find('span', class_='promo-price')
                url_element = title_element['href'] if title_element else 'N/A'

                title = title_element.get_text(strip=True) if title_element else 'N/A'
                price = price_element.get_text(strip=True) if price_element else 'N/A'
                if price != 'N/A':
                    price = f"€{price.replace(',', '').replace('-', '')}.-"
                url = f"https://www.bol.com{url_element}" if url_element != 'N/A' else 'N/A'

                listings_data.append({
                    'title': title,
                    'price': price,
                    'url': url
                })

            next_page = soup.find('a', class_='pagination__next')
            if next_page:
                next_url = next_page['href']
                response = requests.get(next_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    time.sleep(2)  # Delay to avoid overloading the server
                else:
                    break
            else:
                break
        return listings_data
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

def download_excel(data, directory, timestamp):
    df = pd.DataFrame(data)
    df.columns = ['Title', 'Price', 'URL']
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Listings')

        workbook = writer.book
        worksheet = writer.sheets['Listings']

        worksheet.set_column('A:A', 30)  # Title column
        worksheet.set_column('B:B', 20)  # Price column
        worksheet.set_column('C:C', 50)  # URL column

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1,
            'align': 'center'
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    output.seek(0)
    with open(os.path.join(directory, f'bol_com_listings_{timestamp}.xlsx'), 'wb') as f:
        f.write(output.read())
    print("Excel file has been saved successfully.")

def download_csv(data, directory, timestamp):
    df = pd.DataFrame(data)
    df.columns = ['Title', 'Price', 'URL']
    csv_file_path = os.path.join(directory, f'bol_com_listings_{timestamp}.csv')
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    print("CSV file has been saved successfully.")

if __name__ == '__main__':
    listings_data = scrape_bol()

    if listings_data:
        # Create the directory if it doesn't exist
        directory = "Bol_Data"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Ask the user whether to save as Excel, CSV, or both
        choice = input("Do you want to save the data as Excel, CSV, or both? Enter 'excel', 'csv', or 'both': ").strip().lower()

        if choice == 'excel':
            download_excel(listings_data, directory, timestamp)
        elif choice == 'csv':
            download_csv(listings_data, directory, timestamp)
        elif choice == 'both':
            download_excel(listings_data, directory, timestamp)
            download_csv(listings_data, directory, timestamp)
        else:
            print("Invalid choice. Please run the script again and enter 'excel', 'csv', or 'both'.")
    else:
        print("No data to save.")
