import pandas as pd
import ast
from typing import List, Dict, Any
import json
import re

def parse_steps(steps_str: str) -> List[Dict[str, Any]]:
    """
    Parse recipe steps string into a list of dictionaries with step numbers and descriptions.
    
    Args:
        steps_str: String containing recipe steps
        
    Returns:
        List of dictionaries with 'step' and 'description' keys
    """
    try:
        # Try to parse as JSON first
        steps = json.loads(steps_str)
    except json.JSONDecodeError:
        try:
            # Try to parse as Python literal
            steps = ast.literal_eval(steps_str)
        except (ValueError, SyntaxError):
            # If parsing fails, return empty list
            return []
    
    # Convert to list if it's a string
    if isinstance(steps, str):
        steps = [step.strip() for step in steps.split('\n') if step.strip()]
    
    # Process steps into structured format
    processed_steps = []
    for i, step in enumerate(steps, 1):
        if isinstance(step, dict):
            # If step is already a dictionary, ensure it has the right keys
            processed_step = {
                'step': step.get('step', i),
                'description': step.get('description', '')
            }
        else:
            # If step is a string, create dictionary
            processed_step = {
                'step': i,
                'description': str(step).strip()
            }
        processed_steps.append(processed_step)
    
    return processed_steps

def parse_ingredients(ingredients_json: str) -> List[Dict]:
    """Parse ingredients from JSON string into list of dictionaries with name, unit, and amount."""
    if not ingredients_json:
        return []
        
    try:
        ingredients = json.loads(ingredients_json)
        # Return the ingredients as is, since they're already in the correct format
        return ingredients
    except json.JSONDecodeError:
        return []

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the recipe dataframe.
    
    Args:
        df: Input dataframe with recipe data
        
    Returns:
        Preprocessed dataframe with renamed and reordered columns
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Process steps column
    if 'steps' in df.columns:
        print("Processing recipe steps...")
        df['instructions'] = df['steps'].apply(parse_steps)
    
    # Rename columns
    column_mapping = {
        'name': 'title',
        'steps_processed': 'instructions',
        'contributor_id': 'creator_id',
        'ingredients': 'ingredients_raw',
        'ingredients_parsed': 'ingredients',
    }
    df = df.rename(columns=column_mapping)
    
    # Define the desired column order
    column_order = [
        'title',
        'cook_time',
        'difficulty',
        'creator_id',
        'servings',
        'cuisine',
        'description',
        'tags',
        'ingredients',
        'instructions'
    ]
    
    # Reorder columns, keeping any additional columns that might exist
    existing_columns = [col for col in column_order if col in df.columns]
    other_columns = [col for col in df.columns if col not in column_order]
    df = df[existing_columns + other_columns]
    
    return df

def preprocess_recipes():
    # Load the dataframe with scraped data
    df = pd.read_csv('data/recipe_200_with_scraped_data.csv')
    
    # Create new dataframe with processed data
    processed_df = pd.DataFrame()
    
    # Add recipe_id and creator_id
    processed_df['recipe_id'] = df['id']
    processed_df['creator_id'] = df['contributor_id']
    
    # Add both raw and scraped titles
    processed_df['title_raw'] = df['name']
    processed_df['title'] = df['title'].fillna(df['name'])
    
    # Handle description - convert NaN to empty string and ensure it's a string
    processed_df['description'] = df['description'].fillna('').astype(str)
    
    # Parse ingredients from the scraped data
    processed_df['ingredients'] = df['ingredients_parsed'].apply(parse_ingredients)
    
    # Parse instructions from the scraped data
    def format_instructions(instructions_list):
        if pd.isna(instructions_list):
            return []
        try:
            instructions = json.loads(instructions_list)
            return [{'step': idx + 1, 'description': step} for idx, step in enumerate(instructions)]
        except (json.JSONDecodeError, TypeError):
            return []
    
    processed_df['instructions'] = df['instructions'].apply(format_instructions)
    
    # Add additional columns
    processed_df['cook_time'] = df['cook_time']
    processed_df['servings'] = df['servings']
    
    # Add tags if they exist in the original dataframe
    if 'tags' in df.columns:
        processed_df['tags'] = df['tags']
    else:
        processed_df['tags'] = None
    
    # Save the processed dataframe
    processed_df.to_csv('data/recipe_200_processed.csv', index=False)
    print("Preprocessing completed and data saved!")

if __name__ == "__main__":
    preprocess_recipes() 