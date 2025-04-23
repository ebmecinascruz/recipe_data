import pandas as pd

def prepare_reviews():
    # Read the processed recipes to get the recipe_ids we want to keep
    recipes_df = pd.read_csv('data/recipe_200_processed.json_ready.csv')
    recipe_ids = set(recipes_df['recipe_id'].unique())
    
    # Read the raw interactions data
    reviews_df = pd.read_csv('data/archive/RAW_interactions.csv')
    
    # Count unique recipes in reviews
    unique_recipes_in_reviews = reviews_df['recipe_id'].unique()
    print(f"Total unique recipes in reviews dataset: {len(unique_recipes_in_reviews)}")
    
    # Filter reviews to only include recipes in our processed dataset
    filtered_reviews = reviews_df[reviews_df['recipe_id'].isin(recipe_ids)]
    
    # Select only the columns we need and rename review to comment
    final_reviews = filtered_reviews[['recipe_id', 'user_id', 'rating', 'review']].rename(columns={'review': 'comment'})
    
    # Save the processed reviews
    final_reviews.to_csv('data/reviews_processed.csv', index=False)
    print(f"Processed {len(final_reviews)} reviews for {len(recipe_ids)} recipes")

if __name__ == "__main__":
    prepare_reviews() 