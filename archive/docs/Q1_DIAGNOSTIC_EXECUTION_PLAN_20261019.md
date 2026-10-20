# Kế hoạch paper chẩn đoán tracking — đánh giá và thực thi

Ngày lập: **19/10/2026**, Asia/Saigon. Đầu vào là lộ trình Nghĩa vừa dán trong
chat; `scratchpad/q1_plan.md` không có ở workspace hiện tại.

**Quyết định đề xuất: CONDITIONAL GO cho một tuần tạo bản thảo và gói bằng chứng
để gửi thầy. Chưa có cơ sở hứa đạt Q1, được gửi major revision, hoặc sẵn sàng nộp
sau đúng bảy ngày.** Con số 10–25% và mốc thêm 2–3 tuần không có mô hình/dữ liệu
hiệu chỉnh cho manuscript này, nên không dùng làm dự báo xác suất hay cam kết.
Chưa kiểm chứng quartile hiện hành của JRTIP, EAAI, ESWA hay IVC trong nhiệm vụ này.

Đây là **bản kế hoạch**, không phải protocol thực nghiệm đã đóng băng. Chưa chạy
thí nghiệm mới, chưa đổi ROI/mask, chưa gán nhãn thay người, chưa sửa manuscript,
chưa khôi phục code cũ vào main và chưa quyết định license/phát hành.

## 1. Kết luận đánh giá

Chuyển từ paper khẳng định một motion model tốt hơn sang **nghiên cứu chẩn đoán
có đối chứng** phù hợp với bằng chứng hiện có. Đóng góp cần là lời giải thích đã
kiểm tra về input, chính sách association và annotation, thay vì tìm cấu hình để
C2 thắng. Kết quả âm vẫn phải giữ. Tuy nhiên, một camera mới với chỉ600 frame
cũng chưa tự tạo thành benchmark đủ rộng cho một paper mạnh.

Các sửa đổi bắt buộc đối với lộ trình ban đầu:

| Phát biểu/đề xuất | Điều chỉnh cần dùng |
|---|---|
| 3 đoạn ×600 frame, tổng24 giây | Mỗi đoạn24 giây ở25fps; tổng **1.800 frame =72 giây**. Một đoạn DuongBaTrac600 frame thêm24 giây. |
| OC-SORT0.551 so với C20.499 | Đúng ở **Dense, best.pt448, masked ROI**, không phải điểm tổng hợp toàn dataset. Mixed/Freeflow phải báo riêng. |
| Không thành phần nào thắng baseline | Quá mạnh: Dense448, C2 tăng raw IDF1 từ0.477 lên0.499 và giảm IDSW141→62 so với ByteTrack. Điều chưa có là ưu thế ổn định trước baseline mạnh và attribution đã loại confound; không xóa kết quả tốt có thật. |
| C3 không lọc track nào | Đúng ở nhánh observation threshold0.40 đã báo. Không suy ra mọi nhánh/threshold của C3 đều vô tác dụng; trong paper diagnostic này C3 không là đóng góp chính. |
| Đổi OC threshold0.5→0.6 là khớp birth với C2 | OC dùng một ngưỡng cho cả association và birth; ByteTrack/C2 tách high0.5 và birth0.6. Hai cấu hình OC cũ là hai đối chứng khác nhau, chưa khớp toàn bộ chính sách. |
| Oracle0.51→0.92, IDSW81→80 chứng minh detector là nút thắt | Đang trộn macro HOTA với Dense IDSW. Macro OC: HOTA0.507912→0.919570, tổng IDSW93→91. Dense: HOTA0.451468→0.897681, IDSW81→80. Oracle đồng thời đổi miss, FP, geometry và confidence; chưa xác lập phân rã nguyên nhân. |
| Seed bias≈0.04 lớn hơn gain nên gain không có ý nghĩa | Đây là cảnh báo mạnh về độ tin cậy, không phải noise floor phổ quát. Khác GT, detector, operating point và cách đo; cần sensitivity/audit cùng điều kiện. Không so hai con số khác protocol như kiểm định thống kê. |
| GT mới dùng union tất cả tracker là hết bias | Union cải thiện proposal coverage nhưng vẫn thiếu vật thể mà mọi detector bỏ sót; rule “first source kept” có thể giữ ID/geometry của nguồn đầu. Cần blind raw-video pass và adjudication ID, không tự chứng nhận union. |
| Camera mới có GT trung lập sẽ đo lại seed bias | Chỉ kiểm tra được transfer của kết luận. Muốn đo tác động seed phải có đối chứng annotation **trên cùng clip**, có che nguồn/counterbalance và reference độc lập. Khác camera còn lẫn scene difficulty. |
| Review70% case là đủ chấm test | Case count không đo completeness. Chỉ score một test export sau khi toàn bộ phần được chọn đã hoàn tất review và audit theo quy tắc đã khóa. Không dùng70% dễ nhất. |
| Dừng thì nộp ngay JRTIP, chỉ sửa vài chữ | Dừng thí nghiệm khác với đủ chuẩn nộp. Giữ kết quả development, sửa claim và gửi thầy quyết định; không tự động nộp bản còn vấn đề khoa học. |

HOTA đo kết hợp detection, association và localization; không suy nguyên nhân chỉ
từ HOTA hoặc IDSW đơn lẻ. Nguồn metric gốc:
[Luiten et al., HOTA](https://arxiv.org/abs/2009.07736).

## 2. Tình trạng repo đã xác minh

- Main lúc bắt đầu: `79309f0da5342200a37f4f810d50103f67d19942`; working tree sạch.
  Nhánh kế hoạch riêng: `plan/q1-diagnostic-20261019`.
- Nhánh `exp/occlusion-identity-search` không còn trong danh sách branch, nhưng
  commit **`5948218069caed88343cd02819e58c8620591d9b` còn đọc được**.
  Code và báo cáo cũ có thể phục hồi chọn lọc từ object này; không cần viết lại
  toàn bộ hoặc merge cả commit. Ví dụ kiểm chứng chỉ đọc:

  ```powershell
  git show 5948218:docs/research_occlusion_identity/07_EVALUATION_REPORT.md
  git show 5948218:code/scripts/occlusion_identity_diagnostics.py
  ```

- Bản oracle của commit đó là **motorcycle-only input**, fresh600 updates,
 30 warm-up và570 scored frames, tại640. Không so trực tiếp với bảng paper cũ
 dùng prehistory đầy đủ, nhiều class và HOTA@0.5.
- Main đã merge code no-mask, xử lý state suy biến và OC-SORT+CTRV; helper đang
  có là [run_roi_paper.py](../code/scripts/run_roi_paper.py),
  [gt_newcam.py](../code/scripts/gt_newcam.py),
  [seed_bracket.py](../code/scripts/seed_bracket.py). Không giả định helper từ
  commit cũ tương thích nguyên trạng với main mới.
- Camera DuongBaTrac có footage local; window cũ **[10925,11525)** được chọn theo
  mật độ detector, không phải lấy mẫu đại diện ngẫu nhiên. Ba cache existing có
 1600 frame **[9925,11525)**, gồm1000 frame trước window; confidence floor0.1:
  `best.pt448`, `best.pt640`, `yolo11_vn1280`.
- Bundle DuongBaTrac có **825/825 quyết định trống**. Hai bundle camera khác cũng
  chưa review. Con số825 là workload bundle cũ, chưa phải workload sau ROI mới.
- Seed DuongBaTrac union12 output gồm3 detector/size ×4 nhánh của pipeline cũ;
  **không phải union đủ các baseline OC-SORT/BoT-SORT hiện muốn so sánh**.
- Audit leakage cũ tìm **không thấy** overlap của DuongBaTrac với export train
  best.pt đã kiểm. Đây không phải chứng minh tuyệt đối; provenance phiên bản
  train của yolo11_vn vẫn thiếu. Chọn best.pt làm detector chính; checkpoint còn
  lại chỉ là reference có nêu giới hạn nếu đưa vào.
- Tài liệu hiện hành vẫn giữ strict pixel mask và quyết định tạm dừng GT camera
  mới. Các thay đổi tương ứng bên dưới chưa được áp dụng vào PAPER_SCOPE.

Nguồn local: [workflow](PAPER_EXPERIMENT_WORKFLOW.md),
[scope](PAPER_SCOPE.md), [new-camera status](../experiments/gt_newcam/README.md),
[seed evidence](../experiments/seed_bias/evidence.md),
[operating-point evidence](../experiments/operating_point/evidence.md),
[leakage evidence](../experiments/detector_leakage/evidence.md).
Receipt kiểm tra đầu vào nằm ở
[readiness.json](../experiments/q1_diagnostic_plan_20261019/readiness.json).

## 3. Câu hỏi và claim được phép kiểm tra

Tiêu đề làm việc đề xuất:

**Diagnosing Motorcycle Tracking in Dense Mixed Traffic: Detection Quality,
Association Policies, and Annotation Bias**

Ba câu hỏi:

1. Với cùng detector và policy admission, thay đổi chất lượng quan sát còn để
   lại bao nhiêu khó khăn association? Lợi ích của turn rate có tồn tại sau khi
   tách khỏi state representation, gate, NSA và lifecycle không?
2. Ranking/margin tracker nhạy thế nào với annotation membership và nguồn
   pre-label? Kết luận development có lặp lại trên GT camera khác được audit không?
3. Input size và pixel masking làm thay đổi detection/association thế nào? Chỉ
   ghép latency vào accuracy–cost curve nếu đã có phép đo đúng cấu hình cuối.

Không khóa trước câu trả lời “detector chứ không phải motion model”. Có thể kết
luận “quan sát chất lượng thấp hạn chế mạnh kết quả trong các điều kiện đã đo”
hoặc “chưa thấy lợi ích ổn định của turn rate”; không kết luận motion vô ích từ
một phép oracle hay một kết quả không có ý nghĩa thống kê.

Mức đóng góp tối thiểu trong một tuần: controlled diagnostic, audited annotation
limitations và input/mask sensitivity có held-out-camera check. Tuyên bố **đo
causal seed bias** là stretch riêng: cần thiết kế annotation đối chứng, không
được tự coi hoàn tất bằng GT mới. C1/C3 chỉ mô tả trong Discussion nếu đổi scope
được chốt. Severity vẫn ngoài phạm vi; giữ detector Accident class.

## 4. Bốn quyết định trước khi chạy chính thức

| Mục | Khuyến nghị | Trạng thái hiện tại |
|---|---|---|
| 1. GT camera mới | Mở lại DuongBaTrac, yêu cầu hoàn tất/audit100% window trước score | Đề xuất; chưa thay quyết định13/10 |
| 2. Mask | Ưu tiên **không mask pixel** làm primary mới; vẫn lọc bottom-center trước tracker và expire state ngoài ROI. Masked thành ablation, cùng GT/ROI | Đề xuất; chưa đảo lựa chọn14/10 |
| 3. Scope | Diagnostic paper; bỏ real-time khỏi claim chính; C1/C3 không là contribution; title chưa phải kết quả | Đề xuất; chưa sửa manuscript/scope |
| 4. Code | Phục hồi chọn lọc helper vào nhánh `exp/q1-diagnostic-20261019`, giữ current fixes và provenance; không cherry-pick cả5948218 vào main | Có thể thực hiện sau khi chốt execution; hiện chỉ đọc object |

Nghĩa và thầy quyết định venue sau khi xem bằng chứng. Q1 phụ thuộc database,
category và năm cần kiểm chứng khi chọn venue. Không gán quartile hay xác suất
major revision trong kế hoạch này. Không tự gửi email, nộp paper hoặc release.

License là quyết định phát hành riêng: ghi dependency/code/checkpoint provenance,
đọc [điều khoản Ultralytics chính thức](https://www.ultralytics.com/license) theo
phiên bản sử dụng rồi chốt cách phát hành với chủ repo. Chưa tự thêm LICENSE,
không mặc định rằng mọi code/weights/CCTV có cùng quyền phát hành, và không tự
mua dịch vụ. Lệnh không công bố ra ngoài trong đợt nghiên cứu trước chưa được
gỡ: kế hoạch này chỉ commit local, không push.

## 5. Hai đường đánh giá, không trộn số

**H0 — forensic reproduction.** Tái tạo bảng cũ theo đúng cache/GT/config/input
class/prehistory/rounding/ROI đã tạo ra nó. Bắt đầu bằng các arm ở bảng448;
rescore các bảng operating point từ dump có hash, không tính lại detector nếu
cache phù hợp. IDSW/FP/FN phải khớp số nguyên; metric khớp full-precision receipt
trong tolerance đã đăng ký (đề xuất1e-9) và khớp cách làm tròn bảng in. So đúng
HOTA@0.5 với HOTA@0.5; official HOTA19 alpha là endpoint khác. Một phép tính ra
cùng ba chữ số nhưng khác raw dump/config chưa đủ chứng nhận reproduction.

**H1 — diagnostic protocol mới.** Đề xuất motorcycle-only input để loại ảnh hưởng
class-gating khác nhau; fresh600 frames/30 warm-up/570 scored cho mọi arm, cả
detector và oracle. GT phải có đủ600 frame dù30 frame đầu không tính điểm. Dùng
chiều cao box native để chia `<20`, `20–40`, `>=40 px`. Primary: official HOTA
trung bình19 alpha; secondary AssA, DetA, IDF1, MOTA, IDSW, Frag và coverage.
Không gọi H1 là tái lập bảng H0. Đây không phải đánh giá toàn bộ multi-class
application. Nếu scope này đổi, protocol phải sửa trước khi có score mới.

Giữ detector/checkpoint/class map/post-NMS settings và ROI giống nhau trong mỗi
cặp so sánh. Không mask nghĩa là detector thấy ngữ cảnh ngoài polygon, **không
nghĩa là giữ track ngoài ROI**. Cache full-frame có thể lọc lại ROI; cache masked
không thể đổi thành unmasked, hoặc ngược lại, chỉ bằng lọc box. Cache sai weights,
mask, ROI hay floor phải tạo bản mới, không sửa đè file đã đóng băng.

Trước score H1, protocol phải chứa: hashes source/video/weights/GT/cache/code/
config, class mapping, frame/FPS semantics, mask policy, rounding/expiry/solver,
input order, reset/warm-up, metric version, threshold policy, endpoints, split,
budget, GT ambiguity/exclusion rule và correction policy. Hash chỉ cố định byte;
không làm một lựa chọn sau-kết-quả thành preregistration hồi tố.

DuongBaTrac là camera-disjoint với NKKN nhưng đã có density selection và prelabels.
Ghi rõ provenance đó. Chốt method/hyperparameters và mask trên development trước
khi xem score test; tránh để người thiết kế method dùng comparative test previews
để chỉnh phương pháp. Annotator xem nguồn ẩn tên tracker và ID proposal không
được mặc định là đúng. Score locked test một lần bằng một batch các arm đã chốt.
Nếu lỗi mapping/source xác minh được, giữ failed receipt và cho một correction
có log; không cấm sửa lỗi thật chỉ vì đã “chấm một lần”, cũng không retune để thắng.

## 6. Các phép thử tối thiểu và trần compute

Đây là **budget đề xuất**, chưa chạy/chưa khóa. Không mở rộng lưới vì C2 thua.
Đặt640 làm reference diagnostic thực dụng, không gọi là CPU-feasible/real-time
trước khi đo.448/960/1280 là sensitivity, không chọn primary theo điểm test.

| Nhóm | Thiết kế development trên3 đoạn NKKN | Trần cell600 frame |
|---|---|---:|
| Core matrix | ByteTrack, C2, C2ω=0, OC-SORT ×4 size ×2 mask |96|
| Appearance authority | BoT cùng implementation/settings, appearance OFF/ON ×size640/1280 ×2 mask; ON chỉ khi có encoder/checkpoint provenance |24|
| Threshold sensitivity |4 core ×τ={0.3,0.4,0.5,0.6,0.7} ×3 đoạn, chỉ640/no-mask; native rows giữ riêng |60|
| Input interventions | Raw640/no-mask đã có; thêm localization-aligned, confidence intervention và full oracle cho4 core ×3 đoạn |36 thêm|
| Tổng trần mới development | Core/appearance native + sensitivity + intervention; không tính forensic H0 |**216**|

Mỗi arm là một replay độc lập có đúng một update/source frame. Các cell trùng
native policy được ghi reuse receipt, không giả làm replication. Chỉ score locked
test tại640/no-mask với tối đa7 cấu hình đã khóa: ByteTrack, C2, C2ω0,
OC0.5+BYTE, OC0.6+BYTE và BoT OFF/ON. Thêm4 oracle cell cho4 core làm secondary
diagnostic: tối đa **11 cell test**, cùng một batch được khóa trước. Không chọn
ngưỡng hoặc chạy grid search trên DuongBaTrac. Sensitivity test khác chỉ mở khi
đăng ký trước, chưa hứa trong tuần đầu. Không bắt buộc tải dữ liệu mới, retrain
detector hoặc dùng paid compute.

**Threshold semantics.** Với sweep policy chung, high=birth=τ nếu API cho phép;
low floor giữ0.1. OC joint threshold được ghi rõ. Native ByteTrack/C2 high0.5,
birth0.6 giữ thành hàng riêng, cùng hai OC0.5/0.6 cũ. Không đặt high0.3 trong khi
giữ birth0.6 rồi gọi mọi tracker là matched. Chốt exact `>`/`>=`, fuse-score,
min-hits, max-age, duplicate/class policy và source-FPS conversion. Đường cong là
sensitivity; không chọn threshold theo test hay chọn metric nào đang thắng.

**ω=0.** Giữ cùng state representation còn lại, gate, NSA, noise, thresholds,
association, birth/death và input. Cần ràng buộc mean turn-rate, thành phần
covariance/coupling và prediction/update tương ứng sao cho ω không bị measurement
update học lại ở bước sau. Chỉ đặt giá trị khởi tạoω=0 là không đủ. Test đúng
zero-turn limit, finite Jacobian/covariance và cùng lifecycle; ghi rõ đây là
ablation constrained-CTRV, không khẳng định tương đương KF Cartesian của ByteTrack.

**Appearance.** So cùng BoT OFF/ON trước khi quy lợi ích cho encoder. Feature
detector-backbone không được gọi là full dedicated ReID. Nếu không có checkpoint
được xác minh trong nguồn local thì ghi gap, giảm comparison claim; không âm thầm
tải weights hoặc dùng proxy rồi gắn nhãn full method. Một paper diagnostic không
cần thắng mọi SOTA, nhưng không được bỏ cạnh tranh mạnh để tạo câu chuyện.

**Oracle/intervention.** Tracker không nhận GT ID và không thêm box trong khoảng
complete occlusion. Localization-aligned giữ candidate membership/scores, chỉ
snap những box được match one-to-one vào GT geometry. Confidence intervention
giữ boxes/membership nhưng đặt score1 cho **tất cả** proposals, kể cả unmatched;
có thể làm FP/birth tăng, không phải “confidence đúng”. Full oracle thay bằng
các observation GT hiện hữu và score1, bỏ IDs trước deterministic sorting.
GT-assisted diagnostics chỉ là intervention có điều kiện theo annotation. Tác
động không cộng tuyến tính; không cộng các delta thành100% lỗi detection/association.
Sweep score threshold trên full oracle score1 hầu như không thay đổi admission,
nên không diễn giải nó như sensitivity confidence thật.

## 7. GT, seed bias và thời gian của Nghĩa

**Bước đầu:** vẽ ROI và chạy pilot40 case **trên development hoặc calibration
window tách khỏi test**, phân tầng loại lỗi. Đo mean thời gian theo strata,
median/p90 để thấy đuôi dài; đo thêm box editing và raw-frame completeness pass.
Ước tính `Σ N_stratum × mean_time + box/frame_pass + audit + adjudication`, cộng
contingency quản lý được ghi rõ. Không lấy825×một tốc độ trung bình chưa đo để
cam kết11 giờ. Case review không bao gồm mọi box/frame chưa từng được đề xuất.

Sau khi biết ROI, tạo bundle mới có nguồn/ID proposal được ẩn, bổ sung proposals
của baseline được so sánh, giữ bundle825 mục cũ nguyên trạng. Người review có
thể thêm vật thể ngoài union. Mỗi frame trong window phải được rà completeness;
mọi visible track cần class/box/identity consistency. Gắn uncertainty cho quan hệ
ID không quan sát được; không đoán và không vẽ box xuyên complete occlusion.

Audit phải gồm cả raw-video sample không overlay để tìm vật thể mọi tracker bỏ
sót, ID transitions có rủi ro, và adjudication các bất đồng. Nếu chỉ một người
annotate/review, ghi rõ giới hạn; lấy người thứ hai kiểm subset nếu có. Không dùng
agreement giữa tracker và GT như independent annotation agreement. Reviewer
không được biết seed/method khi đưa verdict ở phần blind audit.

Seed bracket cũ là **sensitivity theo các giả định**, chưa phải khoảng tin cậy
cho bias thật hoặc GT đã được “sửa chính xác”. Không gọi union của predictions là
upper bound bảo đảm. Trong tuần này có thể tái tính bracket kèm provenance,
denominator và giới hạn. Controlled seed experiment trên cùng clip, hai seed,
counterbalanced/blinded review và reference adjudication là stretch riêng; nếu
không có thời gian/nhân lực, bỏ claim causal seed effect khỏi đóng góp đã hoàn tất.

## 8. Lịch bảy ngày có dependency và sản phẩm

Ngày1 chỉ bắt đầu sau khi quyết định execution/ROI được chốt và đầu vào sẵn sàng.
Không ghi mặc định là từ19–25/10 nếu human review chưa bắt đầu.

| Ngày | Assistant thực hiện | Nghĩa/người review | Đầu ra và gate |
|---|---|---|---|
|1|Nhánh execution riêng; phục hồi helper chọn lọc; H0 reproduction; xác minh caches; pilot tooling; draft/freeze H1 sau các quyết định|Chốt1–4, ROI, pilot40 có bấm giờ; không xem score test|`reproduction.json`, manifest, time estimate, protocol hash. Sai nguồn/metric thì chưa mở score mới|
|2|Core/interventions/threshold sweep development; ω0 validation; chuẩn bị appearance pair nếu provenance đủ; tạo bundle ROI mới|Review GT camera mới theo workload đo thực|Receipts/test logs; autosave+backup; không score GT dở|
|3|Development scoring full-alpha; audit queue, annotation consistency QA; bracket assumptions; phân tích effect sizes|Hoàn tất toàn bộ selected GT và audit/adjudication; báo cònuncertain|`GT_READY` hoặc dời mốc.70%case chỉ là tiến độ, không là gate khoa học|
|4|Khóa code/GT/config; chạy một batch held-out đã định; lưu mọi kết quả. Không đổi thresholds/mask sau khi xem|Xác nhận export/membership/uncertainty rule đã khóa|`heldout_evaluation.json`; xem kết luận có transfer không, không ép method thắng|
|5–6|Hình và bảng tự sinh từ receipt; viết bản chẩn đoán khi được giao writing task; related work nguồn gốc rõ; latency mô tả nếu đo hợp lệ|Đọc claim-to-evidence checklist, đánh dấu suy diễn/GT chưa chắc|Bản gửi thầy với limitations/negative results; không thêm claim hồi tố|
|7|Build LaTeX/Overleaf artifact, kiểm số/bib/package, ghi source commit; tách release/license khỏi build local|Đọc cuối, thầy quyết venue/sẵn sàng nộp|Gói local reproducible. Không tự gửi thầy, submit, merge main hoặc publish|

**Latency:** nếu tiếp tục contribution accuracy–cost, đo đúng best.pt, size,
mask, preprocessing, CPU threads và tracker cuối; một arm/process, warm-up và
3 trial, báo decode+detector+tracker cùng p50/p95/FPS. Không dùng replay timing
hoặc COCO weights khác làm end-to-end evidence. Counter `% Processor Performance`
là thông tin host, không một mình chứng minh thermal throttling. Nếu host không
ổn định thì lưu trạng thái và bỏ real-time claim; không chi hết tuần chạy lại.

**Thống kê:** frame liền nhau không độc lập. Chỉ có một camera test thì báo
per-camera/per-sequence effect sizes và giới hạn; không tạo CI tổng quát hóa bằng
cách xem hàng nghìn box như mẫu độc lập. Moving-block bootstrap chỉ là bất định
có điều kiện trong clip; nếu cắt/nối block và tách ID thì estimand thay đổi, không
được gắn nhãn CI cho full-sequence global HOTA/IDF1 mà chưa xác minh. Controlled
seed study phải tính đơn vị annotation/clip/reviewer, không dùng box count làmN.

## 9. Gate dừng và tiêu chí hoàn tất

- **G0 provenance:** tìm thấy đúng video/weights/GT/cache/code/metric. Thiếu một
  input bắt buộc thì chỉ làm phần độc lập; không lấp số bằng bản gần giống.
- **G1 reproduction:** mismatch thì điều tra mapping/rounding/solver/versions,
  giữ trace và chỉ sửa một lần cho mỗi lỗi được xác minh. Chưa khớp thì không
  viết paper mới dựa trên số đó; các việc audit không phụ thuộc vẫn có thể tiếp tục.
- **G2 workload:** pilot cho thấy vượt giờ review khả dụng thì kéo timeline hoặc
  đăng ký lại phạm vi dữ liệu **trước khi mở metric**. Không coi70%cases là GT_READY.
- **G3 GT_READY:** đủ review toàn window, raw completeness audit, identity
  adjudication/uncertainty handling, ROI/hash/export và người review ký nhận.
- **G4 held-out:** kết luận trái development thì báo trái; không bỏ camera,
  đổi primary metric hay retune rồi gọi lần sau vẫn là test độc lập.
- **G5 manuscript:** mỗi claim có receipt/source; không gọi source25fps thành
  measured25FPS. Không replace mọi số30→25: buffer/max-age/block size và baseline
  default là tham số có đơn vị riêng, cần kiểm code trước khi đổi thời lượng.
- **G6 publication:** thầy/author chốt scope, venue, license và dữ liệu được phép
  công bố. Đến hạn nhưng thiếu gate thì gửi **bản thảo có giới hạn để đánh giá**,
  không tự tuyên bố submission-ready hoặc chuyển venue để né vấn đề.

Sản phẩm tối thiểu của tuần: reproduction manifest; frozen H1 protocol; GT export
và audit receipt nếu hoàn tất; các raw score/negative results; một bảng claim→
evidence; bản thảo chẩn đoán và zip build nếu có writing authorization. Không
đếm protocol dự thảo, prelabels chưa review hay script tồn tại là thí nghiệm xong.

## 10. Ba hành động tiếp theo theo giá trị khoa học

1. **Chốt scope/ROI và đo pilot review**, rồi khóa protocol. Việc này kiểm chứng
   liệu phần việc không thể tự động hóa có vừa lịch hay không.
2. **H0 replay + H1 diagnostics có đối chứng**, đặc biệt threshold semantics,
   ω0 và oracle từng điều kiện. Đích là loại lời giải thích sai, không tăng điểm.
3. **Hoàn tất/audit camera-disjoint GT, chấm locked batch rồi mới viết claim.**
   Nếu GT hoặc kết luận không đủ mạnh, điều chỉnh thời gian/phạm vi cùng thầy.
