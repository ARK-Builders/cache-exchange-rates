import os
import json
import requests
import time

def fetch_and_save_data(page_number):
    """
    Fetches data from the CoinGecko API for the given page number and saves it
    to a file in the coin_data folder.
    """
    data_dir = "coin_data"
    print(f"Fetching page {page_number}...")
    file_path = os.path.join(data_dir, f"coin_data_{page_number}.json")

    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Skipping download.")
        return
    else:
        # Pause to avoid API rate limits
        time.sleep(5)
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250&page={page_number}"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-2VJGW66iRL8Wu3NfPP8VgsWS",
        }
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Data for page {page_number} saved to {file_path}")
        except Exception as e:
            print(f"Error fetching data for page {page_number}: {e}")
            return

def fetch_all_data():
    """
    Ensures that all expected page files (1 to 69) exist by attempting to fetch
    any missing pages. Then merges all individual page data files into a single file.
    """
    output_file = "all_rates.json"
    data_dir = "coin_data"
    os.makedirs(data_dir, exist_ok=True)

    # Loop until the directory has 69 files (one for each page)
    while len(os.listdir(data_dir)) < 69:
        for n in range(1, 70):
            fetch_and_save_data(n)

    # Merge all page files into one list
    merged_data = []
    for n in range(1, 70):
        page_file = os.path.join(data_dir, f"coin_data_{n}.json")
        with open(page_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged_data.extend(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)
    print(f"Merged data saved to {output_file}")

def reduce_data(full_rates_file, crypto_file, output_file):
    """
    Reads the full data file and reduces its content by:
    
     - Keeping only certain keys: id, symbol, name, current_price.
     - Removing duplicate items.
     - Filtering out items whose id is not in the list provided from crypto.json.
     - Sorting the remaining items by their symbol.
     
    The final reduced data is written to the specified output file.
    """
    # Load the full rates data
    with open(full_rates_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_data = []
    keys_to_keep = ["id", "symbol", "name", "current_price"]

    symbols_set = set()

    with open(crypto_file, "r", encoding="utf-8") as f:
        crypto_data = json.load(f)

    crypto_ids = [key.lower() for key in crypto_data.keys()]

    # Keep only the desired keys and filter out duplicates as well as ones in the master crypto list
    for item in data:
        if item['symbol'] not in symbols_set:# and item['symbol'] in crypto_ids:
            item_filtered = {key: item[key] for key in keys_to_keep if key in item}
            new_data.append(item_filtered)
            symbols_set.add(item['symbol'])
        else:
            #print(f"Duplicate found: {item['symbol']}")
            continue

    print(f"Filtered data contains {len(new_data)} unique items.")

    # Filter out items where 'current_price' is None or missing
    filtered_data = [item for item in new_data if item.get('current_price') is not None]

    #sorted_data = sorted(filtered_data, key=lambda x: x['current_price'], reverse=True)

    # Save the reduced data to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f)
    print(f"Reduced data saved to {output_file}")

def main():
    # Step 1: Fetch and merge API data
    fetch_all_data()

    # Step 2: Reduce the merged data based on crypto.json content.
    # The merged file from the API is used as the full rates file.
    reduce_data("all_rates_from_API.json", "crypto.json", "crypto-rates-JW.json")

if __name__ == "__main__":
    main()
