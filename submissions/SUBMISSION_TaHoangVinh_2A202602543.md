# BÁO CÁO KẾT QUẢ THỰC HÀNH CÁ NHÂN — SENSOR REALITY SPRINT (DAY 04)
## Môn học: AI20K - Track 4: ADAS Sensing & Estimation (VinUni)

* **Họ và tên:** Tạ Hoàng Vinh
* **Mã sinh viên (MSSV):** `2A202602543`
* **Nhóm thực hiện:** Nhóm 01 (4 thành viên)
* **Vai trò trong nhóm:** **Failure Case & SOTA Literature Analyst** — Chịu trách nhiệm bóc tách trực quan hóa Point-Painting (Case 1 $\to$ Case 3), phân tích điểm gãy nguy hiểm tại 1.0° & 2.0°, nghiên cứu chuyên sâu 3 công trình SOTA: CalibRefine (IEEE TIM 2026), DF-Calib (arXiv:2504.01416), Galibr (IEEE IV 2024).
* **Repository GitHub nhóm:** `https://github.com/huybla166/K4-Track4-Day04-Team01-Sensor-Reality-Sprint`
* **Lệnh chạy tái hiện:** `python scripts/run_calibration_drift.py`

---

### 1. Problem (Vấn đề & Bối cảnh lỗi thực tế)
- **Nền tảng & Cảm biến:** Hệ thống xe tự hành ADAS đa cảm biến (Camera 1080p + LiDAR 32-beam).
- **Hiện tượng lỗi:** Khi xe di chuyển trong khu đô thị (gặp ổ gà, gờ giảm tốc), gá đỡ cảm biến bị rung lắc vi mô khiến góc xoay lệch $0.5^\circ - 2.0^\circ$.
- **Hệ quả đối với nhận diện:** Sự bất đối xứng trong cảm biến: Cục LiDAR vẫn đo khoảng cách vật lý chuẩn xác 100%, Camera vẫn đọc biển báo chuẩn 100%, nhưng module ghép nối (Sensor Fusion) bị hỏng hoàn toàn do gán sai ngữ nghĩa không gian.

---

### 2. Method (Bóc tách kiến trúc SOTA: CalibRefine & XCalib)
- **Kiến trúc mạng 4 giai đoạn của CalibRefine:**
  1. *Common Feature Discriminator (CFD):* Trích xuất đặc trưng vị trí tương đối, visual appearance embedding và nhãn ngữ nghĩa để tìm cặp điểm tương ứng camera-LiDAR tin cậy.
  2. *Coarse Homography:* Ước lượng ma trận đồng phẳng sơ bộ từ các điểm tương ứng được chọn lọc.
  3. *Iterative Refinement:* Cập nhật và tối ưu liên tục góc xoay và vector tịnh tiến qua các frame tiếp theo.
  4. *ViT Cross-Attention:* Dùng Vision Transformer với cơ chế chú ý chéo bù trừ biến dạng phi mặt phẳng (non-planar distortions).
- **Triển khai Edge Hardware:** Hỗ trợ xuất ONNX và TensorRT FP16 chạy trên NVIDIA Jetson AGX Orin / Thor.

---

### 3. Benchmark (Bằng chứng số liệu & Điểm gãy sụp đổ)
- **Phát hiện các Điểm gãy nguy hiểm (Failure Breakpoints):**
  - *Điểm gãy 1 (Tại $\Delta\theta = 1.0^\circ$, MRE $\approx 24\text{ px}$):* Bounding Box IoU sụt xuống **0.461**, Point Recall của người đi bộ 25m giảm xuống **61.5%** $\to$ Đây là điểm kích hoạt tối ưu để bật thuật toán Online Re-calibration (Mức S2).
  - *Điểm gãy 2 (Tại $\Delta\theta = 2.0^\circ$, MRE $\approx 48\text{ px}$):* Point Recall của người đi bộ 25m sụt thảm hại xuống **16%**, xe xa 50m rớt về **17%** $\to$ Buộc phải **ngắt hoàn toàn Early Fusion** để bảo vệ hệ thống phanh AEB.
- **Trực quan hóa Point-Painting (Hình 2 trong slide môn học):** Thể hiện rõ chùm điểm laser màu đỏ (Outliers) bị văng ra khỏi khung hình hộp chữ nhật màu xanh khi góc lệch tăng dần.

---

### 4. Failure Case & Giới hạn của SOTA (Challenge)
- **Tình huống thuật toán tự cân chỉnh bị fail:**
  - *Môi trường phi cấu trúc (Textureless):* Đường hầm trơn nhẵn, sương mù dày đặc hoặc ban đêm tối mù không có viền cạnh ảnh.
  - *Suy biến mặt phẳng (Planar Degeneracy):* Đường cao tốc phẳng lì không có cột đèn, cây cối, xe cộ hai bên đường. Hàm mất mát Chamfer distance rơi vào điểm kỳ dị không thể hội tụ.
- **Phân tách rạch ròi bằng chứng:**
  - *[Nhóm tự đo]:* Đo được sự dịch chuyển của điểm laser từ $0.0\text{ px} \to 47.93\text{ px}$ trên tập dữ liệu thực tế nuScenes.
  - *[Paper Dong et al. CVPR 2023 & Galibr]:* Chỉ ra rằng khi góc lệch vượt quá $10^\circ$, vùng hội tụ (Basin of Attraction) của các giải thuật phi tuyến sẽ bị phá vỡ hoàn toàn.

---

### 5. Engineering Decision (Đề xuất kỹ thuật)
- **Cơ chế cảnh báo thông minh:** Sử dụng bộ đệm EMA (Exponential Moving Average) để lọc nhiễu rung chấn tức thời, chỉ kích hoạt Re-calibration khi sai số duy trì liên tục qua 10 frame.
- **Giải quyết tình huống cấm dừng đỗ:** Khi gặp gờ giảm tốc ở đoạn đường có biển cấm đỗ, hệ thống không dừng xe mà tận dụng thuật toán *Continuous Online Calibration (CalibRefine)* để tự cân chỉnh ngay trong lúc xe đang lăn bánh 20 km/h, hoặc tận dụng 0.5s dừng đèn đỏ tiếp theo.
