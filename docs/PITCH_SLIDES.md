# KỊCH BẢN THUYẾT TRÌNH PITCH 3–5 PHÚT (PHÂN VAI 4 THÀNH VIÊN)
## Chủ đề T3: Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm 01)

* **Thời gian tổng:** 4 phút 30 giây (khoảng 60–70 giây / người)
* **Visuals trình chiếu:** Mở sẵn file presentation `SLIDES.html` và app tương tác `DEMO_SIMULATOR.html`.

---

### PHẦN 1 · PROBLEM & GEOMETRY (0:00 – 1:00)
**Người trình bày: Phạm Quang Huy (MSSV: 2A202602900 — Metric & Geometry Architect / Trưởng nhóm)**
> *"Kính thưa Thầy Cô và các bạn, trên xe tự hành ADAS L2+/L3, để phanh khẩn cấp tự động (AEB) an toàn, xe phải kết hợp giữa Camera Full HD 1080p và Roof LiDAR 3D. Cầu nối duy nhất là ma trận ngoại thông số $T_{CL} \in SE(3)$.
> Tuy nhiên, trong thực tế khi xe qua gờ giảm tốc, sập ổ gà, hoặc nhiệt độ mặt kính chênh lệch tới 60°C, giá đỡ bị lệch vi mô từ 0.5° đến 2.0°. Nhiều người hỏi tại sao không hàn cứng? Câu trả lời là khung xe luôn đàn hồi uốn xoắn tự nhiên khi chạy và thấu kính bên trong camera tự co giãn vi dịch chuyển.
> Về mặt hình học, nhóm phát hiện: Sai số góc xoay $\Delta u_{\text{rot}} \approx f_x \cdot \Delta\theta$ là bất biến trên ảnh pixel (1.0° ≈ 24px), nhưng trong không gian 3D thực tế, sai số mét bùng nổ theo cự ly xa: Tại 50m lệch 1.0° làm điểm laser văng xa 0.87m — lớn hơn toàn bộ bề rộng của một người đi bộ!"*

---

### PHẦN 2 · BENCHMARK & EVIDENCE (1:00 – 2:15)
**Người trình bày: Ngô Đức Chung (MSSV: 2A202602985 — Data & Benchmark Evaluation Lead)**
> *"Để chứng minh bằng số liệu thực tế, em đã thiết lập kịch bản quét góc từ 0° đến 2.5° và tịnh tiến 0 đến 15cm trên cặp frame đồng bộ của nuScenes v1.0-mini:
> Xin mời Thầy Cô nhìn vào 4 đồ thị thực nghiệm trên màn hình (Slide 4):
> - Ở mức **Baseline (0.0°)**: Sai số chiếu lại MRE = 0.0 px, 100% điểm laser bám khít vào thân xe.
> - Khi lệch nhẹ **0.5°**: MRE đạt **11.99 px**, Recall đạt **85.7%**, hệ thống nằm trong ngưỡng cảnh báo S1.
> - Điểm gãy sụp đổ đầu tiên tại **1.0°**: MRE tăng vọt lên **23.97 px**, IoU tụt xuống **0.461**, Recall giảm còn **68.9%** — đây là ngưỡng tối ưu để kích hoạt Re-calibration.
> - Và tại **2.0°**: MRE lên tới **47.93 px** (cực đại hơn 80px), Recall người đi bộ ở 25m sụt thảm hại xuống chỉ còn **16%**, khiến xe hoàn toàn mất dấu người đi bộ!"*

---

### PHẦN 3 · FAILURE CASE & SOTA LITERATURE (2:15 – 3:30)
**Người trình bày: Tạ Hoàng Vinh (MSSV: 2A202602543 — Failure Case & SOTA Literature Analyst)**
> *"Tiếp theo, em xin phân tích trực quan hóa Point-Painting ở Hình 2 (Slide 4):
> Tại Case 3 (lệch 1.8° - 2.0°), toàn bộ chùm điểm laser màu đỏ bị trượt văng hoàn toàn ra khỏi Bounding Box xe và người đi bộ. Paper Dong et al. tại CVPR 2023 chỉ ra rằng lỗi lệch tâm này khiến mạng 3D Detection rớt tới 42% mAP do gán nhầm đặc trưng ngữ nghĩa vào voxel rỗng.
> Để giải quyết, nhóm nghiên cứu 3 công trình SOTA hàng đầu: **CalibRefine** (IEEE TIM 2026), **DF-Calib** (arXiv 2025) và **Galibr** (IEEE IV 2024). CalibRefine dùng mạng 4 giai đoạn CFD và ViT Cross-Attention chạy TensorRT FP16 trên chip Jetson Orin để tự cân chỉnh liên tục.
> Tuy nhiên, giới hạn kỹ thuật của các thuật toán này là sẽ thất bại khi xe đi vào đường hầm trơn nhẵn (textureless tunnel) do hiện tượng suy biến mặt phẳng (Planar Degeneracy), ma trận covariance phân kỳ. Đó là lý do hệ thống bắt buộc phải có tầng bảo vệ an toàn State Machine!"*

---

### PHẦN 4 · SAFETY STATE MACHINE & FALLBACK (3:30 – 4:30)
**Người trình bày: Nguyễn Trần Kiên (MSSV: 2A202602571 — Safety State Machine & Fallback Lead)**
> *"Để đảm bảo tiêu chuẩn an toàn quốc tế ISO 26262 ASIL-D và SOTIF ISO 21448, nhóm em thiết kế bộ điều khiển Trigger State Machine 4 cấp độ (Slide 6):
> - **Level S0 (Nominal, MRE < 10px):** Xe lái tự động bình thường.
> - **Level S1 (Warning, 10–20px):** Tăng covariance camera, giảm trọng số camera trong bộ lọc EKF.
> - **Level S2 (Re-calib, 20–30px):** Khoá tính năng tự chuyển làn cao tốc (NOA), kích hoạt CalibRefine chạy ngầm trên Orin để tìm extrinsic mới.
> - **Level S3 (Critical, MRE ≥ 30px hoặc Recall < 50%):** Lập tức **NGẮT HOÀN TOÀN Early Fusion!** Chuyển xe về chế độ **LiDAR-only** cho hệ thống phanh AEB (vì bản thân LiDAR đo khoảng cách vật lý độc lập vẫn đúng 100%) và phát Takeover Request cho tài xế.
> Đặc biệt, nếu gặp gờ giảm tốc ở nơi có biển cấm dừng đỗ trong khu đô thị, xe không phanh chết gây tắc đường mà giảm tốc xuống 20 km/h để LiDAR tự phanh độc lập, đồng thời tận dụng 0.5 giây dừng đèn đỏ tiếp theo hoặc dùng nhà cửa ven đường để tự bù góc!
> Sau đây, nhóm xin kính mời Thầy Cô quan sát trực tiếp Trình mô phỏng Simulator tương tác thời gian thực. Xin trân trọng cảm ơn!"*
