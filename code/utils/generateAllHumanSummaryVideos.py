import os
import sys

dataPath = sys.argv[1]
exe_path = sys.argv[1]

domains = ["soccer", "friends", "surveillance", "techtalk" ,"birthday", "wedding"]

outDir = os.path.join(dataPath, "allHumanSummaryVideos")
if not os.path.exists(outDir):
    os.mkdir(outDir)

for domain in domains:
    print("Processing domain: ", domain)
    if domain == "friends":
        extension = "avi"
    else extension = "mp4"
    domainPath = os.path.join(dataPath, domain)
    humanSummariesPath = os.path.join(domainPath, "allHumanSummaries")
    videos = os.listdir(humanSummariesPath)
    for video in videos:
        print("Processing video: ", video)
        humanSummariesPathForVideo = os.path.join(humanSummariesPath, video)
        summaries = os.listdir(humanSummariesPathForVideo)
        for summary in summaries:
            print("Processing human summary: ", summary)
            summaryPath = os.path.join(humanSummariesPathForVideo, summary)
            command = "python " + exe_path + "/summaryFramesToVideoGenerator.py " + summaryPath + " " + os.path.join(domainPath, video + ".json") + " " + os.path.join(domainPath, domain+".json") + " " + os.path.join(domainPath, video + "." + extension) + " " + os.path.join(outDir, summary.split(".")[0]+"."+extension)
            print(command)
            os.system(command)