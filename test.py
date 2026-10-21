"""
Program Purpose: for each landscape page in metal earth's default instructions pdf, split it into 2 portrait halves, and then distribute the sheet pages to the sheet pdf, and the instruction pages to the instructions pdf
"""

import os
import pymupdf

def get_input_files() -> list[str]:
    input_dirpath: str = os.path.join(os.getcwd(), "input")
    input_files: list[str] = [
        os.path.join(input_dirpath, file) for file in os.listdir(input_dirpath) 
        if file.endswith(".pdf") and 
        (file.startswith("ME") or file.startswith("PC") or file.startswith("UN"))
    ]
    return input_files

def split_landscape_pdf(input_path: str, sheets_count: int):
    base, _ = os.path.splitext(input_path)
    sheets_path: str = f"{base}_sheets.pdf"
    instructions_path: str = f"{base}_instructions.pdf"

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

    sheets_doc.save(sheets_path)
    instruct_doc.save(instructions_path)
    sheets_doc.close()
    instruct_doc.close()

def get_sheets_split_index(sheet_value: float) -> int:
    return 0 if sheet_value <= 3 else 1

def main():
    input_files: list[str] = get_input_files()
    first_file: str = input_files[0]
    model_sheets_num: float = 2.65
    split_idx = get_sheets_split_index(model_sheets_num)
    split_landscape_pdf(first_file, split_idx)    

    return

if __name__ == "__main__":
    main()
