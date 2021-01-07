import tkinter
import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image
import PIL.ImageTk
import time
import codecs
from tkinter.filedialog import askopenfilename
import json
from functools import partial
from tkinter import messagebox
import sys
import subprocess
import math
import os
import os.path as path
import threading
from tkinter import *
from PIL import Image, ImageTk
import time
import copy
import Pmw
from collections import OrderedDict
from bs4 import BeautifulSoup
import argparse

row_id = 0

def ceildiv(a, b):
    return int(math.ceil(a / float(b)))

class App:
    def __init__(self, window, summary_dict, snippet_length, video_file_location, original_dict):
        self.window = window
        self.balloon = Pmw.Balloon(self.window)
        self.window.resizable(False, False)
        self.window_width = 1368
        self.window_height = 768
        self.window.geometry(str(self.window_width) +
                             "x" + str(self.window_height))
        self.window.title('Summary Viewer Tool')
        self.vis_snippets = []
        self.searchIndex = -1
        self.summary_dict = summary_dict

        self.flag_to_stop_video = False
        self.flag_to_pause_video = 0
        self.snippet_length = snippet_length

        self.current_snippet = 1
        self.sd = False

        self.container_video = tk.Frame(self.window)
        self.container_video.grid_columnconfigure(
            0, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(
            1, weight=1, uniform="group1")

        self.text_snippet_count = tk.StringVar()
        self.text_current_snippet = tk.StringVar()
        self.text_summary_snippets = tk.StringVar()
        self.text_video_file_location = tk.StringVar()
        self.text_vis_next = tk.StringVar()
        self.text_vis_prev = tk.StringVar()
        self.text_play_full = tk.StringVar()
        self.label_video = tk.Label(self.window)

        self.textbox_snippet_count = tk.Label(
            self.window, textvariable=self.text_snippet_count)
        self.textbox_file_location = tk.Label(
            self.window, textvariable=self.text_video_file_location)
        self.textbox_current_snippet = tk.Label(
            self.window, textvariable=self.text_current_snippet)
        self.textbox_summary_snippets = tk.Label(
            self.window, textvariable=self.text_summary_snippets)
        self.text_play_button = tk.StringVar()

        self.button_play = tk.Button(
            self.window, textvariable=self.text_play_button, state=DISABLED, command=self.play)
        self.text_play_button.set("PLAY")
        self.balloon.bind(self.button_play, "Play the summary")

        self.text_pause_button = tk.StringVar()
        self.text_pause_button.set("PAUSE")
        self.button_pause = tk.Button(
            self.window, textvariable=self.text_pause_button, state=DISABLED, command=self.pause)
        self.balloon.bind(self.button_pause, "Pause the current snippet/shot")

        self.label_video.grid(in_=self.container_video,
                              row=0, column=0, sticky="nsew")

        self.display_selected_keys = tk.StringVar()
        self.textbox_display = tk.Message(
            self.window, textvariable=self.display_selected_keys, anchor="c", font=("Times", 12, "bold"))
        self.textbox_display.grid(
            in_=self.container_video, row=0, column=1, sticky="nsew")

        self.textbox_snippet_count.grid(
            in_=self.container_video, row=1, column=0, sticky="nsew")
        self.textbox_current_snippet.grid(
            in_=self.container_video, row=2, column=0, sticky="nsew")
        self.textbox_summary_snippets.grid(
            in_=self.container_video, row=4, column=0, sticky="nsew")
        self.textbox_file_location.grid(
            in_=self.container_video, row=3, column=0, sticky="nsew")

        self.button_play.grid(in_=self.container_video,
                              row=5, column=0, sticky="nsew")
        self.button_pause.grid(in_=self.container_video,
                               row=6, column=0, sticky="nsew")
        
        self.button_vis_next = tk.Button(
            self.window, textvariable=self.text_vis_next, command=self.vis_next)
        self.text_vis_next.set("Next Summary Snippet")
        self.balloon.bind(self.button_vis_next, "Play next summary snippet")
        self.button_vis_next.grid(in_=self.container_video,
                                        row=7, column=0, sticky="nsew")

        
        self.button_vis_prev = tk.Button(
            self.window, textvariable=self.text_vis_prev, command=self.vis_prev)
        self.text_vis_prev.set("Previous Summary Snippet")
        self.balloon.bind(self.button_vis_prev, "Play previous summary snippet")
        self.button_vis_prev.grid(in_=self.container_video,
                                        row=8, column=0, sticky="nsew")

        self.button_play_full = tk.Button(
            self.window, textvariable=self.text_play_full, command=self.play_full)
        self.text_play_full.set("Play Continuous")
        self.balloon.bind(self.button_play_full, "Play full summary in one go")
        self.button_play_full.grid(in_=self.container_video,
                                        row=9, column=0, sticky="nsew")

        self.original_dict = original_dict

        self.container_video.grid(row=0, column=0, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=4, uniform="group1")
        #self.window.grid_columnconfigure(1, weight=3, uniform="group1")
        #self.window.grid_columnconfigure(2, weight=2, uniform="group1")
        self.window.grid_rowconfigure(0, weight=1)

        self.stop()
        self.cps = []
        self.text_snippet_count.set("")
        self.text_current_snippet.set("")
        self.text_summary_snippets.set("")

        self.text_video_file_location.set("")

        
        self.video_file_location = video_file_location
        self.video_file_extension = self.video_file_location.split('.')[-1]

        self.video_file_name_with_location = self.video_file_location.split('.')[0]

        """ # Parse the shots change points xml file
        if(os.path.exists(self.video_file_name_with_location + '.xml')):
            file = open(self.video_file_name_with_location + '.xml', 'r')
            result = BeautifulSoup(file, 'lxml')
            shots = result.findAll('shots')
            # print(shots)
            self.cps = []
            self.sd = True
            for i, s in enumerate(shots[0]):
                # print(i, s)
                self.cps.append(float(s['fduration']) +
                                float(s['fbegin']))
            # self.cps = [x.strip() for x in self.cps]
            self.cps = list(map(int, self.cps))
            cap = cv2.VideoCapture(self.video_file_location)
            fps = round(cap.get(cv2.CAP_PROP_FPS))
            print("FPS = ", fps)
            cap.release()
            if "birthday.json" in config_file_location or "wedding.json" in config_file_location:
                print("Domain is either birthday or wedding, doing post processing on cps")
                self.fixcps(fps, 4)
            print("Change Points: ", self.cps, len(self.cps))
        else:
            messagebox.showwarning(
                "Warning", "This video's xml file not found - are you sure this domain doesn't need it?")
            self.sd = False
            print("shot xml not found, assuming snippet mode") """

        self.cps = []
        if "birthday.json" in config_file_location or "wedding.json" in config_file_location or "friends.json" in config_file_location:
            self.sd = True
            index = 1
            while True:
                try:
                    temp = self.original_dict[str(index)].keys()
                except:
                    print("Snippet: ", index, " does not exist, we are done with cps")
                    break
                self.cps.append(self.original_dict[str(index)]["shot_start"] + self.original_dict[str(index)]["shot_length"])
                index += 1
            self.cps = list(map(int, self.cps))
            print("Change Points: ", self.cps, len(self.cps))
        else:
            self.sd = False
        

        self.current_snippet = 1
        self.text_play_button.set("PLAY")
        self.video_file_name = self.video_file_name_with_location.split(
            '/')[-1]
        self.window.title(self.video_file_name)
        self.get_snippet_count()
        self.text_snippet_count.set(
            "Total number of snippets/shots are " + str(self.snippet_count))
        self.text_video_file_location.set(self.video_file_location)
        self.text_current_snippet.set(
            "Selected snippet/shot number " + str(self.current_snippet))
        self.unblock_video_buttons()
        
        self.set_window_name()

        self.vis_snippets = []
        for i in range(1, self.snippet_count + 1):
            if str(i) in summary_dict:
                self.vis_snippets.append(i)
        # if(os.path.exists(self.video_file_name_with_location + '.xml')):
        #     self.sd = True
        # else:
        #     print("shot xml not found, assuming snippet mode")
        #     self.sd = False
        print(self.vis_snippets)
        self.text_summary_snippets.set(self.vis_snippets)
        if len(self.vis_snippets) == 0:
            messagebox.showwarning("Empty Summary", "Nothing to show") 
            return
        
        #goto the first matching snippet
        self.searchIndex = 0
        self.stop
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_current_snippet.set(
                "Current snippet/shot number " + str(self.current_snippet))
        self.text_play_button.set("PLAY")
        self.button_vis_prev.configure(state=DISABLED)
        if len(self.vis_snippets) == 1:
            self.button_vis_next.configure(state=DISABLED)
        else:
            self.button_vis_next.configure(state=NORMAL)

        self.display_message()

        self.stop()
        self.set_window_name()
        self.play()
        self.window.mainloop()
    
    def fixcps(self, fps=25, shot_thresh=4):
        print("cps before manipulation: ", self.cps)
        for cp in self.cps:
            if(self.cps.index(cp) == 0):
                continue
            ele_ind = self.cps.index(cp)
            diff = self.cps[ele_ind] - self.cps[ele_ind - 1]
            if(diff <= fps):
                print("Shot smaller than 1 sec: deleting shot at: ", ele_ind)
                self.cps.remove(cp)
                continue
            if(diff > shot_thresh * fps):
                print("Shot larger than 4 sec: splitting shot at: ", ele_ind)
                num_shots = int(diff / (shot_thresh * fps))
                sp1 = self.cps[:ele_ind]
                sp2 = self.cps[ele_ind:]
                for j in range(num_shots - 1):
                    sp1.append(sp1[-1] + (shot_thresh * fps))
                if((cp - sp1[-1]) > ((shot_thresh + 1) * fps)):
                    sp1.append(sp1[-1] + (shot_thresh * fps))
                self.cps = sp1 + sp2
        print("cps after manipulation: ", self.cps)
        return self.cps

    def display_message(self):
        message = ""
        if 'categories' in self.original_dict[str(self.current_snippet)]:
            for cat, listt in self.original_dict[str(self.current_snippet)]['categories'].items():
                message += cat.upper() + ': '
                for checked_keys in self.original_dict[str(self.current_snippet)]['categories'][cat]:
                    message += checked_keys.rstrip('\n') + ', '
                message += '\n'
        if 'mega_event' in self.original_dict[str(self.current_snippet)]:
            message += 'EVENT ID: ' + \
                str(self.original_dict[str(self.current_snippet)]
                    ['mega_event']['id']) + ', '
            message += '\n'
            message += 'EVENT NAME: ' + \
                str(self.original_dict[str(self.current_snippet)]
                    ['mega_event']['name']) + ', '
            message += '\n'
        if 'sceneId' in self.original_dict[str(self.current_snippet)]:
            message += 'SCENE ID: ' + str(self.original_dict[str(self.current_snippet)]['sceneId'])
        self.display_selected_keys.set(message)

    def vis_next(self):
        #go to next summary snippet
        self.stop()
        self.searchIndex += 1
        #print("SearchIndex: ", self.searchIndex)
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_play_button.set("PLAY")
        if self.searchIndex == len(self.vis_snippets)-1:
            self.button_vis_next.configure(state=DISABLED)

        self.text_current_snippet.set(
                "Current shot/snippet number " + str(self.current_snippet))
        self.button_vis_prev.configure(state=NORMAL)
        self.stop()
        self.display_message()
        self.play()
        self.set_window_name()

    def play_full(self):
        self.stop()
        self.searchIndex = 0
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.flag_to_stop_video = False
        self.block_video_buttons()
        self.button_pause.configure(state=NORMAL)
        self.text_play_button.set("REPLAY")
        self.thread = threading.Thread(target=self.play_snippet_full)
        self.thread.start()
        self.set_window_name()

    def play_snippet_full(self):
        self.snippet_location = self.video_file_location
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        stop = False
        fps = round(self.snippet_capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(self.snippet_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        time_length = int(frame_count / fps)
        for self.searchIndex in range(0, len(self.vis_snippets)):
            self.current_snippet = self.vis_snippets[self.searchIndex]
            self.display_message()
            self.text_current_snippet.set(
                "Current shot/snippet number " + str(self.current_snippet))
            #if(os.path.exists(self.video_file_name_with_location + '.xml')):
            if(self.sd == True):
                if(self.current_snippet == 1):
                    frame_start = 0
                    frames_to_read = self.cps[self.current_snippet - 1] - 1
                else:
                    frame_start = self.cps[self.current_snippet - 2]
                    frames_to_read = self.cps[self.current_snippet -
                                            1] - frame_start - 1
            else:   # If cps is not present
                frame_start = (self.current_snippet - 1) * \
                    (self.snippet_length * fps)
                frames_to_read = self.snippet_length * fps
            print("Snippet/shot number: ", self.current_snippet,
                  " starting from: ", frame_start, ", number of frames = ", frames_to_read)
            self.snippet_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_start)
            subshot_count = 0
            while(self.snippet_capture.isOpened()):
                if(subshot_count == frames_to_read):
                    self.flag_to_pause_video = False
                    break
                if(self.flag_to_pause_video):
                    continue
                ret, frame = self.snippet_capture.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    subshot_count += 1
                    height, width, layers = frame.shape
                    container_video_width = (1368 * 4) / 9

                    if(width > container_video_width):
                        new_width = int(container_video_width)
                        new_height = int((new_width * height) / width)
                        frame = cv2.resize(frame, (new_width, new_height))

                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(img)
                    self.label_video.config(image=imgtk)
                    self.label_video.img = imgtk
                    time.sleep(1 / (fps + 16))
                else:
                    self.unblock_video_buttons()
                    self.text_pause_button.set("PAUSE")
                    self.button_pause.configure(state=DISABLED)
                    self.flag_to_pause_video = False
                    stop = True
                    break
            if stop == True:
                self.snippet_capture.release()
                self.unblock_video_buttons()
                self.text_pause_button.set("PAUSE")
                self.button_pause.configure(state=DISABLED)
                self.flag_to_pause_video = False
                break
            else:
                continue
        self.unblock_video_buttons()
        self.text_pause_button.set("PAUSE")
        self.button_pause.configure(state=DISABLED)
        self.flag_to_pause_video = False
        

    def vis_prev(self):
        #go to previous summary snippet
        self.stop()
        self.searchIndex -= 1
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_play_button.set("PLAY")
        if self.searchIndex == 0:
            self.button_vis_prev.configure(state=DISABLED)
        self.text_current_snippet.set(
                "Current shot/snippet number " + str(self.current_snippet))
        self.button_vis_next.configure(state=NORMAL)
        self.stop()
        self.display_message()
        self.play()
        self.set_window_name()

    def resize(image):
        im = image
        new_siz = siz
        im.thumbnail(new_siz, Image.ANTIALIAS)
        return im

    def pause(self):
        if(self.flag_to_pause_video):
            self.text_pause_button.set("PAUSE")
            self.flag_to_pause_video = False
        else:
            self.text_pause_button.set("RESUME")
            self.flag_to_pause_video = True
    
    def block_video_buttons(self):
        self.button_play.configure(state=DISABLED)
        self.button_vis_next.configure(state=DISABLED)
        self.button_vis_prev.configure(state=DISABLED)
        self.button_play_full.configure(state=DISABLED)

    def unblock_video_buttons(self):
        self.button_play.configure(state=NORMAL)
        #self.button_vis_next.configure(state=NORMAL)
        #self.button_vis_prev.configure(state=NORMAL)
        self.button_play_full.configure(state=NORMAL)
        if self.searchIndex > 0:
            self.button_vis_prev.configure(state=NORMAL)
        if self.searchIndex < len(self.vis_snippets) - 1:
            self.button_vis_next.configure(state=NORMAL)

    def play_snippet(self):
        self.snippet_location = self.video_file_location
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        fps = round(self.snippet_capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(self.snippet_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        time_length = int(frame_count / fps)
        #if(os.path.exists(self.video_file_name_with_location + '.xml')):
        if(self.sd == True):
            if(self.current_snippet == 1):
                frame_start = 0
                frames_to_read = self.cps[self.current_snippet - 1] - 1
            else:
                frame_start = self.cps[self.current_snippet - 2]
                frames_to_read = self.cps[self.current_snippet -
                                            1] - frame_start - 1
        else:   # If cps file is not present
            frame_start = (self.current_snippet - 1) * \
                (self.snippet_length * fps)
            frames_to_read = self.snippet_length * fps
        print("Snippet/shot number: ", self.current_snippet,
              " starting from: ", frame_start, ", number of frames = ", frames_to_read)
        self.snippet_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_start)
        subshot_count = 0
        while(self.snippet_capture.isOpened()):
            if(subshot_count == frames_to_read):
                self.unblock_video_buttons()
                self.text_pause_button.set("PAUSE")
                self.button_pause.configure(state=DISABLED)
                self.flag_to_pause_video = False
                break
            if(self.flag_to_pause_video):
                continue
            ret, frame = self.snippet_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                subshot_count += 1
                height, width, layers = frame.shape
                container_video_width = (1368 * 4) / 9

                if(width > container_video_width):
                    new_width = int(container_video_width)
                    new_height = int((new_width * height) / width)
                    frame = cv2.resize(frame, (new_width, new_height))

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)
                self.label_video.config(image=imgtk)
                self.label_video.img = imgtk
                time.sleep(1 / (fps + 16))
            else:
                self.unblock_video_buttons()
                self.text_pause_button.set("PAUSE")
                self.button_pause.configure(state=DISABLED)
                self.flag_to_pause_video = False
                break
        self.snippet_capture.release()
    
    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if(ret and not(self.flag_to_stop_video)):
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update)
    
    def get_snippet_count(self):
        self.video_length = subprocess.check_output(
            ("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", self.video_file_location)).strip()
        self.video_length = int(float(self.video_length))
        # print("Video length in seconds: "+ str(self.video_length))
        self.snippet_count = self.summary_dict['num_snippets']

    def stop(self):
        self.flag_to_stop_video = True
        time.sleep(1 / 20)

    def play(self):
        self.flag_to_stop_video = False
        self.text_current_snippet.set(
            "Playing shot/snippet number " + str(self.current_snippet))
        self.block_video_buttons()
        self.button_pause.configure(state=NORMAL)
        self.text_play_button.set("REPLAY")

        self.thread = threading.Thread(target=self.play_snippet)
        self.thread.start()

    def set_window_name(self):
        self.window.title(self.video_file_name + "." + self.video_file_extension)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to view generate video summary")
    parser.add_argument('--video', required=True, help='''Full path to the original video''')
    parser.add_argument('--summary', required=True, help='''Full path to the summary JSON file''')
    parser.add_argument('--annotation', required=True, help='''Full path to annotation file''')
    parser.add_argument('--configfile', required=True, help='''Full path to config file''')
    args = parser.parse_args()
    video = args.video
    summary = args.summary
    config_file_location = args.configfile
    annotation = args.annotation
    summary_dict = json.load(
        codecs.open(summary, 'r', 'utf-8-sig'), object_pairs_hook=OrderedDict)
    original_dict = json.load(
        codecs.open(annotation, 'r', 'utf-8-sig'), object_pairs_hook=OrderedDict)
    snippet_length = summary_dict["snippet_size"]

    # Create a window and pass it to the Application object
    w = App(tk.Tk(), summary_dict, snippet_length, video, original_dict)