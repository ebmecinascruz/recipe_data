import pandas as pd
import ast
from typing import List, Dict, Any
import json

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

def main():
    # Load the data
    print("Loading recipe data...")
    df = pd.read_csv('data/recipe_200_with_scraped_data.csv')
    
    # Preprocess the data
    print("Preprocessing recipe data...")
    df = preprocess_dataframe(df)
    
    # Save the preprocessed data
    print("Saving preprocessed data...")
    df.to_csv('data/recipe_200_preprocessed.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    main() 