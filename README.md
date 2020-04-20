# no_x_screensaver
Run a screensaver on any linux device by writing directly to the framebuffer, no X server required. No graphical package dependencies.

## NO X SERVER MAY BE RUNNING
Having a running X environment will be hammering the framebuffer. You can run this program, but you won't see any output!
Easiest way to do this is either on a server install (no x environment) or by restarting in single-user mode by running 
`init 1`.

## Must have proper permissions to write to /dev/fb0
Don't want to run as root? Just add group `video` to your user to write to the buffer, log out and log back in.

## Run it!
`python3 draw.py`
