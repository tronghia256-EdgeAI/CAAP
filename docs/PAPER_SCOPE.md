# Phạm vi sau khi bắt đầu lại — 20/10/2026

Nghĩa yêu cầu loại GT tracking cũ và toàn bộ phần paper cũ khỏi repo để làm lại.
Quyết định này thay thế các kế hoạch GT, ROI, C1/C2/C3, deadline và bản thảo cũ.

## Câu hỏi nghiên cứu (chốt 20/10/2026)

**Seed bias trong ground truth MOT được gán nhãn với trợ giúp của tracker.** Khi GT được tạo bằng cách
review output của một tracker, GT đó thiên vị tracker seed bao nhiêu (IDF1, HOTA@0.5)? Bias phụ thuộc
vào recall của reviewer như thế nào, và ở mức nào thì thứ hạng giữa các tracker bị đảo? Protocol rẻ nào
(union seeding, blind adjudication vùng bất đồng, bracket bound) loại được bias này?

- "Sự thật" là GT công khai của FastTrack (traffic CCTV), MOT17 và DanceTrack. GT seed-rồi-review được
  mô phỏng từ output tracker và GT công khai. Human mini-study được hoãn: chỉ làm nếu reviewer yêu
  cầu ở vòng revision (Nghĩa quyết định 20/10/2026).
- Không cần tạo GT tracking mới, không cần thắng SOTA, không đo latency.
- Phát hiện seed bias trong đợt nghiên cứu trước chỉ được nhắc định tính, như quan sát dẫn tới câu hỏi.
  Không trích số, không khôi phục GT hay bằng chứng từ backup.
- Venue: Q1 theo SJR (Scopus). Ứng viên và lý do nằm trong `CLAUDE.md`. Quartile phải kiểm lại trên
  scimagojr.com trước khi nộp.
- Protocol, giả thuyết và quy tắc dừng: `docs/PROTOCOL.md`, đã được Nghĩa duyệt và đóng băng ngày
  20/10/2026.

## Trạng thái

- Không còn GT tracking, ROI, pre-label, review sessions hoặc kết quả cũ trong
  cây làm việc; backup nằm ngoài repo, không tự lấy lại làm nguồn đánh giá.
- Ngày 20/10/2026, video HCMC, dataset/nhãn train detector, `detector.pt`, provenance train, tool
  detector và ByteTrack vendor đã được chuyển ra `C:/Users/ASUS/Desktop/CAAP_detector_backup_20261020`
  (có `MANIFEST.sha256`); không tự khôi phục.
- Giữ metrics (`code/evaluation/`) như công cụ nền, không coi là contribution mới.
- Không còn pipeline C1/C2/C3, severity classifier, Telegram hoặc nhánh MAPPO.
- Severity vẫn ngoài phạm vi.

## Khi làm lại

Thiết kế mục tiêu, split camera/source, quy ước annotation và protocol trước
khi tạo GT/evaluation mới. Nguồn pre-label không phải ground truth; cần kiểm
tra completeness và identity độc lập với model được đánh giá. Chỉ việc dùng
model cũ tạo pre-label không tự chứng minh GT sai hoặc đúng.

Các metrics train detector cũ (nay nằm trong backup) không phải bằng chứng cho paper mới.

Từ 20/10/2026, code và docs của hướng mới được push lên branch `paper/seed-bias` (Nghĩa
duyệt). Không phát hành dữ liệu, video, nhãn hay weights khi chưa có chỉ dẫn mới. Việc chuyển
backup không rewrite Git history.
