import time

# reads value from a 2d finger slider and applies it to a slideshow in task 2.
# not sure why this is a separate class, but it works, so I'm not changing it.
class Trackpad:
    def __init__(self, finger_slider, slideshow):
        self.finger_slider = finger_slider  
        self.slideshow = slideshow       
        self.last_position = None         
        self.last_update_time = time.time()  

    def update(self, running, cap):
        time.sleep(2)  
        while running[0]:
            frame = cap.get_last_frame()
            if frame is None:
                print("Kamera-Frame konnte nicht gelesen werden.")
                time.sleep(0.01)  
                continue
            
            # get normalized position of finger
            fingertip_pos = self.finger_slider.getValue()
            if fingertip_pos is None or fingertip_pos == (None, None):
                continue

            norm_x, norm_y = fingertip_pos

            # clamp coordinates
            norm_x = max(0, min(norm_x, 1))
            norm_y = max(0, min(norm_y, 1))

            # calculate panning vector from coordinates
            dx = (norm_x - 0.5) * 30
            dy = (norm_y - 0.5) * 30

            dx *= -1
            dy *= 1

            # pan in the direction of the panning vector
            self.slideshow.pan(dx, dy)

            time.sleep(0.01)
