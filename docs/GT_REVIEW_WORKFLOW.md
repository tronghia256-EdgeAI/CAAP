# Review GT — việc đang làm

## Dương Bá Trạc

Tại root repo, chạy `caap.cmd review` hoặc mở `review_gt_duongbatrac.cmd`.

1. Nếu chưa có ROI, vẽ vùng đường đọc được, lưu rồi đóng cửa sổ ROI.
2. Công cụ mở phiên ROI đúng camera và tiếp tục các quyết định/edits đã lưu.
3. Dùng **V** xem video/sửa box; **A/K** theo câu hỏi; **E** xác nhận sửa thủ
   công đã lưu. Dùng **U** nếu chưa chắc, quay lại sau; không đoán ID.
4. Tắt overlay và rà video gốc để bổ sung xe bị thiếu khỏi mọi nguồn pre-label.
5. Hoàn tất review và kiểm tra consistency/completeness trước khi xuất.

Nút hoàn tất **chỉ xuất annotation có phiên bản** vào đúng camera; không tự chấm
tracker và không xác nhận test độc lập. Hai camera còn lại chưa mở lại review.

ROI mới: đóng review rồi chạy:

```powershell
.\caap.cmd review --edit-roi
```

Các phiên cũ được giữ; không dùng finish của NKKN Mixed để xuất GT camera mới.

## Chỗ lưu tiến độ — giữ nguyên sau đợt dọn

- Inputs/window/seed: `experiments/gt_newcam/duongbatrac_0800/`.
- Parent bundle: `experiments/gt_qa/duongbatrac_0800_review/`.
- ROI sessions: dưới bundle đó, chọn qua `roi_active.json`.
- Export: `experiments/gt_newcam/duongbatrac_0800/reviewed/`.

Source GT, edits, ROI và dữ liệu từ footage được gitignore. Quyết định review
đã theo dõi bằng Git vẫn giữ nguyên. Không đổi tên các thư mục này hoặc xóa
cache trong khi review. Nhật ký thời gian có cả thời gian nghỉ, không tự coi
là thời gian annotation thực.

## NKKN và công cụ cũ

Nếu cần mở lại, các launcher nằm trong `tools/launchers/`:

- `tools/launchers/review_gt_mixed.cmd`, `tools/launchers/review_gt_roi_dense.cmd`, `tools/launchers/review_gt_roi_freeflow.cmd`.
- `tools/launchers/review_gt_roi.cmd` để chỉnh ROI; `tools/launchers/review_gt.cmd` cho review ID cũ.
- `tools/launchers/review_gt_audit.cmd` và `tools/launchers/review_gt_reconcile.cmd` cho audit/reconciliation.

GT NKKN đã có receipts; không làm lại chỉ vì launcher được chuyển vị trí.
Xem [receipt sau reconciliation](../archive/docs/GT_RECONCILED_20261013.md).
Các bước lịch sử chi tiết ở [workflow cũ](../archive/docs/GT_REVIEW_WORKFLOW_pre_cleanup.md).

## Trước khi chấm camera mới

Khóa GT export, ROI, ambiguity rule, detector/config/code và evaluation protocol;
kiểm tra leakage và vai trò development/test. Không chọn 70% case dễ nhất làm
GT hoàn tất. Có người thứ hai kiểm subset và adjudication nếu nguồn lực cho phép.

Đợt dọn repo chưa thực hiện các bước này và chưa mở comparative test scores.
Quy ước chi tiết: [annotation guide](GT_ANNOTATION_GUIDE.md).
