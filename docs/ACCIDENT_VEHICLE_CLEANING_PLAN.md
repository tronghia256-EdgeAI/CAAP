# Audit và kế hoạch làm sạch `accident_vehicle`

Ngày: **10/10/2026** (Asia/Saigon). Trạng thái: **đã audit, chờ Nghĩa chốt
kế hoạch; chưa lọc, xóa, sửa nhãn hoặc chia lại dataset**.

Nguồn: `data/annotations/accident_vehicle/`, bản export Roboflow v12.
Thông tin phiên bản/license dưới đây được đọc từ README và YAML đi kèm,
chưa xác minh độc lập nguồn gốc từng ảnh.

## 1. Đã kiểm tra những gì

- Đọc cấu trúc toàn bộ export, YAML và README; giải mã đầy đủ **4.980 ảnh**.
- Đọc toàn bộ **4.980 file nhãn**: class ID, số tọa độ, giá trị hữu hạn,
  miền chuẩn hóa, diện tích/box suy biến, dòng nhãn trùng, ảnh thiếu nhãn và
  nhãn không có ảnh.
- Tính SHA-256 file và RGB pixel, kiểm tra trùng trên **toàn bộ ba split**.
- So sánh tất cả cặp perceptual hash giữa ảnh khác pixel: pHash distance ≤8
  và dHash distance ≤10. Đây là tiêu chí tạo hàng chờ, không tự quyết định xóa.
- Tính kích thước, độ sáng, tỷ lệ pixel tối/sáng, độ sắc nét và kích thước
  annotation. Các điểm chất lượng dùng để xếp ưu tiên duyệt.
- Xem trực quan một bộ mẫu tái lập từ cả ba split, cặp gần giống xuyên split,
  ảnh sắc nét thấp và mẫu ngẫu nhiên từng class, có overlay nhãn.
- Đọc lại hash của **9.960 file ảnh/nhãn** sau audit: **không file nào thay đổi**.

Quét toàn bộ bằng chương trình không đồng nghĩa đã duyệt thủ công từng box.
Syntax hợp lệ không chứng minh nhãn đúng hoặc mọi vật thể đã được gán nhãn.

## 2. Kết quả thực tế

| Split | Ảnh | Annotation | Ảnh nhãn rỗng |
|---|---:|---:|---:|
| Train | 3.984 | 45.960 | 1 |
| Validation | 498 | 4.051 | 2 |
| Test | 498 | 5.383 | 0 |
| Tổng | **4.980** | **55.394** | **3** |

Tất cả ảnh đều **640×640**, giải mã được. Không phát hiện thiếu nhãn, nhãn
không có ảnh hoặc lỗi cú pháp/miền tọa độ theo các kiểm tra trên.

| ID trong export | Class | Annotation | Ảnh chứa class |
|---:|---|---:|---:|
| 0 | Accident | 2.584 | 2.125 |
| 1 | bus | 1.550 | 916 |
| 2 | car | 26.167 | 3.733 |
| 3 | motorcycle | 20.156 | 2.302 |
| 4 | truck | 4.937 | 1.965 |

Một ảnh có thể chứa nhiều class nên cột cuối không cộng thành 4.980.
Phân bố cũng lệch giữa split: ảnh chứa Accident là 39,1% train, 64,9%
validation và 49,0% test; ảnh chứa motorcycle là 50,5%, 26,5% và 32,1%.

### Trùng và gần trùng

- **0 nhóm trùng byte; 0 nhóm trùng RGB pixel**. Vì vậy một bước xóa theo
  SHA-256 đơn thuần sẽ không loại được ảnh nào trong bộ hiện tại.
- **12.643 cặp gần giống** theo ngưỡng hash đã nêu.
- **1.548 cặp xuyên split**, liên quan 1.076 ảnh, gồm **175 ảnh test** và
  **121 ảnh validation**. Đây là ứng viên cần xác minh, không phải số ảnh
  chắc chắn phải loại.
- Ghép các liên kết gần giống thành đồ thị cho **354 cụm ứng viên**, trong
  đó **177 cụm xuyên split**. Cụm lớn nhất có 128 ảnh. Liên kết bắc cầu có
  thể gom nhiều frame khác nhau của một cảnh; không được chọn một ảnh rồi
  xóa cả cụm một cách tự động.
- Sau khi bỏ hậu tố `.rf.<hash>`, có **244 nhóm tên nguồn lặp**, 109 nhóm
  xuyên split. Tên giống chỉ là dấu hiệu: tên chung như `image1` có thể
  thuộc các nguồn khác nhau; các nhóm có annotation khác nhau.

Đã thấy trực quan các frame rất sát nhau ở train/test, gồm nhóm `cam_11`,
`cam_24` và nhóm có tên ngày/giờ `7_20_2017`. Hash không đảm bảo phát hiện
hết ảnh đã xoay, crop hoặc augmentation mạnh. Cần rà nguồn clip/camera/vụ
tai nạn ngoài việc đối chiếu cặp hash.

### Nhãn và chất lượng ảnh

- **54.419 polygon + 975 bounding box** trong cùng dataset.
- **4.410 ảnh chỉ polygon**, **567 ảnh trộn polygon và box**, 3 ảnh nhãn rỗng.
  Export hiện tại chưa phải bộ YOLO detection thống nhất. Với segmentation,
  cũng cần giải quyết các annotation chỉ có box trước khi huấn luyện.
- **572 annotation có ít nhất một cạnh bounding box dưới 4 pixel**. Đây là
  hàng chờ kiểm tra vật thể nhỏ, không phải lý do loại mặc định.
- Ảnh mẫu có CCTV, dashcam, ảnh hiện trường/web, phụ đề/watermark và ảnh
  đã xoay/nhiễu; thấy các biến thể như vậy cả ở validation/test.
- README ghi resize fit 640×640 với viền trắng và tạo 3 phiên bản cho mỗi
  ảnh nguồn, nhưng không liệt kê cụ thể augmentation. Không thể suy ra
  4.980/3 là số sự kiện/ảnh độc lập.
- 3 ảnh nhãn rỗng cần kiểm tra là background thật hay bị bỏ sót vật thể.
- `data.yaml` dùng `../train/images`, `../valid/images`, `../test/images`:
  khi giải quyết tương đối từ thư mục export, cả ba đường dẫn đều không tồn tại.

## 3. Kế hoạch đề xuất sau khi Nghĩa duyệt

### Bước 1 — Giữ nguồn và ghi nguồn gốc

Tạo phiên bản mới, ví dụ `data/annotations/accident_vehicle_clean/v1/`;
giữ nguyên export v12. Lưu manifest ảnh/nhãn/hash, provenance, quyết định
giữ/loại/sửa và lý do. Không xóa nguồn để tiết kiệm dung lượng.

Ưu tiên lấy lại **ảnh gốc chưa augmentation** và mapping phiên bản → ảnh
gốc → clip/camera/vụ tai nạn. Nếu chỉ có export hiện tại, dùng tên và ảnh
để đề xuất nhóm rồi duyệt; đánh dấu `unknown` khi không xác minh được.
Không tự bịa metadata hoặc coi nhóm hash là event ID đã xác nhận.

### Bước 2 — Hàng chờ duyệt ngắn theo cụm

Ưu tiên 177 cụm gần giống xuyên split, rồi nhóm augmentation/tên nguồn,
nhãn rỗng, ảnh khó quan sát và nhãn đáng ngờ. Gom việc theo nhóm có ảnh
đại diện và cho xem thêm thành viên khi cần, thay vì yêu cầu duyệt 12.643
cặp riêng lẻ. Dùng luồng trên máy tương tự GT cũ, lưu ngay và tiếp tục được.

Các quyết định chính:

- Cùng ảnh nguồn/biến thể: chọn bản gốc hoặc bản rõ và có nhãn đã xác minh;
  bản dư chuyển sang danh sách loại của phiên bản mới.
- Frame gần nhau nhưng có diễn biến/vật thể khác: có thể giữ, cùng nhóm nguồn
  để chia split; giảm frame dư thừa phải giữ các thời điểm tai nạn quan trọng.
- Cùng camera/clip/event: ghi quan hệ nguồn để chống rò rỉ, không mặc định xóa.
- Khác nguồn nhưng tình cờ giống: giữ và ghi quyết định để không hỏi lại.
- Nhãn sai/thiếu hoặc chưa chắc chắn: sửa hoặc đưa vào quarantine; không
  chọn annotation đúng bằng cách lấy file có nhiều box nhất.

Các ứng viên hash lớn dùng để định tuyến review; muốn xóa một thành viên
phải có quyết định dựa trên ảnh và nguồn, không chỉ liên kết bắc cầu.

### Bước 3 — Chuẩn hóa cho detector 5 class

Đề xuất bản train chính là **YOLO detection**, phù hợp pipeline đang đọc
`.boxes`: polygon → bounding box min/max; box có sẵn giữ nguyên. Lưu liên
kết đến polygon gốc để kiểm toán và vẫn có thể làm segmentation riêng.
Không tự dựng mask từ box rồi coi đó là segmentation GT.

Giữ mapping gốc `0 Accident, 1 bus, 2 car, 3 motorcycle, 4 truck` trong
bản export detection và khai báo đúng `names`; detector hiện tại đã ánh xạ
class theo tên về class ID của project. Không đổi ID âm thầm.

Sửa YAML ở **bản mới**, kiểm tra đường dẫn từ một working directory khác,
ảnh/label 1:1, định dạng chỉ 5 cột, tọa độ và số annotation trước/sau.
Không auto clamp polygon, sửa class hoặc tạo nhãn severity bằng suy đoán.

Chốt quy tắc annotation của Accident: vùng sự kiện hay từng xe liên quan;
xử lý xe tai nạn đồng thời thuộc car/motorcycle/etc. thế nào. Rà thiếu nhãn
ở ảnh traffic nhiều xe và các nhóm class hiếm; kiểm tra chéo một mẫu bởi
người thứ hai nếu dùng bộ nhãn để đưa số chính vào paper.

### Bước 4 — Chia lại theo nhóm, khóa evaluation

Chỉ chia sau khi có nhóm nguồn đã duyệt. Dự kiến **70/15/15 theo nhóm**, seed
cố định, cân bằng class/domain ở mức nhóm và báo tỷ lệ thực tế. Cùng ảnh
nguồn/clip/vụ tai nạn phải ở một split; ưu tiên giữ camera tách biệt giữa
train và test nếu đủ camera. Không cưỡng ép tỷ lệ làm vỡ nhóm.

Tách metadata CCTV/dashcam/web và ngày/đêm; xây evaluation phù hợp mục tiêu
VN mixed traffic. Nếu test gồm nhiều domain, báo riêng từng domain. Kiểm
tra giao với clip GT/benchmark hiện tại của repo trước khi đưa ảnh vào train,
kể cả ảnh có tên ngày/giờ tương ứng video đang lưu trong `data/raw/videos/`.

Chỉ augmentation **on the fly ở train**. Validation/test dùng ảnh gốc;
không chọn mẫu test dựa trên model nào đạt điểm đẹp. Nếu thiếu ảnh gốc hoặc
provenance, báo rõ giới hạn; một export đã augmentation không tự trở thành
test camera/event độc lập chỉ nhờ lọc hash.

### Bước 5 — Đóng gói và nghiệm thu

Xuất ảnh/nhãn/YAML, `manifest.csv`, `groups.csv`, `splits.csv`,
`review_decisions.csv`, `quarantine.csv`, README và báo cáo trước/sau.
Dataset và các file chi tiết tiếp tục ở máy theo `.gitignore`; chỉ commit
tool, kiểm thử và tài liệu tổng hợp được phép chia sẻ.

Nghiệm thu: nguồn không thay đổi; label detection thống nhất; đường dẫn chạy
được; không còn trùng byte/pixel xuyên split; không có nhóm nguồn **đã xác
nhận** nằm ở nhiều split; ứng viên xuyên split và quyết định loại được giải
trình; mọi ảnh chưa đạt yêu cầu có trạng thái rõ ràng. Số ảnh clean chỉ chốt
sau review, không cam kết giữ một tỷ lệ hoặc tăng mAP.

## 4. Nghĩa cần xác thực

1. Có bộ ảnh gốc trước augmentation và mapping clip/camera/event không?
2. Các cặp chưa rõ là cùng nguồn hay hai tình huống khác nhau; nhãn Accident
   và nhãn rỗng/sai/thiếu cần người quyết định.
3. Những nguồn/camera nào được dành cho evaluation và có giao với benchmark
   hoặc dữ liệu đã dùng train checkpoint trước đây không?

Dataset hiện tại có nhãn detector 5 class, **không có nhãn minor/severe hoặc
khoảng thời gian sự kiện**. Làm sạch bộ ảnh này chưa đủ cho confusion matrix
severity hay precision/recall của hệ thống alert theo video trong paper.

## 5. Tái lập audit

```powershell
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.audit_detection_dataset `
  --source data/annotations/accident_vehicle `
  --output data/processed/dataset_audits/accident_vehicle_20261010_v2
```

Thư mục báo cáo đã tồn tại; khi chạy lại phải dùng output mới. Script từ chối
ghi báo cáo vào nguồn hoặc ghi đè output cũ.

Báo cáo chi tiết local:
`data/processed/dataset_audits/accident_vehicle_20261010_v2/` gồm
`summary.json`, `inventory.json`, `images.csv`, `groups.json`, `issues.csv`,
`near_pairs.csv` và `samples/`. Sheet dùng **bounding box bao polygon** để
quan sát, không thể thay thế kiểm tra mask chi tiết. Ngưỡng hash là heuristic;
các cặp chưa được phát hiện vẫn có thể cùng nguồn.
