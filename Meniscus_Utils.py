import cv2
import numpy as np


class Mark(object):                                             # Marks are the top and bottom of the test tube or burette scale
    def __init__(self, capacity, dist, diam):
        self.yposition = []                                     # Array that holds the vertical position in pixels of the marks
        self.capacity = capacity                                # Capacity in milliliters of each mark
        self.distance = dist                                    # Distance from camera to object (tube)
        self.tube_diameter =diam                                # Tube inner diameter

    def mark_pos(self, event, x, y, flags, parameters):
        if event == cv2.EVENT_LBUTTONDOWN:                      # Act only on a mouse left button click on the image
            if len(self.yposition) < 2:                         # If less than two marks in the array, append.
                self.yposition.append(y)                        # Append the mark position to the array
            else:                                               # If there are 2 mark in the array...
                self.yposition = []                             # clean the array and start appending again
                self.yposition.append(y)
        return


class Meniscus(object):                                         # Class that holds the information of all
    def __init__(self):                                         # the meniscus detected by tensorflow API
        self.yposition = [0, 0]                                 # as vertical position (ypos), score (indicates
        self.score = [0, 0]                                     # the model confidence on the detection) and
        self.reading = [None, None]                             # reading in ml or cubic centimeters.


def meniscus_draw(image, boxes, scores, marks: Mark, max_boxes=20, min_score_thresh=.5):
    meniscus = Meniscus()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)              # Convert image to BW and apply adaptive threshold
    processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    processed_img = cv2.morphologyEx(processed_img, cv2.MORPH_OPEN, kernel, iterations=1)
    for i in range(boxes.shape[0]):                             # Loop through boxes (highest scores come first)
        if max_boxes == i:                                      # If found the maximum amount of boxes end loop
            break
        if scores[i] > min_score_thresh:                        # If score is more than the minimum threshold score
            ymin, xmin, ymax, xmax = tuple(boxes[i].tolist())   # Get the coordinates of the bounding box
            ymin = int(ymin * image.shape[0])
            ymax = int(ymax * image.shape[0])
            xmin = int(xmin * image.shape[1])
            xmax = int(xmax * image.shape[1])
            detail = processed_img[ymin:ymax, xmin:xmax]        # Crop the bounding box from binary img to analyze it
            kernel = np.ones((3, 3), np.uint8)
            detail = cv2.dilate(detail, kernel, iterations=1)
            meniscus.yposition[i] = detect_lower_edge(detail, ymin, i)      # Detect lower edge and reading
            meniscus.score[i] = scores[i]
    meniscus = calculate_volumes(meniscus, marks)               # Calculate volume and save in array
    return image, meniscus


def detect_lower_edge(img, y, index):
    # Evaluates pixels in a vertical line to detect the bottom of the meniscus,
    # gets the last value that is black/white in a threshold or edged image (cropped
    # with the bounding box. Evaluates multiple vertical lines in the center of the
    # meniscus to avoid intermittent movement of the detected bottom due to changes
    # in illumination.
    POINTS_TO_AVERAGE = 5
    center = int(img.shape[1]/2) - int(POINTS_TO_AVERAGE/2)
    delta = [0] * POINTS_TO_AVERAGE                             # array of zeroes with length of the points to avg
    for j in range(POINTS_TO_AVERAGE):
        center = center + j
        center_array = img[:, center:center + 1].flatten()
        for index, value in enumerate(center_array):
            if value == 255:
                delta[j] = index
    avg_delta = int(sum(delta)/POINTS_TO_AVERAGE)
    return y + avg_delta


def calculate_volumes(meniscus, marks: Mark):
    if len(marks.yposition) == 2:                                                   # Only if two marks are defined and y is in between them
        for index, y in enumerate(meniscus.yposition):
            if y != 0:
                y = position_correction(y, marks)
                total_volume_pix = abs(marks.yposition[1] - marks.yposition[0])     # Total usable pixel range
                if marks.yposition[0] > marks.yposition[1]:                         # Non Inverted scale subtract from top mark
                    volume = marks.capacity[1] - ((y - marks.yposition[1]) * (marks.capacity[1] - marks.capacity[0]) / total_volume_pix)
                else:                                                               # Inverted scale, add from top mark
                    volume = marks.capacity[0] + ((y - marks.yposition[0]) * (marks.capacity[1] - marks.capacity[0]) / total_volume_pix)
                meniscus.reading[index] = round(volume, 2)                          # Round volume to 2 decimals and store into class element
            else:
                meniscus.reading[index] = None
    else:
        meniscus.reading = [None, None]                                             # No marks defined, volume cannot be calculated
    return meniscus


def position_correction(y, marks: Mark):                                            # Correct the yposition on the image
    tube_diameter = marks.tube_diameter                                             # using the information of diameter of
    distance = marks.distance                                                       # the tube and the distance from the
    lens_correction = -2.6e-5 * y**2 + 5.12e-2 * y - 3.31                           # camera lens
    y_corr = y + lens_correction
    ypx = (marks.yposition[1] - marks.yposition[0])/2 - (y_corr - marks.yposition[0])
    parallax_corr = ((tube_diameter / 2) * ypx) / distance
    y_corr = int(y_corr - parallax_corr)
    # print('Position: ', y, ' / Lens: ', round(lens_correction, 2), ' / Parallax: ', round(parallax_corr, 2), ' / Corrected: ', y_corr)
    return y_corr


def draw_levels(img, meniscus, canvas_height, cam_height, line_width=1, font_size=1):   # Draws a horizontal line at the bottom of the meniscus
    for index, y in enumerate(meniscus.yposition):                                      # and the parameters (position, confidence and reading)
        if y != 0:
            line = int(y * canvas_height / cam_height)                                  # Resize position from cam_height to canvas size
            start = (0, line)                                                           # Start of horizontal line
            end = (img.shape[1], line)                                                  # End of horizontal line (img.shape[1] is the width of img)
            cv2.line(img, start, end, (255, 0, 0), line_width)
            confidence = 'C= ' + str(round(meniscus.score[index] * 100, 0)) + '%'       # Prints confidence value from the Tensorflow Object Detection API
            position = 'Y= ' + str(y) + 'px'                                            # Prints position on the image in pixels
            cv2.putText(img, confidence, (img.shape[1]-90*font_size, line - 3*font_size), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), line_width, cv2.LINE_AA)
            cv2.putText(img, position, (10, line + 14*font_size), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), line_width, cv2.LINE_AA)
            if meniscus.reading[index] is not None:                                     # Put volume only if there is a value
                volume = 'V= ' + str(meniscus.reading[index]) + 'ml'                    # Prints volume in cubic milliliters
                cv2.putText(img, volume, (10, line - 3*font_size), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), line_width, cv2.LINE_AA)


def draw_center_lines(img, line_width=1):
    # Draw a center line just for reference, detection does not depend on the position of the test tube/burette
    hor_center = int(img.shape[1]/2)
    img_width = int(img.shape[1])
    ver_center = int(img.shape[0]/2)
    img_height = int(img.shape[0])
    cv2.line(img, (hor_center, 0), (hor_center, img_height), (0, 0, 0), line_width)     # Vertical line
    cv2.line(img, (0, ver_center), (img_width, ver_center), (0, 0, 0), line_width)      # Horizontal line


def draw_marks(img, marks: Mark, canvas_height, cam_height, line_width=1, font_size=1):
    for index, y in enumerate(marks.yposition):
        line = int(y * canvas_height / cam_height)                                      # Resize position from cam_height to canvas size
        cv2.line(img, (0, line), (img.shape[1], line), (0, 255, 0), line_width)         # Draw all defined marks in green
        position = 'Y= ' + str(y) + 'px'                                                # Prints position on the original image size in pixels
        cv2.putText(img, position, (10, line + 14*font_size), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), line_width, cv2.LINE_AA)
        capacity = 'V= ' + str(marks.capacity[index]) + 'ml'                            # Prints the mark in volume scale in cubic centimeters
        cv2.putText(img, capacity, (10, line - 3*font_size), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), line_width, cv2.LINE_AA)
