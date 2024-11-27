from asmr import ASMR
from dotenv import load_dotenv
import asyncio, os, requests, json


BASE = "https://api.asmr-200.com/api/"
URLS = [
    ("recommender/recommend-for-user", "POST", "recommend-for-user"),
    ("recommender/popular", "POST", "popular"),
    ("tags", "GET", "tags"),
    ("circles", "GET", "circles"),
    ("vas", "GET", "vas"),
    ("works", "GET", "works"),
]

async def update():
    if requests.get(BASE + "health").text == "OK":        
        asmr  = ASMR(os.environ.get("USERNAME"), os.environ.get("PASSWORD"))
        await asmr.get_token()
        for url, method, name in URLS:
            r = await asmr.request(url= BASE + url, method= method, json={"userId": asmr.uuid} if url == "recommender/recommend-for-user" else {})
            with open(f"./RJS/{name}.json", "w", encoding="utf-8") as f:
                json.dump(r.json(), f, indent=4, ensure_ascii=False)
    else:
        print("ASMR-200 無法連線")

if __name__ == "__main__":
    load_dotenv()
    if not os.path.exists("./RJS"):
        os.mkdir("./RJS")
    asyncio.run(update())
