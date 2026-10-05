import os
import glob
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import csv

def load_nuscenes_meta(v1_dir):
    with open(os.path.join(v1_dir, "calibrated_sensor.json"), "r") as f:
        calibrated_sensors = json.load(f)
    with open(os.path.join(v1_dir, "sensor.json"), "r") as f:
        sensors = json.load(f)
    with open(os.path.join(v1_dir, "sample_data.json"), "r") as f:
        sample_data = json.load(f)
        
    sensor_map = {s["token"]: s["channel"] for s in sensors}
    calib_map = {}
    for cs in calibrated_sensors:
        channel = sensor_map.get(cs["sensor_token"], "")
        calib_map[cs["token"]] = {
            "channel": channel,
            "translation": np.array(cs["translation"]),
            "rotation": np.array(cs["rotation"]),
            "camera_intrinsic": np.array(cs["camera_intrinsic"]) if cs["camera_intrinsic"] else None
        }
    return calib_map, sample_data

def quat_to_rot_matrix(q):
    # q is [w, x, y, z] in nuScenes
    w, x, y, z = q
    return np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])

def main():
    root_p130 = r"D:\AI in Action\P-130\v1.0-mini-001"
    v1_dir = os.path.join(root_p130, "v1.0-mini")
    calib_map, sample_data = load_nuscenes_meta(v1_dir)
    
    # Find matching LIDAR_TOP and CAM_FRONT from the same sample
    cam_front_samples = [sd for sd in sample_data if "CAM_FRONT" in sd["filename"] and sd["is_key_frame"]]
    lidar_samples = {sd["sample_token"]: sd for sd in sample_data if "LIDAR_TOP" in sd["filename"] and sd["is_key_frame"]}
    
    target_cam = None
    target_lidar = None
    for cam in cam_front_samples:
        st = cam["sample_token"]
        if st in lidar_samples:
            target_cam = cam
            target_lidar = lidar_samples[st]
            break
            
    if not target_cam or not target_lidar:
        print("Could not find matching sample pair!")
        return

    cam_path = os.path.join(root_p130, target_cam["filename"])
    lidar_path = os.path.join(root_p130, target_lidar["filename"])
    print(f"CAM_FRONT: {cam_path}")
    print(f"LIDAR_TOP: {lidar_path}")
    
    cam_calib = calib_map[target_cam["calibrated_sensor_token"]]
    lidar_calib = calib_map[target_lidar["calibrated_sensor_token"]]
    
    K = cam_calib["camera_intrinsic"]
    R_cam = quat_to_rot_matrix(cam_calib["rotation"])
    t_cam = cam_calib["translation"]
    
    R_lidar = quat_to_rot_matrix(lidar_calib["rotation"])
    t_lidar = lidar_calib["translation"]
    
    # Load LiDAR points (float32: x, y, z, intensity, ring_index)
    pts_raw = np.fromfile(lidar_path, dtype=np.float32).reshape(-1, 5)[:, :3]
    print(f"Loaded {len(pts_raw)} LiDAR points.")
    
    # Transform: LiDAR -> Ego vehicle -> Camera frame
    # P_ego = R_lidar * P_lidar + t_lidar
    pts_ego = (R_lidar @ pts_raw.T).T + t_lidar
    # P_cam = R_cam^T * (P_ego - t_cam)
    pts_cam = (R_cam.T @ (pts_ego - t_cam).T).T
    
    # Baseline projection
    valid_mask = pts_cam[:, 2] > 1.0 # points in front of camera
    pts_cam_front = pts_cam[valid_mask]
    
    pts_2d_homo = (K @ pts_cam_front.T).T
    u_base = pts_2d_homo[:, 0] / pts_2d_homo[:, 2]
    v_base = pts_2d_homo[:, 1] / pts_2d_homo[:, 2]
    
    # Load Image to check bounds (1600 x 900)
    img = cv2.imread(cam_path)
    img_h, img_w, _ = img.shape
    in_view_base = (u_base >= 0) & (u_base < img_w) & (v_base >= 0) & (v_base < img_h)
    
    # Define two boxes:
    # 1. Close-up vehicle (large: 400x300 px)
    veh_box = [600, 450, 1000, 750]
    # 2. Distant vehicle / pedestrian (tight: 60x80 px around u=750, v=480)
    tight_box = [720, 450, 780, 530]
    
    in_box_base = in_view_base & (u_base >= veh_box[0]) & (u_base <= veh_box[2]) & (v_base >= veh_box[1]) & (v_base <= veh_box[3])
    base_box_pts = np.sum(in_box_base)
    
    in_tight_base = in_view_base & (u_base >= tight_box[0]) & (u_base <= tight_box[2]) & (v_base >= tight_box[1]) & (v_base <= tight_box[3])
    base_tight_pts = max(1, np.sum(in_tight_base))
    print(f"Baseline points in large vehicle: {base_box_pts}, in tight distant object: {base_tight_pts}")
    
    # Perturbation experiments (Yaw angle drift: 0.0 to 5.0 degrees, Translation drift: 0 to 20 cm)
    drifts = [
        {"name": "Baseline", "yaw_deg": 0.0, "trans_x_cm": 0.0, "desc": "Factory calibrated"},
        {"name": "Drift L1 (Rung nhẹ)", "yaw_deg": 0.5, "trans_x_cm": 2.0, "desc": "Gờ giảm tốc / rung động ban đầu"},
        {"name": "Drift L2 (Lệch vừa)", "yaw_deg": 1.0, "trans_x_cm": 5.0, "desc": "Ổ gà / giãn nở nhiệt giá đỡ"},
        {"name": "Drift L3 (Lệch nặng)", "yaw_deg": 2.0, "trans_x_cm": 10.0, "desc": "Va quẹt nhẹ gương / cảm biến"},
        {"name": "Drift L4 (Cực nặng)", "yaw_deg": 3.5, "trans_x_cm": 15.0, "desc": "Lệch khung cơ khí nghiêm trọng"},
        {"name": "Drift L5 (Failure)", "yaw_deg": 5.0, "trans_x_cm": 20.0, "desc": "Mất chuẩn hoàn toàn"}
    ]
    
    results = []
    
    out_dir = r"D:\AI in Action\Labs\Lab-Day04-Sensor-Robustness\results_t3"
    os.makedirs(out_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 11))
    axes = axes.flatten()
    
    for idx, d in enumerate(drifts):
        yaw_rad = np.radians(d["yaw_deg"])
        # Rotation drift around Z (yaw)
        R_err = np.array([
            [np.cos(yaw_rad), -np.sin(yaw_rad), 0],
            [np.sin(yaw_rad), np.cos(yaw_rad), 0],
            [0, 0, 1]
        ])
        t_err = np.array([d["trans_x_cm"]/100.0, 0.0, 0.0])
        
        # Perturbed camera pose
        R_cam_perturbed = R_cam @ R_err
        t_cam_perturbed = t_cam + t_err
        
        pts_cam_pert = (R_cam_perturbed.T @ (pts_ego - t_cam_perturbed).T).T
        pts_cam_pert_front = pts_cam_pert[valid_mask]
        
        pts_2d_pert = (K @ pts_cam_pert_front.T).T
        u_pert = pts_2d_pert[:, 0] / pts_2d_pert[:, 2]
        v_pert = pts_2d_pert[:, 1] / pts_2d_pert[:, 2]
        
        # Calculate Reprojection Error (Euclidean distance on 2D plane for in-view points)
        in_view_pert = (u_pert >= 0) & (u_pert < img_w) & (v_pert >= 0) & (v_pert < img_h)
        common_valid = in_view_base & in_view_pert
        
        reproj_errors = np.sqrt((u_pert[common_valid] - u_base[common_valid])**2 + (v_pert[common_valid] - v_base[common_valid])**2)
        mean_reproj_err = float(np.mean(reproj_errors)) if len(reproj_errors) > 0 else 0.0
        max_reproj_err = float(np.max(reproj_errors)) if len(reproj_errors) > 0 else 0.0
        
        in_box_pert = in_view_pert & (u_pert >= veh_box[0]) & (u_pert <= veh_box[2]) & (v_pert >= veh_box[1]) & (v_pert <= veh_box[3])
        in_tight_pert = in_view_pert & (u_pert >= tight_box[0]) & (u_pert <= tight_box[2]) & (v_pert >= tight_box[1]) & (v_pert <= tight_box[3])
        
        veh_pts_still_in = in_box_base & in_box_pert
        assoc_retention = (np.sum(veh_pts_still_in) / (base_box_pts + 1e-6)) * 100.0
        assoc_drop = max(0.0, 100.0 - assoc_retention)
        
        tight_pts_still_in = in_tight_base & in_tight_pert
        tight_retention = (np.sum(tight_pts_still_in) / (base_tight_pts + 1e-6)) * 100.0
        tight_drop = max(0.0, 100.0 - tight_retention)
        
        # Simulated mAP drop proxy: mAP proxy decreases quadratically with reprojection error > 5px
        mAP_proxy = max(0.0, 100.0 - (mean_reproj_err / 1.5)**1.5)
        
        results.append({
            "Condition": d["name"],
            "Yaw_Drift_deg": d["yaw_deg"],
            "Trans_Drift_cm": d["trans_x_cm"],
            "Mean_Reprojection_Error_px": round(mean_reproj_err, 2),
            "Max_Reprojection_Error_px": round(max_reproj_err, 2),
            "Vehicle_Point_Retention_Pct": round(assoc_retention, 2),
            "Vehicle_Association_Drop_Pct": round(assoc_drop, 2),
            "Distant_Object_Association_Drop_Pct": round(tight_drop, 2),
            "Fusion_mAP_Proxy_Pct": round(mAP_proxy, 2)
        })
        
        # Plot overlay sample on subplot
        vis_img = img.copy()
        # Draw vehicle bbox
        cv2.rectangle(vis_img, (veh_box[0], veh_box[1]), (veh_box[2], veh_box[3]), (0, 255, 0), 3)
        # Sample 500 points to draw
        sampled_indices = np.random.RandomState(42).choice(np.where(common_valid)[0], size=min(400, np.sum(common_valid)), replace=False)
        for si in sampled_indices:
            pt_u = int(u_pert[si])
            pt_v = int(v_pert[si])
            depth = pts_cam_pert_front[si, 2]
            color = (int(min(255, depth*5)), int(max(0, 255 - depth*5)), 255)
            cv2.circle(vis_img, (pt_u, pt_v), 3, color, -1)
            
        cv2.putText(vis_img, f"{d['name']}: Yaw={d['yaw_deg']}deg, Trans={d['trans_x_cm']}cm", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
        cv2.putText(vis_img, f"Reproj Err: {mean_reproj_err:.1f}px | Assoc Drop: {assoc_drop:.1f}%", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255) if mean_reproj_err > 15 else (0, 255, 255), 2)
        
        axes[idx].imshow(cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB))
        axes[idx].set_title(f"{d['name']} (Err={mean_reproj_err:.1f}px)", fontsize=12, fontweight='bold')
        axes[idx].axis('off')

    plt.tight_layout()
    overlay_path = os.path.join(out_dir, "calibration_drift_overlays.png")
    plt.savefig(overlay_path, dpi=200)
    plt.close()
    print(f"Saved visual overlay grid to: {overlay_path}")
    
    # Save CSV
    csv_path = os.path.join(out_dir, "calibration_drift_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved CSV metrics to: {csv_path}")
    
    # Plot metric trend curves
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    yaws = [r["Yaw_Drift_deg"] for r in results]
    reprojs = [r["Mean_Reprojection_Error_px"] for r in results]
    drops = [r["Distant_Object_Association_Drop_Pct"] for r in results]
    maps = [r["Fusion_mAP_Proxy_Pct"] for r in results]
    
    ax1.plot(yaws, reprojs, 'ro-', linewidth=2.5, markersize=8)
    ax1.axhline(y=10.0, color='orange', linestyle='--', label='Warning Threshold (10 px)')
    ax1.axhline(y=25.0, color='red', linestyle='--', label='Critical Trigger Threshold (25 px)')
    ax1.set_title("Calibration Drift vs Reprojection Error", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Yaw Angular Drift (Degrees)")
    ax1.set_ylabel("Mean Reprojection Error (Pixels)")
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2.plot(yaws, [r["Distant_Object_Association_Drop_Pct"] for r in results], 'bs-', linewidth=2.5, label="Distant Object Assoc Drop (%)")
    ax2.plot(yaws, [r["Fusion_mAP_Proxy_Pct"] for r in results], 'g^-', linewidth=2.5, label="Fusion mAP Proxy (%)")
    ax2.set_title("Impact on Perception: Association & mAP Drop", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Yaw Angular Drift (Degrees)")
    ax2.set_ylabel("Percentage (%)")
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    curve_path = os.path.join(out_dir, "calibration_drift_curves.png")
    plt.savefig(curve_path, dpi=200)
    plt.close()
    print(f"Saved trend curves to: {curve_path}")
    
    print("\n=== CALIBRATION DRIFT BENCHMARK COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
