#include <iomanip>
#include <iostream>
#include "colombia/territorial.hpp"
int main(){colombia::Territory t{.82,.55,.30,.74,.91,.58};auto s=colombia::score_territory(t);auto npv=colombia::resilient_npv(10'000'000,2'100'000,550'000,.10,10,.08,.12);std::cout<<std::fixed<<std::setprecision(4)<<"vulnerability="<<s.vulnerability<<" opportunity="<<s.opportunity<<" priority="<<s.priority<<" resilient_npv="<<npv<<"\n";}
