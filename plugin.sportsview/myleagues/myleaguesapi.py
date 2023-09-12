import requests

class MyLeaguesAPI:
    def __init__(self, sportname, leaguename):
        self.sportname = sportname
        self.leaguename = leaguename

    def get_all_leagues(self):
        url = 'https://www.thesportsdb.com/api/v1/json/60130162/all_leagues.php'
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
            url = f'https://www.thesportsdb.com/api/v1/json/60130162/lookupleague.php?id={league_id}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                league_info = data.get('leagues', [])
                return league_info[0] if league_info else None
            else:
                print('Failed to fetch league information.')
        return None
