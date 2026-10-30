#pragma once
#include "risk_core.hpp"
namespace colombia {
struct Territory { double access_gap, climate_hazard, fiscal_capacity, connectivity_gap, renewable_potential, institutional_capacity; };
struct TerritorialScore { double vulnerability, opportunity, priority; };
inline TerritorialScore score_territory(const Territory&t){
 const double v=normalized_score({{t.access_gap,.30},{t.climate_hazard,.20},{1-t.fiscal_capacity,.15},{t.connectivity_gap,.20},{1-t.institutional_capacity,.15}});
 const double o=normalized_score({{t.renewable_potential,.45},{t.institutional_capacity,.25},{t.access_gap,.15},{t.connectivity_gap,.15}});
 // Priority is deliberately non-linear: opportunity is valuable only where vulnerability is material.
 return {v,o,clamp01(std::sqrt(v*o))};
}
inline double resilient_npv(double capex,double annual_benefit,double annual_opex,double discount,int years,double hazard_prob,double hazard_loss_fraction){
 if(capex<0||annual_benefit<0||annual_opex<0||discount<=-1||years<1) throw std::invalid_argument("invalid economics");
 double npv=-capex; const double expected=(annual_benefit-annual_opex)-hazard_prob*hazard_loss_fraction*capex;
 for(int y=1;y<=years;++y) npv+=expected/std::pow(1+discount,y); return npv;
}
}
