# BƯỚC 3 · THIẾT KẾ BENCHMARK CÓ ĐỐI CHỨNG (45 – 95 PHÚT)
## Đề tài: T3. Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm 01)

---

### 1. NGUYÊN TẮC CỐ ĐỊNH ĐIỀU KIỆN SO SÁNH
Để cô lập chính xác ảnh hưởng của sự cố trôi dạt ngoại thông số (Calibration Drift), Nhóm 01 tuân thủ nghiêm ngặt nguyên tắc **chỉ thay đổi duy nhất một yếu tố** (Single Variable Perturbation):
- **Cố định dữ liệu đầu vào:** Cặp khung hình đồng bộ nuScenes v1.0-mini (`CAM_FRONT` 1080p, $f_x = 1350\text{ px}$ và `LIDAR_TOP` 34.688 điểm 3D).
- **Cố định ma trận nội thông số Camera K:** $f_x = 1350.0, f_y = 1350.0, c_x = 960.0, c_y = 540.0$.
- **Cố định công thức và cách tính metric:** Giữ nguyên 100% thuật toán đo trên toàn bộ các mức thử nghiệm.
- **Yếu tố duy nhất thay đổi:** Ma trận ngoại thông số $T_{CL} \in SE(3)$ với góc xoay quanh trục thẳng đứng $\Delta\text{yaw} \in [0.0^\circ, 2.5^\circ]$ và tịnh tiến ngang $\Delta x \in [0, 15\text{ cm}]$.

---

### 2. ĐỊNH NGHĨA METRIC TRƯỚC KHI CHẠY (RÕ CHIỀU TỐT / XẤU)

| Tên Metric | Ký hiệu & Đơn vị | Công thức toán học | Chiều Tốt / Xấu | Ý nghĩa kỹ thuật |
| :--- | :---: | :--- | :---: | :--- |
| **Mean Reprojection Error** | $MRE$ (pixels) | $$MRE = \frac{1}{M}\sum_{i=1}^M \sqrt{(u_i^{\text{pert}} - u_i^0)^2 + (v_i^{\text{pert}} - v_i^0)^2}$$ | Càng **NHỎ** càng tốt ($0\text{ px}$ là tối ưu) | Đo độ lệch tâm hình học trực tiếp giữa chùm tia laser và thấu kính camera. |
| **Point-to-Box Recall** | $Recall$ (%) | $$\text{Recall} = \frac{N_{\text{in\_pert}}}{N_{\text{in\_base}}} \times 100\%$$ | Càng **LỚN** càng tốt ($100\%$ là tối ưu) | Đo chất lượng gán nhãn đặc trưng (Association); khi rơi xuống dưới 50% là thuật toán Fusion hỏng. |
| **Bounding Box IoU** | $IoU$ (score $[0, 1]$) | $$IoU = \frac{\text{Area}(\text{Box}_{\text{pert}} \cap \text{Box}_{\text{base}})}{\text{Area}(\text{Box}_{\text{pert}} \cup \text{Box}_{\text{base}})}$$ | Càng **LỚN** càng tốt ($1.0$ là khớp hoàn toàn) | Đo mức độ trùng khớp của vùng proposal dự đoán 3D khi chiếu sang 2D. |
| **Distant Object Recall (25m)** | $Rec_{25m}$ (%) | Tỷ lệ điểm laser của người đi bộ ở khoảng cách 25m còn rơi trúng Bbox | Càng **LỚN** càng tốt | Thước đo độ nhạy cự ly xa; phản ánh nguy cơ đâm va trực diện người đi bộ. |

---

### 3. THIẾT KẾ MA TRẬN ĐỐI CHỨNG CÁC ĐIỀU KIỆN THỬ NGHIỆM

| Điều kiện kiểm thử | Tham số can thiệp cụ thể | Metric MRE (px) | Metric Recall (%) | Bằng chứng lưu trữ | Điều metric cho phép kết luận |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **1. Baseline (Chuẩn)** | $\Delta\text{yaw} = 0.0^\circ, \Delta x = 0\text{ cm}$<br>*(Xuất xưởng chuẩn xác 100%)* | **0.00 px** | **100.0%**<br>($IoU = 1.0$) | • CSV: Dòng 1<br>• Hình 2: Case 1 | **Mốc đối chứng chuẩn:** Mọi điểm laser bám khít thân xe tải và người đi bộ. |
| **2. Lỗi A (Rung nhẹ - S1)** | $\Delta\text{yaw} = 0.5^\circ, \Delta x = 2\text{ cm}$<br>*(Xe qua gờ giảm tốc nhẹ)* | **11.99 px** | **85.7%**<br>($IoU = 0.667$) | • CSV: Dòng 2<br>• Đồ thị Hình 1 | Sai số tăng nhỏ, hệ thống vẫn duy trì nhận diện nhưng bắt đầu có cảnh báo. |
| **3. Lỗi B (Lệch vừa - S2)** | $\Delta\text{yaw} = 1.0^\circ, \Delta x = 5\text{ cm}$<br>*(Sập ổ gà / Giãn nở nhiệt)* | **23.97 px** | **68.9%**<br>($IoU = 0.461$) | • CSV: Dòng 3<br>• Hình 2: Case 2 | **Ngưỡng kích hoạt Re-calibration:** Bbox IoU tụt dưới 0.5, cần chạy CalibRefine. |
| **4. Lỗi C (Lệch nặng - S3)** | $\Delta\text{yaw} = 2.0^\circ, \Delta x = 10\text{ cm}$<br>*(Va quẹt nhẹ gương / gá)* | **47.93 px** | **41.3%**<br>*(Người 25m: 16%)* | • CSV: Dòng 4<br>• Hình 2: Case 3 | **Ngưỡng cắt khẩn cấp (Fail-safe):** Chùm laser văng ra ngoài xe, bắt buộc ngắt Early Fusion! |
| **5. Lỗi D (Cực nặng - S4)** | $\Delta\text{yaw} = 2.5^\circ, \Delta x = 15\text{ cm}$<br>*(Biến dạng gá cơ khí nặng)* | **59.88 px** | **31.2%**<br>*(Người 25m: 0%)* | • CSV: Dòng 5<br>• Đồ thị Hình 1 | Mất dấu hoàn toàn người đi bộ ở cự ly xa; nguy cơ đâm va cực kỳ nghiêm trọng. |

---

### 4. BẰNG CHỨNG TÁI HIỆN ĐƯỢC LƯU TRỮ
1. **Mã nguồn thực thi:** `scripts/run_calibration_drift.py` (Chạy độc lập trong 3 giây trên mọi máy tính).
2. **File số liệu chi tiết:** `results/calibration_drift_metrics.csv` (Lưu giá trị định lượng từng frame).
3. **Ảnh biểu đồ đối chứng 4 góc nhìn:** `results/image1.png` (MRE, Point Recall, Quy luật 1/Z, Bounding Box IoU).
4. **Ảnh trực quan hóa Point-Painting:** `results/image2.png` (So sánh trước/sau khi bị trôi ngoại thông số).
5. **Trình mô phỏng tương tác:** `DEMO_SIMULATOR.html` (Kéo trượt góc lệch quan sát phản ứng tức thì).

---

### TỰ KIỂM TRA BƯỚC 3 (SELF-CHECKLIST)
- [x] **Người đo metric có biết cần điền số vào cột nào không?**  
  $\to$ *Có: 3 cột chính gồm `MRE (px)`, `Point Recall (%)` và `IoU Overlap`.*
- [x] **Có quy định rõ "tốt hơn / xấu hơn" trước khi xem kết quả không?**  
  $\to$ *Có: MRE càng tăng là càng xấu, Recall và IoU càng tụt là càng xấu.*
- [x] **Baseline có đứng cạnh ít nhất một mức lỗi để thấy rõ xu hướng không?**  
  $\to$ *Có: Baseline đứng cạnh 4 mức lỗi liên tục từ 0.5° đến 2.5° để chỉ ra rõ ràng xu hướng sụp đổ phi tuyến của liên kết cảm biến.*
