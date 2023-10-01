import xbmcgui

class MyCustomDialog(xbmcgui.WindowDialog):
    def __init__(self):
        # Initialize the dialog window
        super(MyCustomDialog, self).__init__()

        # Create a label control to display a message
        self.label = xbmcgui.ControlLabel(50, 50, 500, 30, "Hello, Custom Dialog!", "font13", "0xFFFFFF00")
        self.addControl(self.label)

# Function to show the dialog
def show_custom_dialog():
    dialog = MyCustomDialog()
    dialog.doModal()
