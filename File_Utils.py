from os.path import isfile


class ConfigParams:                                         # Class that contains program config
    def __init__(self, cam, res, distance, diam, canvasw, canvash, lw, fs):
        self.cam = int(cam)
        self.resolution = res
        self.obj_distance = int(distance)
        self.tube_diam = int(diam)
        self.canvas_width = int(canvasw)
        self.canvas_height = int(canvash)
        self.line_width = int(lw)
        self.font_size = int(fs)


def get_config(file, cfg_par: ConfigParams):
    # Get config from file and store it on ConfigParams class variable. If file does not exist create one
    # with the default parameters so the user can then edit the configuration file with a text editor
    if isfile(file):
        with open(file, 'r') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line = line.strip('\n')
            command = line.split("=")
            if command[0] == "Camera":
                cfg_par.cam = int(command[1])
            if command[0] == "Resolution":
                cfg_par.resolution = command[1]
            if command[0] == "Distance_to_object":
                cfg_par.distance = int(command[1])
            if command[0] == "Tube_diameter":
                cfg_par.tube_diam = int(command[1])
            if command[0] == "Line_Width":
                cfg_par.line_width = int(command[1])
            if command[0] == "Font_Size":
                cfg_par.font_size = int(command[1])
            if command[0] == "Canvas_Width":
                cfg_par.canvas_width = int(command[1])
            if command[0] == "Canvas_Height":
                cfg_par.canvas_height = int(command[1])
            f.close()
    else:
        create_config(file, cfg_par)                        # File does not exist, create one with default values
    return cfg_par


def create_config(file, cfg_par: ConfigParams):
    with open(file, 'w') as f:
        line = "Camera=" + str(cfg_par.cam) + '\n'
        f.write(line)
        line = "Resolution=" + str(cfg_par.resolution) + '\n'
        f.write(line)
        line = "Distance_to_object=" + str(cfg_par.obj_distance) + '\n'
        f.write(line)
        line = "Tube_diameter=" + str(cfg_par.tube_diam) + '\n'
        f.write(line)
        line = "Line_Width=" + str(cfg_par.line_width) + '\n'
        f.write(line)
        line = "Font_Size=" + str(cfg_par.font_size) + '\n'
        f.write(line)
        line = "Canvas_Width=" + str(cfg_par.canvas_width) + '\n'
        f.write(line)
        line = "Canvas_Height=" + str(cfg_par.canvas_height) + '\n'
        f.write(line)
        f.close()
