import requests

class SportsAPI:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def get_sports_data(self):
        response = requests.get(self.api_url)
        data = response.json()

        sports_data = []
        for sport in data['sports']:
            if 'strSportThumb' in sport:
                sports_data.append(sport)

        sports_data.sort(key=lambda x: x['strSport'])
        return sports_data
