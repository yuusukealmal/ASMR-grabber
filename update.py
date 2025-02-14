from asmr import ASMR
from dotenv import load_dotenv
import asyncio, os, requests, json
from git import Repo
from datetime import datetime, timedelta

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
        asmr  = ASMR(os.environ.get("NAME"), os.environ.get("PASSWORD"))
        await asmr.get_token()
        for url, method, name in URLS:
            if name in ["tags", "circles", "vas"]:
                r = await asmr.request(url= BASE + url, method= method)
                with open(f"./json/{name}.json", "w", encoding="utf-8") as f:
                    json.dump(r.json(), f, indent=4, ensure_ascii=False)
            else:
                r = await asmr.request(url= BASE + url, method= method, json={"userId": asmr.uuid})
                pageSize = r.json()["pagination"]["pageSize"]
                totalCount = r.json()["pagination"]["totalCount"]
                pages = int(totalCount / pageSize) if totalCount % pageSize == 0 else int(totalCount / pageSize) + 1
                for page in range(1, pages + 1):
                    r = await asmr.request(url= BASE + url + f"?page={page}", method= method, json={"userId": asmr.uuid, "page": page})
                    with open(f"./json/{name}/{name}{-page}.json", "a", encoding="utf-8") as f:
                        json.dump(r.json(), f, indent=4, ensure_ascii=False)
    else:
        print("ASMR-200 無法連線")

def git_push():
    t = datetime.utcnow() + timedelta(hours=8)
    t_str = t.strftime("%Y-%m-%d %H:%M:%S")
    try:
        repo = Repo(os.getenv("REPO"))

        if repo.is_dirty(untracked_files=True) or repo.index.diff(None):

            repo.git.add(update=True)
            commit = repo.index.commit("Update RJS")
            origin = repo.remote(name='origin')
            md5 = commit.hexsha[:7]
            origin.push()
            print(f"{t_str} {md5} Changes were pushed to the repository.")
        else:
            print(f"{t_str} No changes to commit or push.")

    except Exception as e:
        print(f"{t_str} Some error occurred while pushing the code:", e) 

if __name__ == "__main__":
    load_dotenv()
    if not os.path.exists("./json"):
        os.mkdir("./json")
    asyncio.run(update())
    git_push()