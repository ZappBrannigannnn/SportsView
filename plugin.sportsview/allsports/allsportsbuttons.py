# IMPORTS
# region
import xbmcvfs
import os
import xbmcaddon
import base64
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import xbmcgui
import xbmc
# endregion

# API KEY
# region
# Your encryption key (keep it secret)
encryption_key = b'ZappBSportsVAPI6'

# Encrypted API key from settings.xml
addon = xbmcaddon.Addon()
encrypted_api_key = addon.getSetting('setting2')

apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

API_URL = f"https://www.thesportsdb.com/api/v1/json/{apikey}/all_sports.php"
# endregion

# CLASS AllSportsButtons
# region
class AllSportsButtons:
    def __init__(self, *args, **kwargs):

        ######################################################################################################################################
        self.buttons = [] # Initialize a list of button
        self.button_id_to_sport_name = {}  # Dictionary to map button IDs to sport names
        ######################################################################################################################################
    
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
# endregion

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
        
        # launch the what_sports method
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

                #self.display_buttons(button_label, button_image, index)
                self.display_buttons(button_label, index)
                
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
                self.font_size = 120
                font = ImageFont.truetype(self.font_path, self.font_size)

                text = button_label

                text_width, text_height = draw.textsize(text, font)
                x = (image.width - text_width) // 2  # Center the text horizontally
                y = (image.height - text_height) //2  # Center the text vertically

                # Draw the black border around the text
                border_size = 8  # Adjust the border size as needed
                for i in range(-border_size, border_size + 1):
                    for j in range(-border_size, border_size + 1):
                        draw.text((x + i, y + j), text, fill=(44, 44, 44), font=font)

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
        focused_image_path = self.allsports_folder + button_label + "_focused" + ".png"
        bordered_image.save(focused_image_path)

        self.display_buttons(button_label, index)
# endregion

# Method to display the buttons
# region
################### STILL IN THE LOOP 1 and 2 #####################
    def display_buttons(self, button_label, index):

        vert_gap_size = 50
        self.horiz_gap_size = 10

        self.num_buttons = len(self.sports_data)
        self.num_columns = 4

        # Calculate the number of rows based on the number of columns
        self.num_rows = (self.num_buttons + self.num_columns - 1) // self.num_columns

        screen_width = self.parent_window.getWidth()
        self.screen_width = int(screen_width)
        screen_height = self.parent_window.getHeight()
        self.screen_height = int(screen_height)

        # Calculate the width and height of each button
        self.button_width = (self.screen_width - (self.num_columns + 1) * vert_gap_size) // self.num_columns
        self.button_height = int(self.button_width / 1.7777777777777)

        # Calculate the number of visible rows based on screen height
        num_visible_rows = self.screen_height // (self.button_height + self.horiz_gap_size)

        # Calculate the available height for buttons
        available_height = self.screen_height - (self.horiz_gap_size * (num_visible_rows - 1))

        # Calculate the height of each button with gap
        self.button_height_with_gap = available_height // num_visible_rows

        focused_texture_path = self.allsports_folder + button_label + "_focused" + ".png"
        unfocused_texture_path = self.allsports_folder + button_label + "_unfocused" + ".png"

        # Calculate the x and y positions for the button
        button_x = vert_gap_size + (index % self.num_columns) * (self.button_width + vert_gap_size)
        button_y = self.horiz_gap_size + (index // self.num_columns) * (self.button_height_with_gap + self.horiz_gap_size)

        button = xbmcgui.ControlButton(
            x=button_x,
            y=button_y,
            width=self.button_width,
            height=self.button_height,
            label="",
            focusTexture=focused_texture_path,
            noFocusTexture=unfocused_texture_path
        )
        ######################################################################################################################################
        self.buttons.append(button)
        ######################################################################################################################################

        # Add the button to the window
        self.parent_window.addControl(button)

        # Add button ID and sport name mapping to the dictionary
        self.button_id_to_sport_name[button.getId()] = button_label

        # Set focus on the first button
        if index == 0:
            self.parent_window.setFocusId(button.getId())
            self.focused_index = 0

            # Retrieve the name of the currently focused sport
            focused_sport_name = self.get_focused_sport_name()
            if focused_sport_name:
                print("Currently focused sport:", focused_sport_name)
                
        else:
            pass
# endregion

# MOVEMENT
# is the current focused button in the bottom visible row?
# region
    def visible_buttons(self):
        # get the currently focused button
        #print("FOCUSED BUTTON", self.focused_index)

        # Get the total number of buttons available
        num_buttons = len(self.buttons)

        # Calculate the number of visible rows
        self.num_visible_rows = self.screen_height // (self.button_height + self.horiz_gap_size)
        #print("VISIBLE ROWS", self.num_visible_rows)

        # Calculate the number of visible buttons
        num_visible_buttons = self.num_visible_rows * self.num_columns
        #print("VISIBLE BUTTONS", num_visible_buttons)

        self.top_visible_row = -1
        self.bottom_visible_row = int(self.screen_height // (self.button_height + self.horiz_gap_size))
        #print("top visible row", self.top_visible_row)
        #print("bottom visible row", self.bottom_visible_row)
# endregion

# moveFocus method
# region
    def moveFocus(self, x, y):
        #print("movefocussssssssssssssssssssssss", x, y)
        # Calculate where the new focus will go eventually
        new_index = self.focused_index + (x + y * self.num_columns)

        # Check if the up button is pressed and the new index goes below zero
        if y < 0 and new_index < 0:
            # Do nothing and return without changing the focus
            #print("DO NOTHING AT THE TOP")
            return

        # Check if the down button is pressed and the new index exceeds the last available sport index
        elif y > 0 and new_index >= len(self.buttons):
            # Do nothing and return without changing the focus
            #print("DO NOTHING AT THE BOTTOM")
            return

        if new_index >= 0 and new_index < len(self.buttons): #Check if the new index exists
            # Change the focus to the new button
            self.parent_window.setFocusId(self.buttons[new_index].getId()) # Set the focus
            self.focused_index = new_index
        
        # Calculate which row the currently focused button is in
        focused_row = self.focused_index // self.num_columns

        # Calculate the first visible button index
        self.first_visible_button_index = focused_row * self.num_columns

        # Calculate the last visible button index
        self.last_visible_button_index = self.first_visible_button_index + self.num_visible_rows * self.num_columns

        #print("Currently focused button is in row:", focused_row)
        if focused_row == self.bottom_visible_row:
            # Call scrollUp
            self.scrollUp()
        elif focused_row == self.top_visible_row:
            # Call scrollDown
            self.scrollDown()
        
        print ("focused button id", self.buttons[self.focused_index].getId())

        # Retrieve the name of the currently focused sport
        focused_sport_name = self.get_focused_sport_name()
        if focused_sport_name:
            print("Currently focused sport:", focused_sport_name)
# endregion

# ScrollUp Method
# region
    def scrollUp(self):
        # Calculate the new y position for each button when scrolling up
        for index, button in enumerate(self.buttons):
            # Calculate the new y position for the button
            button_y = button.getY() - self.button_height_with_gap - 10

            # Set the new y position for the button
            button.setPosition(button.getX(), button_y)

        # Update the first visible button index
        self.first_visible_button_index -= self.num_columns

        self.bottom_visible_row = self.bottom_visible_row + 1
        self.top_visible_row = self.top_visible_row + 1
# endregion

# ScrollDown Method
# region
    def scrollDown(self):
        # Calculate the new y position for each button when scrolling down
        for index, button in enumerate(self.buttons):
            # Calculate the new y position for the button
            button_y = button.getY() + self.button_height_with_gap + 10

            # Set the new y position for the button
            button.setPosition(button.getX(), button_y)

        # Update the last visible button index
        self.first_visible_button_index += self.num_columns

        self.bottom_visible_row = self.bottom_visible_row - 1
        self.top_visible_row = self.top_visible_row - 1
# endregion

    def get_focused_sport_name(self):
        focused_button_id = self.buttons[self.focused_index].getId()
        return self.button_id_to_sport_name.get(focused_button_id)