# Công cụ detector còn giữ

Checkpoint hiện tại: `weights/detector.pt`. Lượt train tương ứng được nhận diện
bởi các record trong `training/detector/`; không dùng những metric đó làm test mới.
Checkpoint khởi tạo để train lại: `weights/yolo11n.pt`.

Hai bộ local được giữ:

- `data/annotations/accident_vehicle/`: nguồn dataset detector.
- `data/annotations/accident_vehicle_clean/v1/`: bundle đã chuẩn bị, kèm quyết
  định và edits của dataset detector; không phải GT tracking.

## Review và train

```powershell
.\caap.cmd detector-review
.\caap.cmd detector-train --help
.\caap.cmd detector-package --help
.\caap.cmd detector-preview --help
```

Không có lệnh nào tự train khi mở `caap.cmd` không tham số. Muốn train phải
truyền rõ `--prepare`/`--train`; package không tự upload. Preview dùng detector
và cần dataset package mới; các preview/cache trước đây đã đưa ra ngoài repo.

Nếu cần chuẩn bị bundle detector mới từ đầu, audit trước:

```powershell
.\.venv\Scripts\python.exe -m code.scripts.audit_detection_dataset --source data/annotations/accident_vehicle --output data/processed/dataset_audit
```

Tool review đang dùng sẽ tiếp tục bundle detector có sẵn, không tự xác nhận
provenance hoặc tạo test độc lập. Tất cả output mới nằm trong `data/processed/`.
Không upload footage, nhãn hoặc weights chỉ vì công cụ package còn tồn tại.
