from fetch_debtor import google_search
# import pandas as pd

if __name__ == "__main__":
    debtor_id = 303985
    search_results = google_search(debtor_id)
    print(search_results)