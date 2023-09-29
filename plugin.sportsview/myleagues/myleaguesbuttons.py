# INITIAL STUFF
# region

# Imports
# region
import os
import xbmcaddon
import xbmc
import xbmcvfs
import urllib.request
from myleagues.myleaguesapi import MyLeaguesAPI
from mymatches.mymatcheswindow import MyMatchesWindow
import xbmcgui
import PIL
from PIL import Image, ImageEnhance
# endregion

# Class MyLeaguesButtons
# region
class MyLeaguesButtons(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.sportname = str(kwargs.get('sportname'))
        self.parent_window = kwargs.get('parent_window')  # Add parent_window
        super(MyLeaguesButtons, self).__init__(*args, **kwargs)
        self.buttons = []
        self.button_initial_y = 0
        self.button_vert_gap = 0
        self.number_of_buttons_to_display = 0
        self.button_height = 0
        self.button_width = 0
        self.focused_index = 0  # Initialize focused_index attribute
        self.first_visible_index = 0
        self.last_visible_index = 0
        self.available_leagues = []     
        self.new_leagues = []  
        self.cache_folder = 0
        self.cached_banner_path = 0
        self.screen_width = 0
        self.description_textbox = None
# endregion

    # Set parent window
    # region
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    # endregion

    # What league folders are there?
    # region
    def leagues_in_sport_folder(self):
        addon = xbmcaddon.Addon()
        sports_folder_path = addon.getSetting('setting1')

        try:
            # Check if the SMB share exists using xbmcvfs.
            if xbmcvfs.exists(sports_folder_path):
                sport_folder_path = os.path.join(sports_folder_path, self.sportname)

                try:
                    league_folders = xbmcvfs.listdir(sport_folder_path)[0]
                except Exception as e:
                    print("Error listing league folders:", str(e))
                    league_folders = []  # Set a default value if an error occurs

                self.available_leagues = league_folders
                return league_folders  # Return the list of league folders
        except Exception as e:
            print("Error:", str(e))

        # Return an empty list if no folders were found or if an exception occurred
        return []
    # endregion

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
        self.new_leagues = [league for league in self.available_leagues if league not in cached_leagues]

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

    # Calculate button size
    # region
    def calculate_button_size(self): 
        current_window = xbmcgui.getCurrentWindowId()   
        screen_height = self.parent_window.getHeight()
        self.screen_width = self.parent_window.getWidth()
        self.button_initial_y = 50
        self.button_vert_gap = 50
        self.number_of_buttons_to_display = 3

        # Calculate the button height
        a = screen_height - (self.button_initial_y * 2)
        b = a - ((self.number_of_buttons_to_display - 1) * self.button_vert_gap)
        button_height = b // self.number_of_buttons_to_display

        # Calculate the button width
        button_width = int(self.screen_width * 0.15)

        self.button_height = button_height
        self.button_width = button_width

        return button_height, button_width
    # endregion

    # Create the buttons
    # region
    def create_buttons(self, league_name):
        self.screen_width = self.parent_window.getWidth()
        leagues_api = MyLeaguesAPI(self.sportname, "")
        
        league_id = leagues_api.get_correct_league_id(league_name)
        if league_id:
            league_info = leagues_api.get_league_info(league_id)
            if league_info:
                badge_url = league_info.get('strBadge')
                if badge_url:
                    self.download_and_cache_image(badge_url, league_name)  # Call the method to download and cache the image here

                    # Get the badge image using badge_url
                    badge_image = Image.open(urllib.request.urlopen(badge_url))

                    # Create a darker background using PIL
                    darker_background = Image.new("RGBA", badge_image.size, (0, 0, 0, 80))

                    # Combine the badge image and darker background
                    focused_badge_image = Image.alpha_composite(darker_background, badge_image)

                    # Save the focused badge image as a temporary file
                    focused_badge_path = os.path.join(self.cache_folder, f"{league_name}_focused.png")
                    focused_badge_image.save(focused_badge_path)

                    button = xbmcgui.ControlButton(
                        x=50,
                        y=self.button_initial_y,
                        width=self.button_width,
                        height=self.button_height,
                        label=league_name,
                        focusTexture=focused_badge_path,  # Use the saved focused badge image
                        noFocusTexture=badge_url,
                        textOffsetX=3000,
                        textOffsetY=30,
                        textColor="#000000"
                    )
                    self.buttons.append(button)
                else:
                    print(f"Badge URL not found for league: {league_name}")
            else:
                print(f"League not found or API error for {league_name}.")
        else:
            print(f"League not found for sport: {self.sportname} and league name: {league_name}.")
    # endregion

    # Create the cached buttons
    # region
    def create_cached_buttons(self, league_name):
        
        # Get the cached image filename based on the league name
        image_filename = f"{league_name}.png"
        
        # Construct the cached image path
        cached_image_path = os.path.join(self.cache_folder, image_filename)
        
        # Check if the cached image exists
        if xbmcvfs.exists(cached_image_path):
            # Get the cached image using PIL
            cached_image = Image.open(cached_image_path)

            # Create a darker background using PIL
            darker_background = Image.new("RGBA", cached_image.size, (0, 0, 0, 80))

            # Combine the cached image and darker background
            focused_cached_image = Image.alpha_composite(darker_background, cached_image)

            # Save the focused cached image as a temporary file
            focused_cached_path = os.path.join(self.cache_folder, f"{league_name}_focused.png")
            focused_cached_image.save(focused_cached_path)

            # Create a button using the focused cached image
            button = xbmcgui.ControlButton(
                x=50,
                y=self.button_initial_y,
                width=self.button_width,
                height=self.button_height,
                label=league_name,
                focusTexture=focused_cached_path,
                noFocusTexture=cached_image_path,
                textOffsetX=2000,
                textOffsetY=10
            )
            self.buttons.append(button)
        else:
            print(f"Cached image not found for league: {league_name}. Creating regular button.")
            self.create_buttons(league_name)
    # endregion

    # Download and cache the image
    # region
    def download_and_cache_image(self, image_url, league_name):

        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cache_folder):
            xbmcvfs.mkdirs(self.cache_folder)

        image_filename = f"{league_name}.png"  # Use league name as the image filename
        cached_image_path = os.path.join(self.cache_folder, image_filename)

        try:
            # Download the image from the provided URL
            urllib.request.urlretrieve(image_url, cached_image_path)
            print(f"Image cached for league: {league_name}")
        except Exception as e:
            print(f"Error caching image for league: {league_name}. Error: {e}")
    # endregion

    # Display the buttons
    # region
    def display_buttons(self):
        for button in self.buttons:
            button.setPosition(50, self.button_initial_y)
            button.setHeight(self.button_height)
            button.setWidth(self.button_width)
            self.parent_window.addControl(button)  # Use the parent_window instance
            self.button_initial_y += self.button_height + self.button_vert_gap

        # Set focus on the first button
        if self.buttons:
            first_button_id = self.buttons[0].getId()
            self.parent_window.setFocusId(first_button_id)  # Use the parent_window instance
            self.focused_index = 0
    # endregion

# endregion

# MOVEMENT
# region
    # visible_buttons_info
    # region
    def visible_buttons_info(self):
        # Get the total number of buttons available
        num_buttons = len(self.buttons)

        # Calculate the index of the first visible button
        for i, button in enumerate(self.buttons):
            if button.getY() >= self.buttons[self.first_visible_index].getY():
                self.first_visible_index = i
                break

        # Calculate the index of the last visible button
        # Ensure that it doesn't exceed the total number of buttons minus 1
        self.last_visible_index = min(self.first_visible_index + self.number_of_buttons_to_display - 1, num_buttons - 1)
    # endregion

    # scrollup visible update
    # region
    def scrollUp_visible_update(self):
        self.focused_index += 1
        self.first_visible_index += 1
        self.last_visible_index += 1
    # endregion

    # scrollDown visible update
    # region
    def scrollDown_visible_update(self):
        self. focused_index -= 1
        self.first_visible_index -= 1
        self.last_visible_index -= 1
    # endregion

    # moveFocus
    # region
    def moveFocus(self, x, y):
        new_index = self.focused_index + y
                
        if y > 0 and self.focused_index == len(self.buttons) - 1:
            return

        # Check if the up button is pressed and the new index is above the top button (lower than 0)
        elif y < 0 and self.focused_index == 0:
            # Do nothing and return without changing the focus
            return

        # Check if the focused button is the last visible index and the down button is pressed
        elif y > 0 and self.focused_index == self.last_visible_index:
            self.scrollUp()

            # Update the focused index
            self.focused_index = new_index

            # Set focus on the new button
            new_focused_button = self.buttons[self.focused_index]
            new_focused_label = new_focused_button.getLabel()
            self.parent_window.setFocus(new_focused_button)
            return

        # Check if the focused button is the first visible index and the up button is pressed
        elif y < 0 and self.focused_index == self.first_visible_index:
            self.scrollDown()

            # Update the focused index
            self.focused_index = new_index

            # Set focus on the new button
            new_focused_button = self.buttons[self.focused_index]
            new_focused_label = new_focused_button.getLabel()
            self.parent_window.setFocus(new_focused_button)
            return

        # Update the focused index
        self.focused_index = new_index

        # Set focus on the new button
        new_focused_button = self.buttons[self.focused_index]
        new_focused_label = new_focused_button.getLabel()
        self.parent_window.setFocus(new_focused_button)

        # Call the visible_buttons_info method after moving focus
        self.visible_buttons_info()

        # Call the new_or_cached_banner method after moving focus
        self.new_or_cached_banner()

        # Call the new_or_cached_description method after moving focus
        self.new_or_cached_description()
    # endregion

    # Scroll up the buttons by one button height
    # region
    def scrollUp(self):
        for button in self.buttons:
            new_y_position = button.getY() - (self.button_height + self.button_vert_gap)
            button.setPosition(button.getX(), new_y_position)

        # Call visible_buttons_info after scrolling up
        self.scrollUp_visible_update()

        # Call the new_or_cached_banner method after scrolling up
        self.new_or_cached_banner()

        # Call the new_or_cached_description method after scrolling up
        self.new_or_cached_description()
    # endregion

    # Scroll down the buttons by one button height
    # region
    def scrollDown(self):
        for button in self.buttons:
            new_y_position = button.getY() + (self.button_height + self.button_vert_gap)
            button.setPosition(button.getX(), new_y_position)

        # Call visible_buttons_info after scrolling down
        self.scrollDown_visible_update()

        # Call the new_or_cached_banner method after scrolling down
        self.new_or_cached_banner()

        # Call the new_or_cached_description method after scrolling down
        self.new_or_cached_description()
    # endregion
# endregion

# BANNERS
# region
    # New_or_cached_banner method
    # region
    def new_or_cached_banner(self):
        focused_button = self.buttons[self.focused_index]  # Get the focused button
        focused_league_name = focused_button.getLabel()    # Get the label of the focused button

        # Construct the cached banner path
        self.cached_banner_folder = xbmcvfs.translatePath("special://home/temp/sportsview/myleagues_banners_cache/" + self.sportname + "/")
       
        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cached_banner_folder):
            xbmcvfs.mkdirs(self.cached_banner_folder)

        self.cached_banner_path = os.path.join(self.cached_banner_folder, f"{focused_league_name}.png")

        # Check if the cached banner exists
        if xbmcvfs.exists(self.cached_banner_path):
            print(f"CACHED BANNER FOUND FOR: {focused_league_name}")
            # Call the method to display the cached banner
            self.create_cached_banner(focused_league_name)
        else:
            print(f"NO CACHED BANNER FOUND FOR: {focused_league_name}")
            # Call the method to create and display a new banner
            self.create_new_banner(focused_league_name)
    # endregion

    # Create_new_banner method
    # region
    def create_new_banner(self, focused_league_name):
        leagues_api = MyLeaguesAPI(self.sportname, "")
        
        # Get the league ID
        league_id = leagues_api.get_correct_league_id(focused_league_name)
        
        if league_id:
            league_info = leagues_api.get_league_info(league_id)
            if league_info:
                banner_url = league_info.get('strBanner')
                if banner_url:
                    # Display the banner on Kodi window
                    self.display_banner(banner_url)
                    
                    # Download and cache the banner image
                    self.download_and_cache_banner(banner_url, focused_league_name)
                else:
                    print(f"No banner URL found for league: {focused_league_name}. Using fallback image.")
                    # Use a fallback image URL when no banner URL is available
                    fallback_image_url = "special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png"
                    self.display_banner(fallback_image_url)
                    
            else:
                print(f"League not found or API error for {focused_league_name}. Using fallback image.")
                # Use a fallback image URL in case of API error
                fallback_image_url = "special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png"
                self.display_banner(fallback_image_url)
        else:
            print(f"League not found for sport: {self.sportname} and league name: {focused_league_name}. Using fallback image.")
            # Use a fallback image URL if the league is not found
            fallback_image_url = "special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png"
            self.display_banner(fallback_image_url)
    # endregion

    # Download and cache the banner image
    # region
    def download_and_cache_banner(self, banner_url, focused_league_name):

        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cached_banner_path):
            xbmcvfs.mkdirs(self.cached_banner_folder)

        banner_filename = f"{focused_league_name}.png"  # Use league name as the banner filename

        try:
            # Download the banner image from the provided URL
            urllib.request.urlretrieve(banner_url, self.cached_banner_path)
        except Exception as e:
            print(f"Error caching banner image for league: {focused_league_name}. Error: {e}")
    # endregion

    # Create_cached_banner method
    # region
    def create_cached_banner(self, focused_league_name):
        
        # Load the cached banner image from the specified path
        cached_banner_path = os.path.join(self.cached_banner_folder, f"{focused_league_name}.png")
        cached_banner_image = xbmcgui.ControlImage(
            x=self.button_width + 100,
            y=50,
            width=self.screen_width - (self.button_width + 150),
            height=self.button_height,
            filename=cached_banner_path
        )

        # Add the cached banner image control to the Kodi window
        self.parent_window.addControl(cached_banner_image)
    # endregion

    # Display the banner on Kodi window
    # region
    def display_banner(self, banner_url):
        # Create a Kodi image control using the banner URL
        banner_image = xbmcgui.ControlImage(
            x=self.button_width + 100,
            y=50,
            width=self.screen_width - (self.button_width + 150),
            height=self.button_height,
            filename=banner_url
        )

        # Add the banner image control to the Kodi window
        self.parent_window.addControl(banner_image)
    # endregion
# endregion

# DESCRIPTIONS
# region
    # New_or_cached_description method
    # region
    def new_or_cached_description(self):
        focused_button = self.buttons[self.focused_index]  # Get the focused button
        focused_league_name = focused_button.getLabel()    # Get the label of the focused button

        # Construct the cached description path
        self.cached_description_folder = xbmcvfs.translatePath("special://home/temp/sportsview/myleagues_description_cache/" + self.sportname + "/")
    
        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cached_description_folder):
            xbmcvfs.mkdirs(self.cached_description_folder)

        self.cached_description_path = os.path.join(self.cached_description_folder, f"{focused_league_name}.txt")

        # Check if the cached description exists
        if xbmcvfs.exists(self.cached_description_path):
            # Call the method to display the cached description
            self.create_cached_description(focused_league_name)
        else:
            # Call the method to create and display a new description
            self.create_new_description(focused_league_name)
    # endregion

    # Create_new_banner method
    # region
    def create_new_description(self, focused_league_name):
        leagues_api = MyLeaguesAPI(self.sportname, "")
        
        # Get the league ID
        league_id = leagues_api.get_correct_league_id(focused_league_name)
        
        if league_id:
            league_info = leagues_api.get_league_info(league_id)
            if league_info:
                description_text = league_info.get('strDescriptionEN')
                if description_text:
                    # Display the description on Kodi window
                    self.display_description(description_text)
                    
                    # Download and cache the description image
                    self.download_and_cache_description(description_text, focused_league_name)
                else:
                    print(f"No description text found for league: {focused_league_name}. Using fallback description.")
                    # Use a fallback description text when no description text is available
                    fallback_description_text = "DESCRIPTION NOT AVAILABLE"
                    ######self.display_description(fallback_description_text)
                    
            else:
                print(f"League not found or API error for {focused_league_name}. Using fallback description.")
                # Use a fallback description text in case of API error
                fallback_description_text = "DESCRIPTION NOT AVAILABLE"
                ######self.display_description(fallback_description_text)
        else:
            print(f"League not found for sport: {self.sportname} and league name: {focused_league_name}. Using fallback description.")
            # Use a fallback description text if the league is not found
            fallback_description_text = "DESCRIPTION NOT AVAILABLE"
            ######self.display_description(fallback_description_text)
    # endregion

    # Download and cache the description text
    # region
    def download_and_cache_description(self, description_text, focused_league_name):

        # Create the cache folder if it doesn't exist
        if not xbmcvfs.exists(self.cached_description_folder):
            xbmcvfs.mkdirs(self.cached_description_folder)

        description_filename = f"{focused_league_name}.txt"  # Use league name as the description filename
        cached_description_path = os.path.join(self.cached_description_folder, description_filename)

        try:
            # Write the description text to the cached description file
            with open(cached_description_path, "w", encoding="utf-8") as file:
                file.write(description_text)
        except Exception as e:
            print(f"Error caching description for league: {focused_league_name}. Error: {e}")
    # endregion

    # Create the cached description
    # region
    def create_cached_description(self, focused_league_name):
        cached_description_path = os.path.join(self.cached_description_folder, f"{focused_league_name}.txt")
        
        if xbmcvfs.exists(cached_description_path):
            with open(cached_description_path, "r", encoding="utf-8") as file:
                cached_description_text = file.read()
                cleaned_description_text = self.clean_description_text(cached_description_text)
                self.display_description(cleaned_description_text)
        else:
            print(f"Cached description not found for league: {focused_league_name}.")

    def clean_description_text(self, description_text):
        # Remove extra spacing between paragraphs
        cleaned_text = '\n'.join(paragraph.strip() for paragraph in description_text.split('\n\n'))
        return cleaned_text
    # endregion

    # Display the description
    # region
    def display_description(self, description_text):
        if self.description_textbox:
            self.parent_window.removeControl(self.description_textbox)
        
        max_y_position = 675
        label_x = self.button_width + 100
        label_y = self.button_height + 100
        textbox_width = self.screen_width - (self.button_width + 150)
        textbox_height = max_y_position - label_y
                
        self.description_textbox = xbmcgui.ControlTextBox(
            x=label_x,
            y=label_y,
            width=textbox_width,
            height=textbox_height,
            font="font13"  # Set the font size
        )
        self.description_textbox.setText(description_text)  # Set the entire text content
        
        self.parent_window.addControl(self.description_textbox)
        
        self.description_textbox.autoScroll(20000, 2500, 7000)
    # endregion

# endregion

# LAUNCHING MY MATCHES WINDOW
# region

    # Method for launching My Matches window
    # region
    def launch_my_matches_window(self, focused_league_name):
        from window_manager import WindowManager

        # Create an instance of the WindowManager class
        self.window_manager = WindowManager()

        # Call the show_my_matches_page method of the existing WindowManager instance
        self.window_manager.show_my_matches_page(focused_league_name, self.sportname)
    # endregion

    # onClick method to handle button clicks
    # region
    def onClick(self, controlId):
        focused_button = self.buttons[self.focused_index]  # Get the focused button
        focused_league_name = focused_button.getLabel()    # Get the label of the focused button

        # Launch the MyMatchesWindow with the focused league name
        self.launch_my_matches_window(focused_league_name)
    # endregion

# endregion
