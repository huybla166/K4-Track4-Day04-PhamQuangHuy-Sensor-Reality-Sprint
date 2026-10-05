# K4-Track4-Day04-Team01-Sensor-Reality-Sprint
> **Chủ đề 3 (T3): Calibration Drift Impact on Multi-Sensor Fusion (Camera - LiDAR) in ADAS**  
> *Đo lường tác động của lỗi trôi dạt hiệu chuẩn ngoại thông số tới sai số chiếu lại, tỷ lệ liên kết đặc trưng và mức sụt giảm mAP.*

---

## 👥 Danh sách thành viên nhóm (Team Members)
Xem chi tiết danh sách họ tên, MSSV và phân công tại [`TEAMMATES.md`](TEAMMATES.md).

| Thành viên | MSSV | Vai trò | Báo cáo cá nhân |
|:---|:---:|:---|:---|
| **Phạm Quang Huy** (Lead) | `2A202602900` | Metric & Geometry Lead | [`SUBMISSION_PhamQuangHuy_2A202602900.md`](submissions/SUBMISSION_PhamQuangHuy_2A202602900.md) |
| **Trần Trung Kiên** | `2A202602901` | Data & Perturbation Lead | [`SUBMISSION_TranTrungKien_2A202602901.md`](submissions/SUBMISSION_TranTrungKien_2A202602901.md) |
| **Nguyễn Thành Danh** | `2A202602902` | Benchmark Runner & Eval | [`SUBMISSION_NguyenThanhDanh_2A202602902.md`](submissions/SUBMISSION_NguyenThanhDanh_2A202602902.md) |
| **Lê Quốc Việt** | `2A202602903` | Literature & Method Analyst | [`SUBMISSION_LeQuocViet_2A202602903.md`](submissions/SUBMISSION_LeQuocViet_2A202602903.md) |
| **Hoàng Anh Tuấn** | `2A202602904` | Safety & Fallback Lead | [`SUBMISSION_HoangAnhTuan_2A202602904.md`](submissions/SUBMISSION_HoangAnhTuan_2A202602904.md) |

---

## 🎯 Báo cáo tổng quan 5 mục (Executive Summary)

### 1. Problem
* **Nền tảng & Sensor:** Xe tự lái ADAS trang bị Camera góc rộng phía trước (`CAM_FRONT`) và LiDAR 32-beam (`LIDAR_TOP`).
* **Failure Case:** Rung chấn cơ học khi xe qua gờ giảm tốc/ổ gà hoặc biến dạng nhiệt khung đỡ làm trôi ma trận ngoại thông số $(R, t)$ (Extrinsic Calibration Drift): lệch góc quay $\Delta \text{yaw} \in [0.5^\circ, 5.0^\circ]$, dịch chuyển $\Delta x \in [2, 20\text{ cm}]$.

### 2. Method
* **Paper tham khảo:** *Dong et al. (CVPR 2023 - nuScenes-C benchmark)*, *Galibr: Targetless LiDAR-Camera Calibration (2024)*.
* **Input $\to$ Output:** Điểm LiDAR $P_{\text{lidar}} \in \mathbb{R}^{34688 \times 3}$, ảnh Camera $I_{1600 \times 900}$, ma trận $(R, t), K \to$ Tọa độ chiếu 2D $[u, v]$ và gán đặc trưng đa cảm biến.

### 3. Benchmark (Kết quả đo đạc thực tế)
Chạy trực tiếp bằng lệnh: `python scripts/run_calibration_drift.py`

| Điều kiện kiểm thử | Góc xoay ($\Delta \text{yaw}$) | Tịnh tiến ($\Delta x$) | Mean Reproj Error (px) | Max Reproj Error (px) | Vehicle Retention (%) | Fusion mAP Proxy (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseline** | **$0.0^\circ$** | **0 cm** | **0.00 px** | **0.00 px** | **100.0%** | **100.0%** |
| **Drift L1 (Rung nhẹ)** | $0.5^\circ$ | 2 cm | **4.19 px** | 8.72 px | 100.0% | **95.34%** |
| **Drift L2 (Lệch vừa)** | $1.0^\circ$ | 5 cm | **8.50 px** | 17.92 px | 99.29% | **86.50%** |
| **Drift L3 (Lệch nặng)** | $2.0^\circ$ | 10 cm | **16.91 px** | 36.07 px | 98.35% | **62.15%** |
| **Drift L4 (Cực nặng)** | $3.5^\circ$ | 15 cm | **29.07 px** | 58.58 px | 94.80% | **14.67%** |
| **Drift L5 (Failure)** | $5.0^\circ$ | 20 cm | **41.13 px** | **83.23 px** | 92.43% | **0.00%** |

### 4. Failure Case
* **[Nhóm tự đo tại lớp]:** Ở mức lệch $2.0^\circ$, sai số chiếu lại hình học trung bình là **$16.91\text{ px}$** (Max **$36.07\text{ px}$**). Chùm điểm LiDAR của xe tải phía trước bị dịch chuyển hẳn sang làn đường đối diện trên ảnh camera.
* **[Paper Dong et al. 2023]:** Mạng Fusion bị giảm tới $42\%$ mAP do gán nhầm đặc trưng 2D vào voxel 3D rỗng.
* **[Suy luận kỹ thuật]:** Hệ thống AEB tính sai Time-to-Collision (TTC), gây nguy cơ phanh gấp đột ngột (phantom braking) hoặc đâm va nguy hiểm.

### 5. Engineering Decision
* **Ngưỡng Cảnh báo ($10\text{ px} / 1.0^\circ$):** Bật cờ `CALIB_DEGRADED`, lập lịch chạy thuật toán Targetless Calibration ngầm.
* **Ngưỡng Ngắt an toàn ($20\text{ px} / 2.0^\circ$):** Lập tức **ngắt module Sensor Fusion**, hạ cấp về **LiDAR-only** cho phanh AEB và **Camera-only** cho đọc biển báo, tuyệt đối không ghép đặc trưng chéo.

---

## 📁 Cấu trúc thư mục (Repository Structure)
```
K4-Track4-Day04-Team01-Sensor-Reality-Sprint/
├── TEAMMATES.md                                          # Danh sách 5 thành viên nhóm
├── README.md                                             # Báo cáo tổng hợp
├── scripts/
│   └── run_calibration_drift.py                          # Mã nguồn chạy thực nghiệm
├── results/
│   ├── calibration_drift_metrics.csv                     # Bảng số liệu đo đạc CSV
│   ├── calibration_drift_curves.png                      # Biểu đồ xu hướng suy giảm
│   └── calibration_drift_overlays.png                    # Lưới ảnh trực quan 6 mức độ trôi dạt
├── docs/
│   ├── BAO_CAO_NHOM.md                                   # Báo cáo chi tiết cả nhóm
│   └── PITCH_SLIDES.md                                   # Kịch bản thuyết trình 3-5 phút
└── submissions/
    ├── SUBMISSION_PhamQuangHuy_2A202602900.md            # Bản nộp riêng TV1
    ├── SUBMISSION_TranTrungKien_2A202602901.md           # Bản nộp riêng TV2
    ├── SUBMISSION_NguyenThanhDanh_2A202602902.md          # Bản nộp riêng TV3
    ├── SUBMISSION_LeQuocViet_2A202602903.md              # Bản nộp riêng TV4
    └── SUBMISSION_HoangAnhTuan_2A202602904.md            # Bản nộp riêng TV5
```
