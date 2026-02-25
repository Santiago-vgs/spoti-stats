"""K-means mood clustering on audio features."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from src.db.models import AudioFeature
from src.pipeline.load import update_cluster_assignments

FEATURE_COLS = [
    "danceability", "energy", "valence", "acousticness",
    "instrumentalness", "speechiness", "liveness",
]

CLUSTER_LABELS = {
    # These get assigned after clustering based on centroid characteristics
    # For now we use numeric IDs; the API can map them to names
}

N_CLUSTERS = 6


def run_clustering(session: Session) -> dict:
    """Run K-means clustering on audio features. Returns cluster stats."""
    rows = (
        session.query(AudioFeature)
        .filter(AudioFeature.danceability.isnot(None))
        .all()
    )

    if len(rows) < N_CLUSTERS:
        print(f"  Not enough tracks with audio features ({len(rows)}) for clustering.")
        return {}

    track_ids = [r.track_id for r in rows]
    X = np.array([[getattr(r, col) or 0.0 for col in FEATURE_COLS] for r in rows])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    assignments = dict(zip(track_ids, [int(l) for l in labels]))
    update_cluster_assignments(session, assignments)

    # Compute cluster profiles (mean of original features per cluster)
    cluster_profiles = {}
    for cluster_id in range(N_CLUSTERS):
        mask = labels == cluster_id
        centroid = X[mask].mean(axis=0)
        cluster_profiles[cluster_id] = {
            "count": int(mask.sum()),
            "features": dict(zip(FEATURE_COLS, [round(float(v), 3) for v in centroid])),
        }

    print(f"  Clustered {len(track_ids)} tracks into {N_CLUSTERS} mood groups.")
    return cluster_profiles
