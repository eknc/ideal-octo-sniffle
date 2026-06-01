import urllib.request
import json
import os

def load_existing_indicators(file_path):
    """Reads the existing text file and returns a set of indicators."""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def fetch_usom_data():
    output_file = "usom-domains.txt"
    
    # 1. Load what we already have
    existing_indicators = load_existing_indicators(output_file)
    combined_indicators = existing_indicators.copy()
    
    target_types = ["domain", "ip"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    total_new_added = 0
    
    for data_type in target_types:
        try:
            print(f"Checking for new {data_type} records...")
            
            # First, check page 0 to see total page count
            url = f"https://siberguvenlik.gov.tr/api/address/index?type={data_type}&page=0"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                page_count = data.get("pageCount", 0)
            
            # Loop through pages until we find only already-known data
            for i in range(page_count):
                page_url = f"https://siberguvenlik.gov.tr/api/address/index?type={data_type}&page={i}"
                page_req = urllib.request.Request(page_url, headers=headers)
                
                with urllib.request.urlopen(page_req) as p_res:
                    p_data = json.loads(p_res.read().decode())
                    models = p_data.get("models", [])
                    
                    if not models:
                        break
                        
                    page_has_new_data = False
                    for model in models:
                        indicator = model.get("url")
                        if indicator:
                            indicator = indicator.strip()
                            # If this item is NOT in our existing list, it's new!
                            if indicator not in existing_indicators:
                                combined_indicators.add(indicator)
                                total_new_added += 1
                                page_has_new_data = True
                    
                    # Optimization Trigger: 
                    # If this page had absolutely zero new items, it means we have 
                    # hit the historical data zone. No need to fetch remaining pages.
                    if not page_has_new_data:
                        print(f"-> Reached historical data zone for {data_type} at page {i}. Stopping pagination.")
                        break
                        
        except Exception as e:
            print(f"Error occurred while processing {data_type}: {e}")
            
    # 3. If new data was found, rewrite the file
    if total_new_added > 0:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for item in sorted(combined_indicators):
                    f.write(f"{item}\n")
            print(f"Successfully updated. Added {total_new_added} new items. Total items: {len(combined_indicators)}")
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print("No new threat indicators found. Repository is already up-to-date.")

if __name__ == "__main__":
    fetch_usom_data()
