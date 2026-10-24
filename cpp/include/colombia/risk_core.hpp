#pragma once
#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace colombia {
inline double clamp01(double x){ return std::max(0.0,std::min(1.0,x)); }
inline double sigmoid(double x){ return x>=0?1.0/(1.0+std::exp(-x)):std::exp(x)/(1.0+std::exp(x)); }

struct WeightedSignal { double value; double weight; };
inline double normalized_score(const std::vector<WeightedSignal>& xs){
 double num=0.0,den=0.0; for(const auto&s:xs){if(s.weight<0) throw std::invalid_argument("negative weight");num+=clamp01(s.value)*s.weight;den+=s.weight;}
 if(den<=0) throw std::invalid_argument("zero total weight"); return num/den;
}

struct Scenario { double probability; double loss; };
inline double expected_loss(const std::vector<Scenario>& xs){
 double p=0,e=0; for(const auto&s:xs){if(s.probability<0||s.loss<0) throw std::invalid_argument("invalid scenario");p+=s.probability;e+=s.probability*s.loss;}
 if(std::abs(p-1.0)>1e-9) throw std::invalid_argument("probabilities must sum to one"); return e;
}

inline double entropy(const std::vector<double>& probs){double h=0,p=0;for(double x:probs){if(x<0)throw std::invalid_argument("negative probability");p+=x;if(x>0)h-=x*std::log(x);}if(std::abs(p-1)>1e-9)throw std::invalid_argument("probabilities must sum to one");return h;}
}
