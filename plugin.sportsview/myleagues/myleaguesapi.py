import requests
import xbmcaddon
import base64

class MyLeaguesAPI:
    def __init__(self, sportname, leaguename):
        self.sportname = sportname
        self.leaguename = leaguename

        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        self.apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

    def get_all_leagues(self):
        url = f'https://www.thesportsdb.com/api/v1/json/{self.apikey}/all_leagues.php'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            leagues = data.get('leagues', [])
            return leagues
        else:
            print('Failed to fetch all leagues data.')
            return []

    def get_correct_league_id(self, leaguename):
        all_leagues = self.get_all_leagues()
        for league in all_leagues:
            league_sport = league.get('strSport', '').lower()
            league_name = league.get('strLeague', '').lower()
            if league_sport == self.sportname.lower() and league_name == leaguename.lower():
                return league.get('idLeague')
        print('League not found for sport:', self.sportname, 'and league name:', leaguename)
        return None

    def get_league_info(self, league_id):
        if league_id:
            url = f'https://www.thesportsdb.com/api/v1/json/{self.apikey}/lookupleague.php?id={league_id}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                league_info = data.get('leagues', [])
                return league_info[0] if league_info else None
            else:
                print('Failed to fetch league information.')
        return None
