# IMPORTS
# region
import re
import xbmcaddon
import requests
import base64
from mymatches.mymatchesseasons import MyMatchesSeasons
# endregion

# AustralianNationalRugbyLeagueHelper class
# region
class AustralianNationalRugbyLeagueHelper:
    def __init__(self):
        self.my_matches_seasons_instance = None
# endregion
    
    # Teams Dictionary
    # region
    team_mapping = {
        "Eels": {"team_id": 135183},
        "Sharks": {"team_id": 135184},
        "Rabbitohs": {"team_id": 135185},
        "Raiders": {"team_id": 135186},
        "Bulldogs": {"team_id": 135187},
        "Sea Eagles": {"team_id": 135188},
        "Tigers": {"team_id": 135189},
        "Storm": {"team_id": 135190},
        "Broncos": {"team_id": 135191},
        "Roosters": {"team_id": 135192},
        "Warriors": {"team_id": 135193},
        "Titans": {"team_id": 135194},
        "Dragons": {"team_id": 135195},
        "Cowboys": {"team_id": 135196},
        "Panthers": {"team_id": 135197},
        "Knights": {"team_id": 135198},
        "Dolphins": {"team_id": 147022},

        "Parramatta": {"team_id": 135183},
        "Cronulla": {"team_id": 135184},
        "South Sydney": {"team_id": 135185},
        "Canberra": {"team_id": 135186},
        "Canterbury": {"team_id": 135187},
        "Bankstown": {"team_id": 135187},
        "Manly": {"team_id": 135188},
        "Wests": {"team_id": 135189},
        "Melbourne": {"team_id": 135190},
        "Brisbane": {"team_id": 135191},
        "Sydney": {"team_id": 135192},
        "New Zealand": {"team_id": 135193},
        "Gold Coast": {"team_id": 135194},
        "St. George": {"team_id": 135195},
        "Illawarra": {"team_id": 135195},
        "North Queensland": {"team_id": 135196},
        "Penrith": {"team_id": 135197},
        "Newcastle": {"team_id": 135198},
        "Redcliffe": {"team_id": 147022},
    }
    # endregion

    # entry_method method
    # region
    def entry_method(self, focused_season_name, available_matches, id_league, events, my_matches_seasons_instance):
        self.my_matches_seasons_instance = my_matches_seasons_instance

        # Call the get_team_ids_and_round method
        self.get_team_ids_and_round(available_matches, events)
    # endregion

    # get_team_ids_and_round method
    # region
    def get_team_ids_and_round(self, available_matches, events):
        for match in available_matches:
            team01 = None  # Initialize a placeholder for the first team's ID
            team02 = None  # Initialize a placeholder for the second team's ID
            video_path = match  # Initialize a placeholder for the video path
            
            # Iterate through the team mapping to find team IDs for the current match
            for team_name, team_data in AustralianNationalRugbyLeagueHelper.team_mapping.items():
                if team_name in match:
                    if team01 is None:  # If team01 is not assigned yet
                        team01 = team_data["team_id"]  # Assign the team_id to team01
                    else:
                        team02 = team_data["team_id"]  # Assign the team_id to team02
                        break  # We've found both teams, no need to continue checking
            
            round_number = None
            round_match = re.search(r"Round (\d+)", match)
            if round_match:
                round_number = int(round_match.group(1))
            else:
                print("Round number not found in match:", match)

            if team01 is not None and team02 is not None and round_number is not None:
                self.get_event_id(team01, team02, round_number, available_matches, events, match)
            else:
                print("Some information missing in match:", match)
    # endregion

    # get_event_id method
    # region
    def get_event_id(self, team01, team02, round_number, available_matches, events, match):

        # Convert team IDs to strings for accurate comparison
        team01_str = str(team01)
        team02_str = str(team02)

        # Loop through each event in the events list
        for event in events:
            event_home_team = event["idHomeTeam"]
            event_away_team = event["idAwayTeam"]
            event_round = int(event["intRound"])

            # Check if either home and away teams match team01 and team02, or vice versa
            if (event_home_team == team01_str and event_away_team == team02_str) or (event_home_team == team02_str and event_away_team == team01_str):
                
                # Check if the event's round matches the provided round_number
                if event_round == round_number:
                    event_id = event["idEvent"]  # Access the event ID
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

        # Your encryption key (keep it secret)
        encryption_key = b'ZappBSportsVAPI6'

        # Encrypted API key from settings.xml
        addon = xbmcaddon.Addon()
        encrypted_api_key = addon.getSetting('setting2')

        apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

        event_url = f"https://www.thesportsdb.com/api/v1/json/{apikey}/lookupevent.php?id={event_id}"
        
        # Create an instance of MyMatchesSeasons class
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        my_matches_seasons = MyMatchesSeasons('mymatches.xml', cwd)

        # Send an HTTP GET request to the event URL
        response = requests.get(event_url)
        # Parse the response as JSON
        data = response.json()
        
        # Check if the "events" key is present in the JSON data
        if "events" in data:
            # Extract the first event's data (assuming it's an array)
            event_data = data["events"][0]
            # Now you can access different attributes of the event_data dictionary
            
            # Call the receive_event_data method from the instance with event-related data
            my_matches_seasons.receive_event_data(team01, team02, round_number, available_matches, events, event_id, event_data, self.my_matches_seasons_instance, match)

        else:
            # If the "events" key is not found, print an error message
            print("Event data not found for event ID:", event_id)
            
# endregion