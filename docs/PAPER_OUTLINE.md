# Khung paper — seed bias trong GT MOT do tracker hỗ trợ gán nhãn

Trạng thái: khung nội dung, chưa có số. Định dạng (giới hạn trang, template, highlights) chờ đọc trực tiếp
Guide for Authors của venue đích (Pattern Recognition Letters, rồi đến IVC/CVIU). Trang của Elsevier chặn
truy cập tự động; cần mở bằng trình duyệt và lưu lại trước khi viết dòng đầu tiên. Không nhắc đến AI trong
paper, kể cả câu "không dùng AI".

## Tiêu đề làm việc

"How much does a tracker-seeded ground truth favour its seed? Measuring and removing seed bias in
multi-object tracking benchmarks"

## Câu hỏi và kết luận được phép (theo PROTOCOL.md A5–A6)

| Câu hỏi | Kết luận xác nhận | Nguồn trong `summary.json` |
|---|---|---|
| RQ1: GT seed từ tracker A thiên vị A bao nhiêu? | SA ≥ δ = 0.01 IDF1 tại θ_ref, **tách riêng từng dataset**; phát biểu chung chỉ khi cả 3 dataset đều đạt | `h1[REF].sa_same_detector` (BCa), `above_delta` |
| RQ2: Lỗi tương quan với seed làm đảo thứ hạng nhiều hơn lỗi ngẫu nhiên cùng cỡ không? | τ_null − τ_seed và số cặp đảo (ngưỡng δ), ở a = 0 | `h2[ref].a0`, `null_skip_share` |
| RQ3: Protocol rẻ nào giảm bias? | Cận trên BCa của D_P − D_P0 < 0 tại θ_ref, kèm chi phí hai phần | `h3[θ_ref]` |
| Mô tả | Bản đồ θ, đường cong theo r/q/p_fp, chẩn đoán | `h1` (mọi ô), `ranking`, `h1_diagnostics`, `reviewer_diagnostics` |

Nói rõ trong paper: SA ≥ 0 là hệ quả của mô hình reviewer, nên nội dung khoa học nằm ở **độ lớn**. θ_ref là
**giả định**, không phải số đo; human study để dành cho vòng revision (PROTOCOL.md mục 6). Mọi kết luận
trên lưới θ và về thứ hạng chỉ dùng IDF1; HOTA chỉ ở θ_ref.

## Đóng góp (dự kiến, chỉ giữ cái nào số liệu ủng hộ)

1. Phép đo định lượng đầu tiên về seed bias trong GT MOT do tracker hỗ trợ, trên 3 benchmark công khai
   (traffic CCTV FastTrack, MOT17, DanceTrack), 8 hệ thống.
2. Mô hình reviewer có tham số và mở (r, p_fp, q, a), kèm bản đồ độ nhạy và null model khớp số lượng lỗi.
3. Phát hiện: với detector chung, union seeding trùng với seed đơn (A6 mục 3); hình học box gần như không
   góp phần vào bias (A5 mục 4).
4. Đánh giá protocol consensus và bracket theo đường (chi phí kiểm tra, chi phí vẽ) — D.
5. Code tái tạo đầy đủ (không phát lại dữ liệu).

## Cấu trúc

1. **Introduction.** Gán nhãn bằng model đã thành chuẩn. Đã biết ở NLP (Berzak et al. 2016) và y khoa
   ("incorporation bias", QUADAS-2). Trong MOT chỉ có DIVOTrack nhắc một câu, chưa ai đo. Nêu RQ1–3.
2. **Related work.** Lỗi nhãn và thứ hạng benchmark (Northcutt et al. 2021; COCO-ReM 2024; Penquitt et al.
   2026, nói rõ: lỗi ngẫu nhiên ít đảo thứ hạng, còn lỗi tương quan thì đây là câu hỏi). Nhãn chưa đầy đủ
   trong tracking (TETA 2022). Gán nhãn rẻ cho tracking (SPAM 2024). Metric (HOTA 2021, IDF1, TrackEval).
   Pre-annotation (Lingren et al. 2014; Schroeder et al. 2025).
3. **Problem and reviewer model.** Định nghĩa GT_S, SA, mô hình reviewer (episode lỗi ID, run, hình học),
   các identity kiểm tra. Hình minh hoạ một episode swap.
4. **Experimental setup.** Dataset; detector YOLO11x/YOLO11n COCO; 4 tracker (Roboflow trackers), cấu hình
   theo A2; tiền xử lý chung; TrackEval; lưới θ, θ_ref; bootstrap BCa theo sequence; pre-registration
   (PROTOCOL.md và amendments, commit đóng băng).
5. **Results.**
   - 5.1 RQ1: bảng SA tại θ_ref theo dataset (BCa, percentile, leave-one-out); ma trận SA(A, B).
   - 5.2 Độ nhạy: đường cong SA theo r, q, p_fp qua θ_ref; bản đồ (mô tả); ngưỡng match 0.4/0.6;
     độ nhạy SORT.
   - 5.3 RQ2: τ và số cặp đảo, seed so với null, a = 0 (a = 1 kèm theo).
   - 5.4 RQ3: Pareto (chi phí kiểm tra, chi phí vẽ, D); held-out; bracket.
   - 5.5 Chẩn đoán: theo class (FastTrack), nhầm class, theo sequence, hình học ở cặp khác detector.
6. **Discussion.** Hàm ý thực hành: khi nào GT do tracker hỗ trợ an toàn (r, q cần đạt). Giới hạn: θ là
   giả định, detector chung, tracker không ReID, 3 dataset. Kết luận được viết theo kết quả, kể cả khi âm.
7. **Conclusion.**

## Hình và bảng (tối đa theo giới hạn của venue)

- Hình 1: sơ đồ seed → reviewer → GT_S → chấm, và một episode.
- Bảng 1: SA tại θ_ref, 3 dataset (H1).
- Hình 2: SA theo r và theo q qua θ_ref, 3 dataset (dải CI).
- Hình 3: H2 — τ_seed và τ_null theo r.
- Hình 4: Pareto H3.
- Bảng phụ lục: chẩn đoán, độ nhạy.

## Tài liệu tham khảo cần kiểm chứng (Crossref/arXiv) trước khi đưa vào .bib

Berzak et al. 2016 (arXiv 1605.04481); DIVOTrack (arXiv 2302.07676); Schroeder et al. 2025 (arXiv
2507.15821); Northcutt et al. 2021 (arXiv 2103.14749); COCO-ReM (arXiv 2403.18819); Penquitt et al. 2026
(arXiv 2609.21822); TETA (arXiv 2207.12978); SPAM (arXiv 2404.11426); HOTA (arXiv 2009.07736); Lingren et
al. 2014 (JAMIA, PMC3994857); FastTracker (arXiv 2508.14370); MOT17/MOTChallenge; DanceTrack; ByteTrack;
OC-SORT; BoT-SORT; SORT; QUADAS-2. Mỗi mục phải được mở và đối chiếu tác giả, năm, venue, DOI.
