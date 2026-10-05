# BÁO CÁO THỰC NGHIỆM LAB DAY 04 — SENSOR BENCHMARK & ROBUSTNESS
## Chủ đề 3 (T3): Calibration Drift Impact on Multi-Sensor Fusion (Camera - LiDAR) in ADAS

* **Nhóm thực hiện:** Nhóm 5 thành viên (Lớp K04 - L3/4 - Phase 2 - Track 4)
  1. **Phạm Quang Huy (Trưởng nhóm / Metric & Geometry Lead)**
  2. **Trần Trung Kiên (Data & Calibration Perturbation Lead)**
  3. **Nguyễn Thành Danh (Benchmark Runner & Evaluation Lead)**
  4. **Lê Quốc Việt (Literature Reviewer & Method Analyst)**
  5. **Hoàng Anh Tuấn (Failure Case & System Safety Lead)**
* **Repository bài làm:** `D:\AI in Action\Labs\Lab-Day04-Sensor-Robustness`

---

### 1. PROBLEM (BÀI TOÁN & TÌNH HUỐNG LỖI SENSOR THỰC TẾ)
* **Nền tảng (Platform):** Xe tự hành / Xe trợ lái thông minh (ADAS Level 3/4).
* **Tính năng mục tiêu:** Nhận diện chướng ngại vật 3D và Phanh khẩn cấp tự động (3D Object Detection & Autonomous Emergency Braking - AEB).
* **Cảm biến sử dụng:** Hệ thống đa cảm biến gồm Camera góc rộng phía trước (`CAM_FRONT`, $1600 \times 900$) và LiDAR 32-beam nóc xe (`LIDAR_TOP`).
* **Tình huống lỗi vật lý (Physical Failure Case):** Trôi lệch ma trận hiệu chuẩn ngoại (Extrinsic Calibration Drift).
  * Trong điều kiện xe vận hành thực tế trên đường, các rung lắc cơ học khi đi qua ổ gà, gờ giảm tốc, va chạm nhẹ hoặc biến dạng nhiệt của khung giá đỡ làm sai lệch góc đặt của Camera so với LiDAR.
  * Góc lệch xoay trục $\Delta \text{yaw} \in [0.5^\circ, 5.0^\circ]$ và dịch chuyển tịnh tiến $\Delta x \in [2, 20\text{ cm}]$ dù cả hai cảm biến vẫn hoạt động bình thường về mặt phần cứng và truyền dữ liệu.

---

### 2. METHOD (NGUỒN THAM KHẢO & PHƯƠNG PHÁP)
* **Paper tham khảo chuẩn:**
  1. *Dong et al. (CVPR 2023 - S5 trong danh mục gợi ý):* "Benchmarking Robustness in 3D Object Detection: KITTI-C, nuScenes-C, Waymo-C".
  2. *Galibr (2024) / CalibRefine (2025):* "Targetless and Real-time Online LiDAR-Camera Extrinsic Recalibration for Autonomous Driving".
* **Đặc tả thuật toán:**
  * **Input:** Đám mây điểm LiDAR $P_{\text{lidar}} \in \mathbb{R}^{N \times 3}$, ảnh Camera $I \in \mathbb{R}^{H \times W \times 3}$, ma trận nội thông số Camera $K \in \mathbb{R}^{3 \times 3}$, ma trận ngoại thông số danh định $(R, t) \in SE(3)$.
  * **Phép chiếu hình học:**
    $$P_{\text{cam}} = R^{\top} (P_{\text{lidar}} - t)$$
    $$[u, v, 1]^{\top} = \frac{1}{z} K \cdot P_{\text{cam}}$$
  * **Output:** Tọa độ pixel 2D $(u, v)$ của các điểm LiDAR trên ảnh camera để thực hiện gán đặc trưng (Point-to-Pixel Association).
* **Giả định & Limitation của nguồn:**
  * Giả định: Các cảm biến đã được đồng bộ thời gian hoàn hảo (zero time-offset) và mặt phẳng ảnh không bị méo phi tuyến tính lớn.
  * Limitation: Khi góc lệch vượt quá $1.5^\circ$, các phương pháp Feature Matching truyền thống không thể tự tìm điểm tương đồng để bù trừ nếu không có thuật toán tối ưu hóa hình học phi tuyến tính toàn cục.

---

### 3. BENCHMARK (THIẾT KẾ ĐỐI CHỨNG & SỐ LIỆU ĐO ĐẠC)
* **Tập dữ liệu kiểm thử:** Cặp khung hình đồng bộ `CAM_FRONT` và `LIDAR_TOP` (34.688 điểm 3D) từ tập chuẩn `nuScenes v1.0-mini`.
* **Lệnh chạy thực nghiệm:**
  ```bash
  python scripts/run_calibration_drift.py
  ```
* **Bảng kết quả số liệu đo đạc thực tế (Chạy trực tiếp tại lớp):**

| Điều kiện kiểm thử | Góc xoay ($\Delta \text{yaw}$) | Tịnh tiến ($\Delta x$) | Mean Reprojection Error (px) | Max Reprojection Error (px) | Vehicle Point Retention (%) | Vehicle Assoc Drop (%) | Fusion mAP Proxy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Chuẩn)** | **$0.0^\circ$** | **0 cm** | **0.00 px** | **0.00 px** | **100.0%** | **0.0%** | **100.0%** |
| **Drift L1 (Rung nhẹ)** | $0.5^\circ$ | 2 cm | **4.19 px** | 8.72 px | 100.0% | 0.0% | **95.34%** |
| **Drift L2 (Lệch vừa)** | $1.0^\circ$ | 5 cm | **8.50 px** | 17.92 px | 99.29% | 0.71% | **86.50%** |
| **Drift L3 (Lệch nặng)** | $2.0^\circ$ | 10 cm | **16.91 px** | 36.07 px | 98.35% | 1.65% | **62.15%** |
| **Drift L4 (Cực nặng)** | $3.5^\circ$ | 15 cm | **29.07 px** | 58.58 px | 94.80% | 5.20% | **14.67%** |
| **Drift L5 (Failure)** | $5.0^\circ$ | 20 cm | **41.13 px** | **83.23 px** | 92.43% | 7.57% | **0.00%** |

* **Định nghĩa Metric:**
  * `Mean Reprojection Error (px)`: Khoảng cách Euclidean trung bình giữa tọa độ chiếu gốc và tọa độ chiếu sau khi bị lệch.
  * `Vehicle Assoc Drop (%)`: Tỷ lệ các điểm LiDAR ban đầu thuộc thân xe bị văng ra ngoài ranh giới hình học do lệch góc.
  * `Fusion mAP Proxy (%)`: Ước lượng mức độ duy trì độ chính xác nhận diện của mô hình Fusion đa cảm biến.

---

### 4. FAILURE CASE (PHÂN TÍCH TÌNH HUỐNG LỖI CỤ THỂ)
* **Tình huống chọn phân tích:** **Drift L3 ($\Delta \text{yaw} = 2.0^\circ, \Delta x = 10\text{ cm}$)** so với **Drift L4 ($3.5^\circ$)**.
* **Phân biệt rành mạch giữa Tự đo và Nguồn:**
  * **[Nhóm tự đo được tại lớp]:** Ở mức lệch $2.0^\circ$, sai số chiếu lại hình học trung bình đo được là **$16.91\text{ px}$** (Max $36.07\text{ px}$). Khi tăng lên $3.5^\circ$, sai số tăng vọt lên **$29.07\text{ px}$** (Max $58.58\text{ px}$). Đám mây điểm LiDAR của chiếc xe tải phía trước bị dịch chuyển hẳn sang phần đường của dải phân cách trên ảnh Camera (minh chứng: `results_t3/calibration_drift_overlays.png`).
  * **[Paper Dong et al., CVPR 2023 cho biết]:** Các mạng Fusion Camera-LiDAR dạng dense fusion (như BEVFusion) bị sụt giảm từ **$18\%$ đến $42\%$ mAP** khi sai số extrinsic vượt ngưỡng dung sai 5-10 pixel vì thông tin chiều sâu 3D bị chiếu nhầm vào background.
* **Hạn chế của bài thử nghiệm (Limitation) & [Suy luận kỹ thuật]:**
  * *Hạn chế:* Phép thử thực hiện trên tập ảnh ban ngày với góc xoay quanh trục thẳng đứng Z (Yaw), chưa mô phỏng rung chấn 6 bậc tự do (6-DoF) động lực học theo thời gian thực.
  * *[Suy luận kỹ thuật]:* Khi điểm LiDAR của xe trước bị chiếu lệch $16-36$ pixel, thuật toán AEB sẽ gán nhầm khoảng cách của mặt đường cho chiếc xe, dẫn đến tính sai Time-to-Collision (TTC) và có thể gây phanh khẩn cấp đột ngột (phantom braking) hoặc đâm va.

---

### 5. ENGINEERING DECISION (QUYẾT ĐỊNH KỸ THUẬT & HỆ THỐNG FALLBACK)
Dựa trên bằng chứng định lượng từ thực nghiệm, nhóm đề xuất kiến trúc phòng vệ 3 cấp độ:

1. **Ngưỡng cảnh báo giám sát (Sensor Health Monitoring):**
   * Giám sát liên tục chỉ số tương quan viền (Edge-Depth Discontinuity Alignment).
   * **Ngưỡng Warning:** Sai số chiếu lại $\ge 10\text{ px}$ (tương ứng $\Delta \text{yaw} \ge 1.0^\circ$). Hệ thống ghi log cảnh báo `EXTRINSIC_DRIFT_WARNING` và lập lịch chạy thuật toán cân chỉnh lại.
2. **Cơ chế Fallback ngắt kết nối an toàn (Graceful Degradation):**
   * **Ngưỡng Emergency:** Sai số chiếu lại $\ge 20\text{ px}$ (tương ứng $\Delta \text{yaw} \ge 2.0^\circ$, nơi mAP proxy tụt dưới 65%).
   * **Hành động ngắt:** Lập tức **ngắt module Camera-LiDAR Fusion**, chuyển hệ thống về chạy **LiDAR-only** độc lập cho tác vụ đo khoảng cách phanh AEB (vì LiDAR đo khoảng cách vật lý độc lập vẫn chuẩn xác) và **Camera-only** cho việc đọc biển báo. Không cho phép ghép đặc trưng chéo để loại bỏ triệt để nguy cơ nhận diện vật thể ma.
3. **Hiệu chuẩn tự động trực tuyến (Online Auto-Recalibration):**
   * Triển khai module hiệu chuẩn không cần bàn chuẩn (Targetless Calibration - Galibr 2024) tự động chạy khi xe dừng chờ đèn đỏ để phục hồi ma trận $R, t$.
* **Kế hoạch kiểm chứng vòng tiếp theo:** Chạy mô phỏng trên 1000 km dữ liệu CARLA/nuScenes, đo tỷ lệ kích hoạt phanh sai (False Trigger Rate) trước và sau khi áp dụng cơ chế Fallback; đảm bảo thời gian hội tụ cân chỉnh lại $< 500\text{ ms}$.
