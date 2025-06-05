import numpy as np
import cv2
from time import sleep
from image_analysis.video_source import VideoSource

from util.constants import SLIDESHOW_MARK_OPACITY, MARK_COLOR, MARK_RADIUS_TO_VIEWPORT, MARK_THICKNESS_TO_RADIUS, MAX_ZOOM_FACTOR, MIN_ZOOM_FACTOR, FULLSCREEN_WINDOW_HEIGHT, FULLSCREEN_WINDOW_WIDTH, SLIDESHOW_STARTING_ZOOM_FACTOR

WIN_MAIN = "mainview"


class SlideshowViewer(VideoSource):

    def __init__ (self, width, height, image_filepaths:list[str], starting_index=0, blocking_mode=False):
        super().__init__(width, height)
        self.imgs = []
        self.blocking_mode = blocking_mode
        self.index=starting_index
        for fpath in image_filepaths:
            self.imgs.append(cv2.imread(fpath))
        
        self.zoom_factor = SLIDESHOW_STARTING_ZOOM_FACTOR
        #cv2.namedWindow(WIN_MAIN, cv2.WINDOW_NORMAL)
        #sleep(0.5)
        #cv2.setWindowProperty(WIN_MAIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
       # 
       # _, _, self.win_width, self.win_height = cv2.getWindowImageRect(WIN_MAIN)
        #self.win_width, self.win_height = FULLSCREEN_WINDOW_WIDTH, FULLSCREEN_WINDOW_HEIGHT
        #sleep(0.5)
        #cv2.setWindowProperty(WIN_MAIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        #self.frame = np.array([[[]]])
        
        self._load_image()
    

    def _load_image(self):
        
        self.viewport_x, self.viewport_y = 0, 0

        self.aspect_ratio_window = self.width / self.height

        self.img_width = self.imgs[self.index].shape[1]
        self.img_height = self.imgs[self.index].shape[0]
        aspect_ratio_image = self.img_width / self.img_height
        
        if self.aspect_ratio_window > aspect_ratio_image:
            self.original_viewport_width = int(self.img_width)
            self.original_viewport_height = int(self.img_height / self.aspect_ratio_window)
        else:
            self.original_viewport_height = int(self.img_height)
            self.original_viewport_width = int(self.img_height * self.aspect_ratio_window)
        
        
        self.viewport_height = (1/self.zoom_factor) *  self.original_viewport_height
        self.viewport_width = (1/self.zoom_factor) *  self.original_viewport_width

        
        # re-center viewport
        self.viewport_x = (self.original_viewport_width - self.viewport_width) / 2
        self.viewport_y = (self.original_viewport_width - self.viewport_height) / 2

        #if not self.blocking_mode:
        self.render()
        
    def pan(self, dx, dy):
        self.viewport_x = max(0, min(self.img_width-self.viewport_width,  self.viewport_x+dx / (0.5 * self.zoom_factor)  ))
        self.viewport_y = max(0, min(self.img_height-self.viewport_height,  self.viewport_y+dy / (0.5 * self.zoom_factor) ))


    def zoom(self, dz):
        self.zoom_factor += dz
        self.zoom_factor = min(MAX_ZOOM_FACTOR, max(MIN_ZOOM_FACTOR,self.zoom_factor))
        
        center_x = self.viewport_x + self.viewport_width / 2
        center_y = self.viewport_y + self.viewport_height / 2
                

        self.viewport_height = (1/self.zoom_factor) * self.original_viewport_height
        self.viewport_width = (1/self.zoom_factor) * self.original_viewport_width

        # re-center viewport
        self.viewport_x = center_x - self.viewport_width / 2
        self.viewport_y = center_y - self.viewport_height / 2

        # if viewport overlaps with image boundaries, shift it back
        self.viewport_x = max(0, min(self.img_width-self.viewport_width,  self.viewport_x))
        self.viewport_y = max(0, min(self.img_height-self.viewport_height,  self.viewport_y))

    def previous_image(self):
        self.index = max(0, self.index-1)
        self._load_image()

    def next_image(self):
        self.index = min(len(self.imgs)-1, self.index+1)
        self._load_image()
        
    def jump_to_image(self, new_index):
        if new_index is None:
            return
        if self.index != new_index:
            self.index = max(0, min(len(self.imgs)-1, new_index))
            self._load_image()

    def render(self):
        leftbound = int(self.viewport_x)
        rightbound = int(self.viewport_x + self.viewport_width)

        topbound = int(self.viewport_y)
        botbound = int(self.viewport_y + self.viewport_height)
        image_cropped = self.imgs[self.index][topbound:botbound, leftbound:rightbound]
        image_cropped = cv2.resize(image_cropped,(self.width, self.height))
        self.frame = image_cropped
        
        #cv2.imshow(WIN_MAIN,image_cropped)
        #cv2.waitKey(1) 
        #cv2.setWindowProperty(WIN_MAIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def mark(self):
        print(self.index)
        center_x = int(self.viewport_x + self.viewport_width / 2)
        center_y = int(self.viewport_y + self.viewport_height / 2)

        radius = int(min(self.viewport_height, self.viewport_width)/2 * MARK_RADIUS_TO_VIEWPORT)
        thickness = int(radius * MARK_THICKNESS_TO_RADIUS)

        overlay = self.imgs[self.index].copy()

        cv2.circle(overlay, (center_x, center_y), radius, MARK_COLOR, thickness)

        # crude but effective way to control circle opacity, after https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
        self.imgs[self.index] = cv2.addWeighted(overlay, SLIDESHOW_MARK_OPACITY, self.imgs[self.index], 1 - SLIDESHOW_MARK_OPACITY, 0)

        if not self.blocking_mode:
            self.render()
            
    def stop(self):
        self.blocking_mode = False
        self.running = False
        #sleep(0.25)
        #cv2.destroyAllWindows()
        

    def start(self):
        self.blocking_mode = True
        self.running = True
        while self.running:
            self.render()
            sleep(0.1)

    def get_last_frame(self):
        #print(self.frame.shape)
        return self.frame


        
