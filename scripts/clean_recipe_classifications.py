import pandas as pd
import re

def clean_classifications():
    # Read the processed recipes
    recipes_df = pd.read_csv('data/recipe_200_processed.json_ready.csv')
    
    # Function to remove text in parentheses
    def remove_parentheses(text):
        if pd.isna(text):
            return text
        return re.sub(r'\s*\([^)]*\)', '', text)
    
    # Clean cuisine and difficulty columns
    recipes_df['cuisine'] = recipes_df['cuisine'].apply(remove_parentheses)
    recipes_df['difficulty'] = recipes_df['difficulty'].apply(remove_parentheses)
    
    # Save the cleaned data
    recipes_df.to_csv('data/recipe_200_processed_cleaned.csv', index=False)
    print("Cleaned recipe classifications and saved to recipe_200_processed_cleaned.csv")

if __name__ == "__main__":
    clean_classifications() 