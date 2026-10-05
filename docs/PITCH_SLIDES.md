# KỊCH BẢN THUYẾT TRÌNH PITCH 3-5 PHÚT (PHÂN VAI 5 THÀNH VIÊN)
## Chủ đề 3: Calibration Drift Impact on Multi-Sensor Fusion

* **Thời gian tổng:** 3 - 5 phút (khoảng 45-60 giây / người)
* **Slide / Visual minh chứng:** Mở sẵn `calibration_drift_curves.png` và `calibration_drift_overlays.png`.

---

### PHẦN 1 · PROBLEM (0:00 - 0:45) — Trình bày: Phạm Quang Huy (Team Lead)
> "Kính thưa Thầy và các bạn, trên xe tự lái ADAS, để phanh an toàn trước chướng ngại vật, xe phải kết hợp mắt thần Camera 2D và máy quét LiDAR 3D. Cầu nối duy nhất giữa hai cảm biến này là Ma trận Ngoại thông số Extrinsic $(R, t)$.
> Tuy nhiên, trong thực tế, chỉ cần xe đi qua ổ gà, gờ giảm tốc mạnh hoặc khung xe giãn nở nhiệt, góc đặt cảm biến sẽ bị lệch nhẹ từ 0.5 đến 2 độ – hiện tượng này gọi là **Calibration Drift**.
> Câu hỏi nhóm đặt ra là: **Khi ma trận này bị lệch, sai số hình học tích lũy ra sao, và khi nào thì hệ thống Fusion buộc phải ngắt để không phanh nhầm vào bóng ma trên đường?**"

---

### PHẦN 2 · METHOD & BENCHMARK SETUP (0:45 - 1:30) — Trình bày: Lê Quốc Việt (Literature Analyst)
> "Để trả lời câu hỏi này, nhóm tham khảo nghiên cứu của **Dong và cộng sự tại CVPR 2023** về benchmark độ bền 3D trên nuScenes-C, cùng các công trình hiệu chuẩn trực tuyến như **Galibr 2024**.
> Nhóm thiết lập một benchmark thực nghiệm có đối chứng trực tiếp trên tập dữ liệu chuẩn `nuScenes v1.0-mini`. Chúng em cố định toàn bộ dữ liệu mẫu gồm 34.688 điểm LiDAR và ảnh Camera trước độ phân giải cao, sau đó can thiệp có chủ đích góc xoay Yaw từ 0.0 độ (Baseline) tăng dần lên 0.5, 1.0, 2.0, 3.5 và 5.0 độ, kèm dịch chuyển tịnh tiến 2 đến 20 cm để đo đạc sai số định lượng."

---

### PHẦN 3 · BENCHMARK RESULTS (1:30 - 2:30) — Trình bày: Nguyễn Thành Danh (Benchmark Runner)
> "Xin mời Thầy và các bạn nhìn vào bảng số liệu và biểu đồ nhóm đã đo đạc thực tế:
> - Ở mức **Baseline**, sai số chiếu lại bằng 0 pixel, 100% điểm LiDAR bám khít vào thân xe phía trước.
> - Khi xe rung nhẹ **0.5 độ**, sai số trung bình là **4.19 pixel**, hệ thống vẫn an toàn trong dung sai.
> - Nhưng khi góc lệch đạt **2.0 độ**, sai số chiếu lại tăng vọt lên **16.91 pixel** (và cực đại ở biên ảnh lên tới **36.07 pixel**). Lúc này, chỉ số mAP ước lượng của mô hình Fusion tụt mạnh từ 100% xuống còn **62.15%**.
> - Và khi lệch **3.5 độ đến 5.0 độ**, sai số chiếu lại vượt **29 đến 41 pixel** (cực đại hơn 83 pixel), dẫn đến việc mô hình Fusion sụp đổ hoàn toàn!"

---

### PHẦN 4 · FAILURE CASE ANALYSIS (2:30 - 3:30) — Trình bày: Hoàng Anh Tuấn (Safety & Failure Lead)
> "Đây là hình ảnh minh chứng thực tế trên màn hình (Slide 6 khung hình overlay):
> - **Nhóm quan sát trực tiếp được rằng:** Tại mức lệch 2.0 độ (Drift L3), toàn bộ chùm tia LiDAR chiếu lên chiếc xe tải phía trước đã bị trượt văng sang làn đường bên cạnh.
> - **Paper Dong et al. (CVPR 2023) cũng chỉ ra:** Hiện tượng misaligned projection này làm rớt tới 42% mAP vì thuật toán gán nhầm đặc trưng của xe vào khoảng trống.
> - **[Suy luận kỹ thuật của nhóm]:** Nếu xe tiếp tục dùng dữ liệu Fusion bị lệch 17 pixel này, bộ điều khiển phanh khẩn cấp AEB sẽ tính sai hoàn toàn khoảng cách tới xe trước, gây nguy cơ phanh gấp đột ngột (phantom braking) hoặc đâm va nghiêm trọng ở tốc độ cao."

---

### PHẦN 5 · ENGINEERING DECISION (3:30 - 4:30) — Trình bày: Trần Trung Kiên (System Lead)
> "Từ bằng chứng số đo trên, nhóm đưa ra quyết định kỹ thuật với kiến trúc phòng vệ 2 ngưỡng:
> 1. **Ngưỡng Cảnh báo (10 pixel / lệch 1.0 độ):** Bật cảnh báo suy giảm chuẩn `CALIB_DEGRADED` và kích hoạt thuật toán Targetless Calibration chạy ngầm khi xe dừng chờ đèn đỏ.
> 2. **Ngưỡng Ngắt an toàn (20 pixel / lệch 2.0 độ):** Lập tức ngắt hoàn toàn module Camera-LiDAR Fusion! Chuyển xe về chế độ **LiDAR-only** cho hệ thống phanh AEB và **Camera-only** cho đọc biển báo, tuyệt đối không ghép đặc trưng để triệt tiêu nguy cơ nhận diện vật thể ma.
> Đó là cách nhóm bảo vệ an toàn cho hệ thống xe tự lái khi cảm biến gặp sự cố thực tế. Xin cảm ơn Thầy và các bạn đã lắng nghe!"
