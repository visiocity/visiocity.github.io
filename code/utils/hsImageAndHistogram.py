import matplotlib
matplotlib.use('Agg')
import numpy as np
import cv2
import json
import sys
import os
from os import path
import matplotlib.pyplot as plt
from collections import OrderedDict

def getCumulative(i, toPlot, numHumanSummaries):
    val = 0
    for k in range(i+1, numHumanSummaries+1):
        val += toPlot[k]
    return val

humanSummariesPath = sys.argv[1]
video_name = sys.argv[2]
dataPath = sys.argv[3]
generateVideo = sys.argv[4]
generateImages = sys.argv[5]
mode = sys.argv[6]

humanSummaries = os.listdir(humanSummariesPath)
bnwSummary = []
domain = video_name.split("_")[0]
if domain == "friends":
    video_path = os.path.join(dataPath, domain, video_name) + ".avi"
else:
    video_path = os.path.join(dataPath, domain, video_name) + ".mp4"
vidcap = cv2.VideoCapture(video_path)
opencvFps = vidcap.get(cv2.CAP_PROP_FPS)
print(cv2.__version__)
distribution = {}
numHumanSummaries = len(humanSummaries)
for humanSummary in humanSummaries:
    print("Processing ", humanSummary)
    hsPath = os.path.join(humanSummariesPath, humanSummary)
    with open(hsPath) as json_data:
        d = json.load(json_data)
        hs = d['summary']
        seconds = []
        start = 0
        second = 0
        while start < len(hs):
            start = int(round(second * opencvFps))
            end = int(round((second+1) * opencvFps)) - 1
            #print("Checking ", start, end)
            if all(ele == 1 for ele in hs[start:end+1]):
                seconds.append(0.0)
                distribution.setdefault(second, []).append(humanSummary.split("_")[0])
            elif all(ele == 0 for ele in hs[start:end+1]):
                seconds.append(255.0)
            else:
                print("Not matching second boundaries!", hs[start:end+1])
                sys.exit()
            second += 1
            start = int(round(second * opencvFps))
        for i in range(10):
            bnwSummary.append(seconds)
npSummary = np.array(bnwSummary)


# if not os.path.exists(video_name):
#     os.mkdir(video_name)

cv2.imwrite(video_name+"_humanSummaries.png", npSummary)

if(generateVideo == "True" or generateVideo == "true"):
    ann_path = sys.argv[7]
    ratings_path = sys.argv[8]

    if path.exists(ann_path):
        with open(ann_path) as json_file:
            ann_dict = json.load(json_file, object_pairs_hook=OrderedDict)

    if path.exists(ratings_path):
        with open(ratings_path) as json_file:
            ratings_dict = json.load(json_file, object_pairs_hook=OrderedDict)

    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (224, 224, 224)
    outvideo_path = os.path.basename(video_path)
    outvideo_path = "out_" + outvideo_path
    width = int(vidcap.get(3))
    print("Width: ", width)
    height = int(vidcap.get(4))
    print("height: ", height)
 
    change_points = []
    shot_nums = [-1] * len(hs)
    if "friends" in video_name or "birthday" in video_name or "wedding" in video_name:
        num_snippets = ann_dict["num_snippets"]
        for i in range(1, num_snippets + 1):
            start = ann_dict[str(i)]["shot_start"]
            end = start + ann_dict[str(i)]["shot_length"] - 1
            change_points.append((start, end))
        #store shot number for each frame
        for k in range(len(change_points)):
            shot_nums[change_points[k][0]:change_points[k][1]+1] = [k+1] * \
                (change_points[k][1]+1 - change_points[k][0])

    snippet_length = 0
    if "soccer" in video_name:
        snippet_length = 5
    else:
        snippet_length = 2

    fps = round(opencvFps)
    
    out = cv2.VideoWriter(outvideo_path, cv2.VideoWriter_fourcc(*'XVID'), opencvFps, (width, height))
    start = 0
    second = 0
    frame_num = 0
    shotInfo = True
    while start < len(hs):
        #print("Second: ", second)
        print('#', end='')
        start = int(round(second * opencvFps))
        end = int(round((second+1) * opencvFps)) - 1
        if second in distribution.keys():
            text = distribution[second]
            if len(text) == 1:
                redBorder = True
            else:
                redBorder = False
        else:
            text = ''
            redBorder = False
        for i in range(end-start+1):
            print('.', end='')
            ret, frame = vidcap.read()
            if ret == False:
                print("WARNING: video ended")
                break

            #check which shot this frame belongs to
            shot = 0
            if "soccer" in video_name or "techtalk" in video_name or "surveillance" in video_name:
                #snippet mode
                shot = int(frame_num/(fps*snippet_length)) + 1
                if str(shot) not in ann_dict:
                    print("Shot ", str(shot), " not present in annotation")
                    shotInfo = False
            else:
                #shot mode
                if frame_num >= len(hs):
                    print("frame_num is greater than len summary vector. Cant get shot info")
                    shotInfo = False
                else:
                    shot = shot_nums[frame_num]

            

            if shotInfo:

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

                me_name = ""
                if "mega_event" in ann_dict[str(shot)]:
                    me_name = ann_dict[str(shot)]["mega_event"]["name"]

            if "friends" not in video_name:
                fontScale = 1
                thickness = 2
                if len(text) > 0: # means it is a list
                    s = ","
                    s = s.join(text)
                    cv2.putText(frame, s, (80, 100), font, fontScale, color, thickness, cv2.LINE_AA)

                    if shotInfo:

                        cv2.putText(frame, str(shot), (50, height - 200),
                                        font, fontScale, color, thickness, cv2.LINE_AA)
                        cv2.putText(frame, max_text, (50, height - 150),
                                            font, fontScale, color, thickness, cv2.LINE_AA)
                        cv2.putText(frame, min_text, (50, height - 100),
                                            font, fontScale, color, thickness, cv2.LINE_AA)
                        if(me_name != ""):
                            cv2.putText(
                                frame, "Mega Event: " + me_name, (50, height - 50), font, fontScale, color, thickness, cv2.LINE_AA)
                if redBorder:
                    #frame = cv2.copyMakeBorder(frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, [255, 0, 0]) 
                    frame = cv2.circle(frame, (30, 30), 30, (255, 0, 0), -1) 
            else:
                fontScale = 0.5
                thickness = 1
                if len(text) > 0: # means it is a list
                    s = ","
                    s = s.join(text)
                    cv2.putText(frame, s, (40, 50), font, fontScale, color, thickness, cv2.LINE_AA)

                    if shotInfo:

                        cv2.putText(frame, str(shot), (25, height - 100),
                                        font, fontScale, color, thickness, cv2.LINE_AA)
                        cv2.putText(frame, max_text, (25, height - 75),
                                            font, fontScale, color, thickness, cv2.LINE_AA)
                        cv2.putText(frame, min_text, (25, height - 50),
                                            font, fontScale, color, thickness, cv2.LINE_AA)
                        if(me_name != ""):
                            cv2.putText(
                                frame, "Mega Event: " + me_name, (25, height - 25), font, fontScale, color, thickness, cv2.LINE_AA)
                if redBorder:
                    #frame = cv2.copyMakeBorder(frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, [255, 0, 0]) 
                    frame = cv2.circle(frame, (15, 15), 15, (255, 0, 0), -1) 

            #print("Stamping ", frame_num, " with ", text, " and border ", redBorder)
            out.write(frame)
            frame_num += 1
        second += 1
        start = int(round(second * opencvFps))


#fig, axs = plt.subplots(3)
#fig.suptitle('Distribution of human selections for ' + video_name)

hist = {}
for key, value in distribution.items():
    hist[key] = len(value)

if mode == "hist":
    plt.bar(hist.keys(), hist.values(), 1.0, color='g')
    plt.title('1 sec segments across human summaries for ' + video_name)
    plt.xlabel('Segments/Seconds')
    plt.ylabel('Number of human summaries')
    plt.savefig(video_name + "_hist.png")
else:
    toPlot = {}
    numInZero = 0
    for tmp in range(second):
        if tmp not in hist:
            numInZero += 1
    toPlot[0] = numInZero
        
    for i in range(1, numHumanSummaries+1):
        toPlot[i] = sum(1 for value in hist.values() if value == i)

    videoDuration = 0
    for i in range(numHumanSummaries+1):
        videoDuration += toPlot[i]
    
    if mode == "percent_hist":
        toPlotPercent = {}
        for i in range(numHumanSummaries+1):
            toPlotPercent[i] = (toPlot[i]*100)/videoDuration

        #print("toPlot: ", toPlot)

        bars = plt.bar(toPlotPercent.keys(), toPlotPercent.values(), 1.0, color='g')
        #xlocs = axs[1].xticks
        #xlabs = axs[1].xticklabels
        xlocs, xlabs = plt.xticks()
        xlocs=[i for i in toPlotPercent.keys()]
        xlabs=[i for i in toPlotPercent.keys()]
        plt.title('% of 1 sec segments vs no. of summaries they appear in for ' + video_name)
        plt.xlabel('Number of human summaries')
        plt.ylabel('% of 1 second segments')
        plt.xticks(xlocs, xlabs)
        for bar in bars:
            yval = round(bar.get_height(), 1)
            plt.text(bar.get_x(), yval + 0.01, yval)
        plt.savefig(video_name + "_percent_hist.png")
    elif mode == "cum_percent_hist":
        cumPlot = {}
        for i in range(numHumanSummaries+1):
            cumPlot[i] = (getCumulative(i, toPlot, numHumanSummaries) * 100)/videoDuration
        print("Cumplot: ", cumPlot)
        bars = plt.bar(cumPlot.keys(), cumPlot.values(), 1.0, color='b')
        # xlocs = axs[2].xticks
        # xlabs = axs[2].xticklabels
        xlocs, xlabs = plt.xticks()
        xlocs=[i for i in cumPlot.keys()]
        xlabs=[i for i in cumPlot.keys()]
        plt.title('Cumulative histogram for ' + video_name)
        plt.xlabel('Number of human summaries')
        plt.ylabel('Percentage of 1 second segments')
        plt.xticks(xlocs, xlabs)
        for bar in bars:
            #yval = int(round(bar.get_height()))
            yval = round(bar.get_height(), 1)
            plt.text(bar.get_x(), yval + 0.01, yval)

        # fig.tight_layout(pad=3.0)

        # plt.savefig(video_name + "_distribution.png")

        plt.savefig(video_name + "_cum_hist.png")

top100 = sorted(hist, key=hist.get, reverse=True)[:100]
#print(top100)

if generateImages == "True" or generateImages == "true":
    if not os.path.exists(video_name + "/top100/"):
        os.makedirs(video_name + "/top100/")

toSave = OrderedDict()
rank = 1
for item in top100:
    toSave[item] = distribution[item]
    if generateImages == "True" or generateImages == "true":
        print(".", end='')
        start = int(round(item * opencvFps))
        end = int(round((item+1) * opencvFps)) - 1
        middle = int((start + end)/2)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, start)
        #print("About to read ", vidcap.isOpened())
        success, image = vidcap.read()
        #print("Read ", success)
        if success:
            #print("Writing top ", rank)
            cv2.imwrite((video_name + "/top100/%d_%d.jpg") % (rank, start), image)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, middle)
        success, image = vidcap.read()
        if success:
            #print("Writing top ", rank)
            cv2.imwrite((video_name + "/top100/%d_%d.jpg") % (rank, middle), image)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, end)
        success, image = vidcap.read()
        if success:
            #print("Writing top ", rank)
            cv2.imwrite((video_name + "/top100/%d_%d.jpg") % (rank, end), image)
        rank += 1
    
with open(video_name + '_top_matching_seconds.json', 'w') as fp:
    json.dump(toSave, fp)


bottom100 = sorted(hist, key=hist.get, reverse=False)[:100]
#print(top100)

if generateImages == "True" or generateImages == "true":
    if not os.path.exists(video_name + "/bottom100/"):
        os.makedirs(video_name + "/bottom100/")

toSave = OrderedDict()
rank = 1
for item in bottom100:
    toSave[item] = distribution[item]
    if generateImages == "True" or generateImages == "true":
        print(".", end='')
        start = int(round(item * opencvFps))
        end = int(round((item+1) * opencvFps)) - 1
        middle = int((start + end)/2)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, start)
        success, image = vidcap.read()
        if success:
            #print("Writing bottom ", rank)
            cv2.imwrite((video_name + "/bottom100/%d_%d.jpg") % (rank, start), image)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, middle)
        success, image = vidcap.read()
        if success:
            #print("Writing bottom ", rank)
            cv2.imwrite((video_name + "/bottom100/%d_%d.jpg") % (rank, middle), image)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, end)
        success, image = vidcap.read()
        if success:
            #print("Writing bottom ", rank)
            cv2.imwrite((video_name + "/bottom100/%d_%d.jpg") % (rank, end), image)
        rank += 1
    
with open(video_name + '_least_matching_seconds.json', 'w') as fp:
    json.dump(toSave, fp)


