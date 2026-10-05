# BƯỚC 1 · CHUẨN BỊ (0 – 15 PHÚT)
## Đề tài: T3. Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm PhamQuangHuy)

---

### BẢNG KÊ KHAI BƯỚC 1 (ĐỐI CHIẾU TIÊU CHÍ SLIDE CHUẨN)

| Mục cần chốt | Nội dung chi tiết chuẩn mực của Nhóm PhamQuangHuy | Tự kiểm tra & Đánh giá |
| :--- | :--- | :---: |
| **1. Nền tảng, tính năng, sensor** | • **Nền tảng:** Xe tự hành ADAS L2+/L3 (Autonomous Driving Platform).<br>• **Tính năng chịu ảnh hưởng:** Nhận diện vật thể 3D đa cảm biến (3D Object Detection) và Phanh khẩn cấp tự động (AEB - Autonomous Emergency Braking).<br>• **Sensor kiểm tra:** Hệ đa cảm biến Camera góc rộng Full HD 1080p ($f_x = 1350\text{ px}$) gắn sau gương kính lái và Roof LiDAR 3D 32 chùm tia gắn trên nóc xe. | ✅ **Đạt:** Đã khoanh vùng hẹp nền tảng xe ADAS, 2 sensor cụ thể và tính năng an toàn sống còn. |
| **2. Failure case kiểm tra** | • **Tên lỗi:** Trôi dạt ma trận ngoại thông số giữa Camera và LiDAR (**Extrinsic Calibration Drift**).<br>• **Điều kiện xuất hiện thực tế:** Xuất hiện sau khi xe đi qua gờ giảm tốc mạnh, sập ổ gà trong khu đô thị, va quẹt nhẹ khi dừng đỗ, hoặc do biến dạng nhiệt (Thermal Expansion) chênh lệch nhiệt độ tới 60°C giữa trưa hè và đêm lạnh làm giá đỡ kim loại bị vênh $0.5^\circ - 2.5^\circ$. | ✅ **Đạt:** Chỉ rõ điều kiện thực tế (ổ gà, gờ giảm tốc, nhiệt) chứ không nói chung chung "bị hỏng". |
| **3. Claim ban đầu (Giả thuyết)** | *"Khi góc xoay quanh trục thẳng đứng ($\Delta\text{yaw}$) bị trôi lệch từ $0.5^\circ$ đến $2.5^\circ$, sai số chiếu lại ($MRE$) sẽ tăng tuyến tính trên ảnh pixel theo công thức $\Delta u \approx f_x \cdot \Delta\text{yaw}$ (1.0° ≈ 24px), dẫn tới sự sụt giảm phi tuyến nghiêm trọng của Point-to-Box Association Recall (giảm từ 100% xuống dưới 50% ở $2.0^\circ$), làm các vật thể cự ly xa ($Z \ge 25\text{m}$) bị mất liên kết hoàn toàn trước các vật thể gần."* | ✅ **Đạt:** Có hướng thay đổi rõ ràng (MRE tăng tuyến tính, Recall sụt phi tuyến), có đơn vị và giả thuyết cự ly Z. |
| **4. Metric và đơn vị đo** | • **Mean Reprojection Error (MRE) (đơn vị: pixels):** Đo khoảng cách Euclid 2D giữa điểm chiếu chuẩn và điểm chiếu bị lệch:<br>$$MRE = \frac{1}{M}\sum_{i=1}^M \sqrt{(u_i^{\text{pert}} - u_i^0)^2 + (v_i^{\text{pert}} - v_i^0)^2}$$<br>• **Point-to-Box Association Recall (đơn vị: %):** Tỷ lệ điểm LiDAR thuộc vật thể vẫn còn nằm trúng bên trong Bounding Box 2D:<br>$$\text{Recall} = \frac{N_{\text{in\_pert}}}{N_{\text{in\_base}}} \times 100\%$$<br>• **Bounding Box IoU Overlap (đơn vị: score $[0, 1]$):** Đo tỷ lệ diện tích tương giao giữa proposal 2D và cụm điểm laser. | ✅ **Đạt:** Định nghĩa công thức toán học chặt chẽ, đơn vị đo pixel/%/score rõ ràng, không dùng metric ảo. |
| **5. Baseline và Điều kiện lỗi** | • Cùng dữ liệu đầu vào: Cặp khung hình đồng bộ nuScenes v1.0-mini (`CAM_FRONT` × `LIDAR_TOP`, 34.688 điểm 3D).<br>• **Baseline (Cấu hình chuẩn):** Ngoại thông số chuẩn xác $100\%$ ($\Delta\text{yaw} = 0.0^\circ, \Delta x = 0\text{ cm}$). $MRE = 0.0\text{ px}, \text{Recall} = 100\%, IoU = 1.0$.<br>• **Degraded Conditions (Điều kiện lỗi):**<br>  - Mức 1 (Rung nhẹ): $\Delta\text{yaw} = 0.5^\circ, \Delta x = 2\text{ cm}$<br>  - Mức 2 (Lệch vừa - Warning): $\Delta\text{yaw} = 1.0^\circ, \Delta x = 5\text{ cm}$<br>  - Mức 3 (Lệch nặng - Critical): $\Delta\text{yaw} = 2.0^\circ, \Delta x = 10\text{ cm}$<br>  - Mức 4 (Cực nặng): $\Delta\text{yaw} = 2.5^\circ, \Delta x = 15\text{ cm}$. | ✅ **Đạt:** Cùng một tập dữ liệu và cùng một cách tính metric giữa baseline và 4 mức degraded. |
| **6. Phân công 4 thành viên** | • **Phạm Quang Huy (2A202602900 - Lead):** Xây dựng mô hình toán SE(3), ma trận Pinhole K, khảo sát độ nhạy góc xoay vs tịnh tiến, pitch Phần 1 (Problem & Geometry).<br>• **Ngô Đức Chung (2A202602985):** Tiền xử lý dữ liệu nuScenes, chạy benchmark quét góc 0°–2.5°, xuất CSV và 4 đồ thị sai số, pitch Phần 2 (Benchmark & Evidence).<br>• **Tạ Hoàng Vinh (2A202602543):** Bóc tách trực quan Point-Painting, phân tích điểm gãy 1.0° & 2.0°, nghiên cứu 3 repo SOTA (CalibRefine, DF-Calib, Galibr), pitch Phần 3 (Failure Case & SOTA).<br>• **Nguyễn Trần Kiên (2A202602571):** Thiết kế máy trạng thái Trigger State Machine 4 cấp (S0-S3), chiến lược fallback LiDAR-only AEB, xử lý ca cấm đỗ xe, pitch Phần 4 (Safety & Demo). | ✅ **Đạt:** Phân công chi tiết từng người vào đủ 5 mảng: Đọc nguồn, Chạy code, Ghi số liệu, Phân tích lỗi, Trình bày. |

---

### TỰ ĐỐI CHIẾU KIỂM TRA (SELF-CHECKLIST)
- [x] **Một người ngoài nhóm đọc vào có biết nhóm làm gì không?**  
  $\to$ *Có: Nhóm thay đổi góc xoay $\Delta\text{yaw}$ từ $0.5^\circ \to 2.5^\circ$ trên camera Full HD 1080p và đo độ lệch pixel $MRE$ cùng tỷ lệ rớt điểm $Recall$ trên vật thể ở các cự ly $10\text{m} - 50\text{m}$.*
- [x] **Bài toán có đủ hẹp để chạy và kiểm chứng trong 120 phút không?**  
  $\to$ *Có: Cố định 1 cặp frame chuẩn nuScenes, đo đạc hình học giải tích và mô phỏng suy thoái trực tiếp mà không cần train lại cả mạng deep learning nặng nề.*
- [x] **Đã sẵn sàng chuyển sang Bước 2 & Bước 3 chưa?**  
  $\to$ *Đã hoàn thành 100% và sẵn sàng cho các bước tiếp theo.*
