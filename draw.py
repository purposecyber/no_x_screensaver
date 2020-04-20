#!/usr/bin/python3
import struct
from math import pow, sin
class FrameBufScreen:
    class Pixel:
        def __init__(self, xy=(0,0), bgr=(0,0,0)):
            self.x, self.y = xy
            self.b, self.g, self.r = bgr

        def as_bytes(self):
            # assumes TRUECOLOR -- there are other options here depending on your hardware.
            return struct.pack(b"BBBB", *self.bgr(),0)
        
        @staticmethod
        def bgr_from_bytes(byte_val):
            b, g, r, _ = struct.unpack(b"BBBB", byte_val)
            return b, g, r

        def bgr(self):
            return(self.b, self.g, self.r)
        
        def xy(self):
            return(self.x, self.y)

    def __init__(self, framebuf=0):
        assert(type(framebuf) is int)
        self.bufnum = framebuf
        self.stride = int(open("/sys/class/graphics/fb{}/stride".format(framebuf), "r").read().strip())
        
        xpixels, ypixels = [int(d) for d in open(
                    "/sys/class/graphics/fb{}/virtual_size".format(framebuf), "r")\
                    .read().strip().split(",")]
        
        self.bits_per_pixel = int(
                open("/sys/class/graphics/fb0/bits_per_pixel", "r")\
                    .read().strip())

        self.xpixels = range(xpixels+1)
        self.ypixels = range(ypixels+1)
        self.blank_screen()
        
    def blank_screen(self):
        self.blit = bytearray(self.stride * self.ypixels+1)

    def set_pixel(self, pixel):
        if pixel.x not in self.xpixels:
            raise ValueError("Invalid X coordinate, {}".format(pixel.x))
        if pixel.y not in self.ypixels:
            raise ValueError("Invalid Y coordinate, {}".format(pixel.y))
        y_start = self.stride * pixel.y
        x_start = y_start + (self.bits_per_pixel//8)*pixel.x
        x_end = x_start + (self.bits_per_pixel//8)
        self.blit[x_start:x_end] = pixel.as_bytes()

    def write(self):
        open("/dev/fb{}".format(self.bufnum), "wb+").write(self.blit)


    def read(self):
        self.blit = open("/dev/fb{}".format(self.bufnum), "rb").read()

    # really slow. could at least write entire circle width as a single write instead of each pixel.
    # might also try to optimize the math using bitwise functions
    def draw_circle(self, xy, bgr, r, ignore_oob=True):
        x_center, y_center = xy
        try:
            self.set_pixel(self.Pixel((x_center,y_center),bgr))
        except ValueError as e:
            if ignore_oob:
                pass
            else:
                raise e

        for x_offset in range(1,r+1):
            for y_offset in range(int(pow(pow(r,2) - pow(x_offset,2),.5)) + 1):
                for xy in ((x_center + x_offset,y_center + y_offset),
                            (x_center + x_offset, y_center - y_offset),
                            (x_center - x_offset, y_center + y_offset),
                            (x_center - x_offset, y_center - y_offset)):
                    try:
                        self.set_pixel(self.Pixel(xy, bgr))
                    except ValueError as e:
                        if ignore_oob:
                            pass
                        else:
                            raise e

    # also really slow. at least 25% speedup by only writing leading edge of circle
    def draw_line(self,x1y1,x2y2,bgr_line, thickness=1):
        x1, y1 = x1y1
        x2, y2 = x2y2
        steps = max(abs(x1-x2), abs(y1-y2), 1)
        y_step = (y2-y1)/steps
        x_step = (x2-x1)/steps
        for step in range(steps):
            y_center = int(y2 - (y_step*step))
            x_center = int(x2 - (x_step*step))
            self.draw_circle(xy=(x_center,y_center),bgr=bgr_line,r=thickness//2)

    # drawing boxes like this is criminal. needs a memset for the whole row.
    def draw_box(self,x1,x2,y1,y2,bgr_line, thickness=1, bgr_fill=None):
        if x1 > x2:
            raise ValueError("Invalid X Coords: x1 must be < x2")
        if x1 not in self.xpixels or x2 not in self.xpixels:
            raise ValueError("Invalid X Coords: ({}-{}). Out of bounds.".format(x1, x2))
        if y1 > y2:
            raise ValueError("Invalid Y Coords: y1 must be < y2")
        if y1 not in self.ypixels or y2 not in self.ypixels:
            raise ValueError("Invalid Y Coords: ({}-{}). Out of bounds.".format(y1, y2))

        for y in (y1, y2-thickness):
            for x in range(x1,x2):
                for t in range(thickness):
                    self.set_pixel(self.Pixel(xy=(x,y+t), bgr=bgr_line))

        for x in (x1, x2-thickness):
            for y in range(y1, y2):
                for t in range(thickness):
                    self.set_pixel(self.Pixel(xy=(x+t,y), bgr=bgr_line))
        
        if not bgr_fill: return

        for y in range(y1+thickness,y2-thickness):
            for x in range(x1+thickness,x2-thickness):
                self.set_pixel(self.Pixel(xy=(x,y),bgr=bgr_fill))
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
            
if __name__ == "__main__":
    main()
