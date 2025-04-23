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
        elif 'Serves:' in label.text or 'Yields:' in label.text:
            value = item.find('dd', class_='facts__value svelte-1r658j4')
            if value:
                # First try to find the value in the adjust div
                adjust_div = value.find('div', class_='adjust svelte-1o10zxc')
                if adjust_div:
                    value_span = adjust_div.find('span', class_='value svelte-1o10zxc')
                    if value_span:
                        servings = value_span.text.strip()
                else:
                    # If no adjust div, get the value directly from the facts__value div
                    servings = value.text.strip()
    
    return cook_time, servings

def parse_ingredient(ingredient_text: str) -> Dict:
    """Parse ingredient text into structured data."""
    # Remove any leading/trailing whitespace
    ingredient_text = ingredient_text.strip()
    
    # Initialize the result dictionary with the required fields in the correct order
    result = {
        'name': None,
        'unit': None,
        'amount': None
    }
    
    # Split the ingredient text into parts
    parts = ingredient_text.split()
    
    # The first part is usually the amount
    if parts:
        result['amount'] = parts[0]
        
        # The second part might be the unit
        if len(parts) > 1:
            # Check if the second part is a unit
            if parts[1] in ['cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons', 
                          'ounce', 'ounces', 'pound', 'pounds', 'g', 'kg', 'ml', 'l']:
                result['unit'] = parts[1]
                # The rest is the name
                result['name'] = ' '.join(parts[2:])
            else:
                # If no unit, the rest is the name
                result['name'] = ' '.join(parts[1:])
    
    return result

def parse_instructions(instructions_section) -> List[str]:
    """Parse recipe instructions from the directions section."""
    if not instructions_section:
        return []
        
    # Find the direction list
    direction_list = instructions_section.find('ul', class_='direction-list svelte-1r658j4')
    if not direction_list:
        return []
    
    # Get all direction items
    instructions = []
    for li in direction_list.find_all('li', class_='direction svelte-1r658j4'):
        instructions.append(li.text.strip())
    
    return instructions

def parse_description(description_div) -> str:
    """Parse recipe description from the description div."""
    if not description_div:
        print("Debug - No description div found")
        return ""
        
    # Find the recipe-description paragraph
    recipe_desc = description_div.find('div', class_='recipe-description paragraph')
    if not recipe_desc:
        print("Debug - No recipe-description paragraph found")
        return ""
        
    # Find the text-truncate div that contains the description
    truncate_div = recipe_desc.find('div', class_='text-truncate svelte-1aswkii')
    if truncate_div:
        # First try to get the description from the title attribute
        description = truncate_div.get('title', '')
        if description:
            print(f"Debug - Found description in title attribute: {description[:100]}...")
            # Remove any quotes at the start and end
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1]
            return description.strip()
        
        # If no title attribute, try to get from the text div
        text_div = truncate_div.find('div', class_='text svelte-1aswkii')
        if text_div:
            text = text_div.text.strip()
            print(f"Debug - Found text in text div: {text[:100]}...")
            # Remove any quotes at the start and end
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return text.strip()
        else:
            print("Debug - No text div found")
    else:
        print("Debug - No text-truncate div found")
    
    return ""

def scrape_recipe_data(recipe_id: int, recipe_name: str) -> Tuple[List[Dict], str, str, str, List[str], str]:
    """Scrape recipe data including ingredients, cook time, servings, original title, instructions, and description."""
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
        
        # Find the original title
        title_h1 = soup.find('h1', class_='svelte-1muv3s8')
        original_title = title_h1.text.strip() if title_h1 else recipe_name
        
        # Find the description - look for the recipe-description paragraph
        description = ""
        description_div = soup.find('div', class_='author-description svelte-q8300c')
        if description_div:
            print("Debug - Found author-description div")
            description = parse_description(description_div)
        else:
            print("Debug - Could not find author-description div")
        
        # Find ingredient list
        ingredients = []
        ingredient_list = soup.find('ul', class_='ingredient-list')
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
        
        # Find recipe facts
        facts_div = soup.find('div', class_='facts svelte-1r658j4')
        print(f"Debug - Found facts div: {facts_div is not None}")
        
        cook_time, servings = parse_recipe_facts(facts_div)
        print(f"Debug - Cook time: {cook_time}, Servings: {servings}")
        
        # Find instructions section and parse instructions
        instructions_section = soup.find('section', class_='layout__item directions svelte-1r658j4')
        instructions = parse_instructions(instructions_section)
        
        return ingredients, cook_time, servings, original_title, instructions, description
    
    except Exception as e:
        print(f"Error scraping recipe {recipe_id}: {str(e)}")
        return [], None, None, recipe_name, [], ""

def print_recipe_data(ingredients_json: str, cook_time: str, servings: str, instructions: List[str], description: str) -> None:
    """Pretty print recipe data."""
    if cook_time:
        print(f"\nCook Time: {cook_time}")
    if servings:
        print(f"Servings: {servings}")
    
    # Always print description, even if empty
    print(f"\nDescription: {description if description else 'No description found'}")
        
    print("\nIngredients:")
    if not ingredients_json:
        print("No ingredients found")
    else:
        ingredients = json.loads(ingredients_json)
        for idx, ingredient in enumerate(ingredients, 1):
            # Format the ingredient string
            parts = []
            if ingredient.get('amount'):
                parts.append(ingredient['amount'])
            if ingredient.get('unit'):
                parts.append(ingredient['unit'])
            if ingredient.get('name'):
                parts.append(ingredient['name'])
            print(f"{idx}. {' '.join(parts)}")
    
    print("\nInstructions:")
    if not instructions:
        print("No instructions found")
    else:
        for idx, instruction in enumerate(instructions, 1):
            print(f"{idx}. {instruction}")

def main():
    # Load the dataframe
    df = pd.read_csv('data/recipe_200.csv')
    
    # Create new columns for scraped data if they don't exist
    if 'ingredients_parsed' not in df.columns:
        df['ingredients_parsed'] = None
    if 'cook_time' not in df.columns:
        df['cook_time'] = None
    if 'servings' not in df.columns:
        df['servings'] = None
    if 'description' not in df.columns:
        df['description'] = None
    if 'title' not in df.columns:
        df['title'] = None
    if 'instructions' not in df.columns:
        df['instructions'] = None
    
    # Scrape recipe data
    for idx, row in df.iterrows():
        print(f"\nProcessing recipe {idx + 1}/{len(df)}: {row['name']}")
        ingredients, cook_time, servings, original_title, instructions, description = scrape_recipe_data(row['id'], row['name'])
        
        # Store the data
        df.at[idx, 'ingredients_parsed'] = json.dumps(ingredients)
        df.at[idx, 'cook_time'] = cook_time
        df.at[idx, 'servings'] = servings
        df.at[idx, 'title'] = original_title
        df.at[idx, 'description'] = description  # Make sure description is stored
        df.at[idx, 'instructions'] = json.dumps(instructions)
        
        # Print recipe data
        print(f"Original title: {original_title}")
        print_recipe_data(json.dumps(ingredients), cook_time, servings, instructions, description)
    
    # Save the updated dataframe
    df.to_csv('data/recipe_200_with_scraped_data.csv', index=False)
    print("\nScraping completed and data saved!")

if __name__ == "__main__":
    main() 