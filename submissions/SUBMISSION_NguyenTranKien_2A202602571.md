# BÁO CÁO KẾT QUẢ THỰC HÀNH CÁ NHÂN — SENSOR REALITY SPRINT (DAY 04)
## Môn học: AI20K - Track 4: ADAS Sensing & Estimation (VinUni)

* **Họ và tên:** Nguyễn Trần Kiên
* **Mã sinh viên (MSSV):** `2A202602571`
* **Nhóm thực hiện:** Nhóm 01 (4 thành viên)
* **Vai trò trong nhóm:** **Safety State Machine & Fallback Lead** — Chịu trách nhiệm thiết kế bộ điều khiển Trigger State Machine 4 cấp độ (Level S0-S3), chiến lược ngắt liên kết và Fallback LiDAR-only AEB, tuân thủ tiêu chuẩn an toàn ISO 26262 ASIL-D & SOTIF ISO 21448.
* **Repository GitHub nhóm:** `https://github.com/huybla166/K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint`
* **Lệnh chạy tái hiện:** `python scripts/run_calibration_drift.py`

---

### 1. Problem (Vấn đề & Bối cảnh an toàn hệ thống)
- **Nền tảng & Cảm biến:** Xe tự lái ADAS với Camera Full HD và LiDAR 3D.
- **Rủi ro an toàn thực tế:** Hiện tượng trôi dạt góc ngoại thông số (Calibration Drift) là "kẻ giết người thầm lặng" đối với xe tự lái vì các hệ thống giám sát phần cứng thông thường (Hardware Watchdog) không thể phát hiện lỗi (cả Camera và LiDAR đều không bị mất nguồn, không đứt dây).
- **Hậu quả đe dọa an toàn:** Sự sai lệch hình học khiến thuật toán AEB gán nhầm khoảng cách của mặt đường xa (50m) cho xe phía trước (10m) $\to$ Xe không kịp phanh khẩn cấp gây tai nạn nghiêm trọng; hoặc ngược lại gán nhầm cọc tiêu ven đường vào giữa làn $\to$ Phanh gấp bất ngờ (Phantom Braking).

---

### 2. Method (Thuật toán SOTA & Kiến trúc an toàn)
- **Paper/Repo SOTA chuẩn môn học:** CalibRefine (*IEEE TIM 2026 / XCalib repo*), DF-Calib (*arXiv:2504.01416*), Galibr (*IEEE IV 2024*).
- **Chuỗi tín hiệu giám sát an toàn (Sensor Health Signal Chain):**
  $$\text{[Raw Streams]} \to \text{[Time-Sync PTP < 20ms]} \to \text{[Edge-Depth Chamfer Loss + Disparity]} \to \text{[Continuous EMA Filter]} \to \text{[State Machine Gate]} \to \text{[Control Fallback]}$$
- **Mô hình tính toán sai số:** Dựa trên kết quả đo đạc Mean Reprojection Error (MRE) và Point-in-Bbox Recall để làm đầu vào kích hoạt các cổng logic an toàn.

---

### 3. Benchmark (Dữ liệu số đo nền tảng cho State Machine)
- Dữ liệu thực nghiệm 1080p quét góc lệch từ $0.0^\circ \to 2.5^\circ$ cung cấp cơ sở để thiết lập các ngưỡng kích hoạt chính xác:
  - *Ngưỡng an toàn:* $MRE < 10.0\text{ px}$ (Góc lệch $< 0.4^\circ$, Recall $> 85\%$).
  - *Ngưỡng cảnh báo:* $10.0\text{ px} \le MRE < 20.0\text{ px}$ (Góc lệch $0.4^\circ - 0.9^\circ$, Recall $70\% - 85\%$).
  - *Ngưỡng kích hoạt Re-calib:* $20.0\text{ px} \le MRE < 30.0\text{ px}$ (Góc lệch $0.9^\circ - 1.6^\circ$, Recall $50\% - 70\%$).
  - *Ngưỡng cắt khẩn cấp:* $MRE \ge 30.0\text{ px}$ (Góc lệch $> 1.6^\circ$, Recall $< 50\%$).

---

### 4. Failure Case & Ứng phó tình huống đặc biệt
- **Ca thử nghiệm phân tích:** Xe gặp gờ giảm tốc hoặc ổ gà đúng đoạn đường có biển cấm dừng đỗ trong khu đô thị.
- **Phương án giải quyết của hệ thống:**
  1. *Không phanh chết tại chỗ:* Bản thân LiDAR đo vật lý vẫn đúng 100%, Camera đọc biển cấm vẫn chuẩn 100%. Xe giảm tốc độ xuống 20 km/h và tiếp tục lăn bánh.
  2. *Tận dụng cơ hội hợp pháp:* Chạy thuật toán CalibRefine (0.5s) ngay khi dừng chờ đèn đỏ ở ngã tư tiếp theo.
  3. *Tự cân chỉnh khi đang chạy:* Dùng các vật thể cố định hai bên đường (tòa nhà, cột đèn) để chạy bộ lọc Kalman EKF liên tục tự bù góc lệch.

---

### 5. Engineering Decision (Kiến trúc State Machine 4 Cấp Độ)
- **Thiết kế 4 mức xử lý (S0 - S3):**
  - **LEVEL S0 (NOMINAL):** $MRE < 10\text{ px}$, Recall $> 85\%$ $\to$ Duy trì trạng thái lái tự động bình thường.
  - **LEVEL S1 (WARNING):** $10 \le MRE < 20\text{ px}$ $\to$ Tăng covariance của Camera, giảm trọng số camera trong bộ lọc EKF, gửi cờ cảnh báo `CALIB_DEGRADED` về Domain Controller.
  - **LEVEL S2 (RE-CALIB):** $20 \le MRE < 30\text{ px}$ $\to$ **KHOÁ tính năng tự chuyển làn cao tốc (NOA)**, kích hoạt luồng chạy ngầm của CalibRefine/DF-Calib trên GPU Jetson Orin để tự động khôi phục ma trận ghép nối.
  - **LEVEL S3 (CRITICAL):** $MRE \ge 30\text{ px}$ HOẶC $Recall < 50\%$ $\to$ **LẬP TỨC NGẮT HOÀN TOÀN EARLY FUSION!** Chuyển xe về **Dual-Tracker độc lập** (LiDAR-only cho phanh khẩn cấp AEB; Camera-only cho đọc biển báo/làn đường) và phát âm thanh Takeover Request cho tài xế can thiệp.
- **Tiêu chuẩn áp dụng:** Đạt chuẩn an toàn chức năng quốc tế **ISO 26262 ASIL-D** và an toàn tính năng dự định **ISO 21448 (SOTIF)**.
