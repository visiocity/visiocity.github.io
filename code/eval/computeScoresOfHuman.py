import os
import sys
import json
import commands

path = sys.argv[1]
domain = sys.argv[2]
exe_path = sys.argv[3]
forceUpdate = sys.argv[4]
justCheck = sys.argv[5]

allHumanSummariesPath = os.path.join(path, domain, "allHumanSummaries")
video_dirs = os.listdir(allHumanSummariesPath)
for video in video_dirs:
    summariesPath = os.path.join(allHumanSummariesPath, video)
    summaries = os.listdir(summariesPath)
    for humanSummary in summaries:
        updated = False
        humanSummaryPath = os.path.join(summariesPath, humanSummary)
        print("Processing: ", humanSummaryPath)
        with open(humanSummaryPath, "r") as f:
            humanSummaryJson = json.load(f)
        if ("frame_scores" not in humanSummaryJson) or ("frame_scores" in humanSummaryJson and forceUpdate == 'True'):
            print("frame_scores not present")
            if justCheck == "True":
                sys.exit(0)
            print("Computing")
            frame_scores = {}
            frameEvalCommand = os.path.join(exe_path, "GenerateFrameEvalNumbers") + "  -summaryJsonOfAVideo " + humanSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                path, domain + "/allHumanSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
            print("Human frame eval: ", frameEvalCommand)
            result = commands.getoutput(frameEvalCommand)
            print("Result[1-8]: ", result)
            results = result.split(" ")
            results = [float(i) for i in results]
            frame_scores["avgf1"] = results[0]
            frame_scores["maxf1"] = results[1]
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
                exe_path, "GenerateVisContUniformNumbers") + " -summaryJsonOfAVideo " + humanSummaryPath + " -verbose false"
            print("Human ContEval: ", visContUniformEvalCommand)
            visContUniform = commands.getoutput(visContUniformEvalCommand)
            print("Result[9-10]: ", visContUniform)
            visContUniformVals = visContUniform.split(" ")
            visContUniformVals = [float(i) for i in visContUniformVals]
            frame_scores["norm-vis-cont"] = visContUniformVals[0]
            frame_scores["norm-uniform"] = visContUniformVals[1]
            
            humanSummaryJson["frame_scores"] = frame_scores
            updated = True
        else:
            if "avgf1" not in humanSummaryJson["frame_scores"] or "norm-vis-cont" not in humanSummaryJson["frame_scores"]:
                print("frame_scores exist but incomplete!!!")
                sys.exit(0)
        
        if ("snippet_scores" not in humanSummaryJson) or ("snippet_scores" in humanSummaryJson and forceUpdate == 'True'):
            print("snippet_scores not present")
            if justCheck == "True":
                sys.exit(0)
            print("Computing")
            snippet_scores = {}
            snippetEvalCommand = os.path.join(exe_path, "GenerateAllEvalNumbers") + "  -summaryJsonOfAVideo " + humanSummaryPath + "  -pathToAllHumanSummariesOfThisVideo " + os.path.join(
                path, domain + "/allHumanSummaries/" + video) + " -keywordJSONFile " + os.path.join(path, domain + "/" + domain + ".json") + " -annotatedJSONFile " + os.path.join(path, domain + "/" + video + ".json") + " -domain " + domain + " -verbose false"
            print("Human snippet eval: ", snippetEvalCommand)
            result = commands.getoutput(snippetEvalCommand)
            print("Result[1-8]: ", result)
            results = result.split(" ")
            results = [float(i) for i in results]
            snippet_scores["avgf1"] = results[0]
            snippet_scores["maxf1"] = results[1]
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

            visContUniformEvalCommand = os.path.join(
                exe_path, "GenerateVisContUniformNumbers") + " -summaryJsonOfAVideo " + humanSummaryPath + " -verbose false"
            print("human ContEval: ", visContUniformEvalCommand)
            visContUniform = commands.getoutput(visContUniformEvalCommand)
            print("Result[9-10]: ", visContUniform)
            visContUniformVals = visContUniform.split(" ")
            visContUniformVals = [float(i) for i in visContUniformVals]
            snippet_scores["norm-vis-cont"] = visContUniformVals[0]
            snippet_scores["norm-uniform"] = visContUniformVals[1]
            
            humanSummaryJson["snippet_scores"] = snippet_scores
            updated = True
            
        else:
            if "avgf1" not in humanSummaryJson["snippet_scores"] or "norm-vis-cont" not in humanSummaryJson["snippet_scores"]:
                print("snippet_scores exist but incomplete!!!")
                sys.exit(0)
        
        if updated:
            with open(humanSummaryPath, 'w') as outfile:
                json.dump(humanSummaryJson, outfile)
        
