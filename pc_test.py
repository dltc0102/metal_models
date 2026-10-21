import requests
import time
import sys, os

def search_model(model: str):
    ENDPOINT = "http://www.piececool.com/wap/e/action/instructions.php"
    BASE = "http://www.piececool.com"

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": BASE,
        "Referer": f"{BASE}/wap/instructions/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })
    session.cookies.set("zhaoshang", "0")
    r = session.post(
        ENDPOINT,
        data={
            "page": "0",
            "family": "",
            "ttmarket": "",
            "model": model,
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("ret") != "0":
        raise RuntimeError(f"API error: {data}")
    sheet_download_link: str = f"{BASE}{data["results"][0]["metal_map"]}"
    instructions_download_link: str = f"{BASE}{data["results"][0]["download"]}"
    return (sheet_download_link, instructions_download_link)

if __name__ == "__main__":
    print(search_model("P490-SK"))