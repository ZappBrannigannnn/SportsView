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
from PIL import Image, ImageDraw, ImageFont
# endregion

# CLASS MySportsButtons
# region

# Your encryption key (keep it secret)
encryption_key = b'ZappBSportsVAPI6'

# Encrypted API key from settings.xml
addon = xbmcaddon.Addon()
encrypted_api_key = addon.getSetting('setting2')

apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

API_URL = f"https://www.thesportsdb.com/api/v1/json/{apikey}/all_sports.php"

class MySportsButtons:
    def __init__(self, parent_window, window_manager):  # Pass the window_manager instance as an argument
        self.parent_window = parent_window
        self.label = None
        self.buttons = []
        self.focused_index = -1  # Initialize focused_index attribute
        self.available_sports = []  # Initialize available_sports attribute
        self.window_height = None
        self.window_width = None
        self.button_height = None
        self.button_width = None
        self.image_height = None
        self.image_width = None
        self.buttons_start_y = None
        self.button_start_percent = 45
        self.first_visible_index = 0
        self.last_visible_index = 0
        self.sportname = 0
        self.loading = True
        self.temp_folder = xbmcvfs.translatePath("special://home/temp/sportsview/my_sports_buttons_cache/")  # Temporary folder for cached images
        os.makedirs(self.temp_folder, exist_ok=True)  # Create the temp folder if it doesn't exist
# endregion

    # GET THE AVAILABLE SPORTS IN THE SPORTS FOLDER
    # region
    def get_sports_folders(self):

        addon = xbmcaddon.Addon()
        sports_folder_path = addon.getSetting('setting1')
        print("SPORTS FOLDER PATH:", sports_folder_path)

        if sports_folder_path.startswith("smb://"):
            try:
                # Check if the SMB share exists using xbmcvfs.
                if xbmcvfs.exists(sports_folder_path):
                    print("SMB PATH EXISTS")
                    sports_items = xbmcvfs.listdir(sports_folder_path)
                    # Flatten the list and remove the extra nesting
                    sports_folders = [item for sublist in sports_items for item in sublist if not item.startswith(".")]
                    print("SPORTS FOLDERS:", sports_folders)
                    return sports_folders
                else:
                    print("SMB PATH DOES NOT EXIST")
            except Exception as e:
                print("Error:", str(e))
                
        else:
            # Assuming sports_folder_path is a local file system path
            if os.path.exists(sports_folder_path):
                print("LOCAL PATH EXISTS")
                sports_folders = [folder for folder in os.listdir(sports_folder_path) if os.path.isdir(os.path.join(sports_folder_path, folder))]
                print("SPORTS FOLDERS:", sports_folders)
                return sports_folders
            else:
                print("LOCAL PATH DOES NOT EXIST")

        return []
    # endregion

    # Check if the image has been cached using ETag
    # region
    def check_cache(self, image_url, sport_name):
        cache_folder = os.path.join(xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/"))
        os.makedirs(cache_folder, exist_ok=True)

        # Create a filename from the sport name
        filename = f"{sport_name.lower().replace(' ', '_')}.png"
        cache_filepath = os.path.join(cache_folder, filename)
        etag_filepath = os.path.join(cache_folder, f"{filename}.etag")

        # Check if the cached file and ETag file exist
        if os.path.exists(cache_filepath) and os.path.exists(etag_filepath):
            try:
                remote_response = urllib.request.urlopen(image_url)
                remote_etag = remote_response.headers.get("ETag", "")
                remote_response.close()

                # Read the cached ETag from the ETag file
                with open(etag_filepath, "r") as etag_file:
                    cached_etag = etag_file.read().strip()

                # Compare the cached ETag with the remote ETag
                if cached_etag == remote_etag:
                    print("CACHED IMAGE FOUND")
                    return True
                else:
                    print("CACHED IMAGE NOT FOUND")
                    return False

            except Exception as e:
                print("Error checking cache:", e)
                return False

        else:
            print("CACHED IMAGE NOT FOUND")
            return False
    # endregion

    # Download and cache the image with ETag
    # region
    def download_and_cache_image(self, image_url, sport_name):
        cache_folder = os.path.join(xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/"))
        os.makedirs(cache_folder, exist_ok=True)

        # Create a filename from the sport name
        filename = f"{sport_name.lower().replace(' ', '_')}.png"
        cache_filepath = os.path.join(cache_folder, filename)

        try:
            # Fetch the image from the URL
            image_data = urllib.request.urlopen(image_url).read()

            # Calculate the ETag for the fetched image
            remote_response = urllib.request.urlopen(image_url)
            remote_etag = remote_response.headers.get("ETag", "")
            remote_response.close()

            # Write the image data to the cache file
            with open(cache_filepath, "wb") as cached_file:
                cached_file.write(image_data)

            # Save the ETag in a separate file with the same name as the image
            etag_filepath = os.path.join(cache_folder, f"{filename}.etag")
            with open(etag_filepath, "w") as etag_file:
                etag_file.write(remote_etag)

            print("Image downloaded and cached successfully.")

        except Exception as e:
            print("Error downloading and caching image:", e)
            # Handle the error appropriately (e.g., show an error message to the user)
    # endregion

    # GET SPORTS DATA FROM ALLSPORTSAPI.PY
    # region
    def fetch_sports_data(self):
        # Set loading status to True when method starts
        self.update_loading_status(True)

        sports_api = SportsAPI(API_URL)
        sports_data = sports_api.get_sports_data()

        # Get the available sports folders
        sports_folders = self.get_sports_folders()
        print("SPORTS FOLDERS:", sports_folders)

        # CROSS REFERENCE sports_data with sports_folders = available_sports
        self.available_sports = []

        for sport in sports_data:
            sport_name = sport.get('strSport', 'N/A')
            sport_image_url = sport.get('strSportThumb', '')

            if sport_name in sports_folders:
                self.available_sports.append({
                    'strSport': sport_name,
                    'strSportImageURL': sport_image_url
                })

        # Calculate the button size based on the user's screen size (adjust the multiplier as needed)
        self.window_height = self.parent_window.getHeight()
        self.window_width = self.parent_window.getWidth()
        self.button_width = int(self.window_width * 0.5)  # 50% of screen width
        self.button_height = int(self.window_height * 0.1)  # 10% of screen height

        # Create buttons for each available sport (for the custom buttons to be made from)
        for sport in self.available_sports:
            sport_name = sport.get('strSport', 'N/A')
            button_image_path = self.generate_custom_buttons(sport_name, self.button_width, self.button_height)

        # Calculate the image size based on the user's screen size
        self.image_width = int(self.window_width * 0.5)  # 50% of the screen
        self.image_height = int(self.window_height - (self.window_height * (self.button_start_percent * 0.01)))
    
        # Set loading status to False when done fetching sports data
        self.update_loading_status(False)
    # endregion

    # Generate custom font buttons
    # region
    def generate_custom_buttons(self, sport_name, button_width, button_height):
        focused_button_image_path = os.path.join(self.temp_folder, f"{sport_name}_focused.png")
        unfocused_button_image_path = os.path.join(self.temp_folder, f"{sport_name}_unfocused.png")

        if not os.path.exists(focused_button_image_path) or not os.path.exists(unfocused_button_image_path):
            # Create blank images with white backgrounds for both focused and unfocused buttons
            focused_button_image = Image.new("RGBA", (button_width, button_height), color=(0, 0, 0, 50))
            unfocused_button_image = Image.new("RGBA", (button_width, button_height), color=(0, 0, 0, 0))

            # Create drawing objects for both buttons
            focused_draw = ImageDraw.Draw(focused_button_image)
            unfocused_draw = ImageDraw.Draw(unfocused_button_image)

            # Choose a font (You can replace this with the path to your custom font file)
            custom_font_path = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/resources/fonts/ariblk.ttf")
            desired_font_size = 40
            font = ImageFont.truetype(custom_font_path, desired_font_size)

            # Calculate the size of the text
            text_width, text_height = focused_draw.textsize(sport_name, font)

            # Calculate the position to center the text on the buttons
            text_x = (button_width - text_width) // 2
            text_y = (button_height - text_height) // 2

            # Draw the text on both buttons
            focused_draw.text((text_x, text_y), sport_name, fill=(255, 255, 255, 255), font=font)
            unfocused_draw.text((text_x, text_y), sport_name, fill=(255, 255, 255, 255), font=font)

            # Save the button images to the temp folder
            focused_button_image.save(focused_button_image_path)
            unfocused_button_image.save(unfocused_button_image_path)

        return focused_button_image_path, unfocused_button_image_path
    # endregion

    # Display the buttons
    # region
    def display_buttons(self):
        # Set loading status to True when method starts
        self.update_loading_status(True)

        # Clear the existing buttons before adding new ones
        for button in self.buttons:
            self.parent_window.removeControl(button)
        self.buttons.clear()

        # Calculate the button size based on the user's screen size (adjust the multiplier as needed)
        self.button_width = int(self.window_width * 0.5)  # 50% of screen width
        self.button_height = int(self.window_height * 0.11)  # 10% of screen height

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
            sport_name = sport.get('strSport', 'N/A')

            # Generate custom font buttons
            focused_button_image_path, unfocused_button_image_path = self.generate_custom_buttons(sport_name, self.button_width, self.button_height)

            # Calculate the Y position for the button based on its index
            y_position = self.buttons_start_y + self.button_height * index

            # Check if the button is within the visible range
            is_visible = start_visible_index <= index <= end_visible_index

            # Create a clickable button with custom font images
            button = xbmcgui.ControlButton(
                0, y_position,
                self.button_width, self.button_height,
                "",
                focused_button_image_path,
                unfocused_button_image_path
            )

            # Set the visibility of the button
            button.setVisible(is_visible)

            # Add the button to the window
            self.buttons.append(button)
            self.parent_window.addControl(button)

        # Set the focus on the first button (index 0)
        if self.buttons:
            first_button_id = self.buttons[0].getId()
            self.parent_window.setFocusId(first_button_id)
            self.focused_index = 0  # Set the focused index to 0 for the initial focus

        # Set loading status to False when done displaying the buttons
        self.update_loading_status(False)

        # Call visible_buttons_info at the end of display_buttons
        self.visible_buttons_info()
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

    # Update displayed image
    # region
    def update_displayed_image(self):

        # Check if there are available sports and the focused index is valid
        if self.available_sports and 0 <= self.focused_index < len(self.available_sports):
            sport = self.available_sports[self.focused_index]
            sport_name = sport.get('strSport', 'N/A')
            sport_image_url = sport.get('strSportImageURL', '')

            # Check the cache for the image before fetching it from the URL
            is_cached = self.check_cache(sport_image_url, sport_name)
            print("IS CACHED:", is_cached)

            if is_cached:
                print("USING CACHED IMAGE")
                # If the image is cached, load it from the cache and display it
                cache_folder = xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache/")
                filename = f"{sport_name.lower().replace(' ', '_')}.png"
                cache_filepath = os.path.join(cache_folder, filename)

                try:
                    # Use the cached image directly for ControlImage
                    image_control = xbmcgui.ControlImage(
                        int(self.window_width / 2),
                        self.buttons_start_y,
                        self.image_width,
                        self.image_height,
                        cache_filepath
                    )

                    # Add the ControlImage to the Kodi window (replace 100, 100 with the desired position on the window)
                    self.parent_window.addControl(image_control)

                    # Call setVisible(True) to make the image control visible on the window
                    image_control.setVisible(True)

                except Exception as e:
                    print("Error loading cached image:", e)
                    # If there's an error loading the cached image, fall back to fetching the image from the URL
                    self.download_and_cache_image(sport_image_url, sport_name)
                    self.update_displayed_image()  # Recursive call to try displaying the fetched image

            else:

                # Specify the temporary directory
                temp_dir = xbmcvfs.translatePath("special://temp")

                try:
                    # Fetch the image from the URL
                    image_data = urllib.request.urlopen(sport_image_url).read()

                    # Create a temporary file in the specified directory
                    temp_file_path = os.path.join(temp_dir, "temp_image.png")
                    temp_file_path_str = str(temp_file_path)

                    # Write the image data to the temporary file
                    with open(temp_file_path, 'rb') as image_file:
                        # Create a ControlImage for displaying the fetched image
                        image_control = xbmcgui.ControlImage(
                            int(self.window_width / 2),
                            self.buttons_start_y,
                            self.image_width,
                            self.image_height,
                            temp_file_path_str
                        )

                        # Add the ControlImage to the Kodi window
                        self.parent_window.addControl(image_control)

                        # Call setVisible(True) to make the image control visible on the window
                        image_control.setVisible(True)

                        # Cache the fetched image
                        self.download_and_cache_image(sport_image_url, sport_name)

                except Exception as e:
                    print("Error fetching image from API:", e)
                    # Use a fallback image in case of error or invalid image URL
                    fallback_image_path = "special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png"
                    image_control = xbmcgui.ControlImage(
                        int(self.window_width / 2),
                        self.buttons_start_y,
                        self.image_width,
                        self.image_height,
                        fallback_image_path
                    )

                    # Add the ControlImage to the Kodi window (replace 100, 100 with the desired position on the window)
                    self.parent_window.addControl(image_control)

                    # Call setVisible(True) to make the image control visible on the window
                    image_control.setVisible(True)

    # endregion

    # MOVE FOCUS
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

        # Call the method to update the displayed image based on the focused index
        self.update_displayed_image()

        # Call visible_buttons_info at the end of moveFocus
        self.visible_buttons_info()
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

    # Method to update loading status
    # region
    def update_loading_status(self, status):
        self.loading = status
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
    def onClick(self, controlId):
        # Check the loading status before processing any clicks
        if self.loading:
            return

        # Find the index of the clicked button based on its controlId
        clicked_index = None
        for index, button in enumerate(self.buttons):
            if button.getId() == controlId:
                clicked_index = index
                break

        # Check if a valid button is clicked
        if clicked_index is not None:
            # Get the sport data for the clicked button
            clicked_sport = self.available_sports[clicked_index]
            self.sportname = clicked_sport.get('strSport', 'N/A')

            # Launch My Leagues window
            self.launch_my_leagues_window()
    # endregion