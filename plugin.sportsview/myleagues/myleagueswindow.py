# IMPORTS
# region
import xbmcgui
import xbmc
import xbmcaddon
from myleagues.myleaguesbuttons import MyLeaguesButtons
# endregion

# MyLeaguesWindow class
# region
class MyLeaguesWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.sportname = kwargs.get('sportname')

        # Initialize the window and other stuff
        super(MyLeaguesWindow, self).__init__(*args, **kwargs)

        # Pass the required arguments to MyLeaguesButtons
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        self.leagues_buttons = MyLeaguesButtons('myleagues.xml', cwd, sportname=self.sportname)
        self.leagues_buttons.set_parent_window(self)  # Set the parent_window attribute
# endregion

    # onInit method
    # region
    def onInit(self):
        xbmc.log("MyLeaguesWindow - onInit")

        # Calculate button sizes
        self.leagues_buttons.calculate_button_size()

        # Call the leagues_in_sport_folder method
        self.leagues_buttons.leagues_in_sport_folder()

        # Call the new_or_cached method
        self.leagues_buttons.new_or_cached()

        # Call the new_or_cached_banner method
        self.leagues_buttons.new_or_cached_banner()

        # Call the new_or_cached_description method
        self.leagues_buttons.new_or_cached_description()

        # Call the display_buttons method to display the buttons
        self.leagues_buttons.display_buttons()

        # Call the visible_buttons_info method
        self.leagues_buttons.visible_buttons_info()
    # endregion

    # onAction method in this class to handle the button action
    # region
    def onAction(self, action):
        if action == xbmcgui.ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_MOVE_LEFT:
            # Call the method in MyLeaguesButtons to move the focus left
            self.leagues_buttons.moveFocus(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            # Call the method in MyLeaguesButtons to move the focus right
            self.leagues_buttons.moveFocus(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            # Call the method in MyLeaguesButtons to move the focus up
            self.leagues_buttons.moveFocus(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            # Call the method in MyLeaguesButtons to move the focus down
            self.leagues_buttons.moveFocus(0, 1)
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            # Pass the controlId of the clicked button to the onClick method
            focused_button_id = self.getFocusId()
            self.leagues_buttons.onClick(focused_button_id)
        else:
            pass
    # endregion

    # onClick method
    # region
    def onClick(self, controlId):
        # Handle button clicks here (e.g., when a sport button is clicked on the My Leagues page)
        pass
    # endregion
