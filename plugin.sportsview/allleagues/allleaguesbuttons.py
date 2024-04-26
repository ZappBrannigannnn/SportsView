# imports
import xbmcaddon
import base64
import xbmcvfs
import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

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

        # Check if the folder to store league logos ("special://home/temp/sportsview/myleagues_buttons_cache/{self.sportname}/")
        self.leaguesbuttons_folder = xbmcvfs.translatePath(f"special://home/temp/sportsview/myleagues_buttons_cache/{self.sportname}/")
        # Create the temp folder if it doesn't exist
        os.makedirs(self.leaguesbuttons_folder, exist_ok=True)

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
            for index, league in enumerate(self.leagues_data):
                button_label = league['strLeague']
                button_image = league['strBadge']

                self.display_buttons(button_label, index)
                
        else:
            print("ALLLEAGUES LIST DOES NOT MATCH")
            # Write the self.leagues_list to the allsports_list_(sport).txt file
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(str(self.leagues_list))

            # Call the download_and_cache_image method
            self.new_or_cached()
# endregion

# BUTTONS
# region

    # Check if a new image needed or cached image is available
    # region
    def new_or_cached(self):
        # Define the path to the cache folder
        self.cache_folder = xbmcvfs.translatePath("special://home/temp/sportsview/myleagues_buttons_cache/" + self.sportname + "/")
        
        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cache_folder):
            xbmcvfs.mkdirs(self.cache_folder)
        
        # Get a list of filenames in the cache folder that end with ".png"
        cached_image_filenames = [filename for filename in os.listdir(self.cache_folder) if filename.endswith(".png")]

        # Remove the file extensions from the cached image filenames
        cached_leagues = [os.path.splitext(filename)[0] for filename in cached_image_filenames]

        # Calculate the new leagues by finding the difference between available leagues and cached leagues
        self.new_leagues = [league for league in self.leagues_list if league not in cached_leagues]

        # Handle the cached leagues first
        for league_name in cached_leagues:
            if league_name not in self.available_leagues:
                cached_image_path = os.path.join(self.cache_folder, f"{league_name}.png")

            else:
                self.create_cached_buttons(league_name)

        # Handle the new leagues
        for league_name in self.new_leagues:
            self.create_buttons(league_name)

        self.new_leagues.clear()
    # endregion