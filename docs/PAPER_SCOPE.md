# Phạm vi paper — quyết định được lưu

## Dọn repo và xem xét lại hướng nghiên cứu (20/10/2026)

Nghĩa yêu cầu giữ phần cần thiết và đưa tài liệu/thí nghiệm cũ khỏi luồng làm
việc chính. Xem [CURRENT_STATE.md](CURRENT_STATE.md) cho trạng thái bằng chứng
và [archive](../archive/README.md) cho lịch sử. Hai bản thảo cũ được lưu nguyên
nội dung trong `archive/paper/`; chưa có bản nộp mới được duyệt.

Việc dọn không chốt contribution C1/C2/C3, không tự duyệt hướng diagnostic hoặc
thí nghiệm seed A/B, không thay detector/ROI/threshold và không mở score camera
mới. Giới hạn công bố và quyết định bỏ severity bên dưới vẫn giữ nguyên.

## Mở lại GT camera mới (19/10/2026)

Nghĩa đã đồng ý triển khai review một đoạn camera **Dương Bá Trạc** để kiểm tra
kết quả ngoài camera NKKN. Mở `review_gt_duongbatrac.cmd`: chọn ROI riêng rồi
duyệt/sửa GT trong phiên ROI, giữ lại toàn bộ nguồn và tiến độ cũ. Việc này mở
lại phần GT từng được tạm dừng ngày13/10; hai camera còn lại chưa được mở lại.

Lượt này chỉ chuẩn bị annotation: hoàn tất sẽ xuất GT có phiên bản vào đúng
camera, **không tự chấm tracker hoặc xác nhận test độc lập**. Protocol và kiểm tra
independence phải khóa riêng trước khi chấm. Chưa thay đổi pixel-mask runtime,
detector, manuscript, license hoặc quyết định bỏ severity. Nhiều nguồn prelabel
không tự chứng minh GT đầy đủ; cần kiểm tra cả xe bị thiếu và quan hệ ID khó nhìn.

Hướng dẫn: [GT_REVIEW_WORKFLOW.md](GT_REVIEW_WORKFLOW.md).
Theo giới hạn công bố của đợt nghiên cứu, phần triển khai này commit local,
không push ra ngoài khi chưa có chỉ dẫn mới của Nghĩa.

## Quyết định của Nghĩa ngày 12/10/2026

**Bỏ phân loại mức độ tai nạn `minor/severe` khỏi paper hiện tại.**
Đây là quyết định phạm vi, không phải kết quả thực nghiệm mới.

- Không yêu cầu GT severity, train EfficientNet-B0 severity, confusion matrix
  `none/minor/severe` hoặc claim đóng góp phân loại mức độ.
- Giữ detector 5 class: `Accident`, `bus`, `car`, `motorcycle`, `truck`.
  Không đổi class ID hoặc nhãn detector vì quyết định này.
- Tập trung GT tracking, C1/C2, đánh giá C3 có bằng chứng và latency bao gồm detector.
- Nếu giữ ứng dụng cảnh báo, chỉ đánh giá có/không tai nạn theo sự kiện: precision,
  recall, F1, cảnh báo sai/giờ video và độ trễ phát hiện. Cần clip dương/âm tính,
  onset/end, nhóm sự kiện/camera và protocol test độc lập; ảnh box đơn lẻ chưa đủ.
- Không coi C3 là đã được kiểm chứng chỉ vì bỏ severity. Nhánh precision cần
  ablation có/không C3 trên cùng detector và protocol; chưa có thì ghi untested.
- Severity chỉ được mở lại khi Nghĩa yêu cầu thay đổi phạm vi.

## Phân biệt bản thảo và code hiện có

`code/detection/accident_classifier.py` và nhánh alert trong `code/pipeline.py`
vẫn là code legacy dựa trên severity. Tác vụ cập nhật phạm vi paper không thay
runtime, weights hoặc cảnh báo đang dùng. Không mô tả binary alert là đã chạy
chỉ bằng cách đổi nhãn trong hình/bản thảo. Nếu làm nhánh này sau, cần thiết kế,
triển khai, test và chấm event-level riêng; không gửi cảnh báo thật khi benchmark.

Bản thảo JRTIP ở `archive/paper/jrtip/main.tex`; skeleton cũ trong `archive/paper/sections/`
được đồng bộ phạm vi để tránh khôi phục yêu cầu severity ở phiên sau.
Spec dữ liệu hiện hành: [ACCIDENT_DATA_SPEC.md](detector/ACCIDENT_DATA_SPEC.md).

## ROI do Nghĩa chọn cho GT (12/10/2026)

Cho phép polygon ROI theo camera để giới hạn vùng gán nhãn quan sát được.
Giữ GT đầy đủ và ROI riêng; chấm GT và predictions bằng cùng quy tắc tâm đáy
box trong polygon, bao gồm biên. Chốt trước khi xem metric, giữ cố định giữa
variants và khai báo polygon/hash/counts trong báo cáo. ROI không chứng minh
chất lượng vùng xa hoặc test độc lập và không tự hoàn tất human review.

Yêu cầu tiếp theo cùng ngày: tái tạo GT mixed/review chỉ trong ROI, giữ full
GT/lịch sử làm provenance. Runtime phải mask pixel ngoài ROI, loại detection
trước tracker và bỏ track ngoài khỏi state; C1 brightness chỉ tính pixel ROI.
Các kết quả full-frame cũ không tự trở thành kết quả ROI runtime. Đóng băng ROI
cho phiên review và dùng cùng scope/checkpoint cho mọi ablation.
