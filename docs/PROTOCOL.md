# Protocol — seed bias trong GT MOT (ĐÃ ĐÓNG BĂNG 20/10/2026)

Trạng thái: **FROZEN 2026-10-20**, Nghĩa duyệt. Lúc đóng băng chưa có thí nghiệm nào chạy và chưa xem số
nào. Từ đây mọi thay đổi chỉ được thêm vào mục "Amendments" (có ngày), trước khi xem kết quả mà thay
đổi đó ảnh hưởng.

## 1. Định nghĩa

- `GT_true`: GT công khai của dataset.
- `GT_S(θ)`: GT mô phỏng, tạo bằng cách cho một "reviewer" có tham số θ review output của tracker seed S
  (mục 4).
- `M(T; G)`: metric của tracker T khi chấm trên GT G.
- Bias: `b(T, S) = M(T; GT_S) − M(T; GT_true)`.
- **Self-seed advantage** của A so với B dưới seed A:
  `SA(A, B) = [M(A; GT_A) − M(B; GT_A)] − [M(A; GT_true) − M(B; GT_true)]`.

## 2. Giả thuyết và endpoint

- **H1 (chính):** `SA(A, B) > 0` ở tham số tham chiếu θ_ref = (r=0.75, p_fp=0.1, q=0.5, a=1).
  θ_ref được chọn trước khi chạy; nó là **giả định**, không phải số đo, và paper phải nói rõ như vậy.
  Endpoint chính: trung bình `SA` theo IDF1 trên mọi cặp (A, B), kèm CI 95% bootstrap theo sequence
  (10 000 lần lặp), báo cáo riêng cho từng dataset. Báo cáo thêm, trên toàn bộ lưới ở mục 4, vùng θ mà
  CI loại trừ 0, để kết luận không phụ thuộc vào một điểm θ_ref duy nhất.
- **H2:** Lỗi GT tương quan với seed làm đảo thứ hạng nhiều hơn lỗi ngẫu nhiên có **cùng số lượng**
  FN, FP và lỗi ID. Endpoint: Kendall τ giữa thứ hạng trên `GT_S` và trên `GT_true`, so với τ trên GT
  lỗi ngẫu nhiên đã khớp số lượng lỗi.
- **H3:** Protocol khử bias làm giảm |SA| với chi phí review (số box hiển thị cho reviewer) thấp hơn
  gán nhãn lại toàn bộ. Endpoint: đường Pareto giữa |SA| còn lại và chi phí.
- Metric phụ: HOTA@α=0.5, DetA, AssA, MOTA, số ID switch. HOTA lấy trung bình theo α chỉ là phụ, vì
  reviewer giữ nguyên hình học box của seed.

## 3. Dữ liệu, detector, tracker

| Dataset | Phần dùng | Vai trò | Giấy phép (phải kiểm lại khi tải) |
|---|---|---|---|
| FastTrack (arXiv 2508.14370) | 12 video | Testbed traffic CCTV chính | OpenRAIL-M (HF); paper CC BY-NC-SA |
| MOT17 | 7 sequence train | Tổng quát hoá, có public detections | CC BY-NC-SA 3.0 |
| DanceTrack | 25 sequence val | Tổng quát hoá, ngoại hình giống nhau | Nhãn CC BY 4.0, video phi thương mại |

- Detector: YOLO11 pretrain COCO, không fine-tune. Ánh xạ class COCO sang class của dataset; bảng
  ánh xạ được ghi trước khi chạy. Detection chạy một lần trên Kaggle T4 rồi cache, mọi tracker dùng
  chung cache (điều kiện "shared detector").
- Điều kiện phụ "different detector": tracker A dùng YOLO11x, tracker B dùng YOLO11n, để đo thành phần
  seed bias đến từ detector.
- Tracker (tham số mặc định đã công bố, cố định trước khi chạy): SORT, ByteTrack, OC-SORT, BoT-SORT
  (không ReID), và một tracker có ReID (Deep OC-SORT hoặc StrongSORT). Chạy qua `trackers` (Roboflow)
  hoặc BoxMOT; chỉ cài để dùng, không vendor code AGPL.
- Sanity check pipeline: ByteTrack trên MOT17 phải lệch không quá 1 điểm IDF1 so với số tham chiếu
  công bố cho cùng detector. Nếu không đạt, sửa pipeline trước khi chạy tiếp.

## 4. Mô hình reviewer (simulator)

Ghép output seed với `GT_true` theo từng frame (Hungarian, IoU ≥ 0.5). Sau đó:

| Tham số | Ý nghĩa | Lưới |
|---|---|---|
| r | Xác suất reviewer thêm một đoạn GT mà seed bỏ sót (đoạn liên tục của một GT id) | 0, 0.25, 0.5, 0.75, 0.9, 1 |
| p_fp | Xác suất giữ một đoạn FP của seed | 0, 0.1, 0.25, 0.5 |
| q | Xác suất sửa một lỗi ID của seed (switch hoặc fragment) | 0, 0.5, 0.9, 1 |
| a | Xác suất giữ hình học box của seed thay vì box GT | 1 (chính), 0 (kiểm tra) |

- Mỗi ô của lưới chạy 10 random seed.
- Kiểm tra bắt buộc bằng test synthetic: với r=1, p_fp=0, q=1, a=0 thì `GT_S = GT_true` và bias = 0.
  Với r=0, p_fp=1, q=0, a=1 thì `GT_S` = output seed và tracker seed đạt IDF1 = 1.
- Lỗi ngẫu nhiên cho H2: cùng số đoạn FN, FP và lỗi ID như `GT_S`, nhưng chọn ngẫu nhiên, độc lập
  với tracker.

## 5. Protocol khử bias (H3)

1. **Union seeding:** seed bằng hợp output của k ∈ {2, 3} tracker, rồi review với cùng θ.
2. **Blind adjudication:** chỉ review các vùng mà các tracker bất đồng; reviewer không biết box thuộc
   tracker nào (r áp dụng trên vùng bất đồng).
3. **Bracket bound:** chấm trên `GT_A` và `GT_B`, báo cáo khoảng. Chi phí review thêm bằng 0.

Chi phí: số box hiển thị cho reviewer, so với số box của `GT_true` (chi phí gán nhãn lại toàn bộ).

## 6. Human mini-study — HOÃN

Nghĩa quyết định ngày 20/10/2026: bản nộp đầu tiên không có human mini-study. Chỉ làm khi reviewer
yêu cầu trong vòng revision. Khi đó dùng thiết kế dự phòng dưới đây, thêm vào protocol bằng một
amendment, và chỉ dùng nó để hiệu chỉnh θ (không đổi giả thuyết hay endpoint):
- 2 người, khoảng 3–4 giờ mỗi người trên CVAT, khoảng 6 đoạn 10–20 s từ FastTrack và DanceTrack
  (đã có `GT_true`).
- Thiết kế chéo seed A / seed B (Latin square). Đo r, p_fp, q, a bằng cách so với `GT_true`.

Hệ quả cho bản nộp đầu: kết quả dựa trên mô phỏng. Paper phải nêu đây là giới hạn và trình bày kết luận
theo cả lưới θ, không chỉ tại θ_ref.

## 7. Quy tắc dừng sớm

Nếu sau khi chạy đủ lưới ở mục 4, |SA| < 0.01 IDF1 với mọi θ có r ≥ 0.5 trên cả ba dataset và không có
lần đảo thứ hạng nào, thì đổi framing thành "GT do tracker hỗ trợ là an toàn khi r ≥ X", bỏ mục 5 và
viết paper ngắn.

## 8. Phân tích và báo cáo

- Mọi số sinh từ một commit; mỗi lần chạy có `provenance.json` (commit, hash input, tham số).
- Output nằm trong `data/processed/seed_bias/` (gitignored). Chỉ commit bảng tổng hợp nhỏ.
- Không phát lại frame, video hay GT gốc; release code để tái tạo.

## Đóng băng

- 2026-10-20: Nghĩa duyệt. Trước khi đóng băng, mini-study được hoãn đến vòng revision và θ_ref thay
  cho θ\* đo từ mini-study (mục 2, mục 6). Commit đóng băng là commit đầu tiên chứa dòng
  `FROZEN 2026-10-20`: `git log --format=%h -S "FROZEN 2026-10-20" -- docs/PROTOCOL.md`.

## Amendments

- (chưa có)
