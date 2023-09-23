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

# EnglishPremierLeagueHelper class
# region
class EnglishPremierLeagueHelper:
    def __init__(self):
        self.my_matches_seasons_instance = None
# endregion
    
    # Teams Dictionary
    # region
    team_mapping = {
        "Arsenal": {'team_id': '133604'},
        "Aston Villa": {'team_id': '133601'},
        "Bournemouth": {'team_id': '134301'},
        "Brentford": {'team_id': '134355'},
        "Brighton": {'team_id': '133619'},
        "Burnley": {'team_id': '133623'},
        "Chelsea": {'team_id': '133610'},
        "Crystal Palace": {'team_id': '133632'},
        "Everton": {'team_id': '133615'},
        "Fulham": {'team_id': '133600'},
        "Liverpool": {'team_id': '133602'},
        "Luton": {'team_id': '133888'},
        "Manchester City": {'team_id': '133613'},
        "Manchester United": {'team_id': '133612'},
        "Newcastle": {'team_id': '134777'},
        "Nottingham Forest": {'team_id': '133720'},
        "Sheffield United": {'team_id': '133811'},
        "Tottenham": {'team_id': '133616'},
        "West Ham": {'team_id': '133636'},
        "Wolves": {'team_id': '133599'},

        "Hove Albion": {'team_id': '133619'},
        "Wolverhampton": {'team_id': '133599'},
        "Wanderers": {'team_id': '133599'},
        "Southampton": {'team_id': '134778'},
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
            for team_name, team_data in EnglishPremierLeagueHelper.team_mapping.items(): ### DON'T FORGET TO CHANGE THIS NAME!!!!!!
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
            round_match = re.search(r"Round (\d+)|(\d+) Round|R\d{2}|R_(\d+)", match)
            # endregion

            # IF ROUND MATCH HAS A VALUE, THEN CONVERT IT TO ROUND_NUMBER
            # region
            if round_match:
                # Check which part of the regex matched
                if round_match.group(0):
                    round_number = round_match.group(0)
                elif round_match.group(1):
                    round_number = round_match.group(1)
                elif round_match.group(2):
                    round_number = round_match.group(2)
                elif round_match.group(3):
                    round_number = round_match.group(3)
            else:
                print("Round number not found in match:", match)
            
            # remove all non-numeric characters
            round_number = ''.join(filter(str.isdigit, round_number))
            # endregion

            # IF TEAM01, TEAM02, AND ROUND_NUMBER ARE NOT NONE THEN CALL THE GET_EVENT_ID METHOD
            # region

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
        round_number = int(round_number)

        # endregion
        
        # Loop through each event in the events list
        for event in events:
            event_home_team = event["idHomeTeam"]
            event_away_team = event["idAwayTeam"]

            match_found = False

            # Check if either home and away teams match team01 and team02, or vice versa
            if (event_home_team == team01_str and event_away_team == team02_str) or (event_home_team == team02_str and event_away_team == team01_str):
                event_round = int(event["intRound"])
                match_found = True
                
                # Check if the event's round matches the provided round_number
                if match_found:
                    if event_round == round_number:

                        event_id = event["idEvent"]  # Access the event ID

                        # Call the get_event_info method
                        self.get_event_info(team01, team02, round_number, available_matches, events, event_id, match)
                        break

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

        round_number = "Round " + str(round_number)
        
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
    
