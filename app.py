from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
from flask_cors import CORS
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['books_scraper']
collection = db['books']

BASE_URL = "https://books.toscrape.com/"

# Helper function to convert ObjectId to string
def convert_objectid(book_data):
    """Convert MongoDB ObjectId to string."""
    for book in book_data:
        book['_id'] = str(book['_id'])  # Convert ObjectId to string
    return book_data

def save_books_to_mongo(books_data):
    """Save scraped book data to MongoDB."""
    if books_data:
        collection.insert_many(books_data)

def get_category_books(category_url, category_name, page_number=1):
    """Scrape books from a specific category page and assign custom IDs."""
    books_data = []
    modified_url = category_url.replace("index.html","")
    
    while True:
        # Building the page URL
        page_url = f"{modified_url}page-{page_number}.html" if page_number > 1 else category_url

        response = requests.get(page_url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        if not books:
            break

        for idx, book in enumerate(books, start=1):
            title = book.find("h3").find("a").get("title") if book.find("h3") else "No title found"
            price = book.find("p", class_="price_color").text if book.find("p", class_="price_color") else "No price found"
            image_url = book.find("img").get("src") if book.find("img") else "No image found"
            rating_class = book.find("p", class_="star-rating")
            review = rating_class["class"][1] if rating_class else "No review found"
            custom_id = f"{category_name.replace(' ', '_')}-book_{(page_number - 1) * 20 + idx}"

            books_data.append({
                "Category": category_name,
                "Title": title,
                "Price": price,
                "Image URL": image_url,
                "Review": review,
                "ID": custom_id
            })

        next_page = soup.find("li", class_="next")
        if next_page:
            page_number += 1
        else:
            break

    # Save to MongoDB after scraping
    save_books_to_mongo(books_data)

    return books_data



if __name__ == '__main__':
    app.run(debug=True)
