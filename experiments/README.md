# Experiments — GT đang làm và bằng chứng cần giữ

Không bắt đầu bằng việc duyệt từng thư mục. Dùng bảng này để chọn đúng nguồn.
Các kết quả đều phải được đọc cùng protocol/GT/detector tương ứng.

| Thư mục | Lý do còn ở đây |
|---|---|
| `gt_newcam/` | Camera windows, seed provenance, phiên xuất GT camera mới |
| `gt_qa/` | Quyết định người review, ROI sessions, edits và nguồn GT; giữ nguyên đường dẫn |
| `gt_ablation/` | Dumps/summary cũ vẫn là input cho audit và review; không phải headline mới |
| `c2_final/` | Nguồn pre-label cũ còn được công cụ export tham chiếu |
| `c2_real_vnweights_full/` | Detection cache nguồn cho review/audit; không tự biến thành test detector cuối |
| `paper_final/` | Bảng điểm development cuối cùng đã lưu; có protocol và provenance |
| `seed_bias/` | Audit shares và seed sensitivity brackets, không phải GT ground truth replacement |
| `detector_leakage/` | Training-camera overlap audit; giới hạn theo export/checkpoint đã kiểm |
| `operating_point/` | Phân tích input size/mask/latency và helper cũ |
| `ocsort_ctrv/` | Đối chứng motion model trong OC-SORT, có kết quả âm |
| `external_trackers/` | Baseline receipts; runner còn đọc làm reference |
| `c3_accident/` | Case study cũ; không phải đánh giá accident tổng quát |

Các thí nghiệm thăm dò và timing cũ đã chuyển vào
[archive/experiments](../archive/README.md). Không xóa hoặc sửa số cũ để làm
câu chuyện mới đẹp hơn. Chưa chạy thí nghiệm mới chỉ vì repo được dọn.

Output mới của các tool thăm dò nằm dưới `data/processed/`, được gitignore.
Runner NKKN giữ nguyên output mặc định và provenance trong workflow hiện có.
Chỉ đưa summary/evidence mới vào version control sau khi review nội dung và
kiểm tra quyền công bố; không commit footage, cache, weights hay GT coordinates.
