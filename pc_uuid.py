"""
Program Purpose: get piececool ids

"""

import re, time, json
import requests
from bs4 import BeautifulSoup

def get_request(given_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    res = requests.get(given_url, headers=headers)
    if res.status_code != 200:
        res.raise_for_status()
        return None
    return res

def get_soup(given_url: str) -> BeautifulSoup | None:
    res = get_request(given_url)
    if res:
        return BeautifulSoup(res.content, 'html.parser')
    return None

def dump_data(data: dict, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return

def search_pc_model(model_uuid: str):
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
            "model": model_uuid,
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

def normalise_product_name(name: str) -> str:
    new_name = name.replace("（", "(").replace("）", ")")
    new_name = re.sub(r'\s*\(\s*(.+?)\s*\)', r' (\1)', new_name) 
    return new_name

def search_pc_product_codes():
    pc_domain: str = "https://www.piececool.com"
    page_idx = 0
    series_ids: dict[int, str] = {
        "54": "IP",
        "7": "P",
        "59": "M",
        "62": "F",
        "63": "B",
        "8": "PC",
    }

    found_products = {}
    req_delay: int = 5
    series_cd: int = 10
    for series_id in series_ids.keys():
        print(series_id, series_ids[series_id])
        series_name: str = f"{series_ids[series_id]}-series"
        found_products[series_name] = []
        for page_idx in range(0, 30):
            print(f'page {page_idx}')
            product_url: str = f"{pc_domain}/listinfo-{series_id}-{page_idx}.html"
            soup = get_soup(product_url)
            results = soup.find("div", class_="proList clearfix").find_all("li")
            if results == [] or not results:
                break
            for result in results:
                product_img_href: str = result.find("div", class_="photo").find("img").get("src").strip()
                img_link: str = f"{pc_domain}{product_img_href}"
                product_wrapper = result.find("b").find("a")

                # product_page_href: str = product_wrapper.get("href").strip()
                # product_page_link: str = f"{pc_domain}{product_page_href}"
                # time.sleep(3)
                # product_page_soup: BeautifulSoup = get_soup(product_page_link)
                # page_details: str = product_page_soup.find("div", class_="proPara").find("ul").find_all("li")
                # product_ename: str = page_details[1].get_text(strip=True).replace("英文名称：", "")

                product_name_with_id: str = product_wrapper.get_text(strip=True)
                print(product_name_with_id)

                if series_name.startswith("PC-"):
                    match = re.match(r"^(.+?)·?\(([^()（）]+)\)$", product_name_with_id)
                else:
                    match = re.match(r"(.+?)·?\(([^()（）]+-[^()（）]+)\)", product_name_with_id)
                if match:
                    product_cname: str = match.group(1)
                    product_id: str = match.group(2)
                    # full_product_name: str = f"{product_cname}-{product_ename}"
                    product_full_name: str = normalise_product_name(product_cname)
                    sheet_link, instructions_link = search_pc_model(product_id)

                    print(product_full_name)
                    print(product_id)

                    found_products[series_name].append({
                        "name": product_full_name,
                        "sku_uuid": product_id,
                        "img_link": img_link,
                        "sheet_link": sheet_link,
                        "instructions_link": instructions_link
                    })

            time.sleep(req_delay)
        time.sleep(series_cd)
    dump_data(found_products, "pc_product_catalog.json")
    
    
def main():
    search_pc_product_codes()
    return

if __name__ == "__main__":
    main()
