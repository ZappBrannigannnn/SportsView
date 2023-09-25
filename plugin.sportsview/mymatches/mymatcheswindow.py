# INITIAL STUFF
# region

# IMPORTS
# region
import xbmcgui
import xbmc
import xbmcaddon
from mymatches.mymatchesseasons import MyMatchesSeasons
# endregion

# MYMATCHESWINDOW CLASS
# region
class MyMatchesWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.sportname = kwargs.get('sportname')
        self.league_name = kwargs.get('league_name')

        # Initialize the window and other stuff
        super(MyMatchesWindow, self).__init__(*args, **kwargs)

        # Pass the required arguments to MyLeaguesButtons
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        self.matches_seasons = MyMatchesSeasons('mymatches.xml', cwd, sportname=self.sportname , league_name=self.league_name)
        self.matches_seasons.set_parent_window(self) # Set the parent_window attribute

# endregion

# endregion
  
    # onInit method
    # region
    def onInit(self):
        xbmc.log("MyMatchesWindow - onInit")

        # Check if the window has already been initialized
        if not hasattr(self, 'initialized') or not self.initialized:

            # Call the seasons_in_league_folder method
            self.matches_seasons.seasons_in_league_folder()

            # Call the create_season_buttons method
            self.matches_seasons.create_season_buttons()

            # Call the focused_season method
            self.matches_seasons.focused_season()

            # Call the display_bar method
            self.matches_seasons.display_bar()

            # Display the buttons on the my sports window
            self.matches_seasons.display_season_buttons()

            # Call the visible_seasons_buttons_info method
            self.matches_seasons.visible_season_buttons_info()

            # Call the visible_events_buttons_info method
            self.matches_seasons.visible_event_buttons_info()

            # Set the initialization flag
            self.initialized = True
    # endregion

    # onAction method in this class to handle the button action
    # region
    def onAction(self, action):
        
        focused_control_id = self.matches_seasons.parent_window.getFocusId()

        if action == xbmcgui.ACTION_NAV_BACK:
            if focused_control_id in [button.getId() for button in self.matches_seasons.season_buttons]:
                self.close()
            elif focused_control_id in [button.getId() for button in self.matches_seasons.event_buttons]:
                self.matches_seasons.parent_window.setFocusId(self.matches_seasons.season_buttons[self.matches_seasons.previously_focused_season_index].getId())
            return

        elif action == xbmcgui.ACTION_MOVE_LEFT:
            # Call the method in MySportsButtons to move the focus left
            self.matches_seasons.season_or_event(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            # Call the method in MySportsButtons to move the focus right
            self.matches_seasons.season_or_event(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            # Call the method in MySportsButtons to move the focus up
            self.matches_seasons.season_or_event(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            # Call the method in MySportsButtons to move the focus down
            self.matches_seasons.season_or_event(0, 1)

        elif action == xbmcgui.ACTION_SELECT_ITEM:
            if focused_control_id in [button.getId() for button in self.matches_seasons.season_buttons]:
                if self.matches_seasons.event_buttons:
                    self.matches_seasons.previously_focused_season_index = self.matches_seasons.focused_season_index
                    self.matches_seasons.parent_window.setFocusId(self.matches_seasons.event_buttons[0].getId())
                    self.matches_seasons.focused_event()
            elif focused_control_id in [button.getId() for button in self.matches_seasons.event_buttons]:
                self.matches_seasons.event_clicked()
            return
        else:
            pass
    # endregion

