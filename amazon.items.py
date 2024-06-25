import requests
from bs4 import BeautifulSoup

# Function to scrape Amazon search results
def scrape_amazon_search_results(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    products = soup.find_all('div', {'data-asin': True, 'data-component-type': 's-search-result'})
    
    # Check if any products were found
    if not products:
        print("No products found on the page.")
        return []
    
    all_products = []
    
    for index, product in enumerate(products):
        product_details = {}
        
        # Extract product title
        title_section = product.find('h2', class_='a-size-mini a-spacing-none a-color-base s-line-clamp-4')
        if title_section:
            product_details['Title'] = title_section.get_text(strip=True)
        
        # Extract product rating
        rating_section = product.find('span', class_='a-icon-alt')
        if rating_section:
            product_details['Rating'] = rating_section.get_text(strip=True)
        
        # Extract number of reviews
        reviews_section = product.find('span', class_='a-size-base s-underline-text')
        if reviews_section:
            product_details['Number of Reviews'] = reviews_section.get_text(strip=True)
        
        # Extract product price
        price_whole_section = product.find('span', class_='a-price-whole')
        price_fraction_section = product.find('span', class_='a-price-fraction')
        price_symbol_section = product.find('span', class_='a-price-symbol')
        if price_whole_section and price_fraction_section and price_symbol_section:
            product_details['Price'] = price_symbol_section.get_text(strip=True) + price_whole_section.get_text(strip=True) + ',' + price_fraction_section.get_text(strip=True)
        
        # Extract delivery date
        delivery_section = product.find('span', {'aria-label': True})
        if delivery_section:
            product_details['Delivery Date'] = delivery_section.get_text(strip=True)
        
        # Extract shipping information
        shipping_section = product.find('div', class_='a-row a-size-base a-color-secondary s-align-children-center')
        if shipping_section:
            shipping_info = shipping_section.find_all('span')
            product_details['Shipping Info'] = ' '.join([info.get_text(strip=True) for info in shipping_info])
        
        # Extract product URL
        product_link = product.find('a', class_='a-link-normal s-no-outline')
        if product_link:
            product_details['URL'] = 'https://www.amazon.nl' + product_link['href']
        
        # Add to the list of all products if at least one detail is found
        if product_details:
            all_products.append(product_details)
    
    return all_products

# Function to extract detailed product information from a product page
def get_amazon_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize a dictionary to store product details
    product_details = {}
    
    try:
        # Extract product title
        title = soup.find(id='productTitle')
        product_details['Title'] = title.get_text().strip() if title else 'N/A'
        
        # Extract product price
        price_symbol = soup.find('span', {'class': 'a-price-symbol'})
        price_whole = soup.find('span', {'class': 'a-price-whole'})
        price_fraction = soup.find('span', {'class': 'a-price-fraction'})
        if price_symbol and price_whole and price_fraction:
            product_details['Price'] = price_symbol.get_text(strip=True) + price_whole.get_text(strip=True) + ',' + price_fraction.get_text(strip=True)
        else:
            product_details['Price'] = 'N/A'
        
        # Extract product rating
        rating = soup.find('span', {'class': 'a-icon-alt'})
        product_details['Rating'] = rating.get_text().strip() if rating else 'N/A'
        
        # Extract number of reviews
        review_count = soup.find('span', {'id': 'acrCustomerReviewText'})
        product_details['Review Count'] = review_count.get_text().strip() if review_count else 'N/A'

        # Extract detailed specifications from the product overview table
        overview_table = soup.find('div', {'id': 'poExpander'})
        if overview_table:
            rows = overview_table.find_all('tr')
            for row in rows:
                key = row.find('td', {'class': 'a-span3'}).get_text(strip=True)
                value = row.find('td', {'class': 'a-span9'}).get_text(strip=True)
                product_details[key] = value
        
        # Extract additional specifications from another product details table
        additional_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
        if additional_table:
            rows = additional_table.find_all('tr')
            for row in rows:
                key = row.find('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'}).get_text(strip=True)
                value = row.find('td', {'class': 'a-size-base prodDetAttrValue'}).get_text(strip=True).replace('\u200e', '')
                product_details[key] = value

    except AttributeError as e:
        print(f"Error parsing product details: {e}")
        return None
    
    return product_details

if __name__ == "__main__":
    # Example usage
    url = "https://www.amazon.nl/s?k=pc&__mk_nl_NL=%C3%85M%C3%85%C5%BD%C3%95%C3%91"
    search_results = scrape_amazon_search_results(url)
    
    for index, product in enumerate(search_results):
        print(f"Product {index+1}: {product}")
    
    # Prompt user for the product number
    product_number = input("Please enter the product number you are interested in: ")
    
    # Extract the number from the input
    try:
        product_index = int(product_number.strip()) - 1
        if 0 <= product_index < len(search_results):
            product_url = search_results[product_index]['URL']
            
            # Get product details
            details = get_amazon_product_details(product_url)
            
            # Print product details
            if details:
                print(details)
            else:
                print("Failed to retrieve product details.")
        else:
            print("Invalid product number.")
    
    except (IndexError, ValueError):
        print("Invalid product number.")
