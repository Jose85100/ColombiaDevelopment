#pragma once
#include "risk_core.hpp"
namespace colombia {
struct FraudSignals { double identity, device, velocity, behavioral, document, graph; };
struct FraudDecision { double probability; enum class Action{ALLOW,STEP_UP,REVIEW} action; };
inline FraudDecision fraud_decision(const FraudSignals&s){
 // Logistic ensemble; coefficients are synthetic defaults, not calibrated production parameters.
 const double z=-3.2+1.35*clamp01(s.identity)+1.15*clamp01(s.device)+1.10*clamp01(s.velocity)+.75*clamp01(s.behavioral)+1.25*clamp01(s.document)+1.55*clamp01(s.graph);
 const double p=sigmoid(z);
 const auto a=p>=.65?FraudDecision::Action::REVIEW:p>=.30?FraudDecision::Action::STEP_UP:FraudDecision::Action::ALLOW;
 return {p,a};
}
inline double geovelocity_kmh(double km,double hours){if(km<0||hours<=0)throw std::invalid_argument("invalid geovelocity");return km/hours;}
}
