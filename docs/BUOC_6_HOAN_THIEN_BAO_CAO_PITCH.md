# BƯỚC 6 · HOÀN THIỆN BÁO CÁO VÀ KỊCH BẢN PITCH (115 – 120 PHÚT)
## Chủ đề: T3. Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm 01)

---

### BẢNG TỰ KIỂM TRA TRƯỚC KHI PITCH (PRE-PITCH AUDIT CHECKLIST)

| Tiêu chuẩn tự kiểm tra | Hiện trạng trong Repository của Nhóm 01 | Đánh giá |
| :--- | :--- | :---: |
| **1. Có nền tảng, tính năng và sensor cụ thể** | • **Nền tảng:** Xe tự hành ADAS L2+/L3.<br>• **Tính năng:** Nhận diện 3D (3D Detection) & Phanh khẩn cấp tự động (AEB).<br>• **Sensor:** Camera Full HD 1080p ($f_x = 1350\text{ px}$) + Roof LiDAR 3D 32 tia. | ✅ **Đạt 100%** |
| **2. Có metric định lượng, baseline và điều kiện lỗi** | • **Metric:** MRE (pixels), Point Recall (%), BBox IoU.<br>• **Baseline:** $0.0^\circ, 0\text{ cm}$ ($MRE = 0\text{ px}$, $Recall = 100\%$, $IoU = 1.0$).<br>• **Điều kiện lỗi:** 4 mức can thiệp có chủ đích ($0.5^\circ, 1.0^\circ, 2.0^\circ, 2.5^\circ$). | ✅ **Đạt 100%** |
| **3. Có log/ảnh/plot và một failure case** | • **Bảng CSV:** `results/calibration_drift_metrics.csv`.<br>• **Đồ thị 4 góc:** `results/image1.png`.<br>• **Ảnh minh họa Point-Painting:** `results/image2.png`.<br>• **Failure Case:** Drift L3 ($2.0^\circ, 10\text{ cm}$) làm chùm laser văng ra ngoài xe tải. | ✅ **Đạt 100%** |
| **4. Có link nguồn, commit/version, dataset, lệnh chạy** | • **GitHub Repo:** `https://github.com/huybla166/K4-Track4-Day04-Team01-Sensor-Reality-Sprint`<br>• **Commit ID:** `main` (Latest sync: 436c6af, 7b1d128, 2549b63).<br>• **Dataset:** nuScenes v1.0-mini (`CAM_FRONT` × `LIDAR_TOP`).<br>• **Lệnh chạy:** `python scripts/run_calibration_drift.py`. | ✅ **Đạt 100%** |
| **5. Phân biệt kết luận nguồn với kết quả nhóm tự đo** | • **Nhóm tự đo:** MRE vọt lên $47.93\text{ px}$, Recall người đi bộ 25m rớt về $16.0\%$.<br>• **Paper CVPR 2023 cho biết:** Mạng 3D detection rớt tới $42\%$ mAP do gán nhầm đặc trưng vào voxel rỗng. | ✅ **Đạt 100%** |
| **6. Có cải tiến hoặc fallback gắn với failure case** | Thiết kế bộ điều khiển **Trigger State Machine 4 cấp độ (Level S0 $\to$ S3)**: Khi $MRE \ge 30\text{ px}$ hoặc $Recall < 50\%$ $\to$ Lập tức ngắt Early Fusion, chuyển sang **LiDAR-only Mode** cho phanh khẩn cấp AEB. | ✅ **Đạt 100%** |
| **7. Đầy đủ bản báo cáo riêng của từng thành viên** | Cả 4 thành viên đều có file nộp cá nhân hoàn chỉnh riêng biệt trong thư mục `submissions/` (Đã cập nhật đúng MSSV và phân công). | ✅ **Đạt 100%** |

---

### ĐỐI CHIẾU 4 TIÊU CHÍ CHẤM ĐIỂM TRONG PDF GIÁO TRÌNH

```text
┌────────────────────────────────────────────────────────┬───────────┬────────────────────────────────────────────┐
│ TIÊU CHÍ TRONG PDF                                     │ TỶ TRỌNG  │ HIỆN TRẠNG ĐÁP ỨNG CỦA NHÓM 01             │
├────────────────────────────────────────────────────────┼───────────┼────────────────────────────────────────────┤
│ 1. Benchmark / Demo chạy được                           │    40%    │ • Code Python chạy thật trong 3 giây.      │
│                                                        │           │ • Xuất CSV và 2 ảnh biểu đồ trực quan.     │
│                                                        │           │ • Web UI Simulator 60 FPS kéo trượt live.  │
├────────────────────────────────────────────────────────┼───────────┼────────────────────────────────────────────┤
│ 2. Hiểu failure thực tế                                │    25%    │ • Bóc tách bản chất trôi dạt cơ khí/nhiệt. │
│                                                        │           │ • Giải thích tại sao không thể hàn cứng.   │
│                                                        │           │ • Phân tích rủi ro phanh ma / đâm va AEB.  │
├────────────────────────────────────────────────────────┼───────────┼────────────────────────────────────────────┤
│ 3. Giải thích thuật toán                               │    20%    │ • Bóc tách 3 SOTA: CalibRefine, DF-Calib,  │
│                                                        │           │   Galibr (I/O, CFD, ViT, Chamfer edge).    │
│                                                        │           │ • Chỉ rõ limitation: Planar Degeneracy.    │
├────────────────────────────────────────────────────────┼───────────┼────────────────────────────────────────────┤
│ 4. Trình bày trade-off                                 │    15%    │ • Xử lý tình huống cấm đỗ / gờ giảm tốc.   │
│                                                        │           │ • Trade-off: Giữ Fusion vs Ngắt Fusion     │
│                                                        │           │   (Cắt để an toàn tính mạng ISO 26262).    │
└────────────────────────────────────────────────────────┴───────────┴────────────────────────────────────────────┘
```

---

### KỊCH BẢN THUYẾT TRÌNH PITCH 3 – 5 PHÚT (CHIA VAI 4 NGƯỜI)

1. **Phần 1: Problem & Geometry (0:00 – 1:00) — Phạm Quang Huy (2A202602900 - Lead):**
   - Đặt vấn đề: Tại sao Camera và LiDAR cùng sống nhưng ghép nối vẫn sai?
   - Tại sao hàn cứng không giải quyết được (giãn nở nhiệt, khung gầm uốn xoắn).
   - Mô hình SE(3) và sự đối lập: Góc xoay bất biến trên pixel nhưng bùng nổ mét ở cự ly xa ($50\text{m}$ lệch $0.87\text{m} >$ người đi bộ).
2. **Phần 2: Benchmark & Evidence (1:00 – 2:15) — Ngô Đức Chung (2A202602985):**
   - Giới thiệu bộ dữ liệu thật nuScenes v1.0-mini và kịch bản quét góc $0^\circ \to 2.5^\circ$.
   - Trình bày 4 biểu đồ hình 1: Baseline ($0.0\text{ px}$) $\to$ L1 ($11.99\text{ px}$) $\to$ L2 ($23.97\text{ px}$) $\to$ L3 ($47.93\text{ px}$).
   - Điểm gãy sụp đổ: Tại $2.0^\circ$, Recall người đi bộ 25m rớt về $16\%$.
3. **Phần 3: Failure Case & SOTA Literature (2:15 – 3:30) — Tạ Hoàng Vinh (2A202602543):**
   - Phân tích hình 2 Point-Painting: Chùm laser văng ra ngoài xe tải.
   - Tách biệt rạch ròi: Số đo tự đo vs Paper Dong et al. CVPR 2023 (rớt 42% mAP).
   - Bóc tách repo SOTA CalibRefine (4 giai đoạn CFD + ViT trên Orin) và hạn chế suy biến mặt phẳng (Planar Degeneracy) trong hầm trơn nhẵn.
4. **Phần 4: Safety State Machine & Live Demo (3:30 – 4:30) — Nguyễn Trần Kiên (2A202602571):**
   - Trình bày máy trạng thái 4 cấp độ (Level S0 $\to$ S1 $\to$ S2 $\to$ S3).
   - Giải quyết tình huống xe gặp gờ giảm tốc ở nơi cấm dừng đỗ: Giảm tốc 20 km/h, chuyển LiDAR-only AEB, tận dụng 0.5s dừng đèn đỏ tiếp theo để tự cân chỉnh.
   - Mở giao diện `DEMO_SIMULATOR.html`, kéo thanh trượt vài giây cho hội đồng xem trực tiếp!
