# CAAP — không gian nghiên cứu tracking xe máy

Repo giữ code, GT tools và bằng chứng thực nghiệm về tracking trong giao thông
hỗn hợp. **Hướng paper đang được xem xét lại; chưa có kết luận đủ để gọi hệ
C1–C2–C3 là phương pháp vượt trội hoặc bản thảo sẵn sàng nộp.**

Bắt đầu từ [trạng thái hiện tại](docs/CURRENT_STATE.md) và
[phạm vi đã chốt](docs/PAPER_SCOPE.md). Các đề xuất trong cuộc trao đổi và kế
hoạch cũ không tự trở thành protocol được duyệt.

## Chỉ cần nhớ một điểm vào

Trong PowerShell, tại thư mục repo:

```powershell
.\caap.cmd status
.\caap.cmd review
.\caap.cmd test -q
```

- `status`: xem các vị trí làm việc, không chạy thí nghiệm.
- `review`: tiếp tục GT **Dương Bá Trạc**, xuất annotation có phiên bản; không tự chấm tracker.
- `test`: chạy bộ kiểm tra code.
- `reproduce --help`: xem runner tái lập kết quả **development NKKN**.
- `detector-review` / `detector-train --help`: công cụ detector, khi thực sự cần.

Mở `caap.cmd` không có tham số chỉ hiện hướng dẫn. Có thể tiếp tục bấm trực tiếp
`review_gt_duongbatrac.cmd`. Các launcher còn lại nằm trong
[tools/launchers](tools/launchers/README.md).

## Cấu trúc đang dùng

| Vị trí | Vai trò |
|---|---|
| `code/` | Detector, trackers, C1/C2/C3 và các công cụ được giữ để kiểm chứng/tái lập |
| `configs/` | Cấu hình ablation hiện có; chưa thay threshold, ROI policy hay class map |
| `tests/` | Kiểm tra thuật toán, metrics và việc lưu/xuất GT |
| `docs/` | Trạng thái, scope, review GT và hướng dẫn tái lập |
| `experiments/` | GT đang làm, nguồn phục vụ review và bằng chứng còn cần đối chiếu |
| `data/`, `weights/` | Dữ liệu local, annotation và weights được gitignore |
| `ket_qua_train/` | Checkpoint local và provenance detector; giữ đường dẫn để không hỏng workflow |
| `notebooks/` | Notebook training detector hiện có |
| `tools/` | Điểm vào chung và các launcher chuyên dụng |
| `paper/` | Chỉ dẫn tới snapshot bản thảo; chưa có bản nộp mới |
| `archive/` | Bản thảo cũ, kế hoạch lịch sử và thí nghiệm thăm dò |

Chi tiết: [bản đồ code](code/README.md), [bản đồ experiments](experiments/README.md),
[hồ sơ lưu trữ](archive/README.md).

## Việc tiếp theo

1. Hoàn thiện và audit GT Dương Bá Trạc theo [hướng dẫn review](docs/GT_REVIEW_WORKFLOW.md).
2. Cùng tác giả chốt câu hỏi paper, protocol và nguồn lực trước thí nghiệm mới.
3. Chỉ mở score camera mới sau khi GT/config/protocol đủ điều kiện và được khóa.

Hướng nghiên cứu annotation bias/diagnostics là **đề xuất**, chưa được tự triển
khai thành thí nghiệm mới trong đợt dọn repo. Không thêm severity trở lại paper.

## Cài đặt

Môi trường đang dùng: Windows, Python 3.10. Giữ nguyên `.venv` hiện có nếu đã cài.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\caap.cmd test -q
```

Repo chưa cấp license mở cho code dự án. Footage, annotation, checkpoint và
credentials local không được đưa vào commit. Kết quả cũ có giới hạn được ghi
trong từng evidence note; lưu trữ chúng không xác nhận lại các claim cũ.
