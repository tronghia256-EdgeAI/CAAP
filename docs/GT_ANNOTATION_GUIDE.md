# Hướng dẫn label Ground Truth (GT) bằng CVAT

**Cho:** Nghĩa + Lành · **Thời gian ước tính:** 2–4 giờ/người ·
**Deliverable:** `data/annotations/NKKN_gt/` (gitignored — KHÔNG commit)

## Tại sao làm việc này

Mọi số liệu hiện tại (re-id events −60%) là **proxy không có GT** — đủ để
phát triển, không đủ để đưa vào paper. Có GT trên 1800 frames này là có
MOTA/IDF1 thật cho bảng ablation chính, và là thước đo duy nhất không bị
Goodhart (gate sweep đã chứng minh proxy có thể bị game).

Mô hình làm việc: **tracker đã label sẵn ~95% đúng** (pre-labels), người
chỉ **sửa chỗ sai** — nhanh hơn label từ đầu 5–10×.

## Dữ liệu đã chuẩn bị sẵn (chạy `python -m code.scripts.export_prelabels`)

```
data/annotations/prelabels/
├── freeflow/img1/*.jpg   600 frames, ~12 xe/frame  (dễ nhất, làm trước)
├── mixed/img1/*.jpg      600 frames, ~26 xe/frame
├── dense/img1/*.jpg      600 frames, ~47 xe/frame  (khó nhất)
├── freeflow_annotations.zip   ← pre-labels MOT 1.1, import vào CVAT
├── mixed_annotations.zip
└── dense_annotations.zip
```

Gợi ý chia việc: người mới dùng CVAT bắt đầu bằng **freeflow** để quen
tay (~30 phút), sau đó một người nhận **dense**, người kia **mixed**.

## Bước 1 — Cài CVAT (local, 1 lần, ~20 phút)

Dataset là IP của nhóm → **dùng CVAT local qua Docker**, không upload
frames lên app.cvat.ai (cloud của bên thứ ba).

1. Cài [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   (Windows: cần bật WSL2 khi installer hỏi).
2. Terminal:
   ```bash
   git clone https://github.com/cvat-ai/cvat
   cd cvat
   docker compose up -d          # lần đầu tải image ~10 phút
   docker exec -it cvat_server python3 manage.py createsuperuser
   ```
3. Mở `http://localhost:8080`, đăng nhập bằng tài khoản vừa tạo.

## Bước 2 — Tạo Project + Labels (1 lần)

1. **Projects → Create new project**, tên `NKKN GT`.
2. Thêm đúng 5 labels, **tên phải khớp từng ký tự** (thứ tự không quan
   trọng, tên thì có):
   `car`, `motorcycle`, `bus`, `truck`, `accident`

## Bước 3 — Tạo Task cho từng segment

Lặp cho `freeflow`, `mixed`, `dense`:

1. **Tasks → Create new task**, tên = tên segment, Project = `NKKN GT`.
2. **Select files** → chọn toàn bộ 600 file trong
   `data/annotations/prelabels/<segment>/img1/` → Submit.
   (CVAT sắp frame theo tên file — tên đã đánh số sẵn `000001.jpg`…)
3. Mở task → **Actions → Upload annotations → định dạng "MOT 1.1"** →
   chọn `data/annotations/prelabels/<segment>_annotations.zip`.
4. Mở job → thấy boxes phủ sẵn lên xe là import thành công.

## Bước 4 — Sửa pre-labels (phần việc chính)

Cách làm hiệu quả: **xem playback (phím `F` tiến / `D` lùi), chỉ dừng ở
chỗ sai**. Đừng rà từng box từng frame — pre-labels phần lớn đã đúng.

3 loại lỗi cần sửa, theo thứ tự quan trọng với paper:

| Lỗi | Nhận ra thế nào | Sửa thế nào trong CVAT |
|---|---|---|
| **ID switch / track vỡ** (quan trọng nhất — đây là thứ C2 claim cải thiện) | Một xe đi qua mà số ID trên box đổi giữa chừng, hoặc box biến mất rồi hiện lại với ID mới | Chọn track thứ nhất → phím `M` (merge) → chọn track thứ hai → `M` lần nữa → hai track thành một ID. Ngược lại, 2 xe bị dính chung 1 ID → dùng **Split** (icon kéo trên sidebar) tại frame đổi xe |
| **Miss (xe không có box)** | Xe rõ ràng trong hình mà không box nào bám | Vẽ box mới ở **Track mode** (không phải Shape mode) → CVAT tự interpolate các frame sau, chỉnh lại khi lệch |
| **Box lệch / sai class** | Box trùm cả 2 xe, box hụt nửa xe, xe máy bị gán car… | Kéo cạnh box; đổi class trong sidebar phải |

### Quy ước label (đọc kỹ — nhất quán quan trọng hơn "đúng tuyệt đối")

- **Xe máy = xe + người ngồi trên xe** (cả người ôm sau). Đây là quy ước
  detector đã train, giữ nguyên.
- **Che khuất (occlusion):** còn thấy ≥ ~30% xe thì vẫn giữ box, ước
  lượng phần bị che. Khuất hẳn sau xe bus/cây ≥ vài frame → để track
  đứt tại đó là đúng (đừng vẽ box đoán mò); khi xe hiện lại, **nối lại
  cùng ID cũ bằng merge** — chính những chỗ này đo khả năng re-id.
- **Vùng xa (gần vạch sang đường phía trên):** xe nhỏ hơn ~8 px hoặc
  không phân biệt nổi class bằng mắt → **bỏ qua, không label**. GT chỉ
  tính vật thể người nhìn còn xác định được.
- **Xe đậu bên lề:** có label (detector thấy chúng, bỏ ra sẽ thành FP oan).
- **accident:** clip này không có tai nạn; đừng gán class accident.

## Bước 5 — Export GT đã sửa

Với từng task: **Actions → Export task dataset → định dạng "MOT 1.1"**
→ lưu và giải nén về:

```
data/annotations/NKKN_gt/<segment>/gt/gt.txt
```

## Bước 6 — Kiểm tra (Nghĩa chạy, ~1 phút)

```bash
# 1. GT tự chấm chính nó phải ra MOTA = IDF1 = 1.000
python -m code.scripts.import_gt \
    --gt data/annotations/NKKN_gt/dense/gt/gt.txt \
    --pred data/annotations/NKKN_gt/dense/gt/gt.txt

# 2. Chấm thử baseline với GT thật (số MOTA/IDF1 đầu tiên của paper!)
python -m code.scripts.import_gt \
    --gt data/annotations/NKKN_gt/dense/gt/gt.txt \
    --pred-tracks experiments/c2_final/tracks_baseline.json \
    --segment 10700 11300
```

Segment ↔ frame tuyệt đối (cho `--segment`):
`freeflow 6400 7000` · `mixed 2500 3100` · `dense 10700 11300`

## Nếu kẹt

- Docker không chạy → fallback tạm: label duy nhất đoạn `dense` là đủ
  cho bảng MOTA sơ bộ (ưu tiên chất lượng 1 đoạn hơn 3 đoạn vội).
- CVAT hotkeys đầy đủ: `https://docs.cvat.ai/docs/manual/` (mục
  "Shortcuts"). Ba phím dùng nhiều nhất: `F`/`D` (tiến/lùi frame),
  `M` (merge track), `N` (vẽ box mới).
