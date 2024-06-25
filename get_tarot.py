import requests
from bs4 import BeautifulSoup

# Define the base URL and suits
base_url = "https://commons.wikimedia.org/wiki/File:"
suits = ["Cups", "Wands", "Pents", "Swords"]

# Function to construct URL and check for image
def get_image_url(suit, number):
    url = f"{base_url}{suit}{number:02d}.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Find the image URL in the page
        image_tag = soup.find("a", {"class": "internal"})
        if image_tag:
            return "https:" + image_tag['href']
    return None

# Loop through each suit and number to get the image URLs
image_urls = []
for suit in suits:
    for number in range(1, 15):  # Tarot cards go from 01 to 14
        image_url = get_image_url(suit, number)
        if image_url:
            image_urls.append(image_url)

# Print the image URLs
for url in image_urls:
    print(url)