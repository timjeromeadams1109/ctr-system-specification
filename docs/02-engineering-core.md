# Section 2 — Deterministic Engineering Core

## 2.1 Overturning Moment Extraction

### 2.1.1 Single-Story Shear Wall Overturning

For a single-story shear wall segment subjected to lateral load:

$$M_{OT} = V \times h$$

Where:
- $M_{OT}$ = Overturning moment (ft-lb or in-lb)
- $V$ = Shear force applied to wall (lb)
- $h$ = Wall height from point of load application to base (ft)

### 2.1.2 Multi-Story Cumulative Overturning

For multi-story structures, overturning moment at level $n$ from the base:

$$M_{OT,n} = \sum_{i=n}^{roof} V_i \times (H_i - H_n)$$

Where:
- $M_{OT,n}$ = Overturning moment at level $n$ (ft-lb)
- $V_i$ = Story shear at level $i$ (lb)
- $H_i$ = Height of level $i$ from base (ft)
- $H_n$ = Height of level $n$ from base (ft)

### 2.1.3 Code-Defined Overturning per ASCE 7-22 §12.8.5

$$M_x = \sum_{i=x}^{n} F_i (h_i - h_x)$$

---

## 2.2 Tension Demand Per Level

### 2.2.1 Basic Tension from Overturning

$$T = \frac{M_{OT}}{d} - D_{resist}$$

Where:
- $T$ = Net tension demand (lb)
- $M_{OT}$ = Overturning moment (ft-lb)
- $d$ = Moment arm = distance between holdowns (ft)
- $D_{resist}$ = Resisting dead load (lb)

### 2.2.2 Resisting Dead Load Calculation

$$D_{resist} = 0.6 \times D_{tributary} \quad \text{(ASD per ASCE 7-22)}$$
$$D_{resist} = 0.9 \times D_{tributary} \quad \text{(LRFD per ASCE 7-22)}$$

---

## 2.3 Cumulative Axial Force Stacking

$$T_{total}(n) = \sum_{i=n}^{roof} T_{level}(i)$$

Where:
- $T_{total}(n)$ = Cumulative tension at level $n$ (lb)
- $T_{level}(i)$ = Net tension demand at level $i$ (lb)
- Summation from level $n$ down to roof (accumulating downward)

---

## 2.4 ASD vs LRFD Handling

### 2.4.1 Design Methodology Comparison

| Parameter | ASD | LRFD |
|-----------|-----|------|
| Load Factor (Dead) | 1.0 | 1.2 (typical) |
| Load Factor (Seismic E) | 0.7 | 1.0 |
| Resistance Factor | 1.0 | φ = 0.9 (steel tension) |
| Safety Factor | Ω = 2.0 (steel tension) | N/A |
| Dead Load Resist (uplift) | 0.6D | 0.9D |

### 2.4.2 Rod Capacity Equations

**ASD Allowable Tension:**
$$T_{allowable,ASD} = \frac{0.75 \times F_u \times A_s}{\Omega} = \frac{0.75 \times F_u \times A_s}{2.0}$$

**LRFD Design Strength:**
$$\phi T_n = \phi \times 0.75 \times F_u \times A_s = 0.75 \times 0.75 \times F_u \times A_s$$

### 2.4.3 Tensile Stress Area

$$A_s = \frac{\pi}{4} \left( d - \frac{0.9743}{n} \right)^2$$

**Standard Tensile Stress Areas:**

| Diameter (in) | Threads/in | $A_s$ (in²) |
|---------------|------------|-------------|
| 5/8 | 11 | 0.226 |
| 3/4 | 10 | 0.334 |
| 7/8 | 9 | 0.462 |
| 1 | 8 | 0.606 |
| 1-1/8 | 7 | 0.763 |
| 1-1/4 | 7 | 0.969 |
| 1-3/8 | 6 | 1.155 |
| 1-1/2 | 6 | 1.405 |

---

## 2.5 Load Combinations per ASCE 7-22

### 2.5.1 ASD Uplift Combinations

| Combo | Expression | Governing For |
|-------|------------|---------------|
| 7 | D + 0.7E | Seismic uplift |
| 10 | 0.6D + 0.7E | Maximum seismic uplift |
| 9 | 0.6D + 0.6W | Maximum wind uplift |

### 2.5.2 LRFD Uplift Combinations

| Combo | Expression | Governing For |
|-------|------------|---------------|
| 5 | 1.2D + E + L | Seismic with gravity |
| 7 | 0.9D + E | Maximum seismic uplift |
| 6 | 0.9D + W | Maximum wind uplift |

---

## 2.6 Wood Shrinkage Accumulation Model

### 2.6.1 Shrinkage Formula

$$\Delta_{shrinkage} = t \times S \times \Delta MC$$

Where:
- $\Delta_{shrinkage}$ = Dimensional change (inches)
- $t$ = Original thickness perpendicular to grain (inches)
- $S$ = Shrinkage coefficient (in/in per % MC change)
- $\Delta MC$ = Moisture content change (%)

### 2.6.2 Shrinkage Coefficients by Species

| Species | Tangential $S_T$ | Radial $S_R$ | Average $S_{avg}$ |
|---------|------------------|--------------|-------------------|
| Douglas Fir-Larch | 0.00267 | 0.00158 | 0.00213 |
| Southern Pine | 0.00262 | 0.00164 | 0.00213 |
| Spruce-Pine-Fir | 0.00236 | 0.00136 | 0.00186 |
| Hem-Fir | 0.00249 | 0.00143 | 0.00196 |

### 2.6.3 Cumulative Shrinkage

$$\Delta_{total} = \sum_{level=1}^{N} \Delta_{level}$$

---

## 2.7 Rod Elongation Equation

$$\Delta_{rod} = \frac{T \times L}{A_s \times E}$$

Where:
- $\Delta_{rod}$ = Rod elongation (inches)
- $T$ = Tension force (lbs)
- $L$ = Rod length (inches)
- $A_s$ = Tensile stress area (in²)
- $E$ = Modulus of elasticity = 29,000,000 psi (steel)

---

## 2.8 Utilization Ratio Computation

$$\text{Utilization Ratio} = \frac{T_{demand}}{T_{allowable}}$$

### Acceptance Criteria

| Utilization | Status | Action |
|-------------|--------|--------|
| ≤ 0.90 | Acceptable | No action required |
| 0.90 - 1.00 | Marginal | Consider upsizing |
| > 1.00 | Failing | Must upsize rod |

---

## 2.9 Shrinkage Device Selection

### Required Capacity

$$\text{Required Capacity} = \Delta_{shrinkage} - \Delta_{rod}$$

### Simpson Strong-Tie ATUD Capacities

| Model | Rod Diameter | Capacity (in) | Allowable Load ASD (lb) |
|-------|--------------|---------------|-------------------------|
| ATUD5 | 5/8" - 1-1/4" | 1/2" | 14,900 - 55,000 |
| ATUD7 | 5/8" - 7/8" | 7/8" | 14,900 - 26,500 |
| ATUD9 | 5/8" - 1-1/4" | 1-3/8" | 14,900 - 55,000 |
