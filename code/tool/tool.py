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

row_id = 0


def ceildiv(a, b):
    return int(math.ceil(a / float(b)))


class App:
    def __init__(self, window, snippet_length, category_keyword_dict, mega_events, fullScreen, visualize):
        self.window = window
        self.balloon = Pmw.Balloon(self.window)
        self.window.resizable(False, False)
        # self.window_width = self.window.winfo_screenwidth()
        # self.window_height = self.window.winfo_screenheight()
        self.window_width = 1368
        self.window_height = 768
        self.window.geometry(str(self.window_width) +
                             "x" + str(self.window_height))
        self.window.title('Video Annotation Tool')
        self.category_keyword_dictionary = category_keyword_dictionary
        self.mega_events = mega_events
        self.vis_snippets = []

        self.searchIndex = 0

        self.flag_to_stop_video = False
        self.flag_to_pause_video = 0
        self.snippet_length = snippet_length

        self.keyword_state_dict = {}

        self.current_event_id = 0
        self.current_event_name = "_"
        self.current_snippet = 1
        self.output_dict = {}
        self.visualize = visualize
        self.sd = False
        ##################################################################
        # GUI design
        # self.style = ttk.Style()
        # print(self.style.theme_names())
        # self.style.theme_use('classic')

        self.container_video = tk.Frame(self.window)
        self.container_video.grid_columnconfigure(
            0, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(
            1, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(
            2, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(
            3, weight=1, uniform="group1")

        self.text_snippet_count = tk.StringVar()
        self.text_num_results = tk.StringVar()
        self.text_current_snippet = tk.StringVar()
        self.text_video_file_location = tk.StringVar()
        self.text_drive_sync_status = tk.StringVar()
        self.text_vis_keyword = tk.StringVar()
        self.text_vis_next = tk.StringVar()
        self.text_vis_prev = tk.StringVar()
        self.text_vis_mega = tk.StringVar()
        self.label_video = tk.Label(self.window)

        self.textbox_snippet_count = tk.Label(
            self.window, textvariable=self.text_snippet_count)
        self.textbox_num_results = tk.Label(
            self.window, textvariable=self.text_num_results)
        self.textbox_file_location = tk.Label(
            self.window, textvariable=self.text_video_file_location)
        self.textbox_current_snippet = tk.Label(
            self.window, textvariable=self.text_current_snippet)
        self.textbox_goto = tk.Text(self.window, height=2)
        self.balloon.bind(self.textbox_goto, "Snippet/Shot number to jump to")
        self.text_play_button = tk.StringVar()

        self.button_browse = tk.Button(
            self.window, text='LOAD VIDEO', command=self.browse)
        self.balloon.bind(self.button_browse,
                          "Load video from computer into the tool")

        self.button_play = tk.Button(
            self.window, textvariable=self.text_play_button, state=DISABLED, command=self.play)
        self.text_play_button.set("PLAY")
        self.balloon.bind(self.button_play, "Play the loaded video")

        self.button_previous = tk.Button(
            self.window, text='PREVIOUS', state=DISABLED, command=self.previous)
        self.balloon.bind(self.button_previous,
                          "Go to the previous snippet/shot")

        self.button_next = tk.Button(
            self.window, text='NEXT', state=DISABLED, command=self.next)
        self.balloon.bind(self.button_next, "Go to the next snippet/shot")

        self.text_pause_button = tk.StringVar()
        self.text_pause_button.set("PAUSE")
        self.button_pause = tk.Button(
            self.window, textvariable=self.text_pause_button, state=DISABLED, command=self.pause)
        self.balloon.bind(self.button_pause, "Pause the current snippet/shot")

        self.button_play_prev = tk.Button(
            self.window, text='PLAY PREVIOUS', state=DISABLED, command=self.play_prev)
        self.balloon.bind(self.button_play_prev, "Play the next snippet/shot")

        self.button_play_next = tk.Button(
            self.window, text='PLAY NEXT', state=DISABLED, command=self.play_next)
        self.balloon.bind(self.button_play_next, "Play the next snippet/shot")

        self.button_goto = tk.Button(
            self.window, text='GOTO N', state=DISABLED, command=self.goto)
        self.balloon.bind(self.button_goto,
                          "Go to this snippet/shot and play it")

        self.label_video.grid(in_=self.container_video,
                              row=0, column=0, columnspan=4, sticky="nsew")

        self.textbox_snippet_count.grid(
            in_=self.container_video, row=1, column=0, columnspan=4, sticky="nsew")
        self.textbox_num_results.grid(
            in_=self.container_video, row=10, column=2, columnspan=2, sticky="nsew")
        self.textbox_current_snippet.grid(
            in_=self.container_video, row=2, column=0, columnspan=4, sticky="nsew")
        self.textbox_file_location.grid(
            in_=self.container_video, row=3, column=0, columnspan=4, sticky="nsew")

        self.button_browse.grid(in_=self.container_video,
                                row=4, column=0, columnspan=4, sticky="nsew")
        self.button_play.grid(in_=self.container_video,
                              row=5, column=0, columnspan=2, sticky="nsew")
        self.button_pause.grid(in_=self.container_video,
                               row=5, column=2, columnspan=2, sticky="nsew")

        self.button_previous.grid(
            in_=self.container_video, row=6, column=0, columnspan=2, sticky="nsew")
        self.button_next.grid(in_=self.container_video,
                              row=6, column=2, columnspan=2, sticky="nsew")

        self.button_play_prev.grid(
            in_=self.container_video, row=7, column=0, columnspan=2, sticky="nsew")
        self.button_play_next.grid(in_=self.container_video,
                                   row=7, column=2, columnspan=2, sticky="nsew")

        self.textbox_goto.grid(in_=self.container_video,
                               row=8, column=0, sticky="nsew")
        self.textbox_goto.configure(state="disabled")
        self.button_goto.grid(in_=self.container_video,
                              row=8, column=1, columnspan=3, sticky="nsew")

        # Add vis items
        if(self.visualize):
            self.button_vis_keyword = tk.Button(
                self.window, textvariable=self.text_vis_keyword, command=self.vis_keyword)
            self.text_vis_keyword.set("Visualize Keywords")
            self.balloon.bind(self.button_vis_keyword, "visualize keywords")
            self.button_vis_keyword.grid(in_=self.container_video,
                                         row=9, column=1, sticky="nsew")

            self.button_vis_mega = tk.Button(
                self.window, textvariable=self.text_vis_mega, command=self.vis_mega)
            self.text_vis_mega.set("Visualize Mega Events")
            self.balloon.bind(self.button_vis_mega, "visualize mega events")
            self.button_vis_mega.grid(in_=self.container_video,
                                      row=10, column=1, sticky="nsew")

            self.textbox_vis_keyword = tk.Text(self.window, height=2)
            self.textbox_vis_keyword.grid(in_=self.container_video,
                                          row=9, column=0, sticky="nsew")

            self.textbox_vis_mega = tk.Text(self.window, height=2)
            self.textbox_vis_mega.grid(in_=self.container_video,
                                       row=10, column=0, sticky="nsew")

            self.button_vis_next = tk.Button(
                self.window, textvariable=self.text_vis_next, command=self.vis_next)
            self.text_vis_next.set("Next Result")
            self.balloon.bind(self.button_vis_next, "Goto next result")
            self.button_vis_next.grid(in_=self.container_video,
                                      row=9, column=3, sticky="nsew")

            self.button_vis_prev = tk.Button(
                self.window, textvariable=self.text_vis_prev, command=self.vis_prev)
            self.text_vis_prev.set("Previous Result")
            self.balloon.bind(self.button_vis_prev, "Goto previous result")
            self.button_vis_prev.grid(in_=self.container_video,
                                      row=9, column=2, sticky="nsew")

        self.container_video.grid(row=0, column=0, sticky="nsew")

        ############################################

        self.container_middle = tk.Frame(self.window)
        self.container_middle.grid(row=0, column=1, sticky="nsew")
        self.container_middle.grid_columnconfigure(
            0, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(
            1, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(
            2, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(
            3, weight=1, uniform="group1")

        self.create_checklist()

        self.text_sentence_label = tk.StringVar()
        self.textbox_sentence_label = tk.Label(
            self.window, textvariable=self.text_sentence_label, font=("Times", 12, "bold"))
        self.textbox_sentence_label.grid(
            in_=self.container_middle, row=1, column=0, sticky="nsew")
        self.text_sentence_label.set(
            "Caption:")
        self.balloon.bind(self.textbox_sentence_label,
                          "Give a one sentence description of what is happening in this snippet")

        self.textbox_sentence = tk.Text(self.window, height=2)

        self.textbox_sentence.grid(
            in_=self.container_middle, row=2, column=1, columnspan=3, sticky="nsew")
        self.balloon.bind(self.textbox_sentence,
                          "Add only when it is not in the dropdown box above")
        
        if "techtalk.json" not in config_file_location:
            self.textbox_sentence.configure(state=DISABLED)

        self.var = StringVar(self.window)
        self.captions = ["Past captions"]
        # self.var.set("Prev Captions")  # default value
        self.var.set(self.captions[0])  # default value
        self.cap_menu = OptionMenu(
            self.window, self.var, *self.captions, command=self.returnSel)
        self.cap_menu.grid(in_=self.container_middle,
                           row=1, column=1, columnspan=3, sticky="nsew")
        if "techtalk.json" not in config_file_location:
            self.cap_menu.configure(state=DISABLED)

        self.button_same_as_previous = tk.Button(
            self.window, text='LOAD KEYWORDS FROM PREVIOUS SNIPPET', state=DISABLED, command=self.same_as_previous)
        self.balloon.bind(self.button_same_as_previous,
                          "Load keywords used in the previous snippet/shot")
        self.button_same_as_previous.grid(
            in_=self.container_middle, row=3, column=0, columnspan=4, sticky="nsew", pady=50)

        self.is_snippet_transition_var = tk.BooleanVar()
        self.is_snippet_transition = tk.Checkbutton(self.window, text="This snippet/shot is a transition snippet/shot",
                                                    variable=self.is_snippet_transition_var, anchor="w", onvalue=True, offvalue=False, command=self.transitionbutton_click, font=("Times", 12, "bold"))
        self.balloon.bind(self.is_snippet_transition,
                          "Select if this snippet/shot contains more than one scene type")
        self.is_snippet_transition.grid(
            in_=self.container_middle, row=4, column=0, columnspan=4, sticky="nsew")

        #if "techtalk.json" in config_file_location:
         #   self.is_snippet_transition.configure(state=DISABLED)

        self.is_event_checkbutton_var = tk.BooleanVar()
        self.is_event_checkbutton = tk.Checkbutton(self.window, text="This snippet/shot is a part of a mega event", onvalue=True, offvalue=False,
                                                   command=self.checked_checkbutton, anchor="w", variable=self.is_event_checkbutton_var, font=("Times", 12, "bold"))
        self.balloon.bind(self.is_event_checkbutton,
                          "Select if this snippet/shot is a part of a mega event")
        self.is_event_checkbutton.grid(
            in_=self.container_middle, row=5, column=0, columnspan=4, sticky="nsew")

        if "techtalk.json" in config_file_location:
            self.is_event_checkbutton.configure(state=DISABLED)

        self.radio_button_var = IntVar()
        self.button_generate_new_id = Radiobutton(self.window, text='GENERATE NEW EVENT ID', variable=self.radio_button_var, value=1,
                                                  anchor="w", state=DISABLED, command=self.radiobutton_click, font=("Times", 12, "bold"))
        self.balloon.bind(self.button_generate_new_id,
                          "Select if this snippet/shot is the first snippet/shot of a mega event")
        self.button_generate_new_id.grid(
            in_=self.container_middle, row=6, column=0, columnspan=4, sticky="nsew")

        self.button_previous_id_var = tk.StringVar()
        self.button_previous_id_var.set(
            "USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.button_previous_id = Radiobutton(self.window, textvariable=self.button_previous_id_var, variable=self.radio_button_var, value=2,
                                              anchor="w", state=DISABLED, command=self.radiobutton_click, font=("Times", 12, "bold"))
        self.balloon.bind(self.button_previous_id,
                          "Select if this snippet/shot is a continuation of a mega event in the previous snippet/shot")
        self.button_previous_id.grid(
            in_=self.container_middle, row=9, column=0, columnspan=4, sticky="nsew")

        self.event_var = StringVar(self.window)
        self.event_var.set("Mega Events List")  # default value
        # self.captions = self.mega_events
        self.event_menu = OptionMenu(
            self.window, self.event_var, *self.mega_events, command=self.returnEvent)
        self.event_menu.grid(in_=self.container_middle,
                             row=7, column=1, columnspan=3, sticky="nsew")
        self.event_menu.configure(state="disabled")

        self.caption_label = tk.Label(
            self.window, text="Mega Event:", font=("Times", 12, "bold"))
        self.caption_label.grid(in_=self.container_middle,
                                row=7, column=0, sticky="nsew")
        self.balloon.bind(
            self.caption_label, "Choose a mega event name if this snippet/shot begins a new mega event")

        self.textbox_new_id = tk.Text(self.window, height=2)
        self.textbox_new_id.grid(
            in_=self.container_middle, row=8, column=1, columnspan=3, sticky="nsew")
        self.textbox_new_id.configure(state="disabled")
        self.textbox_new_id.insert(tk.END, "default")
        self.balloon.bind(self.textbox_new_id,
                          "Mega event name")

        self.button_submit = tk.Button(
            self.window, text='SAVE TO JSON', command=self.submit, state=DISABLED)
        self.balloon.bind(self.button_submit, "Save above changes to file")
        self.button_submit.grid(
            in_=self.container_middle, row=10, column=0, columnspan=4, sticky="nsew", pady=20)
        # self.submitted = False

        self.button_sync = tk.Button(
            self.window, text='SYNC WITH CLOUD', command=self.drive_sync)
        self.balloon.bind(self.button_sync,
                          "Click this button if you have added a keyword or a co-annotator has added a keyword")
        self.button_sync.grid(
            in_=self.container_middle, row=11, column=0, columnspan=4, sticky="nsew", pady=20)
        self.button_sync.configure(state=DISABLED)

        self.drive_sync_status_label = tk.Label(
            self.window, textvariable=self.text_drive_sync_status, font=("Times", 12, "bold"))
        self.drive_sync_status_label.grid(
            in_=self.container_middle, row=12, column=0, columnspan=4, sticky="nsew", pady=20)
        ######################################################
        # self.display_selected_keys.set("")

        self.json_container = tk.Frame(self.window)
        self.textbox_json = tk.Text(self.window)
        self.json_container.grid(row=0, column=2, sticky="nsew")
        self.json_container.grid_rowconfigure(0, weight=1)
        self.json_container.grid_rowconfigure(1, weight=1)
        self.json_container.grid_columnconfigure(0, weight=1)
        self.display_selected_keys = tk.StringVar()
        self.textbox_display = tk.Message(
            self.window, textvariable=self.display_selected_keys, anchor="c", font=("Times", 12, "bold"))
        self.textbox_display.grid(
            in_=self.json_container, row=0, column=0, sticky="nsew")
        self.textbox_json.grid(in_=self.json_container,
                               row=1, column=0, sticky="nsew")
        self.scroll_bar = tk.Scrollbar(
            self.window, command=self.textbox_json.yview)
        self.scroll_bar.grid(in_=self.json_container,
                             row=1, column=1, sticky='nsew')
        self.textbox_json['yscrollcommand'] = self.scroll_bar.set

        self.window.grid_columnconfigure(0, weight=4, uniform="group1")
        self.window.grid_columnconfigure(1, weight=3, uniform="group1")
        self.window.grid_columnconfigure(2, weight=2, uniform="group1")
        self.window.grid_rowconfigure(0, weight=1)
        # GUI design
        ##################################################################
        if(fullScreen):
            self.window.attributes('-fullscreen', True)
        self.window.mainloop()

    def returnSel(self, value):
        self.textbox_sentence.delete("1.0", tk.END)
        self.textbox_sentence.insert(tk.END, self.var.get())

    def returnEvent(self, value):
        self.textbox_new_id.delete("1.0", tk.END)
        self.textbox_new_id.insert(tk.END, self.event_var.get())

    def vis_next(self):
        # go to next search result
        self.stop()
        self.create_checklist()
        self.searchIndex += 1
        self.text_num_results.set("Result snippets = " + str(len(self.vis_snippets)) + " Current index = " + str(self.searchIndex))
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_play_button.set("PLAY")
        if (self.current_snippet == self.snippet_count):
            self.button_next.configure(state=DISABLED)
        if str(self.current_snippet - 1) not in self.output_dict.keys():
            # This should never happen
            self.block_annotation_buttons()
        else:
            self.unblock_annotation_buttons()

        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")
        else:
            self.button_previous_id_var.set(
                "USE PREVIOUS ID: " + "_" + ": " + "_")
        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            # This should never happen
            self.display_selected_keys.set("")

        self.text_current_snippet.set(
            "Current shot/snippet number " + str(self.current_snippet))
        self.button_previous.configure(state=NORMAL)
        self.button_vis_prev.configure(state=NORMAL)
        self.stop()
        self.restore_checklist()
        self.play()
        if self.searchIndex == len(self.vis_snippets) - 1:
            self.button_vis_next.configure(state=DISABLED)
        self.set_window_name()

    def vis_prev(self):
        # go to previous search result
        self.stop()
        self.searchIndex -= 1
        self.text_num_results.set("Result snippets = " + str(len(self.vis_snippets)) + " Current index = " + str(self.searchIndex))
        print("Search index = ", self.searchIndex)
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_play_button.set("PLAY")
        if(self.current_snippet == 1):
            self.unblock_annotation_buttons()
            self.button_previous.configure(state=DISABLED)
        elif str(self.current_snippet - 1) not in self.output_dict.keys():
            # this should never happen
            self.block_annotation_buttons()
        else:
            self.unblock_annotation_buttons()

        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")
        else:
            self.button_previous_id_var.set(
                "USE PREVIOUS ID: " + "_" + ": " + "_")
        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            # This should never happen
            self.display_selected_keys.set("")

        self.text_current_snippet.set(
            "Current shot/snippet number " + str(self.current_snippet))
        self.button_next.configure(state=NORMAL)
        self.button_vis_next.configure(state=NORMAL)
        self.stop()
        self.restore_checklist()
        self.play()
        if self.searchIndex == 0:
            self.button_vis_prev.configure(state=DISABLED)
        self.set_window_name()

    def create_checklist(self):
        global row_id
        self.container_categories = tk.Frame(self.window)
        self.container_categories.grid(row=0, column=1, sticky="nsew")
        self.container_categories.grid_columnconfigure(
            0, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(
            1, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(
            2, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(
            3, weight=1, uniform="group1")

        self.new_keyword_dict = {}
        self.all_menu_buttons = []
        self.all_button_add_keyword = []
        self.all_textbox_new_keyword = []
        for self.category in self.category_keyword_dictionary:
            self.keyword_state_per_category = {}
            self.textbox_category_label = tk.Label(
                self.window, text=self.category, font=("Times", 12, "bold"))
            self.balloon.bind(self.textbox_category_label,
                              self.category_keyword_dictionary[self.category]["category_desc"])
            self.textbox_category_label.grid(
                in_=self.container_categories, row=row_id, column=0, sticky="nsew")
            menu = Menubutton(self.window, text='SELECT',
                              relief=RAISED)
            self.balloon.bind(
                menu, self.category_keyword_dictionary[self.category]["keywords_desc"])
            self.all_button_add_keyword.append(menu)

            menu.grid(in_=self.container_categories,
                      row=row_id, column=1, sticky="nsew")
            menu.menu = Menu(menu, tearoff=0)
            menu["menu"] = menu.menu

            for self.keyword in self.category_keyword_dictionary[self.category]["keywords"]:
                self.keyword_variable = tk.BooleanVar()
                checkbutton = menu.menu.add_checkbutton(
                    label=self.keyword, onvalue=True, offvalue=False, variable=self.keyword_variable, command=self.display_message_instant)
                # self.balloon.bind(checkbutton, "Demo balloon")
                self.keyword_state_per_category[self.keyword] = self.keyword_variable

            self.textbox_new_keyword = tk.Text(self.window, height=2)
            self.all_textbox_new_keyword.append(self.textbox_new_keyword)
            self.new_keyword_dict[self.category] = self.textbox_new_keyword
            self.textbox_new_keyword.grid(
                in_=self.container_categories, row=row_id, column=2, sticky="nsew")
            self.textbox_new_keyword.configure(state=DISABLED)
            self.button_add_keyword = tk.Button(
                self.window, text='ADD KEYWORD', command=partial(self.add_keyword, self.category))
            self.balloon.bind(
                self.button_add_keyword, "Check previous keywords in all categories before adding a new keyword")
            self.button_add_keyword.configure(state=DISABLED)
            self.all_button_add_keyword.append(self.button_add_keyword)

            self.button_add_keyword.grid(
                in_=self.container_categories, row=row_id, column=3, sticky="nsew")

            self.keyword_state_dict[self.category] = self.keyword_state_per_category
            row_id += 1

            self.container_categories.grid(
                in_=self.container_middle, row=0, column=0, columnspan=4, sticky="nsew")

    def add_keyword(self, category):
        global row_id
        new_keyword_help = self.new_keyword_dict[category].get("1.0", tk.END)
        new_keyword_help = new_keyword_help.strip()
        if("," in new_keyword_help):
            new_keyword, help = new_keyword_help.split(",")
            if(len(new_keyword) > 0):
                if(new_keyword not in self.category_keyword_dictionary[category]["keywords"]):
                    temp_caption = self.category_keyword_dictionary[category]["keywords_desc"] + \
                        "\n" + new_keyword + " (" + help + ")"
                    self.category_keyword_dictionary[category]["keywords"].append(
                        new_keyword)
                    self.category_keyword_dictionary[category]["keywords_desc"] = temp_caption
                    config_file_dictionary["categories"] = self.category_keyword_dictionary
                    with open(config_file_location, 'w') as fp:
                        json.dump(config_file_dictionary, fp)
                    self.container_categories.destroy()
                    row_id = 0
                    keyword_state_dict_copy = {}
                    for category in self.keyword_state_dict:
                        keyword_state_per_category_copy = {}
                        for keyword in self.keyword_state_dict[category]:
                            keyword_state_per_category_copy[keyword] = self.keyword_state_dict[category][keyword].get(
                            )
                        keyword_state_dict_copy[category] = keyword_state_per_category_copy
                    self.create_checklist()
                    for category in keyword_state_dict_copy:
                        for keyword in keyword_state_dict_copy[category]:
                            self.keyword_state_dict[category][keyword].set(
                                keyword_state_dict_copy[category][keyword])

                else:
                    messagebox.showwarning("Error", "Keyword already exists!")
            else:
                messagebox.showwarning("Error", "Enter a keyword first")
        else:
            messagebox.showwarning(
                "Error", "Enter a Keyword and Description/Justifcation Seperated by a comma ,")

    def radiobutton_click(self):
        if self.radio_button_var.get() == 1:
            self.textbox_new_id.configure(state="normal")
            self.event_menu.configure(state="normal")
        else:
            self.textbox_new_id.configure(state="disabled")
            self.event_menu.configure(state="disabled")

    def transitionbutton_click(self):
        if self.is_snippet_transition_var.get() == True:
            self.textbox_sentence.delete("1.0", tk.END)
            self.textbox_new_id.delete("1.0", tk.END)
            self.block_annotation_buttons()
            self.is_snippet_transition.configure(state=NORMAL)
            self.button_submit.configure(state=NORMAL)
        else:
            self.unblock_annotation_buttons()

    def checked_checkbutton(self):
        if(self.is_event_checkbutton_var.get()):
            self.button_generate_new_id.configure(state=NORMAL)
            if self.radio_button_var.get() == 1:
                self.textbox_new_id.configure(state="normal")
                self.event_menu.configure(state="normal")
            if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
                if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                    self.button_previous_id.configure(state=NORMAL)
        else:
            try:
                if('mega_event' in self.output_dict[str(self.current_snippet)]):
                    messagebox.showwarning(
                        "Updating Mega Event tag", "You are removing 'Mega Event' tag from this snippet/shot. Remember to click on 'Save to JSON' otherwise this change will be lost. Also, pls manually double check if previous or next snippets/shots belonging to this mega event also need to be changed and do the needful.")
                    del self.output_dict[str(
                        self.current_snippet)]['mega_event']
            except:
                pass

        # else:
        #     self.button_previous_id.configure(state=DISABLED)
        #     self.button_generate_new_id.configure(state=DISABLED)
        #     self.textbox_new_id.configure(state="disabled")
        #     self.event_menu.configure(state="disabled")

    def submit(self):
        category_caption_dict = {}
        # self.submitted = True
        if self.sd == True:
            if(self.current_snippet == 1):
                category_caption_dict['shot_start'] = 0
                category_caption_dict['shot_length'] = self.cps[self.current_snippet - 1]
            else:
                frame_start_save = self.cps[self.current_snippet - 2]
                category_caption_dict['shot_start'] = frame_start_save
                category_caption_dict['shot_length'] = self.cps[self.current_snippet -
                                                                    1] - frame_start_save

        if(self.is_snippet_transition_var.get()):
            self.textbox_json.delete("1.0", tk.END)
            category_caption_dict['transition'] = True
            category_caption_dict['caption'] = 'Transition'
        else:
            if(self.is_event_checkbutton_var.get()):

                if(self.radio_button_var.get() == 0 and str(self.current_snippet) not in self.output_dict):
                    messagebox.showwarning(
                        "Error", "Either generate new mega event id or select the previous mega event id!")
                    return
                elif(self.radio_button_var.get() == 1 and self.textbox_new_id.get("1.0", tk.END).strip() == ""):
                    messagebox.showwarning(
                        "Error", "Choose some mega event name!")
                    return
            category_dict = {}
            category_caption_dict['transition'] = False
            
            for category in self.keyword_state_dict:
                keyword_dict = []
                for keyword in self.keyword_state_dict[category]:
                    if self.keyword_state_dict[category][keyword].get():
                        keyword_dict.append(keyword)
                if len(keyword_dict) > 0:
                    category_dict[category] = keyword_dict
            category_caption_dict['categories'] = category_dict
            if(len(category_caption_dict['categories']) == 0):
                messagebox.showwarning(
                    "Error", "You must add some keywords to non-transition snippets/shots!")
                return
            self.textbox_json.delete("1.0", tk.END)
            if "techtalk.json" in config_file_location:
                if(self.textbox_sentence.get("1.0", tk.END).rstrip('\n') != ""):
                    caption = self.textbox_sentence.get(
                        "1.0", tk.END).rstrip('\n')
                    category_caption_dict['caption'] = caption
                    # Add caption to dropdown
                    self.keyword_variable = tk.BooleanVar()
                    # checkbutton = self.cap_menu.menu.add_checkbutton(
                    #     label=self.textbox_sentence.get(
                    #         "1.0", tk.END).rstrip('\n'), onvalue=True, offvalue=False, variable=self.keyword_variable)
                    if caption not in self.captions:
                        self.cap_menu['menu'].add_command(
                            label=caption, command=tk._setit(self.var, caption))
                        self.captions.append(caption)
                        self.cap_menu.destroy()
                        self.cap_menu = OptionMenu(
                            self.window, self.var, *self.captions, command=self.returnSel)
                        self.cap_menu.grid(in_=self.container_middle,
                                           row=1, column=1, columnspan=3, sticky="nsew")
                """ else:
                    messagebox.showwarning(
                        "Error", "Please enter caption before saving to json!")
                    return """
            if(self.is_event_checkbutton_var.get()):
                self.mega_event_dic = {}
                if(self.radio_button_var.get() == 1):
                    if str(self.current_snippet) in self.output_dict and 'mega_event' in self.output_dict[str(self.current_snippet)]:
                        temp_event_id = self.output_dict[str(
                            self.current_snippet)]['mega_event']['id']
                        temp_event_name = self.output_dict[str(
                            self.current_snippet)]['mega_event']['name']
                        prompt_message = "In current snippet/shot, event id is " + \
                            str(temp_event_id) + ", do you want to change it to " + \
                            str(self.current_event_id + 1) + "?"
                        answer = messagebox.askyesno(
                            "Question", prompt_message)
                        if answer:
                            self.current_event_id += 1
                            self.current_event_name = self.textbox_new_id.get(
                                "1.0", tk.END).rstrip('\n')
                            self.mega_events.append(self.current_event_name)
                            self.button_previous_id_var.set(
                                "USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
                            self.mega_event_dic["id"] = self.current_event_id
                            self.mega_event_dic["name"] = self.current_event_name
                        else:
                            prompt_message_en = "In current snippet/shot, event name is '" + \
                                str(temp_event_name) + "', do you want to change it to " + \
                                self.textbox_new_id.get(
                                    "1.0", tk.END).rstrip('\n') + "?"
                            answer_en = messagebox.askyesno(
                                "Question", prompt_message_en)
                            if answer_en:
                                self.current_event_name = self.textbox_new_id.get(
                                    "1.0", tk.END).rstrip('\n')
                                self.mega_events.append(
                                    self.current_event_name)
                                self.mega_event_dic["id"] = self.current_event_id
                                self.mega_event_dic["name"] = self.current_event_name
                            else:
                                self.mega_event_dic["id"] = temp_event_id
                                self.mega_event_dic["name"] = temp_event_name
                    else:
                        self.current_event_id += 1
                        self.current_event_name = self.textbox_new_id.get(
                            "1.0", tk.END).rstrip('\n')
                        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
                            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                                temp_event_id = int(self.output_dict[str(
                                    self.current_snippet - 1)]['mega_event']['id'])
                                temp_event_name = self.output_dict[str(
                                    self.current_snippet - 1)]['mega_event']['name']
                                self.button_previous_id_var.set(
                                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)

                        # self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
                        self.mega_event_dic["id"] = self.current_event_id
                        self.mega_event_dic["name"] = self.current_event_name
                elif(self.radio_button_var.get() == 2):
                    print(self.radio_button_var.get())
                    self.mega_event_dic["id"] = self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['id']
                    self.mega_event_dic["name"] = self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['name']
                else:
                    self.mega_event_dic["id"] = int(
                        self.output_dict[str(self.current_snippet)]['mega_event']['id'])
                    self.mega_event_dic["name"] = self.output_dict[str(
                        self.current_snippet)]['mega_event']['name']
                category_caption_dict['mega_event'] = self.mega_event_dic

        #copy sceneId info, if exists
        if str(self.current_snippet) in self.output_dict and "sceneId" in self.output_dict[str(self.current_snippet)]:
            print("sceneId was was there in", str(self.current_snippet), " retaining it")
            category_caption_dict["sceneId"] = self.output_dict[str(self.current_snippet)]["sceneId"]

        self.output_dict[str(self.current_snippet)] = category_caption_dict

        if(str(self.current_snippet) in self.output_dict):
            currect_snippet_dict = self.output_dict[str(self.current_snippet)]
            if("mega_event" in currect_snippet_dict):
                previous_event_name = currect_snippet_dict["mega_event"]["name"].rstrip(
                    '\n')
                # print("previous_event_name = "+previous_event_name)
                new_event_name = self.textbox_new_id.get("1.0", tk.END).strip()
                # print("new_event_name = "+new_event_name)
                if(previous_event_name != new_event_name and new_event_name != ""):
                    event_id = currect_snippet_dict["mega_event"]["id"]
                    for each_key in self.output_dict.keys():
                        if each_key not in self.dict_keys and 'mega_event' in self.output_dict[each_key]:
                            if(self.output_dict[each_key]["mega_event"]["id"] == event_id):
                                self.output_dict[each_key]["mega_event"]["name"] = new_event_name
                                # print("Done")

        with open(self.video_file_name_with_location + '.json', 'w') as fp:
            json.dump(self.output_dict, fp)

        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            self.display_selected_keys.set("")

        self.textbox_json.configure(state=NORMAL)
        self.textbox_json.delete("1.0", tk.END)
        self.textbox_json.insert(
            tk.END, json.dumps(self.output_dict, indent=4))
        self.textbox_json.configure(state=DISABLED)
        if 'mega_event' in self.output_dict[str(self.current_snippet)]:
            if(self.output_dict[str(self.current_snippet)]["mega_event"]["id"] == self.current_event_id):
                self.current_event_name = self.output_dict[str(
                    self.current_snippet)]["mega_event"]["name"]
        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
        else:
            self.button_previous_id_var.set(
                "USE PREVIOUS ID: " + "_" + ": " + "_")
        # self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.set_window_name()

        # Uncomment to enable Auto Sync
        # self.text_drive_sync_status.set("Syncing to drive ...")
        # self.drive_sync()
        # self.text_drive_sync_status.set("Sync completed succesfully")

    def same_as_previous(self):
        if(str(self.current_snippet - 1) in self.output_dict):
            for category in self.keyword_state_dict:
                for keyword in self.keyword_state_dict[category]:
                    self.keyword_state_dict[category][keyword].set(False)
            message = ""
            if('categories' in self.output_dict[str(self.current_snippet - 1)]):
                currect_snippet_dict = self.output_dict[str(
                    self.current_snippet - 1)]['categories']
                for category in currect_snippet_dict:
                    message += category.upper() + ': '
                    for keyword in currect_snippet_dict[category]:
                        message += keyword + ', '
                        self.keyword_state_dict[category][keyword].set(True)
                    message += '\n'
            self.textbox_sentence.delete("1.0", tk.END)
            if('caption' in self.output_dict[str(self.current_snippet - 1)]):
                self.textbox_sentence.insert(
                    tk.END, self.output_dict[str(self.current_snippet - 1)]['caption'])
            self.display_selected_keys.set(message)

    def block_video_buttons(self):
        self.button_next.configure(state=DISABLED)
        self.button_browse.configure(state=DISABLED)
        self.button_previous.configure(state=DISABLED)
        self.button_play.configure(state=DISABLED)
        self.button_play_prev.configure(state=DISABLED)
        self.button_play_next.configure(state=DISABLED)
        self.textbox_goto.configure(state="disabled")
        self.button_goto.configure(state=DISABLED)
        if visualize == True:
            self.button_vis_next.configure(state=DISABLED)
            self.button_vis_prev.configure(state=DISABLED)

    def unblock_video_buttons(self):
        self.button_next.configure(state=NORMAL)
        self.button_browse.configure(state=NORMAL)
        self.button_previous.configure(state=NORMAL)
        self.button_play.configure(state=NORMAL)
        self.button_play_prev.configure(state=NORMAL)
        self.button_play_next.configure(state=NORMAL)
        self.textbox_goto.configure(state="normal")
        self.button_goto.configure(state=NORMAL)
        if self.visualize == True:
            if self.searchIndex > 0:
                #self.button_vis_next.configure(state=NORMAL)
                self.button_vis_prev.configure(state=NORMAL)
            if self.searchIndex < len(self.vis_snippets) - 1:
                self.button_vis_next.configure(state=NORMAL)
                #self.button_vis_prev.configure(state=NORMAL)
            #else:
                #self.button_vis_next.configure(state=NORMAL)
                #self.button_vis_prev.configure(state=NORMAL)

    def block_annotation_buttons(self):
        for btns in self.all_button_add_keyword:
            btns.configure(state=DISABLED)
        for txtbx in self.all_textbox_new_keyword:
            txtbx.configure(state="disabled")
        for btns in self.all_menu_buttons:
            btns.configure(state=DISABLED)
        self.button_same_as_previous.configure(state=DISABLED)
        self.textbox_sentence.configure(state="disabled")
        self.is_snippet_transition.configure(state=DISABLED)
        self.is_event_checkbutton.configure(state=DISABLED)
        self.button_submit.configure(state=DISABLED)
        self.button_generate_new_id.configure(state=DISABLED)
        self.button_previous_id.configure(state=DISABLED)
        self.textbox_new_id.configure(state=DISABLED)
        self.event_menu.configure(state=DISABLED)
        self.cap_menu.configure(state=DISABLED)

    def unblock_annotation_buttons(self):
        for btns in self.all_button_add_keyword:
            btns.configure(state=NORMAL)
        # for txtbx in self.all_textbox_new_keyword:
        #    txtbx.configure(state="normal")
        for btns in self.all_menu_buttons:
            btns.configure(state=NORMAL)
        if(self.current_snippet > 1):
            self.button_same_as_previous.configure(state=NORMAL)
        if "techtalk.json" in config_file_location:
            self.textbox_sentence.configure(state="normal")
        self.is_snippet_transition.configure(state=NORMAL)
        if "techtalk.json" not in config_file_location:
            self.is_event_checkbutton.configure(state=NORMAL)
        self.is_event_checkbutton_var.set(False)
        # self.checked_checkbutton()
        self.button_submit.configure(state=NORMAL)
        self.textbox_new_id.configure(state=NORMAL)
        # self.event_menu.configure(state=NORMAL)
        if "techtalk.json" in config_file_location:
            self.cap_menu.configure(state=NORMAL)
        # if(str(self.current_snippet) in self.output_dict):
        #     self.is_event_checkbutton.configure(state=DISABLED)

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

    def restore_checklist(self):
        for category in self.keyword_state_dict:
            for keyword in self.keyword_state_dict[category]:
                self.keyword_state_dict[category][keyword].set(False)
        self.textbox_sentence.configure(state=NORMAL)
        self.textbox_sentence.delete("1.0", tk.END)
        # self.textbox_sentence.configure(state=DISABLED)
        self.is_snippet_transition_var.set(False)
        self.is_event_checkbutton_var.set(False)
        self.radio_button_var.set(0)
        self.textbox_new_id.configure(state=NORMAL)
        self.textbox_new_id.delete("1.0", tk.END)
        self.textbox_new_id.configure(state=DISABLED)

        if(str(self.current_snippet) in self.output_dict):
            currect_snippet_dict = self.output_dict[str(self.current_snippet)]
            if(currect_snippet_dict["transition"]):
                self.is_snippet_transition_var.set(True)
                self.transitionbutton_click()
            else:
                if("categories" in currect_snippet_dict):
                    currect_snippet_categories_dict = currect_snippet_dict["categories"]
                    for category in currect_snippet_categories_dict:
                        for keyword in currect_snippet_categories_dict[category]:
                            self.keyword_state_dict[category][keyword].set(
                                True)
                if("caption" in currect_snippet_dict):

                    self.textbox_sentence.insert(
                        tk.END, currect_snippet_dict["caption"])
                if("mega_event" in currect_snippet_dict):
                    self.is_event_checkbutton_var.set(True)
                    self.checked_checkbutton()
                    if("name" in currect_snippet_dict["mega_event"]):
                        self.textbox_new_id.configure(state="normal")
                        self.textbox_new_id.insert(
                            tk.END, currect_snippet_dict["mega_event"]["name"])
                    self.is_snippet_transition.configure(state="disabled")
                    # self.is_event_checkbutton.configure(state="disabled")
                    self.button_generate_new_id.configure(state="disabled")
                    self.button_previous_id.configure(state="disabled")

    def play_snippet(self):
        self.snippet_location = self.video_file_location
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        fps = round(self.snippet_capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(self.snippet_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        time_length = int(frame_count / fps)
        # print("FPS: %d , frame_count: %d, time_length: %d" %
        # (round(fps), frame_count, time_length))
        """ if(self.visualize):
            if(self.sd):
                frame_start = self.output_dict[str(
                    self.current_snippet)]['shot_start']
                frames_to_read = self.output_dict[str(
                    self.current_snippet)]['shot_length']
                print("Visualize shot detcetor mode, frame_start = ", frame_start, ", frames_to_read = ", frames_to_read)
            else:
                frame_start = (self.current_snippet - 1) * \
                    (self.snippet_length * fps)
                frames_to_read = self.snippet_length * fps """
        # else:
        # if(self.cps_path != ""):
        #if(os.path.exists(self.video_file_name_with_location + '.xml')):
        if(self.sd == True):
            if(self.current_snippet == 1):
                frame_start = 0
                frames_to_read = self.cps[self.current_snippet - 1] - 1
            else:
                frame_start = self.cps[self.current_snippet - 2]
                frames_to_read = self.cps[self.current_snippet -
                                          1] - frame_start - 1
        else:   # snippet mode
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
                if(self.current_snippet == self.snippet_count):
                    self.button_next.configure(state=DISABLED)
                if(self.current_snippet == 1):
                    self.button_previous.configure(state=DISABLED)
                self.flag_to_pause_video = False
                break
            if(self.flag_to_pause_video):
                continue
            ret, frame = self.snippet_capture.read()
            # if(ret == True and not self.flag_to_stop_video):
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
                # cv2.waitKey(0)
                time.sleep(1 / (fps + 16))
            else:
                self.unblock_video_buttons()
                self.text_pause_button.set("PAUSE")
                self.button_pause.configure(state=DISABLED)
                if(self.current_snippet == self.snippet_count):
                    self.button_next.configure(state=DISABLED)
                if(self.current_snippet == 1):
                    self.button_previous.configure(state=DISABLED)
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
        if(self.visualize):
            self.snippet_count = self.output_dict['num_snippets']
        else:
            if(len(self.cps)):
                self.snippet_count = len(self.cps)
            else:
                self.snippet_count = ceildiv(
                    self.video_length, self.snippet_length)

    def stop(self):
        self.flag_to_stop_video = True
        time.sleep(1 / 20)

    def play_next(self):
        self.next()
        self.play()

    def play_prev(self):
        self.previous()
        self.play()

    def play(self):
        # if(self.visualize and len(self.vis_snippets) > 0):
        #     # i=0
        #     self.current_snippet = self.vis_snippets[0]
        #     self.vis_snippets.pop(0)
        #     self.restore_checklist()
        # elif(self.visualize and len(self.vis_snippets) <= 0):
        #     print("No more snippets to visualize.")
        #     messagebox.showwarning("No More Results", "Reached end of the matching list")

        self.flag_to_stop_video = False
        if(self.current_snippet <= self.snippet_count):
            #self.text_current_snippet.set("Playing snippet number " + str(self.current_snippet) + "\n" + time.strftime('%H:%M:%S', time.gmtime((self.current_snippet * self.snippet_length) - self.snippet_length)) + " -- " + time.strftime('%H:%M:%S', time.gmtime(self.current_snippet * self.snippet_length)))
            self.text_current_snippet.set(
                "Playing shot/snippet number " + str(self.current_snippet))
            self.block_video_buttons()
            self.button_pause.configure(state=NORMAL)
            self.text_play_button.set("REPLAY")

            self.thread = threading.Thread(
                target=self.play_snippet, daemon=True)

            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            # else:
                # self.display_selected_keys.set("")
            self.thread.start()
            # self.thread._stop()

        else:
            self.text_current_snippet.set(
                "!!How is the current snippet more than total number of snippets!!")
        # if(self.visualize and len(self.vis_snippets) > 0):
        #     while(self.vis_snippets[0] == self.current_snippet + 1):
        #         self.play()

    def next(self):
        self.textbox_sentence.delete("1.0", tk.END)
        # if(not(self.submitted)):
        #     messagebox.showwarning("Error",
        #                            "Save to Json before going to next snippet/shot?")
        #     return
        # self.submitted = False
        self.stop()
        self.create_checklist()
        if(self.current_snippet < self.snippet_count):
            self.current_snippet += 1
            self.text_play_button.set("PLAY")
            if (self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
            if str(self.current_snippet - 1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()

            if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
                if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                    temp_event_id = int(self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['id'])
                    temp_event_name = self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['name']
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
                else:
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + "_" + ": " + "_")
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")

            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")

            self.text_current_snippet.set(
                "Current shot/snippet number " + str(self.current_snippet))
            self.button_previous.configure(state=NORMAL)
            self.stop()
            # self.play()
            self.restore_checklist()

        else:
            self.text_current_snippet.set(
                "!!How come NEXT got clicked after last snippet!!")
        self.set_window_name()

    def display_message_instant(self):
        # self.display_selected_keys.set("supp")
        # print(self.keyword_state_dict)
        category_dict = {}
        for category in self.keyword_state_dict:
            keyword_dict = []
            for keyword in self.keyword_state_dict[category]:
                if self.keyword_state_dict[category][keyword].get():
                    keyword_dict.append(keyword)
            if len(keyword_dict) > 0:
                category_dict[category] = keyword_dict
        # print(category_dict)
        message = ""
        for cat, listt in category_dict.items():
            message += cat.upper() + ': '
            for checked_keys in category_dict[cat]:
                message += checked_keys.rstrip('\n') + ', '
            message += '\n'
        if (str(self.current_snippet) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet)]:
                message += 'EVENT ID: ' + \
                    str(self.output_dict[str(self.current_snippet)]
                        ['mega_event']['id']) + ', '
                message += '\n'
                message += 'EVENT NAME: ' + \
                    str(self.output_dict[str(self.current_snippet)]
                        ['mega_event']['name']) + ', '
                message += '\n'
        self.display_selected_keys.set(message)

    def display_message(self):
        message = ""
        if 'categories' in self.output_dict[str(self.current_snippet)]:
            for cat, listt in self.output_dict[str(self.current_snippet)]['categories'].items():
                message += cat.upper() + ': '
                for checked_keys in self.output_dict[str(self.current_snippet)]['categories'][cat]:
                    message += checked_keys.rstrip('\n') + ', '
                message += '\n'
        if 'mega_event' in self.output_dict[str(self.current_snippet)]:
            message += 'EVENT ID: ' + \
                str(self.output_dict[str(self.current_snippet)]
                    ['mega_event']['id']) + ', '
            message += '\n'
            message += 'EVENT NAME: ' + \
                str(self.output_dict[str(self.current_snippet)]
                    ['mega_event']['name']) + ', '
            message += '\n'
        if 'sceneId' in self.output_dict[str(self.current_snippet)]:
            message += 'SCENE ID: ' + \
                str(self.output_dict[str(self.current_snippet)]['sceneId'])
        self.display_selected_keys.set(message)

    def previous(self):
        self.textbox_sentence.delete("1.0", tk.END)
        self.stop()
        if(self.current_snippet > 1):
            self.current_snippet -= 1
            self.text_play_button.set("PLAY")
            if(self.current_snippet == 1):
                self.unblock_annotation_buttons()
                self.button_previous.configure(state=DISABLED)
            elif str(self.current_snippet - 1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()

            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")

            if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
                if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                    temp_event_id = int(self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['id'])
                    temp_event_name = self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['name']
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
                else:
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + "_" + ": " + "_")
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")

            self.text_current_snippet.set(
                "Current shot/snippet: " + str(self.current_snippet))
            self.button_next.configure(state=NORMAL)
            self.stop()
            # self.play()
            self.restore_checklist()

        else:
            self.text_current_snippet.set(
                "!!How come PREVIOUS got clicked on first snippet!!")
        self.set_window_name()

    def goto(self):
        self.textbox_sentence.delete("1.0", tk.END)
        self.goto_snippet = self.textbox_goto.get("1.0", tk.END)
        self.goto_snippet = int(self.goto_snippet)
        self.stop()
        if(self.goto_snippet > 0 and self.goto_snippet <= self.snippet_count):
            self.current_snippet = self.goto_snippet
            self.text_current_snippet.set(
                "Current snippet/shot number " + str(self.current_snippet))
            self.text_play_button.set("PLAY")
            if (self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
            if self.current_snippet == 1:
                self.button_previous.configure(state=DISABLED)
                self.unblock_annotation_buttons()
            elif str(self.current_snippet - 1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")

            if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
                if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                    temp_event_id = int(self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['id'])
                    temp_event_name = self.output_dict[str(
                        self.current_snippet - 1)]['mega_event']['name']
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
                else:
                    self.button_previous_id_var.set(
                        "USE PREVIOUS ID: " + "_" + ": " + "_")
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")

            self.restore_checklist()
            self.stop()
            # self.play()
        else:
            #self.text_current_snippet.set("Invalid snippet/shot number")
            messagebox.showwarning("Error", "Invalid shot/snippet number")
        self.textbox_goto.delete("1.0", tk.END)
        self.set_window_name()

    def check():
        d = ""
        for i in range(len(OPTIONS)):
            for j in range(len(OPTIONS[i])):
                if all_bool_var[i][j].get():
                    d += OPTIONS[i][j] + " "
        text_current_snippet.set(d)

    def vis_keyword(self):
        key = self.textbox_vis_keyword.get("1.0", tk.END).strip()
        print("Looking for snippets with keyword: ", key)
        self.vis_snippets = []
        for i in range(1, self.snippet_count + 1):
            # print(self.output_dict[str(i)]["categories"])
            if "categories" in self.output_dict[str(i)]:
                for category, keywords in self.output_dict[str(i)]["categories"].items():
                    for keyword in keywords:
                        # print(keyword)
                        if(key.lower() in keyword.lower()):
                            self.vis_snippets.append(i)
            if key.lower() == "transition" and "transition" in self.output_dict[str(i)] and self.output_dict[str(i)]["transition"]:
                self.vis_snippets.append(i)
        # if('shot_start' in self.output_dict['1']):
        # if(os.path.exists(self.video_file_name_with_location + '.xml')):
        # if(os.path.exists(self.video_file_name_with_location + '.xml')):
        #     self.sd = True
        # else:
        #     print("shot xml not found, assuming snippet mode")
        #     self.sd = False
        print(self.vis_snippets)
        
        if len(self.vis_snippets) == 0:
            messagebox.showwarning(
                "No Match", "No snippets/shots matching the keywords")
            return

        # goto the first matching snippet
        self.searchIndex = 0
        
        self.text_num_results.set("Result snippets = " + str(len(self.vis_snippets)) + " Current index = " + str(self.searchIndex))
        
        self.stop
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_current_snippet.set(
            "Current snippet/shot number " + str(self.current_snippet))
        self.text_play_button.set("PLAY")
        if (self.current_snippet == self.snippet_count):
            self.button_next.configure(state=DISABLED)
        self.button_vis_prev.configure(state=DISABLED)
        if len(self.vis_snippets) == 1:
            self.button_vis_next.configure(state=DISABLED)
        else:
            self.button_vis_next.configure(state=NORMAL)
        if self.current_snippet == 1:
            self.button_previous.configure(state=DISABLED)
            self.unblock_annotation_buttons()
        elif str(self.current_snippet - 1) not in self.output_dict.keys():
            # this should never happen in visualize mode
            self.block_annotation_buttons()
        else:
            self.unblock_annotation_buttons()
        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            # this should never happen in visualize mode
            self.display_selected_keys.set("")

        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")
        else:
            self.button_previous_id_var.set(
                "USE PREVIOUS ID: " + "_" + ": " + "_")

        self.restore_checklist()
        self.stop()
        self.set_window_name()
        self.play()
        self.button_vis_prev.configure(state=DISABLED)

        # for i in range(len(self.vis_snippets)):
        #     self.current_snippet = self.vis_snippets[i]
        #     self.play()
        #     while(self.vis_snippets[i + 1]==self.vis_snippets[i] + 1):
        #         i = i + 1
        #         self.current_snippet = self.vis_snippets[i]
        #         self.play()

    def vis_mega(self):
        key = self.textbox_vis_mega.get("1.0", tk.END).strip()
        if not key:
            print("Looking for snippets marked as mega events")
        else:
            print("Looking for snippets marked with mega event: ", key)
        
        self.vis_snippets = []
        for i in range(1, self.snippet_count + 1):
            if "mega_event" in self.output_dict[str(i)]:
                if not key:
                    self.vis_snippets.append(i)
                else:
                    if(key.lower() in self.output_dict[str(i)]["mega_event"]["name"].lower()):
                        self.vis_snippets.append(i)
        # if('shot_start' in self.output_dict['1']):
        # if(os.path.exists(self.video_file_name_with_location + '.xml')):
        #     self.sd = True
        # else:
        #     self.sd = False
        #     print("shot xml not found, assuming snippet mode")
        print(self.vis_snippets)
        if len(self.vis_snippets) == 0:
            messagebox.showwarning(
                "No Match", "No snippets/shots matching the mega events")
            return


        # goto the first matching snippet
        self.searchIndex = 0

        self.text_num_results.set("Result snippets = " + str(len(self.vis_snippets)) + " Current index = " + str(self.searchIndex))

        self.stop
        self.current_snippet = self.vis_snippets[self.searchIndex]
        self.text_current_snippet.set(
            "Current snippet/shot number " + str(self.current_snippet))
        self.text_play_button.set("PLAY")
        if (self.current_snippet == self.snippet_count):
            self.button_next.configure(state=DISABLED)
        self.button_vis_prev.configure(state=DISABLED)
        if len(self.vis_snippets) == 1:
            self.button_vis_next.configure(state=DISABLED)
        else:
            self.button_vis_next.configure(state=NORMAL)
        if self.current_snippet == 1:
            self.button_previous.configure(state=DISABLED)
            self.unblock_annotation_buttons()
        elif str(self.current_snippet - 1) not in self.output_dict.keys():
            # this should never happen in visualize mode
            self.block_annotation_buttons()
        else:
            self.unblock_annotation_buttons()
        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            # this should never happen in visualize mode
            self.display_selected_keys.set("")

        if (self.current_snippet > 1 and str(self.current_snippet - 1) in self.output_dict):
            if 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)
            else:
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + "_" + ": " + "_")
        else:
            self.button_previous_id_var.set(
                "USE PREVIOUS ID: " + "_" + ": " + "_")

        self.restore_checklist()
        self.stop()
        self.set_window_name()
        self.play()

    def fixcps(self, fps=25, shot_thresh=4):
        print("cps before manipulation: ", self.cps)
        for cp in self.cps:
            if(self.cps.index(cp) == 0):
                continue
            ele_ind = self.cps.index(cp)
            #TODO: this has a bug when you have two consecutive candidates for removal
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

    def browse(self):

        # reset UI
        self.stop()
        self.cps = []
        self.display_selected_keys.set("")
        self.current_event_id = 0
        self.current_event_name = "_"
        self.button_previous_id_var.set(
            "USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.textbox_json.configure(state=NORMAL)
        self.textbox_json.delete("1.0", tk.END)
        self.textbox_json.configure(state=DISABLED)
        self.restore_checklist()
        self.text_snippet_count.set("")
        self.text_current_snippet.set("")
        self.textbox_new_id.delete("1.0", tk.END)
        self.textbox_new_id.configure(state=DISABLED)
        self.text_video_file_location.set("")

        # open the video file
        self.video_file_location = askopenfilename()
        if(isinstance(self.video_file_location, tuple)):
            return
        self.video_file_extension = self.video_file_location.split('.')[-1]
        if(self.video_file_extension != 'mp4' and self.video_file_extension != 'avi'):
            self.text_current_snippet.set(
                "Chosen file must be either .avi or .mp4")
            return

        self.video_file_name_with_location = self.video_file_location.split('.')[
            0]

        # Parse the shots change points xml file if it exists
        # if(self.cps_path != ""):
        # if(not(self.visualize)):

        if self.visualize == True:
            self.json_file_name_with_location = self.video_file_name_with_location + '.json'
            if path.exists(self.json_file_name_with_location):
                with open(self.json_file_name_with_location) as json_file:
                    self.output_dict = json.load(
                        json_file, object_pairs_hook=OrderedDict)
                print("Annotation file is present - loaded the annotations")
                self.cps = []
                if "birthday.json" in config_file_location or "wedding.json" in config_file_location or "friends.json" in config_file_location:
                    self.sd = True
                    index = 1
                    while True:
                        try:
                            temp = self.output_dict[str(index)].keys()
                        except:
                            print("Snippet: ", index, " does not exist, we are done with cps")
                            break
                        self.cps.append(self.output_dict[str(index)]["shot_start"] + self.output_dict[str(index)]["shot_length"])
                        index += 1
                    self.cps = list(map(int, self.cps))
                    print("Change Points: ", self.cps, len(self.cps))
                else:
                    self.sd = False
            else:
                messagebox.showwarning(
                    "Warning", "Vis mode, but no annotation file present!")
                sys.exit(0)

        else:
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
                print("shot xml not found, assuming snippet mode")
        

        self.json_file_name_with_location = self.video_file_name_with_location + '.json'
        self.output_dict = {}
        self.current_snippet = 1
        self.text_play_button.set("PLAY")
        self.dict_keys = ["video_name", "video_category",
                          "snippet_size", "duration", "num_snippets", "num_scenes", "num_frames", "fps"]
        # check if annotated json for this video exists
        if path.exists(self.json_file_name_with_location):
            with open(self.json_file_name_with_location) as json_file:
                self.output_dict = json.load(
                    json_file, object_pairs_hook=OrderedDict)
            print("Annotation file is present - loading the annotations")
            self.textbox_json.configure(state=NORMAL)
            self.textbox_json.delete("1.0", tk.END)
            self.textbox_json.insert(
                tk.END, json.dumps(self.output_dict, indent=4))
            self.textbox_json.configure(state=DISABLED)
            for each_key in self.output_dict.keys():
                # 33
                if each_key not in self.dict_keys:
                    if "caption" in self.output_dict[str(each_key)]:
                        caption = self.output_dict[str(each_key)]['caption']
                        if caption not in self.captions:
                            self.captions.append(caption)
                            # self.var.set('')
                            self.cap_menu['menu'].add_command(
                                label=caption, command=tk._setit(self.var, caption))
                            self.cap_menu.destroy()
                            self.cap_menu = OptionMenu(
                                self.window, self.var, *self.captions, command=self.returnSel)
                            self.cap_menu.grid(in_=self.container_middle,
                                               row=1, column=1, columnspan=3, sticky="nsew")
                            # checkbutton = self.cap_menu.menu.add_checkbutton(
                            #     label=caption, onvalue=True, offvalue=False, variable=self.keyword_variable)
                ###############################################
                # print(each_key)
                if each_key not in self.dict_keys and 'mega_event' in self.output_dict[str(each_key)]:
                    if int(self.output_dict[str(each_key)]['mega_event']['id']) > self.current_event_id:
                        self.current_event_id = int(
                            self.output_dict[str(each_key)]['mega_event']['id'])
                        self.current_event_name = self.output_dict[str(
                            each_key)]['mega_event']['name']
                if each_key not in self.dict_keys and int(each_key) > self.current_snippet:
                    self.current_snippet = int(each_key)
            self.cap_menu.destroy()
            self.cap_menu = OptionMenu(
                self.window, self.var, *self.captions, command=self.returnSel)
            self.cap_menu.grid(in_=self.container_middle,
                               row=1, column=1, columnspan=3, sticky="nsew")
            if self.current_snippet > 1 and 'mega_event' in self.output_dict[str(self.current_snippet - 1)]:
                temp_event_id = int(self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['id'])
                temp_event_name = self.output_dict[str(
                    self.current_snippet - 1)]['mega_event']['name']
                self.button_previous_id_var.set(
                    "USE PREVIOUS ID: " + str(temp_event_id) + ": " + temp_event_name)

            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")

        self.video_file_name = self.video_file_name_with_location.split(
            '/')[-1]
        self.window.title(self.video_file_name)
        self.get_snippet_count()
        self.output_dict['video_name'] = self.video_file_location.split(
            '/')[-1]
        # self.output_dict['video_category'] = self.video_file_name.split('_')[0]
        self.output_dict['video_category'] = sys.argv[1].split('.')[0]
        self.output_dict['snippet_size'] = self.snippet_length
        self.output_dict['num_snippets'] = self.snippet_count
        self.output_dict['duration'] = self.video_length

        # self.get_snippet_count()
        self.text_snippet_count.set(
            "Total number of snippets/shots are " + str(self.snippet_count))
        self.split_command = "python3 splitter/ffmpeg-split.py -f " + \
            self.video_file_location + " -s " + \
            str(self.snippet_length) + " >/dev/null 2>&1"

        self.text_video_file_location.set(self.video_file_location)
        self.text_current_snippet.set(
            "Selected snippet/shot number " + str(self.current_snippet))
        # os.system(self.split_command)
        self.unblock_video_buttons()
        if(self.current_snippet > 1):
            self.button_same_as_previous.configure(state=NORMAL)
            if(self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
        else:
            self.button_previous.configure(state=DISABLED)

        self.set_window_name()
        self.restore_checklist()
        self.button_submit.configure(state=NORMAL)

    def get_max_done_snippet_id(self):
        max_key = 0
        for each_key in self.output_dict.keys():
            if each_key not in self.dict_keys and int(each_key) > max_key:
                max_key = int(each_key)
        return max_key

    def set_window_name(self):
        max_done_snippet_id = self.get_max_done_snippet_id()
        self.window.title(self.video_file_name + "." + self.video_file_extension +
                          " (# Annotated Snippets/Shots: " + str(max_done_snippet_id) + " / " + str(self.snippet_count) + ")")

    def drive_sync(self):
        self.text_drive_sync_status.set("Syncing to drive ...")
        remote_config = "from_Gdrive"
        if(not(os.path.exists(remote_config))):
            os.mkdir(remote_config)
        res = str(subprocess.check_output("drive_sync -ls", shell=True))
        file_id = res.split(',')[1].split(' ')[2][:-3]
        file_name = res.split(',')[0].split(' ')[1]
        if(os.path.exists(os.path.join(remote_config, file_name))):
            os.remove(os.path.join(remote_config, file_name))
        os.system("drive_sync -d " + file_id)
        print("config json downloaded succesfully from drive")
        remote_config_file_dictionary = json.load(
            codecs.open(os.path.join(remote_config, file_name), 'r', 'utf-8-sig'), object_pairs_hook=OrderedDict)
        remote_category_keyword_dictionary = remote_config_file_dictionary["categories"]
        merged_category_keyword_dictionary = {}
        for category, remote_dict in remote_category_keyword_dictionary.items():
            remote_keywords = remote_dict["keywords"]
            remote_captions = remote_dict["keywords_desc"].split("\n")
            local_keywords = self.category_keyword_dictionary[category]["keywords"]
            local_captions = self.category_keyword_dictionary[category]["keywords_desc"].split(
                "\n")

            # Merge local and remote Keywords
            if(not(set(remote_keywords) == set(local_keywords))):
                self.category_keyword_dictionary[category]["keywords"] = list(set(
                    remote_keywords + local_keywords))
            else:
                self.category_keyword_dictionary[category]["keywords"] = remote_keywords

            # Merge local and remote captions
            if(not(set(remote_captions) == set(local_captions))):
                self.category_keyword_dictionary[category]["keywords_desc"] = '\n'.join(
                    list(set(remote_captions + local_captions)))
            else:
                self.category_keyword_dictionary[category]["keywords_desc"] = '\n'.join(
                    remote_captions)

        config_file_dictionary["categories"] = self.category_keyword_dictionary

        # Merge mega events
        remote_me = remote_config_file_dictionary["mega_events"]
        local_me = self.mega_events
        if(not(set(remote_me) == set(local_me))):
            config_file_dictionary["mega_events"] = list(
                set(remote_me + local_me))
        else:
            config_file_dictionary["mega_events"] = remote_me

        # print(type(config_file_dictionary))
        with open(config_file_location, 'w') as fp:
            json.dump(config_file_dictionary, fp)
        os.system("drive_sync -remove remote " + file_id)
        os.system("drive_sync -upload " + config_file_location)
        print("Sync completed succesfully")
        self.text_drive_sync_status.set("Sync completed succesfully")


if __name__ == "__main__":
    config_file_location = sys.argv[1]
    fullScreen = False
    visualize = False
    if(len(sys.argv) == 3):
        if(sys.argv[2] == "full"):
            fullScreen = True
        elif(sys.argv[2] == "vis"):
            visualize = True
    config_file_dictionary = json.load(
        codecs.open(config_file_location, 'r', 'utf-8-sig'), object_pairs_hook=OrderedDict)

    snippet_length = config_file_dictionary["snippet_size"]
    category_keyword_dictionary = config_file_dictionary["categories"]
    mega_events = config_file_dictionary["mega_events"]

    # Create a window and pass it to the Application object
    w = App(tk.Tk(), snippet_length,
            category_keyword_dictionary, mega_events, fullScreen, visualize)
