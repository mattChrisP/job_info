import os
import requests
import json

from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils import cleanup_old_files
from ranking_utils import generate_ranking_and_save_cv
from email_utils import send_generated_cover_letters

load_dotenv()


JOB_API = os.getenv("JOB_API")


def fetch_jobs(search_title="Software"):
    """
    Fetch job listings from the API. Replace with your chosen API endpoint and parameters.
    """
    api_url = "https://api.apijobs.dev/v1/job/search"
    headers = {
        "apikey": JOB_API, 
        "Content-Type": "application/json"
    }

    last_month = datetime.now() - timedelta(days=30)

    # Format yesterday's date as "YYYY-MM-DDTHH:MM:SS.sssZ"
    formatted_last_month = last_month.strftime('%Y-%m-%dT00:00:00.000Z')

    payload = {
        "title": search_title,
        "status": "open",
        "country": "Singapore",
        "published_since": formatted_last_month,
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def save_jobs_to_file(jobs, filename):
    """
    Save job listings to a file.
    """
    with open(filename, "w") as file:
        json.dump(jobs, file, indent=4)
    print(f"Jobs saved to {filename}")

def main(query="Software"):
    """
    Main function to fetch jobs and save them to a daily file.
    """
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"jobs_{today}.json"
    # Check if today's file already exists
    if os.path.exists(filename):
        print(f"File for today already exists: {filename}")
        send_generated_cover_letters(cover_letters_file="generated_cover_letters.json", recipient_email="matthewchristopherpohadi@gmail.com")
        return 

    #cleanup yesterday file
    cleanup_old_files()

    # Fetch jobs
    print("Fetching jobs...")
    jobs = fetch_jobs(search_title=query)

    if jobs:
        # Save jobs to file
        save_jobs_to_file(jobs, filename)
    else:
        print("No jobs retrieved.")

    generate_ranking_and_save_cv()
    send_generated_cover_letters(cover_letters_file="generated_cover_letters.json", recipient_email="matthewchristopherpohadi@gmail.com")

main()