import json
import os

from dotenv import load_dotenv
from supabase import Client, create_client

# === CONFIG ===
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "recipes"
JSON_FILE = "data/recipes_with_images.json"

# === CONNECT TO SUPABASE ===
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === LOAD RECIPES ===
with open(JSON_FILE, "r", encoding="utf-8") as f:
    recipes = json.load(f)

# === BATCH INSERT ===
inserted = 0
batch_size = 50

for i in range(0, len(recipes), batch_size):
    batch = recipes[i : i + batch_size]
    response = supabase.table(TABLE_NAME).insert(batch).execute()

    if response.data:
        inserted += len(batch)
    else:
        print(f"❌ Error on batch {i // batch_size + 1}: {response}")

print(f"\n✅ Done! Uploaded {inserted} recipes to Supabase.")
