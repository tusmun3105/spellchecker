import requests
from bs4 import BeautifulSoup

# Send a GET request to the web page
response = requests.get("https://www.lalitmauritius.org/en/dictionary.html?letter=n")

# Create a BeautifulSoup object by passing the response text and specifying the parser
soup = BeautifulSoup(response.text, "html.parser")

# Find all the span tags with the class "main"
span_tags = soup.find_all("span", class_="main")

# Extract the values from the span tags
values = [tag.text for tag in span_tags]

print(values)

