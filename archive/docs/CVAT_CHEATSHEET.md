# CVAT cheat-sheet — 1 trang, dán cạnh màn hình

> Chi tiết đầy đủ: `docs/GT_ANNOTATION_GUIDE.md`. Trang này chỉ có thứ
> dùng trong lúc đang sửa label. Kẹt ở đâu: chụp màn hình gửi vào chat
> với Claude, sẽ được chỉ tiếp theo đúng cái đang thấy.

## Setup 1 lần (~10 phút)

```
1. app.cvat.ai → Sign up → đăng nhập
2. Projects → +  : tên "NKKN GT", thêm 5 labels (gõ đúng chính tả):
      car   motorcycle   bus   truck   accident
3. Tasks → +     : tên "dense", Project = NKKN GT,
      kéo thả  data/annotations/prelabels/dense_images.zip  → Submit & Open
4. Trong task:  Actions → Upload annotations → MOT 1.1
      → chọn  data/annotations/prelabels/dense_annotations.zip
5. Mở Job → thấy box phủ sẵn trên xe = xong setup
```

## Làm theo checklist, đừng tua từ đầu

```
Mở  data/annotations/prelabels/dense/review_queue.md
→ 137 chỗ đáng ngờ, có sẵn số frame + việc cần làm, ~57 phút
→ làm mục MERGE trước (đúng thứ C2 claim), tick [x] khi xong
→ số frame trong file gõ thẳng vào ô frame của CVAT được

Chưa có file? chạy:  python -m code.scripts.gt_review_queue --segment dense
```

Checklist **không phải GT** — nó chỉ chỉ chỗ đáng ngờ, đúng/sai vẫn do
mắt bạn quyết. Bỏ qua 1 dòng không sao; sửa bừa 1 dòng mới hỏng.
Nó cũng không bắt được xe bị miss hẳn → xong checklist thì tua nhanh
1 lượt để soát loại đó.

## ⚠️ ID trong file ≠ ID trên CVAT

CVAT đánh số lại toàn bộ track thành `1..N` theo thứ tự export khi ghi
MOT 1.1. Pre-label vào với ID của tracker (`5849`, `6413`…) thì export ra
thành `1..335` liền mạch. Nên **đừng gõ ID từ file vào CVAT để tìm** — sẽ
không ra, hoặc tệ hơn là ra nhầm xe.

Tra theo **frame + vị trí pixel**: gõ số frame, nhìn đúng chỗ, click box →
ID mà CVAT hiện mới là ID thật. Ảnh trong task là 800×450, cùng hệ toạ độ
với cột `centre_after` / `box_after` trong
`experiments/gt_qa/split_candidates/candidates.csv`.

## 5 phím là đủ

| Phím | Làm gì |
|---|---|
| `F` / `D` | Frame tiếp / lùi (giữ để tua) |
| `M` | Merge: nối 2 track thành 1 ID |
| `N` | Vẽ box mới (nhớ chọn **Track**, không phải Shape) |
| `Ctrl+S` | **Lưu — bấm mỗi 5–10 phút, cloud không tự lưu** |
| `Esc` | Thoát thao tác đang dở |

## 3 thao tác sửa

**1. Nối track vỡ (việc chính — xe đổi ID giữa chừng):**
```
Click box có ID cũ → bấm M → tua F tới khi xe hiện lại với ID mới
→ click box ID mới → bấm M   ⇒ 2 track thành 1
```

**2. Xe không có box (miss):**
```
Bấm N → chọn label + chế độ Track → vẽ box quanh xe
→ tua F, box tự nội suy theo — chỉnh lại khi nó lệch khỏi xe
→ xe ra khỏi hình: click box → nút "Switch outside" (phím O)
```

**3. Box lệch / sai class:**
```
Kéo cạnh/góc box cho khít xe.
Sai class: click box → sidebar phải → đổi Label (vd car → motorcycle)
```

## Quy tắc nhớ nhanh

- Xe máy = xe **+ người ngồi trên** (cả người ôm sau)
- Xe khuất hẳn vài frame → để track đứt, khi hiện lại **merge về ID cũ**
- Xe xa quá nhỏ (<~8px) không nhận ra class → bỏ qua, đừng label
- Xe đậu lề đường → vẫn label
- Đừng rà từng frame — **tua playback, chỉ dừng chỗ thấy sai**

## Xong thì

```
Actions → Export task dataset → MOT 1.1
→ giải nén về data/annotations/NKKN_gt/dense/gt/gt.txt  → báo Claude chấm điểm
```
