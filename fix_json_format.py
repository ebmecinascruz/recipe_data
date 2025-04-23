import pandas as pd
import json
import ast

def convert_to_valid_json(value):
    """
    Convert a string representation of a Python list/dict to valid JSON.
    Handles both single and double quotes, and None values.
    """
    if pd.isna(value):
        return None
    
    try:
        # First try to parse as Python literal
        python_obj = ast.literal_eval(value)
        # Then convert to JSON string
        return json.dumps(python_obj)
    except (ValueError, SyntaxError):
        # If that fails, return None
        return None

def main():
    # Load the processed data
    print("Loading recipe data...")
    df = pd.read_csv('data/recipe_200_processed.csv')
    
    # Convert ingredients and instructions to valid JSON
    print("Converting ingredients and instructions to valid JSON...")
    df['ingredients'] = df['ingredients'].apply(convert_to_valid_json)
    df['instructions'] = df['instructions'].apply(convert_to_valid_json)
    
    # Save the updated dataframe
    print("Saving results...")
    df.to_csv('data/recipe_200_processed.json_ready.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    main() 