"""
=============================================================
  PRECAST YARD SIMULATION  —  pure NumPy ML
  Predict TIME given COST  ─or─  COST given TIME

  All monetary values in Indian Rupees (₹ INR)
  Indian market references:
    Concrete M30-M50    :  ₹5,000  –  ₹9,000  / m³
    Equipment fleet     :  ₹8,000  –  ₹25,000 / day
    Typical project     :  ₹5 lakh –  ₹5 crore
  Cost components: material + equipment hire + curing — labour excluded
=============================================================

SIGNALS (10 inputs — curing_method removed from input,
         results are always returned for ALL 3 methods)
  1.  num_elements          – number of precast pieces to produce
  2.  element_complexity    – 1-10 (encodes size, dimension, reinforcement)
  3.  temperature           – ambient °C during production & curing
  4.  humidity              – relative humidity % (0-100)
  5.  yard_area_m2          – available casting area in m²
  6.  equipment_availability– fraction of full fleet ready (0-1)
  7.  water_budget_liters   – max water allowed for curing
  8.  concrete_m3           – total concrete volume (m³)
  9.  material_unit_cost    – cost per m³ of concrete (₹ INR)
 10.  overhead_pct          – overhead as fraction of direct cost (0-1)

CURING METHODS  (always evaluated for all 3)
  WATER    – traditional ponding/spraying; high water use; 14 days
  STEAM    – pressurised steam; accelerated hydration; 1-3 days; costly
  CHEMICAL – curing compound spray; no water; 7-10 days; moderate cost
"""

import numpy as np
from dataclasses import dataclass, asdict
from typing import Optional
from enum import IntEnum


# ─────────────────────────────────────────────────────────────
#  CURING METHOD ENUM
# ─────────────────────────────────────────────────────────────

class CuringMethod(IntEnum):
    WATER    = 0   # ponding / wet burlap — IS 456 standard
    STEAM    = 1   # pressurised steam curing — fastest
    CHEMICAL = 2   # curing compound (resin/wax spray) — no water needed


# (base_curing_days, water_per_m3_liters, curing_cost_per_m3_per_day ₹)
_CURING_PROPS = {
    CuringMethod.WATER:    (14.0, 30.0,  180.0),   # IS 456: min 14 days wet curing
    CuringMethod.STEAM:    ( 2.0,  2.0,  900.0),   # autoclave/boiler ₹900/m³/day
    CuringMethod.CHEMICAL: ( 8.0,  0.0,  280.0),   # compound spray ₹280/m³/day
}

CURING_LABELS = {
    CuringMethod.WATER:    "water",
    CuringMethod.STEAM:    "steam",
    CuringMethod.CHEMICAL: "chemical",
}


# ─────────────────────────────────────────────────────────────
#  DATA CLASS  (no curing_method field — evaluated for all 3)
# ─────────────────────────────────────────────────────────────

@dataclass
class YardScenario:
    num_elements:           int   = 50
    element_complexity:     float = 4.0      # 1-10
    temperature:            float = 32.0     # °C — typical Indian site
    humidity:               float = 65.0     # %
    yard_area_m2:           float = 600.0    # m²
    equipment_availability: float = 0.75     # 0-1
    water_budget_liters:    float = 40000.0  # litres
    concrete_m3:            float = 200.0
    material_unit_cost:     float = 6500.0   # ₹/m³ (M35 concrete)
    overhead_pct:           float = 0.18     # 18% — typical India

    def to_feature_vector(self, curing_method: int) -> np.ndarray:
        return np.array([
            self.num_elements,
            self.element_complexity,
            self.temperature,
            self.humidity,
            self.yard_area_m2,
            self.equipment_availability,
            self.water_budget_liters,
            float(curing_method),           # injected per-method at predict time
            self.concrete_m3,
            self.material_unit_cost,
            self.overhead_pct,
        ], dtype=float)


# ─────────────────────────────────────────────────────────────
#  PHYSICS-BASED GROUND TRUTH  (INR cost model)
# ─────────────────────────────────────────────────────────────

_EQUIPMENT_DAY_COST = 18000.0   # ₹/day — crane + batching plant + vibrators


def _ground_truth_for_method(s: YardScenario, cm: CuringMethod):
    base_curing_days, water_per_m3, curing_cost_rate = _CURING_PROPS[cm]

    # ── Concurrent casting slots ──────────────────────────────
    area_per_element = 5.0 + 2.0 * s.element_complexity
    concurrent_slots = max(1, int(s.yard_area_m2 / area_per_element))

    # ── Daily production rate ─────────────────────────────────
    base_rate   = s.equipment_availability * 2.5
    complex_pen = 1.0 + (s.element_complexity - 1) * 0.18
    eff_rate    = max(0.1, min(base_rate / complex_pen, concurrent_slots))

    temp_factor  = 1.0 - 0.008 * max(0, abs(s.temperature - 28))
    humid_factor = 1.0 - 0.004 * max(0, s.humidity - 65)
    eff_rate    *= max(0.45, temp_factor) * max(0.55, humid_factor)

    production_days = s.num_elements / eff_rate

    # ── Curing days (env-adjusted) ────────────────────────────
    env_factor  = 1.0 - 0.012 * max(0, s.temperature - 20) + 0.006 * max(0, 60 - s.humidity)
    curing_days = base_curing_days * max(0.4, env_factor)

    # Water budget check for water curing — fall back to chemical if insufficient
    water_needed = s.concrete_m3 * water_per_m3
    if cm == CuringMethod.WATER and water_needed > s.water_budget_liters:
        fb_days, _, fb_rate = _CURING_PROPS[CuringMethod.CHEMICAL]
        curing_days      = fb_days * max(0.4, env_factor)
        curing_cost_rate = fb_rate

    total_days = production_days + curing_days

    # ── Cost ₹ INR (material + equipment + curing — no labour) ──
    material_cost  = s.concrete_m3 * s.material_unit_cost
    equipment_cost = s.equipment_availability * _EQUIPMENT_DAY_COST * total_days
    curing_cost    = s.concrete_m3 * curing_cost_rate * curing_days
    direct_cost    = material_cost + equipment_cost + curing_cost
    total_cost     = direct_cost * (1 + s.overhead_pct)

    return float(total_days), float(total_cost)


def _ground_truth(s: YardScenario):
    """Returns ground truth for all 3 curing methods."""
    return {
        CURING_LABELS[cm]: _ground_truth_for_method(s, cm)
        for cm in CuringMethod
    }


# ─────────────────────────────────────────────────────────────
#  SIGNAL SPACE  (curing_method still sampled internally)
# ─────────────────────────────────────────────────────────────

SIGNAL_RANGES = {
    "num_elements":           (5,      300),
    "element_complexity":     (1.0,    10.0),
    "temperature":            (10.0,   45.0),
    "humidity":               (20.0,   95.0),
    "yard_area_m2":           (100,    3000),
    "equipment_availability": (0.1,    1.0),
    "water_budget_liters":    (0,      80000),
    "concrete_m3":            (10,     1200),
    "material_unit_cost":     (5000,   9000),
    "overhead_pct":           (0.10,   0.30),
}

_INT_SIGNALS = {"num_elements"}


def _sample_signals(n_samples=3000, seed=42):
    """Sample across all signals + all 3 curing methods."""
    rng = np.random.default_rng(seed)
    X, y_time, y_cost = [], [], []
    for _ in range(n_samples):
        vals = {
            k: int(round(rng.uniform(lo, hi))) if k in _INT_SIGNALS
            else float(rng.uniform(lo, hi))
            for k, (lo, hi) in SIGNAL_RANGES.items()
        }
        s = YardScenario(**vals)
        # Sample across all curing methods
        for cm in CuringMethod:
            t, c = _ground_truth_for_method(s, cm)
            X.append(s.to_feature_vector(cm.value))
            y_time.append(t * rng.uniform(0.97, 1.03))
            y_cost.append(c * rng.uniform(0.97, 1.03))
    return np.array(X), np.array(y_time), np.array(y_cost)


# ─────────────────────────────────────────────────────────────
#  PURE NUMPY ML STACK
# ─────────────────────────────────────────────────────────────

class StandardScaler:
    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_  = np.where(X.std(axis=0) == 0, 1.0, X.std(axis=0))
        return self
    def transform(self, X):     return (X - self.mean_) / self.std_
    def fit_transform(self, X): return self.fit(X).transform(X)


class PolynomialFeatures:
    def __init__(self, degree=2): self.degree = degree
    def fit(self, X):
        self._n = X.shape[1]; return self
    def transform(self, X):
        cross = [
            (X[:, i] * X[:, j]).reshape(-1, 1)
            for i in range(X.shape[1]) for j in range(i + 1, X.shape[1])
        ]
        return np.hstack([X, X**2] + cross)
    def fit_transform(self, X): return self.fit(X).transform(X)


class RidgeRegression:
    def __init__(self, alpha=1.0): self.alpha = alpha
    def fit(self, X, y):
        Xb = np.hstack([X, np.ones((len(X), 1))])
        reg = self.alpha * np.eye(Xb.shape[1]); reg[-1, -1] = 0.0
        self.w_ = np.linalg.solve(Xb.T @ Xb + reg, Xb.T @ y)
        return self
    def predict(self, X):
        return np.hstack([X, np.ones((len(X), 1))]) @ self.w_


class PolyRidgePipeline:
    """StandardScaler → PolynomialFeatures → RidgeRegression on log1p(y)."""
    def __init__(self, degree=2, alpha=50.0):
        self.scaler = StandardScaler()
        self.poly   = PolynomialFeatures(degree)
        self.ridge  = RidgeRegression(alpha)
    def fit(self, X, y):
        Xp = self.poly.fit_transform(self.scaler.fit_transform(X))
        self.ridge.fit(Xp, np.log1p(y))
        return self
    def predict(self, X):
        Xp   = self.poly.transform(self.scaler.transform(X))
        logp = self.ridge.predict(Xp)
        return np.expm1(np.clip(logp, 0, None))


def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot else 0.0


def kfold_cv_r2(factory, X, y, k=5, seed=0):
    rng   = np.random.default_rng(seed)
    folds = np.array_split(rng.permutation(len(y)), k)
    scores = []
    for i in range(k):
        val   = folds[i]
        train = np.concatenate([folds[j] for j in range(k) if j != i])
        m = factory(); m.fit(X[train], y[train])
        scores.append(r2_score(y[val], m.predict(X[val])))
    a = np.array(scores)
    return float(a.mean()), float(a.std())


# ─────────────────────────────────────────────────────────────
#  INVERSE SEARCH  (sweep: complexity × equipment per method)
# ─────────────────────────────────────────────────────────────

def _build_grid(base: YardScenario, cm: CuringMethod, step=4):
    comp_r  = np.linspace(*SIGNAL_RANGES["element_complexity"],     500)[::step]
    equip_r = np.linspace(*SIGNAL_RANGES["equipment_availability"],  500)[::step]
    rows, meta = [], []
    for cp in comp_r:
        for eq in equip_r:
            s = YardScenario(**{**asdict(base),
                                "element_complexity":     float(cp),
                                "equipment_availability": float(eq)})
            rows.append(s.to_feature_vector(cm.value))
            meta.append((round(float(cp), 2), round(float(eq), 3)))
    return np.array(rows), meta


def _find_best_for_cost(target_cost, base, cm, model_time, model_cost):
    X_grid, meta = _build_grid(base, cm)
    t_pred = model_time.predict(X_grid)
    c_pred = model_cost.predict(X_grid)
    idx    = int(np.argmin(np.abs(c_pred - target_cost)))
    return round(float(t_pred[idx]), 1), round(float(c_pred[idx]), 2), meta[idx]


def _find_best_for_time(target_days, base, cm, model_time, model_cost):
    X_grid, meta = _build_grid(base, cm)
    t_pred = model_time.predict(X_grid)
    c_pred = model_cost.predict(X_grid)
    idx    = int(np.argmin(np.abs(t_pred - target_days)))
    return round(float(t_pred[idx]), 1), round(float(c_pred[idx]), 2), meta[idx]


# ─────────────────────────────────────────────────────────────
#  FORMAT HELPER
# ─────────────────────────────────────────────────────────────

def _inr(amount: float) -> str:
    if amount >= 1e7:  return f"₹{amount/1e7:.2f} Cr"
    if amount >= 1e5:  return f"₹{amount/1e5:.2f} L"
    return f"₹{amount:,.0f}"


# ─────────────────────────────────────────────────────────────
#  PUBLIC SIMULATOR
# ─────────────────────────────────────────────────────────────

class PrecastYardSimulator:
    def __init__(self):
        self._model_time = None
        self._model_cost = None
        self._trained    = False
        self.default_scenario = YardScenario()

    def train(self, n_samples=3000, poly_degree=2, alpha=50.0, seed=42, verbose=True):
        if verbose:
            print("=" * 60)
            print("  PRECAST YARD SIMULATOR  (pure NumPy | ₹ INR)")
            print("  Curing methods: water | steam | chemical")
            print("=" * 60)
            print(f"  Sampling {n_samples} scenarios × 3 curing methods …")
        X, y_time, y_cost = _sample_signals(n_samples, seed)
        self._model_time = PolyRidgePipeline(poly_degree, alpha).fit(X, y_time)
        self._model_cost = PolyRidgePipeline(poly_degree, alpha).fit(X, y_cost)
        if verbose:
            f = lambda: PolyRidgePipeline(poly_degree, alpha)
            mt, st = kfold_cv_r2(f, X, y_time)
            mc, sc = kfold_cv_r2(f, X, y_cost)
            print(f"  Time model R² (5-fold): {mt:.4f} ± {st:.4f}")
            print(f"  Cost model R² (5-fold): {mc:.4f} ± {sc:.4f}")
            print("  Done.\n")
        self._trained = True
        return self

    def _check(self):
        if not self._trained:
            raise RuntimeError("Call .train() first.")

    # ── Evaluate all 3 curing methods directly ───────────────

    def evaluate(self, scenario=None) -> list[dict]:
        """Returns predicted time + cost for every curing method."""
        self._check()
        s = scenario or self.default_scenario
        results = []
        for cm in CuringMethod:
            x      = s.to_feature_vector(cm.value).reshape(1, -1)
            t_pred = round(float(self._model_time.predict(x)[0]), 1)
            c_pred = round(float(self._model_cost.predict(x)[0]), 2)
            t_gt, c_gt = _ground_truth_for_method(s, cm)
            results.append({
                "curing_method":    CURING_LABELS[cm],
                "predicted_days":   t_pred,
                "predicted_cost":   c_pred,
                "groundtruth_days": round(t_gt, 1),
                "groundtruth_cost": round(c_gt, 2),
            })
        return results

    # ── Given budget → time for each curing method ───────────

    def predict_time(self, budget: float, scenario=None, verbose=True) -> list[dict]:
        """Given a budget, returns predicted days for each curing method."""
        self._check()
        s = scenario or self.default_scenario
        results = []
        for cm in CuringMethod:
            t, c, (cp, eq) = _find_best_for_cost(budget, s, cm,
                                                   self._model_time, self._model_cost)
            results.append({
                "curing_method":              CURING_LABELS[cm],
                "predicted_days":             t,
                "predicted_cost":             c,
                "recommended_complexity":     cp,
                "recommended_equip":          eq,
            })
            if verbose:
                print(f"  [{CURING_LABELS[cm]:>8}]  {_inr(budget)}  →  {t} days  "
                      f"/ {_inr(c)}  (complexity={cp}, equip={eq:.0%})")
        return results

    # ── Given days → cost for each curing method ─────────────

    def predict_cost(self, days: float, scenario=None, verbose=True) -> list[dict]:
        """Given target days, returns predicted cost for each curing method."""
        self._check()
        s = scenario or self.default_scenario
        results = []
        for cm in CuringMethod:
            t, c, (cp, eq) = _find_best_for_time(days, s, cm,
                                                   self._model_time, self._model_cost)
            results.append({
                "curing_method":              CURING_LABELS[cm],
                "predicted_days":             t,
                "predicted_cost":             c,
                "recommended_complexity":     cp,
                "recommended_equip":          eq,
            })
            if verbose:
                print(f"  [{CURING_LABELS[cm]:>8}]  {days} days  →  {_inr(c)}  "
                      f"/ {t} days actual  (complexity={cp}, equip={eq:.0%})")
        return results

    # ── Sensitivity for a single signal ──────────────────────

    def sensitivity(self, signal, n_points=10, scenario=None) -> list[dict]:
        self._check()
        if signal not in SIGNAL_RANGES:
            raise ValueError(f"Unknown signal. Choose from: {list(SIGNAL_RANGES)}")
        lo, hi = SIGNAL_RANGES[signal]
        base   = asdict(scenario or self.default_scenario)
        out    = []
        for v in np.linspace(lo, hi, n_points):
            val  = int(round(v)) if signal in _INT_SIGNALS else float(v)
            row  = {signal: val}
            s    = YardScenario(**{**base, signal: val})
            for cm in CuringMethod:
                x = s.to_feature_vector(cm.value).reshape(1, -1)
                row[f"{CURING_LABELS[cm]}_days"] = round(float(self._model_time.predict(x)[0]), 1)
                row[f"{CURING_LABELS[cm]}_cost"] = round(float(self._model_cost.predict(x)[0]), 2)
            out.append(row)
        return out


# ─────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sim = PrecastYardSimulator()
    sim.train(n_samples=4000, verbose=True)

    print("--- Direct Evaluation (all curing methods) ---")
    for r in sim.evaluate():
        print(f"  [{r['curing_method']:>8}]  {r['predicted_days']} days / {_inr(r['predicted_cost'])}"
              f"  (true: {r['groundtruth_days']} days / {_inr(r['groundtruth_cost'])})")

    print("\n--- Budget ₹50L → Time per curing method ---")
    sim.predict_time(budget=50_00_000)

    print("\n--- 45 days → Cost per curing method ---")
    sim.predict_cost(days=45)

    print("\n--- Sensitivity: temperature (all methods) ---")
    print(f"  {'temp':>6}  {'water_d':>8}  {'steam_d':>8}  {'chem_d':>8}")
    for row in sim.sensitivity("temperature", n_points=6):
        print(f"  {row['temperature']:>6.1f}  {row['water_days']:>8.1f}"
              f"  {row['steam_days']:>8.1f}  {row['chemical_days']:>8.1f}")
