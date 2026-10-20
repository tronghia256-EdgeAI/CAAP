# CAAP — nền tảng để làm lại nghiên cứu

Repo đã bắt đầu lại ngày **20/10/2026**. GT tracking, ROI/review, kết quả đánh giá,
pipeline C1/C2/C3 và toàn bộ paper cũ đã được chuyển **ra ngoài repo**.
Chưa có GT tracking mới hoặc kết quả paper mới.

## Phần giữ lại

| Thư mục | Nội dung |
|---|---|
| `code/detection/` | YOLO wrapper, dùng checkpoint được chỉ định; không tự fallback |
| `code/tracker/vendor/` | ByteTrack gốc và bản ghi các patch tương thích |
| `code/evaluation/` | Metrics tracking/detection cơ bản, test bằng dữ liệu synthetic |
| `code/scripts/` | Chuẩn bị/review/train/package/preview dataset detector |
| `tests/` | Tests cho các phần đang giữ |
| `training/detector/` | Hồ sơ nhận diện lượt train detector hiện tại |
| `notebooks/` | Notebook train detector trên Kaggle |
| `data/` | Video gốc và hai bộ dữ liệu detector local, được gitignore |
| `weights/` | `detector.pt` hiện tại và `yolo11n.pt` khởi tạo, được gitignore |

## Bắt đầu

```powershell
.\caap.cmd status
.\caap.cmd test -q
.\caap.cmd detector-review
.\caap.cmd detector-train --help
```

Giữ `.venv` hiện có. Nếu cài trên máy khác:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

Đọc [scope reset](docs/PAPER_SCOPE.md) và [workflow detector](docs/DETECTOR_WORKFLOW.md).
Vị trí backup local được ghi trong `data/reset_backup.json`. Không có archive,
thí nghiệm hoặc bản thảo cũ trong cây làm việc hiện tại; Git history được giữ.

Các nhãn train detector vẫn được giữ để tránh mất công chuẩn bị dữ liệu.
Chúng không thay thế GT tracking độc lập. Phạm vi paper, contribution và protocol
mới cần được thiết kế lại; không kế thừa các claim hoặc số cũ.
