# Duyệt và xuất dataset Accident / Vehicle

## Mở công cụ

Double-click **`review_accident_dataset.cmd`** ở thư mục gốc repo.
Tên người duyệt mặc định: **Nghĩa**. Đóng rồi mở lại để tiếp tục; dữ liệu gốc
được giữ nguyên. Xem [kế hoạch và audit](ACCIDENT_VEHICLE_CLEANING_PLAN.md).

Bản đã chuẩn bị ở `data/annotations/accident_vehicle_clean/v1/`:
**4.980 ảnh, 55.394 annotation đã chuyển thành bounding box**, class ID giữ
nguyên. Chưa loại ảnh nào vì audit không có ảnh trùng tuyệt đối; các ảnh
gần giống cần quyết định dựa trên nguồn và nội dung.

Hàng chờ có **543 cụm/batch**, thay cho việc duyệt 12.643 cặp riêng lẻ:

| Loại | Số mục | Việc cần làm |
|---|---:|---|
| RELATED | 480 | So sánh ảnh/nguồn; 237 cụm xuyên split được ưu tiên đầu tiên |
| QUALITY | 56 | Xem 661 ảnh có cờ chất lượng/nhãn, theo batch tối đa 12 ảnh |
| LABEL_AUDIT | 7 | Xem 77 ảnh mẫu theo class/split, rà nhãn sai hoặc thiếu |

13 ảnh có polygon khác nhau chuyển thành box cùng class/tọa độ. Chúng nằm
trong QUALITY, được giữ đủ nhãn để bạn quyết định sửa hoặc cách ly.

### Bước 1 đã xử lý ngày 11/10/2026

Theo yêu cầu của Nghĩa, QA tự động đã chuyển **13 ảnh còn box trùng** sang
**QUARANTINE**, không tự chọn/xóa một nhãn khi các polygon khác nhau có thể
thuộc các vật thể khác nhau. Ảnh, nhãn gốc và pool vẫn giữ nguyên; quyết định
cách ly được lưu trong `review.json` và journal với tác giả QA tự động.

Hiện có **4.967 ảnh KEEP, 13 ảnh QUARANTINE**. Kiểm tra toàn bộ nhãn của ảnh
KEEP không còn lỗi hình học/class/box trùng theo validator hiện có; đây chưa
phải xác nhận box đúng nội dung ảnh hoặc đầy đủ vật thể.

Báo cáo chi tiết và bản sao review trước thao tác nằm trên máy tại
`data/processed/dataset_audits/accident_vehicle_box_quarantine_20261011/`.
Để đưa một ảnh cách ly trở lại: chọn ảnh, bấm **V** sửa nhãn, bấm **K** giữ
ảnh rồi duyệt lại các mục liên quan. Nếu viewer đang mở, bấm **Tải lại** trước
khi tiếp tục để đọc quyết định mới và tránh lỗi lưu do phiên bản cũ.

Còn **533 mục chưa duyệt** tại thời điểm xử lý. Số tăng từ 532 vì mục RELATED
10 chứa ảnh vừa cách ly phải được xác nhận lại; không có mục nào được tự
đánh dấu đã duyệt. Chưa tạo release hoặc xác nhận thông tin nguồn.

## Duyệt nhẹ nhàng theo cụm

Hai khung ảnh có overlay box; khung bên phải là **ảnh đang chọn**. Danh sách
bên trái cho phép chọn cụm và mọi ảnh thành viên. Với cụm xuyên split,
khung đối chiếu ưu tiên ảnh thuộc split khác. Dùng **← / →** để xem ảnh tiếp.

| Nút/phím | Tác dụng |
|---|---|
| **A — Xác nhận cụm/batch** | Lưu xác nhận và chuyển sang mục chưa duyệt tiếp theo |
| **U — Chưa rõ** | Đưa mục về trạng thái chưa duyệt |
| **N — Cụm chưa duyệt** | Bỏ qua tạm và tới mục chưa duyệt khác |
| **K — Giữ ảnh** | Giữ hoặc khôi phục đúng ảnh đang chọn |
| **D — Loại ảnh dư** | Loại đúng ảnh đang chọn khỏi bản xuất; phải nhập lý do |
| **Q — Cách ly ảnh** | Giữ hồ sơ ảnh chưa đạt/chưa rõ, không đưa vào bản xuất; phải nhập lý do |
| **V — Sửa box** | Mở ảnh ở mức zoom lớn, thêm/sửa/xóa box, đổi class và hoàn tác |

RELATED tự tạo ràng buộc bảo thủ: các thành viên liên quan theo hash/tên
nguồn được giữ **cùng một split**. Bấm A chấp thuận cách xử lý cụm này;
không có nghĩa mọi ảnh là bản trùng, cùng một sự kiện đã được xác minh hoặc
mọi box đều đúng. Không có thao tác tự xóa cả cụm. Xem thêm thành viên trước
khi loại ảnh hoặc điền thông tin cho cả cụm.

Cần hiển thị cặp đối chiếu ban đầu trước khi xác nhận RELATED; với QUALITY
và LABEL_AUDIT cần hiển thị **mọi ảnh trong batch**. Ghi nhận hiển thị chỉ là
điều kiện của luồng duyệt; xác nhận của người vẫn là bước quyết định. Box
trùng trong ảnh giữ lại phải được xử lý trước khi xác nhận batch nhãn.

Ảnh tối/mờ, xe nhỏ và tình huống khó hợp lệ có thể **giữ**. Nhãn rỗng có thể
là background thật; cần xem ảnh. Các chỉ số chất lượng không tự loại ảnh.

## Sửa box và lưu tiến độ

Trong editor: click chọn box, chọn class rồi **Đổi class**; dùng **Thêm box**
hoặc **Vẽ lại box** và kéo chuột. **Xóa box** chỉ sửa nhãn ảnh hiện tại.
**Hoàn tác sửa cuối** hoạt động trong phiên editor đang mở. Mỗi thao tác tự
lưu, kể cả khi chưa bấm A. Bản chuẩn hóa trong `pool/` được giữ cố định;
chỉnh sửa lưu thành override trong `review.json`, chỉ áp vào bản xuất.

Mỗi sửa nhãn/trạng thái/metadata đưa các mục liên quan về chưa duyệt để
xác nhận lại. Không đồng bộ box giữa các frame một cách tự động.

Ghi chú cụm lưu khi rời ô, chuyển cụm hoặc đóng công cụ. Metadata lưu khi
bấm **Lưu thông tin nguồn**. Nếu chưa lưu metadata, chuyển ảnh sẽ đọc metadata
đã lưu của ảnh mới; nên bấm lưu trước. Lỗi lưu do file thay đổi bên ngoài
được báo rõ; dùng **Tải lại** để đọc phiên bản hiện tại, không ghi đè mù.

Sao lưu cả thư mục `v1/`, đặc biệt `review.json`, `manifest.json`, `cases.json`,
`receipt.json` và `pool/`. Các file này được `.gitignore` giữ trên máy.

## Nguồn và ảnh gốc cần Nghĩa xác nhận

Các trường mặc định chưa xác minh. Gợi ý `camera_hint` từ tên file chỉ giúp
định tuyến và ràng buộc chia tập; không được coi là metadata đã chứng thực.

- `source_id`: định danh ảnh gốc/nguồn, dùng cùng ID cho các biến thể của nó.
- `clip_id`: định danh clip gốc, cùng ID cho frame/biến thể thuộc clip đó.
- `event_id`: định danh vụ tai nạn, cùng ID kể cả có nhiều camera.
- `camera_id`: định danh camera; cần tránh đặt ID mới cho mỗi frame.
- `domain`: `cctv`, `dashcam`, `web`, `other`; để `unknown` khi chưa rõ.
- **Tôi đã xác minh nguồn**: chỉ tick khi biết thông tin nguồn là đúng.
- **Ảnh gốc, chưa augmentation**: chỉ tick khi biết đây là bản gốc. Ảnh nhìn
  rõ hoặc không thấy nhiễu không chứng minh nó chưa được biến đổi.

Có thể lưu cho ảnh đang chọn hoặc chủ động áp dụng thông tin cho **cả cụm**
khi biết mọi thành viên cùng thông tin đó. Cụm hash có thể chứa nhiều clip/
sự kiện khác nhau; không gán một event ID cho cả cụm chỉ vì nền giống nhau.

Nếu có metadata hàng loạt, điền `provenance_template.csv` rồi bấm **Nhập CSV
nguồn**, hoặc dùng CLI bên dưới. Không đổi `source_path`; cột gợi ý giữ lại
để đối chiếu. Confirmation nhận `true/false/1/0`. Import kiểm tra toàn bộ
trước khi lưu, chỉ áp dụng metadata thay đổi và không tự xác nhận cụm.

## Hoàn tất và xuất

Sau khi hết mục chưa duyệt, bấm **Hoàn tất → xuất dataset**.

- Mặc định xuất train/val/test theo nhóm, tỷ lệ mục tiêu **70/15/15**, seed 42.
  Cả nhóm giữ cùng split; cân bằng số ảnh/class được xét ở mức nhóm. Báo tỷ
  lệ thực tế và class thiếu, không ép tỷ lệ bằng cách phá nhóm.
- Mỗi ảnh giữ lại phải có nguồn/domain đã xác minh, ít nhất một ID nguồn/
  clip/event và xác nhận ảnh gốc trước augmentation. Nếu chưa đủ, công cụ
  dừng xuất evaluation và chỉ rõ thông tin còn thiếu.
- Nếu chỉ có export hiện tại và không thể xác minh nguồn/ảnh gốc, có thể
  chủ động chọn **Chỉ xuất bộ train (không có evaluation)** sau review.
  Bản này không cung cấp val/test để báo mAP. Cần dataset evaluation độc lập
  và bổ sung cấu hình val riêng khi dùng với trainer.

Kết quả nằm ở `v1/releases/<timestamp_id>/`, có ảnh/label/YAML,
`manifest.csv`, `groups.csv`, `splits.csv`, `review_decisions.csv`,
`quarantine.csv`, snapshot nguồn/quyết định và `report.json` trước/sau.
Loại/cách ly chỉ bỏ ảnh khỏi release mới; nguồn và pool vẫn còn đầy đủ.
Xuất lỗi không để lại release nửa chừng. YAML dùng root tuyệt đối để giải
quyết đường dẫn từ working directory khác.

Trước khi dùng số chính cho paper, đối chiếu nguồn với camera/clip benchmark
và dữ liệu đã train checkpoint cũ; rà domain, camera chưa xác minh và class
thiếu trong `report.json`. Tool không thể suy ra lịch sử training từ ảnh.
Việc review một mẫu nhãn không chứng nhận toàn bộ 55.394 annotation. Bộ này
cũng không cung cấp timeline sự kiện cho đánh giá alert video. Phân loại mức
độ đã được loại khỏi [phạm vi paper](PAPER_SCOPE.md).

## CLI

```powershell
# Resume / verify prepared version; never reset decisions.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.clean_detection_dataset --prepare --check

# Import a completed human metadata table.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.clean_detection_dataset --import-provenance path/to/filled.csv

# Export after review and provenance confirmation.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.clean_detection_dataset --export --reviewer "Nghĩa"

# Explicit training pool alternative when independent evaluation is unavailable.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.clean_detection_dataset --export --training-only --reviewer "Nghĩa"
```
