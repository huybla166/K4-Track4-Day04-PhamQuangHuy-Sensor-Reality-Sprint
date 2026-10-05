# BÁO CÁO CÁ NHÂN — LAB DAY 04: SENSOR ROBUSTNESS & CALIBRATION DRIFT
* **Học viên:** Hoàng Anh Tuấn
* **Vai trò trong nhóm:** Failure Case & System Safety Lead
* **Đóng góp chính:** Phân tích visual failure case tại mức lệch 2.0 độ, xây dựng cơ chế ngắt khẩn cấp Fallback sang LiDAR-only khi Reprojection Error >= 20 px.
* **Chủ đề nhóm:** Chủ đề 3 (T3) — Calibration Drift Impact on Multi-Sensor Fusion (Camera - LiDAR) in ADAS

---

### 1. Problem (Bài toán & Tình huống lỗi)
- **Nền tảng & Cảm biến:** Xe tự lái ADAS sử dụng cặp cảm biến Camera trước (CAM_FRONT) và LiDAR nóc xe (LIDAR_TOP) để phát hiện chướng ngại vật 3D và hỗ trợ phanh tự động khẩn cấp (AEB).
- **Lỗi vật lý:** Ma trận ngoại thông số (Extrinsic Calibration) bị trôi dạt do rung lắc khi xe qua ổ gà/gờ giảm tốc hoặc biến dạng nhiệt khung xe, dẫn đến sai lệch góc quay delta_yaw trong khoảng [0.5, 5.0 độ] và tịnh tiến delta_x trong khoảng [2, 20 cm].

---

### 2. Method (Phương pháp & Nguồn tham khảo)
- **Nguồn tham khảo:** Paper *Dong et al. (CVPR 2023)* về benchmark nuScenes-C; công trình hiệu chuẩn trực tuyến *Galibr (2024)* và *CalibRefine (2025)*.
- **Thuật toán & Input/Output:**
  - *Input:* Point cloud LiDAR 3D, ảnh RGB 2D, ma trận nội thông số K, ma trận ngoại thông số (R, t).
  - *Output:* Tọa độ chiếu 2D [u, v] của điểm LiDAR lên ảnh camera.
- **Giới hạn nguồn:** Chưa tính tới rung động tức thời tần số cao và độ trễ truyền thông giữa các cảm biến.

---

### 3. Benchmark (Thực nghiệm & Số liệu thực tế)
- **Dữ liệu & Lệnh chạy:** Cặp frame đồng bộ nuScenes v1.0-mini (34.688 điểm LiDAR); lệnh: `python scripts/run_calibration_drift.py`.
- **Số liệu đo đạc trực tiếp tại lớp:**
  - *Baseline (0.0 độ):* Reprojection Error = **0.00 px**; mAP Proxy = **100.0%**.
  - *Lệch nhẹ (0.5 độ):* Reprojection Error = **4.19 px**; mAP Proxy = **95.34%** (nằm trong dung sai an toàn).
  - *Lệch vừa (1.0 độ):* Reprojection Error = **8.50 px**; mAP Proxy = **86.50%**.
  - *Lệch nặng (2.0 độ):* Reprojection Error = **16.91 px** (Max **36.07 px**); mAP Proxy tụt xuống **62.15%**.
  - *Mất chuẩn (3.5 - 5.0 độ):* Reprojection Error = **29.07 - 41.13 px** (Max **83.23 px**); mAP Proxy sụp đổ về **0.0%**.

---

### 4. Failure Case (Phân tích tình huống lỗi)
- **Mức lỗi phân tích:** Mức Drift L3 (delta_yaw = 2.0 độ, delta_x = 10 cm).
- **Phân biệt rõ ràng:**
  - *[Nhóm quan sát tự đo]:* Sai số chiếu lại trung bình 16.91 px, chùm điểm LiDAR của xe trước bị trượt văng sang làn đường bên cạnh trên ảnh Camera (minh chứng: `results_t3/calibration_drift_overlays.png`).
  - *[Paper Dong et al. 2023 cho biết]:* Mô hình Fusion bị sụt giảm từ 18% đến 42% mAP do các đặc trưng 2D bị ghép sai vào voxel 3D rỗng.
  - *[Suy luận kỹ thuật]:* Hệ thống AEB tính sai khoảng cách vật lý an toàn, gây phanh khẩn cấp sai lầm (phantom braking) hoặc nguy cơ đâm va.

---

### 5. Engineering Decision (Quyết định kỹ thuật)
- **Ngưỡng cảnh báo (10 px / 1.0 độ):** Bật cờ cảnh báo suy giảm `CALIB_DEGRADED`, lập lịch chạy thuật toán Targetless Calibration ngầm.
- **Ngưỡng ngắt khẩn cấp (20 px / 2.0 độ):** Lập tức ngắt module Camera-LiDAR Fusion! Chuyển xe về chế độ **LiDAR-only Mode** cho tác vụ phanh AEB và **Camera-only Mode** cho đọc biển báo, hoàn toàn loại trừ việc ghép đặc trưng sai lệch.
