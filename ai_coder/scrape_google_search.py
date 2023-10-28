# filename: scrape_google_search.py
from googlesearch import search

# Define the query for the Google search
query = "AI startup ideas"

# Specify the number of results to scrape
num_results = 10

# Helper function to limit the number of search results
def get_top_results(query, num_results):
    results = []
    for result in search(query):
        results.append(result)
        if len(results) == num_results:
            break
    return results

# Get the top results
top_results = get_top_results(query, num_results)

# Print the top results
for i, result in enumerate(top_results):
    print(f"Result {i+1}: {result}")