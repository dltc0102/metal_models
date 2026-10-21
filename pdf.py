"""
Program Purpose: splits the metal earth sheet + instruction pdf into two separate pdfs
"""

import os
import re
import pdfplumber
import pytesseract
from pytesseract import Output

# ME_ICX217 has 2.625 sheets // 1 page
# ME_PS2027 has 3 sheets // 1 page
# ME_PS2024 has 3.25 sheeets // 2 page
# ME_ICX258 has 4 sheets // 2 page
# ME_MMS011 has 1 sheet // 1 page
# ME_MMS465 has 4.5 sheets // 1.5 pages

def extract_letters(page):
    img = page.to_image(resolution=300).original
    data = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 11")
    
    heading_y = None
    for i, text in enumerate(data["text"]):
        if "metal" in text.lower() or "sheets" in text.lower():
            heading_y = data["top"][i] + data["height"][i]
            break
            
    if heading_y is None:
        return []

    search_top = heading_y + 20 
    letters_found = []
    
    for i, text in enumerate(data["text"]):
        text = text.strip()
        word_top = data["top"][i]
        
        if word_top > search_top:
            match = re.match(r"^([A-Z])[\.\)]?$", text)
            if match:
                letters_found.append({
                    "letter": match.group(1),
                    "x": data["left"][i],
                    "y": word_top
                })

    letters_found.sort(key=lambda item: (round(item["y"] / 10), item["x"]))
    
    best_sequence = []
    current_sequence = []
    
    for item in letters_found:
        letter = item["letter"]
        if not current_sequence:
            current_sequence.append(letter)
        elif ord(letter) == ord(current_sequence[-1]) + 1:
            current_sequence.append(letter)
        elif ord(letter) == ord(current_sequence[-1]):
            continue
        else:
            if len(current_sequence) > len(best_sequence):
                best_sequence = current_sequence
            current_sequence = [letter]
            
    if len(current_sequence) > len(best_sequence):
        best_sequence = current_sequence

    return best_sequence

def main():
    input_dirpath: str = os.path.join(os.getcwd(), "input")
    input_files: list[str] = os.listdir(input_dirpath)

    pytesseract.pytesseract.tesseract_cmd = r"D:\tesseract\tesseract.exe"
    for filepdf in input_files:
        filepdf_path: str = os.path.join(input_dirpath, filepdf)
        with pdfplumber.open(filepdf_path) as pdf:
            page = pdf.pages[0]
            letters = extract_letters(page)
            print(f"{filepdf}: Found sections {letters}")
            
    return

if __name__ == "__main__":
    main()