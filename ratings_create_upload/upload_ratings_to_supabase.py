import json
import os

from dotenv import load_dotenv
from supabase import Client, create_client

# === CONFIG ===
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "ratings"
JSON_FILE = "data/ratings.json"

# === CONNECT TO SUPABASE ===
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === LOAD RATINGS ===
with open(JSON_FILE, "r", encoding="utf-8") as f:
    ratings = json.load(f)

# === BATCH INSERT ===
inserted = 0
batch_size = 50

for i in range(0, len(ratings), batch_size):
    batch = ratings[i : i + batch_size]
    response = supabase.table(TABLE_NAME).insert(batch).execute()

    if response.data:
        inserted += len(batch)
    else:
        print(f"❌ Error on batch {i // batch_size + 1}: {response}")

print(f"\n✅ Uploaded {inserted} ratings to Supabase from {JSON_FILE}")
