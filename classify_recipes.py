import pandas as pd
import subprocess
from typing import Tuple, Optional
import ast

def classify_cuisine_and_difficulty(title: str, ingredients: str, description: Optional[str] = None, model: str = "mistral:latest") -> Tuple[str, str]:
    """
    Classify a recipe's cuisine and difficulty using a local LLM.
    
    Args:
        title: Recipe title
        ingredients: Comma-separated list of ingredients
        description: Optional recipe description
        model: Ollama model to use (default: mistral:latest)
        
    Returns:
        Tuple of (cuisine, difficulty)
    """
    # Build prompt
    prompt = f"""
You are a food classification expert.

Given the title, ingredients, and optional description of a recipe, classify the following:

1. Cuisine — choose from:
[American, Mexican, Italian, Indian, Asian, French, Middle-Eastern, Mediterranean, African, Dessert, Breakfast, Snack, Other]

Be sure to only choose from the above categories and don't add any additional text or specific desription of the cuisine. The response should be a single word from the list.

2. Difficulty — choose from:
[Easy, Medium, Hard]

Only choose "Other" for cuisine if none apply.
Only choose "Hard" for recipes with many steps, exotic ingredients, or long cooking times.

---

Title: {title}
Ingredients: {ingredients}
"""

    if description:
        prompt += f"Description: {description}\n"

    prompt += "\nRespond in this format:\nCuisine: <cuisine>\nDifficulty: <difficulty>"

    # Run local LLM (Ollama)
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        capture_output=True,
        text=True
    )

    # Parse result
    output = result.stdout.strip()
    cuisine = None
    difficulty = None

    for line in output.splitlines():
        if line.lower().startswith("cuisine"):
            cuisine = line.split(":")[-1].strip()
        elif line.lower().startswith("difficulty"):
            difficulty = line.split(":")[-1].strip()

    return cuisine, difficulty

def process_recipe(row: pd.Series) -> pd.Series:
    """
    Process a single recipe row to classify its cuisine and difficulty.
    
    Args:
        row: Pandas Series containing recipe data
        
    Returns:
        Pandas Series with cuisine and difficulty
    """
    title = row["title"]
    
    # Handle ingredients in the new format
    try:
        ingredients_list = ast.literal_eval(row["ingredients"])
        # Extract ingredient names from the list of dictionaries
        ingredient_names = [item["ingredient"] for item in ingredients_list if isinstance(item, dict) and "ingredient" in item]
        ingredients = ", ".join(ingredient_names)
    except (ValueError, SyntaxError, TypeError, KeyError):
        # If ingredients can't be parsed or is in a different format, use raw ingredients
        ingredients = str(row.get("ingredients_raw", ""))
    
    # Get description if available
    description = row.get("description", "")
    
    # Call the classifier
    cuisine, difficulty = classify_cuisine_and_difficulty(title, ingredients, description)
    
    return pd.Series([cuisine, difficulty])

def main():
    # Load the preprocessed data
    print("Loading preprocessed recipe data...")
    df = pd.read_csv('data/recipe_200_preprocessed.csv')
    
    # Add new columns
    print("Adding cuisine and difficulty columns...")
    df[["cuisine", "difficulty"]] = df.apply(process_recipe, axis=1)
    
    # Define the desired columns in order
    desired_columns = [
        'id',
        'title',
        'cook_time',
        'creator_id',
        'servings',
        'description',
        'tags',
        'instructions',
        'cuisine',
        'difficulty',
        'ingredients'
    ]
    
    # Select only the desired columns
    df = df[desired_columns]
    
    # Save the updated dataframe
    print("Saving results...")
    df.to_csv('data/recipe_200_with_classification.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    main() 