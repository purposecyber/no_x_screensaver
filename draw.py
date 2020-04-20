#!/usr/bin/python3
import struct
from math import  sin
from frame_buf_screen import FrameBufScreen
from capture_screen import capture_screen

import random
def main():
    # fb = FrameBufScreen((1375,768))
    fb = FrameBufScreen()

    print("Got Screen: {}x{}".format(fb.xpixels[-1], fb.ypixels[-1]))
    red = (0,0,255)
    green = (0,255,0)
    blue = (255,0,0)
    # red vertical line
    # fb.draw_line((fb.xpixels[len(fb.xpixels)//2],0), (fb.xpixels[len(fb.xpixels)//2],fb.ypixels[-1]),red,3)

    # blue horizontal line
    # fb.draw_line((0,fb.ypixels[len(fb.ypixels)//2]), (fb.xpixels[-1],fb.ypixels[len(fb.ypixels)//2]),blue,3)

    # graph

    #starting color
    color = [128,128,128]

    # draw squiggly lines forever
    serial = 0
    while(True):
        ysz = len(fb.ypixels)
        xsz = len(fb.xpixels)
        
        # starting y
        y_0 = random.choice(fb.ypixels)
        
        # random angle (rise/run) to onscreen ending y
        x_ = random.uniform(-y_0-ysz,ysz-y_0)/xsz
        
        # squiggle size (height)
        s_ = [random.randrange(-300,300) for _ in range(3)]
        
        # squiggle ferocity (speed) 
        f_ = [random.randrange(10,300) for _ in range(3)]
        
        # line thickness
        thickness = random.randrange(1,10)
        
        # squiggle equation
        eqn = lambda x: x_*x - s_[0]*sin(x/f_[0]) - s_[1]*sin(x/f_[1]) + s_[2]*sin(x/6)*sin(x/f_[2]) + y_0
        
        # segment begin
        oldxy = 0, y_0
        
        # max color change per pixel x
        colordelta = 5


        for x in fb.xpixels:
            newxy = x,int(eqn(x))
            
            # three chanel random color bump
            for i in range(3): 
                color[i] = max(min(255, color[i]+random.randrange(-colordelta,colordelta)),0)
            
            fb.draw_line(newxy, oldxy, bgr_line=color, thickness=thickness)
            oldxy = newxy
            fb.write()
            serial += 1
            
if __name__ == "__main__":
    main()
