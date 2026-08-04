import re
import json

def clean_latex(text):
    """Removes LaTeX formatting commands and cleans up text."""
    if not text:
        return ""
    text = text.strip()
    
    # Strip superscript math annotations used in the tables
    text = text.replace('$^\\mathcal{H}$', '').replace('$^\\mathcal{P}$', '')
    text = text.replace('^\\mathcal{H}', '').replace('^\\mathcal{P}', '')
    
    # Remove footnotes and specific formatting tags
    text = re.sub(r'\\footnote\{[^}]+\}', '', text)
    text = text.replace('\\footnotesize', '')
    
    # Extract text from \citet{...}, \textbf{...}, \textit{...}
    text = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', text)
    
    # Remove lingering slashes, asterisk formats, brackets, and whitespace
    text = text.replace('~*', '*').replace('\\', '').replace('$', '')
    text = text.replace('{', '').replace('}', '').strip()
    
    # If the cell is explicitly an empty dash, format it as N/A
    if text == '--':
        return "--"
        
    return text

def parse_bib(filepath):
    """Parses a BibTeX file to extract URLs and DOIs for each citation key."""
    bib_links = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find {filepath}. Method links will be empty.")
        return bib_links

    entries = content.split('@')
    for entry in entries:
        if not entry.strip(): continue
        try:
            key = entry.split('{', 1)[1].split(',', 1)[0].strip()
        except IndexError:
            continue
            
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry)
        
        link = ""
        if url_match:
            link = url_match.group(1).strip()
        elif doi_match:
            doi = doi_match.group(1).strip()
            link = doi if doi.startswith('http') else f"https://doi.org/{doi}"
            
        if link:
            bib_links[key] = link
            
    return bib_links

def parse_tex(filepath, expected_cols, carry_over_indices):
    """
    Parses a LaTeX table, dynamically padding missing columns and carrying over 
    specific empty cells from previous rows.
    """
    data = []
    current_disease = "Unknown"
    last_values = [""] * expected_cols
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}. Make sure it is in the same folder.")
        return []

    for line in lines:
        if 'multicolumn' in line and 'textbf' in line:
            match = re.search(r'\\textbf\{([^}]+)\}', line)
            if match:
                current_disease = match.group(1).replace('\\&', '&')
            continue
        
        if any(x in line for x in ['toprule', 'bottomrule', 'midrule', 'hline', 'addlinespace', 'endfirsthead', 'endhead', 'endfoot', 'endlastfoot']):
            continue
            
        if '&' in line:
            raw_cells = line.split('\\\\')[0].split('&')
            cleaned_cells = [clean_latex(cell) for cell in raw_cells]
            
            # Pad the row if it's missing trailing ampersands
            while len(cleaned_cells) < expected_cols:
                cleaned_cells.append("")
                
            if not cleaned_cells or len(cleaned_cells) < 2: continue
            if "Method" in cleaned_cells[0]: continue
                
            # Apply carry-over logic only for specified columns
            for idx in range(expected_cols):
                if cleaned_cells[idx] == "" and idx in carry_over_indices:
                    cleaned_cells[idx] = last_values[idx]
                else:
                    last_values[idx] = cleaned_cells[idx]
            
            row_data = [current_disease] + cleaned_cells[:expected_cols]
            data.append(row_data)
            
    return data

def add_note(existing, new_note):
    """Helper to safely concatenate notes without duplicating."""
    if not new_note or new_note == "N/A": return existing
    if not existing or existing == "N/A": return new_note
    if new_note not in existing: return f"{existing} | {new_note}"
    return existing

def merge_data():
    print("Reading files...")
    bib_links = parse_bib("references.bib")
    
    # Defined specific indices to carry over blanks for each table type
    method_data = parse_tex("MethodTable.tex", expected_cols=6, carry_over_indices=[0, 1, 2, 4, 5])
    dice_data = parse_tex("DiceTable.tex", expected_cols=6, carry_over_indices=[0, 1, 2, 4])
    detection_data = parse_tex("DetectionTable.tex", expected_cols=7, carry_over_indices=[0, 1, 2, 5])

    merged_dict = {}

    def make_key(method, dataset):
        m = method.replace('*', '').strip().lower()
        d = dataset.strip().lower()
        return f"{m}__{d}"

    def get_clean_method_name(method):
        return method.replace('*', '').replace('~', '').strip()

    # 1. Base Data from MethodTable
    for row in method_data:
        disease, method, arch, train_ds, test_ds, modality, input_dim = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        key = make_key(method, test_ds)
        bib_key = get_clean_method_name(method)
        
        merged_dict[key] = {
            "disease": disease, "method": method, "url": bib_links.get(bib_key, ""), "arch": arch,
            "trainData": train_ds if train_ds else "N/A", 
            "testData": test_ds if test_ds else "N/A", 
            "modality": modality if modality else "N/A",
            "inputDim": input_dim if input_dim else "N/A",
            "dice": "--", "auroc": "--", "auprc": "--", 
            "threshStrategy": "N/A", "evalLevel": "N/A", "notes": ""
        }

    # 2. Merge Dice Metrics
    for row in dice_data:
        disease, method, arch, test_ds, dice, thresh, notes = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        key = make_key(method, test_ds)
        bib_key = get_clean_method_name(method)
        
        if key not in merged_dict:
            merged_dict[key] = {
                "disease": disease, "method": method, "url": bib_links.get(bib_key, ""), "arch": arch,
                "trainData": "N/A", "testData": test_ds, "modality": "N/A", "inputDim": "N/A",
                "dice": "N/A", "auroc": "N/A", "auprc": "N/A", 
                "threshStrategy": "N/A", "evalLevel": "N/A", "notes": ""
            }
        merged_dict[key]["dice"] = dice if dice else "--"
        if thresh: merged_dict[key]["threshStrategy"] = thresh
        merged_dict[key]["notes"] = add_note(merged_dict[key]["notes"], notes)

    # 3. Merge Detection Metrics
    for row in detection_data:
        disease, method, arch, test_ds, auroc, auprc, eval_lvl, notes = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
        key = make_key(method, test_ds)
        bib_key = get_clean_method_name(method)
        
        if key not in merged_dict:
            merged_dict[key] = {
                "disease": disease, "method": method, "url": bib_links.get(bib_key, ""), "arch": arch,
                "trainData": "N/A", "testData": test_ds, "modality": "N/A", "inputDim": "N/A",
                "dice": "N/A", "auroc": "N/A", "auprc": "N/A", 
                "threshStrategy": "N/A", "evalLevel": "N/A", "notes": ""
            }
        merged_dict[key]["auroc"] = auroc if auroc else "--"
        merged_dict[key]["auprc"] = auprc if auprc else "--"
        if eval_lvl: merged_dict[key]["evalLevel"] = eval_lvl
        merged_dict[key]["notes"] = add_note(merged_dict[key]["notes"], notes)

    merged_data_array = list(merged_dict.values())

    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data_array, f, indent=4)
        
    print(f"Success! {len(merged_data_array)} rows merged and saved to {output_file}.")

if __name__ == "__main__":
    merge_data()