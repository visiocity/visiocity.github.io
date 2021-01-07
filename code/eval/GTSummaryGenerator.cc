
#include <cmath>
#include <fstream>   // std::ifstream
#include <iostream>  // std::cout
#include <nlohmann/json.hpp>
#include <random>
#include <set>
#include "CombinedScoringFunction.h"
#include "ConceptCoverage.h"
#include "DiversityClustered.h"
#include "ImportanceRating.h"
#include "MegaEventContinuity.h"
#include "DisparitySum.h"
#include "arguments.h"
#include "greedy.h"
#include "set.h"
#include <regex>
#include "ScaledScoringFunction.h"

char *keywordJSONFile;
char *annotatedJSONFile;
char *summaryOutputJsonFile;
//char *normsFile;
//int budgetPercentage
int budgetSeconds;

bool importanceRating;
double importanceRatingLambda;

bool megaEventContinuity;
double megaEventContinuityLambda;

bool diversityClusteredScene;
double diversityClusteredSceneLambda;

bool diversityClusteredTime;
double diversityClusteredTimeLambda;

bool diversityClusteredConcept;
double diversityClusteredConceptLambda;

bool disparitySum;
double disparitySumLambda;

// char *clusteringMode;
// char *mode;
// char *concept;
// char *query;
char *unitOfAnnotation;
bool verbose;
char *help;
bool costSensitiveGreedy;
double randomNess;
bool randomPicking = false;

Arg Arg::Args[] = {
    Arg("keywordJSONFile", Arg::Req, keywordJSONFile,
        "JSON file containing keywords and ratings", Arg::SINGLE),
    Arg("annotatedJSONFile", Arg::Req, annotatedJSONFile,
        "JSON file containing the annotation", Arg::SINGLE),
    Arg("unitOfAnnotation", Arg::Req, unitOfAnnotation,
        "Either shot or snippets", Arg::SINGLE),
    Arg("summaryOutputJsonFile", Arg::Req, summaryOutputJsonFile,
        "Desired summary output JSON file", Arg::SINGLE),
    //Arg("budget", Arg::Req, budgetPercentage, "Desired summary budget",
      //  Arg::SINGLE),
    Arg("budget", Arg::Req, budgetSeconds, "Desired summary budget in seconds",
        Arg::SINGLE),
    Arg("importanceRating", Arg::Opt, importanceRating,
        "If you want ImportanceRating term", Arg::SINGLE),
    Arg("importanceRatingLambda", Arg::Opt, importanceRatingLambda,
        "Relative weight for ImportanceRating term", Arg::SINGLE),
    Arg("megaEventContinuity", Arg::Opt, megaEventContinuity,
        "If you want MegaEventContinuity term", Arg::SINGLE),
    Arg("megaEventContinuityLambda", Arg::Opt, megaEventContinuityLambda,
        "Relative weight for MegaEventContinuity term", Arg::SINGLE),
    Arg("diversityClusteredScene", Arg::Opt, diversityClusteredScene,
        "If you want DiversityClusteredScene term", Arg::SINGLE),
    Arg("diversityClusteredTime", Arg::Opt, diversityClusteredTime,
        "If you want DiversityClusteredTime term", Arg::SINGLE),
    Arg("diversityClusteredConcept", Arg::Opt, diversityClusteredConcept,
        "If you want DiversityClusteredConcept term", Arg::SINGLE),
    Arg("disparitySum", Arg::Opt, disparitySum,
        "If you want DiversitySum term", Arg::SINGLE),
    Arg("diversityClusteredSceneLambda", Arg::Opt, diversityClusteredSceneLambda,
        "Relative weight for DiversityClusteredScene term", Arg::SINGLE),
    Arg("diversityClusteredTimeLambda", Arg::Opt, diversityClusteredTimeLambda,
        "Relative weight for DiversityClusteredTime term", Arg::SINGLE),
    Arg("diversityClusteredConceptLambda", Arg::Opt, diversityClusteredConceptLambda,
        "Relative weight for DiversityClusteredConcept term", Arg::SINGLE),
    Arg("disparitySumLambda", Arg::Opt, disparitySumLambda,
        "Relative weight for DisparitySum term", Arg::SINGLE),
    // Arg("clusteringMode", Arg::Opt, clusteringMode,
    //     "Clusters based on scenes (eg. for FRIENDS) or similarity and time "
    //     "(eg. SURVEILLANCE) or concept (eg. for TECHTALKS)",
    //     Arg::SINGLE),
    // Arg("mode", Arg::Req, mode, "Mode: general | query | concepts",
    //     Arg::SINGLE),
    // Arg("concept", Arg::Opt, concept,
    //     "Desired concept for coverage (any category)", Arg::SINGLE),
    // Arg("query", Arg::Opt, query, "Query keyword", Arg::SINGLE),
    Arg("costSensitiveGreedy", Arg::Opt, costSensitiveGreedy,
        "If you want to run naive greedy in cost sensitive way", Arg::SINGLE),
    Arg("randomNess", Arg::Req, randomNess,
        "Amount of random perturbation to ratings. A value of 1 would add "
        "uniformly distributed random perturbations between -0.5 to 0.5. "
        "Should be less than 2.",
        Arg::SINGLE),
    Arg("randomPicking", Arg::Opt, randomPicking,
        "radomly pick one from many snippets/shots of the same score in the summary",
        Arg::SINGLE),
    // Arg("normsFile", Arg::Req, normsFile,
    //     "Path of the norms JSON file for this domain",
    //     Arg::SINGLE),
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

/* std::string ltrim(const std::string& s) {
	return std::regex_replace(s, std::regex("^\\s+"), std::string(""));
}

std::string rtrim(const std::string& s) {
	return std::regex_replace(s, std::regex("\\s+$"), std::string(""));
} */

std::string ltrim(const std::string& s) {
	return std::regex_replace(s, std::regex("^[\\s+\"\']"), std::string(""));
}

std::string rtrim(const std::string& s) {
	return std::regex_replace(s, std::regex("[\\s+\"\']$"), std::string(""));
}

std::string trim(const std::string& s) {
	return ltrim(rtrim(s));
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

std::string strToLower(std::string data) {
    std::transform(data.begin(), data.end(), data.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return data;
}

int main(int argc, char **argv) {
    bool parse_was_ok = Arg::parse(argc, (char **)argv);
    if (!parse_was_ok) {
        Arg::usage();
        exit(-1);
    }

    if(verbose) {
        std::cout << "Lambda values: " << std::endl;
        std::cout << "Importance: " << importanceRating << " Lambda: " << importanceRatingLambda << std::endl;
        std::cout << "Mega: " << megaEventContinuity << " Lambda: " << megaEventContinuityLambda << std::endl;
        std::cout << "Scene: " << diversityClusteredScene << " Lambda: " << diversityClusteredSceneLambda << std::endl;
        std::cout << "Time: " << diversityClusteredTime << " Lambda: " << diversityClusteredTimeLambda << std::endl;
        std::cout << "Concept: " << diversityClusteredConcept << " Lambda: " << diversityClusteredConceptLambda << std::endl;
        std::cout << "DispSum: " << disparitySum << " Lambda: " << disparitySumLambda << std::endl;
    }

    //adapted from http://xpo6.com/list-of-english-stop-words/
    std::vector<std::string> stopWords = {"&", "a","am","an","and","are","as","at","be","by","for","had","has", "hasnt", "have", "he", "ie", "if", "in", "into", "is", "it", "its", "of", "off","on","or","re", "that", "the", "to", "was"};

    nlohmann::json keywordJSON;
    nlohmann::json annotatedJSON;
    std::ifstream keywordJSONFileHandler;
    keywordJSONFileHandler.open(keywordJSONFile);
    std::ifstream annotatedJSONFileHandler;
    annotatedJSONFileHandler.open(annotatedJSONFile);
    std::cout << "OK";
    keywordJSONFileHandler >> keywordJSON;
    annotatedJSONFileHandler >> annotatedJSON;
    std::string unit_s(unitOfAnnotation);
    int num_frames;
    int num_snippets;
    int snippetSize = annotatedJSON["snippet_size"];
    num_snippets = annotatedJSON["num_snippets"];
    int fps;
    fps = annotatedJSON["fps"];  // fps is stored there from opencv and rounded
    int openCVNumFrames = annotatedJSON["num_frames"];
    if (unit_s == "snippet") {
        //num_frames = annotatedJSON["num_frames"];  //num_frames is stored there from opencv
        num_frames = (num_snippets * snippetSize * fps);
        if(openCVNumFrames > num_frames) {
            num_frames = openCVNumFrames;
        }
    } else {
        num_frames = 0;
    }

    // std::string mode_s(mode);
    // std::cout << "Selected Mode: " << mode_s << '\n';

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
    std::cout << "Map of keywords to ratings created!" << '\n';

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
        std::cout << "Maps of mega events to ratings created!" << '\n';
    }

    int n = annotatedJSON["num_snippets"];
    std::vector<float> snippetRatings = std::vector<float>(n, 0);
    int currMegaEventId = 0;
    bool firstMegaEventEncountered = false;
    std::string currMegaEventName;
    Set megaEventTempSet = Set();
    std::vector<Set> megaEvents = std::vector<Set>();
    std::vector<float> ratingsM = std::vector<float>();

    std::vector<Set> clustersScene = std::vector<Set>();
    std::vector<Set> clustersTime = std::vector<Set>();
    std::vector<Set> clustersConcept = std::vector<Set>();
    std::string clusteringMode_s;
    if (diversityClusteredScene && diversityClusteredSceneLambda != 0) {
        // Initiate an empty set of clusters based on num_scenes
        // clusteringMode_s += clusteringMode;
        // if (clusteringMode_s == "scene") {
            int numClusters = annotatedJSON["num_scenes"];
            for (int j = 0; j < numClusters; j++) {
                Set tempSet = Set();
                clustersScene.push_back(tempSet);
            }
        // }
    }
    std::vector<ScoringFunction *> sfVec = std::vector<ScoringFunction *>();
    std::vector<double> lambdas = std::vector<double>(0);

    std::vector<int> shotSnippetSizes = std::vector<int>(0);
    // std::string diversityName;
    // n = number of snippets/shots in the video
    // create snippet ratings and megaEvents and their ratings as is being
    // done in line 123-194 of SoccerScoring.cc

    std::map<std::string, int> conceptMap = std::map<std::string, int>();
    int newConceptId = 0;
    std::map<std::string, int>::iterator conceptIt;

    // if(diversityClustered && clusteringMode_s == "concept") {
      if(diversityClusteredConcept && diversityClusteredConceptLambda != 0) {
        if(verbose) std::cout << "Preparing concept map..." << std::endl;
        //iterate over each keyword of each category to initialize the conceptmap and clusters
        for (auto it = keywordJSON["categories"].begin(); it != keywordJSON["categories"].end(); ++it) {
            //if(it.key() == "num-people" || it.key() == "camera-angle") {
            //    continue;
            //}
            for(auto elem: it.value()["keywords"]) {
                //if(elem == "blank") {
                //    std::cout << "Ignoring \"blank\"" << std::endl;
                //   continue;
                //}
                conceptMap[strToLower(elem)] = newConceptId;
                if(verbose) std::cout << "Keyword: " << elem << " and Id: " << newConceptId << std::endl;
                newConceptId++;
                Set tempSet = Set();
                clustersConcept.push_back(tempSet);
            }
        }
    }


    std::vector<std::string> prevSetOfKeywords;
    std::vector<std::vector<float>> kernel(n, std::vector<float> (n, 10));
    std::vector<std::vector<std::string>> setOfAllKeywords;
    for (int i = 0; i < n; i++) {
      kernel[i][i] = 1.0;
    }
    // Start of the Annotation For Loop

    for (int i = 1; i <= n; i++) {
        if (verbose) std::cout << "Processing snippet: " << i << std::endl;
        std::vector<std::string> setOfKeywords = std::vector<std::string>();
        if (strToLower(unit_s) == "shot") {
            int shot_length =
                annotatedJSON[std::to_string(i)]["shot_length"];
            num_frames += shot_length;
            shotSnippetSizes.push_back(shot_length);
            if (shot_length > 10 * fps) {
                std::cout << "*****Shot " << i
                          << " is longer than 10 seconds" << std::endl;
            }
        } else {
            shotSnippetSizes.push_back(snippetSize * fps);
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
                        << "Part of a running mega event, adding to the set"
                        << std::endl;
                megaEventTempSet.insert(i - 1);
                currMegaEventName =
                    annotatedJSON[std::to_string(i)]["mega_event"]["name"];
                currMegaEventName = strToLower(currMegaEventName);
            } else {
                if (verbose) {
                    std::cout << "This is a new mega event, pushing { ";
                    for (auto i : megaEventTempSet) std::cout << i << ' ';
                    std::cout << " }"
                              << " and its rating "
                              << ratingMapME[currMegaEventName]
                              << std::endl;
                }
                megaEvents.push_back(megaEventTempSet);
                ratingsM.push_back(ratingMapME[currMegaEventName]);
                megaEventTempSet.clear();
                megaEventTempSet.insert(i - 1);
                currMegaEventId =
                    annotatedJSON[std::to_string(i)]["mega_event"]["id"];
                currMegaEventName =
                    annotatedJSON[std::to_string(i)]["mega_event"]["name"];
                currMegaEventName = strToLower(currMegaEventName);
            }
            snippetRatings[i - 1] =
                -ratingMapping(setOfKeywords, ratingMap);
        } else {
            snippetRatings[i - 1] = ratingMapping(setOfKeywords, ratingMap);
        }
        // Create clusters for diversity clustering
        // if (diversityClustered) {
            //
            // if (clusteringMode_s == "scene") {
            if(diversityClusteredScene && diversityClusteredSceneLambda != 0) {
                // diversityName = "DiversityClusteredScene";
                // prepare clusters according to scene information in
                // annotatedJson refer to how it is being done in
                // FriendsScoring.cc - line 131-137 and 199-207
                if (annotatedJSON[std::to_string(i)].find("sceneId") !=
                    annotatedJSON[std::to_string(i)].end()) {
                    clustersScene[annotatedJSON[std::to_string(i)]["sceneId"]]
                        .insert(i - 1);
                } else {
                    std::cout << "WARNING: Scene information not present "
                                 "in snippet "
                              << i << std::endl;
                    std::cout << "ERROR: DiversityClustered can't proceed"
                              << std::endl;
                    return 0;
                }
            }
            // else if (clusteringMode_s == "time") {
            if(diversityClusteredTime && diversityClusteredTimeLambda != 0) {
                // diversityName = "DiversityClusteredTime";
                if (i == 1) {
                    Set tempSet = Set();
                    clustersTime.push_back(tempSet);
                    clustersTime[0].insert(0);
                    prevSetOfKeywords = setOfKeywords;
                } else {
                    if (prevSetOfKeywords == setOfKeywords) {
                        clustersTime[clustersTime.size() - 1].insert(i - 1);
                    } else {
                        Set tempSet = Set();
                        clustersTime.push_back(tempSet);
                        clustersTime[clustersTime.size() - 1].insert(i - 1);
                    }
                    prevSetOfKeywords = setOfKeywords;
                }
                // prepare clusters such that consecutive snippets whose
                // keywords are exactly the same belong to the same cluster
                // instantiate DiversityClustered after the annotation loop
                // if (annotatedJSON[std::to_string(i)].find("time_chunk")
                // != annotatedJSON[std::to_string(i)].end()) {
                //     clusters[annotatedJSON[std::to_string(i)]["time_chunk"]].insert(i-1);
                // }
            }
            // else if (clusteringMode_s == "concept") {
            if(diversityClusteredConcept && diversityClusteredConceptLambda != 0) {
                // diversityName = "DiversityClusteredConcepts";
                /* if(i>500){
                    return 0;
                } */
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
                                tempSet.insert(i-1);
                                clustersConcept.push_back(tempSet);
                            } else {
                                //it is already encountered
                                if(verbose) std::cout << "Old" << std::endl;
                                clustersConcept[conceptMap[word]].insert(i-1);
                                if (verbose) std::cout << "Adding to cluster id " << conceptMap[word] << " and name " << word << std::endl;
                            }
                        }
                        pch = strtok (NULL, " ,.-\n:_()");
                    }
                }
                //iterate over each keyword of each category of this snippet and do the same
                if (annotatedJSON[std::to_string(i)].find("categories") != annotatedJSON[std::to_string(i)].end()) {
                    for (auto it = annotatedJSON[std::to_string(i)]["categories"].begin(); it != annotatedJSON[std::to_string(i)]["categories"].end(); ++it) {
                        // if(it.key() == "num-people" || it.key() == "camera-angle") {
                        //     continue;
                        // }
                        for(auto elem: it.value()) {
                            if(verbose) std::cout << "Keyword of this snippet: " << elem << std::endl;
                            //ignore if "blank"
                            //if(elem == "blank") continue;
                            /* conceptIt = conceptMap.find(elem);
                            if (conceptIt == conceptMap.end()) {
                                //it is a new concept, add
                                if(verbose) std::cout << "New" << std::endl;
                                conceptMap[elem] = newConceptId;
                                newConceptId++;
                                Set tempSet = Set();
                                tempSet.insert(i-1);
                                clusters.push_back(tempSet);
                            } else {
                                //it is already encountered
                                if(verbose) std::cout << "Old" << std::endl;
                                clusters[conceptMap[elem]].insert(i-1);
                            } */
                            clustersConcept[conceptMap[strToLower(elem)]].insert(i-1);
                            if (verbose) std::cout << "Adding to cluster id " << conceptMap[strToLower(elem)] << " and name " << elem << std::endl;
                        }
                    }
                }
            }
            // else {
            //     std::cout << "Invalid clustering mode. Provide one of [scene|time|concept]" << std::endl;
            // }
        // }
    }
    // end of annotations
    if(disparitySum && disparitySumLambda != 0){
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
            //   std::cout << '\n';
            // std::cout << "Set 0" << '\n';
            // // std::cout << "Set 0 size" << setOfAllKeywords[i].size() << '\n';
            // for (int l = 0; l < setOfAllKeywords[i].size(); l++) {
            //   std::cout << setOfAllKeywords[i][l] << ", ";
            // }
            // std::cout << '\n';
            // std::cout << "Set 1" << '\n';
            // for (int l = 0; l < setOfAllKeywords[j].size(); l++) {
            //   std::cout << setOfAllKeywords[j][l] << ", ";
            // }
            // std::cout << '\n';
            // std::cout << "Intersection size" << commonKeywords.size() << '\n';
            // for (int l = 0; l < commonKeywords.size(); l++) {
            //   std::cout << commonKeywords[l] << ", ";
            // }
            // std::cout << '\n';
            // std::cout << "Union" << '\n';
            // for (int l = 0; l < allKeywords.size(); l++) {
            //   std::cout << allKeywords[l] << ", ";
            // }
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
          //else {
          kernel[i][j] = num/denom;
          kernel[j][i] = num/denom;
          //}
          // std::cout << "num: " << num << " denom: " << denom << '\n';
          // std::cout << "From kernel: " << kernelm[i][j] <<'\n';
        }
      }
    }
    // std::cout << "Kernel Matrix computed!" << '\n';
  }
    // if(clusteringMode_s == "concept") {
      if(diversityClusteredConcept && diversityClusteredConceptLambda != 0) {
        if(verbose) {
            std::cout << "Concept map:" << std::endl;
            for (std::pair<std::string, int> element : conceptMap) {
                std::string word = element.first;
                int index = element.second;
                std::cout << word << " :: " << index << std::endl;
            }
        }
    }

    if (megaEventTempSet.size() > 0) {
        if (verbose) {
            std::cout << "Pushing the last mega event encountered { ";
            for (auto i : megaEventTempSet) std::cout << i << ' ';
            std::cout << " }"
                      << " and its rating "
                      << ratingMapME[currMegaEventName] << std::endl;
        }
        megaEvents.push_back(megaEventTempSet);
        ratingsM.push_back(ratingMapME[currMegaEventName]);
    }

    std::cout << std::endl;

    if (randomNess) {
        std::cout << "Adding random perturbation to the snippet ratings "
                     "and mega event ratings"
                  << std::endl;
        std::random_device rd1;  // Will be used to obtain a seed for the
                                 // random number engine
        std::mt19937 gen1(
            rd1());  // Standard mersenne_twister_engine seeded with rd()
        std::uniform_real_distribution<> dist1(0.0, randomNess);
        float rnd;
        for (int i = 0; i < snippetRatings.size(); i++) {
            rnd = dist1(gen1);
            rnd = rnd - randomNess / 2;
            if (snippetRatings[i] < 0) {
                snippetRatings[i] = -(abs(snippetRatings[i]) + rnd);
            } else if (snippetRatings[i] > 0) {
                snippetRatings[i] += rnd;
            } else {
                // do not disturb the 0 ones
            }
        }
        std::random_device rd2;  // Will be used to obtain a seed for the
                                 // random number engine
        std::mt19937 gen2(
            rd2());  // Standard mersenne_twister_engine seeded with rd()
        std::uniform_real_distribution<> dist2(0.0, randomNess);
        for (int i = 0; i < ratingsM.size(); i++) {
            rnd = dist2(gen2);
            rnd = rnd - randomNess / 2;
            if (ratingsM[i] > 0) {
                ratingsM[i] += rnd;
            } else {
                // do not disturb the 0 ones
            }
        }
    }

    std::cout << "Preparing scoring terms for optimization" << std::endl;

    MegaEventContinuity *m = NULL;
    ImportanceRating *ir = NULL;
    DiversityClustered *dcScene = NULL;
    DiversityClustered *dcTime = NULL;
    DiversityClustered *dcConcept = NULL;
    DisparitySum *dsum = NULL;
    // ScaledScoringFunction *mScaled = NULL;
    // ScaledScoringFunction *irScaled = NULL;
    // ScaledScoringFunction *dcSceneScaled = NULL;
    // ScaledScoringFunction *dcTimeScaled = NULL;
    // ScaledScoringFunction *dcConceptScaled = NULL;
    // ScaledScoringFunction *dsumScaled = NULL;

    // nlohmann::json normData;
    // std::ifstream normDataJson;
    // normDataJson.open(normsFile);
    // normDataJson >> normData;

    std::string video_name_with_extension = annotatedJSON["video_name"];
    size_t lastindex = video_name_with_extension.find_last_of("."); 
    std::string video_name = video_name_with_extension.substr(0, lastindex); 

    // if megaEventContinuity, instantiate it (needs n, megaEvents and their
    // ratings)
    if (megaEventContinuity && megaEventContinuityLambda != 0) {
        m = new MegaEventContinuity("MegaEventContinuity", n, ratingsM,
                                    megaEvents, verbose);
        //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-mega-cont"];
        //mScaled = new ScaledScoringFunction(m, 1/scale);
        //sfVec.push_back(mScaled);
        sfVec.push_back(m);
        lambdas.push_back(megaEventContinuityLambda);
    }

    // if importanceRating and megaEventContinuity, instantiate
    // ImportanceRating with exclusive = true (needs n and snippetRatings)
    // if importanceRating but !megaEventContinuity, instantiate
    // ImportanceRating with exclusive = false (needs n and snippetRatings)
    if (importanceRating && importanceRatingLambda != 0) {
        if (megaEventContinuity && megaEventContinuityLambda != 0) {
            // combined, operates on mutually exclusive snippets
            ir = new ImportanceRating("ImportanceRatingExclusive", n,
                                      snippetRatings, true, verbose);
            //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-imp"];
            //irScaled = new ScaledScoringFunction(ir, 1/scale);
            //sfVec.push_back(irScaled);
            sfVec.push_back(ir);
            lambdas.push_back(importanceRatingLambda);
        } else {
            // operates on all snippets based on their ratings
            ir = new ImportanceRating("ImportanceRatingInclusive", n,
                                      snippetRatings, false, verbose);
            //std::cout << video_name << budgetSeconds << std::endl;
            //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-imp"];
            //irScaled = new ScaledScoringFunction(ir, 1/scale);
            //sfVec.push_back(irScaled);
            sfVec.push_back(ir);
            lambdas.push_back(importanceRatingLambda);
        }
    }

    // if diversityClustered instantiate it appropriately (needs n, clusters
    // and snippetRatings)
    if (diversityClusteredScene && diversityClusteredSceneLambda != 0) {
        dcScene = new DiversityClustered("DiversityClusteredScene", n, clustersScene,
                                    snippetRatings, verbose);
        //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-div-scene"];
        //dcSceneScaled = new ScaledScoringFunction(dcScene, 1/scale);
        //sfVec.push_back(dcSceneScaled);
        sfVec.push_back(dcScene);
        lambdas.push_back(diversityClusteredSceneLambda);
    }
    if(diversityClusteredTime && diversityClusteredTimeLambda != 0){
        dcTime = new DiversityClustered("DiversityClusteredTime", n, clustersTime,
                                    snippetRatings, verbose);
        //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-div-time"];
        //dcTimeScaled = new ScaledScoringFunction(dcTime, 1/scale);
        //sfVec.push_back(dcTimeScaled);
        sfVec.push_back(dcTime);
        lambdas.push_back(diversityClusteredTimeLambda);
    }
    if(diversityClusteredConcept && diversityClusteredConceptLambda != 0){
        dcConcept = new DiversityClustered("DiversityClusteredConcepts", n, clustersConcept,
                                    snippetRatings, verbose);
        //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-div-concept"];
        //dcConceptScaled = new ScaledScoringFunction(dcConcept, 1/scale);
        //sfVec.push_back(dcConceptScaled);
        sfVec.push_back(dcConcept);
        lambdas.push_back(diversityClusteredConceptLambda);
    }
    if(disparitySum && disparitySumLambda != 0){
        dsum = new DisparitySum("DiversitySim", n, kernel, verbose);
        //double scale = normData[video_name][std::to_string(budgetSeconds)]["max-div-sim"];
        //dsumScaled = new ScaledScoringFunction(dsum, 1/scale);
        //sfVec.push_back(dsumScaled);
        sfVec.push_back(dsum);
        lambdas.push_back(disparitySumLambda);
    }
    // prepare the mixture using appropriate lambdas the way it is being
    // done in SoccerScoring.cc line 219-247
    // find optimal set by naiveGreedyMax and create outputSummary json as is
    // being done in line 248 to 283 of SoccerScoring.cc
    std::cout << "N: " << n << '\n';
    CombinedScoringFunction sf =
        CombinedScoringFunction("Mixture", n, sfVec, lambdas);
    // std::cout << "Created Mixtures successfully" << '\n';
    Set greedySet;
    // std::cout << "Instantiated all functions" << std::endl;
    //int budgetFrames = std::ceil((budgetPercentage / 100.0) * num_frames);
    int budgetFrames = budgetSeconds * fps;
    std::cout << "Total number of frames in video (possibly greater due to rounding) = " << num_frames
              << std::endl;

    // if (verbose) {
    std::cout << "Shot / snippet sizes = ";
    for (auto elem : shotSnippetSizes) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    //}

    //remove small non mega event shots/snippets from ground set to be used for naivegreedymax
    //TODO: this and size aware naiveGreedy selection avoids non mega event small snippets to get into the summary, but allows small
    //mega event snippets to get in thus creating holes in mega events
    std::set<int> groundSet;
    for(int j = 0; j < n; j++) {
        if(snippetRatings[j] < 0 || shotSnippetSizes[j] > fps) {
            groundSet.insert(j);
            } else {
            if (verbose) {
                std::cout << "Element " << j << " is a small non-mega event, not adding in ground set" << std::endl;
            }
        }
    }
    bool allowMore = false;
    for(auto elem : sfVec){
      if (elem->getName().find("Diversity") != std::string::npos) {
          allowMore = true;
          if(verbose) {std::cout << "**Found Diversity Element, allowMore is Set to true**" << '\n';}
      }
    }
    // }
    // std::cout << "Calling naiveGreedyMax" << '\n';
    naiveGreedyMax(sf, groundSet, budgetFrames, shotSnippetSizes, greedySet,
                   costSensitiveGreedy, snippetRatings, fps, allowMore, randomPicking, (verbose ? 1 : 0));
    std::cout << "Score: " << sf.eval(greedySet) << '\n';
    // std::sort(greedySet, greedySet.size())
    // std::cout << "Optimized!" << '\n';
    std::set<int> sortedGreedySet;
    for (auto i : greedySet) sortedGreedySet.insert(i);

    nlohmann::json summaryJson;
    summaryJson["video_name"] = annotatedJSON["video_name"];
    summaryJson["num_snippets"] = annotatedJSON["num_snippets"];
    summaryJson["summary_num_snippets"] = greedySet.size();
    summaryJson["video_category"] = annotatedJSON["video_category"];
    summaryJson["snippet_size"] = snippetSize;
    summaryJson["video_fps"] = fps;
    // summaryJson["mode"] = mode_s;
    summaryJson["video_num_frames"] = num_frames;
    summaryJson["budget_seconds"] = budgetSeconds;
    nlohmann::json emptyJson(nlohmann::json::value_t::object);
    std::vector<int> summary(num_frames, 0);
    int start;
    int end;
    int summary_num_frames = 0;
    std::cout << "Size of sorted greedy set: " << sortedGreedySet.size()<< '\n';
    for (auto elem : sortedGreedySet) {
      //std::cout << "element: " << elem <<'\n';
        // Translate shot/snippet number elem to corresponing list of frames and
        // assign 1
        if (unit_s == "shot") {
            start = annotatedJSON[std::to_string(elem + 1)]["shot_start"];
            int shot_length =
                annotatedJSON[std::to_string(elem + 1)]["shot_length"];
            end = start + shot_length - 1 - 1;  //additional -1 is due to the same issue as
            //in tool.py, summaryViewer.py and summarySnippetsToVideoGenerator.py
        } else {
            start = elem * snippetSize * fps;
            //if (start > openCVNumFrames - 1) {
                //std::cout << "Start of snippet " << elem + 1 << " is beyond end of video!!" << std::endl;
                //return 0;
            //}
            end = (start + snippetSize * fps) - 1;
            //if(end > openCVNumFrames - 1) {
                 //if (elem+1 != n) {
                    //std::cout << "End of intermediate snippet " << elem + 1 << " is beyond end of video!!" << std::endl;
                    //return 0;
                //} else {
                    //end = openCVNumFrames - 1;
                //}
            //}
            if(end > num_frames) {
                if (elem+1 != n) {
                    std::cout << "End of intermediate snippet " << elem + 1 << " is beyond end of video!!" << std::endl;
                    return 0;
                } else {
                    end = num_frames - 1;
                }
            }
        }
        for (size_t i = start; i <= end; i++) {
            summary[i] = 1;
            summary_num_frames += 1;
        }
        summaryJson[std::to_string(elem + 1)] = emptyJson;
        //summary_num_frames += shotSnippetSizes[elem];
    }

    if (summary.size() != num_frames) {
        std::cout << "summary.size() " << summary.size() << " is not equal to num_frames " << num_frames << std::endl;
        return 0;
    }
    //std::cout << "Translated!" << '\n';
    summaryJson["summary_num_frames"] = summary_num_frames;

    std::vector<std::string> terms;
    for (auto elem : sfVec) {
        terms.push_back(elem->getName());
    }
    summaryJson["terms"] = terms;
    summaryJson["lambdas"] = lambdas;
    summaryJson["summary"] = summary;
    std::ofstream file(summaryOutputJsonFile);
    file << summaryJson;

    std::cout << "Expected duration of summary = " << budgetSeconds << " seconds" << std::endl;
    std::cout << "Actual duration of summary = " << (summary_num_frames / (float)fps) << " seconds" << std::endl;

    std::cout << "\n******Stats******" << std::endl;
    std::cout << "Budget Randomness CostSensitivity NumBudgetFrames NumSummaryFrames NumSummarySnippets OutputFileName" << std::endl;
    //std::cout << budgetPercentage << " ";
    std::cout << budgetSeconds << " ";
    std::cout << randomNess << " ";
    std::cout << costSensitiveGreedy << " ";
    std::cout << budgetFrames << " ";
    std::cout << summary_num_frames << " ";
    std::cout << sortedGreedySet.size() << " ";
    std::cout << summaryOutputJsonFile << " ";
    std::cout << std::endl;
    for (auto elem : terms) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    for (auto elem : lambdas) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    for (auto i : sortedGreedySet) std::cout << i + 1 << " ";
}
