# FILE NAMES MUST CONTAIN THE DATE, THE NAME OF THE TOURNAMENT, AND THE LAST NAME OF THE PLAYERS WITH "vs" BETWEEN THEM
# FOR EXAMPLE: "ATP.World.Tour.2023-01-02.Adelaide.International.1.Draper.vs.Kwon.mkv" 
# THE DATE CAN BE ANYWHERE. BUT THE PLAYERS' NAMES MUST COME AFTER THE TOURNAMENT NAME AND MUST HAVE "vs" BETWEEN THEM

# IMPORTS
# region
import re
import xbmcaddon
import requests
import base64
from mymatches.mymatchesseasons import MyMatchesSeasons
import xbmcvfs
import os
import shutil
from dateutil import parser
# endregion

# ATPWorldTourHelper class                                               
# region
class ATPWorldTourHelper:                                          
    def __init__(self):
        self.my_matches_seasons_instance = None
# endregion

    # Events Dictionary
    # region
    event_mapping = {
        "Adelaide International 1",
        "Adelaide International 2",
        "Maharashtra Open",
        "ASB Classic",
        "Australian Open",
        "Cordoba Open",
        "Open Sud de France",
        "Dallas Open",
        "Argentina Open",
        "Delray Beach Open",
        "ABN AMRO World Tennis Tournament",
        "Qatar Exxon Mobil Open",
        "Open 13",
        "Rio Open",
        "Dubai Tennis Championships",
        "Chile Open",
        "Abierto Mexicano",
        "BNP Paribas Open",
        "Miami Open",
        "Estoril Open",
        "U.S. Mens Clay Court Championship",
        "Grand Prix Hassan II",
        "Monte Carlo Masters",
        "Barcelona Open",
        "Srpska Open",
        "BMW Open",
        "Mutual Madrid Open",
        "International BNL ditalia",
        "Geneva Open",
        "Lyon Open",
        "French Open",
        "Rosmalen Grass Court Championships",
        "Stuttgart Open",
        "Halle Open",
        "Queens Club Championships",
        "Mallorca Open",
        "Eastbourne International",
        "Wimbledon",
        "Nordea Open",
        "Suisse Open Gstaad",
        "Hall of Fame Championships",
        "Atlanta Open",
        "European Open",
        "Croatian Open",
        "Generali Open",
        "Citi Open",
        "Los Cabos Open",
        "Canadian Open",
        "Western and Southern Financial Group Masters",
        "US Open",
        #### ADD MORE EVENTS HERE ####
    }
    # endregion

    # entry_method method
    # region
    def entry_method(self, focused_season_name, available_matches, id_league, events, my_matches_seasons_instance):
        self.my_matches_seasons_instance = my_matches_seasons_instance
        self.round_number = None
        self.temp_team_folder = my_matches_seasons_instance.temp_team_folder

        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        self.apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

        # Call the get_team_ids_and_round method
        self.get_team_ids_and_round(available_matches, events)
    # endregion

    # get_team_ids_and_round method                                    
    # region
    # region 
    def get_team_ids_and_round(self, available_matches, events):
        # Iterate through the team mapping to find team IDs for the current match
        for match in available_matches:
            team01 = None  # Initialize a placeholder for the first team's ID
            team02 = None  # Initialize a placeholder for the second team's ID
            video_path = match  # Initialize a placeholder for the video path
    # endregion

        # SEARCH THROUGH THE MATCH FILENAME AND GET THE DATE 
        # region 
        round_number = None
        round_match = re.search(r"\d{4}-\d{2}-\d{2}|\d{4}\s+\d{2}\s+\d{2}|\d{4}.\d{2}.\d{2}|\d{2}-\d{2}-\d{4}|\d{2}\s+\d{2}\s+\d{4}|\d{2}.\d{2}.\d{4}", match)

        # IF ROUND MATCH HAS A VALUE, THEN CONVERT IT TO ROUND_NUMBER
        if round_match:
            round_number = (round_match.group(0))
        else:
            print("Date not found in match:", match)
        # endregion

        # SEARCH FILENAME FOR MATCHES IN THE EVENTS DICTIONARY
        # region
        for event_name_pre in ATPWorldTourHelper.event_mapping:
            normalized_event_name = event_name_pre.lower().replace(' ', '').replace('.', '')
            normalized_match = match.lower().replace('.', '')

            if normalized_event_name in normalized_match:

                # Replace periods with spaces in the working_match variable
                working_match, _ = os.path.splitext(match)
                working_match = working_match.replace('.', ' ')

                # Find the index where the event name appears in the working_match
                start_index = working_match.lower().index(event_name_pre.lower())
                
                # Extract characters from working_match starting from the event name to the end
                event_name = working_match[start_index:]

        # endregion

        # IF EVENT NAME AND ROUND NUMBER (DATE) IS NOT NONE THEN CALL THE GET_EVENT_ID METHOD
        # region
        if event_name is not None and round_number is not None:
            self.get_event_id(team01, team02, round_number, available_matches, events, match, event_name)
        else:
            print("Some information missing in match:", match)
        # endregion
    # endregion 

    # get_event_id method                                           
    # region
    def get_event_id(self, team01, team02, round_number, available_matches, events, match, event_name):

        # Loop through each event in the events list                
        # region
        for event in events:
        # endregion

            # region
            event_name_comp = event["strEvent"]
            event_round_str = event["dateEvent"]
            # endregion

            # Check if either home and away teams match team01 and team02, or vice versa (USE IF A TEAM AND DATE ORGANIZED SPORT)
            # region
            match_found = False

            # STRIP AND SAVE THE TOURNAMENT NAME FROM THE EVENT NAME SO I ACCESS AND THEN SWITCH THE PLAYERS' NAMES AROUND IF NEEDED            
            stripped_name = []
            for tournament_name in ATPWorldTourHelper.event_mapping:
                if tournament_name in event_name:
                    event_name_tourn_removed = event_name.replace(tournament_name, "").strip()
                    stripped_name.append(tournament_name)

            # SPLIT THE PLAYERS ON EITHER SIDE OFF THE "vs"
            players = event_name_tourn_removed.split("vs")
            player1 = players[0].strip()
            player2 = players[1].strip()

            # CHECK IF EVENT_NAME (FROM FILENAME) AND EVENT_NAME_COMP (FROM MATCH) MATCH
            if event_name.lower() == event_name_comp.lower():
                print("event_name and event_name_comp match")
                match_found = True
                break  # Exit the loop when a match is found

            # IF THAT DIDN'T WORK FLIP THE PLAYERS' NAMES AND TRY AGAIN
            elif f"{stripped_name[0]} {player2} vs {player1}".lower() == event_name_comp.lower():
                print("event_name and event_name_comp match")
                match_found = True
                break  # Exit the loop when a match is found
            # endregion

        # region   
        if match_found:
            try:
                # Parse the round_number into a datetime object
                parsed_round_date_time = parser.parse(round_number)  
                parsed_round = parsed_round_date_time.date()

                # Convert event_round_str to a datetime object
                event_round = parser.parse(event_round_str)

                # Compare only dates, ignoring the time component
                if parsed_round == event_round.date():
                    event_id = event["idEvent"]
            except ValueError:
                print(f"Invalid date format: {round_number}")
        else:
            # If loop completes without a match, log a message
            print("No matching event found for teams and round.")
        # endregion

        # Call the get_event_info method
        # region
        if event_id:
            self.get_event_info(team01, team02, round_number, available_matches, events, event_id, match)
        # endregion         
    # endregion

    # get_event_info method                                         
    # region
    def get_event_info(self, team01, team02, round_number, available_matches, events, event_id, match):

        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

        event_url = f"https://www.thesportsdb.com/api/v1/json/{apikey}/lookupevent.php?id={event_id}"
        
        # Send an HTTP GET request to the event URL
        response = requests.get(event_url)
        # Parse the response as JSON
        data = response.json()

        # Check if the "events" key is present in the JSON data
        if "events" in data:
            # Extract the first event's data (assuming it's an array)
            event_data = data["events"][0]
            # Now you can access different attributes of the event_data dictionary
            
            # Call the create event button start method
            self.get_more_info(event_id, event_data, match, round_number, available_matches, events, event_url)

        else:
            # If the "events" key is not found, print an error message
            print("Event data not found for event ID:", event_id)
# endregion

    # Getting image info start
    # region
    def get_more_info(self, event_id, event_data, match, round_number, available_matches, events, event_url):
        
        # Extract relevant event information from event_data dictionary
        team01ID = None
        team02ID = None
        team01 = None
        team02 = None
        event_thumbnail = event_data.get("strThumb", "")  # EVENT BUTTON IMAGE 
        
        # Generate a label for the event button
        event_label = event_data.get("idEvent", "")

        # Call get_teams_info method for logos badges jerseys backgrounds
        self.get_teams_info(team01, team02, team01ID, team02ID, match, round_number, available_matches, events, event_id, event_data, event_label, event_thumbnail, event_url)
        # endregion

    # Get teams info for logos badges jerseys backgrounds (USE IF NOT A TEAM SPORT)
    # region
    def get_teams_info(self, team01, team02, team01ID, team02ID, match, round_number, available_matches, events, event_id, event_data, event_label, event_thumbnail, event_url):
        fallback_image = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png")
        event_response = requests.get(event_url)
        
        if event_response.status_code == 200:
            event_get_data = event_response.json()
            event_banner = event_get_data['events'][0]['strBanner']
            event_poster = event_get_data['events'][0]['strPoster']
            event_thumb = event_get_data['events'][0]['strThumb']

            # Check if any of the images is "null" and use a fallback image if necessary
            event_banner = event_banner if event_banner != None else fallback_image
            event_poster = event_poster if event_poster != None else fallback_image
            event_thumb = event_thumb if event_thumb != None else fallback_image

            # Download and cache the images
            self.download_and_cache_image(event_banner, os.path.join(self.temp_team_folder, f"{event_id}_banner.png"))
            self.download_and_cache_image(event_poster, os.path.join(self.temp_team_folder, f"{event_id}_poster.png"))
            self.download_and_cache_image(event_thumb, os.path.join(self.temp_team_folder, f"{event_id}_thumb.png"))

        # Sports that requires the VERSUS Bar to be displayed
        VERSUS = "NO"

        # Create an instance of MyMatchesSeasons class
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        my_matches_seasons = MyMatchesSeasons('mymatches.xml', cwd)

        # Call the receive_event_data method from the instance with event-related data
        my_matches_seasons.receive_event_data(team01, team02, round_number, available_matches, events, event_id, event_data, self.my_matches_seasons_instance, match, VERSUS, event_label, event_thumbnail)
    # endregion

    # Download and cache logos badges jerseys backgrounds (NO CHANGES REQUIRED)
    # region
    def download_and_cache_image(self, url, save_path):
        if url and not os.path.exists(save_path):
            if url.endswith("imagenotavailable.png"):
                # Copy the local file to the specified save_path
                source_path = url
                shutil.copyfile(source_path, save_path)
                print(f"Local file copied and cached: {save_path}")
            else:
                # It's a remote URL, perform the HTTP request
                response = requests.get(url)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                        print(f"Image downloaded and cached: {save_path}")
                else:
                    print(f"Failed to download image: {url}")
        else:
            print(f"Image already cached or URL is empty: {save_path}")
    # endregion