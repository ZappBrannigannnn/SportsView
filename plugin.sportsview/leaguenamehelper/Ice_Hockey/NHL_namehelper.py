# FILENAMES MUST CONTAIN THE ROUND AND THE NAMES OF THE 2 TEAMS

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

# NHLHelper class
# region
class NHLHelper:
    def __init__(self):
        self.my_matches_seasons_instance = None
# endregion
    
    # Teams Dictionary
    # region
    team_mapping = {
        "Anaheim Ducks": {'team_id': '134846'},
        "Arizona Coyotes": {'team_id': '134847'},
        "Boston Bruins": {'team_id': '134830'},
        "Buffalo Sabres": {'team_id': '134831'},
        "Calgary Flames": {'team_id': '134848'},
        "Carolina Hurricanes": {'team_id': '134838'},
        "Chicago Blackhawks": {'team_id': '134854'},
        "Colorado Avalanche": {'team_id': '134855'},
        "Columbus Blue Jackets": {'team_id': '134839'},
        "Dallas Stars": {'team_id': '134856'},
        "Detroit Red Wings": {'team_id': '134832'},
        "Edmonton Oilers": {'team_id': '134849'},
        "Florida Panthers": {'team_id': '134833'},
        "Los Angeles Kings": {'team_id': '134852'},
        "Minnesota Wild": {'team_id': '134857'},
        "Montreal Canadiens": {'team_id': '134834'},
        "Nashville Predators": {'team_id': '134858'},
        "New Jersey Devils": {'team_id': '134840'},
        "New York Islanders": {'team_id': '134841'},
        "New York Rangers": {'team_id': '134842'},
        "Ottawa Senators": {'team_id': '134835'},
        "Philadelphia Flyers": {'team_id': '134843'},
        "Pittsburgh Penguins": {'team_id': '134844'},
        "San Jose Sharks": {'team_id': '134853'},
        "Seattle Kraken": {'team_id': '140082'},
        "St. Louis Blues": {'team_id': '134859'},
        "St Louis Blues": {'team_id': '134859'},
        "Tampa Bay Lightning": {'team_id': '134836'},
        "Toronto Maple Leafs": {'team_id': '134837'},
        "Vancouver Canucks": {'team_id': '134850'},
        "Vegas Golden Knights": {'team_id': '135913'},
        "Washington Capitals": {'team_id': '134845'},
        "Winnipeg Jets": {'team_id': '134851'},

        "Ducks": {'team_id': '134846'},
        "Coyotes": {'team_id': '134847'},
        "Bruins": {'team_id': '134830'},
        "Sabres": {'team_id': '134831'},
        "Flames": {'team_id': '134848'},
        "Hurricanes": {'team_id': '134838'},
        "Blackhawks": {'team_id': '134854'},
        "Avalanche": {'team_id': '134855'},
        "Blue Jackets": {'team_id': '134839'},
        "Stars": {'team_id': '134856'},
        "Red Wings": {'team_id': '134832'},
        "Oilers": {'team_id': '134849'},
        "Panthers": {'team_id': '134833'},
        "Kings": {'team_id': '134852'},
        "Wild": {'team_id': '134857'},
        "Canadiens": {'team_id': '134834'},
        "Predators": {'team_id': '134858'},
        "Devils": {'team_id': '134840'},
        "Islanders": {'team_id': '134841'},
        "Rangers": {'team_id': '134842'},
        "Senators": {'team_id': '134835'},
        "Flyers": {'team_id': '134843'},
        "Penguins": {'team_id': '134844'},
        "Sharks": {'team_id': '134853'},
        "Kraken": {'team_id': '140082'},
        "Blues": {'team_id': '134859'},
        "Lightning": {'team_id': '134836'},
        "Maple Leafs": {'team_id': '134837'},
        "Canucks": {'team_id': '134850'},
        "Golden Knights": {'team_id': '135913'},
        "Capitals": {'team_id': '134845'},
        "Jets": {'team_id': '134851'},
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

            # USE TEAMS DICTIONARY TO FIND TEAM IDS (DELETE IF NOT A TEAM SPORT)
            # region
            for team_name, team_data in NHLHelper.team_mapping.items(): ### DON'T FORGET TO CHANGE THIS NAME!!!!!!
                if team_name in match.replace(".", "").replace("_", " "):
                    if team01 is None:  # If team01 is not assigned yet
                        team01 = team_data["team_id"]  # Assign the team_id to team01
                    else:
                        team02 = team_data["team_id"]  # Assign the team_id to team02
                        break  # We've found both teams, no need to continue checking
            # endregion
            
            # SEARCH THROUGH THE MATCH FILE NAME FOR THE ROUND NUMBER
            # region
            round_number = None
            round_match = re.search(r"\d{4}-\d{2}-\d{2}|\d{4}\s+\d{2}\s+\d{2}|\d{4}.\d{2}.\d{2}|\d{2}-\d{2}-\d{4}|\d{2}\s+\d{2}\s+\d{4}|\d{2}.\d{2}.\d{4}", match)
            # endregion

            # IF ROUND MATCH HAS A VALUE, THEN CONVERT IT TO ROUND_NUMBER
            # region
            if round_match:
                round_number = (round_match.group(0))
                print("Round number:", round_number)
            else:
                print("Date not found in match:", match)
            # endregion


            print("team01:", team01)
            print("team02:", team02)
            print("round_number:", round_number)



            # IF TEAM01, TEAM02, AND ROUND NUMBER (DATE) IS NOT NONE THEN CALL THE GET_EVENT_ID METHOD
            if team01 is not None and team02 is not None and round_number is not None:
                self.get_event_id(team01, team02, round_number, available_matches, events, match)
            else:
                print("Some information missing in match:", match)
            # endregion
    # endregion

    # get_event_id method
    # region
    def get_event_id(self, team01, team02, round_number, available_matches, events, match):

        # Convert team IDs to strings for accurate comparison (DELETE IF NOT A TEAM SPORT)
        # region
        team01_str = str(team01)
        team02_str = str(team02)
        event_id = None
        # endregion
        
        parsed_round_date_time = parser.parse(round_number, dayfirst=True)

#######

        # Loop through each event in the events list
        for event in events:
            event_home_team = event["idHomeTeam"]
            event_away_team = event["idAwayTeam"]
            event_round_str = event["dateEvent"]

            print("event_home_team:", event_home_team)
            print("event_away_team:", event_away_team)
            print("event_round_str:", event_round_str)
            
            if (event_home_team == team01_str and event_away_team == team02_str) or (event_home_team == team02_str and event_away_team == team01_str):
                event_round = parser.parse(event_round_str).date()

                print("PARSED ROUND DATE:", parsed_round_date_time.date())
                
                if parsed_round_date_time.date() == event_round:
                    event_id = event["idEvent"]
                    print(f"Match found for round {parsed_round_date_time.date()}")
                    break
                else:
                    print("FILENAME ROUND DOESN'T MATCH EVENT DATE")
            else:
                print("FILENAME TEAMS DON'T MATCH EVENT TEAMS")

        # Call the get_event_info method
        if event_id:
            self.get_event_info(team01, team02, round_number, available_matches, events, event_id, match)
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

        round_number = str(round_number)
        
        # Check if the "events" key is present in the JSON data
        if "events" in data:
            # Extract the first event's data (assuming it's an array)
            event_data = data["events"][0]
            # Now you can access different attributes of the event_data dictionary
            
            # Call the create event button start method
            self.get_more_info(event_id, event_data, match, round_number, available_matches, events)

        else:
            # If the "events" key is not found, print an error message
            print("Event data not found for event ID:", event_id)
# endregion

    # Getting image info start
    # region
    def get_more_info(self, event_id, event_data, match, round_number, available_matches, events):

        self.round_number = round_number
        
        # Extract relevant event information from event_data dictionary
        team01ID = event_data.get("idHomeTeam", "")
        team02ID = event_data.get("idAwayTeam", "")
        team01 = event_data.get("strHomeTeam", "")
        team02 = event_data.get("strAwayTeam", "")
        round_number = self.round_number 
        event_thumbnail = event_data.get("strThumb", "")  # EVENT BUTTON IMAGE 
        
        # Generate a label for the event button
        event_label = f"{team01} vs {team02} Round {self.round_number}"

        # Call get_teams_info method for logos badges jerseys backgrounds
        self.get_teams_info(team01, team02, team01ID, team02ID, match, round_number, available_matches, events, event_id, event_data, event_label, event_thumbnail)

        # endregion

    # Get teams info for logos badges jerseys backgrounds
    # region
    def get_teams_info(self, team01, team02, team01ID, team02ID, match, round_number, available_matches, events, event_id, event_data, event_label, event_thumbnail):
        fallback_image = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png")
        hometeam_url = f"https://www.thesportsdb.com/api/v1/json/{self.apikey}/lookupteam.php?id={team01ID}"
        hometeam_response = requests.get(hometeam_url)
        
        if hometeam_response.status_code == 200:
            hometeam_data = hometeam_response.json()
            hometeam_logo = hometeam_data['teams'][0]['strTeamLogo']
            hometeam_badge = hometeam_data['teams'][0]['strTeamBadge']
            hometeam_jersey = hometeam_data['teams'][0]['strTeamJersey']
            hometeam_background = hometeam_data['teams'][0]['strTeamFanart1']

            # Check if any of the images is "null" and use a fallback image if necessary
            hometeam_logo = hometeam_logo if hometeam_logo != None else fallback_image
            hometeam_badge = hometeam_badge if hometeam_badge != None else fallback_image
            hometeam_jersey = hometeam_jersey if hometeam_jersey != None else fallback_image
            hometeam_background = hometeam_background if hometeam_background != None else fallback_image

            # Download and cache the images
            self.download_and_cache_image(hometeam_logo, os.path.join(self.temp_team_folder, f"{team01}_logo.png"))
            self.download_and_cache_image(hometeam_badge, os.path.join(self.temp_team_folder, f"{team01}_badge.png"))
            self.download_and_cache_image(hometeam_jersey, os.path.join(self.temp_team_folder, f"{team01}_jersey.png"))
            self.download_and_cache_image(hometeam_background, os.path.join(self.temp_team_folder, f"{team01}_background.png"))

        awayteam_url = f"https://www.thesportsdb.com/api/v1/json/{self.apikey}/lookupteam.php?id={team02ID}"
        awayteam_response = requests.get(awayteam_url)
        if awayteam_response.status_code == 200:
            awayteam_data = awayteam_response.json()
            awayteam_logo = awayteam_data['teams'][0]['strTeamLogo']
            awayteam_badge = awayteam_data['teams'][0]['strTeamBadge']
            awayteam_jersey = awayteam_data['teams'][0]['strTeamJersey']
            awayteam_background = awayteam_data['teams'][0]['strTeamFanart1']

            # Check if any of the images is "null" and use a fallback image if necessary
            awayteam_logo = awayteam_logo if awayteam_logo != None else fallback_image
            awayteam_badge = awayteam_badge if awayteam_badge != None else fallback_image
            awayteam_jersey = awayteam_jersey if awayteam_jersey != None else fallback_image
            awayteam_background = awayteam_background if awayteam_background != None else fallback_image

            # Download and cache the images
            self.download_and_cache_image(awayteam_logo, os.path.join(self.temp_team_folder, f"{team02}_logo.png"))
            self.download_and_cache_image(awayteam_badge, os.path.join(self.temp_team_folder, f"{team02}_badge.png"))
            self.download_and_cache_image(awayteam_jersey, os.path.join(self.temp_team_folder, f"{team02}_jersey.png"))
            self.download_and_cache_image(awayteam_background, os.path.join(self.temp_team_folder, f"{team02}_background.png"))
        
        VERSUS = "YES"

        # Create an instance of MyMatchesSeasons class
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        my_matches_seasons = MyMatchesSeasons('mymatches.xml', cwd)

        # Call the receive_event_data method from the instance with event-related data
        my_matches_seasons.receive_event_data(team01, team02, round_number, available_matches, events, event_id, event_data, self.my_matches_seasons_instance, match, VERSUS, event_label, event_thumbnail)

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
    
