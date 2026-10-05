# BƯỚC 7 · HƯỚNG DẪN NỘP BÀI TRÊN VLEARN & KIỂM TRA RUBRIC
## Tên Repository chuẩn: K4-Track4-Day04-Team01-Sensor-Reality-Sprint
### Khóa học: AI20K - Track 4: ADAS Sensing & Estimation

---

### 1. ĐỐI CHIẾU TIÊU CHUẨN CẤU TRÚC REPOSITORY (BƯỚC 7)
Đề bài yêu cầu đặt tên thư mục gốc là `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`. Repository của nhóm đã chuẩn chỉnh 100%:

```text
K4-Track4-Day04-Team01-Sensor-Reality-Sprint/
├── TEAMMATES.md                                     # [Bắt buộc] Danh sách thành viên (Họ tên, MSSV, Vai trò)
├── README.md                                        # [Bắt buộc] Báo cáo 1 trang chuẩn Trang 8
├── DEMO_SIMULATOR.html                              # [Demo 40%] Trình mô phỏng tương tác 60 FPS
├── SLIDES.html                                      # [Slide] Bộ Slide thuyết trình 8 trang chuẩn đẹp
├── scripts/
│   ├── run_calibration_drift.py                     # [Code chạy thật] Script benchmark định lượng
│   ├── launch_demo.py                               # Launcher mở demo
│   └── build_interactive_ui.py                      # Script build app
├── results/
│   ├── calibration_drift_metrics.csv                # [Bằng chứng số] Bảng CSV 6 mức thử nghiệm
│   ├── image1.png                                   # [Plot chuẩn] 4 đồ thị sai số giáo trình
│   ├── image2.png                                   # [Plot chuẩn] Trực quan hóa Point-Painting
│   └── calibration_drift_curves.png                 # Đồ thị sai số bổ sung
├── docs/
│   ├── BUOC_1_CHUAN_BI.md                           # Kê khai Bước 1
│   ├── BUOC_2_TIM_NGUON_VA_DUONG_CHAY.md            # Nguồn SOTA & Setup Bước 2
│   ├── BUOC_3_THIET_KE_BENCHMARK.md                 # Ma trận đối chứng Bước 3
│   ├── BUOC_4_THUC_HIEN_BENCHMARK_T3.md             # Kết quả chạy thực tế Bước 4
│   ├── BUOC_5_FAIL_CASE_VA_CAI_TIEN.md              # Phân tích Failure Case Bước 5
│   ├── BUOC_6_HOAN_THIEN_BAO_CAO_PITCH.md           # Kiểm tra trước pitch Bước 6
│   ├── BUOC_7_NOP_BAI_VLEARN.md                     # Hướng dẫn nộp bài Bước 7
│   ├── BAO_CAO_NHOM.md                              # Báo cáo nhóm chi tiết
│   └── PITCH_SLIDES.md                              # Kịch bản pitch 3-5 phút chia vai
└── submissions/                                     # [Bản nộp riêng của từng thành viên]
    ├── SUBMISSION_PhamQuangHuy_2A202602900.md
    ├── SUBMISSION_NgoDucChung_2A202602985.md
    ├── SUBMISSION_TaHoangVinh_2A202602543.md
    └── SUBMISSION_NguyenTranKien_2A202602571.md
```

---

### 2. CÁC BƯỚC NỘP BÀI DÀNH CHO TỪNG THÀNH VIÊN TRÊN VLEARN

#### Bước 2.1: Đẩy mã nguồn lên GitHub của bạn
Chạy 3 lệnh sau trong PowerShell để đồng bộ toàn bộ repo lên GitHub:
```powershell
cd "D:\AI in Action\Labs\K4-Track4-Day04-Team01-Sensor-Reality-Sprint"
git remote add origin https://github.com/huybla166/K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint.git
git branch -M main
git push -u origin main
```

#### Bước 2.2: Lượt nộp riêng của từng thành viên
Mỗi thành viên vào link nộp bài trên VLearn:  
🔗 **[https://vlearn.dev/course/k04-l34-p2-t4/reader?day=D04&part=lab-14687d39-submit](https://vlearn.dev/course/k04-l34-p2-t4/reader?day=D04&part=lab-14687d39-submit)**

1. **Phạm Quang Huy (2A202602900):**  
   Mở file [`submissions/SUBMISSION_PhamQuangHuy_2A202602900.md`](submissions/SUBMISSION_PhamQuangHuy_2A202602900.md), copy toàn bộ nội dung và dán vào VLearn.
2. **Ngô Đức Chung (2A202602985):**  
   Mở file [`submissions/SUBMISSION_NgoDucChung_2A202602985.md`](submissions/SUBMISSION_NgoDucChung_2A202602985.md), copy toàn bộ nội dung và dán vào VLearn.
3. **Tạ Hoàng Vinh (2A202602543):**  
   Mở file [`submissions/SUBMISSION_TaHoangVinh_2A202602543.md`](submissions/SUBMISSION_TaHoangVinh_2A202602543.md), copy toàn bộ nội dung và dán vào VLearn.
4. **Nguyễn Trần Kiên (2A202602571):**  
   Mở file [`submissions/SUBMISSION_NguyenTranKien_2A202602571.md`](submissions/SUBMISSION_NguyenTranKien_2A202602571.md), copy toàn bộ nội dung và dán vào VLearn.

*Lưu ý: Cả 4 thành viên đều dùng chung URL repository: `https://github.com/huybla166/K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint` nhưng mỗi người nộp file riêng mang tên và MSSV của mình.*

---

### 3. KIỂM TRA ĐỐI CHIẾU TIÊU CHÍ BƯỚC 7 (100% COMPLETE)
- [x] Tên thư mục gốc đúng chuẩn: `K4-Track4-Day04-Team01-Sensor-Reality-Sprint`.
- [x] File `TEAMMATES.md` nằm ở thư mục gốc, liệt kê đầy đủ họ tên, MSSV, vai trò.
- [x] Cả 4 bản nộp cá nhân đều dẫn link tới repo chung và các file plot/csv tương ứng.
- [x] Đáp ứng đủ 4 tiêu chí chấm điểm trong PDF (40% Demo/Benchmark, 25% Failure thực tế, 20% Thuật toán, 15% Trade-off).
