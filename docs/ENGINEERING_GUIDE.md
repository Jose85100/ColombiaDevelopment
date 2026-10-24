# Engineering guide

## C++17
```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
./build/territorial_risk
./build/fraud_risk
```

## Python
```bash
cd python
python -m pip install -e . pytest
python -m pytest -q
```

## Design rules
- C++ contains deterministic numerical kernels and CLI prototypes.
- Python contains research APIs, scenario generation and explainability experiments.
- Notebooks consume modules; they should not hide core business logic in cells.
- Synthetic data is the default until a dataset has provenance and a compatible license.
- Thresholds and coefficients are configuration/calibration candidates, never production facts.
- New models require a baseline, invariant tests, out-of-sample evaluation where applicable and failure analysis.

## Next numerical components
Territorial: robust optimization, Monte Carlo climate shocks, spatial dependence and portfolio selection under budget constraints.
Fraud: streaming feature state, graph propagation, conformal/uncertainty layer, cost-sensitive thresholds and drift/adversarial evaluation.
