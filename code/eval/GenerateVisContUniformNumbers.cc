/* Takes the following argument
summaryJson (of a particular video and a particular budget generated in some way containing summary frames and shots information)
and prints to stdout viscont score, normalized vis_cont score and normalized uniformity score
 */

#include <cmath>
#include <fstream>   // std::ifstream
#include <iostream>  // std::cout
#include <nlohmann/json.hpp>
#include "arguments.h"
#include "set.h"
#include <regex>
#include <dirent.h>

char *summaryJSONFile;
bool verbose;
char *help;

Arg Arg::Args[] = {
    Arg("summaryJsonOfAVideo", Arg::Req, summaryJSONFile,
        "JSON file containing summary of a video", Arg::SINGLE),
    Arg("verbose", Arg::Req, verbose, "Verbose mode", Arg::SINGLE),
    Arg("help", Arg::Help, help, "Print this message"),
    Arg()};

bool is_number(const std::string &s) {
  if (s.empty()) {
      return false;
  }
  std::string dot = ".";
  size_t dotPos = s.find(dot);
  if (dotPos != std::string::npos) {
      return std::all_of(s.begin(), s.begin() + dotPos, ::isdigit);
  } else {
      return std::all_of(s.begin(), s.end(), ::isdigit);
  }
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

// double computeStdDev(std::vector<int> v) {
//     double sum = std::accumulate(v.begin(), v.end(), 0.0);
//     double mean = sum / v.size();

//     std::vector<double> diff(v.size());
//     std::transform(v.begin(), v.end(), diff.begin(), [mean](double x) { return x - mean; });
//     double sq_sum = std::inner_product(diff.begin(), diff.end(), diff.begin(), 0.0);
//     double stdev = std::sqrt(sq_sum / v.size() - 1);
//     return stdev;
// }

double l2_norm(std::vector<double> const& u) {
    double accum = 0.;
    for (double x : u) {
        accum += (x * x);
    }
    return std::sqrt(accum);
}

int main(int argc, char **argv) {
    bool parse_was_ok = Arg::parse(argc, (char **)argv);
    if (!parse_was_ok) {
        Arg::usage();
        exit(-1);
    }

    nlohmann::json summaryJSON;
    std::ifstream summaryJSONFileHandler;
    summaryJSONFileHandler.open(summaryJSONFile);
    summaryJSONFileHandler >> summaryJSON;

    double vis_cont = 0.0;
    double normalized_vis_cont = 0.0;
    double normalized_uniformity = 0.0;
    double adjusted_uniformity = 0.0;

    //represent this summary as frames vector
    std::vector<int> summaryFrames = summaryJSON["summary"];
    int summaryNumFrames = summaryJSON["summary_num_frames"];
    if(verbose) {
        std::cout << "Total number of frames = " << summaryFrames.size() << std::endl;
        std::cout << "Number of frames in summary = " << summaryNumFrames << std::endl;
    }
    if (summaryNumFrames == 0) {
        if(verbose) {
            std::cout << "Summary is empty!" << std::endl;
        }
        std::cout << "0 0" << std::endl;
        return 0;
    }
    bool chain = false;
    int chainLength = 0;
    for (int i=0; i<summaryFrames.size(); i++) {
        if(summaryFrames[i] == 0) {
            if(chain) {
                //a chain has ended
                if(verbose) {
                    std::cout << "A chain has ended. Chain length: " << chainLength << std::endl;
                }
                vis_cont += (chainLength * chainLength);
                //std::cout << vis_cont << std::endl;
                chain = false;
                chainLength = 0;
            } else {
                continue;
            }
        } else {
            if(chain) {
                chainLength++;
            } else {
                //a new chain has begun
                chain = true;
                chainLength = 1;
            }
        }
    }
    //see if there is a last unprocessed chain remaining
    if(chain) {
        vis_cont += (chainLength * chainLength);
    }
    normalized_vis_cont = vis_cont/(summaryNumFrames * summaryNumFrames);
    if(verbose) {
        std::cout << "vis_cont = " << vis_cont << std::endl;
        std::cout << "normalized_vis_cont = " << normalized_vis_cont << std::endl;
    }
    
    //compute uniformity score
    //add one 1 artifically at end to take the whole length into consideration for uniformity
    //summaryFrames[summaryFrames.size()-1] = 1;
    //summaryFrames[0] = 1;
    //first get representative center frames from chains
    int chainBeginFrame;
    int chainEndFrame;
    chain = false;
    int rep;
    std::vector<int> representativeFrames;
    representativeFrames.push_back(0);
    for (int i=0; i<summaryFrames.size(); i++) {
        if(summaryFrames[i] == 0) {
            if(chain) {
                //a chain has ended
                chain = false;
                chainEndFrame = i - 1;
                if (chainEndFrame == chainBeginFrame) {
                    //this chain had a single frame
                    rep = chainBeginFrame;
                    representativeFrames.push_back(rep);
                } else {
                    //more than one frames in chain, take middle as representative
                    rep = chainBeginFrame + (chainEndFrame - chainBeginFrame)/2;
                    representativeFrames.push_back(rep);
                }
                if(verbose) {
                    std::cout << "A chain has ended; chainBeginFrame: " << chainBeginFrame << " chainEndFrame: " << chainEndFrame << std::endl;
                    std::cout << "Representative: " << rep << std::endl;
                }
            } else {
                continue;
            }
        } else {
            if(chain) {
            } else {
                //a new chain has begun
                chain = true;
                chainBeginFrame = i;
            }
        }
    }
    //see if there is a last unprocessed chain remaining
    if(chain) {
        chainEndFrame = summaryFrames.size() - 1;
        if (chainEndFrame == chainBeginFrame) {
            //this chain had a single frame
            rep = chainBeginFrame;
            representativeFrames.push_back(rep);
        } else {
            //more than one frames in chain, take middle as representative
            rep = chainBeginFrame + (chainEndFrame - chainBeginFrame)/2;
            representativeFrames.push_back(rep);
        }
        if(verbose) {
            std::cout << "A chain has ended; chainBeginFrame: " << chainBeginFrame << " chainEndFrame: " << chainEndFrame << std::endl;
            std::cout << "Representative: " << rep << std::endl;
        }
    }
    representativeFrames.push_back(summaryFrames.size()-1);
    std::vector<int> deltas;
    double deltasSum = 0.0;
    int delta = 0;
    for (int i=1; i<representativeFrames.size(); i++) {
        delta = representativeFrames[i] - representativeFrames[i-1];
        deltas.push_back(delta);
        deltasSum += delta;
    }
    
    //check how uniform the deltas are
    //double stdev = computeStdDev(deltas);
    //taken from https://stats.stackexchange.com/questions/25827/how-does-one-measure-the-non-uniformity-of-a-distribution
    std::vector<double> normalizedDeltas;
    for(int delta : deltas) {
        normalizedDeltas.push_back(delta/deltasSum);
    }
    if(verbose) {
        std::cout << "Deltas:" << std::endl;
        for (int elem : deltas) {
            std::cout << elem << " ";
        }
        std::cout << std::endl;
        std::cout << "Sum of deltas = " << deltasSum << std::endl;
        std::cout << "Normalized Deltas:" << std::endl;
        for (double elem : normalizedDeltas) {
            std::cout << elem << " ";
        }
        std::cout << std::endl;
    }
    double l2norm = l2_norm(normalizedDeltas);
    if(verbose) {
        std::cout << "L2Norm of Normalized Deltas = " << l2norm << std::endl;
    }
    normalized_uniformity = 1 - (((l2norm * std::sqrt(normalizedDeltas.size()) - 1) / (std::sqrt(normalizedDeltas.size()) - 1)));
    //adjusted_uniformity = normalized_uniformity * ((representativeFrames.size()-2-1)/float(summaryNumFrames-1));
    if(verbose) {
        std::cout << "Normalized uniformity: " << normalized_uniformity << std::endl;
        //std::cout << "Adjusted uniformity: " << adjusted_uniformity << std::endl;
    }
    //if(adjusted_uniformity < 0 || adjusted_uniformity > 1) {
    //    std::cout << "***Incorrect normalized value!!!!" << std::endl;
    //    return 0;
    //}

    std::cout << normalized_vis_cont << " " << normalized_uniformity << std::endl;
}
