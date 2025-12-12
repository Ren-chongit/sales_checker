import pdfplumber
import re
import pandas as pd

def extract_pdf_data(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Check if page contains the target header
            if "科目別合計" not in page.extract_text():
                continue
                
            words = page.extract_words()
            # Group words by line (using 'top' coordinate)
            lines = {}
            for word in words:
                top = word['top']
                # Find existing line with similar top (tolerance of 3)
                found_line = False
                for line_top in lines:
                    if abs(line_top - top) < 3:
                        lines[line_top].append(word)
                        found_line = True
                        break
                if not found_line:
                    lines[top] = [word]
            
            # Sort lines by top (vertical order)
            sorted_line_tops = sorted(lines.keys())
            
            for top in sorted_line_tops:
                line_words = sorted(lines[top], key=lambda w: w['x0'])
                
                # Filter out header lines
                line_text = "".join([w['text'] for w in line_words])
                if "科目別合計" in line_text or "仕入先" in line_text or "原価" in line_text:
                    continue
                
                # Parse line words
                idx = 0
                while idx < len(line_words):
                    if idx >= len(line_words):
                        break
                        
                    code_word = line_words[idx]
                    code = code_word['text']
                    idx += 1
                    
                    name_parts = []
                    cost = None
                    
                    while idx < len(line_words):
                        word = line_words[idx]
                        text = word['text']
                        
                        is_number = re.match(r'^[\d,]+$', text)
                        
                        is_cost = False
                        if is_number:
                            if idx + 1 < len(line_words):
                                next_text = line_words[idx+1]['text']
                                if re.match(r'^[\d,]+$', next_text):
                                    is_cost = True
                        
                        if is_cost:
                            cost = int(text.replace(',', ''))
                            idx += 1 
                            if idx < len(line_words):
                                idx += 1
                            break
                        else:
                            name_parts.append(text)
                            idx += 1
                    
                    if cost is not None:
                        name = "".join(name_parts)
                        data.append({
                            'pdf_code': code,
                            'pdf_name': name,
                            'pdf_cost': cost
                        })
    return pd.DataFrame(data)

pdf_path = "c:/Users/R2401-022/Desktop/rpa/AI_dep/dj/sales_checker/data/20251211パッケージ・チョイス出発日精算データ抽出.pdf"
df = extract_pdf_data(pdf_path)
print(df.to_string())
