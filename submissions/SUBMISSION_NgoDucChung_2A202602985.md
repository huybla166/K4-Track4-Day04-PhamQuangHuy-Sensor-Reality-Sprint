# BÁO CÁO KẾT QUẢ THỰC HÀNH CÁ NHÂN — SENSOR REALITY SPRINT (DAY 04)
## Môn học: AI20K - Track 4: ADAS Sensing & Estimation (VinUni)

* **Họ và tên:** Ngô Đức Chung
* **Mã sinh viên (MSSV):** `2A202602985`
* **Nhóm thực hiện:** Nhóm 01 (4 thành viên)
* **Vai trò trong nhóm:** **Data & Benchmark Evaluation Lead** — Chịu trách nhiệm xử lý tập dữ liệu nuScenes v1.0-mini, xây dựng bộ mô phỏng rung chấn quét góc 0°–2.5° và tịnh tiến 0–15cm, trích xuất log, xuất CSV và 4 đồ thị sai số.
* **Repository GitHub nhóm:** `https://github.com/huybla166/K4-Track4-Day04-Team01-Sensor-Reality-Sprint`
* **Lệnh chạy tái hiện:** `python scripts/run_calibration_drift.py`

---

### 1. Problem (Vấn đề kỹ thuật từ góc nhìn dữ liệu)
- **Nền tảng & Cảm biến:** Camera Full HD 1080p ($f_x = 1350\text{ px}$) gắn kính lái và LiDAR 3D 32 chùm tia nóc xe.
- **Hiện tượng trôi dạt trong dữ liệu:** Khi có rung chấn cơ học, dữ liệu thô từ hai cảm biến vẫn đẩy về qua bus Ethernet/CAN bình thường. Tuy nhiên, ma trận không gian giữa hai cảm biến bị lệch $\Delta\text{yaw} = 0.5^\circ - 2.5^\circ$.
- **Hệ quả đo được:** Sự sai lệch này phá vỡ tính liên kết không gian: điểm phản xạ laser rơi ra ngoài bounding box 2D của vật thể trên ảnh camera, khiến mạng PointPainting gán nhầm đặc trưng mặt đường cho xe cộ.

---

### 2. Method (Thuật toán kiểm thử & Pipeline)
- **Paper/Repo SOTA chuẩn môn học:** CalibRefine (*IEEE TIM 2026 / XCalib repo*), DF-Calib (*arXiv:2504.01416*), Galibr (*IEEE IV 2024*).
- **Pipeline xử lý dữ liệu thực nghiệm:**
  1. Load cặp dữ liệu đồng bộ thời gian từ nuScenes: `CAM_FRONT` (1600x900 / 1080p) và `LIDAR_TOP` (34.688 điểm 3D).
  2. Bơm nhiễu ngoại thông số nhân tạo (Perturbation Injection): Góc xoay quanh trục thẳng đứng $\Delta\theta_z \in [0.0^\circ, 2.5^\circ]$ (bước 0.1°) và tịnh tiến trục ngang $\Delta x \in [0, 15\text{ cm}]$.
  3. Chiếu các điểm 3D lên không gian 2D theo ma trận xoay bị lệch $R_{\text{pert}}$ và tính sai số Euclid $MRE = \sqrt{(u - u_0)^2 + (v - v_0)^2}$.

---

### 3. Benchmark (Kết quả định lượng & Bảng số liệu chi tiết)
- **Kết quả đo đạc chính xác từ kịch bản kiểm thử (Lưu tại `results/calibration_drift_metrics.csv` và `results/image1.png`):**
  - *Mức Baseline ($0.0^\circ$):* $MRE = \mathbf{0.00\text{ px}}$, Point-to-Box Recall = **100.0%**, Bounding Box IoU = **1.000**.
  - *Mức L1 ($0.5^\circ$):* $MRE = \mathbf{11.99\text{ px}}$, Recall = **85.7%**, IoU = **0.667** (Hệ thống nằm trong ngưỡng cảnh báo nhẹ).
  - *Mức L2 ($1.0^\circ$):* $MRE = \mathbf{23.97\text{ px}}$, Recall = **68.9%**, IoU = **0.461** $\to$ **Ngưỡng kích hoạt Re-calibration (Mức S2)**.
  - *Mức L3 ($2.0^\circ$):* $MRE = \mathbf{47.93\text{ px}}$, Recall = **41.3%**; Đặc biệt: Người đi bộ 25m rớt về **16%**, xe 50m rớt về **17%** $\to$ **Mức nguy hiểm nghiêm trọng (Mức S3)**.
- **Kiểm chứng quy luật 1/Z của tịnh tiến:** Khi tịnh tiến lệch 10cm, sai số ở vật thể 10m là **13.99 px**, nhưng ở cự ly 50m chỉ còn **2.78 px** (giảm theo tỷ lệ nghịch đảo $1/Z$).

---

### 4. Failure Case (Phân tích ca lỗi nguy hiểm nhất)
- **Ca thử nghiệm phân tích:** Lệch $2.0^\circ$ góc xoay (Mức S3).
- **Bằng chứng dữ liệu:**
  - *[Tự đo tại lớp]:* Sai số chiếu lại cực đại vượt quá $80\text{ px}$ ở các góc viền ảnh. Trên ảnh camera, toàn bộ chùm điểm laser của xe tải phía trước trôi lệch hoàn toàn sang làn đường trống bên cạnh (Hình minh họa: `results/image2.png`).
  - *[Tác động tới AI]:* Mạng nhận diện 3D không tìm thấy điểm laser nào bên trong Bbox người đi bộ ở khoảng cách 25m, dẫn đến hoàn toàn mất dấu vật thể (False Negative).

---

### 5. Engineering Decision (Đề xuất kỹ thuật dựa trên số đo)
- **Cơ chế giám sát dữ liệu:** Bổ sung metric `sensor_health_disparity` tính toán độ lệch trung bình giữa trọng tâm 2D và điểm chiếu 3D theo chu kỳ 200ms.
- **Chiến lược ngưỡng kích hoạt:**
  - Khi $MRE \ge 20\text{ px}$ ($IoU < 0.55$): Lập tức gửi tín hiệu đến ECU để kích hoạt luồng chạy ngầm của CalibRefine/DF-Calib.
  - Khi $MRE \ge 30\text{ px}$ ($Recall < 50\%$): Cắt hoàn toàn kênh Early Fusion, chuyển xe sang chế độ an toàn LiDAR-only cho phanh AEB.
