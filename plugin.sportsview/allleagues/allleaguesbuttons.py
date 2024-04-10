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

# Method to create the allleagues_list_(sport).txt file if it doesn't exist
# region
    def file_exists(self):
        # Check if the allleagues_cache folder exists
        self.allleagues_folder = xbmcvfs.translatePath("special://home/temp/sportsview/allleagues_cache/")
        # Create the temp folder if it doesn't exist
        os.makedirs(self.allleagues_folder, exist_ok=True)  

        # Define the path for allleagues_list_(sport).txt
        self.file_path = xbmcvfs.translatePath(f"special://home/temp/sportsview/allleagues_cache/allleagues_list_{self.sportname}.txt")

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
        self.leagues_data = []
        response = requests.get(self.API_URL)
        data = response.json()
        for league in data['countries']:
            self.leagues_data.append(league)

        # Sort the leagues_data list by strLeague
        self.leagues_data.sort(key=lambda x: x['strLeague'])

        # Extract all of the strLeague from the leagues_data list
        self.leagues_list = []
        for league in self.leagues_data:
            self.leagues_list.append(league['strLeague'])
            print("LEAGUES IN ORDER", self.leagues_list)

        # Call the compare_leagues method
        self.compare_leagues()
# endregion

# Method to compare the allleagues_list_(sport).txt file with the self.sports_list
# region
    def compare_leagues(self):
        # Open the allleagues_list_(sport).txt file for reading
        with open(self.file_path, "r", encoding="utf-8") as file:
            # Read the contents of the file
            self.allleagues_list = file.read()
        # Compare the allleagues_list_(sport).txt file with the self.leagues_list
        if self.allleagues_list == str(self.leagues_list):
            print("ALLLEAGUES_LIST_(SPORT).TXT AND LEAGUES_LIST MATCH")

            ################## LOOP 1 STARTS HERE #######################
            for index, sport in enumerate(self.leagues_data):
                button_label = sport['strLeague']
                button_image = sport['strBadge']

                #self.display_buttons(button_label, button_image, index)
                self.display_buttons(button_label, index)
                
        else:
            print("ALLSPORTS LIST DOES NOT MATCH")
            # Write the self.sports_list to the allsports_list.txt file
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(str(self.leagues_list))

            # Call the download_and_cache_image method
            # self.download_and_cache_image()
# endregion