# BƯỚC 2 · TÌM PAPER/REPOSITORY VÀ CHỐT ĐƯỜNG CHẠY (15 – 45 PHÚT)
## Đề tài: T3. Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm 01)

---

### BẢNG TỔNG KẾT BƯỚC 2 (ĐỐI CHIẾU TIÊU CHÍ SLIDE CHUẨN)

| Câu hỏi khi đọc nguồn | Ghi chép chi tiết của Nhóm 01 |
| :--- | :--- |
| **1. Paper / Repo chính thức được chọn** | • **Repo SOTA 1 (Challenge):** `Galibr: Targetless LiDAR-Camera Calibration` (IEEE IV 2024 / PRBonn, repo: `https://github.com/PRBonn/galibr`).<br>• **Repo SOTA 2 (Continuous):** `CalibRefine: Continuous Online Extrinsic Calibration` (IEEE TIM 2026 / XCalib repo: `https://github.com/hku-mars/CalibRefine`).<br>• **Paper SOTA 3 (Direct & Fast):** `DF-Calib` (*arXiv:2504.01416*, 2025).<br>• **Paper Benchmark nền tảng [S5]:** *Dong et al., CVPR 2023* (*Benchmarking Robustness in 3D Object Detection Against Sensor Corruptions* - nuScenes-C / KITTI-C). |
| **2. Phương pháp nhận gì và tạo gì? (Input $\to$ Output)** | • **Input:** Ảnh RGB ($1600 \times 900$ hoặc Full HD 1080p), Đám mây điểm LiDAR thô ($N \times 3$), Ma trận nội suy Camera $K$ ($f_x, f_y, c_x, c_y$), Ma trận ngoại thông số danh định ban đầu $T_0$.<br>• **Output:** Ma trận ngoại thông số tối ưu $T_{\text{cam\_lidar}} = [R \mid t] \in SE(3)$ gồm 6 bậc tự do (6-DoF), sai số chiếu lại (MRE) và Similarity Confidence Score. |
| **3. Giả định & Điều kiện của nguồn (Assumptions)** | • Camera đã được khử méo quang học chuẩn (undistorted pinhole).<br>• Đồng bộ thời gian giữa Camera và LiDAR ở mức vi mô (PTP/PPS offset &lt; 20ms).<br>• Khung cảnh có tối thiểu 2–3 vật thể tĩnh có biên cạnh hình học rõ rệt (tòa nhà, cột đèn, xe đỗ, mép vỉa hè). |
| **4. Nguồn đo chất lượng bằng gì? (Metrics)** | • Nguồn CalibRefine/Galibr đo: Sai số góc xoay $\Delta R$ (độ), sai số tịnh tiến $\Delta t$ (cm), Chamfer edge distance.<br>• Nguồn benchmark Dong et al. CVPR 2023 đo: Độ sụt giảm $mAP$ và $NDS$ (nuScenes Detection Score) của các mạng PointPainting, CenterPoint, BEVFusion dưới các mức suy thoái ngoại thông số. |
| **5. Có chạy được nguyên bản ở lớp không? (Feasibility)** | • **Khảo sát tính khả thi trong 120 phút:** Repo nguyên bản của CalibRefine/Galibr yêu cầu môi trường ROS/ROS2, CUDA TensorRT, GPU dung lượng lớn (NVIDIA Jetson AGX Orin / RTX 3080+) và tải bộ trọng số/dataset hoàn chỉnh hàng chục GB $\to$ **Không khả thi để build và chạy end-to-end trong thời gian 120 phút tại lớp.** |
| **6. Nhóm chọn đường chạy nào? (Setup khả thi)** | • **Đường chạy khả thi đã chốt:** Chạy **Benchmark mô phỏng có đối chứng trực tiếp trên cặp dữ liệu thật nuScenes v1.0-mini** (`scripts/run_calibration_drift.py`) và ứng dụng mô phỏng trực quan tương tác 60 FPS (`DEMO_SIMULATOR.html`).<br>• **Metric thật của nhóm:** Đo trực tiếp sai số hình học **Mean Reprojection Error (MRE)** tính bằng pixel ($px$) và tỷ lệ rơi điểm **Point-to-Box Association Recall** (%).<br>• **Metric proxy:** Sử dụng mức suy giảm tỷ lệ điểm LiDAR rơi vào trong Bounding Box 2D để làm proxy cho $mAP$ Drop. *(Lý do: Khi điểm laser rơi ra ngoài Bbox, mạng Fusion gán nhầm đặc trưng nền vào voxel rỗng, trực tiếp gây rớt mAP như chứng minh trong paper Dong et al.)*. |
| **7. Khả năng tái hiện (Truy vết kết quả)** | • **Repo GitHub:** `https://github.com/huybla166/K4-Track4-Day04-Team01-Sensor-Reality-Sprint`<br>• **Dataset sử dụng:** nuScenes v1.0-mini keyframe `CAM_FRONT` × `LIDAR_TOP` (34.688 điểm 3D).<br>• **Lệnh chạy tái hiện:** `python scripts/run_calibration_drift.py`<br>• **File kết quả lưu tự động:** `results/calibration_drift_metrics.csv`, `results/image1.png`, `results/image2.png`. |

---

### TỰ KIỂM TRA BƯỚC 2 (SELF-CHECKLIST)
- [x] **Nói ngắn gọn được "Phương pháp nhận gì, trả gì, đo bằng gì"?**  
  $\to$ *Nhận: Ảnh RGB + Điểm LiDAR + Ma trận K. Trả về: Ma trận ngoại thông số 6-DoF $T \in SE(3)$ bù trừ góc lệch. Đo bằng: Reprojection Error (pixels) và Point-in-Bbox Recall (%).*
- [x] **Đã phân tách rạch ròi kết luận của Paper vs kết quả tự đo của nhóm chưa?**  
  $\to$ *Có: Paper Dong et al. CVPR 2023 kết luận mạng Fusion rớt 42% mAP; Nhóm tự đo trực tiếp tại lớp thấy sai số hình học vọt lên 47.93 px và Recall người đi bộ 25m rớt về 16% ở mức lệch 2.0°.*
- [x] **Có lệnh chạy và đường chạy rõ ràng không?**  
  $\to$ *Có lệnh chạy Python thực thi ngay lập tức trong 3 giây và giao diện HTML tương tác click mở tức thì.*
