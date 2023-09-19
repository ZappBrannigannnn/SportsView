# Imports
# region
import xbmcgui
import xbmc
from mysports.mysportsbuttons import MySportsButtons
# endregion

# Class MySportsWindow
# region
class MySportsWindow(xbmcgui.WindowXML):
    def __init__(self, window_manager, *args, **kwargs):
        # Initialize the window and other stuff
        super(MySportsWindow, self).__init__(*args, **kwargs)
        self.sports_buttons = MySportsButtons(self, window_manager)
# endregion

    # onInit (stuff that happens on initialization)
    # region
    def onInit(self):
        xbmc.log("MySportsWindow - onInit")

        # Call the method to fetch sports data and create buttons
        self.sports_buttons.fetch_sports_data()

        # Display the buttons on the my sports window
        self.sports_buttons.display_buttons()

        # Display the image
        self.sports_buttons.update_displayed_image()
    # endregion

    # onAction method in this class to handle the button action
    # region
    def onAction(self, action):
        print("ON ACTION")
        if action == xbmcgui.ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_MOVE_LEFT:
            # Call the method in MySportsButtons to move the focus left
            self.sports_buttons.moveFocus(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            # Call the method in MySportsButtons to move the focus right
            self.sports_buttons.moveFocus(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            # Call the method in MySportsButtons to move the focus up
            self.sports_buttons.moveFocus(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            # Call the method in MySportsButtons to move the focus down
            self.sports_buttons.moveFocus(0, 1)
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            # Pass the controlId of the clicked button to the onClick method
            focused_button_id = self.getFocusId()
            self.sports_buttons.onClick(focused_button_id)
        else:
            pass
    # endregion