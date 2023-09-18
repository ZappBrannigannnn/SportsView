import requests

def get_sports():
    # Make API request to retrieve sports data
    api_url = "https://www.thesportsdb.com/api/v1/json/60130162/all_sports.php"
    response = requests.get(api_url)
    data = response.json()

    sports_data = []

    # Process the retrieved data and collect the sports data
    for sport in data['sports']:
        if 'strSportThumb' in sport:
            sports_data.append(sport)

    return sports_data

# Get the list of image URLs
allsportsdblist = get_sports()