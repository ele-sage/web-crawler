import os
import json
import pandas as pd
from typing import Dict, Optional
from dotenv import load_dotenv
from serpapi import GoogleSearch
from utils import load_previous_search

from config import (
    DEBTOR_CSV_PATH,
    SERP_PREVIOUS_SEARCHES_PATH,
    COUNTRY_CONFIG,
    STATES_BY_ID
)

load_dotenv()

SERP_API_KEY = os.getenv('SERP_API_KEY')


def load_current_debtor_info(debtor_id: int) -> Optional[pd.Series]:
    """Load debtor information from CSV file by ID."""
    try:
        df = pd.read_csv(DEBTOR_CSV_PATH, index_col='ID')
        if debtor_id not in df.index:
            return None
        return df.loc[debtor_id]
    except FileNotFoundError:
        print(f"Error: Debtor CSV file not found at {DEBTOR_CSV_PATH}")
        return None
    except Exception as e:
        print(f"Error loading debtor info: {e}")
        return None


def build_search_params(debtor_id: int) -> Optional[Dict]:
    """Build search parameters for Google search based on debtor information."""
    current_debtor_info = load_current_debtor_info(debtor_id)

    if current_debtor_info is None:
        return None

    # Validate required fields
    try:
        country_id = int(current_debtor_info['CountryID'])
        state_id = int(current_debtor_info['StateID'])
        last_name = str(current_debtor_info['LastName']).strip()
    except (ValueError, KeyError):
        return None

    # Check if country is supported and last name is valid
    if country_id not in [1, 2] or last_name in ['nan', '']:
        return None

    # Build location string
    country_config = COUNTRY_CONFIG[country_id]
    state = STATES_BY_ID.get(state_id, {})

    if state:
        location = f"{state.get('name', '')}, {country_config.get('name', '')}"
    else:
        # Default fallback location
        location = 'Quebec, Canada' if country_id == 2 else 'United States'

    params = {
        "engine": "google",
        "q": last_name,
        "location": location,
        "api_key": SERP_API_KEY,
        "gl": country_config['gl'],
        "hl": country_config['hl'],
        "google_domain": country_config['google_domain'],
    }

    return params

def save_search_results(debtor_id: int, search_results: Dict) -> bool:
    """Save search results to JSON file."""
    json_file = os.path.join(SERP_PREVIOUS_SEARCHES_PATH, f'{debtor_id}.json')

    # Ensure directory exists
    os.makedirs(SERP_PREVIOUS_SEARCHES_PATH, exist_ok=True)

    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(search_results, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving search results for debtor {debtor_id}: {e}")
        return False


def perform_google_search(debtor_id: int) -> Optional[Dict]:
    """Perform Google search for debtor information."""
    if not SERP_API_KEY:
        print("Error: SERP_API_KEY not found in environment variables")
        return None

    params = build_search_params(debtor_id)
    if not params:
        print(f"Unable to build search parameters for debtor {debtor_id}")
        return None

    try:
        search = GoogleSearch(params)
        search_results = search.get_dict()
        save_search_results(debtor_id, search_results)

        if not search_results or 'organic_results' not in search_results:
            print(f"No organic results found for debtor {debtor_id}")
            return None
        return search_results['organic_results']

    except Exception as e:
        print(f"Error performing Google search for debtor {debtor_id}: {e}")
        return None


def google_search(debtor_id: int) -> Optional[Dict]:
    """
    Main function to get Google search results for a debtor.
    Returns cached results if available, otherwise performs new search.
    """
    # Check for previous search results
    previous_search = load_previous_search(debtor_id)

    if previous_search and 'organic_results' in previous_search:
        print(previous_search['organic_results'])
        return previous_search['organic_results']

    return previous_search
    # Perform new search
    return perform_google_search(debtor_id)