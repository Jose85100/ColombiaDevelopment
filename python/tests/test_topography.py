from colombia_dev.topography import profile_metrics,interpolate_profile

def test_flat_profile():
    x=profile_metrics([(0,100),(1000,100),(2000,100)])
    assert x["max_abs_grade"]==0 and x["segments_above_limit"]==[]

def test_steep_segment():
    assert profile_metrics([(0,100),(1000,130)],.015)["segments_above_limit"]==[1]

def test_interpolation():
    assert interpolate_profile([(0,0),(100,20)],50)==[(0,0),(50,10),(100,20)]
