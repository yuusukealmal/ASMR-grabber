from asmr import ASMR
from dotenv import load_dotenv
import asyncio, os, requests, json
from git import Repo

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

def git_push():
    load_dotenv()
    try:
        repo = Repo(os.getenv("REPO"))

        if repo.is_dirty(untracked_files=True) or repo.index.diff(None):
            repo.git.add(update=True)
            repo.index.commit("Update RJS")
            origin = repo.remote(name='origin')
            origin.push()
            print("Changes were pushed to the repository.")
        else:
            print("No changes to commit or push.")

    except Exception as e:
        print('Some error occurred while pushing the code:', e) 

if __name__ == "__main__":
    load_dotenv()
    if not os.path.exists("./RJS"):
        os.mkdir("./RJS")
    asyncio.run(update())
    git_push()