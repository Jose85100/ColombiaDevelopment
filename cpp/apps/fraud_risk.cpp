#include <iomanip>
#include <iostream>
#include "colombia/fraud.hpp"
int main(){colombia::FraudSignals s{.7,.8,.6,.4,.2,.9};auto d=colombia::fraud_decision(s);const char* a=d.action==colombia::FraudDecision::Action::ALLOW?"ALLOW":d.action==colombia::FraudDecision::Action::STEP_UP?"STEP_UP":"REVIEW";std::cout<<std::fixed<<std::setprecision(4)<<"fraud_probability="<<d.probability<<" action="<<a<<"\n";}
