# Lưu trữ — không phải hướng dẫn hiện hành

Ngày dọn: **20/10/2026**, theo yêu cầu của Nghĩa. Tài liệu hiện hành bắt đầu ở
[README](../README.md), [CURRENT_STATE](../docs/CURRENT_STATE.md) và
[PAPER_SCOPE](../docs/PAPER_SCOPE.md).

| Khu vực | Nội dung |
|---|---|
| `paper/` | Cả hai bản thảo cũ, bibliography, template và hình đã có |
| `docs/` | Kế hoạch, protocol/audit/GT receipts lịch sử và bản workflow dài trước đợt dọn |
| `experiments/` | 16 nhóm thí nghiệm thăm dò, synthetic outputs và timing cũ |
| `tools/` | Script hình của bản thảo cũ |
| `maintenance/` | Script di chuyển một lần, giữ để kiểm tra cách dọn |
| `local-notes/` | Bản ghi chú local cũ; gitignored, không phát hành |

Các kết quả âm, sai sót và quyết định cũ vẫn được giữ. Những từ như
"validated", "corrected", "upper bound", "real-time" hoặc "đã chốt" trong
snapshot phải được đọc cùng giới hạn hiện tại; không dùng chúng để phục hồi
severity, scope cũ, deadline cũ hoặc tự mở test camera mới.

## Tra đường dẫn và kiểm tra bảo toàn

[Manifest](cleanup_20261020_manifest.json) ghi từng file được chuyển, SHA-256
trước/sau và commit trước đợt dọn. Ngoài các launcher và hướng dẫn đang dùng
cần sửa đường dẫn, các file chuyển giữ nguyên byte. Số liệu/protocol/receipt cũ
không được chỉnh để hợp thức hóa kết luận mới.

Lịch sử ghi địa chỉ ở thời điểm tạo ra nó, nên code example, Markdown link,
absolute path trong receipt hoặc code hash của snapshot có thể trỏ về cấu trúc
cũ. Tra manifest để tìm file hiện tại. Muốn chạy đúng môi trường source trước
đợt dọn thì dùng baseline commit trong manifest với đúng local inputs tương ứng;
không chạy các script lưu trữ như workflow hiện hành. Không reset workspace đang
có dữ liệu/tiến độ để làm việc đó.

## Dữ liệu và quyền công bố

Không xóa footage, GT, weights, cache hoặc quyết định review. Các thư mục
experiment được chuyển cả phần local đi kèm; `.gitignore` tiếp tục loại footage,
track dumps, cache và build artifacts khỏi commit. `data/`, `weights/`,
`ket_qua_train/` và các đường dẫn GT đang dùng không được di chuyển.

Chưa cấp license mới hoặc thay đổi giới hạn công bố. Đợt này không chạy inference,
training, score camera mới, gửi alert, nộp paper hoặc phát hành dữ liệu.
