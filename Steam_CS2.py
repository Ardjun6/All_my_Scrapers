import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from datetime import datetime

def scrape_steam_market(page):
    if page == 1:
        url = 'https://steamcommunity.com/market/search?appid=730'
    else:
        url = f'https://steamcommunity.com/market/search?appid=730#p{page}_popular_desc'
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = soup.find('div', id='searchResultsRows')
    top_items = []
    for item in results.find_all('a', class_='market_listing_row_link'):
        name = item.find('span', class_='market_listing_item_name').text
        price = item.find('span', class_='normal_price').text.strip()
        link = item['href']
        image = item.find('img')['src']
        top_items.append({
            'name': name,
            'price': price,
            'link': link,
            'image': image
        })
    return top_items

def download_excel(data, directory, timestamp):
    df = pd.DataFrame(data)
    df.columns = ['Name', 'Price', 'Link', 'Image URL']
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Top Items')

        workbook = writer.book
        worksheet = writer.sheets['Top Items']

        worksheet.set_column('A:A', 30)  # Name column
        worksheet.set_column('B:B', 20)  # Price column
        worksheet.set_column('C:C', 50)  # Link column
        worksheet.set_column('D:D', 50)  # Image URL column

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
        
        row_formats = [
            workbook.add_format({'bg_color': '#FFFFFF'}),
            workbook.add_format({'bg_color': '#F3F3F3'})
        ]
        
        for row_num, row_data in enumerate(df.values, 1):
            row_format = row_formats[row_num % 2]
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data, row_format)

        price_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C5700'
        })
        worksheet.conditional_format('B2:B{}'.format(len(df) + 1), {'type': 'text', 'criteria': 'containing', 'value': 'USD', 'format': price_format})

    output.seek(0)
    with open(os.path.join(directory, f'steam_market_top_items_{timestamp}.xlsx'), 'wb') as f:
        f.write(output.read())
    print("Excel file has been saved successfully.")

def download_csv(data, directory, timestamp):
    df = pd.DataFrame(data)
    df.columns = ['Name', 'Price', 'Link', 'Image URL']
    csv_file_path = os.path.join(directory, f'steam_market_top_items_{timestamp}.csv')
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    print("CSV file has been saved successfully.")

def save_file(output, filename):
    # Create the directory if it doesn't exist
    directory = "Steam_Market_Data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, filename)
    with open(file_path, 'wb') as f:
        f.write(output.read())
    print(f"File saved to {file_path}")

if __name__ == '__main__':
    page = 1  # Example page number, you can change it as needed
    top_items = scrape_steam_market(page)

    if top_items:
        # Create the directory if it doesn't exist
        directory = "Steam_Market_Data"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Ask the user whether to save as Excel, CSV, or both
        choice = input("Do you want to save the data as Excel, CSV, or both? Enter 'excel', 'csv', or 'both': ").strip().lower()

        if choice == 'excel':
            # Save to Excel
            download_excel(top_items, directory, timestamp)
        elif choice == 'csv':
            # Save to CSV
            download_csv(top_items, directory, timestamp)
        elif choice == 'both':
            # Save to both
            csv_output = download_csv(top_items, directory, timestamp)
            excel_output = download_excel(top_items, directory, timestamp)
        else:
            print("Invalid choice. Please run the script again and enter 'excel', 'csv', or 'both'.")
    else:
        print("No data to save.")
