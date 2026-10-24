#include <cassert>
#include <cmath>
#include "colombia/territorial.hpp"
#include "colombia/fraud.hpp"
int main(){using namespace colombia;assert(std::abs(normalized_score({{0,.5},{1,.5}})-.5)<1e-12);assert(std::abs(expected_loss({{.25,100},{.75,0}})-25)<1e-12);auto low=fraud_decision({0,0,0,0,0,0});auto high=fraud_decision({1,1,1,1,1,1});assert(high.probability>low.probability);auto a=score_territory({.8,.6,.2,.8,.9,.7});assert(a.priority>=0&&a.priority<=1);assert(geovelocity_kmh(100,2)==50);return 0;}
