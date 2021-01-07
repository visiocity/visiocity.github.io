#include <cmath>
#include <fstream>   // std::ifstream
#include <iostream>  // std::cout
#include <nlohmann/json.hpp>
#include "DiversityClustered.h"
#include "ImportanceRating.h"
#include "MegaEventContinuity.h"
#include "DisparitySum.h"
#include "arguments.h"
#include "set.h"
#include <regex>
#include <dirent.h>

char *keywordJSONFile;
char *annotatedJSONFile;
char *summaryJSONFile;
char *humanSummariesPath_c;
char *domain_c;
bool verbose;
char *help;
bool withoutF1 = false;

Arg Arg::Args[] = {
    Arg("withoutF1", Arg::Opt, withoutF1,
        "Set to False if you do not want F1 values to be computed", Arg::SINGLE),
    Arg("summaryJsonOfAVideo", Arg::Req, summaryJSONFile,
        "JSON file containing summary of a video", Arg::SINGLE),
    Arg("pathToAllHumanSummariesOfThisVideo", Arg::Opt, humanSummariesPath_c,
        "Folder containing all human summaries of this video", Arg::SINGLE),
    Arg("keywordJSONFile", Arg::Req, keywordJSONFile,
        "JSON file containing keywords and ratings", Arg::SINGLE),
    Arg("annotatedJSONFile", Arg::Req, annotatedJSONFile,
        "JSON file containing the annotation", Arg::SINGLE),
    Arg("domain", Arg::Req, domain_c,
        "Domain of this video", Arg::SINGLE),
    Arg("verbose", Arg::Req, verbose, "Verbose mode", Arg::SINGLE),
    Arg("help", Arg::Help, help, "Print this message"),
    Arg()};

std::vector<std::string> intersection (std::vector<std::string> &v1,
                                      std::vector<std::string> &v2) {
    std::vector<std::string> v3;

    std::sort(v1.begin(), v1.end());
    std::sort(v2.begin(), v2.end());

    std::set_intersection(v1.begin(), v1.end(), v2.begin(), v2.end(),
                          back_inserter(v3));
    return v3;
}

std::vector<std::string> unions(std::vector<std::string> &v1,
                                std::vector<std::string> &v2) {
    std::vector<std::string> v3;

    std::sort(v1.begin(), v1.end());
    std::sort(v2.begin(), v2.end());

    std::set_union(v1.begin(), v1.end(), v2.begin(), v2.end(),
                          back_inserter(v3));
    return v3;
}

std::string ltrim(const std::string& s) {
	return std::regex_replace(s, std::regex("^[\\s+\"\']"), std::string(""));
}

std::string rtrim(const std::string& s) {
	return std::regex_replace(s, std::regex("[\\s+\"\']$"), std::string(""));
}

std::string trim(const std::string& s) {
	return ltrim(rtrim(s));
}

std::string strToLower(std::string data) {
    std::transform(data.begin(), data.end(), data.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return data;
}

double ratingMapping(std::vector<std::string> SetofKeywords,
                     std::map<std::string, int> &ratingMap) {
    double maxRating = 0;
    for (int i = 0; i < SetofKeywords.size(); i++) {
        if (ratingMap[SetofKeywords[i]] == 0) {
            return 0;
        } else {
            if (ratingMap[SetofKeywords[i]] >= maxRating)
                maxRating = ratingMap[SetofKeywords[i]];
        }
    }
    return maxRating;
}

int main(int argc, char **argv) {
    bool parse_was_ok = Arg::parse(argc, (char **)argv);
    if (!parse_was_ok) {
        Arg::usage();
        exit(-1);
    }

    std::string domain;
    domain += domain_c;

    std::string humanSummariesPath;
    humanSummariesPath += humanSummariesPath_c;

    nlohmann::json summaryJSON;
    std::ifstream summaryJSONFileHandler;
    summaryJSONFileHandler.open(summaryJSONFile);
    summaryJSONFileHandler >> summaryJSON;

    if(verbose) {
        std::cout << "Summary loaded" << std::endl;
    }

    float maxf1 = 999999;
    float avgf1 = 999999;

    nlohmann::json annotatedJSON;
    std::ifstream annotatedJSONFileHandler;
    annotatedJSONFileHandler.open(annotatedJSONFile);
    annotatedJSONFileHandler >> annotatedJSON;
    
    //represent this summary as frames vector
    std::vector<int> summaryFrames = summaryJSON["summary"];
    
    if(!withoutF1) {
        //calculate F1
        if(verbose) std::cout << "Computing F1 ..." << std::endl;

        float summaryNumFrames = summaryJSON["summary_num_frames"];

        if (summaryNumFrames == 0) {
            if(verbose) {
                std::cout << "Summary is empty!" << std::endl;
            }
            std::cout << "0 0 0 0 0 0 0 0" << std::endl;
            return 0;
        }
        std::vector<float> f1Scores;
        DIR* dirFile;
        dirFile = opendir(humanSummariesPath_c);
        float f1 = -1;
        if (dirFile) {
            struct dirent* hFile;
            errno = 0;
            while (( hFile = readdir( dirFile )) != NULL ) {
                if ( !strcmp( hFile->d_name, "."  )) continue;
                if ( !strcmp( hFile->d_name, ".." )) continue;
                if (( hFile->d_name[0] == '.' )) continue;
                std::string name(hFile->d_name);
                std::string summaryFile(summaryJSONFile);
                //std::cout << "Summary file: " << summaryFile << std::endl;
                //std::cout << "Only name: " << summaryFile.substr(summaryFile.find_last_of("/\\") + 1) << std::endl;
                if(name == (summaryFile.substr(summaryFile.find_last_of("/\\") + 1))) {
                    if(verbose) {
                        std::cout << "Ignoring " << name << " as it is myself only" << std::endl;
                    }
                    continue;
                }
                if (verbose) std::cout << "Computing F1 with " << name << std::endl;
                nlohmann::json currJson;
                std::ifstream currJsonFile;
                currJsonFile.open(humanSummariesPath + "/" + name);
                if(currJsonFile.fail()) {
                    std::cout<<"Error opening file: "<< humanSummariesPath + "/" + name << std::endl;
                    exit(0);
                }
                currJsonFile >> currJson;
                std::vector<int> refSummaryFrames = currJson["summary"];
                float refSummaryNumFrames = currJson["summary_num_frames"];

                if(refSummaryFrames.size() != summaryFrames.size()) {
                    std::cout << "Mismatch in size of summary frame vectors between this summary " << summaryFrames.size() << " and " << name << refSummaryFrames.size() << std::endl;
                    return 0;
                }

                //compute precision and recall
                float numMatches = 0;
                float precision = 0;
                float recall = 0;
                for (int i=0; i<refSummaryFrames.size(); i++) {
                    if (refSummaryFrames[i] == 1 && summaryFrames[i] == 1) numMatches++;
                }
                precision = numMatches/summaryNumFrames;
                recall = numMatches/refSummaryNumFrames;
                if ((precision + recall) == 0) {
                    f1 = 0;
                } else {
                    f1 = 2 * (precision * recall) / (precision + recall);
                }
                //store in a vector
                f1Scores.push_back(f1);
                //if (verbose) std::cout << f1 << std::endl;
            }
            //report max f1 and avg f1
            if (verbose) std::cout << "Number of reference summaries = " << f1Scores.size() << std::endl;;
            maxf1 = *max_element(f1Scores.begin(), f1Scores.end());
            avgf1 = std::accumulate(std::begin(f1Scores), std::end(f1Scores), 0.0) / f1Scores.size();
            if (verbose) {
                std::cout << "Max F1 Score = " << maxf1 << std::endl;
                std::cout << "Mean F1 Score = " << avgf1 << std::endl;
            }
        } else {
            std::cout << "Error: provide a path to the folder containing all Human GTSummaries" << std::endl;
        }
    }

    float importanceScore = 999999;
    float megaEventContinuityScore = 999999;
    float diversityTimeScore = 999999;
    float diversitySceneScore = 999999;
    float diversityConceptScore = 999999;
    float diversitySimScore = 999999;

    std::string unit_s;

    if (domain == "friends" || domain == "birthday" || domain == "wedding") {
        unit_s = "shot";
    } else if (domain == "techtalk" || domain == "soccer" || domain == "surveillance") {
        unit_s = "snippet";
    } else {
        std::cout << "Invalid domain" << std::endl;
        return 0;
    }

    //adapted from http://xpo6.com/list-of-english-stop-words/
    std::vector<std::string> stopWords = {"&", "a","am","an","and","are","as","at","be","by","for","had","has", "hasnt", "have", "he", "ie", "if", "in", "into", "is", "it", "its", "of", "off","on","or","re", "that", "the", "to", "was"};

    nlohmann::json keywordJSON;
    std::ifstream keywordJSONFileHandler;
    keywordJSONFileHandler.open(keywordJSONFile);
    keywordJSONFileHandler >> keywordJSON;

    int num_snippets;
    int snippetSize = annotatedJSON["snippet_size"];
    num_snippets = annotatedJSON["num_snippets"];
    int fps;
    fps = annotatedJSON["fps"];  // fps is stored there from opencv and rounded

    // create ratings map of keywords
    std::map<std::string, int> ratingMap = std::map<std::string, int>();
    std::map<std::string, int> ratingMapME = std::map<std::string, int>();
    for (auto it = keywordJSON["categories"].begin();
         it != keywordJSON["categories"].end(); ++it) {
        std::vector<std::string> arrayKw = it.value()["keywords"];
        std::vector<int> arrayRatings = it.value()["ratings"];
        if (arrayKw.size() != arrayRatings.size()) {
            std::cout
                << "ERROR:Mismatch in number of keywords and number of ratings"
                << std::endl;
            return 0;
        }

        if (verbose) {
            std::cout << it.key() << std::endl;
            for (auto i : arrayKw) std::cout << i << ' ';
            std::cout << "\n" << std::endl;
            for (auto i : arrayRatings) std::cout << i << ' ';
            std::cout << "\n" << std::endl;
        }

        for (int i = 0; i < arrayKw.size(); i++) {
            ratingMap[strToLower(arrayKw[i])] = arrayRatings[i];
        }
    }
    ratingMap["transition"] = 0;
    if(verbose) std::cout << "Map of keywords to ratings created!" << '\n';

    //std::vector<std::string> arrayKwME;
    //std::vector<int> arrayRatingsME;
    std::vector<std::string> arrayKwME = keywordJSON["mega_events"];
    std::vector<int> arrayRatingsME = keywordJSON["mega_events_ratings"];
    if(arrayRatingsME.size()!=0) {
        if (verbose) {
            std::cout << "Mega events:" << std::endl;
            for (auto i : arrayKwME) std::cout << i << ' ';
            std::cout << "\n" << std::endl;
            for (auto i : arrayRatingsME) std::cout << i << ' ';
            std::cout << "\n" << std::endl;
        }
        for (int i = 0; i < arrayKwME.size(); i++) {
            ratingMapME[strToLower(arrayKwME[i])] = arrayRatingsME[i];
        }
        if(verbose) std::cout << "Maps of mega events to ratings created!" << '\n';
    }

    int n = annotatedJSON["num_snippets"];
    std::vector<float> frameRatings;

    int currMegaEventId = 0;
    bool firstMegaEventEncountered = false;
    std::string currMegaEventName;
    Set megaEventTempSet = Set();
    std::vector<Set> megaEvents = std::vector<Set>();
    std::vector<float> ratingsM = std::vector<float>();

    std::vector<Set> timeClusters = std::vector<Set>();
    std::vector<Set> sceneClusters = std::vector<Set>();
    std::vector<Set> conceptClusters = std::vector<Set>();

    int numSceneClusters = 0;

    if (domain == "friends") {
        numSceneClusters = annotatedJSON["num_scenes"];
        for (int j = 0; j < numSceneClusters; j++) {
            Set tempSet = Set();
            sceneClusters.push_back(tempSet);
        }
    }

    std::map<std::string, int> conceptMap = std::map<std::string, int>();
    int newConceptId = 0;
    std::map<std::string, int>::iterator conceptIt;

    //iterate over each keyword of each category to initialize the conceptmap and clusters
    if(verbose) std::cout << "Initializing conceptMap ..." << std::endl;
    for (auto it = keywordJSON["categories"].begin(); it != keywordJSON["categories"].end(); ++it) {
        for(auto elem: it.value()["keywords"]) {
            conceptMap[strToLower(elem)] = newConceptId;
            if(verbose) std::cout << "Keyword: " << elem << " and Id: " << newConceptId << std::endl;
            newConceptId++;
            Set tempSet = Set();
            conceptClusters.push_back(tempSet);
        }
    }

    // Start of the Annotation For Loop
    std::vector<std::string> prevSetOfKeywords;
    std::vector<std::vector<float>> kernel(n, std::vector<float> (n, 10));
    std::vector<std::vector<std::string>> setOfAllKeywords;
    for (int i = 0; i < n; i++) {
      kernel[i][i] = 1.0;
    }

    std::vector<int> framesToShots(summaryFrames.size(), -1);
    for (int i = 1; i <= n; i++) {
        if (verbose) std::cout << "Processing snippet: " << i << std::endl;
        if(unit_s == "shot") {
            int start = annotatedJSON[std::to_string(i)]["shot_start"];
            int length = annotatedJSON[std::to_string(i)]["shot_length"];
            for (int k = start; k < start + length; k++) {
                framesToShots[k] = i-1;
            }
        } else {
            int start = (i-1)*snippetSize*fps;
            int length = snippetSize*fps;
            for (int k = start; k < start + length; k++) {
                framesToShots[k] = i-1;
            }
        }
        std::vector<std::string> setOfKeywords = std::vector<std::string>();
        if (unit_s == "shot") {
            int shot_length =
                annotatedJSON[std::to_string(i)]["shot_length"];
        } else {
            //shotSnippetSizes.push_back(snippetSize * fps);
        }
        if ((annotatedJSON[std::to_string(i)].find("transition") !=
                annotatedJSON[std::to_string(i)].end()) &&
            (annotatedJSON[std::to_string(i)]["transition"] == true)) {
            if (verbose)
                std::cout << "This is a transition snippet" << std::endl;
            setOfKeywords.push_back("transition");
        } else {
            for (auto it =
                        annotatedJSON[std::to_string(i)]["categories"].begin();
                    it != annotatedJSON[std::to_string(i)]["categories"].end();
                    ++it) {
                std::vector<std::string> currVec = it.value();
                for (std::string key : currVec) {
                    setOfKeywords.push_back(strToLower(key));
                }
            }
        }
        setOfAllKeywords.push_back(setOfKeywords);
        if (verbose) {
            std::cout << "Snippet: " << i << " Keywords setKeywords set: { ";
            for (auto elem : setOfKeywords) {
                std::cout << elem << ", ";
            }
            std::cout << " } and rating: "
                        << ratingMapping(setOfKeywords, ratingMap)
                        << std::endl;
        }
        if (annotatedJSON[std::to_string(i)].find("mega_event") !=
            annotatedJSON[std::to_string(i)].end()) {
            if (verbose)
                std::cout
                    << "It's a mega event with ID: "
                    << annotatedJSON[std::to_string(i)]["mega_event"]["id"]
                    << " and NAME: "
                    << annotatedJSON[std::to_string(i)]["mega_event"]
                                    ["name"]
                    << std::endl;
            if (!firstMegaEventEncountered) {
                currMegaEventId =
                    annotatedJSON[std::to_string(i)]["mega_event"]["id"];
                currMegaEventName =
                    annotatedJSON[std::to_string(i)]["mega_event"]["name"];
                currMegaEventName = strToLower(currMegaEventName);
                firstMegaEventEncountered = true;
                if (verbose)
                    std::cout << "First mega event encountered, "
                                    "initialized currMegaEventId as "
                                << currMegaEventId
                                << " and currMegaEventName as "
                                << currMegaEventName << std::endl;
            }
            if (annotatedJSON[std::to_string(i)]["mega_event"]["id"] ==
                currMegaEventId) {
                if (verbose)
                    std::cout
                        << "Part of a running mega event, adding all corresponding frames to the set"
                        << std::endl;
                if(unit_s == "shot") {
                    int start = annotatedJSON[std::to_string(i)]["shot_start"];
                    int length = annotatedJSON[std::to_string(i)]["shot_length"];
                    for (int k = start; k < start + length - 1; k++) {
                        megaEventTempSet.insert(k);
                    }
                } else {
                    int start = (i-1)*snippetSize*fps;
                    int length = snippetSize*fps;
                    for (int k = start; k < start + length; k++) {
                        megaEventTempSet.insert(k);
                    }
                }
                currMegaEventName =
                    annotatedJSON[std::to_string(i)]["mega_event"]["name"];
                currMegaEventName = strToLower(currMegaEventName);

                } else {
                megaEvents.push_back(megaEventTempSet);
                ratingsM.push_back(ratingMapME[currMegaEventName]);
                megaEventTempSet.clear();
                if(unit_s == "shot") {
                    int start = annotatedJSON[std::to_string(i)]["shot_start"];
                    int length = annotatedJSON[std::to_string(i)]["shot_length"];
                    for (int k = start; k < start + length - 1; k++) {
                        megaEventTempSet.insert(k);
                    }
                } else {
                    int start = (i-1)*snippetSize*fps;
                    int length = snippetSize*fps;
                    for (int k = start; k < start + length; k++) {
                        megaEventTempSet.insert(k);
                    }
                }
                currMegaEventId =
                    annotatedJSON[std::to_string(i)]["mega_event"]["id"];
                currMegaEventName =
                    annotatedJSON[std::to_string(i)]["mega_event"]["name"];
                currMegaEventName = strToLower(currMegaEventName);
            }
            if(unit_s == "shot") {
                int start = annotatedJSON[std::to_string(i)]["shot_start"];
                int length = annotatedJSON[std::to_string(i)]["shot_length"];
                if (verbose) std::cout << "Pushing for " << start << " to " << start+length-1 << std::endl;
                for (int k = start; k < start + length; k++) {
                    frameRatings.push_back(-ratingMapping(setOfKeywords, ratingMap));
                }
            } else {
                int start = (i-1)*snippetSize*fps;
                int length = snippetSize*fps;
                if (verbose) std::cout << "Pushing for " << start << " to " << start+length-1 << std::endl;
                for (int k = start; k < start + length; k++) {
                    frameRatings.push_back(-ratingMapping(setOfKeywords, ratingMap));
                }
            }
        } else {
            if(unit_s == "shot") {
                int start = annotatedJSON[std::to_string(i)]["shot_start"];
                int length = annotatedJSON[std::to_string(i)]["shot_length"];
                if (verbose) std::cout << "Pushing for " << start << " to " << start+length-1 << std::endl;
                for (int k = start; k < start + length; k++) {
                    frameRatings.push_back(ratingMapping(setOfKeywords, ratingMap));
                }
            } else {
                int start = (i-1)*snippetSize*fps;
                int length = snippetSize*fps;
                if (verbose) std::cout << "Pushing for " << start << " to " << start+length-1 << std::endl;
                for (int k = start; k < start + length; k++) {
                    frameRatings.push_back(ratingMapping(setOfKeywords, ratingMap));
                }
            }
        }

        if(domain == "friends") {
            // prepare clusters according to scene information in
            // annotatedJson refer to how it is being done in
            // FriendsScoring.cc - line 131-137 and 199-207
            if (annotatedJSON[std::to_string(i)].find("sceneId") !=
                annotatedJSON[std::to_string(i)].end()) {
                    if(unit_s == "shot") {
                        int start = annotatedJSON[std::to_string(i)]["shot_start"];
                        int length = annotatedJSON[std::to_string(i)]["shot_length"];
                        for (int k = start; k < start + length - 1; k++) {
                            sceneClusters[annotatedJSON[std::to_string(i)]["sceneId"]].insert(k);
                        }
                    } else {
                        int start = (i-1)*snippetSize*fps;
                        int length = snippetSize*fps;
                        for (int k = start; k < start + length; k++) {
                            sceneClusters[annotatedJSON[std::to_string(i)]["sceneId"]].insert(k);
                        }
                    }
            } else {
                std::cout << "WARNING: Scene information not present "
                                "in snippet "
                            << i << std::endl;
                std::cout << "ERROR: DiversityClusteredScene can't proceed"
                            << std::endl;
                return 0;
            }
        }
        //prepare timeClusters
        if (i == 1) {
            Set tempSet = Set();
            timeClusters.push_back(tempSet);
            if(unit_s == "shot") {
                int start = annotatedJSON[std::to_string(i)]["shot_start"];
                int length = annotatedJSON[std::to_string(i)]["shot_length"];
                for (int k = start; k < start + length - 1; k++) {
                    timeClusters[0].insert(k);
                }
            } else {
                int start = (i-1)*snippetSize*fps;
                int length = snippetSize*fps;
                for (int k = start; k < start + length; k++) {
                    timeClusters[0].insert(k);
                }
            }
            prevSetOfKeywords = setOfKeywords;
        } else {
            if (prevSetOfKeywords == setOfKeywords) {
                if(unit_s == "shot") {
                    int start = annotatedJSON[std::to_string(i)]["shot_start"];
                    int length = annotatedJSON[std::to_string(i)]["shot_length"];
                    for (int k = start; k < start + length - 1; k++) {
                        timeClusters[timeClusters.size() - 1].insert(k);
                    }
                } else {
                    int start = (i-1)*snippetSize*fps;
                    int length = snippetSize*fps;
                    for (int k = start; k < start + length; k++) {
                        timeClusters[timeClusters.size() - 1].insert(k);
                    }
                }
            } else {
                Set tempSet = Set();
                timeClusters.push_back(tempSet);
                if(unit_s == "shot") {
                    int start = annotatedJSON[std::to_string(i)]["shot_start"];
                    int length = annotatedJSON[std::to_string(i)]["shot_length"];
                    for (int k = start; k < start + length - 1; k++) {
                        timeClusters[timeClusters.size() - 1].insert(k);
                    }
                } else {
                    int start = (i-1)*snippetSize*fps;
                    int length = snippetSize*fps;
                    for (int k = start; k < start + length; k++) {
                        timeClusters[timeClusters.size() - 1].insert(k);
                    }
                }
            }
            prevSetOfKeywords = setOfKeywords;
        }

        //concept clusters

        //if this is transition snippet, do nothing, continue to next snippet
        if (annotatedJSON[std::to_string(i)].find("transition") != annotatedJSON[std::to_string(i)].end() && annotatedJSON[std::to_string(i)]["transition"]==true) {
            if(verbose) std::cout << "Transition snippet, ignoring" << std::endl;
            continue;
        }

        //identify the concepts present in this snippet
        //caption
        std::string caption;
        if (annotatedJSON[std::to_string(i)].find("caption") != annotatedJSON[std::to_string(i)].end()) {
            caption = annotatedJSON[std::to_string(i)]["caption"];
            caption = trim(caption);
            caption = strToLower(caption);
            if(verbose) std::cout << "Caption: " << caption << std::endl;
            char *pch;
            pch = strtok (const_cast<char*>(caption.c_str())," ,.-\n:_()");
            while (pch != NULL) {
                //do whatever you want with this word
                std::string word(pch);
                //word = strToLower(word);
                if(verbose) std::cout << "Word: " << word << std::endl;
                if (std::find(stopWords.begin(), stopWords.end(), word) != stopWords.end()) {
                    //ignore this word
                    if(verbose) std::cout << "Ignoring" << std::endl;
                } else {
                    conceptIt = conceptMap.find(word);
                    if (conceptIt == conceptMap.end()) {
                        //it is a new concept, add
                        if(verbose) std::cout << "New" << std::endl;
                        conceptMap[word] = newConceptId;
                        if(verbose) std::cout << "Adding to cluster id " << newConceptId << " and name " << word << std::endl;
                        newConceptId++;
                        Set tempSet = Set();
                        //tempSet.insert(i-1);
                        if(unit_s == "shot") {
                            int start = annotatedJSON[std::to_string(i)]["shot_start"];
                            int length = annotatedJSON[std::to_string(i)]["shot_length"];
                            for (int k = start; k < start + length - 1; k++) {
                                tempSet.insert(k);
                            }
                        } else {
                            int start = (i-1)*snippetSize*fps;
                            int length = snippetSize*fps;
                            for (int k = start; k < start + length; k++) {
                                tempSet.insert(k);
                            }
                        }
                        conceptClusters.push_back(tempSet);
                    } else {
                        //it is already encountered
                        if(verbose) std::cout << "Old" << std::endl;
                        //conceptClusters[conceptMap[word]].insert(i-1);
                        if(unit_s == "shot") {
                            int start = annotatedJSON[std::to_string(i)]["shot_start"];
                            int length = annotatedJSON[std::to_string(i)]["shot_length"];
                            for (int k = start; k < start + length - 1; k++) {
                                conceptClusters[conceptMap[word]].insert(k);
                            }
                        } else {
                            int start = (i-1)*snippetSize*fps;
                            int length = snippetSize*fps;
                            for (int k = start; k < start + length; k++) {
                                conceptClusters[conceptMap[word]].insert(k);
                            }
                        }
                        if (verbose) std::cout << "Adding corresponding frames to cluster id " << conceptMap[word] << " and name " << word << std::endl;
                    }
                }
                pch = strtok (NULL, " ,.-\n:_()");
            }
        }
        //iterate over each keyword of each category of this snippet and do the same
        if (annotatedJSON[std::to_string(i)].find("categories") != annotatedJSON[std::to_string(i)].end()) {
            for (auto it = annotatedJSON[std::to_string(i)]["categories"].begin(); it != annotatedJSON[std::to_string(i)]["categories"].end(); ++it) {
                for(auto elem: it.value()) {
                    if(verbose) std::cout << "Keyword of this snippet: " << elem << std::endl;
                    //conceptClusters[conceptMap[elem]].insert(i-1);
                    if(unit_s == "shot") {
                        int start = annotatedJSON[std::to_string(i)]["shot_start"];
                        int length = annotatedJSON[std::to_string(i)]["shot_length"];
                        for (int k = start; k < start + length - 1; k++) {
                            conceptClusters[conceptMap[strToLower(elem)]].insert(k);
                        }
                    } else {
                        int start = (i-1)*snippetSize*fps;
                        int length = snippetSize*fps;
                        for (int k = start; k < start + length; k++) {
                            conceptClusters[conceptMap[strToLower(elem)]].insert(k);
                        }
                    }
                    if (verbose) std::cout << "Adding corresponding frames to cluster id " << conceptMap[strToLower(elem)] << " and name " << elem << std::endl;
                }
            }
        }
    } //end of annotations

    if(unit_s == "shot" && summaryFrames.size() != frameRatings.size()) {
        std::cout << "Unit is shots, yet summaryFrames.size() " << summaryFrames.size() << " is not equal to frameRatings.size() " << frameRatings.size() << std::endl;
        return 0;
    }

    if(summaryFrames.size() > frameRatings.size()) {
        //possible because we have used max in case of snippets
        //treat the extra ones as rating 0
        int diff = summaryFrames.size() - frameRatings.size();
        for (int k = 0; k < diff; k++) {
                frameRatings.push_back(0);
        }
    } else if(summaryFrames.size() < frameRatings.size()) {
        std::cout << "How can summaryFrames.size() " << summaryFrames.size() << " be less than frameRatings.size() " << frameRatings.size() << std::endl;
        return 0;
    }

    if(verbose) std::cout << "Computing kernel for div-sim ..." << std::endl;
    //Compute Kernel matrix
    std::vector<std::string> commonKeywords;
    std::vector<std::string> allKeywords;
    float num, denom;
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if(kernel[i][j] == 10){
          num = 0.0;
          denom = 0.0;
          commonKeywords = intersection(setOfAllKeywords[i], setOfAllKeywords[j]);
          allKeywords = unions(setOfAllKeywords[i], setOfAllKeywords[j]);
          for (int l = 0; l < commonKeywords.size(); l++) {
            num += (ratingMap[commonKeywords[l]]+1);
          }
          for (int l = 0; l < allKeywords.size(); l++) {
            denom += (ratingMap[allKeywords[l]]+1);
          }
        //   if(denom == 0.0){
        //     kernelm[i][j] = 0.0;
        //     kernelm[j][i] = 0.0;
        //   }
          kernel[i][j] = num/denom;
          kernel[j][i] = num/denom;
        }
      }
    }

    if(verbose) {
        std::cout << "Concept map:" << std::endl;
        for (std::pair<std::string, int> element : conceptMap) {
            std::string word = element.first;
            int index = element.second;
            std::cout << word << " :: " << index << std::endl;
        }
    }

    if (megaEventTempSet.size() > 0) {
        megaEvents.push_back(megaEventTempSet);
        ratingsM.push_back(ratingMapME[currMegaEventName]);
    }

    if(verbose) std::cout << "Preparing scoring terms for evaluation" << std::endl;

    MegaEventContinuity *m = NULL;
    ImportanceRating *ir = NULL;
    DiversityClustered *dcTime = NULL;
    DiversityClustered *dcScene = NULL;
    DiversityClustered *dcConcept = NULL;
    DisparitySum *dsum = NULL;

    if(verbose) std::cout << "Creating summarySet for evals ..." << std::endl;
    Set summarySet;
    int tempId;
    for (int i = 0; i < summaryFrames.size(); i++) {
        if (summaryFrames[i] == 1) {
            summarySet.insert(i);
        }
    }

    // if megaEventContinuity, instantiate it (needs n, megaEvents and their
    // ratings)
    if(verbose) std::cout << "Computing MegaEventContinuity ..." << std::endl;
    if(domain != "techtalk") {
        m = new MegaEventContinuity("MegaEventContinuity", summaryFrames.size(), ratingsM,
                                megaEvents, verbose);
        megaEventContinuityScore = m->eval(summarySet);
        if(verbose) std::cout << "MegaEventContinuityScore = " << megaEventContinuityScore << std::endl;
    }
    // operates on all snippets based on their ratings
    if(verbose) std::cout << "Computing ImportanceRating ..." << std::endl;
    ir = new ImportanceRating("ImportanceRatingInclusive", summaryFrames.size(),
                                frameRatings, false, verbose);
    importanceScore = ir->eval(summarySet);
    if(verbose) std::cout << "ImportanceRatingScore = " << importanceScore << std::endl;

    // if diversityClustered instantiate it appropriately (needs n, clusters
    // and snippetRatings)

    if(verbose) std::cout << "Computing DiversityClusteredTime ..." << std::endl;
    dcTime = new DiversityClustered("DiversityClusteredTime", summaryFrames.size(), timeClusters,
                                frameRatings, verbose);
    diversityTimeScore = dcTime->eval(summarySet);
    if(verbose) std::cout << "DiversityTimeScore = " << diversityTimeScore << std::endl;

    if (domain == "friends") {
        if(verbose) std::cout << "Computing DiversityClusteredScene ..." << std::endl;
        dcScene = new DiversityClustered("DiversityClusteredScene", summaryFrames.size(), sceneClusters,
                                frameRatings, verbose);
        diversitySceneScore = dcScene->eval(summarySet);
        if(verbose) std::cout << "DiversitySceneScore = " << diversitySceneScore << std::endl;
    }
    if(verbose) std::cout << "Computing DiversityClusteredConcept ..." << std::endl;
    dcConcept = new DiversityClustered("DiversityClusteredConcept", summaryFrames.size(), conceptClusters,
                                frameRatings, verbose);
    diversityConceptScore = dcConcept->eval(summarySet);
    if(verbose) std::cout << "DiversityConceptScore = " << diversityConceptScore << std::endl;

    if(verbose) std::cout << "Computing DiversitySim ..." << std::endl;
    dsum = new DisparitySum("DiversitySim", n, kernel, framesToShots, verbose);
    diversitySimScore = dsum->evalFrames(summarySet);
    if(verbose) std::cout << "DiversitySimScore = " << diversitySimScore << std::endl;

    if(withoutF1) {
        std::cout << importanceScore << " " << megaEventContinuityScore << " " << diversityTimeScore << " " << diversitySceneScore << " " << diversityConceptScore << " " << diversitySimScore << std::endl;
    } else {
        std::cout << avgf1 << " " << maxf1 << " " << importanceScore << " " << megaEventContinuityScore << " " << diversityTimeScore << " " << diversitySceneScore << " " << diversityConceptScore << " " << diversitySimScore << std::endl;
    }
}
