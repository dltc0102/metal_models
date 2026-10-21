"""
Program Purpose: splits the metal earth sheet + instruction pdf into two separate pdfs
"""

import os
import re
import pymupdf
import json

# ME_ICX217 has 2.625 sheets // 1 page
# ME_PS2027 has 3 sheets // 1 page
# ME_PS2024 has 3.25 sheeets // 2 page
# ME_ICX258 has 4 sheets // 2 page
# ME_MMS011 has 1 sheet // 1 page
# ME_MMS465 has 4.5 sheets // 1.5 pages

def get_input_files() -> list[str]:
    input_dirpath: str = os.path.join(os.getcwd(), "input")
    input_files: list[str] = [
        os.path.join(input_dirpath, file) for file in os.listdir(input_dirpath) 
        if file.endswith(".pdf") and 
        (file.startswith("ME") or file.startswith("PC") or file.startswith("UN"))
    ]
    return input_files

def split_landscape_pdf(input_path: str, sheets_count: int, output_dirpath: str, needs_sheets: bool, needs_instructions: bool):
    base, _ = os.path.splitext(input_path)
    sheets_path: str = os.path.join(output_dirpath, f"Sheets.pdf")
    instructions_path: str = os.path.join(output_dirpath, f"Instructions.pdf")

    src = pymupdf.open(input_path)
    out = pymupdf.open()

    # split logic
    for page in src:
        rect = page.rect
        mid_x = rect.x0 + rect.width / 2

        left_rect = pymupdf.Rect(rect.x0, rect.y0, mid_x, rect.y1)
        right_rect = pymupdf.Rect(mid_x, rect.y0, rect.x1, rect.y1)

        for r in (left_rect, right_rect):
            new_page = out.new_page(width=r.width, height=r.height)
            new_page.show_pdf_page(new_page.rect, src, page.number, clip=r)

    src.close()

    # distribute logic
    sheets_doc = pymupdf.open()
    instruct_doc = pymupdf.open()

    for idx, page in enumerate(out):
        target_doc = sheets_doc if idx <= sheets_count else instruct_doc
        target_doc.insert_pdf(out, from_page=idx, to_page=idx)

    out.close()

    if needs_sheets: sheets_doc.save(sheets_path)
    if needs_instructions: instruct_doc.save(instructions_path)
    sheets_doc.close()
    instruct_doc.close()

def get_sheets_split_index(sheet_value: float) -> int:
    return 0 if sheet_value <= 3 else 1

def load_catalog(fname: str) -> dict[str, str]:
    with open(fname, 'r', encoding='utf-8') as sf:
        data = json.load(sf)
    return data

def search_catalog_with_uuid(catalog_data: dict[str, str], uuid: str) -> dict[str, str] | None:
    for category, products in catalog_data.items():
        for product in products:
            if product["sku_uuid"].lower() == uuid.lower():
                return product
    return None

def check_for_pdf_download(output_dirpath: str) -> tuple[bool, bool]:
    if os.path.exists(output_dirpath):
        curr_files: list[str] = os.listdir(output_dirpath)
        needs_sheets = "Sheets.pdf" in curr_files
        needs_instructions = "Instructions.pdf" in curr_files
        return (not needs_sheets, not needs_instructions)
    return (True, True)

def identify_page_structure():
    # identify whether the page has tips and tricks / instructions / metal sheets / mixed
    # returns sheets / instructions / mixed

    return

def crop_smartly():
    # somehow be able to identify 'METAL SHEETS' or where the bounding boxes of metal sheets end?
    return

def main():
    input_files: list[str] = get_input_files()
    for filepath in input_files:
        filename: str = os.path.splitext(os.path.basename(filepath))[0]
        vendor, uuid = [p.strip() for p in filename.split("_")]

        me_catalogue: dict[str, str] = load_catalog("me_product_catalogue.json")
        pc_catalogue: dict[str, str] = load_catalog("pc_product_catalogue.json")

        if vendor == "ME":
            output_dirpath: str = os.path.join(os.getcwd(), "manuals", "Metal Earth", uuid)
            if not os.path.exists(output_dirpath):
                os.makedirs(output_dirpath)

            needs_sheets, needs_instructs = check_for_pdf_download(output_dirpath)
            model_sheets_num: float = search_catalog_with_uuid(me_catalogue, uuid)["sheets"]
            split_idx: int = get_sheets_split_index(model_sheets_num)

            # print(f"output_dirpath: {output_dirpath}")
            # print(f"filename: {filename}")
            # print(f"model_sheets_num: {model_sheets_num}")
            # print(f"split_idx: {split_idx}")
            # print(f"needs_sheets: {needs_sheets}")
            # print(f"needs_instructs: {needs_instructs}")

            split_landscape_pdf(filepath, split_idx, output_dirpath, needs_sheets, needs_instructs)

        elif vendor == "PC":
            output_dirpath: str = os.path.join("manuals", "Piececool", uuid)
            


if __name__ == "__main__":
    main()