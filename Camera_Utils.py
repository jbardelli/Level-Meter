import cv2
import numpy as np


def set_cam_params(cap, x, y, brightness=None, focus=None, auto_focus=False):
    if cap.isOpened():                                  # Sets camera parameters as definition
        if x and y:                                     # brightness, focus and auto_focus
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
        if brightness is not None:
            cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        if auto_focus is True:
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        else:
            if focus is not None:
                cap.set(cv2.CAP_PROP_FOCUS, focus)
        w = str(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        h = str(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        b = str(int(cap.get(cv2.CAP_PROP_BRIGHTNESS)))
        f = str(int(cap.get(cv2.CAP_PROP_FOCUS)))
        af = str(int(cap.get(cv2.CAP_PROP_AUTOFOCUS)))
    else:
        w, h, b, f, af = None, None, None, None, None
    return w, h, b, f, af


def get_cam_hor_res(cap):                               # Returns camera horizontal resolution
    w = str(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
    return w


def get_cam_calibration(file, width, height):           # gets camera calibration parameters from file
    mtx = np.loadtxt(file, delimiter=',', max_rows=3)
    dist = np.loadtxt(file, delimiter=',', skiprows=3, max_rows=1)
    new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (width, height), 0, (width, height))
    return mtx, new_mtx, dist, roi


def print_img_resolution(img):                          # prints the resolution of an image
    width = img.shape[0]
    height = img.shape[1]
    print('Image resolution (w,h)= ', width, ', ', height)
    return


def set_cam_brightness(cap, brightness=None):           # Changes the brightness of a camera
    if cap.isOpened():
        if brightness is not None:
            cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness.get())
    return
