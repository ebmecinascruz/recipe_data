from supabase import create_client, Client
from dotenv import load_dotenv
import os
from collections import defaultdict
import statistics

# === CONFIG ===
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Step 1: Load all ratings ===
response = supabase.table("ratings").select("recipe_id", "rating").execute()
ratings_data = response.data

# === Step 2: Group by recipe and compute avg + count ===
recipe_ratings = defaultdict(list)

for r in ratings_data:
    recipe_ratings[r["recipe_id"]].append(r["rating"])

# === Step 3: Update recipes with new values ===
updated = 0

for recipe_id, ratings in recipe_ratings.items():
    avg_rating = round(statistics.mean(ratings), 2)
    count = len(ratings)

    update_payload = {
        "rating": avg_rating,
        "rating_count": count
    }

    response = supabase.table("recipes").update(update_payload).eq("id", recipe_id).execute()

    if response.data:
        updated += 1
    else:
        print(f"❌ Failed to update recipe {recipe_id}: {response}")

print(f"\n✅ Updated {updated} recipes with average rating + count.")