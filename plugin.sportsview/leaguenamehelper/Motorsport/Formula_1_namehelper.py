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
# endregion

# Formula1Helper class
# region
class Formula1Helper:
    def __init__(self):
        self.my_matches_seasons_instance = None
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
    def get_team_ids_and_round(self, available_matches, events):

        # NOT USED BUT NEED TO BE PASSED
        team01 = None
        team02 = None

        for match in available_matches:
            race_type = None
            video_path = match  # Initialize a placeholder for the video path
            
            # Iterate through the team mapping to find team IDs for the current match
            RACE = re.search(r"RACE|Grand Prix", match)
            if RACE is not None:
                race_type = "RACE"
            else:
                FP1 = re.search(r"FP1|FP01|Free Practice One|Free.Practice.One", match)
                if FP1 is not None:
                    race_type = "FP1"
                else:
                    FP2 = re.search(r"FP2|FP02|Free Practice Two|Free.Practice.Two", match)
                    if FP2 is not None:
                        race_type = "FP2"
                    else:
                        FP3 = re.search(r"FP3|FP03|Free Practice Three|Free.Practice.Three", match)
                        if FP3 is not None:
                            race_type = "FP3"
                        else:
                            QUALY = re.search(r"QUALY|Qualy|Qualifying|qualifying", match)
                            if QUALY is not None:
                                race_type = "QUALY"                            
                            else:
                                SPRINT = re.search(r"SPRINT|Sprint", match)
                                if SPRINT is not None:
                                    race_type = "SPRINT"                                
                                else:
                                    print("Race type not found in match:", match)

            round_number_with_words = None
            round_match = re.search(r"Round (\d+)|Round(\d+)|R\d{2}", match)
            if round_match:
                round_number_with_words = (round_match.group(0))
                round_number = int(re.sub(r'\D|^0+', '', round_number_with_words))
                print("Round number:", round_number)   
            else:
                print("Round number not found in match:", match)

            if round_number is not None:
                self.get_event_id(team01, team02, round_number, available_matches, events, match, race_type)
            else:
                print("Some information missing in match:", match)
    # endregion

    # get_event_id method
    # region
    def get_event_id(self, team01, team02, round_number, available_matches, events, match, race_type):

        # Loop through each event in the events list
        for event in events:
            event_round = int(event["intRound"])

            # is Grand Prix or Practice 1 or Practice 2 or Practice 3 or Qualifying or Sprint is strEvent?
            event_type_full = event["strEvent"]

            # Iterate through the team mapping to find team IDs for the current match
            FP1 = re.search(r"Practice 1", event_type_full)
            if FP1 is not None:
                event_type = "FP1"
            else:
                FP2 = re.search(r"Practice 2", event_type_full)
                if FP2 is not None:
                    event_type = "FP2"
                else:
                    FP3 = re.search(r"Practice 3", event_type_full)
                    if FP3 is not None:
                        event_type = "FP3"
                    else:
                        QUALY = re.search(r"Qualifying", event_type_full)
                        if QUALY is not None:
                            event_type = "QUALY"                            
                        else:
                            SPRINT = re.search(r"Sprint", event_type_full)
                            if SPRINT is not None:
                                event_type = "SPRINT"                                
                            else:
                                RACE = re.search(r"Grand Prix", event_type_full)
                                if RACE is not None:
                                    event_type = "RACE"
                                else:
                                    print("Race type not found in match:", event_type_full)

            if race_type == event_type:

                # Check if the event's round matches the provided round_number
                if event_round == round_number:
                    event_id = event["idEvent"]  # Access the event ID
                    print("Event ID:", event_id)
                    break  # Exit the loop, a match is found
        else:
            # If loop completes without a match, log a message
            print("No matching event found for teams and round.")

        # Call the get_event_info method
        self.get_event_info(team01, team02, round_number, available_matches, events, event_id, match)
    # endregion          

    # get_event_info method
    # region
    def get_event_info(self, team01, team02, round_number, available_matches, events, event_id, match):
        print("GET EVENT INFO RUNNING")

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
        print("GET MORE INFO RUNNING")
        
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

    # Get teams info for logos badges jerseys backgrounds
    # region
    def get_teams_info(self, team01, team02, team01ID, team02ID, match, round_number, available_matches, events, event_id, event_data, event_label, event_thumbnail, event_url):
        print("GET TEAMS INFO RUNNING")
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
        my_matches_seasons.receive_event_data(team01, team02, round_number, available_matches, events, event_id, event_data, self.my_matches_seasons_instance, match, VS, event_label, event_thumbnail)
    # endregion

    # Download and cache logos badges jerseys backgrounds
    # region
    def download_and_cache_image(self, url, save_path):
        if not os.path.exists(save_path):
            if url.endswith("imagenotavailable.png"):  # Check if it's a local file
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
            print(f"Image already cached: {save_path}")
    # endregion
