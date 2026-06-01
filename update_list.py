import urllib.request
import json
import os

def fetch_usom_data():
    # We will collect both domains and IPs in a single set to avoid duplicates
    combined_indicators = set()
    
    # Types to fetch from USOM API
    target_types = ["domain", "ip"]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for data_type in target_types:
        try:
            print(f"Fetching {data_type} data from USOM...")
            # First page to get total page count for this type
            url = f"https://siberguvenlik.gov.tr/api/address/index?type={data_type}&page=0"
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                page_count = data.get("pageCount", 0)
            
            # Loop through all pages for the current type
            for i in range(page_count):
                page_url = f"https://siberguvenlik.gov.tr/api/address/index?type={data_type}&page={i}"
                page_req = urllib.request.Request(page_url, headers=headers)
                
                with urllib.request.urlopen(page_req) as p_res:
                    p_data = json.loads(p_res.read().decode())
                    for model in p_data.get("models", []):
                        indicator = model.get("url")
                        if indicator:
                            # Clean whitespace and add to set
                            combined_indicators.add(indicator.strip())
                            
            print(f"Completed fetching {data_type}. Current total unique items: {len(combined_indicators)}")
            
        except Exception as e:
            print(f"Error occurred while fetching {data_type}: {e}")
            
    # Write all combined data to the output file
    output_file = "usom-domains.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for item in sorted(combined_indicators):
                f.write(f"{item}\n")
        print(f"Successfully wrote {len(combined_indicators)} items to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    fetch_usom_data()
