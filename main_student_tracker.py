import requests
import csv
import os
import random
from datetime import datetime
from dotenv import load_dotenv

# Load the secrets from the .env file into your local environment
load_dotenv()

# CONFIGURATION
USERNAME = '974'
API_KEY = os.getenv('CONCORDIA_API_KEY')
CSV_FILE = 'library_stats.csv'
URL = 'https://opendata.concordia.ca/API/v1/library/occupancy/'

def get_last_count():
    """Reads the CSV to find the last recorded occupancy for estimation."""
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE, mode='r') as file:
        lines = list(csv.reader(file))
        if len(lines) <= 1: # Only headers exist
            return 0
        # Return the occupancy from the last row
        return int(lines[-1][1])

def run_tracker():
    # INITIALIZATION: Create CSV with headers if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Occupancy', 'Type'])

    current_minute = datetime.now().minute
    is_real_fetch = (current_minute % 10 == 0)

    try:
        if is_real_fetch:
            response = requests.get(URL, auth=(USERNAME, API_KEY))
            response.raise_for_status()
            data = response.json()
            
            count = max(0, int(float(data['Webster']['Occupancy'])))
            # Real timestamp from API looks like: 2026-02-25 08:25:00.000
            timestamp = data['Webster']['LastRecordTime']
            record_type = "Real"
        else:
            last_val = get_last_count()
            variance = random.uniform(0.95, 1.05)
            count = max(0, int(last_val * variance))
            
            # FIXED: Create a timestamp that matches the API exactly
            # format: YYYY-MM-DD HH:MM:SS.000
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.000')
            record_type = "Estimated"

        # Append to CSV
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, count, record_type])

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Success ({record_type}): {count} recorded.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")

if __name__ == "__main__":
    run_tracker()