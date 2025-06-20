import re
import os
import json
import glob
from typing import Dict, List, Set, Optional, Any
from urllib.parse import urlparse

from config import SERP_PREVIOUS_SEARCHES_PATH

COMPANY_STOP_WORDS = {'inc', 'ltd', 'llc', 'corp', 'co', 'group'}
SOCIAL_MEDIA_DOMAINS = {
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "pinterest.com", "tiktok.com", "snapchat.com", "reddit.com",
}


def find_input_files(input_directory, file_extension: str = None) -> List[str]:
    """Finds and returns a sorted list of files in the input directory."""
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' not found.")
        return []

    file_extension = '*' if file_extension is None else f"*.{file_extension}"
    files = sorted(glob.glob(os.path.join(input_directory, file_extension)))

    if not files:
        print(f"No files found in directory '{input_directory}'.")
        return []

    print(f"Found {len(files)} files in '{input_directory}'.")
    return files


def ensure_directory_exists(filepath_or_dir):
    """Checks if the directory for a file/dir exists, creates it if not."""
    directory = filepath_or_dir if os.path.isdir(filepath_or_dir) else os.path.dirname(filepath_or_dir)
    if directory and not os.path.exists(directory):
        print(f"Creating directory: '{directory}'")
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")


def load_json_file(file_path: str) -> Optional[Dict]:
    """Load json file"""
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return None

def deduplicate_social_media_urls(url_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters a list to keep only the best URL per social media domain."""
    social_media_groups: Dict[str, List[Dict[str, Any]]] = {}
    other_urls: List[Dict[str, Any]] = []

    for url_info in url_list:
        domain = urlparse(url_info['url']).netloc.replace("www.", "")
        if domain in SOCIAL_MEDIA_DOMAINS:
            social_media_groups.setdefault(domain, []).append(url_info)
        else:
            other_urls.append(url_info)

    final_list = other_urls
    for domain, group in social_media_groups.items():
        best_url = sorted(group, key=lambda x: len(x['url']))[0]
        final_list.append(best_url)

    return final_list


def _are_all_keywords_present(text_to_check: str, keywords: Set[str]) -> bool:
    if not keywords:
        return False
    text_lower = text_to_check.lower()
    return all(keyword in text_lower for keyword in keywords)


def _is_missing_check_ok(missing_list: Optional[List[str]]) -> bool:
    if not missing_list:
        return True
    return all(word.lower() in COMPANY_STOP_WORDS for word in missing_list)


def select_relevant_sites(serp_api_result: Dict[str, Any]) -> List[int]:
    """
    Selects relevant site positions from the 'organic_results' of a SERP API result.

    Args:
        serp_api_result: The full JSON dictionary from a SERP API search.

    Returns:
        A list of integer positions of the relevant and deduplicated organic results.
    """
    relevant_items: List[Dict[str, Any]] = []
    keywords = set()

    query = serp_api_result.get("search_parameters", {}).get("q", "")

    if query:
        name = re.sub(r'[^\w\s]', '', query.lower())
        keywords = {word for word in name.split() if word not in COMPANY_STOP_WORDS}

    # 1. Find all organic result items that match the strict criteria
    for item in serp_api_result.get("organic_results", []):
        title = item.get('title', '')
        missing_list = item.get('missing')

        if _is_missing_check_ok(missing_list) and _are_all_keywords_present(title, keywords):
            if item.get("link") and item.get("position"):
                relevant_items.append(item)

    return [item['position'] for item in relevant_items]