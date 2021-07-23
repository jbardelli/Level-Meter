# LEVEL METER GUI by Julian Bardelli
# GUI Application used to measure the volume of liquids in a graduated test tube or burette
# A USB camera feed is analyzed to detect meniscus using a tensorflow model trained with little more
# than 700 images.
# The user has to set the minimum and maximum capacity of the tube or burette doing a left mouse click
# over the mar in the image.
# Once the min and max marks are set, the program calculates the volume reading of one interface
# (oil or water to air) or two interfaces (oil to air and water to oil).
# The program then prints the calculated volumes on command line so these values can be picked up by
# another application (Labview in my case).

from tkinter import *
from PIL import Image, ImageTk
from Camera_Utils import *
from Meniscus_Utils import *
from GUI_Utils import *
from File_Utils import *
from Paths import *
import os
import socket
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.builders import model_builder
from object_detection.utils import config_util

# Default Parameters that will be used unless specified in CONFIG_FILE
CONFIG_FILE = "Level_Meter.cfg"
DEFAULT_CAM = 0
RESOLUTIONS = '1280x720'
DISTANCE = 200
TUBE_DIAM = 6
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 600
LINE_WIDTH = 1
FONT_SIZE = 1
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 64250  # The port used by the server

# Load category index
category_index = label_map_util.create_category_index_from_labelmap(files['LABELMAP'])
# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
detection_model = model_builder.build(model_config=configs['model'], is_training=False)
# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], 'ckpt-21')).expect_partial()


# @tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections_ = detection_model.postprocess(prediction_dict, shapes)
    return detections_


class App:
    def __init__(self, window, window_title, cfg_par: ConfigParams):
        # Class variables
        self.window = window
        self.window.title(window_title)
        self.cfg = cfg_par
        self.video_source = self.cfg.cam
        self.resolution = tk.StringVar()                                    # This var is declared here because the resolution
        self.resolution.set(cfg_par.resolution)                             # is needed by MyVideoCapture function
        self.vid = MyVideoCapture(video_source=self.video_source, res_list=self.res_to_list())
        self.x1, self.x2, self.y1, self.y2 = 0, int(self.vid.height), 0, int(self.vid.width)
        self.origin_x = 0
        self.origin_y = 0
        self.meniscus = Meniscus()
        self.static_mark = Mark([0, 0], self.cfg.obj_distance, self.cfg.tube_diam)

        # Tkinter window definitions
        # Image Canvas
        self.canvas = tk.Canvas(window, width=self.cfg.canvas_width, height=self.cfg.canvas_height)
        self.canvas.bind("<Button-1>", self.click_callback)
        self.canvas.grid(row=0, column=0, rowspan=4)

        # Camera Frame
        self.cam_frame = frame_create(window, text_="Camera", row_=0, col_=1, colspan_=2, rowspan_=1)
        label_create(self.cam_frame, width_=15, row_=0, col_=1, pad_x=1, pad_y=8, label="Resolution", var=self.resolution)
        self.brightness = tk.IntVar()
        self.brightness.set(50)
        self.brightness.trace("w", self.set_brightness)
        self.scaleb = tk.Scale(self.cam_frame, variable=self.brightness, orient=tk.HORIZONTAL, from_=10, to=150, resolution=10, label='Brightness', length=189)
        self.scaleb.grid(row=1, column=0, columnspan=2, padx=14, pady=0)
        self.focus = tk.IntVar()
        self.focus.set(50)
        self.focus.trace("w", self.set_focus)
        self.scale_f = tk.Scale(self.cam_frame, variable=self.focus, orient=tk.HORIZONTAL, from_=10, to=100, resolution=5, label='Focus', length=189)
        self.scale_f.grid(row=2, column=0, columnspan=2, padx=14, pady=0)

        # ROI Frame
        self.roi_frame = frame_create(window, text_="ROI Selection", row_=1, col_=1, colspan_=2, rowspan_=1)
        self.percent_x = tk.IntVar()
        self.percent_x.set(100)
        self.percent_x.trace("w", self.update_roi)
        self.scale_roi_x = tk.Scale(self.roi_frame, variable=self.percent_x, orient=tk.HORIZONTAL, from_=10, to=100, resolution=10, label='Percent X', length=189)
        self.scale_roi_x.grid(row=0, column=0, columnspan=2, padx=14, pady=0)
        self.percent_y = tk.IntVar()
        self.percent_y.set(100)
        self.percent_y.trace("w", self.update_roi)
        self.scale_roi_y = tk.Scale(self.roi_frame, variable=self.percent_y, orient=tk.HORIZONTAL, from_=10, to=100, resolution=10, label='Percent Y', length=189)
        self.scale_roi_y.grid(row=1, column=0, columnspan=2, padx=14, pady=0)

        # Volumes Frame
        self.vol_frame = frame_create(window, text_="Tube Volumes", row_=2, col_=1, colspan_=2, rowspan_=1)
        self.min_vol_var = tk.DoubleVar()
        self.min_vol_var.trace("w", self.change_vol_min)
        entry_create(self.vol_frame, width_=15, row_=0, col_=1, pad_x=5, pad_y=8, label="Min Mark (ml)", var=self.min_vol_var)
        self.min_pos_var = tk.IntVar()
        self.min_pos_var.trace("w", self.change_pos_min)
        spinbox_create(self.vol_frame, width_=13, row_=1, col_=1, pad_x=5, pad_y=8, label="Min Mark (px)", var=self.min_pos_var)
        self.max_vol_var = tk.DoubleVar()
        self.max_vol_var.trace("w", self.change_vol_max)
        entry_create(self.vol_frame, width_=15, row_=2, col_=1, pad_x=5, pad_y=8, label="Max Mark (ml)", var=self.max_vol_var)
        self.max_pos_var = tk.IntVar()
        self.max_pos_var.trace("w", self.change_pos_max)
        spinbox_create(self.vol_frame, width_=13, row_=3, col_=1, pad_x=5, pad_y=8, label="Max Mark (px)", var=self.max_pos_var)

        # Reading Frame
        self.reading_frame = frame_create(window, text_="Volume Reading", row_=3, col_=1, colspan_=2, rowspan_=1)
        self.intf1 = tk.StringVar()
        label_create(self.reading_frame, width_=15, row_=0, col_=1, pad_x=1, pad_y=8, label="Interface1 (ml)", var=self.intf1)
        self.intf2 = tk.StringVar()
        label_create(self.reading_frame, width_=15, row_=1, col_=1, pad_x=1, pad_y=8, label="Interface2 (ml)", var=self.intf2)

        self.delay = 100
        self.update()
        self.update_roi()
        self.window.mainloop()

    def update(self):                           # This Function executes every self.delay
        ret, frame = self.vid.get_frame()                           # Get the frame from the camera
        if ret:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)      # Rotate image
            image_np = np.array(frame)
            image_np = image_np[self.y1:self.y2, self.x1:self.x2]   # Crop Image according to ROI control values
            image_np_with_detections = image_np.copy()

            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0),
                                                dtype=tf.float32)   # Convert image to Tensor
            detections = detect_fn(input_tensor)
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
            detections['num_detections'] = num_detections
            # detection_classes should be ints.
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            # detect objects in image_np_with_detections, return a Meniscus class with the information
            image_np_with_detections, self.meniscus = meniscus_draw(image_np_with_detections,
                                                                    detections['detection_boxes'],
                                                                    detections['detection_scores'],
                                                                    self.static_mark,
                                                                    max_boxes=2,
                                                                    min_score_thresh=0.2)

            self.order_intf()                               # Order interfaces so the one on top goes first and not according confidence
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:            #Open socket and try to send to Labview
                s.connect((HOST, PORT))
                joined_readings = self.intf1.get() + ',' + self.intf2.get() + "\r\n"
                s.sendall(bytes(joined_readings, 'ascii'))
                s.close()

            print('Readings: ', self.meniscus.reading)      # Print on Command Line of another program (Labview) to capture it

            image_np_with_detections = cv2.resize(image_np_with_detections, self.fit_img_to_canvas())                       # Resize image to fit the height in the canvas
            draw_levels(image_np_with_detections, self.meniscus, self.cfg.canvas_height, self.vid.width, self.cfg.line_width, self.cfg.font_size)      # Draw line and text at the meniscus lower edge
            draw_marks(image_np_with_detections, self.static_mark, self.cfg.canvas_height, self.vid.width, self.cfg.line_width, self.cfg.font_size)    # Draw the marks that limit the volume calculation
            draw_center_lines(image_np_with_detections, self.cfg.line_width)                                                         # Draw centered reference lines

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(image_np_with_detections))  # Create photo from array
            self.canvas.create_image(self.origin_x, self.origin_y, image=self.photo, anchor=tk.NW)  # Set image to center of canvas
        self.window.after(self.delay, self.update)                      # Repeat after self.delay

    def set_brightness(self, *args):
        self.vid.vid.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness.get())  # Sets cam Brightness using the IntVar.get()

    def set_focus(self, *args):
        self.vid.vid.set(cv2.CAP_PROP_FOCUS, self.focus.get())  # Sets cam Focus using the IntVar.get()

    def res_to_list(self):                                              # Converts the stringVar from the Combo box in a
        res_list = str(self.resolution.get()).split('x')                # format like '1280x720' to an integer list like [1280, 720]
        res_list = list(map(int, res_list))                             # to be used by function that set the camera resolution
        return res_list                                                 # and need a list of integers

    def update_roi(self, *args):                                                    # When a ROI Scale widget changes its value, this function
        self.x1 = int((self.vid.height - (self.vid.height * self.percent_x.get() / 100)) / 2)  # updates the ROI so when the image is displayed inside
        self.x2 = int(self.x1 + (self.vid.height * self.percent_x.get() / 100))     # the canvas it is cropped to the size specified by
        self.y1 = int((self.vid.width - (self.vid.width * self.percent_y.get() / 100)) / 2)  # percentages in x and y of the camera resolution
        self.y2 = int(self.y1 + (self.vid.width * self.percent_y.get() / 100))      # x1 and x2 are the horizontal max and min pixels
        img_x, img_y = self.fit_img_to_canvas()                                     # y1 and y2 are the vertical max and min pixels
        self.origin_x = (self.cfg.canvas_width - img_x) / 2                                  # Origin values are calculated so the image can be
        self.origin_y = (self.cfg.canvas_height - img_y) / 2                                 # positioned in the center of the canvas

    def fit_img_to_canvas(self):                                                    # Returns pixels wide and high for the cv2.resize image function
        scale_x = int((self.x2 - self.x1) * (self.cfg.canvas_height / (self.y2 - self.y1)))  # Proportionally resize x and y of image
        scale_y = int(self.cfg.canvas_height)                                                # to fit the height of canvas
        return scale_x, scale_y

    def click_callback(self, event):                        # When mouse left-click on canvas, update marks to the
        y = int(event.y * (self.y2 - self.y1) / self.cfg.canvas_height)  # mouse click position
        if len(self.static_mark.yposition) < 2:             # If less than two marks in the array, append.
            self.static_mark.yposition.append(y)            # Append the mark position to the array
        else:                                               # If there are 2 mark in the array...
            self.static_mark.yposition = []                 # clean the array and start appending again
            self.static_mark.yposition.append(y)
        if len(self.static_mark.yposition) == 1:
            self.min_pos_var.set(self.static_mark.yposition[0])
        if len(self.static_mark.yposition) == 2:
            self.min_pos_var.set(self.static_mark.yposition[0])
            self.max_pos_var.set(self.static_mark.yposition[1])
        print('Marks: ', self.static_mark.yposition)

    def change_vol_min(self, *args):                        # Callback when the min_vol_var widget value changes
        self.static_mark.capacity[0] = self.min_vol_var.get()

    def change_vol_max(self, *args):                        # Callback when the max_vol_var widget value changes
        self.static_mark.capacity[1] = self.max_vol_var.get()

    def change_pos_min(self, *args):                        # Callback when the min_pos_var widget value changes
        if len(self.static_mark.yposition) > 0:
            self.static_mark.yposition[0] = self.min_pos_var.get()

    def change_pos_max(self, *args):                        # Callback when the max_pos_var widget value changes
        if len(self.static_mark.yposition) == 2:
            self.static_mark.yposition[1] = self.max_pos_var.get()

    def order_intf(self):
        # Readings are ordered in array by confidence, reorder so intf1 is the meniscus on top and intf2 is bottom
        if any(x is None for x in self.meniscus.reading):   # If any of the readings is None
            self.intf1.set(self.meniscus.reading[0])        # The first one can be the only one with value
            self.intf2.set(self.meniscus.reading[1])        # Second one is None for sure
        else:                                               # Image has its origin position (0, 0) on top left corner
            idx = self.meniscus.yposition.index(min(self.meniscus.yposition))  # Index of the reading that is on top
            self.intf1.set(self.meniscus.reading[idx])      # and update the intf1 indicator StringVar
            idx = self.meniscus.yposition.index(max(self.meniscus.yposition))  # Index of the reading that is at bottom
            self.intf2.set(self.meniscus.reading[idx])      # Update indicator StringVar

    # OLD Code section (used to allow user to change resolution, but that caused hardware problems with USB camera
    # Resolution cannot be changed on the fly, close app, change Level_Meter.cfg file and start app again.
    #
    # def set_resolution(self, *args):                                    # Sets camera Resolution using the resolution StringVar
    #     res_list = self.res_to_list()                                   # Change the resolution string to integer list
    #     old_res = int(self.vid.vid.get(cv2.CAP_PROP_FRAME_WIDTH))       # Resolution before the change
    #     w, h, _, _, _ = set_cam_params(self.vid.vid, res_list[0], res_list[1], 100, 50, False)
    #     self.vid.width, self.vid.height = int(w), int(h)                # Convert returned resolution values to integer
    #     self.update_roi()                                               # Update the roi to the new resolution values
    #     for idx, y in enumerate(self.static_mark.yposition):
    #         self.static_mark.yposition[idx] = int(y * int(w) / old_res)     # Rescale the mark positions to new resolution
    #     self.min_pos_var.set(self.static_mark.yposition[0])
    #     self.max_pos_var.set(self.static_mark.yposition[1])
    #     print('Resolution: ', self.vid.width, 'x', self.vid.height)     # Print returned resolution


class MyVideoCapture:
    def __init__(self, video_source=0, res_list=None):
        if res_list is None:                                # Assign default value to res_list
            res_list = [800, 600]                           # to avoid mutable default values
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)     # Open the video source
        if not self.vid.isOpened():                         # If not opened raise error
            raise ValueError("Unable to open video source", video_source)
        w, h, _, _, _ = set_cam_params(self.vid, res_list[0], res_list[1], 100, 50, False)  # Set camera parameters
        self.width, self.height = int(w), int(h)            # Camera resolution
        print('Resolution: ', self.width, 'x', self.height)     # Print Resolution

    def get_frame(self):
        if self.vid.isOpened():                             # If stream is open, read a frame
            ret, frame = self.vid.read()
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # If read succeeds, convert to RGB and return
            else:
                return ret, None                            # If read fails or stream is closed return False and None for the frame
        else:
            return False, None                              # If video feed is not open

    def __del__(self):                                      # If program closes, release the camera
        if self.vid.isOpened():
            print('Closing video feed...')
            self.vid.release()


if __name__ == "__main__":
    cfg_params = ConfigParams(DEFAULT_CAM, RESOLUTIONS, DISTANCE, TUBE_DIAM, CANVAS_WIDTH, CANVAS_HEIGHT, LINE_WIDTH, FONT_SIZE)
    cfg_params = get_config(CONFIG_FILE, cfg_params)


    App(tk.Tk(), "Level Meter", cfg_params)
