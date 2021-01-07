import os
import sys
import json
import random
from collections import OrderedDict
import cv2

domainPath = sys.argv[1]
files = os.listdir(domainPath)
domain = sys.argv[2]

# soccer
soccer_budgets = [60, 90, 120, 150, 154, 180, 185, 193, 199, 200, 210, 211, 216, 225, 230, 231, 235, 236, 238, 240, 241, 244, 250, 251, 255, 258, 287, 293, 295, 305, 330, 345]
# friends
friends_budgets = [49, 53, 54, 60, 61, 68, 71, 73, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 90, 120, 150, 180]
# surveillance
surveillance_budgets = [60, 90, 92, 117, 118, 120, 130, 131, 132, 140, 150, 162, 173, 176, 180, 182, 184, 186, 188, 205, 212, 216, 217, 220, 224, 226, 228, 230, 248, 260]
# techtalk
techtalk_budgets = [46, 60, 61, 64, 70, 74, 78, 80, 90, 120, 150, 163, 166, 168, 169, 170, 174, 175, 178, 180, 182, 184, 187, 198, 199, 200, 201, 202, 206, 208]
# birthday
birthday_budgets = [60, 69, 71, 88, 89, 90, 93, 95, 99, 105, 112, 113, 114, 120, 126, 127, 128, 134, 136, 138, 140, 146, 147, 148, 150, 152, 153, 166, 180]
# wedding
wedding_budgets = [60, 90, 118, 120, 132, 141, 143, 144, 148, 150, 151, 153, 158, 161, 167, 171, 172, 173, 175, 177, 178, 179, 180, 181, 182, 188, 196, 199, 204]

budgets = [60, 90, 120, 150, 180]

videos = []
for file in files:
    if file.endswith('mp4') or file.endswith('avi'):
        video_name = file.split(".")[0]
        if video_name not in ['soccer_7', 'soccer_18', 'friends_1', 'friends_5', 'surveillance_6', 'surveillance_8', 'techtalk_1', 'techtalk_9', 'birthday_5', 'birthday_6', 'wedding_1', 'wedding_5']:
            videos.append(file)

snippet_size = 0
if(domain == "soccer"):
    snippet_size = 5
if(domain == "surveillance" or domain == "techtalk"):
    snippet_size = 2

for video in videos:
    print("Processing ", video)
    videoPath = os.path.join(domainPath, video)
    #if domain == "soccer":
    #    budgets = soccer_budgets
    #elif domain == "friends":
    #    budgets = friends_budgets
    #elif domain == "surveillance":
    #    budgets = surveillance_budgets
    #elif domain == "techtalk":
    #    budgets = techtalk_budgets
    #elif domain == "birthday":
    #    budgets = birthday_budgets
    #elif domain == "wedding":
    #    budgets = wedding_budgets
    #else:
    #    print("Invalid domain")
    #    sys.exit(0)

    temp = os.path.join(domainPath, video.split(".")[0] + ".json")
    if(not os.path.exists(temp)):
        print("Corresponding json doesn't exist...ignoring")
        continue
    with open(temp) as json_file:
        ann_file = json.load(json_file, object_pairs_hook=OrderedDict)

    vidcap = cv2.VideoCapture(videoPath)
    fps = int(round(vidcap.get(cv2.CAP_PROP_FPS)))
    
    num_snippets = ann_file['num_snippets']
    frame_count = 0
    # Calculate frame_count for other domains
    if(not(domain == "soccer" or domain == "surveillance" or domain == "techtalk")):
        for k in range(1, num_snippets + 1):
            frame_count += ann_file[str(k)]['shot_length']
    else:
        frame_count = num_snippets * snippet_size * fps
        opencv_frame_count = ann_file["num_frames"]
        if opencv_frame_count > frame_count:
            frame_count = opencv_frame_count

    for budgetSeconds in budgets:
        budget = budgetSeconds * fps
        for j in range(100):
            summary = {}
            summary_frame = [0] * frame_count
            num_snips = 0
            if(domain == "soccer" or domain == "surveillance" or domain == "techtalk"):
                needed_num_snips = int(budget / (snippet_size * fps))
                actual_num_snips = 0
                while(actual_num_snips < needed_num_snips):
                    attempts = 0
                    while(True):
                        random_snip = random.randint(1, num_snippets)
                        if str(random_snip) in summary:
                            # this has already been picked up, try again
                            attempts += 1
                            if attempts == 100:
                                print(
                                    "Something wrong: Not able to pick up a different random snippet")
                                sys.exit()
                        else:
                            break
                    summary[str(random_snip)] = {}
                    begin_frame = (random_snip - 1) * (snippet_size * fps)
                    #if begin_frame > opencv_frame_count - 1:
                        #print("Start of snippet ", random_snip, " is beyond end of video!!")
                        #sys.exit()
                    end_frame = begin_frame + (snippet_size * fps)
                    #if end_frame > opencv_frame_count:
                        #if random_snip != num_snippets:
                            #print("End of intermediate snippet beyond the video!!", random_snip)
                            #sys.exit()
                        #else:
                            #pass
                            #end_frame = opencv_frame_count
                    summary_frame[begin_frame: end_frame] = [
                        1] * (end_frame - begin_frame)
                    actual_num_snips += 1
            else:
                currentSize = 0
                attempts = 0
                num_snips = 0
                while(True):
                    attemptsRepeatCheck = 0
                    while(True):
                        random_snip = random.randint(1, num_snippets)
                        if str(random_snip) in summary:
                            # this has already been picked up, try again
                            attemptsRepeatCheck += 1
                            if attemptsRepeatCheck == 100:
                                print(
                                    "Something wrong: Not able to pick up a different random snippet")
                                sys.exit()
                        else:
                            break
                    if(ann_file[str(random_snip)]['shot_length'] + currentSize <= budget):
                        currentSize += ann_file[str(random_snip)
                                                ]['shot_length']
                        num_snips += 1
                        summary[str(random_snip)] = {}
                        begin_frame = ann_file[str(random_snip)]['shot_start']
                        # additional -1 is due to the same issue as
                        # in tool.py, summaryViewer.py and summarySnippetsToVideoGenerator.py
                        end_frame = begin_frame + \
                            ann_file[str(random_snip)]['shot_length'] - 1
                        summary_frame[begin_frame: end_frame] = [
                            1] * (end_frame - begin_frame)
                    else:
                        attempts += 1
                        if(attempts > 100):
                            #print("Not able to pick any more snippet which fits in budget")
                            break
            if frame_count != len(summary_frame):
                print("Mismatch in frame_count and summary vector size!!!!")
                sys.exit()

            #print("Expected summary duration: ", budgetSeconds)
            #print("Actual summary duration: ", sum(summary_frame)/fps)
            summary["summary"] = summary_frame
            summary["summary_num_frames"] = sum(summary_frame)
            summary["video_name"] = video
            summary["num_snippets"] = num_snippets
            summary["summary_num_snippets"] = num_snips
            summary["video_category"] = domain
            summary["snippet_size"] = snippet_size
            summary["video_fps"] = fps
            summary["mode"] = "random"
            summary["video_num_frames"] = frame_count
            summary["budget_seconds"] = int(budget / fps)

            budgetPath = os.path.join(
                domainPath, str(int(budget / fps)))
            if(not(os.path.exists(budgetPath))):
                os.mkdir(budgetPath)
                os.mkdir(os.path.join(budgetPath, "random"))
            if(not(os.path.exists(os.path.join(budgetPath, "random")))):
                os.mkdir(os.path.join(budgetPath, "random"))
            if(not(os.path.exists(os.path.join(budgetPath + "/random", video.split(".")[0])))):
                os.mkdir(os.path.join(budgetPath +
                                      "/random", video.split(".")[0]))
            save_path = os.path.join(budgetPath + "/random/" + video.split(".")[0], video.split(
                ".")[0] + "_" + str(int(budget / fps)) + "_" + str(j) + ".json")
            with open(save_path, 'w') as fp:
                json.dump(summary, fp)
