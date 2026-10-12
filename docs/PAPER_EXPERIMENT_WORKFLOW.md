# Thí nghiệm sau khi hoàn tất GT ROI

Runner: [run_roi_paper.py](../code/scripts/run_roi_paper.py).
Chỉ dùng GT sau lượt sửa [32 nhóm audit](GT_RECONCILED_20261013.md).
Đây là **development trên cùng camera NKKN**, chưa phải test độc lập.
Phạm vi theo [PAPER_SCOPE.md](PAPER_SCOPE.md); không chạy severity hoặc gửi alert.

## Đầu vào và các bước tự chạy

- Checkpoint `ket_qua_train/best.pt`, SHA256 `85bbd3e66e228612d8402d9f51e911ffa6982d6be3e24a5ca4d3e91861b226a1`.
- Receipt GT `data/annotations/paper_gt_reconciliation/reconcile_90026162a7963db7/reconciled_e880ead8.json`.
- Ba đoạn Mixed `[2500,3100)`, Freeflow `[6400,7000)`, Dense `[10700,11300)`;
  tổng 33.420 box. Mọi frame ở đây là zero-based, end-exclusive; GT MOT là local, one-based.
- ROI đóng băng theo receipt, mask pixel ngoài ROI, lọc tâm đáy detection và loại state tracker ngoài ROI.

Runner đóng băng hash của video, checkpoint, GT, ROI, manifest, code và config.
Độ phân giải 640 và 448 có cache riêng; **mọi tracker dùng cùng cache ở mỗi độ phân giải**.
Cache chạy tuần tự từ frame 0 đến 11.299, để có cùng lịch sử trước từng đoạn GT;
không seek ASF theo keyframe. Mỗi chunk tối đa 200 frame lưu atomically và có hash,
nên chạy lại có thể tiếp tục từ chunk cuối. Mean grayscale thật trong ROI được lưu
và replay qua chính EMA của C1; density vẫn lấy từ lịch sử riêng của từng tracker.
Giờ footage cố định là 8, frame rate tracker lấy từ header nguồn (25 fps).

Các nhánh: baseline, CTRV, CTRV+NSA, CTRV+gate, CTRV+gate+NSA,
C1+C2, C1+C2+C3; thêm OC-SORT và BoT-SORT theo tham số công bố và
các đối chứng khớp threshold. OC-SORT còn có nhánh 0.6 + BYTE.
Trong tất cả nhánh, không giữ state ngoài ROI. Hệ số gate/NSA/scale được ghi
rõ, tránh kế thừa config làm hai ablation trùng nhau. Lưu cả track trước/sau C3;
`c1c2c3_raw` trong bảng điểm là đối chứng trước bộ lọc C3 trên cùng run.

Mỗi đoạn được chấm theo class và ALL: MOTA, IDF1, IDSW, Frag, FN, FP,
HOTA/DetA/AssA. ALL là class-agnostic. HOTA lấy trung bình 19 ngưỡng IoU
0.05–0.95, không đổi HOTA@0.5 thành HOTA chuẩn.
Nếu có bản TrackEval đã dùng ở thí nghiệm trước, runner đối chiếu HOTA và
lưu thêm CLEAR/Identity chính thức; sai khác HOTA trên `1e-10` sẽ dừng.
Có thể chỉ định thư mục package bằng `--trackeval <directory>` khi tạo run mới.
Thiếu package thì trường cross-check là null; không được mô tả là đã đối chiếu.

Khoảng tin cậy motorcycle cho C2/baseline và C1C2C3/baseline: paired moving-block,
10.000 lần, seed 20261013, block 15/30/60 frame. ID được tách giữa các block;
CI mô tả thống kê trong đoạn theo evaluator của repo, không phải bất định giữa
camera, không thể dùng để chứng minh test độc lập hoặc CI cho IDF1 toàn sequence.
`exact_box_share` giữ thông tin trùng hình học với GT để xem thiên lệch prelabels.

Latency đo baseline, C2 và C1C2C3: mỗi nhánh/lần lặp ở **process riêng**,
3 lần, 20 frame warm-up rồi 200 frame Dense `[10700,10900)`. Tracker được
pre-roll bằng cache từ frame 0; sau đó chạy detector thực trên ảnh thật.
Đo decode + context/ROI + detector + tracker + C3, báo mean/p50/p95/FPS
và từng stage. Không cộng severity hay mạng gửi alert vào phép đo này.
PyTorch CPU 8 thread, OpenCV 1 thread; runner đặt lại thread sau bước khởi tạo
Ultralytics. Không dùng latency replay làm latency end-to-end.
Đo thực trên máy đang chạy; phải kiểm tra tải nền và độ ổn định trước khi
đưa claim realtime vào paper. Accuracy và latency có cùng checkpoint/ROI/input size.

## Chạy và xem tiến độ

Double-click **`run_paper_experiments.cmd`**, hoặc từ repo root:

```powershell
.\.venv\Scripts\python.exe -X utf8 -u -m code.scripts.run_roi_paper --phase all
```

Kết quả mặc định dưới `data/processed/paper_runs/best85_roi_20261013_v4/`:

| File | Ý nghĩa |
|---|---|
| `protocol.json` | Đầu vào/hash và protocol đã đóng băng |
| `status.json` | RUNNING, FAILED, INTERRUPTED hoặc COMPLETED, kèm phase/size |
| `640/cache_index.json`, `448/cache_index.json` | Số frame cache đã lưu; `complete` phải true để chấm |
| `640/summary.md`, `448/summary.md` | Bảng motorcycle sau khi score xong |
| `640/metrics.json`, `448/metrics.json` | Đầy đủ class/variant/HOTA/CI/cross-check |
| `640/benchmark.json`, `448/benchmark.json` | Các lần đo end-to-end riêng process |

Nếu Codex khởi chạy ở nền, `run.log`, `error.log` và `launcher.json` nằm trong
cùng thư mục. Không mở thêm một run vào đó; khóa OS chặn hai process cùng ghi.
Khóa tự nhả khi process kết thúc, kể cả crash; file `run.lock` còn tồn tại là bình thường.

Nếu máy bị ngắt, chạy lại cùng lệnh/đầu vào. Cache và track dump hoàn tất được dùng
lại; các trial latency hoàn tất được dùng lại với hash protocol khớp. Score có thể
được tính lại từ cùng dump. Nếu code/config/GT/weights đổi, dùng `--out` mới;
không sửa hash hoặc ghi đè protocol để bỏ qua kiểm tra.
Có thể chạy riêng `--phase cache`, `replay`, `score`, `benchmark` với **cùng**
`--sizes`, `--threads`, `--receipt`, `--video`, `--weights` và `--out` của run gốc.
Smoke test `--phase cache --stop-after 32` chỉ lưu cache một phần, không cho chấm.

## Sau khi máy chạy xong

Kiểm tra status COMPLETED và hash/metrics/cross-check, đọc kết quả cả ba đoạn,
đối chiếu trước/sau C3 và các độ phân giải. Sau đó cập nhật bảng, hình, abstract,
kết luận và limitation của bản thảo bằng một bộ số liệu nhất quán; không trộn
bảng detector/GT cũ với run mới. Bản thảo hiện có số liệu lịch sử, chưa phải bản
cuối cho GT sau sửa và checkpoint này.

Nghĩa vẫn cần xác nhận nguồn/quyền dùng dữ liệu, cung cấp video khác camera/ngày
cho test độc lập và duyệt GT mới đó; xác nhận thông tin tác giả/declarations.
Kết quả tracker development không thay cho event GT để chấm binary accident alert.
Code, hướng dẫn và báo cáo phù hợp được commit/push theo AGENTS.md; footage,
checkpoint, cache, track dump và GT cục bộ vẫn được gitignore.
