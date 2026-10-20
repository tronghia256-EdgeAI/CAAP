# Hồ sơ detector được giữ để làm lại

`weights/detector.pt` là bản sao byte-for-byte của checkpoint `best.pt` đã có
trước reset. Các file ở đây nhận diện dataset package, tham số, checkpoint khởi
tạo và metric của lượt train đó. Không đổi nội dung các receipt gốc.

Đây là provenance của model đang có, không phải GT tracking hoặc kết quả paper
mới. Output hình/batch preview và toàn bộ thư mục train cũ nằm trong backup
ngoài repo; không tự nhập lại vào một evaluation mới.
