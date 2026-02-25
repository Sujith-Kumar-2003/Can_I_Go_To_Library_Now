import requests
import csv
import os
import random
from datetime import datetime
from dotenv import load_dotenv # <-- Import the new library

# Load the secrets from the .env file into your local environment
load_dotenv() 

# CONFIGURATION
USERNAME = '974'

API_KEY = os.getenv('CONCORDIA_API_KEY') 
CSV_FILE = 'library_stats.csv'
URL = 'https://opendata.concordia.ca/API/v1/library/occupancy/'

def fetch_real_data():
    """Fetches real data from the API and writes to CSV."""
    response = requests.get(URL, auth=(USERNAME, API_KEY))
    response.raise_for_status() # error check
    data = response.json()

    # Extract Webster Data
    webster_count = int(float(data['Webster']['Occupancy']))
    timestamp = data['Webster']['LastRecordTime']

    # Clean the data
    clean_count = max(0, webster_count)

    # Append to CSV
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, clean_count])
        
    return clean_count

def save_estimated_data(last_count):
    """Generates an estimate +/- 5% of the last real count and writes to CSV."""
    # Generate a random multiplier between 0.95 (-5%) and 1.05 (+5%)
    variance = random.uniform(0.95, 1.05)
    estimated_count = int(last_count * variance)
    estimated_count = max(0, estimated_count) # Ensure it doesn't drop below 0
    
    # Generate our own timestamp since we aren't calling the API
    timestamp = datetime.now().isoformat(timespec='seconds')
    
    # Append to CSV
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, estimated_count])
        
    return estimated_count

# INITIALIZATION: Create CSV with headers if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Occupancy'])

# MAIN LOOP
print(f"--- Webster Library Tracker Active ---")
print(f"Target: {URL}")
print(f"Interval: 5 Minutes (Real API call every 10 mins, Estimate every 5 mins)")

last_real_count = 0
is_real_fetch = True # Toggle to switch between Real and Estimate

try:
    while True:
        current_time = datetime.now().strftime('%H:%M:%S')
        
        if is_real_fetch:
            try:
                last_real_count = fetch_real_data()
                print(f"[{current_time}] Success (Real API): {last_real_count} people recorded.")
            except Exception as e:
                print(f"[{current_time}] Error (Real API): {e}")
                # If API fails, last_real_count stays whatever it was previously
        else:
            estimated_count = save_estimated_data(last_real_count)
            print(f"[{current_time}] Success (Estimated): {estimated_count} people recorded.")
            
        # Toggle the flag for the next loop iteration
        is_real_fetch = not is_real_fetch
        
        # Sleep for 5 mins (300 seconds)
        time.sleep(300)
        
except KeyboardInterrupt:
    print("\nTracker stopped by user. The page will be updated soon!")