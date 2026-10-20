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

### A1 — 20/10/2026, trước khi có bất kỳ kết quả nào

**Lý do.** Review phản biện bản simulator đầu tiên (3 hướng độc lập) phát hiện mô hình mục 4, khi diễn
giải theo từng liên kết, kéo GT_S về phía seed ở mọi 0 < q < 1. Ví dụ: sửa một lần cho một lỗi
"excursion" không có tác dụng gì; một swap được sửa trọn chỉ với xác suất khoảng q⁴. Hiệu ứng này làm SA
tăng khoảng 0.01 IDF1, ngang ngưỡng dừng mục 7. Các điểm dưới đây thay thế cách diễn giải mục 4; giả
thuyết, endpoint, lưới θ, θ_ref và quy tắc dừng giữ nguyên.

1. **Matching box.** Hungarian theo từng frame, chỉ trên các cặp có IoU ≥ 0.5 (dung sai epsilon máy,
   như TrackEval), lọc trước khi gán.
2. **Danh tính.** Ghép một-một seed id ↔ GT id bằng Hungarian trên số box đã match (như IDF1).
   `label(g)` = seed id được ghép với g, hoặc một nhãn mới nếu g không được ghép.
3. **Đơn vị sửa ID = episode.** Một cặp (seed id, GT id) nằm ngoài phép ghép danh tính là một cặp lỗi.
   Các cặp lỗi mà việc sửa sẽ va chạm nhau trong cùng frame (ví dụ hai nửa của một swap) gộp thành một
   episode. Mỗi episode được sửa với xác suất **q**, rút một lần: được sửa thì mọi box của nó nhận
   `label(g)`, không thì giữ seed id. Theo cách xây dựng, output luôn hợp lệ, không còn quy tắc xung đột.
4. **Run.** Đoạn bị bỏ sót và đoạn FP là các đoạn **liên tục theo frame** của một id. Một khoảng trống
   frame làm tách run.
5. **Nhãn của box thêm/giữ.** Đoạn bỏ sót được thêm nhận `label(g)`, hoặc nhãn mới nếu `label(g)` đã bị
   dùng ở một frame của đoạn. Đoạn FP được giữ nhận seed id của nó, hoặc nhãn mới nếu trùng.
   **Box GT được thêm thay thế** box seed chưa match chồng lên nó (IoU ≥ 0.1) trong cùng frame: reviewer
   sửa box lệch chứ không giữ cả hai.
6. **Hình học a.** Rút theo từng box match.
7. **Input.** Frame/id phải là số nguyên, (frame, id) duy nhất, mọi giá trị hữu hạn. Input được sắp xếp
   về thứ tự chuẩn, nên kết quả không phụ thuộc thứ tự hàng trong file. Thứ tự rút ngẫu nhiên cố định:
   episode (theo frame đầu), đoạn bỏ sót, đoạn FP (theo id rồi frame đầu), hình học.
8. **Tiền xử lý chung.** GT_true và mọi output tracker đi qua **cùng một** bước lọc, trước khi mô phỏng
   và trước khi chấm, để GT_true và GT_S được chấm như nhau:
   - MOT17: GT_true là các hàng có consider = 1 và class = 1. Box tracker match (IoU ≥ 0.5) với GT
     distractor (class 2, 7, 8, 12) hoặc consider = 0 bị bỏ một lần, theo đúng quy tắc của TrackEval.
     Sau đó chấm không qua bước distractor.
   - FastTrack: class 9 (`ignore_region`) và các class 10–15 là vùng bỏ qua. Box tracker có tâm nằm
     trong một vùng bỏ qua cùng frame bị bỏ.
9. **Detection (mục 3).** Detector chung là YOLO11x pretrain COCO. Điều kiện "different detector" dùng
   YOLO11n. imgsz 1280, conf ≥ 0.05, ultralytics 8.4.92, script `tools/kaggle_detect_cache.py`.
   MOT17 dùng detection YOLO11 trên ảnh của thư mục `*-FRCNN`, không dùng public detections.
   Ánh xạ class (COCO → FastTrack, đánh số 1-based theo `labels.txt`):

   | Class đánh giá | FastTrack | COCO |
   |---|---|---|
   | person | 1 | 0 person |
   | bus | 2 bus_small, 3 bus_big | 5 bus |
   | truck | 4 truck_small, 5 truck_big | 7 truck |
   | car | 6 | 2 car |
   | bicycle | 7 bike | 1 bicycle |
   | motorbike | 8 | 3 motorcycle |

   MOT17 và DanceTrack chỉ có person.
10. **Chẩn đoán báo cáo kèm** (từ review phương pháp): tỉ lệ sửa thực tế theo kích thước episode; SA
    tại a = 0 cạnh a = 1 (tách phần danh tính và phần hình học); độ nhạy theo ngưỡng match 0.4 / 0.6
    (chỉ tại θ_ref); phân bố độ dài đoạn bỏ sót của từng tracker seed; phương sai giữa các random seed
    trong từng ô của lưới.

### A2 — 20/10/2026, trước khi có bất kỳ kết quả nào

Chốt chi tiết chạy tracker và chấm điểm (mục 3, mục 8), sau khi đã xem API của thư viện:

1. **Tracker.** Roboflow `trackers` 2.6.1, tham số mặc định của thư viện, `frame_rate` lấy từ
   `seqinfo.ini`. Chạy riêng cho từng class đánh giá. ByteTrack, OC-SORT và BoT-SORT nhận toàn bộ
   detection đã cache (conf ≥ 0.05) và tự áp ngưỡng của mình. **SORT** chỉ nhận detection có
   conf ≥ 0.25 (ngưỡng kích hoạt của nó), vì SORT không có tầng điểm thấp. **BoT-SORT tắt CMC**, vì
   không có ảnh khi chạy offline. Tracker có ReID chạy trên Kaggle ở bước sau và sẽ được chốt bằng một
   amendment riêng trước khi chạy.
2. **Tiền xử lý MOT17 theo đúng TrackEval.** Chỉ bỏ box tracker match (Hungarian, IoU ≥ 0.5) với GT
   thuộc class distractor 2/7/8/12. Box match với GT pedestrian có consider = 0 **không** bị bỏ (sửa
   cụm "hoặc consider = 0" ở A1 mục 8 cho khớp quy tắc của TrackEval). GT_true là consider = 1 và
   class = 1.
3. **Metric.** TrackEval chính thức @12c8791 (JonathonLuiten), gọi trực tiếp các lớp metric HOTA,
   CLEAR và Identity trên dữ liệu trong bộ nhớ. Các alias `np.float`/`np.int`/`np.bool` mà numpy 2 đã
   bỏ được khôi phục trước khi import. Cầu nối phải cho kết quả trùng với Evaluator file-based chính
   thức của TrackEval (sai số tuyệt đối ≤ 1e-12, có test). Phép kiểm này **thay cho sanity check ở
   mục 3** ("ByteTrack trên MOT17 lệch ≤ 1 điểm so với số công bố"), vì không có số tham chiếu nào
   được công bố cho detector YOLO11 COCO này.
4. **Đơn vị.** Mỗi (sequence, class) là một đơn vị chấm. Dataset-level metric cộng gộp theo cách của
   TrackEval (`combine_sequences`). Bootstrap lấy mẫu lại theo **sequence**, mỗi sequence mang theo
   mọi class của nó.
5. **Lưu trữ.** Track đã tiền xử lý nằm ở `data/processed/tracks/`. `provenance.json` ghi commit,
   trạng thái thay đổi chưa commit, phiên bản thư viện và hash của mọi file detection/GT đầu vào.

### A3 — 20/10/2026, trước khi có bất kỳ kết quả nào

Chốt cách tính và phân tích H1 và phần thứ hạng của H2 (`code/seedbias/experiment.py`):

1. **Seed và tracker được chấm** đều thuộc bốn tracker ở A2 (detector chung YOLO11x). Mỗi tracker lần
   lượt làm seed A. SA được tính cho mọi cặp có thứ tự (A, B) với A ≠ B.
2. **IDF1 trên GT_S** được tính đúng theo Identity của TrackEval: đếm các cặp cùng frame có IoU ≥ 0.5
   (IoU tính bằng hàm của TrackEval), rồi tìm phép ghép id có tổng lớn nhất. Các cặp IoU được tính một
   lần với box GT và box seed, vì mỗi box của GT_S mang hình học của một trong hai. Có test bắt buộc
   IDTP phải trùng với cầu nối TrackEval trên GT mô phỏng.
3. **Số ngẫu nhiên chung (common random numbers).** Random seed của simulator là (k, A, đơn vị) với
   k = 0..9, **giống nhau ở mọi ô θ**, nên khác biệt giữa các ô không bị nhiễu bởi các lần rút khác nhau.
4. **Endpoint H1** = trung bình SA (IDF1) trên mọi cặp có thứ tự và trên 10 random seed, tính ở cấp
   dataset (cộng IDTP và số box trên mọi đơn vị). CI 95% là percentile của 10 000 lần bootstrap lấy mẫu
   lại sequence (seed bootstrap cố định 0). Mỗi ô θ được tính cùng cách; "vùng CI loại trừ 0" là tập
   các ô có cận dưới > 0.
5. **H2, phần thứ hạng.** Với mỗi (A, θ, k): Kendall τ-b (scipy) giữa IDF1 các tracker trên GT_A và trên
   GT_true, và số cặp tracker bị đảo thứ tự. Báo cáo τ trung bình, số cặp đảo trung bình, và tỉ lệ lần
   rút có ít nhất một cặp đảo. Phần so sánh với lỗi ngẫu nhiên (null model) sẽ được chốt ở amendment
   sau, trước khi chạy.
6. **Metric phụ** (HOTA@0.5, DetA, AssA, MOTA, IDSW) tính bằng cầu nối TrackEval đầy đủ, chỉ tại θ_ref,
   với cả 10 random seed.

### A4 — 20/10/2026, trước khi có bất kỳ kết quả nào

Chốt null model của H2, tập hệ thống được chấm, và định nghĩa vận hành của H3 (mục 5):

1. **Tập hệ thống.** 8 hệ thống = 4 tracker × {YOLO11x, YOLO11n}. Seed vẫn là 4 hệ thống YOLO11x.
   Endpoint H1 (A3 mục 4) giữ nguyên: chỉ gồm các cặp (A, B) cùng dùng YOLO11x. Các cặp (A YOLO11x,
   B YOLO11n) được báo cáo riêng như thành phần detector của seed bias (mục 3, điều kiện "different
   detector"). Thứ hạng cho H2 (τ, số cặp đảo) tính trên cả 8 hệ thống.
2. **Lát cắt θ cho các phân tích đắt.** S_r = {θ_ref với r thay bằng từng giá trị trong lưới}, gồm 6 ô,
   có θ_ref. Null model của H2 và các protocol của H3 chỉ chạy trên S_r, với 10 random seed.
3. **Null model của H2.** Với mỗi lần rút GT_S (A, θ, k, đơn vị), dựng GT_R từ GT_true, cùng random
   seed:
   - Với mỗi đoạn bỏ sót không được thêm trong GT_S, độ dài ℓ: xoá một đoạn ℓ box liên tiếp ở vị trí
     ngẫu nhiên trên một track GT ngẫu nhiên (chưa bị xoá), nếu track còn đủ dài.
   - Với mỗi cặp lỗi ID không được sửa, n box: chọn một đoạn n box liên tiếp ngẫu nhiên trên một track
     ngẫu nhiên. Nếu seed id của cặp lỗi đó còn nằm trên object khác (kiểu merge), gán đoạn này id của
     một track khác không có mặt ở các frame đó; nếu không (kiểu fragment) hoặc không có track phù hợp,
     gán một id mới.
   - Với mỗi đoạn FP được giữ, độ dài ℓ: chép một đoạn ℓ box liên tiếp ngẫu nhiên của một track GT, dịch
     sang thời điểm ngẫu nhiên khác trong sequence (độ dịch ≠ 0, nằm trong [1, n_frames]), với id mới.
   - Hình học các box còn lại là của GT (a = 0), để so lỗi cấu trúc với lỗi cấu trúc. Phần SA đến từ
     hình học được báo cáo riêng qua a = 0 / a = 1 (A1 mục 10).
   - **Endpoint H2** tại θ_ref: trung bình (τ_null − τ_seed) và (số cặp đảo của seed − của null) trên
     (A, k), cặp theo cùng (A, θ, k). CI 95% bằng bootstrap sequence như A3. Các ô còn lại của S_r được
     báo cáo như đường cong.
4. **Các protocol của H3** (chỉ trên 4 hệ thống YOLO11x, theo thứ tự chữ cái tên tracker):
   - P0, seed đơn: như H1.
   - P1, union seeding, k ∈ {2, 3}, mọi tổ hợp k hệ thống: hợp output theo thứ tự cố định; ở mỗi
     frame, box của hệ thống sau bị bỏ nếu match (Hungarian, IoU ≥ 0.5) với box đã có trong hợp. Id
     được tách riêng cho từng hệ thống, hình học giữ nguyên. Sau đó mô phỏng review với cùng θ.
   - P2, **consensus seeding** (bản vận hành của "blind adjudication"): box đồng thuận là box mà cả 4
     hệ thống đều có (match chuỗi IoU ≥ 0.5 với box của hệ thống đầu tiên). Hình học là trung bình các
     box, nên không giống hình học của hệ thống nào. Hai box đồng thuận ở hai frame liên tiếp được nối
     khi và chỉ khi mọi hệ thống giữ cùng id trên cả hai. Box bất đồng không được seed; reviewer bổ sung
     chúng như đoạn bỏ sót với xác suất r.
   - P3, bracket: với mỗi hệ thống T, khoảng [min_A M(T; GT_A), max_A M(T; GT_A)] trên 4 GT seed đơn.
     Báo cáo độ rộng và tỉ lệ khoảng chứa M(T; GT_true). Chi phí bằng tổng chi phí các GT seed đơn
     (sửa câu "chi phí review thêm bằng 0" ở mục 5).
   - **Chỉ tiêu H3** cho mọi protocol: độ méo cặp đôi
     D = trung bình trên các cặp có thứ tự (A, B) của |[M(A; GT_P) − M(B; GT_P)] − [M(A; true) − M(B; true)]|
     (IDF1, 4 hệ thống YOLO11x). Với P1 báo cáo thêm SA của thành viên so với hệ thống ngoài tập.
     **Chi phí** = số box hiển thị cho reviewer (box seed + box ứng viên bất đồng ở P2), chia cho số box
     của GT_true. Kết quả là đường Pareto (chi phí, D) tại θ_ref, kèm CI bootstrap sequence cho D.

### A5 — 20/10/2026, trước khi có bất kỳ kết quả nào

**Lý do.** Review phản biện thứ hai (3 hướng, trên commit 139dea1) không tìm thấy lỗi tính toán làm sai
SA: IDF1 nhanh, bootstrap và common random numbers đều được kiểm lại bằng cài đặt brute-force. Nhưng
review chỉ ra một số điểm phương pháp phải chốt trước khi xem số:

1. **H1 là mệnh đề về độ lớn.** Mô hình reviewer chỉ kéo GT về phía seed, nên SA ≥ 0 gần như theo định
   nghĩa. Dấu của SA không phải bằng chứng. H1 được phát biểu lại: **SA ≥ δ, với δ = 0.01 IDF1**, tại
   θ_ref, đánh giá bằng cận dưới của khoảng tin cậy (mục 2). Bản đồ vùng θ báo cáo cả hai: cận dưới > 0
   và cận dưới > δ. Paper phải nói rõ SA ≥ 0 là hệ quả của mô hình; nội dung khoa học nằm ở độ lớn.
2. **Khoảng tin cậy.** Với 7–25 sequence, khoảng percentile phủ thấp hơn 95% (mô phỏng của review:
   84–91%). Khoảng chính là **BCa**: bootstrap sequence 10 000 lần, hệ số gia tốc lấy từ jackknife
   leave-one-sequence-out. Báo cáo kèm khoảng percentile và khoảng leave-one-sequence-out. Khoảng của
   MOT17 (7 sequence) được ghi là xấp xỉ.
3. **Đảo thứ hạng có ngưỡng.** Chỉ tính một cặp là bị đảo khi khoảng cách IDF1 trên GT_true của cặp đó
   lớn hơn δ, để các tracker gần như hoà nhau (ví dụ BoT-SORT không CMC và ByteTrack) không làm nhiễu.
   τ-b giữ nguyên. Endpoint H2 (A4 mục 3) dùng số cặp đảo có ngưỡng. **Quy tắc dừng mục 7** được phát
   biểu lại: cận trên BCa của SA < δ với mọi θ có r ≥ 0.5 trên cả ba dataset, và không có cặp đảo có
   ngưỡng nào.
4. **Chẩn đoán báo cáo kèm, tại θ_ref:** SA theo từng sequence và trung bình không trọng số; khoảng
   leave-one-sequence-out; SA theo từng class; ma trận SA(A, B) đầy đủ và SA khi bỏ các cặp có SORT;
   SA tại a = 1 so với a = 0, cho cặp cùng detector và cặp khác detector. Với detector chung, mọi tracker
   trả nguyên box detection, nên hình học không gây khác biệt. Phép đo hình học có ý nghĩa nằm ở cặp
   khác detector, và paper phải nói rõ điều này.
5. **Nhầm class (FastTrack).** Với mỗi class, đo tỉ lệ box seed không khớp GT cùng class nhưng khớp
   (IoU ≥ 0.5) GT của một class khác trong cùng frame; đếm số đơn vị không có GT và tỉ lệ box tracker
   nằm trong chúng. Nếu tỉ lệ nhầm của một class > 10%, paper báo cáo SA khi bỏ class đó, và chạy thêm
   phân tích độ nhạy với car + bus + truck gộp làm một class "vehicle".
6. **Vùng ignore của FastTrack** (sửa A1 mục 8): box tracker có tâm nằm trong vùng ignore chỉ bị bỏ khi
   nó **không** khớp (IoU ≥ 0.5) với một box GT_true của class đang chấm trong frame đó, gần với quy tắc
   bỏ qua vùng của TrackEval. Mỗi sequence phải có `labels.txt` đúng với bảng ánh xạ ở A1 mục 9, nếu
   không thì dừng.
7. **MOT17** dùng đúng công thức của TrackEval, kể cả chiều của ma trận ghép (GT × tracker, GT theo thứ
   tự trong file). Có test so với Evaluator chính thức khi bật `DO_PREPROC=True`, trên dữ liệu cố tình
   tạo ties.
8. **Cache và provenance.** Track được gắn khoá bằng hash input, hash mã nguồn và phiên bản thư viện, và
   tự tạo lại khi khoá đổi. Kết quả thí nghiệm được checkpoint theo (seed, đơn vị), trong thư mục gắn khoá
   theo code + input + lưới. `provenance.json` ghi commit của chính repo này và cờ thay đổi chưa commit.
9. **Phạm vi metric.** Kết luận trên toàn lưới θ và kết luận về thứ hạng chỉ dùng IDF1. Kết luận HOTA chỉ
   ở θ_ref.
10. **Độ nhạy của SORT.** Tại θ_ref, chạy thêm SORT nhận mọi detection (conf ≥ 0.05) như một hệ thống
    phụ, để đo ảnh hưởng của ngưỡng 0.25 ở A2. Không thay đổi endpoint.

### A6 — 20/10/2026, trước khi có bất kỳ kết quả nào

**Lý do.** Review phản biện thứ ba (null model, các protocol H3, thống kê, phạm vi kết luận; trên commit
8540728) xác nhận phần thống kê khớp với cài đặt brute-force, nhưng tìm ra các vấn đề thiết kế ở H2 và
H3. Các điểm dưới đây thay thế phần tương ứng của A4 và A5.

1. **H2 so lỗi cấu trúc với lỗi cấu trúc.** Endpoint H2 và đường cong S_r dùng các ô **a = 0**, vì GT_S
   khi đó mang hình học GT giống null model. Null không phụ thuộc a: nhờ common random numbers, cùng một
   lần rút cho ra cùng các lỗi cấu trúc ở a = 0 và a = 1. Hiệu ở a = 1 được báo cáo kèm, với nhãn
   "cấu trúc + hình học".
2. **Null model khớp đủ số lỗi.**
   - Đơn vị không có box GT_true bị loại khỏi H2 ở cả hai phía, vì null không đặt được FP của chúng.
   - Lỗi được đặt theo thứ tự đoạn dài trước.
   - Một bản sao FP phải không trùng (IoU ≥ 0.5) với box GT_true nào ở frame mới; nếu trùng thì rút đoạn
     hoặc độ dịch khác, tối đa 100 lần, rồi mới bỏ qua.
   - Nhánh merge chỉ dùng nhãn còn trống ở mọi frame của đoạn, nên (frame, nhãn) luôn duy nhất (có kiểm
     tra).
   - Đoạn bỏ sót mà GT_S gán nhãn mới cũng được chuyển sang null như một fragment.
   - Số box lỗi bị bỏ qua được báo cáo theo loại (FN, ID, FP), dưới dạng tỉ lệ trên số đã yêu cầu. Nếu
     một loại vượt 1%, paper ghi rõ và coi endpoint H2 của dataset đó là xấp xỉ.
3. **P1 (union seeding) không được chạy như một protocol.** Với detector chung, mọi tracker trả nguyên box
   detection, nên hợp các output trùng đúng với output của thành viên đầu tiên (review đã kiểm chứng).
   P1 vì thế trùng với P0 của thành viên đó. Paper báo cáo điều này như một phát hiện: union seeding vô
   tác dụng khi các tracker dùng chung detector.
4. **P2 consensus, định nghĩa lại.**
   - Box đồng thuận như A4.
   - Một box đồng thuận được nối với box đồng thuận gần nhất phía sau, trong vòng **30 frame**, mà **đa
     số** hệ thống (3/4, hoặc 2/3) giữ cùng id. Nhờ vậy một tracker đứt track hay một khoảng trống
     detection không làm vỡ track.
   - Box ngoài đồng thuận được khử trùng lặp giữa các hệ thống (Hungarian, IoU ≥ 0.5) và hiển thị như
     ứng viên ẩn danh.
   - Các ứng viên không khớp GT_true được đưa vào như đoạn FP (theo id của hệ thống gốc, liên tục theo
     frame), giữ với xác suất p_fp. Ứng viên đúng là object thật được reviewer bổ sung với xác suất r,
     như đoạn bỏ sót.
   - Chạy P2 trên cả 4 hệ thống YOLO11x, và trên từng tập 3 hệ thống (leave-one-out). Hệ thống bị loại
     ra là phép thử khái quát hoá: SA của các thành viên so với nó được báo cáo.
5. **Chỉ tiêu H3.**
   - D tính trên 4 hệ thống YOLO11x (chính) và trên cả 8 hệ thống.
   - Báo cáo SA của thành viên so với 4 hệ thống YOLO11n.
   - **Tiêu chí "giảm bias":** cận trên BCa của hiệu ghép cặp D_P − D_P0 (cùng các cột bootstrap) < 0
     tại θ_ref, với D_P0 là trung bình trên 4 seed đơn.
   - P3 bracket: báo cáo độ phủ cho từng hệ thống, kèm CI bootstrap sequence.
6. **Chi phí gồm hai phần, không gộp:** (i) box phải kiểm tra = box seed (P2: thêm ứng viên đã khử trùng
   lặp); (ii) box phải vẽ mới = số box của các đoạn bỏ sót được reviewer thêm (phụ thuộc r). Cả hai chia
   cho số box của GT_true. Gán nhãn lại toàn bộ tương ứng (0, 1). Chỉ được viết "rẻ hơn gán nhãn lại
   toàn bộ" khi nêu đủ cả hai phần.
7. **Phạm vi kết luận.**
   - Kết luận xác nhận (confirmatory) chỉ ở θ_ref và tách riêng từng dataset.
   - Muốn phát biểu H1 chung thì cả ba dataset đều phải đạt (intersection-union, không cần hiệu chỉnh).
   - Bản đồ 192 ô θ chỉ mang tính mô tả, với CI theo từng điểm.
   - Không gộp ba dataset làm một.
8. **Chẩn đoán đã cam kết ở A1 mục 10 nay có code chạy:**
   - tỉ lệ sửa thực tế theo kích thước episode tại θ_ref;
   - độ nhạy theo ngưỡng match 0.4 / 0.6 tại θ_ref (IoU khi chấm vẫn 0.5);
   - phân bố độ dài đoạn bỏ sót của từng seed;
   - độ lệch chuẩn giữa 10 random seed trong mỗi ô.
9. **BCa** so sánh ties với dung sai làm tròn (1e-12) và lấy phân vị bằng nội suy tuyến tính, như
   `np.percentile`.
