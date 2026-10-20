# ByteTrack — nguồn và patch tương thích

Nguồn: `ifzhang/ByteTrack`, các file trong `yolox/tracker/`.
Giữ baseline này để có công cụ tracking tối thiểu khi thiết kế lại nghiên cứu.
Các bản sao upstream local và pipeline nghiên cứu cũ đã đưa ra ngoài repo.

Các thay đổi của bản vendor đang giữ:

- Import tương đối, bỏ phụ thuộc YOLOX/torch khỏi tracker.
- Thay `np.float` bằng `float` cho NumPy mới.
- Thay `lap` bằng SciPy assignment trên extended cost matrix; tie ở ngưỡng
  có thể được giải khác, nên không hứa dump byte-identical mọi trường hợp.
- IoU bằng NumPy, giữ quy ước `+1` pixel của code gốc.
- Input NumPy N×5 hoặc N×6, có `class_id` dạng metadata.
- Giữ hai-stage association, state lifecycle, duplicate removal và các hook
  mặc định của bản vendor. Hook không tự bật một motion model mới.

`tests/test_vendor_bytetrack.py` kiểm ID ổn định, empty frames, input contract
và matching. Đây là kiểm tra code bằng synthetic data, không phải kết quả paper.
