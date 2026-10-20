# Bản đồ code

Giữ tên package `code` để không phá import, tests và provenance cũ. Khi chạy
module, dùng Python trong `.venv` từ root repo, hoặc `caap.cmd`.

| Nhóm | File chính | Trạng thái |
|---|---|---|
| Detector | `detection/detector.py` | Dùng trong runner; giữ nguyên class mapping |
| Tracking | `tracker/adaptive_bytetrack.py`, `tracker/ocsort_ctrv.py` | Baseline và ablation hiện có |
| Motion/C1/C3 | `models/` | Giữ để kiểm chứng, không mặc định mọi module đều có contribution đã validated |
| Metrics | `evaluation/metrics.py`, `scripts/eval_hota_ci.py` | Đọc rõ metric/alpha/bootstrap trước khi dùng số |
| GT mới | `scripts/gt_newcam_review.py`, `gt_newcam.py` | Review camera mới và xuất annotation-only |
| GT editor/ROI | `scripts/gt_mixed_*`, `gt_roi*`, `gt_review*` | Các module phụ thuộc nhau; không xóa vì tên gần giống |
| Audit GT | `scripts/paper_gt_audit*`, `gt_audit_reconcile*`, `audit_*`, `seed_bracket.py` | Provenance và sensitivity, chưa chứng minh GT trung lập hoàn toàn |
| Runner | `scripts/run_roi_paper.py` | Tái lập development NKKN, không tự chứng nhận test camera mới |
| Detector data/train | `scripts/clean_detection_*`, `train_detection_trial.py`, `package_kaggle_detection.py` | Giữ dataset review và provenance training |
| Exploratory/reproduction | `scripts/compare_motion_models.py`, `sweep_*`, `benchmark_realtime.py`, `run_experiment.py` | Không là bước bắt buộc hằng ngày |
| Legacy downstream | `detection/accident_classifier.py`, `alert/`, nhánh severity trong `pipeline.py` | Ngoài paper; còn được import bởi pipeline/tests, chưa tháo runtime trong đợt dọn |

Vendor code và license giữ trong `tracker/vendor/`, `tracker/external/`.
Các script vẽ hình của bản thảo cũ nằm trong `archive/`; không dùng chúng làm
bước mặc định cho một paper mới.

Ưu tiên kiểm tra GT và metric trước khi mở rộng thuật toán. Các config cũ vẫn
được giữ để chạy ablation/tái lập, không phải danh sách contribution đã được duyệt.
