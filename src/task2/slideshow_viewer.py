import numpy as np
import cv2
from time import sleep
from image_analysis.video_source import VideoSource

from util.constants import SLIDESHOW_MARK_OPACITY, MARK_COLOR, MARK_RADIUS_TO_VIEWPORT, MARK_THICKNESS_TO_RADIUS, MAX_ZOOM_FACTOR, MIN_ZOOM_FACTOR, FULLSCREEN_WINDOW_HEIGHT, FULLSCREEN_WINDOW_WIDTH, SLIDESHOW_STARTING_ZOOM_FACTOR

WIN_MAIN = "mainview"

# displays a slideshow.
# supports zooming and moving the viewport.
# can also mark details in image by drawing a red circle to the center of the screen.
class SlideshowViewer(VideoSource):

    def __init__ (self, width, height, image_filepaths:list[str], starting_index=0, blocking_mode=False):
        super().__init__(width, height)
        self.imgs = []
        self.blocking_mode = blocking_mode
        self.index=starting_index
        # load all images from given filepaths
        for fpath in image_filepaths:
            self.imgs.append(cv2.imread(fpath))
        
        self.zoom_factor = SLIDESHOW_STARTING_ZOOM_FACTOR
        self._load_image()
    
    # calculates initial size and position of the viewport.
    def _load_image(self):
        
        self.viewport_x, self.viewport_y = 0, 0

        self.aspect_ratio_window = self.width / self.height

        self.img_width = self.imgs[self.index].shape[1]
        self.img_height = self.imgs[self.index].shape[0]
        aspect_ratio_image = self.img_width / self.img_height
        
        # calculate optimal viewport width and height when fully zoomed out.
        if self.aspect_ratio_window > aspect_ratio_image:
            self.original_viewport_width = int(self.img_width)
            self.original_viewport_height = int(self.img_height / self.aspect_ratio_window)
        else:
            self.original_viewport_height = int(self.img_height)
            self.original_viewport_width = int(self.img_height * self.aspect_ratio_window)
        
        # apply zoom factor to viewport
        self.viewport_height = (1/self.zoom_factor) *  self.original_viewport_height
        self.viewport_width = (1/self.zoom_factor) *  self.original_viewport_width

        
        # re-center viewport
        self.viewport_x = (self.original_viewport_width - self.viewport_width) / 2
        self.viewport_y = (self.original_viewport_width - self.viewport_height) / 2

        #if not self.blocking_mode:
        self.render()
        
    # moves the viewport by dx and dy pixels.
    def pan(self, dx, dy):
        self.viewport_x = max(0, min(self.img_width-self.viewport_width,  self.viewport_x+dx / (0.5 * self.zoom_factor)  ))
        self.viewport_y = max(0, min(self.img_height-self.viewport_height,  self.viewport_y+dy / (0.5 * self.zoom_factor) ))

    # changes zoom factor and recalculates viewport size
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

    # jump to the previous image.
    def previous_image(self):
        self.index = max(0, self.index-1)
        self._load_image()

    # jump to the next image
    def next_image(self):
        self.index = min(len(self.imgs)-1, self.index+1)
        self._load_image()
        
    # jump to the image specified by new_index
    def jump_to_image(self, new_index):
        if new_index is None:
            return
        if self.index != new_index:
            self.index = max(0, min(len(self.imgs)-1, new_index))
            self._load_image()

    # applies current viewport settings and outputs the resulting image.
    def render(self):
        # calculate boundaries of viewport
        leftbound = int(self.viewport_x)
        rightbound = int(self.viewport_x + self.viewport_width)

        topbound = int(self.viewport_y)
        botbound = int(self.viewport_y + self.viewport_height)

        # crop image to viewport
        image_cropped = self.imgs[self.index][topbound:botbound, leftbound:rightbound]
        image_cropped = cv2.resize(image_cropped,(self.width, self.height))
        self.frame = image_cropped
    
    # draws a red circle to the image.
    # the circle appears in the center of the current viewport 
    # and its radius and thickness are proportional to the size of the viewport.
    def mark(self):
        # calculate circle center
        center_x = int(self.viewport_x + self.viewport_width / 2)
        center_y = int(self.viewport_y + self.viewport_height / 2)

        # calculate radius and thickness in relation to viewport
        radius = int(min(self.viewport_height, self.viewport_width)/2 * MARK_RADIUS_TO_VIEWPORT)
        thickness = int(radius * MARK_THICKNESS_TO_RADIUS)

        # copy image
        overlay = self.imgs[self.index].copy()

        # draw circle
        cv2.circle(overlay, (center_x, center_y), radius, MARK_COLOR, thickness)

        # overlay image copy onto original image. 
        # crude but effective way to control circle opacity, after https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
        self.imgs[self.index] = cv2.addWeighted(overlay, SLIDESHOW_MARK_OPACITY, self.imgs[self.index], 1 - SLIDESHOW_MARK_OPACITY, 0)

        if not self.blocking_mode:
            self.render()

    # stop the slideshow            
    def stop(self):
        self.blocking_mode = False
        self.running = False
        

    # start the slideshow in blocking mode
    def start(self):
        self.blocking_mode = True
        self.running = True
        while self.running:
            self.render()
            sleep(0.1)

    # output current frame
    def get_last_frame(self):
        #print(self.frame.shape)
        return self.frame


        
