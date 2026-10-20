# Seed-bias results (pre-registered quantities)

θ_ref = {'r': 0.75, 'p_fp': 0.1, 'q': 0.5, 'a': 1}; δ = 0.01; 95% intervals are BCa over sequences (A5), unless marked.

## H1 — self-seed advantage at θ_ref (IDF1)

| Dataset | seqs | SA same detector | percentile CI | leave-one-seq-out | SA vs other detector | BCa low > δ |
|---|---|---|---|---|---|---|
| mot17 | 7 | +0.069 [0.060, 0.089] | [0.059, 0.086] | [0.063, 0.074] | +0.069 [0.058, 0.091] | True |
| dancetrack | 25 | +0.160 [0.148, 0.170] | [0.149, 0.171] | [0.158, 0.163] | +0.158 [0.144, 0.170] | True |
| fasttrack | 12 | +0.049 [0.042, 0.059] | [0.041, 0.058] | [0.046, 0.051] | +0.049 [0.041, 0.058] | True |

GT_true IDF1 per system:

| Dataset | yolo11x/botsort | yolo11x/bytetrack | yolo11x/ocsort | yolo11x/sort | yolo11n/botsort | yolo11n/bytetrack | yolo11n/ocsort | yolo11n/sort |
|---|---|---|---|---|---|---|---|---|
| mot17 | 0.509 | 0.524 | 0.473 | 0.535 | 0.481 | 0.480 | 0.444 | 0.468 |
| dancetrack | 0.472 | 0.458 | 0.440 | 0.353 | 0.390 | 0.377 | 0.350 | 0.270 |
| fasttrack | 0.607 | 0.623 | 0.530 | 0.608 | 0.439 | 0.456 | 0.318 | 0.482 |

### SA(A, B) at θ_ref (rows: seed A; cols: evaluated B)

**mot17**

| A \ B | x/botsort | x/bytetrack | x/ocsort | x/sort | n/botsort | n/bytetrack | n/ocsort | n/sort |
|---|---|---|---|---|---|---|---|---|
| yolo11x/botsort | +0.000 | +0.058 | +0.051 | +0.063 | +0.044 | +0.072 | +0.061 | +0.055 |
| yolo11x/bytetrack | +0.050 | +0.000 | +0.068 | +0.080 | +0.067 | +0.081 | +0.086 | +0.074 |
| yolo11x/ocsort | +0.056 | +0.082 | +0.000 | +0.084 | +0.059 | +0.077 | +0.056 | +0.068 |
| yolo11x/sort | +0.067 | +0.085 | +0.083 | +0.000 | +0.074 | +0.095 | +0.092 | +0.049 |

**dancetrack**

| A \ B | x/botsort | x/bytetrack | x/ocsort | x/sort | n/botsort | n/bytetrack | n/ocsort | n/sort |
|---|---|---|---|---|---|---|---|---|
| yolo11x/botsort | +0.000 | +0.132 | +0.107 | +0.110 | +0.115 | +0.150 | +0.135 | +0.123 |
| yolo11x/bytetrack | +0.154 | +0.000 | +0.174 | +0.155 | +0.165 | +0.179 | +0.176 | +0.165 |
| yolo11x/ocsort | +0.130 | +0.173 | +0.000 | +0.128 | +0.132 | +0.162 | +0.133 | +0.134 |
| yolo11x/sort | +0.212 | +0.240 | +0.206 | +0.000 | +0.192 | +0.225 | +0.195 | +0.142 |

**fasttrack**

| A \ B | x/botsort | x/bytetrack | x/ocsort | x/sort | n/botsort | n/bytetrack | n/ocsort | n/sort |
|---|---|---|---|---|---|---|---|---|
| yolo11x/botsort | +0.000 | +0.029 | +0.023 | +0.039 | +0.026 | +0.038 | +0.042 | +0.037 |
| yolo11x/bytetrack | +0.027 | +0.000 | +0.037 | +0.054 | +0.042 | +0.042 | +0.054 | +0.052 |
| yolo11x/ocsort | +0.049 | +0.068 | +0.000 | +0.071 | +0.042 | +0.057 | +0.042 | +0.052 |
| yolo11x/sort | +0.055 | +0.074 | +0.060 | +0.000 | +0.061 | +0.073 | +0.073 | +0.051 |

## H1 sensitivity and diagnostics at θ_ref

| Dataset | SD over seeds | thr 0.4 | thr 0.6 | sort_all as seed | without SORT pairs | geometry same det a1/a0 | geometry other det a1/a0 | per-seq unweighted mean |
|---|---|---|---|---|---|---|---|---|
| mot17 | 0.0026 | +0.074 [0.066, 0.095] | +0.062 [0.055, 0.080] | +0.079 [0.070, 0.095] | +0.061 | +0.069/+0.069 | +0.069/+0.074 | +0.069 |
| dancetrack | 0.0047 | +0.166 [0.155, 0.176] | +0.151 [0.139, 0.159] | +0.173 [0.161, 0.183] | +0.145 | +0.160/+0.160 | +0.158/+0.158 | +0.158 |
| fasttrack | 0.0011 | +0.052 [0.044, 0.062] | +0.045 [0.039, 0.056] | +0.058 [0.050, 0.068] | +0.039 | +0.049/+0.049 | +0.049/+0.051 | +0.051 |

Per-class SA (FastTrack): bicycle +0.060, bus +0.021, car +0.045, motorbike +0.079, person +0.072, truck +0.025

Class confusion (FastTrack, share of seed boxes matching another class's GT; zero-GT units):

- person: share 0.000, seed boxes 338294, zero-GT units 2
- bus: share 0.012, seed boxes 68556, zero-GT units 1
- truck: share 0.139, seed boxes 46536, zero-GT units 1
- car: share 0.023, seed boxes 1265347, zero-GT units 0
- bicycle: share 0.000, seed boxes 30772, zero-GT units 6
- motorbike: share 0.105, seed boxes 4881, zero-GT units 7

A5 item 5 (share > 10%: truck, motorbike): FastTrack SA without them = +0.050 [0.042, 0.060]
A5 item 5 merged-vehicle sensitivity (car+bus+truck as one class): SA = +0.047 [0.038, 0.060]

Reviewer diagnostics (realised fix rate by episode size at θ_ref, nominal q = 0.5):

- mot17: 1: 0.50 (n=17700), 2: 0.48 (n=850), 3: 0.48 (n=350), 4: 0.48 (n=130), 5: 0.40 (n=10), 6: 0.40 (n=10), 7: 0.30 (n=10), 8+: 0.40 (n=10)
  - kept FP boxes carrying a real track's label (S_r): 0.671, 0.639, 0.583, 0.498, 0.406, 0.290
- dancetrack: 1: 0.50 (n=65420), 2: 0.49 (n=2170), 3: 0.49 (n=790), 4: 0.48 (n=390), 5: 0.47 (n=310), 6: 0.51 (n=190), 7: 0.56 (n=100), 8+: 0.46 (n=490)
  - kept FP boxes carrying a real track's label (S_r): 0.548, 0.516, 0.476, 0.410, 0.347, 0.299
- fasttrack: 1: 0.50 (n=26470), 2: 0.49 (n=810), 3: 0.52 (n=300), 4: 0.53 (n=150), 5: 0.63 (n=30), 6: 0.44 (n=50), 7: 0.50 (n=30), 8+: 0.50 (n=30)
  - kept FP boxes carrying a real track's label (S_r): 0.388, 0.346, 0.305, 0.255, 0.215, 0.189

## SA curves through θ_ref (one parameter at a time, a = 1)

- mot17: r=0: +0.155; r=0.25: +0.119; r=0.5: +0.091; r=0.75: +0.069; r=0.9: +0.058; r=1: +0.051
- mot17: q=0: +0.124; q=0.5: +0.069; q=0.9: +0.026; q=1: +0.015
- mot17: p_fp=0: +0.067; p_fp=0.1: +0.069; p_fp=0.25: +0.072; p_fp=0.5: +0.078
  - cells with BCa lower bound > 0: 190/192; > δ: 170/192 (descriptive, A6 item 7)
- dancetrack: r=0: +0.186; r=0.25: +0.177; r=0.5: +0.168; r=0.75: +0.160; r=0.9: +0.156; r=1: +0.153
- dancetrack: q=0: +0.327; q=0.5: +0.160; q=0.9: +0.033; q=1: +0.005
- dancetrack: p_fp=0: +0.158; p_fp=0.1: +0.160; p_fp=0.25: +0.163; p_fp=0.5: +0.167
  - cells with BCa lower bound > 0: 191/192; > δ: 161/192 (descriptive, A6 item 7)
- fasttrack: r=0: +0.136; r=0.25: +0.099; r=0.5: +0.071; r=0.75: +0.049; r=0.9: +0.038; r=1: +0.030
- fasttrack: q=0: +0.079; q=0.5: +0.049; q=0.9: +0.024; q=1: +0.018
- fasttrack: p_fp=0: +0.046; p_fp=0.1: +0.049; p_fp=0.25: +0.053; p_fp=0.5: +0.059
  - cells with BCa lower bound > 0: 190/192; > δ: 172/192 (descriptive, A6 item 7)

## Ranking (IDF1, 8 systems) at θ_ref

- mot17: τ-b mean 0.664; δ-margin flips mean 3.23; draws with ≥1 δ-margin flip 1.00; raw flips mean 4.70
- dancetrack: τ-b mean 0.748; δ-margin flips mean 3.52; draws with ≥1 δ-margin flip 1.00; raw flips mean 3.52
- fasttrack: τ-b mean 0.873; δ-margin flips mean 1.02; draws with ≥1 δ-margin flip 0.75; raw flips mean 1.77

## H2 — seed-correlated vs null errors (endpoint: a = 0, θ_ref)

| Dataset | units | τ_null − τ_seed (a=0) | flips_seed − flips_null (a=0) | τ_seed / τ_null (a=0) | τ_null − τ_seed (a=1) | null skip share fn/id/fp |
|---|---|---|---|---|---|---|
| mot17 | 7 | +0.198 [0.118, 0.350] | +2.35 [1.02, 4.08] | 0.657 / 0.855 | +0.191 [0.114, 0.345] | 0.000/0.009/0.000 |
| dancetrack | 25 | +0.227 [0.204, 0.284] | +3.17 [2.98, 3.97] | 0.741 / 0.968 | +0.220 [0.195, 0.280] | 0.000/0.002/0.123 |
| fasttrack | 55 | +0.104 [0.039, 0.161] | +1.05 [0.28, 2.00] | 0.870 / 0.973 | +0.100 [0.038, 0.157] | 0.000/0.001/0.139 |

H2 along r (a = 0): τ_null − τ_seed point estimates

- mot17: r=0: +0.220; r=0.25: +0.311; r=0.5: +0.259; r=0.75: +0.198; r=0.9: +0.164; r=1: +0.152
- dancetrack: r=0: +0.234; r=0.25: +0.248; r=0.5: +0.223; r=0.75: +0.227; r=0.9: +0.216; r=1: +0.207
- fasttrack: r=0: +0.171; r=0.25: +0.214; r=0.5: +0.171; r=0.75: +0.104; r=0.9: +0.089; r=1: +0.045

## H3 — protocols at θ_ref (IDF1 distortion D; costs relative to GT_true boxes)

**mot17**

| Protocol | D (4 seed systems) | D (8 systems) | D_P − D_P0 (4) | member SA vs YOLO11n | member SA vs held-out | cost verify | cost draw |
|---|---|---|---|---|---|---|---|
| P0 single seed | +0.042 [0.038, 0.053] | +0.029 [0.026, 0.036] | — | — | — | 0.56 | 0.38 |
| P2 consensus | +0.018 [0.010, 0.022] | +0.018 [0.014, 0.020] | -0.024 [-0.035, -0.017] | +0.016 [0.005, 0.022] | — | 0.75 | 0.40 |
| P2 consensus without botsort | +0.015 [0.007, 0.019] | +0.020 [0.012, 0.025] | -0.027 [-0.039, -0.019] | +0.010 [-0.001, 0.016] | -0.009 [-0.017, 0.004] | 0.75 | 0.37 |
| P2 consensus without bytetrack | +0.020 [0.014, 0.024] | +0.020 [0.016, 0.023] | -0.022 [-0.031, -0.012] | +0.017 [0.005, 0.023] | +0.026 [0.008, 0.037] | 0.71 | 0.40 |
| P2 consensus without ocsort | +0.018 [0.010, 0.023] | +0.019 [0.013, 0.027] | -0.024 [-0.036, -0.015] | +0.017 [0.010, 0.024] | +0.014 [-0.004, 0.047] | 0.75 | 0.38 |
| P2 consensus without sort | +0.021 [0.018, 0.024] | +0.020 [0.016, 0.021] | -0.021 [-0.036, -0.015] | +0.018 [0.004, 0.026] | +0.017 [-0.003, 0.032] | 0.61 | 0.39 |
| P1 union botsort+bytetrack | +0.030 [0.026, 0.038] | +0.023 [0.020, 0.030] | -0.012 [-0.015, -0.011] | +0.028 [0.022, 0.038] | — | 0.60 | 0.37 |
| P1 union botsort+ocsort | +0.034 [0.027, 0.047] | +0.024 [0.020, 0.032] | -0.008 [-0.012, -0.002] | +0.033 [0.014, 0.048] | — | 0.53 | 0.39 |
| P1 union botsort+sort | +0.035 [0.029, 0.048] | +0.026 [0.022, 0.035] | -0.007 [-0.012, 0.001] | +0.035 [0.029, 0.048] | — | 0.71 | 0.30 |
| P1 union bytetrack+ocsort | +0.040 [0.036, 0.045] | +0.028 [0.025, 0.030] | -0.002 [-0.010, 0.004] | +0.040 [0.023, 0.050] | — | 0.60 | 0.37 |
| P1 union bytetrack+sort | +0.034 [0.023, 0.050] | +0.028 [0.021, 0.038] | -0.008 [-0.019, 0.009] | +0.046 [0.036, 0.065] | — | 0.75 | 0.29 |
| P1 union ocsort+sort | +0.044 [0.029, 0.055] | +0.030 [0.019, 0.040] | +0.002 [-0.009, 0.008] | +0.037 [0.025, 0.050] | — | 0.70 | 0.30 |
| P1 union botsort+bytetrack+ocsort | +0.030 [0.025, 0.039] | +0.023 [0.020, 0.027] | -0.012 [-0.017, -0.009] | +0.022 [0.011, 0.029] | — | 0.61 | 0.36 |
| P1 union botsort+bytetrack+sort | +0.033 [0.027, 0.045] | +0.028 [0.023, 0.039] | -0.009 [-0.016, -0.001] | +0.024 [0.017, 0.030] | — | 0.75 | 0.29 |
| P1 union botsort+ocsort+sort | +0.032 [0.025, 0.045] | +0.026 [0.021, 0.035] | -0.010 [-0.016, -0.003] | +0.025 [0.017, 0.038] | — | 0.71 | 0.30 |
| P1 union bytetrack+ocsort+sort | +0.034 [0.024, 0.048] | +0.027 [0.021, 0.036] | -0.008 [-0.020, 0.009] | +0.028 [0.016, 0.033] | — | 0.75 | 0.29 |

P3 bracket: width +0.080 [0.073, 0.100]; cost verify 2.24, draw 1.52; coverage per system: botsort 0.00 [0.00, 0.00], bytetrack 0.00 [0.00, 0.20], ocsort 0.00 [0.00, 0.00], sort 0.00 [0.00, 0.10]

**dancetrack**

| Protocol | D (4 seed systems) | D (8 systems) | D_P − D_P0 (4) | member SA vs YOLO11n | member SA vs held-out | cost verify | cost draw |
|---|---|---|---|---|---|---|---|
| P0 single seed | +0.091 [0.083, 0.097] | +0.056 [0.051, 0.060] | — | — | — | 0.88 | 0.13 |
| P2 consensus | +0.032 [0.026, 0.038] | +0.031 [0.025, 0.034] | -0.059 [-0.066, -0.051] | +0.028 [0.021, 0.035] | — | 1.01 | 0.12 |
| P2 consensus without botsort | +0.085 [0.073, 0.098] | +0.064 [0.055, 0.073] | -0.006 [-0.015, 0.006] | +0.008 [-0.009, 0.017] | +0.048 [0.035, 0.064] | 1.01 | 0.11 |
| P2 consensus without bytetrack | +0.083 [0.072, 0.096] | +0.061 [0.054, 0.070] | -0.007 [-0.017, 0.003] | +0.018 [0.002, 0.027] | +0.086 [0.070, 0.107] | 0.97 | 0.12 |
| P2 consensus without ocsort | +0.040 [0.031, 0.048] | +0.033 [0.027, 0.039] | -0.051 [-0.061, -0.045] | +0.024 [0.011, 0.033] | +0.020 [0.004, 0.038] | 1.01 | 0.10 |
| P2 consensus without sort | +0.033 [0.023, 0.041] | +0.031 [0.024, 0.037] | -0.058 [-0.069, -0.050] | +0.008 [-0.002, 0.018] | -0.035 [-0.049, -0.014] | 0.96 | 0.11 |
| P1 union botsort+bytetrack | +0.067 [0.058, 0.079] | +0.045 [0.039, 0.052] | -0.024 [-0.030, -0.014] | +0.066 [0.054, 0.080] | — | 0.96 | 0.09 |
| P1 union botsort+ocsort | +0.071 [0.060, 0.083] | +0.047 [0.040, 0.054] | -0.020 [-0.028, -0.010] | +0.079 [0.064, 0.096] | — | 0.89 | 0.11 |
| P1 union botsort+sort | +0.071 [0.061, 0.081] | +0.049 [0.042, 0.056] | -0.020 [-0.028, -0.015] | +0.085 [0.071, 0.098] | — | 0.97 | 0.09 |
| P1 union bytetrack+ocsort | +0.084 [0.070, 0.101] | +0.050 [0.042, 0.057] | -0.007 [-0.021, 0.007] | +0.083 [0.070, 0.105] | — | 0.96 | 0.09 |
| P1 union bytetrack+sort | +0.090 [0.075, 0.106] | +0.054 [0.045, 0.061] | -0.001 [-0.016, 0.013] | +0.100 [0.086, 0.115] | — | 1.01 | 0.08 |
| P1 union ocsort+sort | +0.091 [0.080, 0.103] | +0.057 [0.052, 0.063] | +0.000 [-0.009, 0.011] | +0.089 [0.079, 0.098] | — | 0.95 | 0.10 |
| P1 union botsort+bytetrack+ocsort | +0.069 [0.060, 0.080] | +0.047 [0.041, 0.054] | -0.022 [-0.028, -0.013] | +0.054 [0.043, 0.066] | — | 0.96 | 0.09 |
| P1 union botsort+bytetrack+sort | +0.069 [0.061, 0.079] | +0.048 [0.041, 0.053] | -0.021 [-0.027, -0.016] | +0.053 [0.041, 0.062] | — | 1.01 | 0.08 |
| P1 union botsort+ocsort+sort | +0.070 [0.060, 0.080] | +0.048 [0.041, 0.054] | -0.021 [-0.027, -0.014] | +0.064 [0.050, 0.075] | — | 0.97 | 0.09 |
| P1 union bytetrack+ocsort+sort | +0.085 [0.070, 0.096] | +0.052 [0.043, 0.058] | -0.006 [-0.022, 0.006] | +0.063 [0.053, 0.071] | — | 1.01 | 0.08 |

P3 bracket: width +0.176 [0.161, 0.186]; cost verify 3.54, draw 0.50; coverage per system: botsort 0.00 [0.00, 0.00], bytetrack 0.00 [0.00, 0.00], ocsort 0.00 [0.00, 0.00], sort 0.00 [0.00, 0.00]

**fasttrack**

| Protocol | D (4 seed systems) | D (8 systems) | D_P − D_P0 (4) | member SA vs YOLO11n | member SA vs held-out | cost verify | cost draw |
|---|---|---|---|---|---|---|---|
| P0 single seed | +0.031 [0.028, 0.035] | +0.021 [0.018, 0.023] | — | — | — | 0.58 | 0.36 |
| P2 consensus | +0.014 [0.009, 0.017] | +0.013 [0.009, 0.015] | -0.018 [-0.024, -0.014] | +0.012 [0.008, 0.018] | — | 0.77 | 0.38 |
| P2 consensus without botsort | +0.013 [0.007, 0.019] | +0.012 [0.009, 0.016] | -0.018 [-0.026, -0.013] | +0.009 [0.004, 0.016] | -0.002 [-0.008, 0.004] | 0.77 | 0.35 |
| P2 consensus without bytetrack | +0.012 [0.008, 0.015] | +0.011 [0.008, 0.014] | -0.020 [-0.026, -0.016] | +0.014 [0.008, 0.020] | +0.020 [0.007, 0.032] | 0.73 | 0.37 |
| P2 consensus without ocsort | +0.010 [0.007, 0.013] | +0.012 [0.008, 0.013] | -0.021 [-0.029, -0.018] | +0.012 [0.007, 0.021] | +0.003 [-0.007, 0.030] | 0.77 | 0.36 |
| P2 consensus without sort | +0.016 [0.011, 0.020] | +0.013 [0.009, 0.015] | -0.016 [-0.022, -0.011] | +0.015 [0.010, 0.022] | +0.018 [0.007, 0.030] | 0.63 | 0.36 |
| P1 union botsort+bytetrack | +0.021 [0.016, 0.024] | +0.015 [0.012, 0.017] | -0.011 [-0.015, -0.008] | +0.018 [0.008, 0.027] | — | 0.62 | 0.33 |
| P1 union botsort+ocsort | +0.022 [0.018, 0.029] | +0.016 [0.013, 0.020] | -0.010 [-0.013, -0.004] | +0.025 [0.019, 0.034] | — | 0.56 | 0.36 |
| P1 union botsort+sort | +0.021 [0.015, 0.027] | +0.019 [0.014, 0.022] | -0.011 [-0.016, -0.006] | +0.032 [0.025, 0.040] | — | 0.73 | 0.28 |
| P1 union bytetrack+ocsort | +0.028 [0.022, 0.035] | +0.019 [0.016, 0.023] | -0.004 [-0.009, 0.001] | +0.027 [0.023, 0.032] | — | 0.62 | 0.33 |
| P1 union bytetrack+sort | +0.018 [0.012, 0.034] | +0.017 [0.014, 0.024] | -0.014 [-0.019, -0.002] | +0.032 [0.025, 0.042] | — | 0.77 | 0.26 |
| P1 union ocsort+sort | +0.044 [0.037, 0.053] | +0.029 [0.023, 0.034] | +0.013 [0.006, 0.020] | +0.031 [0.023, 0.038] | — | 0.71 | 0.29 |
| P1 union botsort+bytetrack+ocsort | +0.021 [0.016, 0.026] | +0.015 [0.012, 0.017] | -0.010 [-0.017, -0.006] | +0.017 [0.009, 0.025] | — | 0.63 | 0.32 |
| P1 union botsort+bytetrack+sort | +0.020 [0.014, 0.027] | +0.017 [0.013, 0.021] | -0.012 [-0.017, -0.007] | +0.017 [0.010, 0.025] | — | 0.77 | 0.26 |
| P1 union botsort+ocsort+sort | +0.020 [0.013, 0.027] | +0.018 [0.014, 0.022] | -0.012 [-0.017, -0.007] | +0.025 [0.018, 0.030] | — | 0.73 | 0.28 |
| P1 union bytetrack+ocsort+sort | +0.017 [0.011, 0.036] | +0.017 [0.013, 0.025] | -0.014 [-0.020, 0.000] | +0.022 [0.018, 0.027] | — | 0.77 | 0.26 |

P3 bracket: width +0.061 [0.053, 0.071]; cost verify 2.32, draw 1.42; coverage per system: botsort 0.00 [0.00, 0.00], bytetrack 0.00 [0.00, 0.20], ocsort 0.00 [0.00, 0.00], sort 0.00 [0.00, 0.00]

## Secondary metrics at θ_ref (TrackEval, mean over seeds; SA analogue = own − others on GT_A minus on GT_true)

- mot17 IDF1: mean SA +0.0688
- mot17 HOTA50: mean SA +0.0577
- mot17 AssA50: mean SA +0.0964
- mot17 DetA50: mean SA +0.0249
- mot17 MOTA: mean SA +0.0350
- dancetrack IDF1: mean SA +0.1600
- dancetrack HOTA50: mean SA +0.1402
- dancetrack AssA50: mean SA +0.1955
- dancetrack DetA50: mean SA +0.0303
- dancetrack MOTA: mean SA +0.0312
- fasttrack IDF1: mean SA +0.0488
- fasttrack HOTA50: mean SA +0.0424
- fasttrack AssA50: mean SA +0.0598
- fasttrack DetA50: mean SA +0.0289
- fasttrack MOTA: mean SA +0.0383

## Stop rule (A5 item 3)

Upper BCa bound < δ for every θ with r ≥ 0.5 in all datasets: False → stop rule not triggered.

Provenance: mot17 commit b2ad9f3 run 14109e6cd127 dirty=False, dancetrack commit b2ad9f3 run 1e3907710f75 dirty=False, fasttrack commit b2ad9f3 run 182f706e72b3 dirty=False
