from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone
import random
import os
import json

# === ENV ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "ratings"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Get Users & Recipes ===
users = supabase.table("users").select("id").execute().data
recipes = supabase.table("recipes").select("id").execute().data

user_ids = [u["id"] for u in users]
recipe_ids = [r["id"] for r in recipes]

print(f"📦 Users: {len(user_ids)} | Recipes: {len(recipe_ids)}")

# === Rating Count Distribution ===
def get_num_ratings():
    roll = random.random()
    if roll < 0.6:
        return random.randint(1, 5)
    elif roll < 0.9:
        return random.randint(6, 15)
    else:
        return random.randint(16, 25)

# === Weighted Rating Distribution ===
rating_weights = [1]*5 + [2]*10 + [3]*20 + [4]*45 + [5]*20

# === Generate Ratings ===
ratings = []
for user_id in user_ids:
    num_ratings = get_num_ratings()
    recipe_sample = random.sample(recipe_ids, min(num_ratings, len(recipe_ids)))

    for recipe_id in recipe_sample:
        rating = random.choice(rating_weights)
        ratings.append({
            "user_id": user_id,
            "recipe_id": recipe_id,
            "rating": rating,
            "rated_at": datetime.now(timezone.utc).isoformat()
        })

print(f"✅ Generated {len(ratings)} ratings.")

# === Save to JSON ===
with open("data/ratings.json", "w", encoding="utf-8") as f:
    json.dump(ratings, f, indent=2, ensure_ascii=False)

print("💾 Saved ratings to ratings.json")