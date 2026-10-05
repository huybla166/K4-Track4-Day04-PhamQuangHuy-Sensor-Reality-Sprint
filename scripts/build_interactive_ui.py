import os
import json
import base64
import numpy as np
import cv2

def quat_to_rot_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])

def main():
    root_p130 = r"D:\AI in Action\P-130\v1.0-mini-001"
    v1_dir = os.path.join(root_p130, "v1.0-mini")
    
    with open(os.path.join(v1_dir, "calibrated_sensor.json")) as f: cs = json.load(f)
    with open(os.path.join(v1_dir, "sample_data.json")) as f: sd = json.load(f)

    c_front = [x for x in sd if "CAM_FRONT" in x["filename"] and x["is_key_frame"]][0]
    l_top = [x for x in sd if "LIDAR_TOP" in x["filename"] and x["sample_token"] == c_front["sample_token"]][0]

    cam_calib = [x for x in cs if x["token"] == c_front["calibrated_sensor_token"]][0]
    lidar_calib = [x for x in cs if x["token"] == l_top["calibrated_sensor_token"]][0]

    K = np.array(cam_calib["camera_intrinsic"])
    R_cam = quat_to_rot_matrix(cam_calib["rotation"])
    t_cam = np.array(cam_calib["translation"])

    R_lidar = quat_to_rot_matrix(lidar_calib["rotation"])
    t_lidar = np.array(lidar_calib["translation"])

    # Load image
    img_path = os.path.join(root_p130, c_front["filename"])
    img = cv2.imread(img_path)
    orig_h, orig_w, _ = img.shape
    
    # Scale image to 1280x720 for crisp display and fast canvas rendering
    target_w, target_h = 1280, 720
    scale_x = target_w / orig_w
    scale_y = target_h / orig_h
    img_resized = cv2.resize(img, (target_w, target_h))
    
    # Scale camera intrinsic K accordingly
    K_scaled = K.copy()
    K_scaled[0, :] *= scale_x
    K_scaled[1, :] *= scale_y

    # Encode image as JPEG base64
    _, buf = cv2.imencode('.jpg', img_resized, [cv2.IMWRITE_JPEG_QUALITY, 82])
    img_b64 = base64.b64encode(buf).decode('utf-8')
    img_data_url = f"data:image/jpeg;base64,{img_b64}"

    # Load LiDAR points
    lidar_path = os.path.join(root_p130, l_top["filename"])
    pts_raw = np.fromfile(lidar_path, dtype=np.float32).reshape(-1, 5)[:, :3]

    # Transform to ego frame
    pts_ego = (R_lidar @ pts_raw.T).T + t_lidar
    
    # In camera frame
    pts_cam = (R_cam.T @ (pts_ego - t_cam).T).T
    
    # Filter points in front
    front_mask = (pts_cam[:, 2] > 1.5) & (pts_cam[:, 2] < 70.0)
    pts_ego_front = pts_ego[front_mask]
    pts_cam_front = pts_cam[front_mask]
    
    # Check baseline projection
    homo = (K_scaled @ pts_cam_front.T).T
    u = homo[:, 0] / homo[:, 2]
    v = homo[:, 1] / homo[:, 2]
    
    in_view = (u >= 0) & (u < target_w) & (v >= 0) & (v < target_h)
    pts_ego_inview = pts_ego_front[in_view]
    
    # Subsample points evenly to ~2,200 points for super-smooth 60fps canvas animation
    step = max(1, len(pts_ego_inview) // 2200)
    pts_ego_sub = pts_ego_inview[::step]
    
    print(f"Total points in view: {len(pts_ego_inview)}, Subsampled for real-time UI: {len(pts_ego_sub)}")
    
    # Convert points to compact list of [x, y, z] in ego frame
    points_ego_list = np.round(pts_ego_sub, 3).tolist()
    
    out_dir = r"D:\AI in Action\Labs\K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint\demo_ui"
    os.makedirs(out_dir, exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADAS Sensor Reality Demo · Calibration Drift Simulator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --panel-border: #334155;
            --accent-blue: #38bdf8;
            --accent-green: #22c55e;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 100%);
            border-bottom: 1px solid #312e81;
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-title h1 {{
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge-tag {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-family: 'JetBrains Mono', monospace;
        }}
        .team-meta {{
            font-size: 0.85rem;
            color: var(--text-muted);
            text-align: right;
        }}
        .team-meta strong {{
            color: #e2e8f0;
        }}

        .main-layout {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 20px;
            padding: 20px 28px;
            flex: 1;
        }}

        .viewport-card {{
            background: var(--panel-bg);
            border-radius: 12px;
            border: 1px solid var(--panel-border);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }}

        .viewport-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .viewport-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #cbd5e1;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .toggles-bar {{
            display: flex;
            gap: 14px;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
        .toggles-bar label {{
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }}
        .toggles-bar input[type="checkbox"] {{
            accent-color: var(--accent-blue);
            cursor: pointer;
        }}

        .canvas-container {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #475569;
        }}
        canvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}
        .kpi-card {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .kpi-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .kpi-value {{
            font-size: 1.35rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #f1f5f9;
        }}
        .kpi-sub {{
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        /* Control Sidebar */
        .controls-card {{
            background: var(--panel-bg);
            border-radius: 12px;
            border: 1px solid var(--panel-border);
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            overflow-y: auto;
        }}

        .section-title {{
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #38bdf8;
            margin-bottom: 2px;
        }}

        /* Preset buttons */
        .preset-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        .btn-preset {{
            background: #0f172a;
            border: 1px solid var(--panel-border);
            color: #cbd5e1;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .btn-preset span {{
            font-size: 0.68rem;
            color: var(--text-muted);
            font-weight: 400;
        }}
        .btn-preset:hover {{
            background: #334155;
            border-color: #64748b;
            color: #fff;
        }}
        .btn-preset.active {{
            background: rgba(56, 189, 248, 0.15);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}

        /* Sliders */
        .slider-group {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .slider-row {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .slider-header {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #cbd5e1;
        }}
        .slider-val {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: var(--accent-blue);
        }}
        input[type="range"] {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            -webkit-appearance: none;
            cursor: pointer;
        }}
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: var(--accent-blue);
            cursor: pointer;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.8);
        }}

        /* Decision Status Box */
        .status-box {{
            border-radius: 8px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border: 1px solid #334155;
            background: #0f172a;
            transition: all 0.3s;
        }}
        .status-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            font-weight: 700;
        }}
        .status-indicator {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.3); opacity: 0.7; }}
        }}
        .status-desc {{
            font-size: 0.78rem;
            color: #cbd5e1;
            line-height: 1.4;
        }}
        .status-action {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 6px 10px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.05);
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Tabs bottom section */
        .info-tabs {{
            margin-top: 10px;
            border-top: 1px solid var(--panel-border);
            padding-top: 10px;
        }}
        .tab-nav {{
            display: flex;
            gap: 8px;
            margin-bottom: 10px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 600;
            padding: 4px 8px;
            cursor: pointer;
            border-radius: 4px;
        }}
        .tab-btn.active {{
            color: #fff;
            background: #334155;
        }}
        .tab-pane {{
            display: none;
            font-size: 0.78rem;
            color: #cbd5e1;
            line-height: 1.5;
        }}
        .tab-pane.active {{
            display: block;
        }}

        /* Legend */
        .legend {{
            display: flex;
            gap: 12px;
            font-size: 0.72rem;
            color: var(--text-muted);
            align-items: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-title">
            <span>🚗 ADAS Sensor Reality Sprint</span>
            <span class="badge-tag">Topic 3 · Calibration Drift</span>
            <span class="badge-tag" style="background: rgba(34,197,94,0.15); color: #22c55e; border-color: rgba(34,197,94,0.3)">Live nuScenes Demo</span>
        </div>
        <div class="team-meta">
            <div>Team PhamQuangHuy · <strong>VinUni AI Thực Chiến K04</strong></div>
            <div style="font-size: 0.72rem; color: #64748b;">nuScenes CAM_FRONT × LIDAR_TOP (34,688 points)</div>
        </div>
    </header>

    <div class="main-layout">
        <!-- Left: Canvas Viewport & KPIs -->
        <div class="viewport-card">
            <div class="viewport-header">
                <div class="viewport-title">
                    <span>📡 Multi-Sensor Fusion Projection Frustum</span>
                </div>
                <div class="toggles-bar">
                    <label><input type="checkbox" id="chkGroundTruth" checked> Baseline Points (Cyan)</label>
                    <label><input type="checkbox" id="chkDrifted" checked> Drifted Points (Rainbow/Red)</label>
                    <label><input type="checkbox" id="chkDisplacement" checked> Error Vectors</label>
                    <label><input type="checkbox" id="chkBBox" checked> 2D BBoxes</label>
                </div>
            </div>

            <div class="canvas-container">
                <canvas id="viewCanvas" width="1280" height="720"></canvas>
            </div>

            <div class="legend">
                <div class="legend-item"><span class="dot" style="background: #00f0ff;"></span> Baseline Ground Truth</div>
                <div class="legend-item"><span class="dot" style="background: #ef4444;"></span> Drifted LiDAR Cloud</div>
                <div class="legend-item"><span class="dot" style="background: #eab308;"></span> Reprojection Shift Vector</div>
                <div class="legend-item"><span class="dot" style="background: #22c55e;"></span> Target Bounding Box</div>
            </div>

            <!-- KPI Row -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Mean Reproj Error</div>
                    <div class="kpi-value" id="kpiMeanErr">0.00 px</div>
                    <div class="kpi-sub">Baseline: 0.0 px</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Max Reproj Error</div>
                    <div class="kpi-value" id="kpiMaxErr">0.00 px</div>
                    <div class="kpi-sub">Edge points at Z > 30m</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Point Retention</div>
                    <div class="kpi-value" id="kpiRetention" style="color: #22c55e;">100.0%</div>
                    <div class="kpi-sub">Vehicle 2D Overlap</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Fusion mAP Proxy</div>
                    <div class="kpi-value" id="kpiMap" style="color: #22c55e;">100.0%</div>
                    <div class="kpi-sub">Expected Detection Quality</div>
                </div>
            </div>
        </div>

        <!-- Right: Interactive Controls & Safety ECU Status -->
        <div class="controls-card">
            <div>
                <div class="section-title">⚡ Quick Presets (Benchmark Levels)</div>
                <div class="preset-grid" style="margin-top: 8px;">
                    <button class="btn-preset active" onclick="applyPreset(0.0, 0.0)">
                        Factory Baseline
                        <span>0.0° · 0 cm (Norm)</span>
                    </button>
                    <button class="btn-preset" onclick="applyPreset(0.5, 2.0)">
                        Level 1 (Minor)
                        <span>0.5° · 2 cm (Speedbump)</span>
                    </button>
                    <button class="btn-preset" onclick="applyPreset(1.0, 5.0)">
                        Level 2 (Warning)
                        <span>1.0° · 5 cm (Pothole)</span>
                    </button>
                    <button class="btn-preset" onclick="applyPreset(2.0, 10.0)">
                        Level 3 (Fail-safe)
                        <span>2.0° · 10 cm (Minor collision)</span>
                    </button>
                    <button class="btn-preset" onclick="applyPreset(3.5, 15.0)">
                        Level 4 (Severe)
                        <span>3.5° · 15 cm (Mount bent)</span>
                    </button>
                    <button class="btn-preset" onclick="applyPreset(5.0, 20.0)">
                        Level 5 (Failure)
                        <span>5.0° · 20 cm (Dislodged)</span>
                    </button>
                </div>
            </div>

            <div class="slider-group">
                <div class="section-title">🎛️ Continuous Drift Controls</div>
                
                <div class="slider-row">
                    <div class="slider-header">
                        <span>Yaw Drift (Δθz)</span>
                        <span class="slider-val" id="valYaw">0.0°</span>
                    </div>
                    <input type="range" id="sliderYaw" min="-5.0" max="5.0" step="0.1" value="0.0">
                </div>

                <div class="slider-row">
                    <div class="slider-header">
                        <span>Pitch Drift (Δθx)</span>
                        <span class="slider-val" id="valPitch">0.0°</span>
                    </div>
                    <input type="range" id="sliderPitch" min="-3.0" max="3.0" step="0.1" value="0.0">
                </div>

                <div class="slider-row">
                    <div class="slider-header">
                        <span>Translation X (Δx)</span>
                        <span class="slider-val" id="valTransX">0 cm</span>
                    </div>
                    <input type="range" id="sliderTransX" min="-30" max="30" step="1" value="0">
                </div>
                
                <div class="slider-row">
                    <div class="slider-header">
                        <span>Translation Y (Δy)</span>
                        <span class="slider-val" id="valTransY">0 cm</span>
                    </div>
                    <input type="range" id="sliderTransY" min="-30" max="30" step="1" value="0">
                </div>
            </div>

            <!-- ADAS Safety & Fallback State Machine -->
            <div>
                <div class="section-title">🛡️ ADAS ECU Safety State Machine</div>
                <div class="status-box" id="statusBox" style="margin-top: 8px;">
                    <div class="status-header">
                        <div class="status-indicator" id="statusDot" style="background: #22c55e;"></div>
                        <span id="statusTitle" style="color: #22c55e;">NORMAL OPERATION</span>
                    </div>
                    <div class="status-desc" id="statusDesc">
                        Extrinsic geometry within tolerance. Camera-LiDAR early/late fusion active with 100% confidence.
                    </div>
                    <div class="status-action" id="statusAction">
                        ACTION: System Healthy · Normal Drive
                    </div>
                </div>
            </div>

            <!-- Tabbed Tech Notes for Pitch -->
            <div class="info-tabs">
                <div class="tab-nav">
                    <button class="tab-btn active" onclick="switchTab('tab-calib')">Galibr Targetless</button>
                    <button class="tab-btn" onclick="switchTab('tab-math')">Geometry Math</button>
                    <button class="tab-btn" onclick="switchTab('tab-safety')">Safety Logic</button>
                </div>
                <div class="tab-pane active" id="tab-calib">
                    <strong>Challenge Repo: Galibr (PRBonn 2024)</strong><br>
                    • <em>Input:</em> Raw LiDAR cloud + RGB frame.<br>
                    • <em>Method:</em> Depth discontinuities ↔ Photometric edges Chamfer distance minimization.<br>
                    • <em>Limitation:</em> Needs rich geometric/edge scenes; 200–500ms execution latency.
                </div>
                <div class="tab-pane" id="tab-math">
                    <strong>Projection Pipeline:</strong><br>
                    1. \(P_{{cam}} = R_{{cam}}^T (P_{{ego}} - t_{{cam}})\)<br>
                    2. \([u, v, 1]^T \sim K \cdot P_{{cam}}\)<br>
                    3. \(\text{{Error}} = \sqrt{{(u_{{pert}} - u_0)^2 + (v_{{pert}} - v_0)^2}}\)
                </div>
                <div class="tab-pane" id="tab-safety">
                    <strong>Decision Thresholds:</strong><br>
                    • <strong>< 10 px:</strong> Safe, nominal fusion.<br>
                    • <strong>10–20 px (1.0°–2.0°):</strong> Degraded; queue Galibr online calibration at standstill.<br>
                    • <strong>≥ 20 px (> 2.0°):</strong> Cut fusion; Fallback to LiDAR-only for AEB safety!
                </div>
            </div>
        </div>
    </div>

    <script>
        // Camera Intrinsics scaled to 1280x720
        const K = [
            [{K_scaled[0,0]}, {K_scaled[0,1]}, {K_scaled[0,2]}],
            [{K_scaled[1,0]}, {K_scaled[1,1]}, {K_scaled[1,2]}],
            [{K_scaled[2,0]}, {K_scaled[2,1]}, {K_scaled[2,2]}]
        ];
        
        // Nominal Camera Extrinsics in Ego frame
        const R_cam_nominal = {json.dumps(R_cam.tolist())};
        const t_cam_nominal = {json.dumps(t_cam.tolist())};

        // Ego points (subsampled: {len(points_ego_list)} points)
        const egoPoints = {json.dumps(points_ego_list)};

        // Bounding boxes in 1280x720 coords:
        // Scaled veh_box: [600, 450, 1000, 750] * scale
        const vehBox = [{int(600 * scale_x)}, {int(450 * scale_y)}, {int(1000 * scale_x)}, {int(750 * scale_y)}];
        const tightBox = [{int(720 * scale_x)}, {int(450 * scale_y)}, {int(780 * scale_x)}, {int(530 * scale_y)}];

        const canvas = document.getElementById('viewCanvas');
        const ctx = canvas.getContext('2d');
        const bgImg = new Image();
        bgImg.src = "{img_data_url}";

        // Precompute baseline projections
        let baseline2D = [];
        let baseVehCount = 0;

        function initBaseline() {{
            baseline2D = [];
            baseVehCount = 0;
            for (let i = 0; i < egoPoints.length; i++) {{
                const p = egoPoints[i];
                // P_cam = R_cam^T * (P_ego - t_cam)
                const dx = p[0] - t_cam_nominal[0];
                const dy = p[1] - t_cam_nominal[1];
                const dz = p[2] - t_cam_nominal[2];

                const xc = R_cam_nominal[0][0]*dx + R_cam_nominal[1][0]*dy + R_cam_nominal[2][0]*dz;
                const yc = R_cam_nominal[0][1]*dx + R_cam_nominal[1][1]*dy + R_cam_nominal[2][1]*dz;
                const zc = R_cam_nominal[0][2]*dx + R_cam_nominal[1][2]*dy + R_cam_nominal[2][2]*dz;

                if (zc > 1.0) {{
                    const u = (K[0][0]*xc + K[0][2]*zc) / zc;
                    const v = (K[1][1]*yc + K[1][2]*zc) / zc;
                    baseline2D.push({{ u, v, z: zc, inView: (u >= 0 && u < 1280 && v >= 0 && v < 720) }});
                    if (u >= vehBox[0] && u <= vehBox[2] && v >= vehBox[1] && v <= vehBox[3]) {{
                        baseVehCount++;
                    }}
                }} else {{
                    baseline2D.push({{ u: -999, v: -999, z: 0, inView: false }});
                }}
            }}
            baseVehCount = Math.max(1, baseVehCount);
        }}

        bgImg.onload = () => {{
            initBaseline();
            render();
        }};

        // Rotation matrix from Euler angles (yaw, pitch, roll in radians)
        function eulerToMatrix(yaw, pitch, roll) {{
            const cy = Math.cos(yaw), sy = Math.sin(yaw);
            const cp = Math.cos(pitch), sp = Math.sin(pitch);
            const cr = Math.cos(roll), sr = Math.sin(roll);

            return [
                [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
                [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
                [-sp,   cp*sr,            cp*cr]
            ];
        }}

        function mat3Mul(A, B) {{
            const C = [[0,0,0],[0,0,0],[0,0,0]];
            for (let i = 0; i < 3; i++) {{
                for (let j = 0; j < 3; j++) {{
                    C[i][j] = A[i][0]*B[0][j] + A[i][1]*B[1][j] + A[i][2]*B[2][j];
                }}
            }}
            return C;
        }}

        function render() {{
            const yawDeg = parseFloat(document.getElementById('sliderYaw').value);
            const pitchDeg = parseFloat(document.getElementById('sliderPitch').value);
            const transXcm = parseFloat(document.getElementById('sliderTransX').value);
            const transYcm = parseFloat(document.getElementById('sliderTransY').value);

            document.getElementById('valYaw').innerText = yawDeg.toFixed(1) + '°';
            document.getElementById('valPitch').innerText = pitchDeg.toFixed(1) + '°';
            document.getElementById('valTransX').innerText = transXcm.toFixed(0) + ' cm';
            document.getElementById('valTransY').innerText = transYcm.toFixed(0) + ' cm';

            const yawRad = yawDeg * Math.PI / 180.0;
            const pitchRad = pitchDeg * Math.PI / 180.0;
            const R_err = eulerToMatrix(yawRad, pitchRad, 0);

            // Perturbed camera rotation & translation
            const R_cam_pert = mat3Mul(R_cam_nominal, R_err);
            const t_cam_pert = [
                t_cam_nominal[0] + transXcm / 100.0,
                t_cam_nominal[1] + transYcm / 100.0,
                t_cam_nominal[2]
            ];

            // Clear canvas & draw background image
            ctx.drawImage(bgImg, 0, 0, 1280, 720);

            const showGT = document.getElementById('chkGroundTruth').checked;
            const showDrifted = document.getElementById('chkDrifted').checked;
            const showDisp = document.getElementById('chkDisplacement').checked;
            const showBBox = document.getElementById('chkBBox').checked;

            if (showBBox) {{
                // Draw Vehicle BBox
                ctx.strokeStyle = '#22c55e';
                ctx.lineWidth = 3;
                ctx.strokeRect(vehBox[0], vehBox[1], vehBox[2] - vehBox[0], vehBox[3] - vehBox[1]);
                ctx.fillStyle = '#22c55e';
                ctx.font = 'bold 12px Inter';
                ctx.fillText('Target Vehicle (Lead)', vehBox[0] + 6, vehBox[1] + 16);

                // Draw Tight BBox
                ctx.strokeStyle = '#f59e0b';
                ctx.lineWidth = 2;
                ctx.strokeRect(tightBox[0], tightBox[1], tightBox[2] - tightBox[0], tightBox[3] - tightBox[1]);
                ctx.fillStyle = '#f59e0b';
                ctx.fillText('Distant Target', tightBox[0] + 4, tightBox[1] + 14);
            }}

            let sumErr = 0;
            let maxErr = 0;
            let validCount = 0;
            let currentVehCount = 0;

            for (let i = 0; i < egoPoints.length; i++) {{
                const p = egoPoints[i];
                const dx = p[0] - t_cam_pert[0];
                const dy = p[1] - t_cam_pert[1];
                const dz = p[2] - t_cam_pert[2];

                // P_cam_pert = R_cam_pert^T * (P_ego - t_cam_pert)
                const xc = R_cam_pert[0][0]*dx + R_cam_pert[1][0]*dy + R_cam_pert[2][0]*dz;
                const yc = R_cam_pert[0][1]*dx + R_cam_pert[1][1]*dy + R_cam_pert[2][1]*dz;
                const zc = R_cam_pert[0][2]*dx + R_cam_pert[1][2]*dy + R_cam_pert[2][2]*dz;

                const base = baseline2D[i];

                if (zc > 1.0) {{
                    const u = (K[0][0]*xc + K[0][2]*zc) / zc;
                    const v = (K[1][1]*yc + K[1][2]*zc) / zc;

                    const inView = (u >= 0 && u < 1280 && v >= 0 && v < 720);

                    if (inView && base && base.inView) {{
                        const err = Math.sqrt((u - base.u)**2 + (v - base.v)**2);
                        sumErr += err;
                        if (err > maxErr) maxErr = err;
                        validCount++;

                        if (u >= vehBox[0] && u <= vehBox[2] && v >= vehBox[1] && v <= vehBox[3]) {{
                            currentVehCount++;
                        }}

                        // Draw baseline point
                        if (showGT) {{
                            ctx.fillStyle = 'rgba(0, 240, 255, 0.5)';
                            ctx.beginPath();
                            ctx.arc(base.u, base.v, 2.0, 0, Math.PI * 2);
                            ctx.fill();
                        }}

                        // Draw displacement vector
                        if (showDisp && err > 2.0 && i % 4 === 0) {{
                            ctx.strokeStyle = 'rgba(234, 179, 8, 0.7)';
                            ctx.lineWidth = 1.2;
                            ctx.beginPath();
                            ctx.moveTo(base.u, base.v);
                            ctx.lineTo(u, v);
                            ctx.stroke();
                        }}

                        // Draw drifted point
                        if (showDrifted) {{
                            // Color by error severity
                            if (err < 5.0) {{
                                ctx.fillStyle = '#38bdf8';
                            }} else if (err < 15.0) {{
                                ctx.fillStyle = '#f59e0b';
                            }} else {{
                                ctx.fillStyle = '#ef4444';
                            }}
                            ctx.beginPath();
                            ctx.arc(u, v, 2.5, 0, Math.PI * 2);
                            ctx.fill();
                        }}
                    }}
                }}
            }}

            const meanErr = validCount > 0 ? (sumErr / validCount) : 0;
            const retention = Math.min(100.0, (currentVehCount / baseVehCount) * 100.0);
            const mAPProxy = Math.max(0.0, 100.0 - Math.pow(meanErr / 1.5, 1.5));

            // Update UI KPIs
            document.getElementById('kpiMeanErr').innerText = meanErr.toFixed(2) + ' px';
            document.getElementById('kpiMaxErr').innerText = maxErr.toFixed(2) + ' px';
            
            const elRet = document.getElementById('kpiRetention');
            elRet.innerText = retention.toFixed(1) + '%';
            elRet.style.color = retention > 95 ? '#22c55e' : (retention > 80 ? '#f59e0b' : '#ef4444');

            const elMap = document.getElementById('kpiMap');
            elMap.innerText = mAPProxy.toFixed(1) + '%';
            elMap.style.color = mAPProxy > 80 ? '#22c55e' : (mAPProxy > 50 ? '#f59e0b' : '#ef4444');

            // Update ADAS Decision Engine
            updateDecisionEngine(meanErr, maxErr, retention);
        }}

        function updateDecisionEngine(meanErr, maxErr, retention) {{
            const box = document.getElementById('statusBox');
            const dot = document.getElementById('statusDot');
            const title = document.getElementById('statusTitle');
            const desc = document.getElementById('statusDesc');
            const action = document.getElementById('statusAction');

            if (meanErr < 10.0) {{
                // Green: Safe
                box.style.borderColor = '#22c55e';
                dot.style.background = '#22c55e';
                title.style.color = '#22c55e';
                title.innerText = 'NORMAL OPERATION (SAFE)';
                desc.innerText = 'Extrinsic calibration within nominal tolerance (< 10 px). Camera-LiDAR fusion maintains high IoU association.';
                action.innerText = 'ACTION: Continue Normal Autonomous Driving';
                action.style.color = '#22c55e';
            }} else if (meanErr < 20.0) {{
                // Amber: Warning
                box.style.borderColor = '#f59e0b';
                dot.style.background = '#f59e0b';
                title.style.color = '#f59e0b';
                title.innerText = 'WARNING: CALIBRATION DEGRADED';
                desc.innerText = 'Mean reprojection error exceeded 10 px (yaw drift ~1.0°). Distant object association drops by 20-30%.';
                action.innerText = 'TRIGGER: Schedule Targetless Online Re-calibration (Galibr) at next standstill';
                action.style.color = '#f59e0b';
            }} else {{
                // Red: Critical Fail-safe
                box.style.borderColor = '#ef4444';
                dot.style.background = '#ef4444';
                title.style.color = '#ef4444';
                title.innerText = 'CRITICAL FAIL-SAFE TRIGGERED';
                desc.innerText = 'Reprojection error ≥ 20 px (> 2.0° yaw drift). Severe spatial mismatch causing false negatives in 3D fusion!';
                action.innerText = 'EMERGENCY: Sever Camera-LiDAR Fusion -> Fallback to LiDAR-only AEB Collision Avoidance';
                action.style.color = '#ef4444';
            }}
        }}

        function applyPreset(yaw, trans) {{
            document.getElementById('sliderYaw').value = yaw;
            document.getElementById('sliderPitch').value = 0;
            document.getElementById('sliderTransX').value = trans;
            document.getElementById('sliderTransY').value = 0;

            const btns = document.querySelectorAll('.btn-preset');
            btns.forEach(b => b.classList.remove('active'));
            if (event && event.currentTarget) event.currentTarget.classList.add('active');

            render();
        }}

        // Listen to controls
        ['sliderYaw', 'sliderPitch', 'sliderTransX', 'sliderTransY'].forEach(id => {{
            document.getElementById(id).addEventListener('input', () => {{
                document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
                render();
            }});
        }});

        ['chkGroundTruth', 'chkDrifted', 'chkDisplacement', 'chkBBox'].forEach(id => {{
            document.getElementById(id).addEventListener('change', render);
        }});

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}
    </script>
</body>
</html>
"""

    html_path = os.path.join(out_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive UI written to: {html_path}")

    # Also write a copy to root as DEMO_SIMULATOR.html so it's super easy to double click
    root_html = r"D:\AI in Action\Labs\K4-Track4-Day04-PhamQuangHuy-Sensor-Reality-Sprint\DEMO_SIMULATOR.html"
    with open(root_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Copied standalone launcher to: {root_html}")

if __name__ == "__main__":
    main()
