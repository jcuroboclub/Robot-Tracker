__author__ = 'JCU Robo Club (IEEE Student Branch)'

import numpy as np
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk  # sudo pip3 install pillow


class App:
    def __init__(self, tkroot):
        # cam
        self.root = tkroot
        self.cam = cv.VideoCapture(0)
        ret, self.frame = self.cam.read()
        self.orig_frame = self.frame

        # colour definitions
        self.left_def = np.zeros((1, 1, 3), np.uint8)
        self.right_def = np.zeros((1, 1, 3), np.uint8)
        self.front_def = np.zeros((1, 1, 3), np.uint8)

        # gui
        left_but = tk.Button(width=15, height=2, text='Set Left Colour')
        left_but.grid(row=0, column=0)
        left_but.bind("<Button-1>",
                      lambda event:
                      self.change_set_current(event, self.left_def))
        right_but = tk.Button(width=15, height=2, text='Set Right Colour')
        right_but.grid(row=0, column=1)
        right_but.bind("<Button-1>",
                       lambda event:
                       self.change_set_current(event, self.right_def))
        front_but = tk.Button(width=15, height=2, text='Set Front Colour')
        front_but.grid(row=0, column=2)
        front_but.bind("<Button-1>",
                       lambda event:
                       self.change_set_current(event, self.front_def))
        self.thresh_slide = tk.Scale(width=20, from_=0, to_=50,
                                orient=tk.HORIZONTAL)

        self.thresh_slide.grid(row=0, column=3)
        self.left_ind = tk.Label(text=str(self.left_def))
        self.left_ind.grid(row=1, column=0)
        self.right_ind = tk.Label(text=str(self.right_def))
        self.right_ind.grid(row=1, column=1)
        self.front_ind = tk.Label(text=str(self.front_def))
        self.front_ind.grid(row=1, column=2)
        self.img_lab = tk.Label(tkroot)
        self.img_lab.grid(row=2, column=0, columnspan=4)
        self.img_lab.bind("<Button-1>", self.onmouse)

        self.set_current = None

    def process(self):
        # capture
        ret, frame = self.cam.read()
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)
        frame = cv.flip(frame, 1)
        self.orig_frame = frame

        for col in [self.left_def, self.right_def, self.front_def]:
            if col[0, 0, 1] != 0:
                thresh = self.thresh_slide.get()
                hlower = (col[0, 0, 0] - thresh) % 180
                hupper = (col[0, 0, 0] + thresh) % 180
                invert = hlower > hupper
                if invert: # in case we have gone under 0 or over 180
                    hlower, hupper = hupper, hlower
                lower = np.uint8([[[hlower, 20, 20]]])
                upper = np.uint8([[[hupper, 255, 255]]])
                hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                mask = cv.inRange(hsv, lower, upper)
                if not invert:
                    mask = cv.bitwise_not(mask)
                frame = cv.bitwise_and(frame, frame, mask=mask)
        self.frame = frame

        self.root.after(50, self.process)

    def update(self):
        # indicators
        self.left_ind.configure(text=self.left_def)
        self.right_ind.configure(text=self.right_def)
        self.front_ind.configure(text=self.front_def)

        # image
        cv2image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.img_lab.imgtk = imgtk
        self.img_lab.configure(image=imgtk)
        self.root.after(50, self.update)

    def onmouse(self, event):
        x = int(event.x / self.img_lab.winfo_width() * np.size(self.frame, 1))
        y = int(event.y / self.img_lab.winfo_height() * np.size(self.frame, 0))
        print("Setting", str(self.set_current), x, y)
        if self.set_current is not None:
            colour = self.orig_frame[y:y+3, x:x+3]
            colour = cv.cvtColor(colour, cv.COLOR_BGR2HSV)
            print("HSV", colour)
            colour = np.mean(colour[0, 0])
            self.set_current[0, 0, 0] = colour
            self.set_current[0, 0, 1] = 128
            self.set_current[0, 0, 2] = 128

    def change_set_current(self, event, arg):
        print(arg)
        self.set_current = arg

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.process()
    app.update()
    root.mainloop()
