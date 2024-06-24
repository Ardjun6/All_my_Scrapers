import requests
from bs4 import BeautifulSoup

# Function to extract product details
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
        product_details['title'] = title.get_text().strip() if title else 'N/A'
        
        # Extract product price
        price_span = soup.find('span', {'class': 'a-price a-text-price a-size-medium apexPriceToPay'})
        if price_span:
            price = price_span.find('span', {'class': 'a-offscreen'})
            product_details['price'] = price.get_text().strip() if price else 'N/A'
        else:
            product_details['price'] = 'N/A'
        
        # Extract product rating
        rating = soup.find('span', {'class': 'a-icon-alt'})
        product_details['rating'] = rating.get_text().strip() if rating else 'N/A'
        
        # Extract number of reviews
        review_count = soup.find('span', {'id': 'acrCustomerReviewText'})
        product_details['review_count'] = review_count.get_text().strip() if review_count else 'N/A'
        
    except AttributeError as e:
        print(f"Error parsing product details: {e}")
        return None
    
    return product_details

if __name__ == "__main__":
    # Prompt user for the Amazon product URL
    product_url = input("Please enter the Amazon product URL: ")

    # Get product details
    details = get_amazon_product_details(product_url)

    # Print product details
    if details:
        print(details)
    else:
        print("Failed to retrieve product details.")
