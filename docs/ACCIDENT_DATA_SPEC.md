# Spec dữ liệu tai nạn — Paper 2

**Cho:** đồng tác giả phụ trách dataset · **Hạn go/no-go: 20/9/2026**
**Deliverable:** clip + annotation theo format dưới đây, đặt vào
`data/raw/accidents/` và `data/annotations/accidents/` (cả hai gitignored —
KHÔNG commit)

---

## Vì sao cần, và cần chính xác cái gì

Paper đang claim pipeline phục vụ **hai** downstream task: accident alerting và
MAPPO observations. Phần tracking đã có số thật trên 600 frame GT người. Phần
accident thì **chưa có một con số nào** — không có clip tai nạn nào trong repo.

Ba thứ trong paper đang treo vì thiếu dữ liệu này:

1. **Bảng alert precision/recall/F1** — Section V. Hiện trống.
2. **Confusion matrix 3-class severity** (none/minor/severe) — cần để train
   `weights/efficientnet_severity.pt`, hiện chưa tồn tại nên nhánh này tự
   disable, chưa từng chạy thật lần nào.
3. **C3 (Track Reliability Score)** — đây là chỗ quan trọng nhất. C3 hiện là
   một *negative result*: nhánh MAPPO của nó vô dụng (score AUC chỉ 0.609, mà
   false positive sau C2 chỉ còn 5.5% nên không có gì để lọc). Giả thuyết cứu
   được C3 là bất đối xứng: **với alert thì vứt 4 track đúng để chặn 1 alert
   sai là đánh đổi tốt**. Giả thuyết đó chỉ kiểm chứng được trên clip tai nạn.
   Không có data này thì C3 mất chân đứng và paper còn 1 contribution.

---

## 1. Clip DƯƠNG TÍNH (có tai nạn) — mục tiêu >500

| Yêu cầu | Chi tiết |
|---|---|
| Nguồn | Camera cố định (CCTV/giám sát giao thông), giống setup hiện tại. Dashcam chỉ dùng nếu không đủ số lượng — ghi rõ nguồn nào là dashcam |
| Bối cảnh | Đường đô thị VN, mixed traffic, xe máy chiếm đa số |
| Độ dài | Mỗi clip bao **trước tai nạn ít nhất 5 giây** và sau ít nhất 5 giây |
| Định dạng | mp4/asf/mkv đều được, giữ nguyên gốc, đừng re-encode |
| Đặt tên | `<địa_điểm>_<YYYY-MM-DD>_<HHMM>_<id>.mp4` |

### Annotation cần cho mỗi clip dương tính

```
clip_id, start_frame, end_frame, severity, bbox_track
```

- `start_frame` / `end_frame`: **khoảng frame mà tai nạn đang diễn ra**. Không
  phải cả clip. Đây là cái quyết định recall được tính thế nào.
- `bbox_track`: bounding box vùng tai nạn, theo từng frame trong khoảng trên
  (format MOT 1.1 như GT tracking hiện tại, xem `docs/GT_ANNOTATION_GUIDE.md`).
- `severity`: một trong hai nhãn dưới.

### Tiêu chí `severe` vs `minor` — dán cạnh màn hình

| | Dấu hiệu |
|---|---|
| **severe** | xe lật · người bị văng khỏi xe · >2 xe liên quan · xe không tự di chuyển được sau va chạm |
| **minor** | va chạm nhẹ · xe tự đi tiếp được sau va chạm |

Chỉ cần **một** dấu hiệu `severe` là gán `severe`. Nếu phân vân, ghi vào cột
`note` và để `minor` — sẽ rà lại sau, đừng đoán.

**Cân bằng:** cần tối thiểu ~100 clip `severe`. Nếu tỉ lệ lệch quá nặng
(vd 480 minor / 20 severe) thì confusion matrix 3-class sẽ vô nghĩa — báo sớm
để còn tính đường khác (gộp lớp, hoặc report binary).

---

## 2. Clip ÂM TÍNH (không có tai nạn) — mục tiêu ≥100, **đừng bỏ qua**

Đây là phần dễ bị quên nhất, và thiếu nó thì **không đo được false-positive
rate** — mà giảm false alert chính là động cơ gốc của cả paper (Telegram alert
sai liên tục). Không có clip âm tính thì không có mẫu số.

- Traffic bình thường, **cùng camera / cùng góc** với clip dương tính
- Ưu tiên các tình huống dễ gây báo động giả: xe dừng đèn đỏ, xe máy chen sát
  nhau, xe rẽ cắt mặt nhau, người dắt bộ, tắc đường
- Có cả ban ngày và **ban đêm** — hàng `NIGHT` trong C1 chưa từng chạy lần nào
  vì không có footage tối
- Không cần annotate gì ngoài: `clip_id, "no_accident"`

8 clip traffic thường đang có trong `data/raw/videos/` dùng tạm được, nhưng
đều cùng một thành phố, ban ngày, và chỉ 1 clip đã xử lý.

---

## 3. Split protocol — **theo CLIP, không theo frame**

```
train / val / test  =  70 / 15 / 15,  chia theo CLIP
```

Chia theo frame sẽ **leak**: frame trước và frame sau của cùng một vụ tai nạn
gần như giống hệt nhau, nên model gặp lại chính nó ở test và số đẹp giả. Nếu
làm sai chỗ này thì mọi con số severity đều phải làm lại.

Thêm một tầng nữa nếu có thể: **cùng một camera không nên nằm ở cả train lẫn
test** — nếu không, model học background của camera đó chứ không học tai nạn.
Nếu số camera quá ít để làm được, ghi rõ ra để paper khai báo trung thực.

Gửi kèm file `splits.csv` chốt sẵn: `clip_id, split`. Đừng để bên code tự chia
— chia lại là số lại đổi.

---

## 4. Metadata mỗi clip — cần cho bảng dataset trong paper

Section IV của paper đang có một `\todo{}` đỏ chờ đúng những trường này:

```csv
clip_id, location, date, time_of_day, weather, resolution, fps, duration_s, source, split, label, severity
```

`time_of_day`: `day` / `night` / `dusk`. `weather`: `dry` / `rain`.

---

## 4b. Xin thêm: bộ train của `yolo11_vn.pt` (việc riêng, cũng gấp)

Phát hiện khi đo real-time ngày 27/8: `weights/yolo11_vn.pt` là checkpoint
**segment** (`task='segment'`), trong khi pipeline chỉ đọc `.boxes` và không
bao giờ dùng mask. Cái mask head đó không miễn phí:

| model | head | imgsz | detect (ms/frame) |
|---|---|---|---|
| yolo11_vn (segment) | segment | 640 | **130.7** |
| yolo11n (detect) | detect | 640 | **58.2** |

Cùng cỡ nano (2.84M vs 2.62M param), cùng ảnh, cùng máy → **mask branch đang
tốn 2.25× cho một output bị vứt đi**. Ngân sách real-time của nguồn 25 fps là
40 ms/frame, nên 72 ms lãng phí này là khoảng cách giữa "chạy được real-time"
và "không".

Vậy xin **bộ dữ liệu + config đã dùng để train `yolo11_vn.pt`**, để train lại
một checkpoint `task='detect'` cùng 5 class. Không cần label mask mới — chỉ cần
bounding box, mà bộ segment đã có sẵn (box là tập con của polygon).

Cần: ảnh + label, `data.yaml`, và số epoch / imgsz / batch đã dùng (paper đang
có một `\todo{}` đỏ đúng chỗ khai báo training detail này).

---

## 5. Mốc thời gian

| Ngày | Việc |
|---|---|
| Ngay | Xác nhận đã đọc spec + ước lượng bao giờ giao được |
| ~10/9 | Giao lô đầu (dù chỉ 50 clip) để chạy thử pipeline train, phát hiện sai format sớm |
| **20/9** | **GO/NO-GO.** Chưa có đủ data thì Paper 2 chốt submit bản tracking-focused |
| 31/10 | Submit JRTIP |

**Nếu 20/9 chưa có data:** không phải bỏ, mà nhánh accident chuyển thành phần
mở rộng của Paper 3. Paper 2 vẫn submit được với C2 + real-time + các negative
result có phân tích. Nói sớm tốt hơn nói muộn — lô đầu 50 clip đúng format có
giá trị hơn 500 clip sai format giao ngày 19/9.

---

## 6. Câu hỏi hay gặp

**Tai nạn xảy ra ngoài khung hình một phần thì sao?**
Vẫn lấy, gán `note=partial`. Nhưng đừng để loại này quá 20% — nó làm nhiễu
severity.

**Cùng một vụ quay từ 2 camera?**
Lấy cả hai, nhưng **phải cùng một split** (đặt cùng `clip_id` gốc, thêm hậu tố
camera). Để hai góc của cùng một vụ ở train và test là leak.

**Clip lấy từ YouTube/báo chí?**
Được, nhưng đánh dấu `source=web` và **không trộn vào test set** — độ phân giải
và cách encode khác hẳn CCTV, model sẽ học nhầm đặc trưng nén. Cũng cần cân
nhắc bản quyền vì dataset không public nhưng paper có mô tả.

**Có cần label cả xe (car/motorcycle/…) trong clip tai nạn không?**
Không bắt buộc. Detector đã có class `Accident` sẵn trong
`weights/yolo11_vn.pt`. Chỉ cần box vùng tai nạn + severity.
