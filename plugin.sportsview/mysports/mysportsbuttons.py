# Imports
# region
import xbmcgui
import xbmcaddon
import xbmcvfs
import xbmc
import os
import io
import tempfile
import math
import hashlib
import urllib.request
import base64
from allsports.allsportsapi import SportsAPI
from myleagues.myleagueswindow import MyLeaguesWindow
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
# endregion

# CLASS MySportsButtons
# region

# API KEY STUFF
# region
# Your encryption key (keep it secret)
encryption_key = b'ZappBSportsVAPI6'

# Encrypted API key from settings.xml
addon = xbmcaddon.Addon()
encrypted_api_key = addon.getSetting('setting2')

apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

API_URL = f"https://www.thesportsdb.com/api/v1/json/{apikey}/all_sports.php"
# endregion

class MySportsButtons:
    def __init__(self, parent_window, window_manager):  # Pass the window_manager instance as an argument
        self.parent_window = parent_window
        self.buttons = []
        self.button_start_percent = 45
        self.sports_data = []
        self.sports_folders = []

        self.focused_index = -1  # Initialize focused_index attribute
        self.available_sports = []  # Initialize available_sports attribute

        # Calculate the button size based on the user's screen size (adjust the multiplier as needed)
        self.window_height = self.parent_window.getHeight()
        self.window_width = self.parent_window.getWidth()
        self.button_width = int(self.window_width * 0.5)  # 50% of screen width

        # Calculate the vertical offset for the starting position of the buttons
        self.buttons_start_y = int(self.window_height * (self.button_start_percent * 0.01))
        self.button_height = int((self.window_height - self.button_start_percent) / 9) # no idea why 9 works but it does

        self.image_height = int(((100 - self.button_start_percent)*0.01)*self.window_height)

        self.temp_folder = xbmcvfs.translatePath("special://home/temp/sportsview/my_sports_buttons_cache/")  # Temporary folder for cached images
        os.makedirs(self.temp_folder, exist_ok=True)  # Create the temp folder if it doesn't exist

        self.allsports_folder = xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/")
# endregion

# GET THE AVAILABLE SPORTS IN THE SPORTS FOLDER
# region
    def get_sports_folders(self):

        addon = xbmcaddon.Addon()
        sports_folder_path = addon.getSetting('setting1')

        # Check if the SMB share exists using xbmcvfs.
        if xbmcvfs.exists(sports_folder_path):
            print("SPORTS PATH EXISTS")
            sports_items = xbmcvfs.listdir(sports_folder_path)
            # Flatten the list and remove the extra nesting
            self.sports_folders = [item for sublist in sports_items for item in sublist if not item.startswith(".")]
                    
            # Call the method to check if the sport buttons have been cached
            self.check_button_cache()

            return self.sports_folders

        else:
            print("SPORTS PATH DOES NOT EXIST")
        return []
# endregion

# Check if the buttons have been cached
# region
    def check_button_cache(self):
        # Check if there is a cached button for each sport in self.sports_folders
        ### LOOP 1 START ###
        for sport in self.sports_folders:
            button_image_path = os.path.join(self.temp_folder, f"{sport}_unfocused.png")
            if os.path.exists(button_image_path):
                print("CACHED BUTTON FOUND")
                # Call the method to display the buttons
                self.display_buttons(sport)
            else:
                print("CACHED BUTTON NOT FOUND")
                # Call the method to create and cache the button
                self.generate_custom_buttons(sport)
# endregion

# Generate custom button
# region
    ### STILL IN LOOP 1 ###
    def generate_custom_buttons(self, sport):
        self.focused_button_image_path = os.path.join(self.temp_folder, f"{sport}_focused.png")
        self.unfocused_button_image_path = os.path.join(self.temp_folder, f"{sport}_unfocused.png")

        if not os.path.exists(self.focused_button_image_path) or not os.path.exists(self.unfocused_button_image_path):
            # Create blank images with white backgrounds for both focused and unfocused buttons
            focused_button_image = Image.new("RGBA", (self.button_width, self.button_height), color=(0, 0, 0, 50))
            unfocused_button_image = Image.new("RGBA", (self.button_width, self.button_height), color=(0, 0, 0, 0))

            # Create drawing objects for both buttons
            focused_draw = ImageDraw.Draw(focused_button_image)
            unfocused_draw = ImageDraw.Draw(unfocused_button_image)

            # Choose a font (You can replace this with the path to your custom font file)
            custom_font_path = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/resources/fonts/ariblk.ttf")
            desired_font_size = 40
            font = ImageFont.truetype(custom_font_path, desired_font_size)

            # Calculate the size of the text
            text_width, text_height = focused_draw.textsize(sport, font)

            # Calculate the position to center the text on the buttons
            text_x = (self.button_width - text_width) // 2
            text_y = (self.button_height - text_height) // 2

            # Draw the text on both buttons
            focused_draw.text((text_x, text_y), sport, fill=(255, 255, 255, 255), font=font)
            unfocused_draw.text((text_x, text_y), sport, fill=(255, 255, 255, 255), font=font)

            # Save the button images to the temp folder
            focused_button_image.save(self.focused_button_image_path)
            unfocused_button_image.save(self.unfocused_button_image_path)

        # Call the method to display the buttons
        self.display_buttons(sport)

# endregion

# Display the custom buttons
# region
    ### STILL IN LOOP 1 ###
    def display_buttons(self, sport):
        self.available_sports = self.sports_folders
        self.first_visible_index = -1

        # Calculate the number of buttons that can fit on the screen vertically
        max_buttons_vertical = math.floor((self.window_height - self.button_start_percent * 0.01 * self.window_height) / self.button_height)
        num_buttons_to_display = min(max_buttons_vertical, len(self.available_sports))

        # Calculate the vertical offset for the starting position of the buttons
        self.buttons_start_y = int(self.window_height * (self.button_start_percent * 0.01))

        # Calculate the visible range of buttons on the screen
        start_visible_index = max(self.first_visible_index, 0)
        end_visible_index = min(start_visible_index + num_buttons_to_display - 1, len(self.available_sports) - 1)

        # Create buttons for each available sport (for the custom buttons to be made from)
        for index, sport in enumerate(self.available_sports):

            self.focused_button_image_path = os.path.join(self.temp_folder, f"{sport}_focused.png")
            self.unfocused_button_image_path = os.path.join(self.temp_folder, f"{sport}_unfocused.png")   

            # Calculate the Y position for the button based on its index
            y_position = self.buttons_start_y + self.button_height * index

            # Check if the button is within the visible range
            is_visible = start_visible_index <= index <= end_visible_index

            # Create a clickable button with custom font images
            button = xbmcgui.ControlButton(
                x=0, 
                y=y_position,
                width=self.button_width, 
                height=self.button_height,
                label="",
                focusTexture=self.focused_button_image_path,
                noFocusTexture=self.unfocused_button_image_path
            )

            # Add the button to the window
            self.buttons.append(button)
            self.parent_window.addControl(button)

        # Set the focus on the first button (index 0)
        if self.buttons:
            first_button_id = self.buttons[0].getId()
            self.parent_window.setFocusId(first_button_id)
            self.focused_index = 0  # Set the focused index to 0 for the initial focus

        # Call visible_buttons_info at the end of display_buttons
        self.visible_buttons_info()

        return
# endregion

# MOVEFOCUS
# region
    def moveFocus(self, x, y):
        new_index = self.focused_index + y

        # Check if the down button is pressed and the new index exceeds the last available sport index
        if y > 0 and new_index >= len(self.available_sports):
            # Do nothing and return without changing the focus
            return

        # Check if the up button is pressed and the new index goes below zero
        elif y < 0 and new_index < 0:
            # Do nothing and return without changing the focus
            return

        # Check if the focused button is the last visible index and the down button is pressed
        elif y > 0 and self.focused_index == self.last_visible_index:
            self.scrollUp()

        # Check if the focused button is the first visible index and the up button is pressed
        elif y < 0 and self.focused_index == self.first_visible_index:
            self.scrollDown()

        # Update the focused index after checking for scrolling
        self.focused_index = new_index

        # Set the focus on the new focused button
        self.parent_window.setFocusId(self.buttons[self.focused_index].getId())

        # Add the focus to the new focused button
        focused_label_text = self.buttons[self.focused_index].getLabel()
        self.buttons[self.focused_index].setLabel(focused_label_text)

        # Call visible_buttons_info at the end of moveFocus
        self.display_image()
# endregion

# Visible buttons
# region
    def visible_buttons_info(self):
        # Calculate the number of buttons that can fit on the screen vertically
        max_buttons_vertical = math.floor((self.window_height - self.button_start_percent * 0.01 * self.window_height) / self.button_height)
        num_buttons_to_display = min(max_buttons_vertical, len(self.available_sports))

        # Calculate the vertical offset for the starting position of the buttons
        buttons_initial_y = int(self.window_height * (self.button_start_percent * 0.01))

        # Calculate the index of the first visible button, considering the vertical offset
        self.first_visible_index = -1
        for i, button in enumerate(self.buttons):
            if button.getY() >= buttons_initial_y:
                self.first_visible_index = i
                break

        # Calculate the index of the last visible button, considering the vertical offset
        self.last_visible_index = min(len(self.available_sports) - 1, self.first_visible_index + num_buttons_to_display - 1)

        # Calculate the number of buttons currently visible on the screen
        num_visible_buttons = self.last_visible_index - self.first_visible_index + 1
# endregion

# Scroll up the buttons by one button height
# region
    def scrollUp(self):
        for button in self.buttons:
            new_y_position = button.getY() - self.button_height
            if self.buttons_start_y <= new_y_position < self.window_height:
                button.setVisible(True)
            else:
                button.setVisible(False)
            button.setPosition(button.getX(), new_y_position)

        self.first_visible_index -= 1
        self.last_visible_index -= 1

        # Call visible_buttons_info after scrolling up
        self.visible_buttons_info()
# endregion

# Scroll down the buttons by one button height
# region
    def scrollDown(self):
        for button in self.buttons:
            new_y_position = button.getY() + self.button_height
            if self.buttons_start_y <= new_y_position < self.window_height:
                button.setVisible(True)
            else:
                button.setVisible(False)
            button.setPosition(button.getX(), new_y_position)

        self.first_visible_index += 1
        self.last_visible_index += 1

        # Call visible_buttons_info after scrolling down
        self.visible_buttons_info()
# endregion

####### ALL SPORTS METHODS #######
# region
# Method to create the allsports_list.txt file if it doesn't exist
# region
    def file_exists(self):
        # Check if the allsports_cache folder exists
        self.allsports_folder = xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/")
        # Create the temp folder if it doesn't exist
        os.makedirs(self.allsports_folder, exist_ok=True)  

        # Define the path for allsports_list.txt
        self.file_path = xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/allsports_list.txt")

        # Check if the file exists, and create it if it doesn't
        if not xbmcvfs.exists(self.file_path):
            with xbmcvfs.File(self.file_path, 'w') as file:
                pass  # This creates an empty file
        
        # Run the file_exists method in a background thread
        self.what_sports()
# endregion
   
# Get the list of all sports from the API an add them to a temporary list
# region
    def what_sports(self):
        self.sports_data = []
        response = requests.get(API_URL)
        data = response.json()
        for sport in data['sports']:
            self.sports_data.append(sport)

        # Sort the sports_data list by strSport
        self.sports_data.sort(key=lambda x: x['strSport'])

        # Extract all of the strSport from the sports_data list
        self.sports_list = []
        for sport in self.sports_data:
            self.sports_list.append(sport['strSport'])

        # Call the compare_sports method
        self.compare_sports()
# endregion
       
# Method to compare the allsports_list.txt file with the self.sports_list
# region
    def compare_sports(self):
        # Open the allsports_list.txt file for reading
        with open(self.file_path, "r", encoding="utf-8") as file:
            # Read the contents of the file
            self.allsports_list = file.read()
        # Compare the allsports_list.txt file with the self.sports_list
        if self.allsports_list == str(self.sports_list):
            print("ALLSPORTS_LIST.TXT AND SPORTS_LIST MATCH")

            ################## LOOP 1 STARTS HERE #######################
            for index, sport in enumerate(self.sports_data):
                button_label = sport['strSport']
                button_image = sport['strSportThumb']
        else:
            print("ALLSPORTS LIST DOES NOT MATCH")
            # Write the self.sports_list to the allsports_list.txt file
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(str(self.sports_list))

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
        for index, sport in enumerate(self.sports_data):
            button_label = sport['strSport']
            button_image = sport['strSportThumb']
            
            # If the strSportThumb is empty then use the fallback image
            if button_image == "":
                button_image = self.FALLBACK_IMAGE_PATH

            # Download the image to the self.allsports_folder folder
            response = requests.get(button_image)
            if response.status_code == 200:
                sport_image = self.allsports_folder + button_label + ".png"
                with open(sport_image, 'wb') as f:
                    f.write(response.content)
                    print(f"Sport image downloaded and cached: {sport_image}")

                unfocused_image = self.allsports_folder + button_label + "_unfocused" + ".png"
                with open(unfocused_image, 'wb') as f:
                    f.write(response.content)
                    print(f"Unfocused image downloaded and cached: {unfocused_image}")

                # Add the Label to the image using PIL
                image = Image.open(unfocused_image)
                draw = ImageDraw.Draw(image)

                # Define the font specifics
                self.font_path = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/resources/fonts/ariblk.ttf")
                self.font_size = 20
                font = ImageFont.truetype(self.font_path, self.font_size)

                text = button_label
                text_width, text_height = draw.textsize(text, font)
                x = (image.width - text_width) // 2  # Center the text horizontally
                y = image.height - text_height  # Position the text at the bottom

                draw.text((x, y), text, fill=(255, 255, 255), font=font)

                # Save the image with the added label
                image.save(unfocused_image)

                print(f"Label added to the image: {unfocused_image}")

                # Call the grayscale method inside the loop
                self.grayscale(image, unfocused_image, button_label, index)

            else:
                print("Failed to download the image, using fallback image instead")
                # Use the local fallback image
                if os.path.exists(self.FALLBACK_IMAGE_PATH):
                    unfocused_image = self.allsports_folder + button_label + "_unfocused" + ".png"
                    sport_image = self.allsports_folder + button_label + ".png"

                    with open(sport_image, 'wb') as f:
                        with open(self.FALLBACK_IMAGE_PATH, 'rb') as local_f:
                            f.write(local_f.read())

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
                    self.font_size = 100
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
# endregion

# Method to use PIL to make a grayscale version of the image
# region
    ############################# STILL IN LOOP 2 ##########################
    def grayscale(self, image, unfocused_image, button_label, index):
        grayscale_image = ImageOps.grayscale(image)
        focused_image_rgb = grayscale_image.convert('RGB')

        border_color_rgb = (18, 101, 196)
        border_width = 10
        bordered_image = ImageOps.expand(focused_image_rgb, border=border_width, fill=border_color_rgb)

        # Save the bordered grayscale image with the correct filename
        focused_image_path = self.allsports_folder + button_label + "_focused" + ".png"
        bordered_image.save(focused_image_path)
# endregion
####### ALL SPORTS METHODS CLOSE #######
# endregion

# Method to display image
# region
    def display_image(self):
        # Get the sport of the focused button
        sport = self.available_sports[self.focused_index]
        
        image_path = os.path.join(self.allsports_folder, sport + ".png")

        # Check if the image file exists before using it
        if os.path.exists(image_path):
            print("IMAGE EXISTS")
        else:
            print(f"The image for {sport} does not exist.")

        # Create a clickable button with custom font images
        button = xbmcgui.ControlButton(
            x=self.button_width, 
            y=self.buttons_start_y,
            width=self.button_width, 
            height=self.image_height,
            label="",
            focusTexture=image_path,
            noFocusTexture=image_path
            )   

        # Add the button to the window
        self.buttons.append(button)
        self.parent_window.addControl(button)
# endregion

# Method for launching My Leagues window
# region
    def launch_my_leagues_window(self):
        from window_manager import WindowManager

        # Create an instance of the WindowManager class
        self.window_manager = WindowManager()

        # Call the show_my_leagues_page method of the existing WindowManager instance
        self.window_manager.show_my_leagues_page(sportname=self.sportname)
# endregion

# onClick
# region
    def onClick(self, focused_button_id, sport):
        print("SPORT", sport)

        """
        # Find the index of the clicked button based on its controlId
        clicked_index = None
        for index, button in enumerate(self.buttons):
            if button.getId() == controlId:
                clicked_index = index
                break

        # Check if a valid button is clicked
        #if clicked_index is not None:
        # Get the sport data for the clicked button
        clicked_sport = self.available_sports[clicked_index]
        self.sportname = clicked_sport.get('strSport', 'N/A')
"""
        self.sportname = sport
        # Launch My Leagues window
        self.launch_my_leagues_window()
# endregion
