import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

__cur_dir__ = Path(__file__).parent


PROJECT_ROOT = __cur_dir__.parent

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

DEBTOR_CSV_PATH = os.path.join(PROJECT_ROOT, 'data/Debtors.csv')
SERP_PREVIOUS_SEARCHES_PATH = os.path.join(PROJECT_ROOT, 'data/serp_previous_searches')


COUNTRY_CONFIG = {
    1: {
        'code': 'US',
        'name': 'United States',
        'gl': 'us',
        'hl': 'en',
        'google_domain': 'google.com',
    },
    2: {
        'code': 'CA',
        'name': 'Canada',
        'gl': 'ca',
        'hl': 'en',
        'google_domain': 'google.ca',
    }
}

STATES_BY_ID = {
    1: {'name': 'New York', 'code': 'NY'},
    2: {'name': 'Puerto Rico', 'code': 'PR'},
    3: {'name': 'Virgin Islands', 'code': 'VI'},
    4: {'name': 'Massachusetts', 'code': 'MA'},
    5: {'name': 'Rhode Island', 'code': 'RI'},
    6: {'name': 'New Hampshire', 'code': 'NH'},
    7: {'name': 'Maine', 'code': 'ME'},
    8: {'name': 'Vermont', 'code': 'VT'},
    9: {'name': 'Connecticut', 'code': 'CT'},
    10: {'name': 'New Jersey', 'code': 'NJ'},
    11: {'name': 'Armed Forces - Europe/Africa/Canada', 'code': 'AE'},
    12: {'name': 'Pennsylvania', 'code': 'PA'},
    13: {'name': 'Kansas', 'code': 'KS'},
    14: {'name': 'Illinois', 'code': 'IL'},
    15: {'name': 'North Carolina', 'code': 'NC'},
    16: {'name': 'Virginia', 'code': 'VA'},
    17: {'name': 'Idaho', 'code': 'ID'},
    18: {'name': 'Texas', 'code': 'TX'},
    19: {'name': 'Alabama', 'code': 'AL'},
    20: {'name': 'Iowa', 'code': 'IA'},
    21: {'name': 'California', 'code': 'CA'},
    22: {'name': 'Maryland', 'code': 'MD'},
    23: {'name': 'South Carolina', 'code': 'SC'},
    24: {'name': 'Tennessee', 'code': 'TN'},
    25: {'name': 'Nebraska', 'code': 'NE'},
    26: {'name': 'Washington', 'code': 'WA'},
    27: {'name': 'Florida', 'code': 'FL'},
    28: {'name': 'Colorado', 'code': 'CO'},
    29: {'name': 'Arkansas', 'code': 'AR'},
    30: {'name': 'Michigan', 'code': 'MI'},
    31: {'name': 'Georgia', 'code': 'GA'},
    32: {'name': 'Oklahoma', 'code': 'OK'},
    33: {'name': 'Ohio', 'code': 'OH'},
    34: {'name': 'Missouri', 'code': 'MO'},
    35: {'name': 'Indiana', 'code': 'IN'},
    36: {'name': 'Minnesota', 'code': 'MN'},
    37: {'name': 'Wyoming', 'code': 'WY'},
    38: {'name': 'North Dakota', 'code': 'ND'},
    39: {'name': 'West Virginia', 'code': 'WV'},
    40: {'name': 'Oregon', 'code': 'OR'},
    41: {'name': 'Mississippi', 'code': 'MS'},
    42: {'name': 'Wisconsin', 'code': 'WI'},
    43: {'name': 'Kentucky', 'code': 'KY'},
    44: {'name': 'Arizona', 'code': 'AZ'},
    45: {'name': 'Delaware', 'code': 'DE'},
    46: {'name': 'Montana', 'code': 'MT'},
    47: {'name': 'Nevada', 'code': 'NV'},
    48: {'name': 'South Dakota', 'code': 'SD'},
    49: {'name': 'Louisiana', 'code': 'LA'},
    50: {'name': 'District of Columbia', 'code': 'DC'},
    51: {'name': 'Utah', 'code': 'UT'},
    52: {'name': 'New Mexico', 'code': 'NM'},
    53: {'name': 'Alaska', 'code': 'AK'},
    54: {'name': 'Armed Forces - Pacific', 'code': 'AP'},
    55: {'name': 'Hawaii', 'code': 'HI'},
    56: {'name': 'Guam', 'code': 'GU'},
    57: {'name': 'Northern Mariana Islands', 'code': 'MP'},
    58: {'name': 'Marshall Islands', 'code': 'MH'},
    59: {'name': 'Armed Forces - Americas', 'code': 'AA'},
    60: {'name': 'Palau', 'code': 'PW'},
    61: {'name': 'Federated States of Micronesia', 'code': 'FM'},
    62: {'name': 'American Samoa', 'code': 'AS'},
    63: {'name': 'Newfondland and Labrador', 'code': 'NL'},
    64: {'name': 'Nova Scotia', 'code': 'NS'},
    65: {'name': 'Prince Edward Island', 'code': 'PE'},
    66: {'name': 'Nouveau-Brunswick', 'code': 'NB'},
    67: {'name': 'Quebec', 'code': 'QC'},
    68: {'name': 'Ontario', 'code': 'ON'},
    69: {'name': 'Manitoba', 'code': 'MB'},
    70: {'name': 'Saskatchewan', 'code': 'SK'},
    71: {'name': 'Alberta', 'code': 'AB'},
    72: {'name': 'British Columbia', 'code': 'BC'},
    73: {'name': 'Nunavut', 'code': 'NU'},
    74: {'name': 'Northwest Territories', 'code': 'NT'},
    75: {'name': 'Yukon', 'code': 'YT'},
}