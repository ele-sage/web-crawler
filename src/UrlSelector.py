import glob
import json
import os
import re
from typing import Dict, List, Set, Any, Optional
from utils import deduplicate_social_media_urls
from config import SERP_PREVIOUS_SEARCHES_PATH


class UrlSelector:
    """
    Selects relevant URLs from the 'organic_results' of a SERP API result
    based on a strict matching criteria.
    """

    COMPANY_STOP_WORDS = {'inc', 'ltd', 'llc', 'corp', 'co', 'group'}

    def __init__(self, serp_api_result: Dict[str, Any]):
        """
        Initializes the UrlSelector.
        Args:
            serp_api_result: The full JSON dictionary from a SERP API search.
        """
        self.result = serp_api_result
        self.company_name = self.result.get("search_parameters", {}).get("q", "")
        self.keywords = self._prepare_keywords()
        self._relevant_urls: Optional[List[Dict[str, Any]]] = None

    def _prepare_keywords(self) -> Set[str]:
        """Creates a set of significant keywords from the company name."""
        if not self.company_name:
            return set()
        name = re.sub(r'[^\w\s]', '', self.company_name.lower())
        keywords = {word for word in name.split() if word not in self.COMPANY_STOP_WORDS}
        return keywords

    def _are_all_keywords_present(self, text_to_check: str) -> bool:
        """Checks if every significant keyword is present in the text."""
        if not self.keywords:
            return False
        text_lower = text_to_check.lower()
        return all(keyword in text_lower for keyword in self.keywords)

    def _is_missing_check_ok(self, missing_list: Optional[List[str]]) -> bool:
        """
        Checks if the 'missing' array is acceptable.
        It's acceptable if it's empty or only contains company stop words.
        """
        if not missing_list:
            return True  # Empty or non-existent is OK.

        # Check if every word in the missing list is a stop word.
        return all(word.lower() in self.COMPANY_STOP_WORDS for word in missing_list)

    def select_relevant_urls(self) -> List[Dict[str, Any]]:
        """
        Extracts and filters relevant URLs using strict matching rules.
        """
        if self._relevant_urls is not None:
            return self._relevant_urls

        found_urls: List[Dict[str, Any]] = []

        for item in self.result.get("organic_results", []):
            title = item.get('title', '')
            missing_list = item.get('missing')

            # Apply the strict, two-part matching rule
            if self._is_missing_check_ok(missing_list) and self._are_all_keywords_present(title):
                url = item.get("link")
                if url:
                    found_urls.append({
                        "url": url,
                        "title": title,
                        "source": "organic",
                    })

        deduplicated_urls = deduplicate_social_media_urls(found_urls)

        self._relevant_urls = deduplicated_urls
        return self._relevant_urls


if __name__ == "__main__":
    json_files = glob.glob(os.path.join(SERP_PREVIOUS_SEARCHES_PATH, '*.json'))
    searches = {}
    for file in json_files:
        serp_data = json.load(open(file, 'r', encoding='utf-8'))
        url_selector = UrlSelector(serp_data)

        relevant_urls = url_selector.select_relevant_urls()

        print(f"Found {len(relevant_urls)} relevant URLs for '{url_selector.company_name}' (Strict Match & Deduplicated):")
        print("-" * 80)
        for url_info in relevant_urls:
            print(f"  URL: {url_info['url']}")
            print(f"  Title: {url_info['title']}")
            print("-" * 20)