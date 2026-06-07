import urllib.request
import json
import os

def load_existing_indicators(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def test_fetch_usom_data():
    output_file = "usom-hourly.txt"
    
    existing_indicators = load_existing_indicators(output_file)
    combined_indicators = existing_indicators.copy()
    
    target_types = ["domain", "ip"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    total_new_added = 0
    MAX_TEST_PAGES = 300 # Sayfa Limiti
    
    for data_type in target_types:
        try:
            print(f"\n--- Testing {data_type.upper()} ---")
            url = f"https://siberguvenlik.gov.tr/api/address/index?type={data_type}&page=0"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                actual_page_count = data.get("pageCount", 0)
            
            pages_to_scan = min(actual_page_count, MAX_TEST_PAGES)
            print(f"Total pages in API: {actual_page_count}. Scanning first {pages_to_scan} pages.")
            
            for i in range(pages_to_scan):
                print(f"Fetching page {i}...")
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
                            if indicator not in existing_indicators:
                                combined_indicators.add(indicator)
                                total_new_added += 1
                                page_has_new_data = True
                    
                    if not page_has_new_data and len(existing_indicators) > 0:
                        print(f"-> Optimization hit at page {i}. Stopping.")
                        break
                        
        except Exception as e:
            print(f"Error ({data_type}): {e}")
            
    if total_new_added > 0:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for item in sorted(combined_indicators):
                    # Eğer item bir IP adresi DEĞİLSE (nokta barındırıyor ama harf de içeriyorsa domaindir)
                    # Veya daha garanti bir yöntem: USOM API'sinden gelen veride IP formatında olmayanlar için:
                    if any(c.isalpha() for c in item) and not item.startswith("||"):
                        # Domain ise ABP formatına çevir
                        f.write(f"||{item}^\n")
                    else:
                        # IP adresi ise olduğu gibi yaz (veya zaten formatlıysa dokunma)
                        f.write(f"{item}\n")
            print(f"\n[SUCCESS] Added {total_new_added} new items. Total items: {len(combined_indicators)}")
        except Exception as e:
            print(f"File write error: {e}")
    else:
        print("\n[INFO] No new items found.")

if __name__ == "__main__":
    test_fetch_usom_data()
