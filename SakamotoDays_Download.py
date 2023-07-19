import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, filedialog

def download_image(img_url, session):
    """Download an image and return its content"""
    if (img_url.startswith("https://cdn.hxmanga.com/file/") and
        ("Sakamoto" in img_url or "Days" in img_url) and
        "shirt.png" not in img_url):
        img_data = session.get(img_url).content
        return img_data

# Create a Tkinter root window (it will not be shown)
root = Tk()
root.withdraw()

# Open a file chooser dialog to select the path
sd_folder = Path(filedialog.askdirectory(title="Select the path where you want to create the 'Sakamoto Days' folder"))

# Create a folder named "Sakamoto Days" if it doesn't exist
sd_folder = sd_folder / "Sakamoto Days"
sd_folder.mkdir(exist_ok=True)

# Set the URL of the main page
main_url = "https://sakamotodaymanga.com"

# Create a session object to reuse the underlying TCP connection
session = requests.Session()

# Get the HTML content of the main page
main_page = session.get(main_url)
main_soup = BeautifulSoup(main_page.content, "html.parser")

# Find all links to chapters that have "sakamoto-days-chapter" or "sakamotos-days-chapter" in them
chapter_links = main_soup.find_all("a", href=lambda href: href and ("sakamoto-days-chapter" in href or "sakamotos-days-chapter" in href))

# Iterate over the chapter links
for link in chapter_links:
    # Get the chapter number from the link
    if "sakamoto-days-chapter-" in link["href"]:
        chapter_number = link["href"].split("sakamoto-days-chapter-")[1].split("-")[0]
    else:
        chapter_number = link["href"].split("sakamotos-days-chapter-")[1].split("-")[0]

    # Check if a folder for the chapter already exists
    chapter_folder = sd_folder / chapter_number
    if chapter_folder.exists():
        # Skip this chapter and move on to the next one
        continue

    # Create a folder for the chapter
    chapter_folder.mkdir()

    # Get the HTML content of the chapter page
    chapter_page = session.get(link['href'])
    chapter_soup = BeautifulSoup(chapter_page.content, "html.parser")
    
    # Find all image tags on the chapter page
    images = chapter_soup.find_all("img")
    
    # Create a ThreadPoolExecutor to download images concurrently
    with ThreadPoolExecutor() as executor:
        # Submit tasks to download images and store the future objects in a list
        futures = [executor.submit(download_image, img["src"], session) for img in images]
        
        # Iterate over the completed tasks
        for i, future in enumerate(as_completed(futures), start=1):
            # Get the downloaded image data from the future object
            img_data = future.result()
            
            # Save the image to the chapter folder if it was downloaded successfully
            if img_data is not None:
                with open(chapter_folder / f"{i}.jpg", "wb") as f:
                    f.write(img_data)
