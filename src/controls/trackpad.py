import time

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

            fingertip_pos = self.finger_slider.getValue()
            if fingertip_pos is None or fingertip_pos == (None, None):
              #  print("Fingertip Pos not found")
                continue

            norm_x, norm_y = fingertip_pos

            print(f"Normalized Position: {norm_x}, {norm_y}")

            norm_x = max(0, min(norm_x, 1))
            norm_y = max(0, min(norm_y, 1))

            dx = (norm_x - 0.5) * 30
            dy = (norm_y - 0.5) * 30

            dx *= -1
            dy *= 1

            print(f"Pan values: dx={dx}, dy={dy}")

            self.slideshow.pan(dx, dy)

            time.sleep(0.01)



       # position = self.finger_slider.getValue()

        #if position is None or position == (None, None):
        #    return  

        #norm_x, norm_y = position

        #if self.last_position is not None:

        #    dx = norm_x - self.last_position[0]
        #    dy = norm_y - self.last_position[1]

        #    dx *= -1
        #    dy *= -1

        #    scaling_factor = 100

        #    self.slideshow.pan(dx * scaling_factor, dy * scaling_factor)

        #self.last_position = (norm_x, norm_y)
        #self.last_update_time = time.time()

    #def reset(self):
    #    self.last_position = None
