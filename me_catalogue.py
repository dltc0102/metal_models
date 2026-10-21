"""
Program Purpose: gets all metal earth instruction manuals

Pseudo code/program details: 
instructions_url: https://www.metalearth.com/instructions
"""

import os
import json
from bs4 import BeautifulSoup


def dump_data(data: dict, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return

def load_soup(soup_file: str) -> BeautifulSoup:
    with open(soup_file, 'r', encoding='utf-8') as sf:
        data = sf.read()
    return BeautifulSoup(data, 'html.parser')

def get_category_class_name(cat_name: str) -> str:
    exceptions = {
        'caterpillar': 'cat',
        'doctor who': 'doctorwho',
        'game of thrones': 'got',
        'gundam': 'gundam-collection',
        'harry potter': 'hp',
        'lord of the rings': 'lotr',
        'lord of the rings - legends': 'lotr-legends',
        'mass effect': 'masseffect',
        'my little pony': 'mlp',
        'mythical & fantasy': 'mythical-fantasy',
        'premium series': 'premium',
        'star trek': 'startrek',
        'star wars': 'starwars',
        'western star trucks': 'western-star',
    }

    key = cat_name.strip().lower()
    section_id = exceptions.get(key, key.replace(' ', '-'))
    return f'ins-section-{section_id}'

def get_product_details(product) -> dict[str, str]:
    me_domain: str = "https://www.metalearth.com"
    product_picture = product.find("div", class_="ins-p-pic")
    is_premium: bool = "yes" if product_picture.find("div", class_="p-premium-tag") else "no"
    picture_link: str = product_picture.find("img", class_="me-lazy animated bounceIn").get("src").strip()

    product_details = product.find("div", class_="ins-product-details")
    sku_uuid: str = product_details.find("h6", class_="ins-p-sku").get_text(strip=True)
    title: str = product_details.find("div", class_="ins-p-title").get_text(strip=True)
    download_href = product_details.find("div", class_="ins-p-download").find("a").get("href").strip()
    download_link: str = f"{me_domain}{download_href}"

    return {
        "name": title,
        "sku_uuid": sku_uuid,
        "is_premium": is_premium,
        "picture_link": picture_link,
        "download_link": download_link
    }

def get_product_catalogue() -> None:
    isoup = load_soup("metal_earth_instructions.html")
    categories = isoup.find_all("div", class_="ins-cate-header")
    category_names = [c.get_text(strip=True).lower() for c in categories]
    category_names = [n for n in category_names if 'search results' not in n]

    product_catalog: dict[str, list[dict]] = {}

    for category_name in category_names:
        category_class_name: str = get_category_class_name(category_name)
        # print(f"category_class_name: {category_class_name}")
        products = isoup.find("div", id=category_class_name).find_all("div", class_="ins-product-sm-wrap")
        for product in products:
            details = get_product_details(product)
            if category_name in product_catalog.keys():
                product_catalog[category_name].append(details)
            else:
                product_catalog[category_name] = [details]

    me_product_catalog_fpath: str = os.path.join(os.getcwd(), "me_product_catalogue.json")
    dump_data(product_catalog, me_product_catalog_fpath)
    return

def main():
    get_product_catalogue()

if __name__ == "__main__":
    main()
