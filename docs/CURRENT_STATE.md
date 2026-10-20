# Trạng thái làm việc — 20/10/2026

## Quyết định hiện hành

Nghĩa yêu cầu dọn repo và xem xét lại hướng paper. Đợt này chỉ tổ chức lại
workspace, không phê duyệt một phương pháp mới, thí nghiệm annotation A/B,
protocol test, venue hay deadline nộp bài.

- Phạm vi ràng buộc: [PAPER_SCOPE.md](PAPER_SCOPE.md).
- Công việc GT đã mở: **Dương Bá Trạc**, annotation-only. Hai camera còn lại chưa mở lại.
- Bỏ severity khỏi paper; giữ detector `Accident` và class mapping đang dùng.
- Pixel mask/ROI, thresholds và cấu hình ablation chưa đổi vì việc dọn repo.
- Giới hạn công bố của đợt nghiên cứu vẫn còn: commit local, chưa push phần
  chưa được phép công bố. Không dùng việc dọn repo để phát hành các commit cũ.

## Bằng chứng đã có và giới hạn

| Có thể đối chiếu | Chưa được suy ra |
|---|---|
| Ba đoạn NKKN, mỗi đoạn 600 frame, tổng 72 giây ở 25 fps | Test độc lập hoặc tổng quát hóa nhiều camera |
| Dense 448: ByteTrack IDF1 0.4769, C2 0.4994; IDSW 141 → 62 | C2 vượt baseline mạnh một cách ổn định |
| OC-SORT 0.5+BYTE cùng điều kiện: IDF1 0.5512, IDSW 39 | Mọi chính sách threshold/birth đã được khớp hoàn toàn |
| Audit tìm được xe thật thiếu khỏi GT | Đã đo causal seed effect hoặc đã sửa GT hoàn chỉnh bằng nội suy |
| Input size và pixel mask có ảnh hưởng tới xe nhỏ | Có một nguyên nhân duy nhất hoặc mask luôn có hại |
| C1/C3 đã được triển khai, có ablation và kết quả âm | Đã chứng minh lợi ích downstream hoặc alert precision |
| Thí nghiệm accident có một sự kiện dương tính | Ước lượng recall tổng quát hoặc lợi ích lọc false alerts |
| Có timing cũ với COCO weights | Cấu hình detector/tracker cuối đã đạt real-time |

Nguồn: [kết quả 448](../experiments/paper_final/best85_roi_final/448/summary.md),
[seed audit](../experiments/seed_bias/evidence.md),
[OC-SORT+CTRV](../experiments/ocsort_ctrv/evidence.md),
[operating point](../experiments/operating_point/evidence.md),
[accident case study](../experiments/c3_accident/evidence.md).

Evidence notes và bản thảo cũ ghi lại cách diễn giải ở thời điểm tạo ra chúng.
Những giới hạn trong bảng trên phải được giữ khi sử dụng lại kết quả đó.
Không gọi các seed brackets là GT đã sửa chính xác hoặc confidence interval
cho bias thật. Bootstrap reset ID theo block không tự là CI cho global IDF1.

## Chỗ làm việc

- [Review Dương Bá Trạc](GT_REVIEW_WORKFLOW.md): `caap.cmd review`.
- [Runner NKKN](PAPER_EXPERIMENT_WORKFLOW.md): `caap.cmd reproduce --help`.
- [Quy ước annotation](GT_ANNOTATION_GUIDE.md).
- [Detector workflows](detector/DETECTOR_TRIAL_WORKFLOW.md): chỉ dùng khi cần sửa/train detector.
- [Bản đồ experiments](../experiments/README.md) và [code](../code/README.md).
- [Lịch sử](../archive/README.md): bản thảo, kế hoạch và thí nghiệm thăm dò.

## Hướng đang cân nhắc, chưa phải kế hoạch đã duyệt

Nghiên cứu sai lệch annotation và các yếu tố ảnh hưởng tới việc đánh giá tracking
xe máy có thể kế thừa bằng chứng hiện có. Để chọn hướng đó cần chốt thiết kế
đối chứng cùng clip, người review, reference độc lập và dữ liệu kiểm chứng.
Giữ C2 làm đóng góp chính cũng cần tách lợi ích turn rate khỏi các cơ chế khác
và kiểm tra trên camera độc lập. Không mặc định phải làm cả hai hướng.

## Sau đợt dọn repo

Runtime và cấu hình khoa học được giữ. Một số đường dẫn **output của các tool
thăm dò** chuyển vào `data/processed/` để không tạo lại thư mục lịch sử ở root
experiments. Code hash của protocol mới sẽ khác do dọn cấu trúc; các receipt và
metric cũ không được sửa lại để giả vờ khớp code mới. Tái lập đúng snapshot cũ
thì dùng baseline commit trong [manifest](../archive/cleanup_20261020_manifest.json).
