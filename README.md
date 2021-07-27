# Level-Meter
Level Meter of liquid interfaces in a burette or test tube using tensorflow object detection and OpenCV

# Background
This project started as a way to automatically measure volumes of oil and water in a test tube or burette used as a two phase separator. When these measurements need to be done at specific intervals during a large period of time, it is desirable to automate the process, since it can allow us to run a test without human intervention or sometimes after-hours. The required sensibility in a 10ml tube was at least 0.01ml which is what a person with experience can usually estimate in a glass burette (1/10th of the smallest division). 

There are many methods to measure level in liquids, among those there are ultrasonic, capacitive and optical. 

* **Ultrasonic:** In our case the availability and price of ultrasonic devices for the required sensibility was beyond the budget of this project. 

* **Capacitive:** For the capacitive method, a metalic tube is used as two phase separator with a concentric and isolated rod  which forms a coaxial capacitor. Changing the amount of air, water and oil in the container (outer tube) changes the dielectric of the capacitor and hence the total measured capacity. Tests made showed that with a good LCR (impedance meter) the capacity value reading was not stable enough to make measurements in a long period of time. Parasite capacities could have a major factor in these tests and further investigation is needed to determine if the method is feasable to this project required sensibility and presition.

* **Optical:** Tests made in the past with a 1920 pixels resolution camera, proved to be suficient for the project requirements, but the detection of the meniscus (interface between two phases either air-liquid or water oil) was very difficult using computer vision tools at the time. The detection in that case was made using a colored liquid (usually blue) and doing a thresholding on the blue channel. But thresholding technique (even the adaptive thresolding) is not good enough as the interface (meniscus) is lost when illumination levels change in the room or when both phases are translucid.

Broad availability of new tools for computer vision as image classification and object detection, provided new possibilities for the optical method. 

# Object Detection
If it could be proved that an Object Detection model is capable of consistently detect a meniscus in a test tube or burette, then detecting the bottom level of the meniscus and calculating the volume of the liquid could be possible. 
Online research indicated Tensorflow Object Detection API as a good tool because it has proved to be accurate, it has a large user base and there are lots of resources online that can make troubleshooting easier.
Inital tests with Tensorflow Object Detection API with only 50 images, showed promising reasults with positive detections (understandably inconsistent). Further image training with a final number of around 750 images with varying intensity, position, tube type, etc. made the detection very consistenf and with high confidence.The proof of concept was successful. Illumination of the tubes was made with led strips from the back of a white translucid acrylic. 

![OD tests demo](demos/test_tube_reading_4.gif)

# GUI Application
Once the object detection part of the program was finished, I developed a GUI application with OpenCV routines that analyze the bounding box provided by Tensorflow to detect not the meniscus, but the lower edge of it, calculate  the volume with max and min references given by the user, and a cropping function so the OD API receives only the tube image.



![GUI interface demo](demos/test_tube_reading_3.gif)

# Usage
You need first Tkinter, OpenCV and Tensorflow packages installed to be able to run the program.
first you need to clone the repository and then run "Level_Meter_GUI.py".
Once the image is cropped so only the white background and the tube are in the frame, click on the image to mark the minimum mark of the tube and then the maximum mark. Then specify the volume that correcsponds to this marks in the Tube Volumes section fields.

# Changing Config File
If the configuration file does not exist, the app will create one with default parameters. You can edit the "Level_Meter.cfg" file with a text editor and change the default values. See below a reference to the available parameters and the meaning of each one.

* Camera=0                (USB Camera number that openCV uses to open the stream)

* Resolution=1920x1080    (Resolution, use the best resolution supported by the camera separated by an "x")

* Distance_to_object=200  (Distance from the tube to the lens of the camera in millimeters, it is used for parallax correction)

* Tube_diameter=6         (Tube inner diameter in millimeters, aslo used in parallax correction)

* Line_Width=1            (width of the lines to be displayed overlayed in the image, usually there is no need to change the default value)

* Font_Size=1             (size of the font to be displayed overlayed in the image, must be integer or the program will fail)

* Canvas_Width=400        (Canvas Size can be changed to match the resolution of the monitor or available screen space)

* Canvas_Height=670

