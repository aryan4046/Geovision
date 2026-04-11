"""
clustering.py — GeoVision AI
Hotspot Detection using DBSCAN.
Endpoint: GET /get-hotspots
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from .utils import normalize


# ---------------------------------------------------------------------------
# DBSCAN Hotspot Detection
# ---------------------------------------------------------------------------

def detect_hotspots(
    coordinates: list[dict],
    eps_km: float = 1.5,
    min_samples: int = 3,
) -> dict:
    """
    Identify geographic hotspots from a list of location data points.

    Parameters
    ----------
    coordinates : list[dict]
        Each element:
        {
            "lat": float,
            "lng": float,
            "population":    float,   # optional — used as intensity weight
            "footfall":      float,   # optional
            "accessibility": float    # optional
        }
    eps_km : float
        DBSCAN neighbourhood radius in km (converted to radians for haversine).
    min_samples : int
        Minimum points to form a cluster core.

    Returns
    -------
    dict
        {
            "hotspots": [
                {
                    "lat":       float,
                    "lng":       float,
                    "intensity": float,   # 0-1
                    "cluster_id": int,
                    "point_count": int
                },
                ...
            ],
            "total_clusters": int,
            "noise_points":   int
        }
    """
    if not coordinates:
        return {"hotspots": [], "total_clusters": 0, "noise_points": 0}

    # Build feature matrix: [lat, lng, population, footfall, accessibility]
    X = np.array([
        [
            pt["lat"],
            pt["lng"],
            float(pt.get("population",    50_000)),
            float(pt.get("footfall",      500)),
            float(pt.get("accessibility", 5.0)),
        ]
        for pt in coordinates
    ])

    # Geo features in radians for haversine metric
    coords_rad = np.radians(X[:, :2])

    # Convert eps from km to radians (Earth radius ≈ 6371 km)
    eps_rad = eps_km / 6371.0

    db = DBSCAN(
        eps=eps_rad,
        min_samples=min_samples,
        algorithm="ball_tree",
        metric="haversine",
    ).fit(coords_rad)

    labels = db.labels_

    # ── Aggregate clusters ──────────────────────────────────────────────────
    cluster_ids = set(labels) - {-1}
    hotspots    = []

    # Compute raw intensities (population + footfall normalisation)
    pop_vals  = X[:, 2].tolist()
    foot_vals = X[:, 3].tolist()
    all_intensity = [p + f for p, f in zip(pop_vals, foot_vals)]
    max_intensity = max(all_intensity) or 1.0

    for cid in sorted(cluster_ids):
        mask     = labels == cid
        cluster_pts = X[mask]
        raw_pts_full = [coordinates[i] for i, m in enumerate(mask) if m]

        centroid_lat = float(cluster_pts[:, 0].mean())
        centroid_lng = float(cluster_pts[:, 1].mean())

        # Intensity = normalised sum of population + footfall within cluster
        cluster_intensity_sum = sum(
            (float(p.get("population", 50_000)) + float(p.get("footfall", 500)))
            for p in raw_pts_full
        )
        intensity = round(cluster_intensity_sum / (max_intensity * len(raw_pts_full)), 4)
        intensity = min(1.0, intensity)

        hotspots.append(
            {
                "lat":         round(centroid_lat, 6),
                "lng":         round(centroid_lng, 6),
                "intensity":   intensity,
                "cluster_id":  int(cid),
                "point_count": int(mask.sum()),
            }
        )

    hotspots.sort(key=lambda h: h["intensity"], reverse=True)
    noise_count = int((labels == -1).sum())

    return {
        "hotspots":      hotspots,
        "total_clusters": len(cluster_ids),
        "noise_points":  noise_count,
    }


# ---------------------------------------------------------------------------
# Default sample dataset (used when endpoint is called with no body / for demo)
# ---------------------------------------------------------------------------

SAMPLE_COORDINATES = [
    {"lat": 28.6139, "lng": 77.2090, "population": 120_000, "footfall": 3_500, "accessibility": 7.5},
    {"lat": 28.6200, "lng": 77.2100, "population": 95_000,  "footfall": 2_800, "accessibility": 6.0},
    {"lat": 28.6150, "lng": 77.2080, "population": 110_000, "footfall": 3_200, "accessibility": 8.0},
    {"lat": 28.6145, "lng": 77.2095, "population": 105_000, "footfall": 3_000, "accessibility": 7.0},
    {"lat": 19.0760, "lng": 72.8777, "population": 200_000, "footfall": 8_000, "accessibility": 9.0},
    {"lat": 19.0800, "lng": 72.8800, "population": 180_000, "footfall": 7_500, "accessibility": 8.5},
    {"lat": 19.0750, "lng": 72.8760, "population": 195_000, "footfall": 7_800, "accessibility": 9.2},
    {"lat": 19.0820, "lng": 72.8820, "population": 170_000, "footfall": 7_000, "accessibility": 8.0},
    {"lat": 12.9716, "lng": 77.5946, "population": 150_000, "footfall": 5_000, "accessibility": 8.8},
    {"lat": 12.9750, "lng": 77.5960, "population": 145_000, "footfall": 4_800, "accessibility": 8.6},
    {"lat": 51.5074, "lng": -0.1278,  "population": 300_000, "footfall": 9_000, "accessibility": 9.5},
    {"lat":  0.0000, "lng":  0.0000,  "population":   1_000, "footfall":    50, "accessibility": 1.0},  # noise
]


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = detect_hotspots(SAMPLE_COORDINATES)
    print(f"Total clusters : {result['total_clusters']}")
    print(f"Noise points   : {result['noise_points']}")
    for h in result["hotspots"]:
        print(f"  Cluster {h['cluster_id']}: ({h['lat']}, {h['lng']})  intensity={h['intensity']}  pts={h['point_count']}")
