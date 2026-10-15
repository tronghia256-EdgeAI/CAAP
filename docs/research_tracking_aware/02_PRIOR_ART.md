# Prior art, verification status and novelty boundary

**Search cut-off: 15 October 2026.** Entries use primary publisher/proceedings,
author/institutional copies and author preprints. A preprint is labelled as such.
No speedups from these papers are treated as measurements of CAAP.

## Search and evidence policy

Queries combined MOT/active perception/track-guided detection with covariance,
identity ambiguity, scheduling, budget, crop, tiling, resolution and edge. Search
families included CVF/NeurIPS/IEEE, arXiv, RTSS/ECRTS and journal publishers.
Foundational work before 2022 is included where it directly removes a novelty claim.
Coverage is targeted, not proof of exhaustive absence through October 2026.

**FULL/SECTIONS** means relevant primary text was inspected, not every experiment
independently reproduced. **ABSTRACT** limits conclusions to that text.
**METADATA** is bibliographic verification only. Missing hardware/code is not evidence
that a paper cannot run on that hardware. Hardware below means reported evaluation
hardware, not a theorem about minimum requirements.

## P01 — DriftSched (2026): closest threat

**DriftSched: Covariance-Guided Adaptive Detection Scheduling for Efficient Multi-Object Tracking.**
Yuewen Xu, Zhihua Jiang, Xuanzhe Li, Naim Dahnoun. **MECO 2026**.
[Publisher record](https://ieeexplore.ieee.org/abstract/document/11579050),
[DOI](https://doi.org/10.1109/MECO70748.2026.11579050),
[publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1109/MECO70748.2026.11579050).

- **Verified:** DOI/authors/venue/date; indexed publisher **ABSTRACT**, not full text.
- **Mechanism:** per-track detector allocation using prediction covariance and predicted-overlap ambiguity; rate-matched controls.
- **Evaluation:** MOT17, DanceTrack validation; TI AM62A edge experiment. Exact CPU/NPU execution split is unverified.
- **Overlap:** directly occupies the generic identity-risk/budget scheduling claim.
- **Open:** actual spatial inference mechanism, resolution actions, runtime accounting, code and parameter availability. Obtain full text before claiming the proposed distinction. Do not confuse this paper with the unrelated LLM scheduler also named DriftSched.

## P02 — RT-MOT (2022)

**RT-MOT: Confidence-Aware Real-Time Scheduling Framework for Multi-Object Tracking Tasks.**
Donghwa Kang, Seunghoon Lee, Hoon Sung Chwa, Seung-Hwan Bae, Chang Mook Kang,
Jinkyu Lee, Hyeongboo Baek. **IEEE RTSS 2022**, pp. 318–330.
[Author PDF](https://rtclskku.github.io/website/papers/IC202212KLC.pdf),
[DOI](https://doi.org/10.1109/RTSS55097.2022.00035),
[official conference program](https://2022.rtss.org/conference-program/).

- **SECTIONS verified:** confidence predicts benefits of detector/association workload pairs; deadline-aware multicamera scheduling.
- **Hardware/protocol:** Xeon Silver 4215R, V100; Waymo; YOLOv5 672/256 and SORT/DeepSORT workload alternatives, tracking accuracy and timing.
- **Overlap:** tracking confidence controlling resolution/workload under a budget predates this proposal.
- **Boundary:** frame/task choices differ from the proposed region-action experiment; CPU transfer and identity-specific incremental benefit are not established by merely citing this difference. Its timing analysis is stronger than an empirical p95 claim.

## P03 — CA-MOT (2025)

**Real-time scheduling for multi-object tracking tasks in regions with different criticalities.**
Donghwa Kang, Jinkyu Lee, Hyeongboo Baek. **Journal of Systems Architecture**, 2025,
article 103349. [Publisher](https://www.sciencedirect.com/science/article/pii/S1383762125000219),
[DOI](https://doi.org/10.1016/j.sysarc.2025.103349),
[author PDF](https://rtcl-yonsei.github.io/website/papers/IJ202503KLB.pdf).

- **SECTIONS verified:** low/middle/high detector/association workloads; safety-region criticality and aging; EDF-based resource scheduling.
- **Hardware/data:** Jetson Xavier MAXN, GPU-enabled; KITTI; multiple detector architectures, region accuracy and timing.
- **Overlap:** region-prioritized, age-aware budgeted MOT is already studied.
- **Limitation for transfer:** criticality is not the same target as identity preservation; its sensor inputs and hardware differ. Neither difference alone proves a novel algorithm.

## P04 — SAHI (2022)

**Slicing Aided Hyper Inference and Fine-Tuning for Small Object Detection.**
Fatih Cagatay Akyon, Sinan Onur Altinuc, Alptekin Temizel. **IEEE ICIP 2022**.
[Publisher/DOI](https://doi.org/10.1109/ICIP46576.2022.9897990),
[author preprint](https://arxiv.org/abs/2202.06934),
[author implementation](https://github.com/obss/sahi).

- **ABSTRACT verified:** generic sliced inference/fine-tuning, including detector-agnostic use without retraining.
- **Data/protocol:** VisDrone and xView detection AP; no MOT identity endpoint established by this source.
- **Hardware:** exact experimental device not verified in this review; remeasure locally.
- **Overlap:** tiling, coordinate remapping and duplicate fusion are established. Use fixed slicing as an essential control; adding a tracker does not make slicing novel. Slice count and call overhead can erase savings.

## P05 — QueryDet (2022)

**QueryDet: Cascaded Sparse Query for Accelerating High-Resolution Small Object Detection.**
Chenhongyi Yang, Zehao Huang, Naiyan Wang. **CVPR 2022**.
[Official paper](https://openaccess.thecvf.com/content/CVPR2022/html/Yang_QueryDet_Cascaded_Sparse_Query_for_Accelerating_High-Resolution_Small_Object_Detection_CVPR_2022_paper.html),
[PDF](https://openaccess.thecvf.com/content/CVPR2022/papers/Yang_QueryDet_Cascaded_Sparse_Query_for_Accelerating_High-Resolution_Small_Object_Detection_CVPR_2022_paper.pdf).

- **SECTIONS verified:** coarse low-resolution queries activate sparse high-resolution feature computation.
- **Hardware/data:** NVIDIA 2080 Ti referenced in speed comparisons; COCO/VisDrone, detection AP and speed. No CPU-only reproduction here.
- **Overlap:** spending high-resolution compute only near promising small objects is established.
- **Boundary:** feature-level sparse convolution needs detector changes; the proposed image-crop wrapper is simpler but simplicity is not novelty. Identity-conditioned action value must show an additional benefit.

## P06 — RTScale (2022)

**RTScale: Sensitivity-Aware Adaptive Image Scaling for Real-Time Object Detection.**
Seonyeong Heo, Shinnung Jeong, Hanjun Kim. **ECRTS 2022**.
[Official proceedings](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECRTS.2022.2),
[DOI](https://doi.org/10.4230/LIPIcs.ECRTS.2022.2).

- **SECTIONS verified:** predicted accuracy sensitivity and time constraints determine per-image scales across streams.
- **Hardware/data:** two Xeon Silver 4210 CPUs, up to three RTX 2080 Ti GPUs; KITTI MOT/BDD100K MOT imagery; detector accuracy/latency, not identity-driven selection.
- **Overlap:** budget-constrained resolution allocation and estimating action sensitivity are not new abstractions.
- **Boundary:** a useful control family for resolution scheduling. Its detection benchmark must not be represented as an AssA/IDF1 result.

## P07 — AttTrack (2023)

**AttTrack: Online Deep Attention Transfer for Multi-Object Tracking.**
Keivan Nalaie, Rong Zheng. **WACV 2023**.
[Official author paper](https://openaccess.thecvf.com/content/WACV2023/papers/Nalaie_AttTrack_Online_Deep_Attention_Transfer_for_Multi-Object_Tracking_WACV_2023_paper.pdf),
[preprint](https://arxiv.org/abs/2210.08648).

- **ABSTRACT/introduction verified:** interleaved teacher/student execution and transferred features/predictions accelerate MOT.
- **Data/protocol:** MOT15/MOT17, YOLOv5/DLA34, tracking performance versus speed.
- **Hardware:** exact device not verified here; not a demonstrated CPU-only result.
- **Overlap:** selectively paying for stronger perception during tracking is established.
- **Boundary:** cross-model learned transfer differs from a frozen single-detector spatial wrapper, but a wrapper still needs benefits beyond a periodic stronger-model control.

## P08 — ZoomTrack (2023)

**ZoomTrack: Target-aware Non-uniform Resizing for Efficient Visual Tracking.**
Yutong Kou, Jin Gao, Bing Li, Gang Wang, Weiming Hu, Yizheng Wang, Liang Li.
**NeurIPS 2023**.
[Official paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/9fc291fef2f9607a46777d367f900a15-Paper-Conference.pdf),
[author code](https://github.com/Kou-99/ZoomTrack).

- **SECTIONS verified:** target-location prior drives nonuniform sampling through a QP, retaining target detail at smaller input sizes.
- **Data/protocol:** single-object tracking with OSTrack/TransT on multiple benchmarks, including LaSOT, GOT-10k, TrackingNet and TNL2K.
- **Hardware:** CUDA evaluation code; exact reported GPU model not verified here.
- **Overlap:** track-guided resolution concentration already exists. SOT is not multi-identity association; use this as conceptual prior art, not as a directly comparable MOT baseline without substantial adaptation.

## P09 — UTrack (2024)

**UTrack: Multi-Object Tracking with Uncertain Detections.**
Edgardo Solano-Carrillo, Felix Sattler, Antje Alex, Alexander Klein,
Bruno Pereira Costa, Angel Bueno Rodriguez, Jannis Stoppe.
**ECCV 2024 Workshop on Uncertainty Quantification for Computer Vision**, as
reported by the authors; not an ECCV main-conference claim.
[Author paper](https://arxiv.org/abs/2408.17098),
[full text](https://arxiv.org/html/2408.17098v1).

- **SECTIONS verified:** empirical detection uncertainty is propagated into association/filtering.
- **Hardware/data:** A100 in reported timing; MOT17/MOT20/DanceTrack/KITTI.
- **Overlap:** detector confidence is not complete predictive uncertainty; uncertainty-aware association is established.
- **Boundary:** not evidence that a YOLO scalar score or a hand-tuned covariance is a calibrated identity-failure probability. Any extra uncertainty passes in our method must enter the CPU budget.

## P10 — ADARE-HD (2024)

**ADARE-HD: Adaptive-Resolution Framework for Efficient Object Detection and Tracking via HD-Computing.**
Mohamed Mejri, Chandramouli Amarnath, Abhijit Chatterjee.
**IEEE MWSCAS 2024**.
[Author/institutional copy](https://par.nsf.gov/servlets/purl/10586801),
[DOI](https://doi.org/10.1109/MWSCAS60917.2024.10658671),
[official proceedings contents](https://www.proceedings.com/content/076/076093webtoc.pdf).

- **ABSTRACT verified:** spatially adaptive pixel downsampling with hyperdimensional detection/tracking; object size/image fidelity guide resolution.
- **Data/hardware:** exact benchmark datasets and execution hardware not verified from accessible sections; no local reproduction.
- **Overlap:** spatially variable resolution in detection/tracking is not new.
- **Boundary:** a different representation and classification objective from identity-benefit crop selection. Do not transfer its compute/energy claims to CPU YOLO inference.

## P11 — ROI-Gated SAHI (2026, preprint)

**ROI-Gated SAHI: Content-Adaptive Slicing-Based Inference for Efficient Object Detection.**
Rashid Riyadh, Abd Ullah Khan, Imad Gohar, Muzammil Behzad.
**arXiv preprint**, 25 August 2026; peer-reviewed venue not verified.
[Author record](https://arxiv.org/abs/2608.23923).

- **ABSTRACT verified:** foreground proposals restrict sliced inference; adaptive routing is studied.
- **Data/protocol:** COCO128 and a three-image case study; average ROI gating can be slower than full SAHI. These small studies do not establish broad effectiveness.
- **Hardware:** not verified here.
- **Overlap:** content-adaptive slicing is an explicit recent control/threat, not an original module to claim. It does not establish identity-aware scheduling or independent-camera MOT improvements.

## P12 — ByteTrack (2022) and OC-SORT (2023)

**ByteTrack: Multi-Object Tracking by Associating Every Detection Box.** Yifu Zhang
et al., **ECCV 2022**. [Author paper](https://arxiv.org/abs/2110.06864).
Low-score recovery; MOT17/MOT20 and other tracking benchmarks. Complete detector
plus tracker timing is not interchangeable with association timing. Exact hardware
must be read from each published experiment before comparison.

**Observation-Centric SORT: Rethinking SORT for Robust Multi-Object Tracking.**
Jinkun Cao et al., **CVPR 2023**. [Author paper](https://arxiv.org/abs/2203.14360),
[author implementation](https://github.com/noahcao/OC_SORT).
Observation-centric motion/association and re-update; MOT17/MOT20/DanceTrack and
other benchmarks. Its quoted single-CPU tracking throughput uses supplied detections,
not detector-inclusive CPU video throughput. These are mandatory backbones/controls,
not novelty sources to rename.

## P13 — BoT-SORT (2022) and BoostTrack (2024)

**BoT-SORT: Robust Associations Multi-Pedestrian Tracking.** Nir Aharon, Roy Orfaig,
Ben-Zion Bobrovsky. **arXiv 2022**; formal venue not established by the cited record.
[Author paper](https://arxiv.org/abs/2206.14651). Appearance, motion and camera motion
combine on MOT17/MOT20. ReID adds inference cost; hardware for the full configuration
is not verified here. The repository disables ReID/GMC and must name that restriction.

**BoostTrack: boosting the similarity measure and detection confidence for improved
multiple object tracking.** Vukasin D. Stanojevic, Branimir T. Todorovic.
**Machine Vision and Applications 35, 53 (2024)**.
[Publisher/DOI](https://doi.org/10.1007/s00138-024-01531-5).
Confidence, Mahalanobis and shape cues strengthen association on MOT17/MOT20.
Exact evaluation device unverified here. This is an additional strong cheap-cue
control, not an established detector scheduler. Consult the publisher's correction
before selecting a reproduction version.

## Foundational work that must not disappear from related work

| Work and verified primary reference | Mechanism / evaluation / boundary |
|---|---|
| Denzler, Zobel, Niemann, **Information Theoretic Focal Length Selection for Real-Time Active 3-D Object Tracking**, ICCV 2003; [author publication page](https://inf-cv.uni-jena.de/home/staff/denzler/) | Active sensing/zoom for state estimation is old; optical camera control is not the same action as digital ROI inference. Hardware/dataset details not verified here. |
| Yu, Cheng, Zhu, Bedmutha, Basu, **Adaptive Resolution Optimization and Tracklet Reliability Assessment for Efficient Multi-Object Tracking**, TCSVT 28(7), 2018; [author CV](https://webdocs.cs.ualberta.ca/~crome/mrc/people/anup_basu/files/CV_AnupBasu2022.pdf), [DOI](https://doi.org/10.1109/TCSVT.2017.2668278) | **METADATA verified only**; full algorithm, hardware and datasets remain unverified. Its title alone is a warning against claiming the adaptive-resolution/reliability combination first. |
| Chin, Ding, Marculescu, **AdaScale: Towards Real-time Video Object Detection using Adaptive Scaling**, MLSys 2019; [official proceedings](https://proceedings.mlsys.org/paper_files/paper/2019/hash/b3ac5aacb06c91fda1af776a677100ab-Abstract.html), [paper](https://mlsys.org/Conferences/2019/doc/2019/209.pdf) | Predict next-frame scale; GTX 1080 Ti; ImageNet VID/mini YouTube-BB; detection AP/speed, not identities. Resolution effects need not be monotone. |
| Najibi, Singh, Davis, **AutoFocus: Efficient Multi-Scale Inference**, ICCV 2019; [official paper](https://openaccess.thecvf.com/content_ICCV_2019/html/Najibi_AutoFocus_Efficient_Multi-Scale_Inference_ICCV_2019_paper.html) | FocusPixels/FocusChips concentrate fine-scale inference and fuse outputs; COCO, Titan X Pascal. Spatial coarse-to-fine inference and fusion are established. |
| Li, Wang, Ramanan, **Towards Streaming Perception**, ECCV 2020; [author project and paper](https://www.cs.cmu.edu/~mengtial/proj/streaming/) | Evaluating outputs when they become available changes the accuracy/latency trade-off; asynchronous prediction and scheduling are established. Argoverse-HD, urban detection/segmentation. Exact evaluation hardware not verified here. This is not an existing definition of streaming HOTA. |
| Guo, Pleiss, Sun, Weinberger, **On Calibration of Modern Neural Networks**, ICML 2017; [PMLR](https://proceedings.mlr.press/v70/guo17a.html) | Classification probability calibration, not proof of identity-risk or covariance calibration. Hardware/datasets of a new calibration experiment must be reported separately. |
| Luiten, Osep, Dendorfer, Torr, Geiger, Leal-Taixé, Leibe, **HOTA: A Higher Order Metric for Evaluating Multi-object Tracking**, IJCV 2021; [author paper](https://arxiv.org/abs/2009.07736), [DOI](https://doi.org/10.1007/s11263-020-01375-2), [TrackEval](https://github.com/JonathonLuiten/TrackEval) | Standard detection/association evaluation; no special accelerator required by the metric. Use full localization-threshold average, official sequence handling and explicit class scope. |

## Coverage of the ten requested areas

| Area | Main inspected references | Remaining gap in verification |
|---|---|---|
| Active perception for MOT | P01–P03; Denzler | P01 full implementation and sensing granularity |
| Tracking-guided detection | P02, P07, P08, P10 | Exact spatial MOT resolution selection is not fully mapped |
| Uncertainty scheduling | P01, P02, P09 | Distinguish failure risk from action-induced improvement |
| Adaptive resolution | P02, P06, P08, P10; AdaScale | Local CPU reproduction |
| Dynamic crops/tiling | P04, P05, P11; AutoFocus | Action-level fusion and identity-specific benefit |
| SAHI family | P04, P11 | Strong cost-matched baseline on this footage |
| Budgeted perception | P01–P03, P06 | True end-to-end CPU cost rather than detection rate |
| Observation-centric MOT | P12 | Causal preview/commit integration |
| Identity ambiguity/calibration | P01, P09, P13; Guo | Independent labels and intervention targets |
| Edge/traffic systems | P01–P03, P06 | CPU-only workload, thermal state and independent traffic cameras |

## Explicit answers

**Has tracking-guided adaptive resolution selection already been proposed?** Yes in
related forms: P02 couples tracking confidence to detector workload/resolution; P08
uses a tracking prior for spatial resolution in SOT. P10 also joins variable
resolution with detection/tracking. Claiming the broad combination as new is unsafe.

**Has identity uncertainty been used to allocate detector computation?** Yes: see
P01's indexed publisher abstract. That is sufficient to reject a broad first-use
claim; insufficient to assert that its unavailable full method lacks our exact action.

**What gap remains defensible?** Only a **candidate** gap: action-conditioned joint
region utility, discovery and measured CPU deadlines, demonstrated beyond strong
uncertainty scheduling. Full-text comparison and experiments must establish it.
None of the sources proves that this particular combination is absent elsewhere.

## At most three alternative formulations

1. **Action-benefit spatial scheduling:** predict which joint region can repair an
   association, rather than rank unreliable tracks. Test matched recall and matched
   latency; retain only if this distinction survives P01–P03 and crop baselines.
2. **Discovery–identity allocation:** explicitly divide a limited budget between
   never-detected entrants and existing ambiguous tracks; quantify starvation and
   delayed track births. This must outperform a simple reserved round-robin budget.
3. **Empirical evaluation rather than a new tracker:** isolate detector scale,
   ROI context, membership annotation bias and actual CPU costs on multiple cameras.
   A transparent negative result may be scientifically useful; a one-camera sweep
   or a compilation of earlier modules is insufficient by itself.

## Unresolved searches before a novelty claim

Obtain P01 full text and executable details; inspect 2025–15 October 2026 citing work
around P01–P03/P06; inspect the 2018 TCSVT full text. Recheck adjacent T-ITS/TIP/TCSVT
papers using both **scheduling** and **resource allocation**, including non-identical
terminology. Venue priority did not yield a directly verified closest T-ITS or TIP
counterpart in this search; that is a search limitation, not evidence of absence.

Publisher scope pages and quartile access limitations are recorded in the paper
strategy. No external article's results have been copied into local experiment tables.
