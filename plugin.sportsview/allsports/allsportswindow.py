# Imports
# region
import xbmcgui
import xbmcaddon
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests
import os
import xbmcvfs
import xbmc
import time
from allsports.allsportsapi import SportsAPI
# endregion

# Class AllSportsWindow
# region
class AllSportsWindow(xbmcgui.WindowXML):

    addon = xbmcaddon.Addon()
    apikey = addon.getSetting('setting2')

    API_URL = F"https://www.thesportsdb.com/api/v1/json/{apikey}/all_sports.php"
    FALLBACK_IMAGE_PATH = xbmcvfs.translatePath("special://home/addons/plugin.sportsview/allsports/media/imagenotavailable.png")
    CACHE_DIR = xbmcvfs.translatePath("special://home/temp/sportsview/allsports_cache")

    # Create the cache folder if it doesn't exist
    if not xbmcvfs.exists(CACHE_DIR):
        xbmcvfs.mkdirs(CACHE_DIR)

    CACHE_EXPIRY = 604800  # Cache expiry time in seconds

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        self.font_path = "special://home/addons/plugin.sportsview/resources/fonts/ariblk.ttf"
        self.font_size = 40
        self.line_spacing = 1
        self.num_columns = 4
        self.num_rows = 4
        self.num_buttons = 0
        self.first_visible_button_index = 0
        self.last_visible_button_index = 0
        self.controls = []
        self.vert_gap_size = 10  # Define the vertical gap size here
        self.loading_dialog = None
    # endregion

    # onInit
    # region
    def onInit(self):
        xbmc.log("AllSportsWindow - onInit")
        sports_data = self.getSportsData()
        total_buttons = len(sports_data)  # Get the total number of buttons in sports_data
        self.showLoadingDialog(total_buttons)  # Pass the total_buttons to the loading dialog
        self.populate_sports_grid(sports_data)
    # endregion

    # tempPath
    # region
    def tempPath(self):
        return xbmcvfs.translatePath("special://temp/")
    # endregion

    # getSportsData
    # region
    def getSportsData(self):
        sports_api = SportsAPI(self.API_URL)
        return sports_api.get_sports_data()
    # endregion

    # showLoadingDialog
    # region
    def showLoadingDialog(self, total_buttons):
        # Create a dialog window
        dialog = xbmcgui.DialogProgressBG()
        dialog.create('Loading', 'Please wait...')
        self.loading_dialog = dialog
        self.total_buttons = total_buttons
        self.buttons_loaded = 0
        dialog.update(0)  # Initialize the progress bar to 0%
    # endregion

    # populate_sports_grid
    # region
    def populate_sports_grid(self, sports_data):
        vert_gap_size = 50
        horiz_gap_size = 10
        total_vert_gap_size = vert_gap_size * (self.num_rows + 1)
        screen_width = self.getWidth()
        button_width = (screen_width - total_vert_gap_size) // self.num_columns
        button_height = int(button_width / 1.7777777777777)
        self.num_visible_rows = self.getHeight() // (button_height + horiz_gap_size)
        available_height = self.getHeight() - (horiz_gap_size * (self.num_visible_rows - 1))
        button_height_with_gap = available_height // self.num_visible_rows
        self.num_buttons = len(sports_data)
        self.num_rows = (self.num_buttons + self.num_columns - 1) // self.num_columns
        self.first_visible_button_index = 0
        self.last_visible_button_index = self.num_visible_rows * self.num_columns - 1
        font = ImageFont.truetype(self.font_path, self.font_size)

        print("TOTAL NUMBER OF BUTTONS", self.num_buttons)
        print("TOTAL NUMBER OF ROWS", self.num_rows)
        print("NUMBER OF VISIBLE ROWS", self.num_visible_rows)
        print("BUTTON WIDTH", button_width)
        print("BUTTON HEIGHT", button_height)
        print("WINDOW HEIGHT:", self.getHeight())
        print("AVAILABLE HEIGHT", available_height)
        print("BUTTON HEIGHT WITH GAP", button_height_with_gap)

        for index, sport in enumerate(sports_data):
            button_label = sport['strSport']
            button_image = sport['strSportThumb']
            self.sports_data = sports_data
            button_x = vert_gap_size + (index % self.num_columns) * (button_width + vert_gap_size)
            button_y = horiz_gap_size + (index // self.num_columns) * (button_height_with_gap + horiz_gap_size)

            # Check if the image is already cached
            cache_filename = self.getCacheFilename(button_image)
            if self.isCacheValid(button_image, cache_filename):
                # Use the cached image
                image = xbmcgui.ControlImage(button_x, button_y, button_width, button_height, filename=cache_filename)
                xbmc.log("USING CACHED IMAGE: " + cache_filename)  # Print the filename of the cached image
            else:
                # Download and cache the image
                image = self.downloadAndCacheImage(button_image, button_x, button_y, button_width, button_height)
                xbmc.log("USING NEW IMAGE: " + cache_filename)  # Print the filename of the new image

            self.addControl(image)
            self.controls.append(image)

            try:
                response = requests.get(button_image)
                if response.status_code == 200:
                    # Use the button image if it was retrieved successfully
                    unfocused_image = Image.open(BytesIO(response.content))
                else:
                    raise Exception("Failed to retrieve button image")
            except Exception as e:
                # Use the fallback image if there was an error retrieving the button image
                unfocused_image = Image.open(self.FALLBACK_IMAGE_PATH)

            focused_image_gray = ImageOps.grayscale(unfocused_image)
            focused_image_rgb = focused_image_gray.convert('RGB')
            border_color_rgb = (18, 101, 196)
            border_width = 10
            bordered_image = ImageOps.expand(focused_image_rgb, border=border_width, fill=border_color_rgb)

            focused_gray_path = os.path.join(self.tempPath(), f"focused_gray_{index}.png")
            focused_image_gray.save(focused_gray_path)

            focused_texture_path = os.path.join(self.tempPath(), f"focused_image_{index}.png")
            bordered_image.save(focused_texture_path)

            # Create the path to the unfocused texture image
            unfocused_texture_path = os.path.join(self.tempPath(), f"unfocused_image_{index}.png")
            unfocused_image.save(unfocused_texture_path)

            border_color_int = (0)
            border_width = 10
            bordered_image = ImageOps.expand(bordered_image, border=border_width, fill=border_color_int)

            label_image = Image.new("RGBA", (button_width, button_height), (0, 0, 0, 0))
            label_draw = ImageDraw.Draw(label_image)

            words = button_label.split()
            label_text = '\n'.join(words)
            lines = label_text.split('\n')
            text_width, text_height = label_draw.textsize(label_text, font=font)

            if len(lines) > 1:
                line_height = (button_height - text_height) // 2
            else:
                line_height = (button_height - text_height) // 2

            for line in lines:
                buttonx = (button_width - label_draw.textsize(line, font=font)[0]) // 2
                label_draw.text((buttonx, line_height), line, font=font, fill=(255, 255, 255, 255), anchor='mm')
                line_height += label_draw.textsize(line, font=font)[1] + self.line_spacing

            label_image_path = os.path.join(self.tempPath(), f"label_image_{index}.png")
            label_image.save(label_image_path)

            button = xbmcgui.ControlButton(
                button_x,
                button_y,
                button_width,
                button_height,
                label="",
                focusTexture=focused_texture_path,
                noFocusTexture=unfocused_texture_path  # Set the unfocused texture path
            )
            self.addControl(button)
            self.controls.append(button)

            sport['control_id'] = button.getId()

            label_image_control = xbmcgui.ControlImage(button_x, button_y, button_width, button_height, filename=label_image_path)
            self.addControl(label_image_control)
            self.controls.append(label_image_control)

            # Update the loading progress
            self.buttons_loaded += 1
            progress_percentage = (self.buttons_loaded / self.total_buttons) * 100
            self.loading_dialog.update(int(progress_percentage), "Loading", f"{int(progress_percentage)}%")

            if index == 0:
                self.setFocus(button)

        # Remove the loading dialog once all buttons are loaded
        self.loading_dialog.close()
        self.loading_dialog = None
    # endregion

    # downloadAndCacheImage
    # region
    def downloadAndCacheImage(self, image_url, x, y, width, height):
        try:
            cache_filename = self.getCacheFilename(image_url)
            if self.isCacheValid(image_url, cache_filename):
                return xbmcgui.ControlImage(x, y, width, height, filename=cache_filename)
            else:
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Use the button image if it was retrieved successfully
                    unfocused_image = Image.open(BytesIO(response.content))
                    etag = response.headers.get('ETag')
                    print("ETag for new image:", etag)  # Print the ETag value
                    unfocused_image.save(cache_filename)
                    # Save the ETag value in the cache
                    self.saveCacheETag(cache_filename, etag)
                    return xbmcgui.ControlImage(x, y, width, height, filename=cache_filename)
                else:
                    raise Exception("Failed to retrieve button image")
        except Exception as e:
            # Use the fallback image if there was an error retrieving the button image
            unfocused_image = Image.open(self.FALLBACK_IMAGE_PATH)
            return xbmcgui.ControlImage(x, y, width, height, filename=self.FALLBACK_IMAGE_PATH)
    # endregion

    # getCacheFilename
    # region
    def getCacheFilename(self, image_url):
        filename = image_url.rsplit('/', 1)[-1]
        return os.path.join(self.CACHE_DIR, filename)
    # endregion

    # saveCacheETag
    # region
    def saveCacheETag(self, cache_filename, etag):
        etag_file = cache_filename + ".etag"
        with open(etag_file, 'w') as f:
            f.write(etag)
    # endregion

    # isCacheValid
    # region
    def isCacheValid(self, image_url, cache_filename):
        if not os.path.exists(cache_filename):
            print("CACHE NOT FOUND: " + cache_filename)  # Print the cache filename
            return False

        # Check the file modification time
        cache_mtime = os.path.getmtime(cache_filename)
        current_time = time.time()
        if current_time - cache_mtime >= self.CACHE_EXPIRY:
            print("CACHE EXPIRED: " + cache_filename)  # Print the cache filename
            return False

        # Check the ETag header in the response
        try:
            response = requests.head(image_url)
            if 'ETag' in response.headers:
                etag = response.headers['ETag'].strip('"')  # Remove surrounding double quotes
                cache_etag = self.getCacheETag(cache_filename).strip('"')  # Remove surrounding double quotes from cache ETag
                if etag != cache_etag:
                    print("ETAG MISMATCH: " + cache_filename)  # Print the cache filename
                    print("EXPECTED ETAG: " + cache_etag)  # Print the expected ETag value
                    print("RECEIVED ETAG: " + etag)  # Print the received ETag value
                    return False
                else:
                    # ETag matches, cache is still valid
                    return True
            else:
                # ETag header not found, cache is invalid
                return False
        except:
            pass

        # ETag validation failed, cache is invalid
        return False
    # endregion

    # getCacheETag
    # region
    def getCacheETag(self, cache_filename):
        etag_file = cache_filename + ".etag"
        if os.path.exists(etag_file):
            with open(etag_file, 'r') as f:
                return f.read().strip()
        return ""
    # endregion

    # onAction
    # region
    def onAction(self, action):
        if action == xbmcgui.ACTION_MOVE_LEFT:
            self.moveFocus(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            self.moveFocus(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            self.moveFocus(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            self.moveFocus(0, 1)
        else:
            pass

        xbmcgui.WindowXML.onAction(self, action)
    # endregion

    # moveFocus
    # region
    def moveFocus(self, x, y):
        focused_control_id = self.getFocusId()
        focused_index = None

        for index, sport in enumerate(self.sports_data):
            if 'control_id' in sport and sport['control_id'] == focused_control_id:
                focused_index = index
                break

        if focused_index is None:
            return

        current_row = focused_index // self.num_columns
        current_col = focused_index % self.num_columns

        new_row = current_row + y
        new_col = current_col + x

        if new_row < 0 or new_row >= self.num_rows or new_col < 0 or new_col >= self.num_columns:
            return

        new_focused_button_index = new_row * self.num_columns + new_col

        if 0 <= new_focused_button_index < len(self.sports_data):
            new_control_id = self.sports_data[new_focused_button_index].get('control_id')

            if new_control_id is not None:
                self.setFocusId(new_control_id)

                # Calculate the row and column of the focused button
                focused_button_row = new_focused_button_index // self.num_columns
                focused_button_col = new_focused_button_index % self.num_columns

                # Calculate the row and column of the first visible button on the screen
                first_visible_button_row = self.first_visible_button_index // self.num_columns
                first_visible_button_col = self.first_visible_button_index % self.num_columns

                # Calculate the row and column of the last visible button on the screen
                last_visible_button_row = self.last_visible_button_index // self.num_columns
                last_visible_button_col = self.last_visible_button_index % self.num_columns

                print("FIRST VISIBLE BUTTON ON SCREEN", self.first_visible_button_index)
                print("LAST VISIBLE BUTTON ON SCREEN", self.last_visible_button_index)
                print("FOCUSED BUTTON ROW", focused_button_row)
                print("FOCUSED BUTTON COL", focused_button_col)
                print("FIRST VISIBLE ROW", first_visible_button_row)
                print("FIRST VISIBLE COL", first_visible_button_col)
                print("LAST VISIBLE ROW", last_visible_button_row)
                print("LAST VISIBLE COL", last_visible_button_col)

                # Check if the focused button is at the edge of the screen
                if y < 0 and focused_button_row < first_visible_button_row:
                    self.scrollUp()
                    self.setFocusId(new_control_id)  # Set the focus again after scrolling
                elif y > 0 and focused_button_row > last_visible_button_row:
                    self.scrollDown()
                    self.setFocusId(new_control_id)  # Set the focus again after scrolling

        super().onAction(xbmcgui.Action(self.getFocusId()))
    # endregion

    # scrollUp
    # region
    def scrollUp(self):
        scrollUp_amount = 28  # Increase the scroll amount by ## pixels
        self.first_visible_button_index -= self.num_columns
        self.last_visible_button_index -= self.num_columns

        # Update the positions of the controls
        for control in self.controls:
            control.setPosition(control.getX(), control.getY() + control.getHeight() + self.vert_gap_size + scrollUp_amount)
    # endregion

    # scrollDown
    # region
    def scrollDown(self):
        scrollDown_amount = 28  # Increase the scroll amount by ## pixels
        self.first_visible_button_index += self.num_columns
        self.last_visible_button_index += self.num_columns

        # Update the positions of the controls
        for control in self.controls:
            control.setPosition(control.getX(), control.getY() - control.getHeight() - self.vert_gap_size - scrollDown_amount)
    # endregion
