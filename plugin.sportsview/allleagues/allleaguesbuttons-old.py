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
            self.download_and_cache_image()
# endregion

# Method to download and cache the images
# region
    def download_and_cache_image(self):
        # Define the fallback image path
        self.FALLBACK_IMAGE_PATH = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png")

        # Get the label and image for each button
        ################# LOOP 2 STARTS HERE #######################
        for index, sport in enumerate(self.leagues_data):
            sport_label = sport['strSport']
            button_label = sport['strLeague']
            button_image = sport['strLogo']
            
            # If the strSportThumb is empty then use the fallback image
            if button_image == "":
                button_image = self.FALLBACK_IMAGE_PATH

            # Download the image to the self.allsports_folder folder
            response = requests.get(button_image)
            if response.status_code == 200:
                league_image = self.leaguesbuttons_folder + ".png"
                with open(league_image, 'wb') as f:
                    f.write(response.content)
                    print(f"Sport image downloaded and cached: {league_image}")

                unfocused_image = self.leaguesbuttons_folder + "_unfocused" + ".png"
                with open(unfocused_image, 'wb') as f:
                    f.write(response.content)
                    print(f"Unfocused image downloaded and cached: {unfocused_image}")

                # Add the Label to the image using PIL
                image = Image.open(unfocused_image)

                # Call the grayscale method inside the loop
                self.grayscale(image, unfocused_image, button_label, index)

            else:
                print("Failed to download the image, using fallback image instead")
                # Use the local fallback image
                if os.path.exists(self.FALLBACK_IMAGE_PATH):
                    unfocused_image = self.allsports_folder + button_label + "_unfocused" + ".png"

                    # Copy the local fallback image to the cache folder
                    with open(unfocused_image, 'wb') as f:
                        with open(self.FALLBACK_IMAGE_PATH, 'rb') as local_f:
                            f.write(local_f.read())

                    print(f"Fallback image copied to cache: {unfocused_image}")

                    # Add the Label to the image using PIL
                    image = Image.open(unfocused_image)
                    draw = ImageDraw.Draw(image)

                    # Define the font specifics
                    self.font_path = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/resources/fonts/ariblk.ttf")
                    self.font_size = 180
                    font = ImageFont.truetype(self.font_path, self.font_size)

                    text = button_label
                    text_width, text_height = draw.textsize(text, font)
                    x = (image.width - text_width) // 2  # Center the text horizontally
                    y = image.height - text_height  # Position the text at the bottom

                    draw.text((x, y), text, fill=(255, 255, 255), font=font)

                    # Save the image with the added label
                    image.save(unfocused_image)

                    print(f"Label added to the fallback image: {unfocused_image}")

                    # Call the grayscale method inside the loop for the fallback image
                    self.grayscale(image, unfocused_image, button_label, index)

                else:
                    print("Fallback image file not found.")

# Method to use PIL to make a grayscale version of the image
# region
    ############################# STILL IN LOOP 2 ##########################
    def grayscale(self, image, unfocused_image, button_label, index):
        grayscale_image = ImageOps.grayscale(image)
        focused_image_rgb = grayscale_image.convert('RGB')

        border_color_rgb = (18, 101, 196)
        border_width = 15
        bordered_image = ImageOps.expand(focused_image_rgb, border=border_width, fill=border_color_rgb)

        # Save the bordered grayscale image with the correct filename
        focused_image_path = self.leaguesbuttons_folder + "_focused" + ".png"
        bordered_image.save(focused_image_path)

        self.display_buttons(button_label, index)
# endregion