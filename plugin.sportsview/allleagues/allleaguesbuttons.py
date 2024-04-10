# imports
import xbmcaddon
import base64
import xbmcvfs
import os
import requests

# CLASS AllLeaguesButtons
# region
class AllLeaguesButtons:
    def __init__(self, *args, **kwargs):
        self.sportname = str(kwargs.get('sportname'))
        print("allleaguesbuttons.py sportname", self.sportname)

        # API KEY
        # region
        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

        self.API_URL = f"https://www.thesportsdb.com/api/v1/json/{apikey}/search_all_leagues.php?s={self.sportname}"
        print("APIURLLLLLLLLLL", self.API_URL)
        # endregion
        

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
# endregion

# Method to create the allleagues_list.txt file if it doesn't exist
# region
    def file_exists(self):
        # Check if the allleagues_cache folder exists
        self.allleagues_folder = xbmcvfs.translatePath("special://home/temp/sportsview/allleagues_cache/")
        # Create the temp folder if it doesn't exist
        os.makedirs(self.allleagues_folder, exist_ok=True)  

        # Define the path for allleagues_list.txt
        self.file_path = xbmcvfs.translatePath("special://home/temp/sportsview/allleagues_cache/allleagues_list.txt")

        # Check if the file exists, and create it if it doesn't
        if not xbmcvfs.exists(self.file_path):
            with xbmcvfs.File(self.file_path, 'w') as file:
                pass  # This creates an empty file
        
        # launch the what_sports method
        self.what_leagues()
# endregion

# Get the list of all leagues from the API an add them to a temporary list
# region
    def what_leagues(self):
        self.league_data = []
        response = requests.get(self.API_URL)
        data = response.json()
        for league in data['leagues']:
            self.league_data.append(league)

#####################
        # Sort the league_data list by strSport*********
        self.league_data.sort(key=lambda x: x['strSport**************'])
#####################

        # Extract all of the strSport from the league_data list
        self.leagues_list = []
        for league in self.league_data:
            self.leagues_list.append(league['strSport**************'])

        # Call the compare_sports method
        self.compare_leagues()
# endregion