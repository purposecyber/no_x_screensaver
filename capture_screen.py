from frame_buf_screen import FrameBufScreen
from PIL import Image

def capture_screen(serial):
    fb = FrameBufScreen()
    fb.read()
    image = Image.frombytes('RGBA',(fb.stride//(fb.bits_per_pixel//8), fb.ypixels[-1]), fb.blit, "raw")
    image.save("contents{}.png".format(serial), format="PNG")

if __name__ == "__main__":
    capture_screen()
