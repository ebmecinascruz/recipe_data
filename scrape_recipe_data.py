import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List, Tuple
import json
from pprint import pprint

def clean_recipe_name(name: str) -> str:
    """Clean recipe name to create URL-friendly string."""
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    return name

def parse_fraction(quantity_span) -> str:
    """Parse fraction from HTML span element."""
    if not quantity_span:
        return ""
        
    # Handle fractions (e.g., 1/2)
    sup = quantity_span.find('sup')
    sub = quantity_span.find('sub')
    if sup and sub:
        return f"{sup.text}/{sub.text}"
    
    # Handle ranges (e.g., 1-2)
    text = quantity_span.text.strip()
    if '-' in text:
        return text.replace(' ', '')
    
    return text

def parse_recipe_facts(facts_div) -> Tuple[str, str]:
    """Parse cook time and servings from facts div."""
    if not facts_div:
        return None, None
        
    cook_time = None
    servings = None
    
    # Find the dl element that contains the facts items
    dl = facts_div.find('dl', class_='svelte-1r658j4')
    if not dl:
        return None, None
        
    for item in dl.find_all('div', class_='facts__item svelte-1r658j4'):
        label = item.find('dt', class_='facts__label svelte-1r658j4')
        if not label:
            continue
            
        if 'Ready In:' in label.text:
            value = item.find('dd', class_='facts__value svelte-1r658j4')
            if value:
                cook_time = value.text.strip()
        elif 'Serves:' in label.text:
            value = item.find('dd', class_='facts__value svelte-1r658j4')
            if value:
                # Find the span with class 'value' inside the adjust div
                value_span = value.find('span', class_='value svelte-1o10zxc')
                if value_span:
                    servings = value_span.text.strip()
    
    return cook_time, servings

def parse_ingredient(ingredient_text: str) -> Dict:
    """Parse ingredient text into name, unit, and amount."""
    # Split the text into parts
    parts = ingredient_text.strip().split()
    
    # Initialize variables
    amount = None
    unit = None
    name = None
    
    # Try to find amount (can be fraction or number)
    if parts and (parts[0].isdigit() or '/' in parts[0] or '-' in parts[0]):
        amount = parts[0]
        parts = parts[1:]
    
    # Try to find unit
    if parts and parts[0] in ['cup', 'cups', 'teaspoon', 'teaspoons', 'tablespoon', 'tablespoons', 
                             'ounce', 'ounces', 'pound', 'pounds', 'gram', 'grams', 'kilogram', 'kilograms',
                             'milliliter', 'milliliters', 'liter', 'liters', 'pinch', 'dash']:
        unit = parts[0]
        parts = parts[1:]
    
    # The rest is the ingredient name
    name = ' '.join(parts)
    
    return {
        'name': name,
        'unit': unit,
        'amount': amount
    }

def scrape_recipe_data(recipe_id: int, recipe_name: str) -> Tuple[List[Dict], str, str]:
    """Scrape recipe data including ingredients, cook time, and servings."""
    # Create URL
    url_name = clean_recipe_name(recipe_name)
    url = f'https://www.food.com/recipe/{url_name}-{recipe_id}'
    
    try:
        # Add delay to be respectful to the server
        time.sleep(1)
        
        # Make request
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find ingredient list
        ingredient_list = soup.find('ul', class_='ingredient-list')
        ingredients = []
        
        if ingredient_list:
            for li in ingredient_list.find_all('li', style='display: contents'):
                # Skip headings
                if li.find('h4'):
                    continue
                    
                # Get quantity and text
                quantity_span = li.find('span', class_='ingredient-quantity')
                text_span = li.find('span', class_='ingredient-text')
                
                if quantity_span and text_span:
                    # Parse the quantity properly
                    quantity = parse_fraction(quantity_span)
                    ingredient_text = f"{quantity} {text_span.text.strip()}"
                    ingredient_data = parse_ingredient(ingredient_text)
                    ingredients.append(ingredient_data)
        
        # Find recipe facts - using the exact class names from the HTML
        facts_div = soup.find('div', class_='facts svelte-1r658j4')
        print(f"Debug - Found facts div: {facts_div is not None}")
        
        cook_time, servings = parse_recipe_facts(facts_div)
        print(f"Debug - Cook time: {cook_time}, Servings: {servings}")
        
        return ingredients, cook_time, servings
    
    except Exception as e:
        print(f"Error scraping recipe {recipe_id}: {str(e)}")
        return [], None, None

def print_recipe_data(ingredients_json: str, cook_time: str, servings: str) -> None:
    """Pretty print recipe data."""
    if cook_time:
        print(f"\nCook Time: {cook_time}")
    if servings:
        print(f"Servings: {servings}")
        
    print("\nIngredients:")
    if not ingredients_json:
        print("No ingredients found")
        return
        
    ingredients = json.loads(ingredients_json)
    for idx, ingredient in enumerate(ingredients, 1):
        print(f"{idx}. {ingredient['amount'] or ''} {ingredient['unit'] or ''} {ingredient['name']}")

def main():
    # Load the dataframe
    df = pd.read_csv('data/recipe_200.csv')
    
    # Create new columns
    df['ingredients_parsed'] = None
    df['cook_time'] = None
    df['servings'] = None
    
    # Scrape recipe data
    for idx, row in df.iterrows():
        print(f"\nProcessing recipe {idx + 1}/{len(df)}: {row['name']}")
        ingredients, cook_time, servings = scrape_recipe_data(row['id'], row['name'])
        
        # Store the data
        df.at[idx, 'ingredients_parsed'] = json.dumps(ingredients)
        df.at[idx, 'cook_time'] = cook_time
        df.at[idx, 'servings'] = servings
        
        # Print recipe data
        print_recipe_data(json.dumps(ingredients), cook_time, servings)
    
    # Save the updated dataframe
    df.to_csv('data/recipe_200_with_scraped_data.csv', index=False)
    print("\nScraping completed and data saved!")

if __name__ == "__main__":
    main() 