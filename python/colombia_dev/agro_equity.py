"""Transparent scenario tools for farmer ownership and agroindustry economics.

Research only: no legal advice, securities offering, or promised returns.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Ownership:
    farmers: float = .55
    investors: float = .30
    adult_incentive_pool: float = .10
    founders: float = .05

    def validate(self):
        values=(self.farmers,self.investors,self.adult_incentive_pool,self.founders)
        if not all(isfinite(x) and x>=0 for x in values) or abs(sum(values)-1)>1e-9:
            raise ValueError("ownership must be nonnegative and total 100%")

def equity_after_round(ownership: Ownership, pre_money: float, new_money: float, farmer_pro_rata: float=0.0):
    """New shares priced at pre-money valuation; farmer_pro_rata is producer cash contribution.

    Returns percentage ownership after primary financing; assumes existing holders do
    not subscribe except farmer vehicle, and new_money includes its contribution.
    """
    ownership.validate()
    if pre_money<=0 or new_money<0 or not 0<=farmer_pro_rata<=new_money:
        raise ValueError("invalid financing")
    dilution=pre_money/(pre_money+new_money)
    return {"farmers":ownership.farmers*dilution+farmer_pro_rata/(pre_money+new_money),
            "investors_existing":ownership.investors*dilution,
            "adult_incentive_pool":ownership.adult_incentive_pool*dilution,
            "founders":ownership.founders*dilution,
            "new_external_investors":(new_money-farmer_pro_rata)/(pre_money+new_money)}

@dataclass(frozen=True)
class AgroScenario:
    hectares: float
    yield_tons_per_ha: float
    sale_price_per_ton: float
    farm_cost_per_ha: float
    processing_cost_per_ton: float
    fixed_cost: float
    spoilage_rate: float = .05

def operating_result(s: AgroScenario):
    values=(s.hectares,s.yield_tons_per_ha,s.sale_price_per_ton,s.farm_cost_per_ha,s.processing_cost_per_ton,s.fixed_cost)
    if any(not isfinite(x) or x<0 for x in values) or not isfinite(s.spoilage_rate) or not 0<=s.spoilage_rate<1:
        raise ValueError("invalid agro scenario")
    harvest=s.hectares*s.yield_tons_per_ha
    saleable=harvest*(1-s.spoilage_rate)
    revenue=saleable*s.sale_price_per_ton
    costs=s.hectares*s.farm_cost_per_ha+saleable*s.processing_cost_per_ton+s.fixed_cost
    return {"harvest_tons":harvest,"saleable_tons":saleable,"revenue":revenue,"operating_cost":costs,"operating_surplus_before_tax_finance":revenue-costs}

def hypothetical_distribution(surplus: float, distributable_fraction: float, ownership: Ownership):
    """Illustrative distribution only; actual dividends require lawful approvals."""
    ownership.validate()
    if surplus<0 or not 0<=distributable_fraction<=1:
        raise ValueError("invalid distribution")
    amount=surplus*distributable_fraction
    return {"farmers":amount*ownership.farmers,"investors":amount*ownership.investors,
            "adult_incentive_pool":amount*ownership.adult_incentive_pool,"founders":amount*ownership.founders,
            "retained":surplus-amount}
