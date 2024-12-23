from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

BASE_URL = "https://books.toscrape.com/"

def get_category_books(category_url, category_name, page_number):
    """Scrape books from a specific category page and assign custom IDs."""
    books_data = []
    modified_url = category_url.replace("index.html", "")
    
    # Build the correct URL for the current page
    if page_number == 1:
        page_url = category_url  # First page uses the base URL (no page number)
    else:
        page_url = f"{modified_url}page-{page_number}.html"  # Subsequent pages use page-{page_number}.html

    print(f"Scraping {page_url}")  # Debugging output
    response = requests.get(page_url)

    # Check if the request is successful
    if response.status_code != 200:
        print(f"Failed to retrieve {page_url}. Status code: {response.status_code}")  # Debugging output
        return books_data  # Return empty list if request failed

    # Parse the page content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all book elements on the current page
    books = soup.find_all("article", class_="product_pod")

    # If no books are found, exit the loop
    if not books:
        print("No books found on this page.")  # Debugging output
        return books_data

    # Scrape data for each book on the current page
    for idx, book in enumerate(books, start=1):  # Start numbering from 1 for each category
        title = book.find("h3").find("a").get("title") if book.find("h3") else "No title found"
        price = book.find("p", class_="price_color").text if book.find("p", class_="price_color") else "No price found"
        image_url = book.find("img").get("src") if book.find("img") else "No image found"
        
        # Extract the rating or review class (e.g., "star-rating Three" for a 3-star book)
        rating_class = book.find("p", class_="star-rating")
        review = rating_class["class"][1] if rating_class else "No review found"  # Gets the rating class like "Three", "Four", etc.

        # Create a custom ID by combining the category name and the index
        custom_id = f"{category_name.replace(' ', '_')}-book_{(page_number - 1) * 20 + idx}"

        books_data.append({
            "Category": category_name,
            "Title": title,
            "Price": price,
            "Image URL": image_url,
            "Review": review,
            "ID": custom_id
        })

    return books_data

@app.route('/scrape', methods=['GET'])
def scrape_books():
    # Get the page number from the request, default to 1 if not provided
    page_number = int(request.args.get('page', 1))
    
    # Scrape the main page to get the category URLs
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        return jsonify({"error": f"An error occurred with status {response.status_code}"}), 500

    # Parse the main page content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the category links on the main page
    categories = soup.find_all("a", href=re.compile(r"^catalogue/category/books/"))
    categories_data = []

    for category in categories:
        category_name = category.text.strip()
        category_url = BASE_URL + category["href"].replace("../../", "")
        category_books = get_category_books(category_url, category_name, page_number)
        categories_data.append({
            "Category": category_name,
            "Books": category_books
        })

    # Return the scraped data as JSON response
    return jsonify(categories_data)

if __name__ == '__main__':
    app.run(debug=True)
