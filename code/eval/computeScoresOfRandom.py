import os
import sys
import json
import commands

path = sys.argv[1]
domain = sys.argv[2]
exe_path = sys.argv[3]
#forceUpdate = sys.argv[4]
mode = sys.argv[4] #frame, snippet, both
stride = sys.argv[5]

# human_videos = []
soccer_human_videos = ['soccer_7', 'soccer_18']
friends_human_videos = ['friends_1', 'friends_5']
surveillance_human_videos = ['surveillance_6', 'surveillance_8']
techtalk_human_videos = ['techtalk_1', 'techtalk_9']
birthday_human_videos = ['birthday_5', 'birthday_6']
wedding_human_videos = ['wedding_1', 'wedding_5']

soccer_budgets = [154, 193, 199, 211, 216, 231, 236, 238, 241, 244, 251, 258, 287, 293, 330]

friends_budgets = [60, 68, 71, 77, 79, 80, 83, 84, 86]

surveillance_budgets = [90, 117, 131, 162, 173, 176, 186, 205, 212, 216, 217, 220]

techtalk_budgets = [46, 60, 61, 64, 163, 169, 170, 175, 178, 184, 187, 198, 199, 201, 202]

birthday_budgets = [69, 88, 95, 113, 114, 127, 128, 134, 140, 147, 148, 150]

wedding_budgets = [120, 143, 144, 151, 153, 158, 172, 173, 178, 179, 181, 188, 196, 204]


if domain == 'soccer':
    videos = soccer_human_videos
    budgets = soccer_budgets
elif domain == 'friends':
    videos = friends_human_videos
    budgets = friends_budgets
elif domain == 'surveillance':
    videos = surveillance_human_videos
    budgets = surveillance_budgets
elif domain == 'techtalk':
    videos = techtalk_human_videos
    budgets = techtalk_budgets
elif domain == 'birthday':
    videos = birthday_human_videos
    budgets = birthday_budgets
elif domain == 'wedding':
    videos = wedding_human_videos
    budgets = wdding_budgets
else:
    print("Invalid domain")
    sys.exit()


budgetFoldersPath = os.path.join(path, domain)
#budgets = os.listdir(budgetFoldersPath)
#budgets = [60, 90, 120, 150, 180]
for budget in budgets:
    #if unicode(budget, 'utf-8').isnumeric():
    randomPath = os.path.join(budgetFoldersPath, str(budget), "random")
    if(not os.path.exists(randomPath)):
        print("Path doesnt exist: ", randomPath)
        sys.exit()
    #videos = os.listdir(randomPath)
    for video in videos:
        #if (budget, video) in [("171", "wedding_1"), ("171", "wedding_5"), ("175", "wedding_1"), ("175", "wedding_5"), ("182", "wedding_1"), ("182", "wedding_5"), ("204", "wedding_1"), ("204", "wedding_5"), ("173", "wedding_1"), ("173", "wedding_5"), ("153", "wedding_1"), ("153", "wedding_5"), ("118", "wedding_1"), ("118", "wedding_5"), ("120", "wedding_1"), ("120", "wedding_5"), ("172", "wedding_1"), ("172", "wedding_5"), ("188", "wedding_1"), ("188", "wedding_5"), ("179", "wedding_1"), ("179", "wedding_5"), ("144", "wedding_1"), ("144", "wedding_5"), ("178", "wedding_1"), ("178", "wedding_5"), ("60", "wedding_1"), ("60", "wedding_5"), ("167", "wedding_1"), ("167", "wedding_5"), ("196", "wedding_1"), ("196", "wedding_5"), ("150", "wedding_1"), ("150", "wedding_5"), ("161", "wedding_1"), ("161", "wedding_5"), ("181", "wedding_1"), ("181", "wedding_5"), ("177", "wedding_1"), ("177", "wedding_5"), ("132", "wedding_1"), ("132", "wedding_5"), ("199", "wedding_1"), ("199", "wedding_5"), ("141", "wedding_1")]:
            #print("Already computed, skipping")
            #continue
        randomSummariesPath = os.path.join(randomPath, video)
        randomSummaries = os.listdir(randomSummariesPath)
        index = 0
        for randomSummary in randomSummaries:
            if index % int(stride) != 0:
                print("Skipping this due to stride")
                index += 1
                continue
            index += 1
            updated = False
            randomSummaryPath = os.path.join(randomSummariesPath, randomSummary)
            print("Processing: ", randomSummaryPath)
            with open(randomSummaryPath, "r") as f:
                randomSummaryJson = json.load(f)
            if mode == "frame" or mode == "both":
                if ("frame_scores" not in randomSummaryJson):
                    print("frame_scores not present!")
                    sys.exit(0)
                    frame_scores = {}
                    frameEvalCommand = os.path.join(exe_path, "GenerateFrameEvalNumbers") + "  -summaryJsonOfAVideo " + randomSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                        path, domain + "/allAutomaticGTSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
                    print("Random frame eval: ", frameEvalCommand)
                    result = commands.getoutput(frameEvalCommand)
                    print("Result[1-8]: ", result)
                    results = result.split(" ")
                    results = [float(i) for i in results]
                    frame_scores["avgf1auto"] = results[0]
                    frame_scores["maxf1auto"] = results[1]
                    frame_scores["imp"] = results[2]
                    if not(domain == "techtalk"):
                        frame_scores["mega-cont"] = results[3]
                    else:
                        frame_scores["mega-cont"] = 99999
                    frame_scores["div-time"] = results[4]
                    if domain == "friends":
                        frame_scores["div-scene"] = results[5]
                    else:
                        frame_scores["div-scene"] = 99999
                    frame_scores["div-concept"] = results[6]
                    frame_scores["div-sim"] = results[7]
                    
                    visContUniformEvalCommand = os.path.join(
                        exe_path, "GenerateVisContUniformNumbers") + " -summaryJsonOfAVideo " + randomSummaryPath + " -verbose false"
                    print("Random ContEval: ", visContUniformEvalCommand)
                    visContUniform = commands.getoutput(visContUniformEvalCommand)
                    print("Result[9-10]: ", visContUniform)
                    visContUniformVals = visContUniform.split(" ")
                    visContUniformVals = [float(i) for i in visContUniformVals]
                    frame_scores["norm-vis-cont"] = visContUniformVals[0]
                    frame_scores["norm-uniform"] = visContUniformVals[1]
                    
                    randomSummaryJson["frame_scores"] = frame_scores
                    updated = True
                else:
                    if "avgf1" not in randomSummaryJson["frame_scores"] or "norm-vis-cont" not in randomSummaryJson["frame_scores"]:
                        print("frame_scores exist but incomplete!!!")
                        sys.exit(0)
                    if "avgf1auto" in randomSummaryJson["frame_scores"]:
                        print("Already computed, skipping")
                        continue
                    frameEvalCommand = os.path.join(exe_path, "GenerateFrameEvalNumbers") + "  -summaryJsonOfAVideo " + randomSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                        path, domain + "/allAutomaticGTSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
                    print("Random frame eval: ", frameEvalCommand)
                    result = commands.getoutput(frameEvalCommand)
                    print("Result[1-8]: ", result)
                    results = result.split(" ")
                    results = [float(i) for i in results]
                    randomSummaryJson["frame_scores"]["avgf1auto"] = results[0]
                    randomSummaryJson["frame_scores"]["maxf1auto"] = results[1]
                    randomSummaryJson["frame_scores"]["imp"] = results[2]
                    if not(domain == "techtalk"):
                        randomSummaryJson["frame_scores"]["mega-cont"] = results[3]
                    else:
                        randomSummaryJson["frame_scores"]["mega-cont"] = 99999
                    randomSummaryJson["frame_scores"]["div-time"] = results[4]
                    if domain == "friends":
                        randomSummaryJson["frame_scores"]["div-scene"] = results[5]
                    else:
                        randomSummaryJson["frame_scores"]["div-scene"] = 99999
                    randomSummaryJson["frame_scores"]["div-concept"] = results[6]
                    randomSummaryJson["frame_scores"]["div-sim"] = results[7]
                    
                    visContUniformEvalCommand = os.path.join(
                        exe_path, "GenerateVisContUniformNumbers") + " -summaryJsonOfAVideo " + randomSummaryPath + " -verbose false"
                    print("Random ContEval: ", visContUniformEvalCommand)
                    visContUniform = commands.getoutput(visContUniformEvalCommand)
                    print("Result[9-10]: ", visContUniform)
                    visContUniformVals = visContUniform.split(" ")
                    visContUniformVals = [float(i) for i in visContUniformVals]
                    randomSummaryJson["frame_scores"]["norm-vis-cont"] = visContUniformVals[0]
                    randomSummaryJson["frame_scores"]["norm-uniform"] = visContUniformVals[1]
                    
                    updated = True
            
            if mode == "snippet" or mode == "both":
                if ("snippet_scores" not in randomSummaryJson):
                    snippet_scores = {}
                    snippetEvalCommand = os.path.join(exe_path, "GenerateAllEvalNumbers") + "  -summaryJsonOfAVideo " + randomSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                        path, domain + "/allAutomaticGTSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
                    print("Random snippet eval: ", snippetEvalCommand)
                    result = commands.getoutput(snippetEvalCommand)
                    print("Result[1-8]: ", result)
                    results = result.split(" ")
                    results = [float(i) for i in results]
                    snippet_scores["avgf1auto"] = results[0]
                    snippet_scores["maxf1auto"] = results[1]
                    snippet_scores["imp"] = results[2]
                    if not(domain == "techtalk"):
                        snippet_scores["mega-cont"] = results[3]
                    else:
                        snippet_scores["mega-cont"] = 99999
                    snippet_scores["div-time"] = results[4]
                    if domain == "friends":
                        snippet_scores["div-scene"] = results[5]
                    else:
                        snippet_scores["div-scene"] = 99999
                    snippet_scores["div-concept"] = results[6]
                    snippet_scores["div-sim"] = results[7]
                
                    randomSummaryJson["snippet_scores"] = snippet_scores
                    updated = True
                else:
                    print("###Snippet scores already exist for ", randomSummaryPath)
                    snippetEvalCommand = os.path.join(exe_path, "GenerateAllEvalNumbers") + "  -summaryJsonOfAVideo " + randomSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                        path, domain + "/allAutomaticGTSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
                    print("Random snippet eval: ", snippetEvalCommand)
                    result = commands.getoutput(snippetEvalCommand)
                    print("Result[1-8]: ", result)
                    results = result.split(" ")
                    results = [float(i) for i in results]
                    randomSummaryJson["snippet_scores"]["avgf1auto"] = results[0]
                    randomSummaryJson["snippet_scores"]["maxf1auto"] = results[1]
                    randomSummaryJson["snippet_scores"]["imp"] = results[2]
                    if not(domain == "techtalk"):
                        randomSummaryJson["snippet_scores"]["mega-cont"] = results[3]
                    else:
                        randomSummaryJson["snippet_scores"]["mega-cont"] = 99999
                    randomSummaryJson["snippet_scores"]["div-time"] = results[4]
                    if domain == "friends":
                        randomSummaryJson["snippet_scores"]["div-scene"] = results[5]
                    else:
                        randomSummaryJson["snippet_scores"]["div-scene"] = 99999
                    randomSummaryJson["snippet_scores"]["div-concept"] = results[6]
                    randomSummaryJson["snippet_scores"]["div-sim"] = results[7]
                    updated = True
            
            if updated:
                with open(randomSummaryPath, 'w') as outfile:
                    json.dump(randomSummaryJson, outfile)
                
