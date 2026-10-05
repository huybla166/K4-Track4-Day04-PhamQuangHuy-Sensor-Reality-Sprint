# BÁO CÁO KẾT QUẢ THỰC HÀNH CÁ NHÂN — SENSOR REALITY SPRINT (DAY 04)
## Môn học: AI20K - Track 4: ADAS Sensing & Estimation (VinUni)

* **Họ và tên:** Phạm Quang Huy
* **Mã sinh viên (MSSV):** `2A202602900`
* **Nhóm thực hiện:** Nhóm PhamQuangHuy (4 thành viên)
* **Vai trò trong nhóm:** **Metric & Geometry Architect (Trưởng nhóm)** — Chịu trách nhiệm xây dựng mô hình toán học biến đổi không gian SE(3), ma trận chiếu Pinhole K, khảo sát độ nhạy góc xoay vs tịnh tiến.
* **Repository GitHub nhóm:** `https://github.com/huybla166/K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint`
* **Lệnh chạy tái hiện:** `python scripts/run_calibration_drift.py`

---

### 1. Problem (Vấn đề & Bối cảnh kỹ thuật)
- **Nền tảng & Cảm biến:** Xe tự hành ADAS trang bị Camera Full HD 1080p (fx = 1350px) trên kính lái và Roof LiDAR 3D trên nóc xe.
- **Sự cố thực tế:** Sau xóc nảy gờ giảm tốc, ổ gà, giãn nở nhiệt mặt kính (chênh lệch 60°C) hoặc va quẹt nhẹ, ma trận ngoại thông số (Extrinsic Calibration) bị trôi lệch vi mô: góc xoay $\Delta\text{yaw} \in [0.5^\circ, 2.5^\circ]$, tịnh tiến $\Delta x \in [2, 15\text{ cm}]$, dù cả Camera và LiDAR vẫn truyền dữ liệu bình thường.
- **Hệ quả đối với Fusion:** Sai số chiếu lại $MRE > 25\text{ px}$ làm Bbox 2D gán nhầm đặc trưng của mặt đường xa (50m) vào vật thể gần (10m), gây phanh khẩn cấp ảo (Phantom Braking) hoặc bỏ sót người đi bộ. Hàn cơ khí cứng không thể giải quyết do khung xe đàn hồi uốn xoắn tự nhiên khi chạy.

---

### 2. Method (Phương pháp & Cơ sở toán học)
- **Paper/Repo SOTA chuẩn môn học:** CalibRefine (*IEEE TIM 2026 / XCalib repo*), DF-Calib (*arXiv:2504.01416*), Galibr (*IEEE IV 2024*); Benchmark nền tảng: Dong et al. (*CVPR 2023*).
- **Mô hình toán học SE(3) & Độ nhạy chiếu:**
  - $P_C = R_{CL} \cdot P_L + t_{CL}$; Chiếu phối cảnh: $u = f_x (X_C / Z_C) + c_x$, $v = f_y (Y_C / Z_C) + c_y$.
  - **Quy luật bất biến góc xoay (Rotation):** $\Delta u_{\text{rot}} \approx f_x \cdot \Delta\theta$. Sai số pixel bất biến theo khoảng cách $Z$ ($1.0^\circ \approx 23.6\text{ px}$), nhưng sai số mét thực tế $\Delta X_{3D} = Z \cdot \sin(\Delta\theta)$ bùng nổ ở cự ly xa (lệch $0.87\text{m}$ ở $50\text{m}$ $\to$ văng khỏi thân người đi bộ $0.6\text{m}$).
  - **Quy luật nghịch đảo (Translation):** $\Delta u_{\text{trans}} \approx f_x (\Delta t / Z_C)$ nhạy cảm nhất ở cự ly gần ($10\text{cm}$ lệch $13.5\text{px}$ ở $10\text{m}$, nhưng chỉ $2.7\text{px}$ ở $50\text{m}$).

---

### 3. Benchmark (Thực nghiệm & Số liệu định lượng)
- **Cấu hình kiểm thử:** Full HD 1080p ($f_x = 1350\text{ px}$), quét góc $0^\circ \to 2.5^\circ$ và tịnh tiến $0 \to 15\text{ cm}$. Dữ liệu đồng bộ nuScenes v1.0-mini (`CAM_FRONT` × `LIDAR_TOP`).
- **Kết quả đo đạc thực tế:**
  - *Baseline ($0.0^\circ, 0\text{cm}$):* MRE = **0.00 px**; Recall = **100.0%**; IoU = **1.000** (Hoạt động hoàn hảo).
  - *Mức 1 ($0.5^\circ, 2\text{cm}$):* MRE = **11.99 px**; Recall = **85.7%**; IoU = **0.667** (Mức cảnh báo S1).
  - *Mức 2 ($1.0^\circ, 5\text{cm}$):* MRE = **23.97 px**; Recall = **68.9%**; IoU = **0.461** $\to$ **Điểm kích hoạt Online Re-calibration (Mức S2)**.
  - *Mức 3 ($2.0^\circ, 10\text{cm}$):* MRE = **47.93 px**; Recall = **41.3%**; Recall người đi bộ 25m rớt về **16%** $\to$ **Critical Ngắt Early Fusion (Mức S3)**.

---

### 4. Failure Case (Phân tích lỗi & Suy biến toán học)
- **Tình huống thuật toán fail:** Khi xe đi vào đường hầm đơn sắc (textureless tunnel) hoặc bãi đỗ xe phẳng hoàn toàn không có cây cối, xe đỗ.
- **Bản chất toán học:** Hiện tượng suy biến mặt phẳng vô hạn (**Planar Degeneracy**), ma trận Hessian rơi vào điểm kỳ dị khiến hàm mất mát Chamfer distance không thể tìm gradient giảm dốc để hội tụ.
- **Phân tách rạch ròi bằng chứng:**
  - *[Nhóm tự quan sát]:* Tại $\Delta\theta = 2.0^\circ$, sai số pixel trung bình vọt lên $47.93\text{ px}$, các điểm laser của xe trước bị hất văng sang làn cạnh.
  - *[Paper Dong et al. CVPR 2023]:* Mạng 3D detection rớt tới $42\%$ mAP do gán nhầm semantic class vào voxel rỗng.

---

### 5. Engineering Decision (Quyết định kỹ thuật & Fallback)
- **Máy trạng thái 4 cấp độ (Trigger State Machine):**
  - $MRE < 10\text{ px}$ (S0 Nominal): Duy trì Sensor Fusion bình thường.
  - $10 \le MRE < 20\text{ px}$ (S1 Warning): Tăng covariance của Camera, giảm trọng số camera trong bộ lọc EKF.
  - $20 \le MRE < 30\text{ px}$ (S2 Re-calib): Khoá tính năng tự chuyển làn (NOA), kích hoạt CalibRefine chạy ngầm.
  - $MRE \ge 30\text{ px}$ (S3 Critical): **Lập tức ngắt Early Fusion**, chuyển sang chế độ **LiDAR-only** cho hệ thống phanh AEB và phát Takeover Request.
- **Tuân thủ tiêu chuẩn an toàn:** Đảm bảo ISO 26262 ASIL-D và SOTIF ISO 21448 chống phanh ma.
