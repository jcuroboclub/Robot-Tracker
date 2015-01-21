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
        ret, self.first = self.cam.read()
        self.frame = self.first
        self.orig_frame = self.frame
        self.samplerad = 2

        # colour definitions
        self.undefined_col = np.zeros((1, 1, 3), np.uint8)
        self.left_def = self.undefined_col.copy()
        self.right_def = self.undefined_col.copy()
        self.front_def = self.undefined_col.copy()
        self.col_defs = [self.left_def, self.right_def, self.front_def]
        self.undefined_pos = np.zeros((1, 1, 2), np.uint8)
        self.left_pos = self.undefined_pos.copy()
        self.right_pos = self.undefined_pos.copy()
        self.front_pos = self.undefined_pos.copy()
        self.col_poss = [self.left_pos, self.right_pos, self.front_pos]

        # gui
        left_but = tk.Button(width=15, height=2, text='Set Left Colour')
        left_but.grid(row=0, column=0, columnspan=2)
        left_but.bind("<Button-1>",
                      lambda event:
                      self.change_set_current(event, (self.left_def,
                                                      self.left_pos,
                                                      self.left_disp)))
        right_but = tk.Button(width=15, height=2, text='Set Right Colour')
        right_but.grid(row=0, column=2, columnspan=2)
        right_but.bind("<Button-1>",
                       lambda event:
                       self.change_set_current(event, (self.right_def,
                                                       self.right_pos,
                                                       self.right_disp)))
        front_but = tk.Button(width=15, height=2, text='Set Front Colour')
        front_but.grid(row=0, column=4, columnspan=2)
        front_but.bind("<Button-1>",
                       lambda event:
                       self.change_set_current(event, (self.front_def,
                                                       self.front_pos,
                                                       self.front_disp)))
        self.thresh_slide = tk.Scale(width=20, from_=0, to_=50,
                                orient=tk.HORIZONTAL)
        self.thresh_slide.grid(row=0, column=6)

        # colour box display
        dispsize = 10
        self.left_disp = np.zeros((dispsize, dispsize, 3), np.uint8)
        self.left_disp_lab = tk.Label(tkroot)
        self.left_disp_lab.grid(row=1, column=1)
        self.right_disp = np.zeros((dispsize, dispsize, 3), np.uint8)
        self.right_disp_lab = tk.Label(tkroot)
        self.right_disp_lab.grid(row=1, column=3)
        self.front_disp = np.zeros((dispsize, dispsize, 3), np.uint8)
        self.front_disp_lab = tk.Label(tkroot)
        self.front_disp_lab.grid(row=1, column=5)
        self.col_disps = [self.left_disp, self.right_disp, self.front_disp]

        self.left_ind = tk.Label(text=str(self.left_def))
        self.left_ind.grid(row=1, column=0)
        self.right_ind = tk.Label(text=str(self.right_def))
        self.right_ind.grid(row=1, column=2)
        self.front_ind = tk.Label(text=str(self.front_def))
        self.front_ind.grid(row=1, column=4)
        self.img_lab = tk.Label(tkroot)
        self.img_lab.grid(row=2, column=0, columnspan=8)
        self.img_lab.bind("<Button-1>", self.onmouse)

        self.set_current_col = None
        self.set_current_pos = None
        self.set_current_disp = None

    def process(self):
        # capture
        ret, frame = self.cam.read()
        #frame = self.first
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)
        frame = cv.flip(frame, 1)
        self.orig_frame = frame

        for click in (c for c in list(zip(self.col_defs, self.col_poss,
                                          self.col_disps))
                    if (c[0] != self.undefined_col).all()
                        and (c[1] != self.undefined_pos).all()):
            col = click[0]
            pos = click[1]
            disp = click[2]
            thresh = self.thresh_slide.get()
            hlower = (col[0, 0, 0] - thresh) % 180
            hupper = (col[0, 0, 0] + thresh) % 180

            # in case we have gone under 0 or over 180
            invert = hlower > hupper
            if invert:
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
        bgr2tk = lambda img: ImageTk.PhotoImage(
            image=Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGBA)))
        hsv2tk = lambda img: ImageTk.PhotoImage(
            image=Image.fromarray(cv.cvtColor(
                cv.cvtColor(img, cv.COLOR_HSV2BGR), cv.COLOR_BGR2RGBA)))

        self.img_lab.imgtk = bgr2tk(self.frame)
        self.img_lab.configure(image=self.img_lab.imgtk)
        self.left_disp_lab.imgtk = hsv2tk(self.left_disp)
        self.left_disp_lab.configure(image=self.left_disp_lab.imgtk)
        self.right_disp_lab.imgtk = hsv2tk(self.left_disp)
        self.right_disp_lab.configure(image=self.right_disp_lab.imgtk)
        self.front_disp_lab.imgtk = hsv2tk(self.left_disp)
        self.front_disp_lab.configure(image=self.front_disp_lab.imgtk)
        self.root.after(50, self.update)

    def onmouse(self, event):
        x = int(event.x / self.img_lab.winfo_width() * np.size(self.frame, 1))
        y = int(event.y / self.img_lab.winfo_height() * np.size(self.frame, 0))
        print("Setting", str(self.set_current_col), x, y)
        if self.set_current_col is not None:
            self.set_current_pos[0, 0, 0] = x
            self.set_current_pos[0, 0, 1] = y
            colour = self.orig_frame[y-self.samplerad:y+self.samplerad,
                                     x-self.samplerad:x+self.samplerad]
            print(colour)
            colour = cv.cvtColor(colour, cv.COLOR_BGR2HSV)
            print("HSV", colour)
            h = np.mean(colour[:, :, 0])
            s = np.mean(colour[:, :, 1])
            v = np.mean(colour[:, :, 2])
            self.set_current_col[0, 0, :] = [h, s, v]
            self.set_current_disp[:] = [h, s, v]
            print(self.set_current_disp)

    def change_set_current(self, event, arg):
        print(arg)
        (self.set_current_col, self.set_current_pos, self.set_current_disp) \
            = arg

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.process()
    app.update()
    root.mainloop()