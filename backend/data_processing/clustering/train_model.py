import json
import os
import pandas as pd
import numpy as np
import hdbscan
import joblib
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


# ======================
# 1. Chargement données
# ======================
def load_packets(json_file):
    with open(json_file, "r") as f:
        raw = json.load(f)

    packets = []
    for ts, entries in raw.items():
        for e in entries:
            if "rxpk" not in e:
                continue
            rx = e["rxpk"][0]

            packets.append({
                "Dev_Add": e.get("Dev_Add"),
                "SF": e.get("SF"),
                "Bandwidth": e.get("Bandwidth"),
                "BitRate": e.get("BitRate"),
                "Coding_rate": e.get("Coding_rate"),
                "Airtime": e.get("Airtime"),
                "freq": rx.get("freq"),
                "rssi": rx.get("rssi"),
                "lsnr": rx.get("lsnr"),
                "size": rx.get("size"),
                "Type": e.get("Type")
            })

    return pd.DataFrame(packets)

def build_pipeline():
    numeric_features = [
        "SF", "Bandwidth", "BitRate",
        "Airtime", "freq", "rssi",
        "lsnr", "size"
    ]

    categorical_features = [
        "Coding_rate", "Type"
    ]

    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features)
        ]
    )

    return preprocessor

# ======================
# 2. Entraînement
# ======================
def train(json_file, output_dir="model"):
    df = load_packets(json_file)

    start_time = time.time()
    print(f"Loaded {len(df)} packets from {json_file}")

    # On garde uniquement les paquets avec Dev_Add connu
    df = df[df["Dev_Add"].notna()].reset_index(drop=True)

    X = df.drop(columns=["Dev_Add"])
    y = df["Dev_Add"].values

    preprocessor = build_pipeline()
    print("Preprocessing packet features...")
    t0 = time.time()
    X_proc = preprocessor.fit_transform(X)
    print(f"Packet preprocessing done in {time.time()-t0:.1f}s")

    min_samples_for_supervised = 10
    device_counts = pd.Series(y).value_counts()
    eligible_devices = set(device_counts[device_counts >= min_samples_for_supervised].index)

    sup_mask = df["Dev_Add"].isin(eligible_devices)
    X_sup = X[sup_mask.values]
    y_sup = y[sup_mask.values]

    classifier = None
    label_encoder = None
    if len(y_sup) > 0:

        tmp = preprocessor.transform(X_sup)

        if hasattr(tmp, "toarray"):
            X_sup_proc = tmp.toarray().astype(np.float32)
        else:
            X_sup_proc = tmp.astype(np.float32)
        label_encoder = LabelEncoder()
        y_enc = label_encoder.fit_transform(y_sup)

        device_counts_sup = pd.Series(y_sup).value_counts()
        max_supervised_devices = 200
        if len(device_counts_sup) > max_supervised_devices:
            top_devices = set(device_counts_sup.nlargest(max_supervised_devices).index)
            sel_mask = np.isin(y_sup, list(top_devices))
            X_sup_proc = X_sup_proc[sel_mask]
            y_enc = y_enc[sel_mask]

        max_supervised_samples = 50000
        if X_sup_proc.shape[0] > max_supervised_samples:
            num_classes = len(np.unique(y_enc))
            per_class = max(1, max_supervised_samples // num_classes)
            idx_list = []
            rng = np.random.default_rng(42)
            for cl in np.unique(y_enc):
                idxs = np.where(y_enc == cl)[0]
                if len(idxs) > per_class:
                    pick = rng.choice(idxs, size=per_class, replace=False)
                else:
                    pick = idxs
                idx_list.append(pick)
            sampled_idx = np.concatenate(idx_list)
            X_sup_proc = X_sup_proc[sampled_idx]
            y_enc = y_enc[sampled_idx]

        X_train, X_val, y_train, y_val = train_test_split(X_sup_proc, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

        classifier = RandomForestClassifier(n_estimators=100, max_depth=16, n_jobs=1, random_state=42)
        print(f"Training classifier on {X_train.shape[0]} samples / {len(np.unique(y_enc))} classes")
        tclf = time.time()
        classifier.fit(X_train, y_train)
        print(f"Classifier trained in {time.time()-tclf:.1f}s")
        y_pred = classifier.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        print(f"Supervised classifier trained on {len(np.unique(y_enc))} devices, validation accuracy: {acc:.3f}")
    else:
        print("No devices with enough samples for supervised training; skipping classifier.")

    # ======================
    # Clustering
    # ======================

    agg = df.groupby("Dev_Add").agg({
        "SF": ["mean", "std"],
        "Bandwidth": ["mean"],
        "BitRate": ["mean", "std"],
        "Airtime": ["median"],
        "freq": ["mean", "nunique"],
        "rssi": ["mean", "std"],
        "lsnr": ["mean", "std"],
        "size": ["mean", "std"],
        "Type": lambda s: s.mode().iloc[0] if len(s.mode())>0 else "",
        "Coding_rate": lambda s: s.mode().iloc[0] if len(s.mode())>0 else ""
    })

    agg.columns = ["_" . join(filter(None, col)).strip() if isinstance(col, tuple) else col for col in agg.columns]
    agg = agg.reset_index()

    cat_cols = [
        c for c in agg.columns
        if ("Type" in c) or ("Coding_rate" in c) or (agg[c].dtype == object)
    ]

    device_features = [c for c in agg.columns if c != "Dev_Add" and c not in cat_cols]

    agg = agg.fillna(0)

    numeric_pipeline = Pipeline(steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_pipeline = Pipeline(steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))])

    device_preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_pipeline, device_features),
        ("cat", categorical_pipeline, cat_cols)
    ])

    max_devices_for_clustering = 3000
    if agg.shape[0] > max_devices_for_clustering:
        print(f"Device profiles ({agg.shape[0]}) > {max_devices_for_clustering}, sampling top devices by packet count")

        top_devs = df["Dev_Add"].value_counts().nlargest(max_devices_for_clustering).index
        agg = agg[agg["Dev_Add"].isin(top_devs)].reset_index(drop=True)

    print(f"Device profiles to cluster: {agg.shape[0]}")
    t1 = time.time()
    X_device_proc = device_preprocessor.fit_transform(agg[device_features + cat_cols])

    if hasattr(X_device_proc, "toarray"):
        X_device_proc = X_device_proc.toarray()
    print(f"Device preprocessing done in {time.time()-t1:.1f}s")

    if hasattr(X_device_proc, "toarray"):
        X_device_proc = X_device_proc.toarray()

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=10,
        min_samples=5,
        prediction_data=True
    )

    print("Clustering device profiles with HDBSCAN...")
    t2 = time.time()
    clusters = clusterer.fit_predict(X_device_proc)
    print(f"Clustering done in {time.time()-t2:.1f}s")

    unique_devices_total = df["Dev_Add"].nunique()
    device_packet_counts = pd.Series(y).value_counts()
    devices_with_at_least_min_samples = (device_packet_counts >= 10).sum()

    agg_dev_vals = agg["Dev_Add"].values
    devices_assigned_to_clusters = len(np.unique(agg_dev_vals[clusters != -1]))
    devices_marked_noise = len(np.unique(agg_dev_vals[clusters == -1]))

    print(f"Total unique Dev_Add in data: {unique_devices_total}")
    print(f"Devices with >=10 packets: {devices_with_at_least_min_samples}")
    print(f"Devices assigned to clusters (non-noise): {devices_assigned_to_clusters}")
    print(f"Devices marked as noise: {devices_marked_noise}")

    # ======================
    # 3. Correspondance cluster → Dev_Add
    # ======================

    cluster_map = {}
    cluster_distribution = {}
    agg_devices = agg["Dev_Add"].values
    for cluster_id in np.unique(clusters):
        if cluster_id == -1:
            continue
        devs = agg_devices[clusters == cluster_id]
        counts = pd.Series(devs).value_counts()
        total = counts.sum()
        cluster_distribution[int(cluster_id)] = (counts / total).to_dict()

        cluster_map[int(cluster_id)] = counts.idxmax()

    cluster_sizes = pd.Series(clusters).value_counts()
    non_noise_clusters = [c for c in np.unique(clusters) if c != -1]
    num_clusters = len(non_noise_clusters)
    devices_total = agg.shape[0]
    print(f"Device profiles: {devices_total} devices -> {num_clusters} clusters")

    # ======================
    # 4. Sauvegarde
    # ======================

    os.makedirs(output_dir, exist_ok=True)

    joblib.dump(preprocessor, f"{output_dir}/preprocessor.pkl")
    if classifier is not None:
        joblib.dump(classifier, f"{output_dir}/classifier.pkl")
    if label_encoder is not None:
        joblib.dump(label_encoder, f"{output_dir}/label_encoder.pkl")

    joblib.dump(device_preprocessor, f"{output_dir}/device_preprocessor.pkl")
    joblib.dump(clusterer, f"{output_dir}/device_clusterer.pkl")
    joblib.dump(cluster_map, f"{output_dir}/cluster_map.pkl")
    joblib.dump(cluster_distribution, f"{output_dir}/cluster_distribution.pkl")

    print("✅ Modèles entraînés et sauvegardés dans:", output_dir)
    print("Clusters détectés :", len(cluster_map))

if __name__ == "__main__":
    train("lorawan_packets_reduced_set.json")
