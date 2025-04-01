import requests
from bs4 import BeautifulSoup
import unicodedata
import json
import time

BASE_URL = "https://en.wikibooks.org"
START_URL = "https://en.wikibooks.org/wiki/Category:Recipes_with_images"

def clean_text(text):
    text = unicodedata.normalize("NFKC", text).replace("⁄", "/").strip()
    return text

def get_infobox_value(soup, label_text):
    table = soup.find("table", class_="infobox")
    if not table:
        return None
    for row in table.find_all("tr"):
        label = row.find("th", class_="infobox-label")
        data = row.find("td", class_="infobox-data")
        if label and data and label.get_text(strip=True).lower() == label_text.lower():
            text = data.get_text(strip=True)
            if text:
                return text
            tag = data.find(["img", "a"])
            if tag:
                return tag.get("title") or tag.get("alt")
    return None

def scrape_recipe_if_complete(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    title = soup.find("h1").text.replace("Cookbook:", "").strip()
    servings = get_infobox_value(soup, "Servings")
    time_text = get_infobox_value(soup, "Time")
    category = get_infobox_value(soup, "Category")
    difficulty = get_infobox_value(soup, "Difficulty")

    if servings:
        servings = servings.replace("\u2013", "-").strip()

    image_tag = soup.select_one(".infobox img")
    if image_tag and image_tag.get("src"):
        src = image_tag["src"]
        if src.startswith("//"):
            image_url = "https:" + src
        elif src.startswith("/"):
            image_url = BASE_URL + src
        else:
            image_url = src
    else:
        image_url = None

    ingredients, instructions = [], []
    for section_div in soup.select("div.mw-heading"):
        heading_tag = section_div.find(["h2", "h3"])
        if not heading_tag:
            continue
        heading = heading_tag.get_text().lower().strip()
        next_node = section_div.find_next_sibling()

        if "ingredient" in heading:
            while next_node and next_node.name not in ["div", "h2", "h3"]:
                if next_node.name in ["ul", "ol"]:
                    ingredients += [clean_text(li.get_text()) for li in next_node.find_all("li")]
                next_node = next_node.find_next_sibling()

        if any(word in heading for word in ["procedure", "instruction", "direction", "preparation", "method"]):
            while next_node and next_node.name not in ["div", "h2", "h3"]:
                if next_node.name == "p":
                    instructions.append(clean_text(next_node.get_text()))
                elif next_node.name in ["ul", "ol"]:
                    instructions += [clean_text(li.get_text()) for li in next_node.find_all("li")]
                next_node = next_node.find_next_sibling()

    if not (ingredients and instructions and time_text and servings and image_url and difficulty):
        return None

    return {
        "title": title,
        "image": image_url,
        "cook_time": time_text,
        "prep_time": None,
        "difficulty": difficulty,
        "creator_id": None,
        "servings": servings,
        "cuisine": category,
        "description": None,
        "tags": category.lower().replace(" recipes", "") if category else None,
        "ingredients": ingredients,
        "instructions": instructions,
        "rating": None,
        "fts": None,
        "url": url
    }

def get_paginated_links(start_url, max_pages=5):
    recipe_links = []
    next_page = start_url
    page_count = 0

    while next_page and page_count < max_pages:
        res = requests.get(next_page)
        soup = BeautifulSoup(res.content, "html.parser")

        for link in soup.select(".mw-category-group ul li a"):
            href = link.get("href")
            if href and href.startswith("/wiki/Cookbook:"):
                full_url = BASE_URL + href
                if full_url not in recipe_links:
                    recipe_links.append(full_url)

        next_link = soup.find("a", string="next page")
        next_page = BASE_URL + next_link.get("href") if next_link else None
        page_count += 1
        time.sleep(0.5)

    return recipe_links

if __name__ == "__main__":
    all_recipes = []
    links = get_paginated_links(START_URL, max_pages=5)

    for url in links:
        try:
            recipe = scrape_recipe_if_complete(url)
            if recipe:
                all_recipes.append(recipe)
            time.sleep(0.3)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    with open("data/recipes_with_images.json", "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(all_recipes)} complete recipes and saved to recipes_with_images.json")