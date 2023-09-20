# IMPORTS
# region
import re
import xbmcaddon
import requests
import base64
from mymatches.mymatchesseasons import MyMatchesSeasons
from dateutil import parser

# endregion

# MLBHelper class
# region
class MLBHelper:
    def __init__(self):
        self.my_matches_seasons_instance = None
# endregion
    
    # Teams Dictionary
    # region
    team_mapping = {
        "Diamondbacks": {'team_id': '135267'},
        "Braves": {'team_id': '135268'},
        "Orioles": {'team_id': '135251'},
        "Red Sox": {'team_id': '135252'},
        "Cubs": {'team_id': '135269'},
        "White Sox": {'team_id': '135253'},
        "Reds": {'team_id': '135270'},
        "Guardians": {'team_id': '135254'},
        "Rockies": {'team_id': '135271'},
        "Tigers": {'team_id': '135255'},
        "Astros": {'team_id': '135256'},
        "City Royals": {'team_id': '135257'},
        "Angels": {'team_id': '135258'},
        "Dodgers": {'team_id': '135272'},
        "Marlins": {'team_id': '135273'},
        "Brewers": {'team_id': '135274'},
        "Twins": {'team_id': '135259'},
        "Mets": {'team_id': '135275'},
        "Yankees": {'team_id': '135260'},
        "Athletics": {'team_id': '135261'},
        "Phillies": {'team_id': '135276'},
        "Pirates": {'team_id': '135277'},
        "Padres": {'team_id': '135278'},
        "Giants": {'team_id': '135279'},
        "Mariners": {'team_id': '135262'},
        "Cardinals": {'team_id': '135280'},
        "Rays": {'team_id': '135263'},
        "Rangers": {'team_id': '135264'},
        "Blue Jays": {'team_id': '135265'},
        "Nationals": {'team_id': '135281'},
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
            for team_name, team_data in MLBHelper.team_mapping.items():
                if team_name in match:
                    if team01 is None:  # If team01 is not assigned yet
                        team01 = team_data["team_id"]  # Assign the team_id to team01
                    else:
                        team02 = team_data["team_id"]  # Assign the team_id to team02
                        break  # We've found both teams, no need to continue checking
            
            round_number = None
            round_match = re.search(r"\d{4}-\d{2}-\d{2}|\d{4}\s+\d{2}\s+\d{2}|\d{2}-\d{2}-\d{4}|\d{2}\s+\d{2}\s+\d{4}", match)

            if round_match:
                round_number = (round_match.group(0))
            else:
                print("Date not found in match:", match)

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
            event_round_str = (event["dateEvent"])

            # Check if either home and away teams match team01 and team02, or vice versa
            if (event_home_team == team01_str and event_away_team == team02_str) or (event_home_team == team02_str and event_away_team == team01_str):
                try:
                    # Parse the round_number into a datetime object
                    parsed_round_date_time = parser.parse(round_number, dayfirst=True)  # Set dayfirst=True for DD-MM-YYYY format
                    parsed_round = parsed_round_date_time.date

                    # Convert event_round_str to a datetime object
                    event_round = parser.parse(event_round_str)

                    # Compare only dates, ignoring the time component
                    if parsed_round() == event_round.date():
                        event_id = event["idEvent"]
                        print(f"Match found for round {parsed_round}")
                        break
                except ValueError:
                    print(f"Invalid date format: {round_number}")

        else:
            # If loop completes without a match, log a message
            print("No matching event found for teams and round.")

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