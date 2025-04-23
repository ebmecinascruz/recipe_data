import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def clean_recipe_name(name: str) -> str:
    """Clean recipe name to create URL-friendly string."""
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    return name

def scrape_creator_names():
    # Read the cleaned recipes
    recipes_df = pd.read_csv('data/recipe_200_processed_cleaned.csv')
    
    # Create a mapping of creator_id to creator_name
    creator_mapping = {}
    
    # Headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # First, try to get creator names for all recipes
    for index, row in recipes_df.iterrows():
        recipe_id = row['recipe_id']
        creator_id = row['creator_id']
        title = row['title_raw']
        
        # Skip if we already have this creator in our mapping
        if creator_id in creator_mapping:
            continue
            
        # Clean the recipe name and construct the URL
        url_name = clean_recipe_name(title)
        recipe_url = f'https://www.food.com/recipe/{url_name}-{recipe_id}'
        
        try:
            # Make the request
            response = requests.get(recipe_url, headers=headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the creator name in the byline div
            byline_div = soup.find('div', class_='byline')
            if byline_div:
                creator_link = byline_div.find('a', class_='svelte-176rmbi')
                if creator_link:
                    creator_name = creator_link.text.strip()
                    creator_mapping[creator_id] = creator_name
                    print(f"Found creator name for creator_id {creator_id}: {creator_name}")
                else:
                    print(f"Could not find creator link for recipe {recipe_id}")
            else:
                print(f"Could not find byline div for recipe {recipe_id}")
                
        except Exception as e:
            print(f"Error scraping recipe {recipe_id}: {str(e)}")
    
    # Create a dataframe from the mapping
    creator_df = pd.DataFrame({
        'creator_id': list(creator_mapping.keys()),
        'creator_name': list(creator_mapping.values())
    })
    
    # Save the creator information
    creator_df.to_csv('data/creator_names.csv', index=False)
    print(f"Saved {len(creator_df)} unique creator names")
    
    # Print summary of missing creator names
    missing_creators = set(recipes_df['creator_id']) - set(creator_mapping.keys())
    if missing_creators:
        print(f"\nMissing creator names for {len(missing_creators)} creator IDs:")
        for creator_id in missing_creators:
            print(f"Creator ID: {creator_id}")

if __name__ == "__main__":
    scrape_creator_names() 