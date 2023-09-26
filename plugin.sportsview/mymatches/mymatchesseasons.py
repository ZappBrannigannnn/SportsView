# INITIAL STUFF
# region

# IMPORTS
# region
import xbmcgui
import xbmcaddon
import os
from io import BytesIO
import xbmcvfs
import requests
import importlib
import shutil
import xbmc
import base64
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re
# endregion

# CLASS MYMATCHESSEASONS
# region
class MyMatchesSeasons(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.sportname = str(kwargs.get('sportname'))
        self.league_name = str(kwargs.get('league_name'))
        self.parent_window = kwargs.get('parent_window')  # Add parent_window
        super(MyMatchesSeasons, self).__init__(*args, **kwargs)
        self.window_height = None
        self.window_width = None
        self.season_button_height = None
        self.season_button_width = None
        self.seasons_in_folder = []
        self.temp_folder = xbmcvfs.translatePath("special://home/temp/sportsview/mymatches_seasons_cache/")  # Temporary folder for cached images
        self.temp_event_folder = xbmcvfs.translatePath("special://home/temp/sportsview/mymatches_events_cache/")
        self.temp_team_folder = xbmcvfs.translatePath("special://home/temp/sportsview/mymatches_teams_cache/")
        os.makedirs(self.temp_folder, exist_ok=True)  # Create the temp folder if it doesn't exist
        os.makedirs(self.temp_event_folder, exist_ok=True)  # Create the temp folder if it doesn't exist
        os.makedirs(self.temp_team_folder, exist_ok=True)  # Create the temp folder if it doesn't exist
        self.season_buttons = []
        self.event_buttons = []
        self.first_visible_season_index = 0
        self.last_visible_season_index = 0
        self.first_visible_event_index = 0
        self.last_visible_index = 0
        self.focused_season_index = 0
        self.focused_event_index = 0
        self.reversed_seasons_in_folder = []
        self.available_matches = []
        self.focused_season_name = None
        self.my_matches_seasons_instance = self  # Initialize the instance with itself to pass the variables away and back
        self.event_button_width = None
        self.event_button_height = None
        self.event_button_width = None
        self.previously_focused_season_index = None
        self.focused_event_texture_path = None
        self.team01ID = None
        self.event_button_data = {}
        self.hometeam_logo_control = None
        self.hometeam_badge_control = None
        self.hometeam_jersey_control = None
        self.hometeam_background_control = None
        self.awayteam_logo_control = None
        self.awayteam_badge_control = None
        self.awayteam_jersey_control = None
        self.awayteam_background_control = None

        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        self.apikey = base64.b64decode(encrypted_api_key).decode('utf-8')
        
# endregion

    # Set parent window
    # region
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    # endregion

    # Set league and sport
    # region
    def set_league_and_sport(self, league_name, sportname):
        self.league_name = league_name
        self.sportname = sportname
    # endregion

    # What season folders are there?
    # region
    def seasons_in_league_folder(self):

        addon = xbmcaddon.Addon()
        sports_folder_path = addon.getSetting('setting1')

        sport_folder_path = os.path.join(sports_folder_path, self.sportname)

        league_folder_path = os.path.join(sport_folder_path, self.league_name)
        
        self.seasons_in_folder = [folder for folder in os.listdir(league_folder_path) if os.path.isdir(os.path.join(league_folder_path, folder))]

        return self.seasons_in_folder
    # endregion

    # Display a vertical bar spanning from top to bottom next to season buttons
    # region
    def display_bar(self):

        # Create a ControlImage for the vertical bar
        bar_control = xbmcgui.ControlImage(
            x=self.season_button_width, 
            y=0,
            width=15, 
            height=self.window_height,  # Span the full height of the screen
            filename="special://home/addons/plugin.sportsview/mymatches/media/seasondividingbar.png"  # Replace with the actual path to your vertical bar image
        )
        
        # Add the vertical bar to the window
        self.parent_window.addControl(bar_control)
    # endregion

    # Display a vertical bar spanning from top to bottom next to event buttons
    # region
    def second_display_bar(self):

        # Create a ControlImage for the vertical bar
        bar_control = xbmcgui.ControlImage(
            x=int(self.season_button_width + self.event_button_width + 15), 
            y=0,
            width=15, 
            height=self.window_height,  # Span the full height of the screen
            filename="special://home/addons/plugin.sportsview/mymatches/media/seasondividingbar.png"  # Replace with the actual path to your vertical bar image
        )
        
        # Add the vertical bar to the window
        self.parent_window.addControl(bar_control)
    # endregion

# endregion

# SEASON BUTTONS
# region

    # Create season buttons before generating custom font buttons
    # region
    def create_season_buttons(self):
        # Calculate the button size based on the user's screen size (adjust the multiplier as needed)
        self.window_height = self.parent_window.getHeight()
        self.window_width = self.parent_window.getWidth()
        self.season_button_width = int(self.window_width * 0.1)  # 10% of screen width
        self.season_button_height = int(self.window_height * 0.1)  # 10% of screen height

        self.reversed_seasons_in_folder = list(reversed(self.seasons_in_folder))

        # Create buttons for each available season
        for season in self.reversed_seasons_in_folder:
            focused_button_image_path, unfocused_button_image_path = self.generate_custom_seasons(season)
            focused_button = xbmcgui.ControlImage(
                self.season_button_width, self.season_button_height, 
                self.season_button_width, self.season_button_height, 
                focused_button_image_path
            )
    # endregion

    # Generate custom font buttons
    # region
    def generate_custom_seasons(self, season):
        focused_button_image_path = os.path.join(self.temp_folder, f"{season}_focused.png")
        unfocused_button_image_path = os.path.join(self.temp_folder, f"{season}_unfocused.png")

        if not os.path.exists(focused_button_image_path) or not os.path.exists(unfocused_button_image_path):
            # Create blank images with white backgrounds for both focused and unfocused buttons
            focused_button_image = Image.new("RGBA", (self.season_button_width, self.season_button_height), color=(0, 0, 0, 50))
            unfocused_button_image = Image.new("RGBA", (self.season_button_width, self.season_button_height), color=(0, 0, 0, 0))

            # Create drawing objects for both buttons
            focused_draw = ImageDraw.Draw(focused_button_image)
            unfocused_draw = ImageDraw.Draw(unfocused_button_image)

            # Choose a font (You can replace this with the path to your custom font file)
            custom_font_path = "special://home/addons/plugin.sportview/resources/fonts/ariblk.ttf"
                    # Initialize font size based on season text length

            if len(season) == 4:
                desired_font_size = 50
            elif len(season) == 9:
                desired_font_size = 32
            else:
                desired_font_size = 20  # Default font size for other lengths

            # Create a new ImageFont object with the desired font size
            font = ImageFont.truetype(custom_font_path, desired_font_size)

            # Calculate the size of the text with the font
            text_width, text_height = focused_draw.textsize(season, font)

            # Calculate the position to center the text on the buttons
            text_x = (self.season_button_width - text_width) // 2
            text_y = (self.season_button_height - text_height - 10) // 2

            # Draw the text on both buttons with the font
            focused_draw.text((text_x, text_y), season, fill=(255, 255, 255, 255), font=font)
            unfocused_draw.text((text_x, text_y), season, fill=(255, 255, 255, 255), font=font)

            # Save the button images to the temp folder
            focused_button_image.save(focused_button_image_path)
            unfocused_button_image.save(unfocused_button_image_path)

        return focused_button_image_path, unfocused_button_image_path
    # endregion

    # Display the buttons
    # region
    def display_season_buttons(self):

        # Calculate y position for button placement
        y_position = 0

        # Create buttons for each available season
        for season in self.reversed_seasons_in_folder:
            # Generate custom font buttons
            focused_button_image_path, unfocused_button_image_path = self.generate_custom_seasons(season)

            # Create a clickable button with custom font images
            button_control = xbmcgui.ControlButton(
                x=0, 
                y=y_position,
                width=self.season_button_width,
                height=self.season_button_height,
                label="season",
                textOffsetX=2000,
                focusTexture=focused_button_image_path,
                noFocusTexture=unfocused_button_image_path
            )

            # Set the position of the button
            button_control.setPosition(0, y_position)

            # Add the button to the window and the buttons list
            self.season_buttons.append(button_control)
            self.parent_window.addControl(button_control)

            # Set focus on the first season button right after adding it
            if self.season_buttons and len(self.season_buttons) == 1:
                self.parent_window.setFocusId(button_control.getId())

            # Increment the y_position for the next button
            y_position += self.season_button_height  # Add some vertical spacing between buttons

        # Call the visible_season_buttons_info method after displaying buttons
        self.visible_season_buttons_info()
    # endregion

# endregion

# EVENT BUTTONS
# region

    # What matches are available in season of the league of the sport
    # GETS THE LIST OF MATCHES THAT ARE IN THE SEASON (SELF.AVAILABLE_MATCHES)
    # CALLS THE NEW_OR_CACHED_EVENT_BUTTONS METHOD(SELF.AVAILABLE_MATCHES)
    # region
    def matches_in_season(self):

        # Get the currently focused season index
        focused_season_index = self.focused_season_index

        # Check if the focused season index is valid
        if 0 <= focused_season_index < len(self.reversed_seasons_in_folder):
            self.focused_season_name = self.reversed_seasons_in_folder[focused_season_index]

            addon = xbmcaddon.Addon()
            sports_folder_path = addon.getSetting('setting1')
            sport_folder_path = os.path.join(sports_folder_path, self.sportname)
            league_folder_path = os.path.join(sport_folder_path, self.league_name)
            season_folder_path = os.path.join(league_folder_path, self.focused_season_name)

            # List available matches in the focused season folder
            self.available_matches = [match for match in os.listdir(season_folder_path)]

            if self.available_matches:
                print("Available matches in season '{}'".format(self.focused_season_name), self.available_matches)
            else:
                print("No matches available in season '{}'." .format(self.focused_season_name))
        else:
            print("No season focused or invalid focused index.")
        
        # Call the new_or_cached_event_buttons method 
        self.new_or_cached_event_buttons(self.available_matches)

    # endregion

    # New or cached event buttons
    # READS THE SAVED AVAILABLE MATCHES FILE AND COMPARES TO SELF.AVAILABLE_MATCHES 
    # IF THEY MATCH START A LOOP FOR EACH MATCH DISPLAY_THE_CACHED_PAGE_EVENT_BUTTON
    # IF THEY DON'T MATCH WRITE A NEW SAVED AVAILABLE MATCHES FILE AND START THE GET_ALL_LEAGUES METHOD (NOT CACHED FORK)
    # region
    def new_or_cached_event_buttons(self, available_matches):      
        # get the saved available matches and define some preliminarty stuff
        # region
        saved_available_matches_folder = os.path.join(f"special://home/temp/sportsview/mymatches_saved_available_matches/{self.sportname}/{self.league_name}/")
        saved_available_matches_folder = xbmcvfs.translatePath(saved_available_matches_folder)
        os.makedirs(saved_available_matches_folder, exist_ok=True)  # Create the temp folder if it doesn't exist
        saved_available_matches_path = (f"{saved_available_matches_folder}/{self.focused_season_name}_saved.txt")
        # endregion

        # read the saved_available_matches_path and call the contents saved_available_matches
        # region
        if os.path.exists(saved_available_matches_path):
            # Open the text file for reading
            with open(saved_available_matches_path, "r", encoding="utf-8") as file:
                # Read the contents of the file
                saved_available_matches = file.read()
        else:
            # Call the get_all_leagues method
            print("Error reading saved_available_matches file or it doesn't exist. Calling get_all_leagues method to start the process of making new event buttons.")
            # Write the saved_available_matches to the saved_available_matches_path
            # open the saved_available_matches_path for writing
            with open(saved_available_matches_path, "w", encoding="utf-8") as file:
                # Write the opening square bracket
                file.write("[")
                # Write each match to the file
                for i, match in enumerate(available_matches):
                    if i > 0:
                        file.write(", ")  # Add a comma and space for all items except the first
                    file.write("'" + match + "'")
                # Write the closing square bracket
                file.write("]")

            self.get_all_leagues()
            return
        # endregion

        # Check if the saved_available_matches are the same as the available_matches (CHECKING IF THERE ARE CHANGES TO THE FOLDER CONTENTS)
        # region
        if str(available_matches) == str(saved_available_matches):
            # CODE TO USE THE CACHED EVENT BUTTONS
            # Call the display_event_buttons method
            for event in available_matches:
                try:
                    self.display_cached_page_event_button(event)
                except StopIteration:
                    # Handle the case where the loop should be stopped
                    break
        # endregion

        # If the saved_available_matches and available_matches don't match
        # region
        else:
            # Call the get_all_leagues method
            self.get_all_leagues()

            # Write the saved_available_matches to the saved_available_matches_path
            # open the saved_available_matches_path for writing
            with open(saved_available_matches_path, "w", encoding="utf-8") as file:
                # Write the opening square bracket
                file.write("[")
                # Write each match to the file
                for i, match in enumerate(available_matches):
                    if i > 0:
                        file.write(", ")  # Add a comma and space for all items except the first
                    file.write("'" + match + "'")
                # Write the closing square bracket
                file.write("]")
        # endregion
    # endregion
    
    # EVERYTHING API
    # region

    # Starts the dominoes
    # Get all leagues
    # region
    def get_all_leagues(self):
        url = f'https://www.thesportsdb.com/api/v1/json/{self.apikey}/all_leagues.php'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            leagues = data.get('leagues', [])

            # Call the get_correct_league_id method
            self.get_correct_league_id(leagues)

            return leagues
        else:
            print('Failed to fetch all leagues data.')
            return []
    # endregion

    # Get correct league id by checking if the combination of my sport and league name matches a combination in the list of leagues
    # region
    def get_correct_league_id(self, leagues):
        target_league = None

        for league in leagues: # searching each league in leagues
            if league['strLeague'] == self.league_name and league['strSport'] == self.sportname: # If strLeague and our league name match AND strSport and our sport name match
                target_league = league  # then target_league is whatever league that was

                break
                
        if target_league:
            league_id = target_league
            
            # Call the get_all_events_in_season method
            self.get_all_events_in_season(league_id)

            return league_id
        else:
            return None
        
    # endregion

    # Get all events in league by season
    # region
    def get_all_events_in_season(self, league_id):
        # Extract the league id from the league_id league objectc
        id_league = league_id['idLeague']  # Using dictionary indexing
 
        url = f'https://www.thesportsdb.com/api/v1/json/{self.apikey}/eventsseason.php?id={id_league}&s={self.focused_season_name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])

            # Call the call_dynamic_namehelper method
            self.call_dynamic_namehelper(events, id_league)

            return events
        else:
            print('Failed to fetch all events data.')
            return []
    # endregion

    # Find which namehelper you need and call it.
    # region
    def call_dynamic_namehelper(self, events, id_league):
        
        # Construct the module name dynamically
        module_name = f"leaguenamehelper.{self.sportname.replace(' ', '_')}.{self.league_name.replace(' ', '_')}_namehelper"
        # Import the module dynamically
        module = importlib.import_module(module_name)
        
        # Get the class using getattr
        class_name = f"{self.league_name.replace(' ', '')}Helper"  # Replace with the actual class name
        
        helper_class = getattr(module, class_name)
        
        # Create an instance of the class
        helper_instance = helper_class()
        
        # Call the method on the instance
        method_name = "entry_method"  # Replace with the actual method name

        method = getattr(helper_instance, method_name)
        
        # Call the method with appropriate arguments
        method(self.focused_season_name, self.available_matches, id_league, events, self.my_matches_seasons_instance)
    # endregion

# endregion

    # RECEIVE event data from specific league name helper
    # region
    def receive_event_data(self, team01, team02, round_number, available_matches, events, event_id, event_data, my_matches_seasons_instance, match, VERSUS, event_label, event_thumbnail):

        self.sportname = my_matches_seasons_instance.sportname
        self.league_name = my_matches_seasons_instance.league_name
        self.parent_window = my_matches_seasons_instance.parent_window
        self.window_height = my_matches_seasons_instance.window_height
        self.window_width = my_matches_seasons_instance.window_width
        self.season_button_height = my_matches_seasons_instance.season_button_height
        self.season_button_width = my_matches_seasons_instance.season_button_width
        self.seasons_in_folder = my_matches_seasons_instance.seasons_in_folder
        self.temp_folder = my_matches_seasons_instance.temp_folder
        self.temp_event_folder = my_matches_seasons_instance.temp_event_folder
        self.temp_team_folder = my_matches_seasons_instance.temp_team_folder
        self.season_buttons = my_matches_seasons_instance.season_buttons
        self.first_visible_season_index = my_matches_seasons_instance.first_visible_season_index
        self.last_visible_season_index = my_matches_seasons_instance.last_visible_season_index
        self.first_visible_event_index = my_matches_seasons_instance.first_visible_event_index
        self.last_visible_index = my_matches_seasons_instance.last_visible_index
        self.focused_season_index = my_matches_seasons_instance.focused_season_index
        self.reversed_seasons_in_folder = my_matches_seasons_instance.reversed_seasons_in_folder
        self.available_matches = my_matches_seasons_instance.available_matches
        self.focused_season_name = my_matches_seasons_instance.focused_season_name
        self.event_buttons = my_matches_seasons_instance.event_buttons
        self.event_button_height = my_matches_seasons_instance.event_button_height
        self.event_button_width = my_matches_seasons_instance.event_button_width
        self.focused_event_texture_path = my_matches_seasons_instance.focused_event_texture_path
        self.team01ID = my_matches_seasons_instance.team01ID
        self.event_button_data = my_matches_seasons_instance.event_button_data
        self.match_to_click = match
        self.round_number = round_number

        # Call the create_event_button method
        self.create_event_button_start(event_id, event_data, match, event_label, VERSUS, event_thumbnail, team01, team02, self.available_matches)
    # endregion

    # Create event button start
    # region
    def create_event_button_start(self, event_id, event_data, match, event_label, VERSUS, event_thumbnail, team01, team02, available_matches):

        # Calculate button size based on screen size (adjust as needed)
        self.event_button_width = (self.window_width * 0.3)
        self.event_button_height = ((self.window_height / 4) - 7)

        # Calculate y position for the event button
        if self.event_buttons:
            last_event_button = self.event_buttons[-1]
            y_position = last_event_button.getY() + last_event_button.getHeight() + 10  # You can adjust the spacing (10 in this case)
        else:
            y_position = 0

        # NEW_OR_CACHED_EVENT_BUTTON inside create_event_button_start
        # region
        cached_button_path = os.path.join(self.temp_event_folder, "focused_" + event_id + ".png")
        
        if os.path.exists(cached_button_path):
            print("Event button cached")
            self.display_event_button(event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches)
        else:
            print("Event button not cached")
            self.create_nofocus_event_button(event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches)
        # endregion

    # endregion

    # Create nofocus_event_button
    # region
    def create_nofocus_event_button(self, event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches):

        # Define the font size and load the custom font
        font_size = 100  # Adjust the font size as needed
        font_path = os.path.join('special://home/addons/plugin.sportview/resources/fonts/ariblk.ttf')
        font = ImageFont.truetype(font_path, font_size)

        # Check if event_thumbnail is empty
        if not event_thumbnail:
            # Create a placeholder image
            width, height = 1920, 1080  # Set the desired width and height
            background_color = (200, 200, 200)  # Set the background color (white in this example)

            # Create a new image with the specified width, height, and background color
            placeholder_image = Image.new("RGB", (width, height), background_color)

            # You can also draw text or shapes on the placeholder image if desired
            draw = ImageDraw.Draw(placeholder_image)
            text = match
            text_color = (0, 0, 0)  # Set the text color (black in this example)
            # Define a font and size
            font = ImageFont.truetype("special://home/addons/plugin.sportview/resources/fonts/ariblk.ttf", size=160)  # Replace with the path to your font file and desired size
            # Calculate the position to center the text
            text_width, text_height = draw.textsize(text, font)
            #x = (width - text_width) / 2
            #y = (height - text_height) / 2

            # Define the maximum width for word wrapping
            max_width = 15  # Adjust to your desired maximum width

            # Use textwrap to wrap the text within the specified width
            wrapped_text = textwrap.fill(text, width=max_width)

            # Draw the wrapped text with the specified font and size
            draw.text((100, 100), wrapped_text, fill=text_color, font=font)


            # Use the placeholder image
            image = placeholder_image
        else:
            # Download the image from the URL
            response = requests.get(event_thumbnail)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                image = Image.open(image_data)
                
        # Create a drawing object
        draw = ImageDraw.Draw(image)

        # Define the position and text for the round number
        text = str(self.round_number)
        text_size = font.getsize(text)
        text_width = text_size[0]
        half_text_width = int((text_width / 2) - 340)
        half_button_width = int(self.event_button_width / 2)
        text_x = int(half_button_width - half_text_width)

        # Draw the round number text on the image
        draw.text(
            xy=(text_x, 540), 
            text=text, 
            fill=(255, 255, 255, 255), 
            font=font,
            align='center'
)

        # Save or display the modified image
        image.save(self.temp_event_folder + event_id + ".png")

        # Call the create_focus_event_button method
        self.create_focus_event_button(event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches)
    # endregion

    # Create focus_event_button
    # region
    def create_focus_event_button(self, event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches):

        # Load the previously saved noFocusTexture image
        nofocus_texture_path = self.temp_event_folder + event_id + ".png"
        image = Image.open(nofocus_texture_path)

        # Convert the image to grayscale
        grayscale_image = image.convert("L")

        # Add a colored border
        border_color = (18, 101, 196)  # Change this to the desired border color
        border_thickness = 30  # Adjust as needed

        # Calculate new dimensions for the bordered image
        new_width = image.width + 2 * border_thickness
        new_height = image.height + 2 * border_thickness

        # Create a new image with the calculated dimensions and fill it with the border color
        bordered_image = Image.new("RGB", (new_width, new_height), border_color)

        # Calculate the position to paste the grayscale image to center it within the bordered image
        paste_position = ((new_width - image.width) // 2, (new_height - image.height) // 2)

        # Paste the grayscale image onto the bordered image
        bordered_image.paste(grayscale_image, paste_position)

        # Give the modified image a name
        self.focused_event_texture_path = self.temp_event_folder + "focused_" + event_id + ".png"
        # Save the modified image
        bordered_image.save(self.focused_event_texture_path)

        # Call display_event_button method with the focused image
        self.display_event_button(event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches)
    # endregion

    # Display event button called from 
    # region
    def display_event_button(self, event_label, event_thumbnail, event_data, y_position, team01, team02, match, event_id, available_matches):

        # Create a button control for the event
        self.focused_event_texture_path = self.temp_event_folder + "focused_" + event_id + ".png"
        nofocus_event_texture_path = self.temp_event_folder + event_id + ".png"

        event_button = xbmcgui.ControlButton(
            x=int(self.season_button_width + 15),  # Adjust as needed
            y=int(y_position),
            width=int(self.event_button_width),
            height=int(self.event_button_height),
            label="event",
            textOffsetX=2000,
            focusTexture=self.focused_event_texture_path,  # Replace with actual path
            noFocusTexture=nofocus_event_texture_path,  # Use the event thumbnail as noFocusTexture
        )

        # Add the event button to the window
        self.parent_window.addControl(event_button)
        self.event_buttons.append(event_button)  # Keep track of buttons

        button_id = event_button.getId()

        # Associate additional information with the ControlButton
        # each time the loop gets here this appends the event's data to self.event_button_data
        self.event_button_data[button_id] = {
            "team01NAME": str(team01),
            "team02NAME": str(team02),
            "match_path": str(match),
            "event_id": str(event_id)
        }
        
        # Get and name associated info folder and file
        saved_associated_info_folder = os.path.join(f"special://home/temp/sportsview/mymatches_saved_available_matches/{self.sportname}/{self.league_name}/")
        saved_associated_info_folder = xbmcvfs.translatePath(saved_associated_info_folder)
        saved_associated_info_path = (f"{saved_associated_info_folder}/{self.focused_season_name}_associated_info.txt")

        # Write the saved_available_matches to the saved_available_matches_path
        # open the saved_available_matches_path for writing
        with open(saved_associated_info_path, "w", encoding="utf-8") as file:
            # Write each event's data to a separate line in the file
            with open(saved_associated_info_path, "w", encoding="utf-8") as file:
                for data in self.event_button_data.values():
                    file.write(
                        "Match:" + data["match_path"] + ", " +
                        "Team01NAME:" + data["team01NAME"] + ", " +
                        "Team02NAME:" + data["team02NAME"] + ", " +
                        "match_path:" + data["match_path"] + ", " +
                        "event_id:" + data["event_id"] + "\n\n"
                    )
            self.event_button_data = {}

        # Call the second_display_bar method
        self.second_display_bar()
    # endregion

    # Display_cached_page_event_button called from new_or_cached_event_button
    # region
    def display_cached_page_event_button(self, event):
        # Calculate y position for the event button
        # region
        if self.event_buttons:
            last_event_button = self.event_buttons[-1]
            y_position = last_event_button.getY() + last_event_button.getHeight() + 10  # You can adjust the spacing (10 in this case)
        else:
            y_position = 0
            pass
        # endregion

        # Calculate button size based on screen size (adjust as needed)
        # region
        self.event_button_width = (self.window_width * 0.3)
        self.event_button_height = ((self.window_height / 4) - 7)
        # endregion

        # Get and name associated info folder and file
        # region
        saved_associated_info_folder = os.path.join(f"special://home/temp/sportsview/mymatches_saved_available_matches/{self.sportname}/{self.league_name}/")
        saved_associated_info_folder = xbmcvfs.translatePath(saved_associated_info_folder)
        saved_associated_info_path = (f"{saved_associated_info_folder}/{self.focused_season_name}_associated_info.txt")
        current_match_data = {}  # Initialize an empty dictionary
        Team01 = ""
        Team02 = ""
        match = ""
        event_id = ""
        match_found = False
        # endregion

        # Get the associated info from the saved_associated_info_path
        # region
        # Look through the saved_associated_info_path and find our current event in the "Match:"
        if os.path.exists(saved_associated_info_path):
            with open(saved_associated_info_path, "r", encoding="utf-8") as file:
                for line in file:
                    # If the line starts with "Match:" followed by the event ID
                    if line.startswith(f"Match:{event}"):
                        match_from_saved_file = re.search(r'Match:(.*?),', line).group(1).strip()
                        # Now match_from_saved_file should contain everything after "Match:" and before the first comma ","
                        if(event == match_from_saved_file):

                            # Create a dictionary to store match data
                            if "Team01NAME:" in line:
                                team01 = re.search(r'Team01NAME:(.*?),', line).group(1).strip()

                            if "Team02NAME:" in line:
                                team02 = re.search(r'Team02NAME:(.*?),', line).group(1).strip()

                            if "match_path:" in line:
                                match = re.search(r'match_path:(.*?),', line).group(1).strip()  

                            # Extract the event_id separately
                            event_id_match = re.search(r'event_id:(\d+)', line)
                            if event_id_match:
                                event_id = event_id_match.group(1)
                        
                        match_found = True  # Set the flag to True when the match is found
                        break  # Exit the loop when the match is found

        if not match_found:
            print("Error reading saved_associated_info_path or it doesn't exist. Calling get_all_leagues method to start the process of making new event buttons.(222)")
            # Call the get_all_leagues method
            self.get_all_leagues()
            raise StopIteration  # Raise an exception to stop the loop
        else:
            pass
        # endregion

        # Create a button control for the event
        # region
        self.focused_event_texture_path = self.temp_event_folder + "focused_" + event_id + ".png"
        nofocus_event_texture_path = self.temp_event_folder + event_id + ".png"

        event_button = xbmcgui.ControlButton(
            x=int(self.season_button_width + 15),  # Adjust as needed
            y=int(y_position),
            width=int(self.event_button_width),
            height=int(self.event_button_height),
            label="event",
            textOffsetX=2000,
            focusTexture=self.focused_event_texture_path,  # Replace with actual path
            noFocusTexture=nofocus_event_texture_path,  # Use the event thumbnail as noFocusTexture
        )

        # Add the event button to the window
        self.parent_window.addControl(event_button)
        self.event_buttons.append(event_button)  # Keep track of buttons

        button_id = event_button.getId()
        # endregion

        # Associate additional information with the ControlButton
        # region
        self.event_button_data[button_id] = {
            "team01NAME": team01,
            "team02NAME": team02,
            "match_path": match,
            "event_id": event_id
        }
        # endregion

        # Call the second_display_bar method
        self.second_display_bar()
    # endregion

# endregion

# EVENT LOGOS BADGES JERSEYS BACKGROUNDS
# region

    # Display the team images method
    # region
    def display_team_images(self):

        button_id = self.focused_event_name.getId()

        # Remove previous event images if they exist
        # region
        if self.hometeam_logo_control is not None:
            self.parent_window.removeControl(self.hometeam_logo_control)
        if self.hometeam_badge_control is not None:
            self.parent_window.removeControl(self.hometeam_badge_control)
        if self.hometeam_jersey_control is not None:
            self.parent_window.removeControl(self.hometeam_jersey_control)
        if self.hometeam_background_control is not None:
            self.parent_window.removeControl(self.hometeam_background_control)
        if self.awayteam_logo_control is not None:
            self.parent_window.removeControl(self.awayteam_logo_control)
        if self.awayteam_badge_control is not None:
            self.parent_window.removeControl(self.awayteam_badge_control)
        if self.awayteam_jersey_control is not None:
            self.parent_window.removeControl(self.awayteam_jersey_control)
        if self.awayteam_background_control is not None:
            self.parent_window.removeControl(self.awayteam_background_control)
        # endregion
        
        # Some calculations and getting the teamNAMEs for naming images
        # region
        self.event_button_width = int(self.window_width * 0.3)
        self.event_button_height = ((self.window_height / 4) - 7)

        if button_id in self.event_button_data:
            data = self.event_button_data[button_id]
            team01NAME = data.get("team01NAME", "")
            team02NAME = data.get("team02NAME", "")
            match_path = data.get("match_path", "")
            event_id = data.get("event_id", "")
 
        available_width = int(self.window_width - (self.season_button_width + 15 + self.event_button_width + 15))
        logo_width = int(available_width / 3)
        logo_height = int(self.window_height / 4)
        starting_x = int(self.season_button_width + 15 + self.event_button_width + 15)
        left_image_location = int(starting_x + 15)
        center_image_location = int(starting_x + (available_width / 2) - (logo_width / 2))
        right_image_location = int(starting_x + (available_width - (logo_width + 15)))
        bottom_image_location = int(self.window_height - (logo_height + (logo_height / 2)))
        # endregion

        # Create the hometeam_background for the event (poster else thumb else banner)
        # region
        if team01NAME != "None" and team01NAME != None:
            print("USING BACKGROUND")
            hometeam_background = xbmcgui.ControlImage(
                x=starting_x,  # season button + bar + event button + bar
                y=0,  # Adjust as needed
                width=available_width,
                height=int(self.window_height / 2),
                filename=f"{self.temp_team_folder}/{team01NAME}_background.png",
                colorDiffuse="0x50FFFFFF" # Change the 0xFF to 0xE0, 0xD0, 0xC0, 0xB0, 0xA0, 0x90, 0x80, 0x70, 0x60, 0x50, 0x40, 0x30, 0x20, 0x10, 0x00 to reduce opacity
            )

######################################CHECK WITH EVENT THAT HAS NO POSTER OR THUMBNAIL#############################################            
        else:
            if os.path.exists(f"{self.temp_team_folder}/{event_id}_poster.png"):
                print("USING POSTER")
                hometeam_background = xbmcgui.ControlImage(
                    x=int((available_width - (available_width - 170)) / 2) + starting_x,  # season button + bar + event button + bar
                    y=0,  # Adjust as needed
                    width=available_width - 170,
                    height=self.window_height,
                    filename=f"{self.temp_team_folder}/{event_id}_poster.png",
                )
            elif os.path.exists(f"{self.temp_team_folder}/{event_id}_thumb.png"):
                print("NO POSTER FOUND USING THUMBNAIL")
                hometeam_background = xbmcgui.ControlImage(
                    x=starting_x,  # season button + bar + event button + bar
                    y=0,  # Adjust as needed
                    width=available_width,
                    height=self.window_height - 500,
                    filename=f"{self.temp_team_folder}/{event_id}_thumb.png",
                )
            elif os.path.exists(f"{self.temp_team_folder}/{event_id}_banner.png"):
                print("NO POSTER OR THUMBNAIL FOUND USING BANNER")
                hometeam_background = xbmcgui.ControlImage(
                    x=int((available_width - (available_width - 170)) / 2) + starting_x,  # season button + bar + event button + bar
                    y=0,  # Adjust as needed
                    width=available_width - 170,
                    height=self.window_height,
                    filename=f"{self.temp_team_folder}/{event_id}.png",
                )
            else:
                print("NO IMAGE FOUND FOR THIS EVENT")
####################################################################################################################################               
        # Store the control for removal later
        self.hometeam_background_control = hometeam_background

        # Add the event button to the window
        self.parent_window.addControl(hometeam_background)
        # endregion

        # Create the hometeam_logo for the event (no)
        # region
        if team01NAME != None:
            hometeam_logo = xbmcgui.ControlImage(
                x=left_image_location,
                y=int(logo_height / 2),  
                width=logo_width,
                height=logo_height,
                filename=f"{self.temp_team_folder}/{team01NAME}_logo.png"
                )
        else:
            pass

        # Store the control for removal later
        self.hometeam_logo_control = hometeam_logo

        # Add the event button to the window
        self.parent_window.addControl(hometeam_logo)
        # endregion

        # Create the hometeam_jersey for the event (no)
        # region
        if team01NAME != None:
            hometeam_jersey = xbmcgui.ControlImage(
                x=center_image_location,  # season button + bar + event button + bar + space
                y= int(logo_height / 2),  # Adjust as needed
                width=logo_width,
                height=int(self.event_button_height),
                filename=f"{self.temp_team_folder}/{team01NAME}_jersey.png"
                )
        else:
            pass

        # Store the control for removal later
        self.hometeam_jersey_control = hometeam_jersey

        # Add the event button to the window
        self.parent_window.addControl(hometeam_jersey)
        # endregion

        # Create the hometeam_badge for the event (no)
        # region
        if team01NAME != None:
            hometeam_badge = xbmcgui.ControlImage(
                x=right_image_location,  # season button + bar + event button + bar + space
                y=int(logo_height / 2),  # Adjust as needed
                width=logo_width,
                height=int(self.event_button_height),
                filename=f"{self.temp_team_folder}/{team01NAME}_badge.png"
                )
        else:
            pass

        # Store the control for removal later
        self.hometeam_badge_control = hometeam_badge

        # Add the event button to the window
        self.parent_window.addControl(hometeam_badge)
        # endregion

        # Create the awayteam_background for the event (no)
        # region
        if team02NAME != None:
            awayteam_background = xbmcgui.ControlImage(
                x=starting_x,
                y=int(self.window_height / 2),  # Adjust as needed
                width=available_width,
                height=int(self.window_height / 2),
                filename=f"{self.temp_team_folder}/{team02NAME}_background.png",
                colorDiffuse="0x50FFFFFF" # Change the 0xFF to 0xE0, 0xD0, 0xC0, 0xB0, 0xA0, 0x90, 0x80, 0x70, 0x60, 0x50, 0x40, 0x30, 0x20, 0x10, 0x00 to reduce opacity
            )
        else:
            pass

        # Store the control for removal later
        self.awayteam_background_control = awayteam_background

        # Add the event button to the window
        self.parent_window.addControl(awayteam_background)
        # endregion

        # Create the awayteam_logo for the event (no)
        # region
        if team02NAME != None:
            awayteam_logo = xbmcgui.ControlImage(
                x=left_image_location,
                y= bottom_image_location,  
                width=logo_width,
                height=logo_height,
                filename=f"{self.temp_team_folder}/{team02NAME}_logo.png"
                )
        else:
            pass

        # Store the control for removal later
        self.awayteam_logo_control = awayteam_logo

        # Add the event button to the window
        self.parent_window.addControl(awayteam_logo)
        # endregion

        # Create the awayteam_jersey for the event (no)
        # region
        if team02NAME != None:
            awayteam_jersey = xbmcgui.ControlImage(
                x=center_image_location, 
                y= bottom_image_location,
                width=logo_width,
                height=logo_height,
                filename=f"{self.temp_team_folder}/{team02NAME}_jersey.png"
            )
        else:
            pass

        # Store the control for removal later
        self.awayteam_jersey_control = awayteam_jersey

        # Add the event button to the window
        self.parent_window.addControl(awayteam_jersey)
        # endregion

        # Create the awayteam_badge for the event (no)
        # region
        if team02NAME != None:
            awayteam_badge = xbmcgui.ControlImage(
                x=right_image_location,
                y= bottom_image_location,
                width=logo_width,
                height=logo_height,
                filename=f"{self.temp_team_folder}/{team02NAME}_badge.png"
            )
        else:
            pass

        # Store the control for removal later
        self.awayteam_badge_control = awayteam_badge

        # Add the event button to the window
        self.parent_window.addControl(awayteam_badge)
        # endregion
        
        # Create the VS bar
        # region
        if team01NAME != "None" and team01NAME != None and team02NAME != "None" and team02NAME != None:
            vs_bar = xbmcgui.ControlImage(
                x=starting_x,
                y=int(self.window_height / 2) - 75,
                width=available_width,
                height=150,
                filename="special://home/addons/plugin.sportsview/mymatches/media/versus_bar.png"
                )
        else:
            vs_bar = None
            pass

        # Store the control for removal later
        if vs_bar != None:
            self.vs_bar_control = vs_bar

            # Add the event button to the window
            self.parent_window.addControl(vs_bar)
        # endregion
    # endregion
        
# MOVEMENT
# region

    # Season or an event movement?
    # region
    def season_or_event(self, x, y):
        
        focused_control_id = self.parent_window.getFocusId()

        if focused_control_id in [button.getId() for button in self.season_buttons]:
            print("Focused control is a season button.")

            # Call the moveSeasonFocus method
            self.moveSeasonFocus(x, y)

        elif focused_control_id in [button.getId() for button in self.event_buttons]:
            print("Focused control is an event button.")

            # Call the moveEventFocus method
            self.moveEventFocus(x, y)
        else:
            print("Focused control is not a season or event button.")
    # endregion

    # SEASON BUTTONS MOVEMENT
    # region

    # visible_season_buttons_info
    # region
    def visible_season_buttons_info(self):

        # Get the total number of buttons available
        num_buttons = len(self.reversed_seasons_in_folder)

        # Calculate the number of buttons that can be displayed on the screen at once
        max_visible_buttons = self.window_height // self.season_button_height

        # Calculate the index of the first visible button based on the focused index
        self.first_visible_season_index = max(0, self.focused_season_index - max_visible_buttons)

        # Calculate the index of the last visible button based on the first visible index
        self.last_visible_season_index = min(num_buttons - 1, self.first_visible_season_index + max_visible_buttons - 1)
    # endregion

    # MOVE SEASON FOCUS BUTTONS 
    # region
    def moveSeasonFocus(self, x, y):

        new_index = self.focused_season_index + y

        # Check if the right button is pressed and a previously focused season index exists
        if x > 0:
            if self.event_buttons:
                self.previously_focused_season_index = self.focused_season_index
                self.parent_window.setFocusId(self.event_buttons[0].getId())
                self.focused_event()
            return
        
        elif x < 0:
            # do nothing
            return

        # Check if the down button is pressed and the new index exceeds the last available sport index
        if y > 0 and new_index >= len(self.reversed_seasons_in_folder):
            # Do nothing and return without changing the focus
            print("DO NOTHING AT THE BOTTOM")
            return

        # Check if the up button is pressed and the new index goes below zero
        elif y < 0 and new_index < 0:
            # Do nothing and return without changing the focus
            print("DO NOTHING AT THE TOP")
            return

        # Check if the focused button is the last visible index and the down button is pressed
        elif y > 0 and self.focused_season_index == self.last_visible_season_index:
            self.scrollUpSeason()

        # Check if the focused button is the first visible index and the up button is pressed
        elif y < 0 and self.focused_season_index == self.first_visible_season_index:
            self.scrollDownSeason()

        # Update the focused index after checking for scrolling
        self.focused_season_index = new_index

        # Set the focus on the new focused button
        self.parent_window.setFocusId(self.season_buttons[self.focused_season_index].getId())

        # Add the focus to the new focused button
        focused_label_text = self.season_buttons[self.focused_season_index].getLabel()
        self.season_buttons[self.focused_season_index].setLabel(focused_label_text)

        # Call the visible_season_buttons_info method after moving focus
        # Exclude calling visible_season_buttons_info when scrolling
        if y == 0:  # Only call when moving focus without scrolling
            self.visible_season_buttons_info()

        # Clear the existing EVENT buttons before adding new ones
        for event_button_control in self.event_buttons:
            self.parent_window.removeControl(event_button_control)
        self.event_buttons.clear()

        # Call the focused_season method after moving focus
        self.focused_season()
    # endregion

    # Scroll up the SEASON buttons by one button height
    # region
    def scrollUpSeason(self):

        for button in self.season_buttons:
            new_y_position = button.getY() - (self.season_button_height)
            button.setPosition(button.getX(), new_y_position)
        
        # Call visible_update after scrolling up
        self.scrollUpSeason_visible_update()

        # Call the focused_season method after scrolling up
        self.focused_season()
    # endregion

    # scrollupSeason visible update
    # region
    def scrollUpSeason_visible_update(self):
        self.focused_season_index += 1
        self.first_visible_season_index += 1
        self.last_visible_season_index += 1
    # endregion

    # Scroll down the SEASON buttons by one button height
    # region
    def scrollDownSeason(self):

        for button in self.season_buttons:
            new_y_position = button.getY() + (self.season_button_height)
            button.setPosition(button.getX(), new_y_position)

        # Call visible_update after scrolling down
        self.scrollDownSeason_visible_update()

        # Call the focused_season method after scrolling down
        self.focused_season()
    # endregion

    # scrollDownSeason visible update
    # region
    def scrollDownSeason_visible_update(self):
        self.focused_season_index -= 1
        self.first_visible_season_index -= 1
        self.last_visible_season_index -= 1
    # endregion

    # Focused season
    # region
    def focused_season(self):
        focused_season_index = self.focused_season_index
        if 0 <= focused_season_index < len(self.reversed_seasons_in_folder):
            self.focused_season_name = self.reversed_seasons_in_folder[focused_season_index]
        else:
            print("No season focused or invalid focused index.")

        # Call the matches_in_season method
        self.matches_in_season()
    # endregion
  
    # endregion

    # EVENT BUTTONS MOVEMENT
    # region

    # visible_event_buttons_info
    # region
    def visible_event_buttons_info(self):

        # Get the total number of buttons available
        num_buttons = len(self.event_buttons)

        # Calculate the number of buttons that can be displayed on the screen at once
        max_visible_buttons = 4

        # Calculate the index of the first visible button based on the focused index
        self.first_visible_event_index = max(0, self.focused_event_index - max_visible_buttons)

        # Calculate the index of the last visible button based on the first visible index
        self.last_visible_event_index = min(num_buttons - 1, self.first_visible_event_index + max_visible_buttons - 1)
    # endregion

    # MOVE EVENT FOCUS BUTTONS 
    # region
    def moveEventFocus(self, x, y):

        new_index = self.focused_event_index + y

        # Update the previously focused season index if moving left from the event button
        if x < 0:
            if self.season_buttons:
                self.parent_window.setFocusId(self.season_buttons[self.previously_focused_season_index].getId())
            return

        # Check if the down button is pressed and the new index exceeds the last available sport index
        if y > 0 and new_index >= len(self.event_buttons):
            # Do nothing and return without changing the focus
            print("DO NOTHING AT THE BOTTOM")
            return

        # Check if the up button is pressed and the new index goes below zero
        elif y < 0 and new_index < 0:
            # Do nothing and return without changing the focus
            print("DO NOTHING AT THE TOP")
            return

        # Check if the focused button is the last visible index and the down button is pressed
        elif y > 0 and self.focused_event_index == self.last_visible_event_index:
            self.scrollUpEvent()

        # Check if the focused button is the first visible index and the up button is pressed
        elif y < 0 and self.focused_event_index == self.first_visible_event_index:
            self.scrollDownEvent()

        # Update the focused index after checking for scrolling
        self.focused_event_index = new_index

        # Set the focus on the new focused button
        self.parent_window.setFocusId(self.event_buttons[self.focused_event_index].getId())

        # Add the focus to the new focused button
        focused_label_text = self.event_buttons[self.focused_event_index].getLabel()
        self.event_buttons[self.focused_event_index].setLabel(focused_label_text)

        # Call the visible_season_buttons_info method after moving focus
        # Exclude calling visible_season_buttons_info when scrolling
        if y == 0:  # Only call when moving focus without scrolling
            self.visible_event_buttons_info()

        # Call the focused_season method after moving focus
        self.focused_event()
    # endregion

    # Scroll up the EVENT buttons by one button height
    # region
    def scrollUpEvent(self):

        # Calculate button size based on screen size (adjust as needed)
        self.event_button_width = (self.window_width * 0.3)
        self.event_button_height = (self.window_height / 4)

        for button in self.event_buttons:
            new_y_position = button.getY() - int(self.event_button_height + 3)
            button.setPosition(button.getX(), new_y_position)
        
        # Call visible_update after scrolling up
        self.scrollUpEvent_visible_update()

        # Call the focused_season method after scrolling up
        self.focused_event()
    # endregion

    # scrollupEvent visible update
    # region
    def scrollUpEvent_visible_update(self):
        self.focused_event_index += 1
        self.first_visible_event_index += 1
        self.last_visible_event_index += 1
    # endregion

    # Focused event
    # region
    def focused_event(self):
        focused_event_index = self.focused_event_index
        if 0 <= focused_event_index < len(self.event_buttons):
            self.focused_event_name = self.event_buttons[focused_event_index]
            # Call the display_team_images method
            self.display_team_images()
        else:
            print("No event focused or invalid focused index.")
    # endregion

    # Scroll down the EVENT buttons by one button height
    # region
    def scrollDownEvent(self):

        for button in self.event_buttons:
            new_y_position = button.getY() + int(self.event_button_height + 10)
            button.setPosition(button.getX(), new_y_position)

        # Call visible_update after scrolling down
        self.scrollDownEvent_visible_update()

        # Call the focused_season method after scrolling down
        self.focused_event()
    # endregion

    # scrollDownSeason visible update
    # region
    def scrollDownEvent_visible_update(self):
        self.focused_event_index -= 1
        self.first_visible_event_index -= 1
        self.last_visible_event_index -= 1
    # endregion

# endregion

    # EVENT CLICK
    # region
    # event_click method
    def event_clicked(self):

        focused_control_id = self.parent_window.getFocusId()

        data = self.event_button_data[focused_control_id]
        match_file = data.get("match_path", "")

        addon = xbmcaddon.Addon()
        sports_folder_path = addon.getSetting('setting1')
        video_path = sports_folder_path + self.sportname + '/' + self.league_name + '/' + self.focused_season_name + '/' + match_file

        # Play the video in the fullscreen dialog
        xbmc.Player().play(video_path)

    # endregion