# Xem detector đã train

`code/scripts/preview_trained_detector.py` chạy kiểm tra trực quan với `best.pt`
do Nghĩa tải từ Kaggle, không thay checkpoint cấu hình mặc định và không sửa GT.

```powershell
# Tạo preview mới: 12 ảnh val và 150 frame camera NKKN, frame nguồn bắt đầu 2500.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.preview_trained_detector

# Mở video và gallery GT / dự đoán trong cửa sổ local.
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.preview_trained_detector --view
```

Output mặc định: `data/processed/detector_previews/best_20261012_v2/`.
Nếu đã tồn tại, dùng `--output data/processed/detector_previews/TEN_MOI`
cho lượt mới; script giữ nguyên kết quả cũ.
Viewer có menu **Camera video** / `val_01.jpg` ... và nút **Play / Pause**.
Ảnh val: bên trái GT xanh lá, bên phải dự đoán với class/confidence.

Mẫu val chọn cố định seed 42, ưu tiên phủ class trước, không chọn theo kết quả
model. Kiểm tra hash ảnh/nhãn, `task=detect`, 5 class và remap qua wrapper CAAP
(`Accident -> 4`, `bus -> 2`, `car -> 0`, `motorcycle -> 1`, `truck -> 3`).
Display dùng confidence 0.25; wrapper sanity check dùng confidence 0.1 theo
pipeline. Hai ngưỡng khác nhau nên số box hiển thị không bằng số box đầu vào tracker.

`report.json` ghi hash model/dataset, môi trường, detections và timing. Tổng số
detections video là số box cộng qua frame, không phải số xe duy nhất. Preview
không chạy tracker, classifier mức độ, logic sự kiện hoặc Telegram.
Ảnh/video/report là dữ liệu local được gitignore.

Đây là development preview: val đã dùng chọn best checkpoint, camera/nguồn chưa
được chứng nhận độc lập với training. Timing CPU của lượt này là thời gian gọi
predict sau warmup, không gồm decode/vẽ/ghi video và không phải benchmark latency
paper được kiểm soát. Xem box trực quan không thay thế chấm GT và test độc lập.
