import os
from typing import Set, Dict, Optional
from config import SERP_PREVIOUS_SEARCHES_PATH
from utils import find_input_files, load_json_file, select_relevant_sites
from ContactExtractor import ContactExtractor

# return title and snippet given a position in organic_result
get_organic_result_info = lambda x, i: x['organic_results'][i].get('title', '') + ' ' + x['organic_results'][i].get('snippet', '')
get_organic_result_link = lambda x, i: x['organic_results'][i].get('link', '')

def get_contact_info(search: Dict) -> Dict[str, Set[str]]:
    full_text = ''
    for position in search['relevant_sites']:
        full_text += get_organic_result_info(search, position - 1) + ' '
    return ContactExtractor(full_text).extract_all()

if __name__ == "__main__":
    json_files = find_input_files(SERP_PREVIOUS_SEARCHES_PATH)
    searches: Dict = {}

    for json_file in json_files:
        file_name = os.path.basename(json_file).split('.')[0]
        serp_data = load_json_file(json_file)
        searches[file_name] = serp_data
        searches[file_name]['relevant_sites'] = select_relevant_sites(serp_data)
        searches[file_name]['contact_info'] = get_contact_info(searches[file_name])

        searches[file_name]['relevant_links'] = []
        for position in searches[file_name]['relevant_sites']:
            searches[file_name]['relevant_links'].append(get_organic_result_link(searches[file_name], position - 1))

    for search_id, search in searches.items():
        print(f"Search ID: {search_id}")
        print("=" * 100)
        print(f"   Search Query:: {search['search_parameters']['q']}")
        print(f"   Relevant Links ({len(search['relevant_links'])}): {search['relevant_links']}")
        print(f"   Contact Info: {search['contact_info']}")
        print("-" * 50)