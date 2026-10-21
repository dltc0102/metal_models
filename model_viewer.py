import os, requests, json
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright

def image_enhance(input: str, output: str):
    return

def load_sheet(name: str):
    sheet_dir_path: str = os.join(os.getcwd(), "model_sheets")
    modelname_subdirs: list[str] = os.listdir(sheet_dir_path)

def dump_data(data: dict, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return

def load_soup(soup_file: str) -> BeautifulSoup:
    with open(soup_file, 'r', encoding='utf-8') as sf:
        data = sf.read()
    return BeautifulSoup(data, 'html.parser')

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


class ModelInquirer:
    def __init__(self, initial_filename: str, model_vendor: str = "Unknown", model_number: str = "", keywords: list[str] = []):
        self.initial_filename: str = initial_filename
        self.model_vendor: str = model_vendor.strip().lower().replace(" ", "_")
        self.model_number: str = model_number
        self.model_keywords: list[str] = keywords
        self.query = self.model_search()


    def _get_request(self, given_url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        res = requests.get(given_url, headers=headers)
        if res.status_code != 200: 
            res.raise_for_status()
            return None
        return res

    def _get_soup(self, given_url: str) -> BeautifulSoup | None:
        res = self._get_request(given_url)
        if res:
            return BeautifulSoup(res.content, 'html.parser')
        return None

    def model_search(self):
        # redirect to MetalEarth or Piececool or register as UnknownVendor
        return 



class MetalEarth:
    def __init__(self, filename: str):
        self.input_filename: str = filename.replace(".pdf", "")
        self.filename_sku: str = self.input_filename.split("_")[-1].strip()
        self.me_domain: str = "https://www.metalearth.com"
        self.catalog_fname: str = "me_product_catalog.json"

        if not os.path.exists(self.catalog_fname):
            self.get_product_catalogue()
        self.catalog_data = self.load_catalog()

    async def get_me_instructions_html(url: str = "https://www.metalearth.com/instructions") -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url, wait_until="load", timeout=60000)

            await page.wait_for_selector("div.ins-product-sm-wrap", state="attached", timeout=60000)

            last_count = -1
            stable_rounds = 0
            while stable_rounds < 5:
                count = await page.evaluate("document.querySelectorAll('div.ins-product-sm-wrap').length")
                if count == last_count:
                    stable_rounds += 1
                else:
                    stable_rounds = 0
                    last_count = count
                await page.wait_for_timeout(1000)

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

            html_content = await page.content()

            await browser.close()
            return html_content

    def get_category_class_name(self, cat_name: str) -> str:
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

    def get_product_details(self, product) -> dict[str, str]:
        me_domain: str = "https://www.metalearth.com"
        product_picture = product.find("div", class_="ins-p-pic")
        product_link: str = product_picture.find("a").get("href").strip()
        product_page_url: str = f"{me_domain}{product_link}"
        product_page_soup: BeautifulSoup = get_soup(product_page_url)
        product_details_spans = product_page_soup.find("div", class_="product-collateral").find_all("span", class_="value")

        product_sheets_num = None
        for span in product_details_spans:
            text = span.get_text(strip=True)
            if "Sheet" in text:
                try:
                    product_sheets_num = float(
                        text.replace("Sheets", "").replace("Sheet", "").strip()
                    )
                except ValueError:
                    pass
                break

        if product_sheets_num is None:
            print(f"Could not find sheet count for: {product_page_url}")
            print(f"Spans were: {[s.get_text(strip=True) for s in product_details_spans]}")
            
        picture_link: str = product_picture.find("img", class_="me-lazy animated bounceIn").get("src").strip()

        product_details = product.find("div", class_="ins-product-details")
        sku_uuid: str = product_details.find("h6", class_="ins-p-sku").get_text(strip=True)
        title: str = product_details.find("div", class_="ins-p-title").get_text(strip=True)
        download_href = product_details.find("div", class_="ins-p-download").find("a").get("href").strip()
        download_link: str = f"{me_domain}{download_href}"

        return {
            "name": title,
            "sku_uuid": sku_uuid,
            "sheets": product_sheets_num,
            "picture_link": picture_link,
            "download_link": download_link
        }

    def get_product_catalogue(self) -> None:
        isoup = load_soup("metal_earth_instructions.html")
        categories = isoup.find_all("div", class_="ins-cate-header")
        category_names = [c.get_text(strip=True).lower() for c in categories]
        category_names = [n for n in category_names if 'search results' not in n]

        product_catalog: dict[str, list[dict]] = {}

        for category_name in category_names:
            category_class_name: str = self.get_category_class_name(category_name)
            print(f"category_class_name: {category_class_name}")
            products = isoup.find("div", id=category_class_name).find_all("div", class_="ins-product-sm-wrap")
            for product in products:
                details = self.get_product_details(product)
                if category_name in product_catalog.keys():
                    product_catalog[category_name].append(details)
                else:
                    product_catalog[category_name] = [details]

        me_product_catalog_fpath: str = os.path.join(os.getcwd(), self.catalog_fname)
        dump_data(product_catalog, me_product_catalog_fpath)
        return

    def load_catalog(self):
        with open(self.catalog_fname, 'r', encoding='utf-8') as sf:
            data = json.load(sf)
        return data
    
    def search_catalog_with_uuid(self) -> dict[str, str] | None:
        print(self.filename_sku.lower())
        for category, products in self.catalog_data.items():
            for product in products:
                if product["sku_uuid"].lower() == self.filename_sku.lower():
                    print(f"category: {category}")
                    return product
        return None



class Piececool:
    def __init__(self):
        return

def get_manuals_dirpath(filename: str) -> str:
    normalised_fname: str = filename.replace(".pdf", "").strip()
    manuals_dirpath: str = os.path.join(os.getcwd(), "manuals")
    if normalised_fname.startswith("ME_"): return os.path.join(manuals_dirpath, "Metal Earth")
    if normalised_fname.startswith("PC_"): return os.path.join(manuals_dirpath, "Piececool")
    if normalised_fname.startswith("UN_"): return os.path.join(manuals_dirpath, "Other")

def needs_download(filename: str, download_link: str) -> bool:
    # filename is most probably in input folder, but will check manuals ME too.
    input_dirpath: str = os.path.join(os.getcwd(), "input")
    manuals_dirpath: str = get_manuals_dirpath(filename)
    if filename not in os.listdir(input_dirpath): return True
    if filename not in os.listdir(manuals_dirpath): return True
    
def main():
    input_dirpath: str = os.path.join(os.getcwd(), "input")
    input_files: list[str] = [
        file for file in os.listdir(input_dirpath) 
        if file.endswith(".pdf") and 
        (file.startswith("ME") or file.startswith("PC") or file.startswith("UN"))
    ]

    for input_file in input_files:
        if input_file.startswith("ME"):
            inst = MetalEarth(input_file)
            details = inst.search_catalog_with_uuid()

    return

if __name__ == "__main__":
    main()