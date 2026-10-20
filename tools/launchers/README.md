# Launcher chuyên dụng

Các file ở đây vẫn chạy từ root repo dù đã được chuyển thư mục. Không có
launcher nào tự chạy khi mở `caap.cmd` không tham số.

| Tác vụ | Launcher |
|---|---|
| Review NKKN Mixed | `tools/launchers/review_gt_mixed.cmd` |
| Review NKKN Dense / Freeflow | `tools/launchers/review_gt_roi_dense.cmd`, `tools/launchers/review_gt_roi_freeflow.cmd` |
| Vẽ/chỉnh ROI | `tools/launchers/review_gt_roi.cmd` |
| Review tách/nối ID cũ | `tools/launchers/review_gt.cmd` |
| Audit GT / sửa sau audit | `tools/launchers/review_gt_audit.cmd`, `tools/launchers/review_gt_reconcile.cmd` |
| Review dataset detector | `tools/launchers/review_accident_dataset.cmd` |
| Train thử detector trên CPU | `tools/launchers/train_detector_trial.cmd` — chạy prepare/train khi mở |
| Runner NKKN toàn bộ phase | `tools/launchers/run_paper_experiments.cmd` — chạy khi mở |

Hằng ngày ưu tiên `caap.cmd review` hoặc `review_gt_duongbatrac.cmd` ở root.
Các launcher NKKN/audit giữ để mở lại công việc cũ khi cần, không phải yêu cầu
làm lại GT đã hoàn tất. Hướng dẫn: [GT review](../../archive/docs/GT_REVIEW_WORKFLOW_pre_cleanup.md).
