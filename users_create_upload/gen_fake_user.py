import requests
import random
import json
from datetime import datetime, timezone
from user_bios import BASIC_BIOS

NUM_USERS = 50
genders = ["male", "female"]
users = []

def fetch_user(gender):
    res = requests.get(f"https://randomuser.me/api/?gender={gender}")
    if res.status_code != 200:
        return None

    data = res.json()["results"][0]
    full_name = f"{data['name']['first']} {data['name']['last']}"
    username = data["login"]["username"]
    avatar_url = data["picture"]["large"]
    bio = random.choice(BASIC_BIOS)

    return {
        "full_name": full_name,
        "username": username,
        "avatar_url": avatar_url,
        "bio": bio,
        "website": None,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

for _ in range(NUM_USERS):
    gender = random.choice(genders)
    user = fetch_user(gender)
    if user:
        users.append(user)

with open("data/fake_users.json", "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(users)} fake users to fake_users.json")