"""Private-capital agroindustry unit economics; currency COP millions throughout.
Illustrative parameters only, not Colombia observed costs or legally validated payroll.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Project:
    hectares:float=200
    yield_ton_ha:float=6
    sale_price_mcop_ton:float=2.4
    variable_cost_mcop_ton:float=.85
    field_cost_mcop_ha:float=3.5
    capex_mcop:float=4500
    annual_fixed_mcop:float=600
    staff_per_rotation:int=16
    annual_fully_loaded_pay_mcop_per_staff:float=52
    transport_lodging_mcop_per_staff_year:float=12
    spoilage:float=.08
    annual_growth:float=.02
    discount_rate:float=.16
    tax_rate:float=.35
    years:int=12
    working_capital_mcop:float=350
    maintenance_capex_mcop_year:float=120
    water_m3_per_ton:float=150
    max_water_m3_year:float=200000

def evaluate(p:Project):
    vals=(p.hectares,p.yield_ton_ha,p.sale_price_mcop_ton,p.variable_cost_mcop_ton,p.field_cost_mcop_ha,p.capex_mcop,p.annual_fixed_mcop,p.annual_fully_loaded_pay_mcop_per_staff,p.transport_lodging_mcop_per_staff_year,p.spoilage,p.annual_growth,p.discount_rate,p.tax_rate,p.working_capital_mcop,p.maintenance_capex_mcop_year,p.water_m3_per_ton,p.max_water_m3_year)
    if any(not isfinite(v) for v in vals) or any(v<0 for v in vals[:9]) or p.staff_per_rotation<0 or not 0<=p.spoilage<1 or p.annual_growth<=-1 or p.discount_rate<=-1 or not 0<=p.tax_rate<=1 or p.years<1 or any(v<0 for v in vals[13:]):
        raise ValueError('invalid project')
    # Two full-time equivalent rotating crews is a planning assumption, not labor-law validation.
    headcount=p.staff_per_rotation*2
    payroll=headcount*(p.annual_fully_loaded_pay_mcop_per_staff+p.transport_lodging_mcop_per_staff_year)
    harvest=p.hectares*p.yield_ton_ha
    sold=harvest*(1-p.spoilage)
    water=harvest*p.water_m3_per_ton
    cashflows=[-p.capex_mcop-p.working_capital_mcop]
    rows=[]
    for t in range(1,p.years+1):
        scale=(1+p.annual_growth)**(t-1)
        revenue=sold*p.sale_price_mcop_ton*scale
        cost=sold*p.variable_cost_mcop_ton*scale+p.hectares*p.field_cost_mcop_ha+payroll+p.annual_fixed_mcop
        ebitda=revenue-cost
        # Simplification: tax on positive EBITDA, not actual taxable income; no debt, depreciation or loss carryforward.
        tax=max(0,ebitda)*p.tax_rate
        free_cash=ebitda-tax-p.maintenance_capex_mcop_year
        if t==p.years:free_cash+=p.working_capital_mcop
        cashflows.append(free_cash)
        rows.append({'year':t,'revenue_mcop':revenue,'ebitda_mcop':ebitda,'unlevered_fcf_mcop':free_cash})
    npv=sum(cf/(1+p.discount_rate)**t for t,cf in enumerate(cashflows))
    return {'npv_mcop':npv,'cashflows_mcop':cashflows,'annual_water_m3':water,'water_within_cap':water<=p.max_water_m3_year,'headcount_assumed':headcount,'annual_staff_cost_mcop':payroll,'year1':rows[0],'annual':rows}
