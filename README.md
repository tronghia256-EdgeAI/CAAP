# CAAP — seed bias trong ground truth MOT

Câu hỏi nghiên cứu (chốt 20/10/2026): khi GT tracking được tạo bằng cách review output của một
tracker, GT đó thiên vị tracker seed bao nhiêu, khi nào thứ hạng tracker bị đảo, và protocol rẻ nào
khử được bias đó. Thí nghiệm dùng GT công khai (FastTrack, MOT17, DanceTrack) làm chuẩn.

- Phạm vi và quyết định: [docs/PAPER_SCOPE.md](docs/PAPER_SCOPE.md)
- Protocol đã đóng băng: [docs/PROTOCOL.md](docs/PROTOCOL.md)

## Nội dung repo

| Thư mục | Nội dung |
|---|---|
| `code/evaluation/` | Metrics tracking/detection (MOTA, IDF1, IoU matching), kiểm chéo với `motmetrics` |
| `code/utils/files.py` | `sha256`, `atomic_write` cho provenance |
| `tests/` | pytest |
| `tools/caap.py` | CLI (`status`, `test`) |
| `data/`, `weights/` | Dữ liệu và weights local, gitignored (`weights/yolo11n.pt` là YOLO11n pretrain COCO) |

Code và dữ liệu detector cũ (tool dataset, ByteTrack vendor, nhãn train, `detector.pt`, video HCMC)
đã được chuyển ra `C:/Users/ASUS/Desktop/CAAP_detector_backup_20261020` (có `MANIFEST.sha256`) và
vẫn còn trong Git history.

## Bắt đầu

```powershell
.\caap.cmd status
.\caap.cmd test -q
```

Nếu cài trên máy khác:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```
