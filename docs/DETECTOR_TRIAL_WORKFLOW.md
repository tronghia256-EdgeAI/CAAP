# Train thử detector Accident / Vehicle

Nghĩa chọn dùng dữ liệu hiện tại để **train thử**, chưa chốt dataset đã review
hoặc evaluation cho paper. Luồng này không sửa `review.json`, không xác nhận
nguồn/ảnh gốc thay người và không thay checkpoint của pipeline.

## Chạy trên máy hiện tại

Double-click `train_detector_trial.cmd`: tạo snapshot mới rồi chạy YOLO11n
detection, 1 epoch, ảnh 320, batch 2, CPU; mẫu 32 ảnh train / 8 ảnh val.
Đây là kiểm tra luồng training, không phải lượt huấn luyện đầy đủ.
Mỗi lần chạy tạo thư mục mới, không ghi đè lượt trước.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.train_detection_trial --prepare --train --profile smoke --device cpu
```

Snapshot đầy đủ nằm ở `data/processed/detector_trials/trial_<id>/`:

- Chia train/val phát triển theo nhóm, mục tiêu 80/20; không có test.
- Nhóm hash/tên nguồn, gợi ý camera và metadata nguồn đã xác nhận được giữ
  cùng split. Tỷ lệ thật và số nhãn mỗi class nằm trong `report.json`.
- Giữ quyết định EXCLUDE/QUARANTINE và sửa box đã lưu. Ảnh còn box trùng được
  bỏ khỏi lượt thử, ghi trong `skipped.csv`; ảnh/nhãn gốc vẫn nguyên vẹn.
- `manifest.csv` lưu split, nhóm, hash ảnh/nhãn và thành viên mẫu smoke.
- `review_snapshot.json` ghi trạng thái review tại lúc tạo, không phải phê duyệt.
- `runs/` lưu checkpoint, log, CSV metric và receipt phiên bản phần mềm,
  tham số, hash checkpoint đầu vào, trạng thái thành công/thất bại.

Trước mỗi lượt train, kiểm tra hash/inventory/nhãn và nhóm train/val của
snapshot. Checkpoint đầu vào mặc định là `weights/yolo11n.pt` có sẵn; không
dùng `yolo11_vn.pt` segmentation và không tự thay model đang dùng.

## Tiếp tục trên GPU

Chép thư mục snapshot, repo và `weights/yolo11n.pt` sang máy có PyTorch CUDA
phù hợp. Dữ liệu là nội bộ; không đưa ảnh/nhãn/checkpoint lên GitHub.
Script tạo lại YAML theo vị trí snapshot mới, không cần sửa đường dẫn cũ.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m code.scripts.train_detection_trial --train --dataset data/processed/detector_trials/trial_ID --profile trial --device 0 --epochs 30 --batch 8 --imgsz 640
```

`trial_ID` là thư mục snapshot đã tạo. Dùng `--device cpu` nếu chỉ có CPU;
train đầy đủ sẽ chậm. Số epoch 30 là cấu hình thử ban đầu, chưa bảo đảm hội tụ.
Giảm batch nếu GPU hết bộ nhớ. Mẫu smoke ưu tiên phủ class nhưng quá nhỏ để
đo chất lượng mô hình; validation đầy đủ vẫn chỉ là development.

## Sau lượt train thử

1. Kiểm tra loss, metric từng class và ảnh dự đoán sai trên val phát triển;
   xác định lỗi nhãn, thiếu dữ liệu và hiện tượng overfit.
2. Hoàn tất review và xác minh nguồn/ảnh trước augmentation theo
   [workflow dataset clean](ACCIDENT_DATASET_REVIEW_WORKFLOW.md). Bộ export
   hiện tại có thể chứa augmentation và nguồn chưa nhận diện: ràng buộc nhóm
   chỉ hạn chế rò rỉ đã biết, không chứng minh evaluation độc lập.
3. Chốt detector và train protocol bằng train/val; đánh giá một lần trên test
   độc lập sau khi kiểm tra overlap với benchmark và lịch sử training.
4. Dùng cùng một detector cố định cho các biến thể C1/C2/C3; chấm tracking GT
   đã duyệt và đo latency bao gồm detector. Bộ ảnh này chưa có severity/timeline
   để đánh giá cảnh báo tai nạn theo video.

Metric lượt này mang nhãn `DEVELOPMENT_ONLY_NOT_PAPER_EVALUATION`.
