import sys
import os
from os import path
from collections import OrderedDict
import cv2
import json


summary_path = sys.argv[1]
ann_path = sys.argv[2]
ratings_path = sys.argv[3]
video_path = sys.argv[4]
output_video_path = sys.argv[5]

if path.exists(summary_path):
    with open(summary_path) as json_file:
        summary_dict = json.load(
            json_file, object_pairs_hook=OrderedDict)

if path.exists(ann_path):
    with open(ann_path) as json_file:
        ann_dict = json.load(
            json_file, object_pairs_hook=OrderedDict)

if path.exists(ratings_path):
    with open(ratings_path) as json_file:
        ratings_dict = json.load(
            json_file, object_pairs_hook=OrderedDict)

print(video_path)
shot_capture = cv2.VideoCapture(video_path)
width = int(shot_capture.get(3))
print("Width: ", width)
height = int(shot_capture.get(4))
print("height: ", height)
fps = round(shot_capture.get(cv2.CAP_PROP_FPS))
#frame_count = int(shot_capture.get(cv2.CAP_PROP_FRAME_COUNT))
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(
    *'XVID'), fps, (width, height))


if len(summary_dict['summary']) != summary_dict['video_num_frames']:
    print("Mismtach in length of summary vector and number of frames in video")
    sys.exit()

change_points = []
n_frame_per_seg = []
shot_nums = [-1] * len(summary_dict['summary'])
#get change points for shot mode
if "friends" in video_path or "birthday" in video_path or "wedding" in video_path:
    num_snippets = ann_dict["num_snippets"]
    for i in range(1, num_snippets + 1):
        start = ann_dict[str(i)]["shot_start"]
        end = start + ann_dict[str(i)]["shot_length"] - 1
        change_points.append((start, end))
        n_frame_per_seg.append(ann_dict[str(i)]["shot_length"])
    #store shot number for each frame
    for k in range(len(change_points)):
        shot_nums[change_points[k][0]:change_points[k][1]+1] = [k+1] * \
            (change_points[k][1]+1 - change_points[k][0])
    #print(change_points)
    #print(shot_nums)

snippet_length = 0
if "soccer" in video_path:
    snippet_length = 5
else:
    snippet_length = 2

#for each frame in summary
for frame_num in [i for i, x in enumerate(summary_dict['summary']) if x == 1]:
    print("."),
    #check which shot it belongs to
    shot = 0
    if "soccer" in video_path or "techtalk" in video_path or "surveillance" in video_path:
        #snippet mode
        shot = int(frame_num/(fps*snippet_length)) + 1
    else:
        #shot mode
        shot = shot_nums[frame_num]
    #print("Frame", frame_num, "Shot", shot)
    #get the desired annotations from that shot
    # Find keyword with max rating in the shot
    max_keyword = ""
    max_rating = 0
    min_keyword = ""
    min_rating = 100

    if "categories" in ann_dict[str(shot)]:
        for category, keywords in ann_dict[str(shot)]["categories"].items():
            for keyword in keywords:
                keyword_ind = ratings_dict["categories"][category]["keywords"].index(
                    keyword)
                keyword_rating = ratings_dict["categories"][category]["ratings"][keyword_ind]
                if(keyword_rating > max_rating):
                    max_rating = keyword_rating
                    max_keyword = keyword
                if(keyword_rating < min_rating):
                    min_rating = keyword_rating
                    min_keyword = keyword
        max_text = "Max Keyword: " + str(max_keyword) + " : " + str(max_rating)
        min_text = "Min Keyword: " + str(min_keyword) + " : " + str(min_rating)
    else:
        #it must be a transition shot
        max_text = "Transition shot/snippet"
        min_text = "Transition shot/snippet"

    # Check if shot is in a megaevent
    me_name = ""
    if "mega_event" in ann_dict[str(shot)]:
        me_name = ann_dict[str(shot)]["mega_event"]["name"]
    #grab this frame
    shot_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = shot_capture.read()
    #annotate appropriately
    if ret:
        if "soccer" in video_path or "surveillance" in video_path:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # frame = cv2.resize(frame, (width, height))
            # font
            font = cv2.FONT_HERSHEY_SIMPLEX
            # org = (50, 50)
            # fontScale
            fontScale = 1
            # Blue color in BGR
            color = (255, 255, 255)
            # Line thickness of 2 px
            thickness = 1
            # Using cv2.putText() method
            frame = cv2.putText(frame, str(shot), (50, height - 200),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            frame = cv2.putText(frame, max_text, (50, height - 150),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            frame = cv2.putText(frame, min_text, (50, height - 100),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            if(me_name != ""):
                frame = cv2.putText(
                    frame, "Mega Event: " + me_name, (50, height - 50), font, fontScale, color, thickness, cv2.LINE_AA)
            #cv2.imshow("frame", frame)
            out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # frame = cv2.resize(frame, (width, height))
            # font
            font = cv2.FONT_HERSHEY_SIMPLEX
            # org = (50, 50)
            # fontScale
            fontScale = 0.5
            # Blue color in BGR
            color = (255, 255, 255)
            # Line thickness of 2 px
            thickness = 1
            # Using cv2.putText() method
            frame = cv2.putText(frame, str(shot), (25, height - 100),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            frame = cv2.putText(frame, max_text, (25, height - 75),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            frame = cv2.putText(frame, min_text, (25, height - 50),
                                font, fontScale, color, thickness, cv2.LINE_AA)
            if(me_name != ""):
                frame = cv2.putText(
                    frame, "Mega Event: " + me_name, (25, height - 25), font, fontScale, color, thickness, cv2.LINE_AA)
            #cv2.imshow("frame", frame)
            out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("WARNING - Frame number ", frame_num, " doesn't exist in the video!!!")
        sys.exit()
shot_capture.release()
out.release()
