#IMPORTS
# region
import xbmcgui
import xbmcaddon
import time
from landingpage.landingpage import LandingPageWindow
from allsports.allsportswindow import AllSportsWindow
from myleagues.myleagueswindow import MyLeaguesWindow
from mysports.mysportswindow import MySportsWindow
from mymatches.mymatcheswindow import MyMatchesWindow
# endregion

# Class WINDOWMANAGER
# region
class WindowManager:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.cwd = self.addon.getAddonInfo('path')
        self.current_window = None
        self.window_initialized = None
# endregion

# PAGES
# region

    # LANDING PAGE
    # region
    def show_landing_page(self):
        print("WINDOW MANAGER: LAUNCH LANDING PAGE")
        # Create and show the landing page window
        self.close_current_window()

        # Check if the window has already been initialized
        if self.window_initialized != "Landing":
            # Create and show the landing page window
            self.current_window = LandingPageWindow('landingpage.xml', self.cwd, 'default', '1080i')
            self.window_initialized = "Landing"  # Set the flag to True
            self.current_window.doModal()
        else:
            # Window has already been initialized, no need to recreate it
            self.current_window.setFocus()
    # endregion

    # ALL SPORTS PAGE
    # region
    def show_all_sports_page(self):
        print("WINDOW MANAGER: LAUNCH ALL SPORTS PAGE")
        # Create and show the All Sports page window
        self.close_current_window()

        # Check if the window has already been initialized
        if self.window_initialized != "AllSports":
            # Create and show the All Sports page window
            self.current_window = AllSportsWindow('allsports.xml', self.cwd, 'default', '1080i')
            self.window_initialized = AllSports  # Set the flag to True
            self.current_window.doModal()
        else:
            # Window has already been initialized, no need to recreate it
            self.current_window.setFocus()
    # endregion

    # MY SPORTS PAGE
    # region
    def show_my_sports_page(self):
        print("WINDOW MANAGER: LAUNCH MY SPORTS PAGE")
        # Create and show the My Sports page window
        self.close_current_window()

        # Check if the window has already been initialized
        if self.window_initialized != "MySports":
            # Create and show the My Sports page window
            self.current_window = MySportsWindow('mysports.xml', self.cwd, 'default', '1080i')
            self.window_initialized = "MySports"  # Set the flag to True
            self.current_window.doModal()
        else:
            # Window has already been initialized, no need to recreate it
            self.current_window.setFocus()
    # endregion

    # MY LEAGUES PAGE
    # region
    def show_my_leagues_page(self, sportname):
        print("WINDOW MANAGER: LAUNCH MY LEAGUES PAGE")
        # Create and show the My Leagues page window
        self.close_current_window()

        # Check if the window has already been initialized
        if self.window_initialized != "MyLeagues":
            # Create and show the My Leagues page window
            self.current_window = MyLeaguesWindow('myleagues.xml', self.cwd, 'default', '1080i', sportname=sportname)
            self.window_initialized = "MyLeagues"  # Set the flag to True
            self.current_window.doModal()
        else:
            # Window has already been initialized, no need to recreate it
            self.current_window.setFocus()
    # endregion

    # MY MATCHES PAGE
    # region
    def show_my_matches_page(self, focused_league_name, sportname):
        print("WINDOW MANAGER: LAUNCH MY MATCHES PAGE")
        # Create and show the My Matches page window
        self.close_current_window()

        # Check if the window has already been initialized
        if self.window_initialized != "MyMatches":
            # Create and show the My Matches page window
            self.current_window = MyMatchesWindow('mymatches.xml', self.cwd, 'default', '1080i', sportname=sportname, league_name=focused_league_name)
            self.window_initialized = "MyMatches"  # Set the flag to True
            self.current_window.doModal()
        else:
            # Window has already been initialized, no need to recreate it
            self.current_window.setFocus()
    # endregion

    # CLOSE CURRENT WINDOW
    # region
    def close_current_window(self):
        print("WINDOW MANAGER: CLOSE PAGE")  
        # Close the current window if it exists
        if self.current_window:
            self.current_window.close()
            self.current_window = None
    # endregion

# endregion