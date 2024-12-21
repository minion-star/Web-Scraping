from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
@app.route('/scrape', methods=['GET'])
def scrape_books():
    # specify the target URL (page 1 of the travel books category)
    target_url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"

    # send a GET request to the target URL
    response = requests.get(target_url)

    # check if the response status code is 200 (OK)
    if response.status_code != 200:
        return jsonify({"error": f"An error occurred with status {response.status_code}"}), 500

    # get the page HTML content
    html_content = response.text

    # parse HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the category from the breadcrumb (navigate to <nav> and find the last <li>)
    category = soup.find("ul", class_="breadcrumb").find_all("li")[-1].text.strip()

    # Find all the book elements (use the appropriate tags)
    books = soup.find_all("article", class_="product_pod")

    data = []
    for book in books:
        # Extract the book title (from the <a> tag within the <h3> tag)
        title = book.find("h3").find("a").get("title") if book.find("h3") else "No title found"
        
        # Extract the book price (from the <p> tag with the class 'price_color')
        price = book.find("p", class_="price_color").text if book.find("p", class_="price_color") else "No price found"
        
        # Extract the book image URL (from the <img> tag with the class 'thumbnail')
        image_url = book.find("img").get("src") if book.find("img") else "No image found"
        
        # Extract the book ID (from the book link URL)
        book_url = book.find("h3").find("a").get("href") if book.find("h3").find("a") else ""
        
        if book_url:
            # Extract book ID from the URL (e.g., index_1.html, index_2.html)
            match = re.search(r"index_(\d+).html", book_url)
            book_id = match.group(1) if match else "No ID found"
        else:
            book_id = "No ID found"
        
        # Store all information in a dictionary
        data.append({
            "Category": category,
            "ID": book_id,
            "Title": title,
            "Price": price,
            "Image URL": image_url
        })

    # Return the data as a JSON response
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
