# BƯỚC 5 · GIẢI THÍCH FAILURE CASE VÀ CHỌN CẢI TIẾN (95 – 115 PHÚT)
## Chủ đề: T3. Calibration Drift Impact & Targetless Online Re-calibration
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation (Nhóm PhamQuangHuy)

---

### BẢNG ĐỐI CHIẾU NĂM CÂU HỎI BẮT BUỘC BƯỚC 5

| Câu cần trả lời | Bằng chứng nhóm đưa ra | Phân loại bản chất thông tin |
| :--- | :--- | :---: |
| **1. Sensor gặp lỗi gì, ở mức nào?** | • **Lỗi:** Lệch góc ngoại thông số quanh trục thẳng đứng kết hợp tịnh tiến ngang.<br>• **Mức lỗi chọn phân tích:** Mức **Drift L3** ($\Delta\text{yaw} = 2.0^\circ, \Delta x = 10\text{ cm}$).<br>• **Mẫu dữ liệu:** nuScenes v1.0-mini keyframe `CAM_FRONT` (1080p, $f_x = 1350\text{ px}$) và `LIDAR_TOP` (34.688 điểm 3D).<br>• **Bằng chứng:** Hình 2 (Case 3 trong `results/image2.png`) và dòng 4 trong `results/calibration_drift_metrics.csv`. | 📌 **Quan sát thực tế**<br>(Đã tạo lỗi và ghi log) |
| **2. Metric thay đổi ra sao so với Baseline?** | • **Sai số chiếu lại MRE:** Từ **0.00 px** (Baseline) vọt lên **47.93 px** (Cực đại ở biên ảnh đạt **72.14 px**).<br>• **Point-to-Box Recall:** Từ **100.0%** sụt xuống **41.3%** ($58.7\%$ điểm laser bị văng ra ngoài xe).<br>• **Bounding Box IoU Overlap:** Từ **1.000** rơi tự do xuống **0.252**.<br>• **Người đi bộ 25m:** Recall sụt thảm hại từ **100.0%** xuống chỉ còn **16.0%**. | 📌 **Số liệu tự đo tại lớp**<br>(Đo đạc định lượng trực tiếp) |
| **3. Thuật toán/tính năng bị ảnh hưởng thế nào?** | • **[Nhóm tự quan sát được]:** Toàn bộ chùm điểm phản xạ laser của chiếc xe tải đi trước bị dịch chuyển trôi lệch hẳn sang làn đường bên cạnh (xem hình minh họa `results/image2.png`).<br>• **[Paper Dong et al., CVPR 2023 cho biết]:** Trên benchmark nuScenes-C, sự trôi dạt ngoại thông số này làm rớt tới $42\%$ mAP của mạng 3D Object Detection do gán nhầm semantic class vào voxel rỗng.<br>• **[Suy luận kỹ thuật ADAS của nhóm]:** Khi chùm laser bị lệch ra khoảng trống, hệ thống phanh tự động AEB tính sai khoảng cách Time-to-Collision (TTC) từ $15\text{m}$ thành $> 40\text{m}$ $\to$ **Xe không kích hoạt phanh, gây nguy cơ đâm va trực diện chết người ở tốc độ cao!** | 📌 **Phân tách rạch ròi**<br>• Đo đạc thực tế<br>• Báo cáo của Paper<br>• Suy luận kỹ thuật |
| **4. Phương pháp còn hạn chế ở đâu? (Limitation)** | • **Hạn chế của bài thử tại lớp:** Dữ liệu mới thử trên 1 cặp keyframe mẫu nuScenes, chưa đo độ trễ phần cứng thực tế (Latency end-to-end trên bus CAN/Ethernet của xe thật) và chưa kết hợp với nhiễu đồng bộ thời gian (Jitter/Timestamp offset).<br>• **Hạn chế từ các Paper/Repo SOTA (Galibr, CalibRefine):** Thuật toán tự cân chỉnh không cọc tiêu sẽ thất bại hoàn toàn khi xe đi vào **đường hầm trơn nhẵn (textureless tunnel)** hoặc mặt đường băng/sa mạc phẳng do hiện tượng **Suy biến mặt phẳng (Planar Degeneracy)**, ma trận Hessian rơi vào điểm kỳ dị không thể hội tụ. | 📌 **Limitation khoa học**<br>(Thừa nhận giới hạn bài thử & trích dẫn limitation từ paper) |
| **5. Nên làm gì tiếp? (Cải tiến & Fallback)** | • **Đề xuất Cải tiến 1:** Xây dựng bộ lọc liên tục EMA và chỉ số giám sát viền hình học `sensor_health_disparity` để phát hiện lệch tâm sớm.<br>• **Đề xuất Fallback An toàn (State Machine S0-S3):** Khi $MRE \ge 30\text{ px}$ hoặc $Recall < 50\%$ $\to$ **Lập tức ngắt hoàn toàn Early Fusion**! Chuyển xe về **LiDAR-only Mode** cho phanh AEB (vì bản thân LiDAR đo khoảng cách vật lý độc lập vẫn đúng 100%) và phát âm thanh Takeover Request cho tài xế.<br>• **Cách kiểm chứng ở vòng thử tiếp theo:** Thu thập 1000 km dữ liệu xe chạy qua nhiều loại gờ giảm tốc đô thị và đo tỷ lệ kích hoạt phanh giả (False Trigger Rate) trước và sau khi có bộ điều khiển Fallback. | 📌 **Quyết định kỹ thuật**<br>(Gắn liền trực tiếp với số đo tại Bước 4) |

---

### TỰ KIỂM TRA BƯỚC 5 (TIÊU CHÍ SLIDE CHUẨN)
- [x] **Có phân biệt rõ ba loại câu không?**  
  $\to$ *Rạch ròi 100%: Có câu "Nhóm quan sát được..." cho kết quả tự đo; "Paper Dong et al. cho biết..." cho kết luận của nguồn; và gắn nhãn rõ "[Suy luận kỹ thuật]" cho nguy cơ đâm va AEB.*
- [x] **Đề xuất cải tiến có nối trực tiếp với failure vừa thấy không?**  
  $\to$ *Có: Thấy failure là do điểm laser bị lệch tâm văng khỏi xe tải $\to$ Cải tiến bằng cách ngắt việc ghép Camera-LiDAR và chuyển về LiDAR-only độc lập để tránh gán nhầm độ sâu.*
- [x] **Có chỉ ra metric/log nào dùng để kiểm tra cải tiến tiếp theo không?**  
  $\to$ *Có: Dùng log `sensor_health_disparity` và metric False Trigger Rate trên 1000 km log thực tế.*
