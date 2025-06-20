import re
import json
import os
import glob
import phonenumbers
import pyap
from typing import Set, Dict, Optional
from config import SERP_PREVIOUS_SEARCHES_PATH


class ContactExtractor:
    """
    A class to extract structured data like phone numbers, emails, and addresses
    from a block of unstructured text.

    The results of each extraction are cached to avoid re-calculating on
    subsequent calls.
    """

    def __init__(self, text: str):
        """
        Initializes the Extractor with the text to be analyzed.

        Args:
            text: The source string to extract information from.
        """
        self.text = text
        self._phones: Optional[Set[str]] = None
        self._emails: Optional[Set[str]] = None
        self._addresses: Optional[Set[str]] = None

    def extract_phone_numbers(self) -> Set[str]:
        """Finds all valid North American phone numbers."""
        if self._phones is not None:
            return self._phones

        found_numbers = set()
        for match in phonenumbers.PhoneNumberMatcher(self.text, "CA"):
            if phonenumbers.is_valid_number(match.number) and match.number.country_code == 1:
                formatted_number = phonenumbers.format_number(
                    match.number,
                    phonenumbers.PhoneNumberFormat.NATIONAL
                )
                found_numbers.add(formatted_number)

        self._phones = found_numbers
        return self._phones

    def extract_emails(self) -> Set[str]:
        """
        Finds all email addresses using a two-step find-and-validate process.
        """
        if self._emails is not None:
            return self._emails

        # Step 1: Use a broad, simple regex to find all potential email candidates.
        basic_email_finder = re.compile(r"[\w.\-+'_]+@[\w.\-]+\.\w+")

        # Step 2: Use a strict, comprehensive regex to validate each candidate.
        # This regex is intended for use on isolated strings (hence the ^ and $).
        validation_email_regex = re.compile(
            r"^(?P<local>[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*)"
            r"@"
            r"(?P<domain>(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$",
            re.IGNORECASE
        )

        potential_emails = basic_email_finder.findall(self.text)

        validated_emails = set()
        for email_candidate in potential_emails:
            match = validation_email_regex.fullmatch(email_candidate)
            if match:
                validated_emails.add(match.group(0).lower())

        self._emails = validated_emails
        return self._emails

    def extract_addresses(self) -> Set[str]:
        """Finds all Canadian or US addresses."""
        if self._addresses is not None:
            return self._addresses

        found_addresses = set()
        for address in pyap.parse(self.text, country='CA'):
            found_addresses.add(address.full_address)

        self._addresses = found_addresses
        return self._addresses

    def extract_all(self) -> Dict[str, Set[str]]:
        """
        Runs all extractors and returns a dictionary of all found data.

        Returns:
            A dictionary with keys 'phones', 'emails', and 'addresses'.
        """
        return {
            "phones": self.extract_phone_numbers(),
            "emails": self.extract_emails(),
            "addresses": self.extract_addresses()
        }


# --- The load_searches function remains the same ---
def load_searches() -> Dict[str, Dict[int, Dict[str, str]]]:
    """Load text from serp api json file"""
    json_files = glob.glob(os.path.join(SERP_PREVIOUS_SEARCHES_PATH, '*.json'))
    searches = {}
    for file in json_files:
        file_name = os.path.basename(file).split('.')[0]
        try:
            with open(file, 'r', encoding='utf-8') as f:
                processed_results = {}
                data = json.load(f)
                organic_results = data.get('organic_results', [])

                for organic_item in organic_results:
                    title = organic_item.get('title', '')
                    snippet = organic_item.get('snippet', '')
                    position = organic_item.get('position')

                    if position:
                        processed_results[position] = {
                            'title': title,
                            'snippet': snippet,
                        }

                if processed_results:
                    searches[file_name] = processed_results
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load or parse file {file_name}. Error: {e}")
            continue
    return searches

if __name__ == "__main__":
    debtor_searches = load_searches()
    for debtor_id, search_results in debtor_searches.items():
        print(f"Debtor ID: {debtor_id}")
        print("=" * 100)

        for position, result in search_results.items():
            title = result.get('title', '')
            snippet = result.get('snippet', '')

            # Combine title and snippet for analysis
            full_text = f"{title} {snippet}"

            # --- New, cleaner workflow using the Extractor class ---
            # 1. Create an instance of the Extractor for the combined text
            extractor = Extractor(full_text)

            # 2. Get all extracted data in one go
            all_data = extractor.extract_all()

            # 3. Print the results neatly
            print(f"   Position: {position}")
            print(f"   Title: {title}")

            if all_data["phones"]:
                print(f"   Phone Numbers: {all_data['phones']}")
            if all_data["emails"]:
                print(f"   Emails: {all_data['emails']}")
            if all_data["addresses"]:
                print(f"   Addresses: {all_data['addresses']}")

            print("-" * 50)
        print("\n")