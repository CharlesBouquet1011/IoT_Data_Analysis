import json
import os
import sys
import pandas as pd
import numpy as np
import hdbscan
import joblib
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Import de la fonction centralisée pour charger les données
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'preprocessing'))
from useData import Choose_Open


# ======================
# 1. Chargement données
# ======================

def load_packets(json_file_or_dir):
    """Load packets from a single JSON file or recursively from a directory.

    Supports two JSON layouts found in this repo:
    - files where top-level is mapping timestamp -> [entries] (each entry contains 'rxpk')
    - files where top-level is mapping id -> entry (fields directly present, may contain 'Raw_pckt')
    """

    if os.path.isdir(json_file_or_dir):
        dfs = []
        for root, _, files in os.walk(json_file_or_dir):
            for fname in files:
                if not fname.lower().endswith('.json'):
                    continue
                path = os.path.join(root, fname)
                try:
                    df = load_packets(path)
                    if df is not None and not df.empty:
                        dfs.append(df)
                except Exception as e:
                    print(f"Warning: failed to load {path}: {e}")
        if len(dfs) == 0:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    with open(json_file_or_dir, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Essayer de parser comme JSON standard
    try:
        raw = json.loads(content)
    except json.JSONDecodeError:
        # Si échec, essayer comme JSON Lines (une ligne = un objet JSON)
        packets = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if not isinstance(entry, dict):
                    continue
                
                rx = {}
                raw_pckt = entry.get('Raw_pckt') or entry.get('raw_pckt')
                if isinstance(raw_pckt, str):
                    try:
                        parsed = json.loads(raw_pckt)
                        if isinstance(parsed, dict) and 'rxpk' in parsed and isinstance(parsed['rxpk'], list) and len(parsed['rxpk'])>0:
                            rx = parsed['rxpk'][0]
                    except Exception:
                        rx = {}
                
                packets.append({
                    'Dev_Add': entry.get('Dev_Add') or entry.get('dev_add'),
                    'Dev_EUI': entry.get('Dev_EUI') or entry.get('Dev_EUI'.lower()) or entry.get('Dev_EUI'),
                    'SF': entry.get('SF'),
                    'Bandwidth': entry.get('Bandwidth'),
                    'BitRate': entry.get('BitRate'),
                    'Coding_rate': entry.get('Coding_rate') or entry.get('codr'),
                    'Airtime': entry.get('Airtime'),
                    'freq': entry.get('freq') or rx.get('freq'),
                    'rssi': entry.get('rssi') or rx.get('rssi'),
                    'lsnr': entry.get('lsnr') or rx.get('lsnr'),
                    'size': entry.get('size') or rx.get('size'),
                    'Type': entry.get('Type')
                })
            except json.JSONDecodeError:
                continue
        
        return pd.DataFrame(packets)

    packets = []

    if isinstance(raw, dict) and all(isinstance(v, dict) for v in raw.values()):
        for _id, entry in raw.items():
            if not isinstance(entry, dict):
                continue
            rx = {}
            raw_pckt = entry.get('Raw_pckt') or entry.get('raw_pckt')
            if isinstance(raw_pckt, str):
                try:
                    parsed = json.loads(raw_pckt)
                    if isinstance(parsed, dict) and 'rxpk' in parsed and isinstance(parsed['rxpk'], list) and len(parsed['rxpk'])>0:
                        rx = parsed['rxpk'][0]
                except Exception:
                    rx = {}

            packets.append({
                'Dev_Add': entry.get('Dev_Add') or entry.get('dev_add'),
                'Dev_EUI': entry.get('Dev_EUI') or entry.get('Dev_EUI'.lower()) or entry.get('Dev_EUI'),
                'SF': entry.get('SF'),
                'Bandwidth': entry.get('Bandwidth'),
                'BitRate': entry.get('BitRate'),
                'Coding_rate': entry.get('Coding_rate') or entry.get('codr'),
                'Airtime': entry.get('Airtime'),
                'freq': entry.get('freq') or rx.get('freq'),
                'rssi': entry.get('rssi') or rx.get('rssi'),
                'lsnr': entry.get('lsnr') or rx.get('lsnr'),
                'size': entry.get('size') or rx.get('size'),
                'Type': entry.get('Type')
            })

        return pd.DataFrame(packets)

    if isinstance(raw, dict):
        items = raw.items()
    elif isinstance(raw, list):
        items = [(None, raw)]
    else:
        items = []

    for ts, entries in items:
        if isinstance(entries, dict):
            entries = [entries]
        for e in entries:
            if not isinstance(e, dict):
                continue
            if 'rxpk' not in e:
                raw_pckt = e.get('Raw_pckt') or e.get('raw_pckt')
                rx = {}
                if isinstance(raw_pckt, str):
                    try:
                        parsed = json.loads(raw_pckt)
                        if isinstance(parsed, dict) and 'rxpk' in parsed and isinstance(parsed['rxpk'], list) and len(parsed['rxpk'])>0:
                            rx = parsed['rxpk'][0]
                    except Exception:
                        rx = {}
            else:
                rx = e.get('rxpk')[0] if isinstance(e.get('rxpk'), list) and len(e.get('rxpk'))>0 else {}

            packets.append({
                'Dev_Add': e.get('Dev_Add') or e.get('dev_add'),
                'Dev_EUI': e.get('Dev_EUI') or e.get('Dev_EUI'.lower()) or e.get('Dev_EUI'),
                'SF': e.get('SF'),
                'Bandwidth': e.get('Bandwidth'),
                'BitRate': e.get('BitRate'),
                'Coding_rate': e.get('Coding_rate') or e.get('codr'),
                'Airtime': e.get('Airtime'),
                'freq': e.get('freq') or rx.get('freq'),
                'rssi': e.get('rssi') or rx.get('rssi'),
                'lsnr': e.get('lsnr') or rx.get('lsnr'),
                'size': e.get('size') or rx.get('size'),
                'Type': e.get('Type')
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

def train(json_file_or_dir=None, output_dir=None, year=None, month=None, categories=None):
    """Entraîner le modèle de prédiction Dev_EUI.
    
    Deux modes de chargement des données:
    1. Utiliser Choose_Open (recommandé): fournir year, month, categories
    2. Utiliser load_packets (legacy): fournir json_file_or_dir
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "model")

    # Essayer d'abord Choose_Open si les paramètres sont fournis
    if year is not None or month is not None or categories is not None:
        try:
            print(f"Loading data using Choose_Open(year={year}, month={month}, categories={categories})...")
            df = Choose_Open(year=year, month=month, categories=categories)
            print(f"Loaded {len(df)} packets from database")
        except Exception as e:
            print(f"Warning: Choose_Open failed: {e}")
            if json_file_or_dir is None:
                raise ValueError("Choose_Open failed and no json_file_or_dir provided as fallback")
            print(f"Falling back to load_packets({json_file_or_dir})...")
            df = load_packets(json_file_or_dir)
            print(f"Loaded {len(df)} packets from {json_file_or_dir}")
    elif json_file_or_dir is not None:
        # Mode legacy : charger depuis JSON
        df = load_packets(json_file_or_dir)
        print(f"Loaded {len(df)} packets from {json_file_or_dir}")
    else:
        raise ValueError("Must provide either (year/month/categories) or json_file_or_dir")

    start_time = time.time()

    # On garde uniquement les Join Requests avec Dev_EUI connu
    df = df[(df["Type"] == "Join Request") & (df["Dev_EUI"].notna()) & (df["Dev_EUI"] != "")].reset_index(drop=True)
    print(f"Filtered to {len(df)} Join Request packets with Dev_EUI")

    X = df.drop(columns=["Dev_Add", "Dev_EUI"])
    y = df["Dev_EUI"].values

    preprocessor = build_pipeline()
    print("Processing packet features...")
    t0 = time.time()
    X_proc = preprocessor.fit_transform(X)
    print(f"Packet processing done in {time.time()-t0:.1f}s")

    X_sup = X
    y_sup = y
    
    device_counts = pd.Series(y_sup).value_counts()
    print(f"   - Total unique Dev_EUI: {len(device_counts)}")
    print(f"   - Dev_EUI with >=10 packets: {(device_counts >= 10).sum()}")
    print(f"   - Dev_EUI with 5-9 packets: {((device_counts >= 5) & (device_counts < 10)).sum()}")
    print(f"   - Dev_EUI with 2-4 packets: {((device_counts >= 2) & (device_counts < 5)).sum()}")
    print(f"   - Dev_EUI with only 1 packet: {(device_counts == 1).sum()}")
    print(f"   - Total packets: {len(y_sup)}\n")

    classifier = None
    label_encoder = None
    if len(y_sup) > 0:

        tmp = preprocessor.transform(X_sup)

        if hasattr(tmp, "toarray"):
            X_sup_proc = tmp.toarray().astype(np.float32)
        else:
            X_sup_proc = tmp.astype(np.float32)

        y_sup_filtered = y_sup.copy()

        # Limit training data if too large to prevent OOM
        max_training_samples = 50000
        if len(y_sup_filtered) > max_training_samples:
            print(f"Sampling {max_training_samples} from {len(y_sup_filtered)} samples to reduce memory usage")
            indices = np.random.RandomState(42).choice(len(y_sup_filtered), max_training_samples, replace=False)
            X_sup_proc = X_sup_proc[indices]
            y_sup_filtered = y_sup_filtered[indices]

        label_encoder = LabelEncoder()
        y_enc = label_encoder.fit_transform(y_sup_filtered)

        unique, counts = np.unique(y_enc, return_counts=True)
        single_sample_classes = unique[counts == 1]
        
        if len(single_sample_classes) > 0:
            print(f"Warning: {len(single_sample_classes)} devices have only 1 packet, using non-stratified split")
            X_train, X_val, y_train, y_val = train_test_split(
                X_sup_proc, y_enc, test_size=0.2, random_state=42
            )
        else:
            X_train, X_val, y_train, y_val = train_test_split(
                X_sup_proc, y_enc, test_size=0.2, random_state=42, stratify=y_enc
            )

        base_clf = RandomForestClassifier(n_estimators=100, max_depth=12, n_jobs=1, random_state=42, class_weight='balanced_subsample', max_features='sqrt')
        
        train_unique, train_counts = np.unique(y_train, return_counts=True)
        min_samples_per_class = train_counts.min()
        
        tclf = time.time()
        
        if min_samples_per_class >= 3:
            try:
                classifier = CalibratedClassifierCV(estimator=base_clf, cv=3)
            except TypeError:
                classifier = CalibratedClassifierCV(base_estimator=base_clf, cv=3)
            print(f"Training classifier on {X_train.shape[0]} samples / {len(np.unique(y_enc))} unique Dev_EUI (ALL devices included, with cv=3 calibration)")
            classifier.fit(X_train, y_train)
        elif min_samples_per_class >= 2:
            # Use cv=2 instead
            try:
                classifier = CalibratedClassifierCV(estimator=base_clf, cv=2)
            except TypeError:
                classifier = CalibratedClassifierCV(base_estimator=base_clf, cv=2)
            print(f"Training classifier on {X_train.shape[0]} samples / {len(np.unique(y_enc))} unique Dev_EUI (ALL devices included, with cv=2 calibration)")
            classifier.fit(X_train, y_train)
        else:
            print(f"Training base classifier on {X_train.shape[0]} samples / {len(np.unique(y_enc))} unique Dev_EUI (ALL devices included)")
            base_clf.fit(X_train, y_train)
            
            if len(X_val) > 100 and len(np.unique(y_val)) > 20:
                from sklearn.calibration import CalibratedClassifierCV
                try:
                    classifier = CalibratedClassifierCV(base_clf, method='isotonic', cv='prefit')
                    classifier.fit(X_val, y_val)
                except Exception as e:
                    classifier = base_clf
            else:
                classifier = base_clf
        
        print(f"Classifier trained in {time.time()-tclf:.1f}s")
        y_pred = classifier.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        print(f"Validation accuracy: {acc:.3f} ({len(np.unique(y_train))} devices in train, {len(np.unique(y_val))} in validation)")
        ### Décomentter pour afficher le rapport de classification complet
        # try:
        #     y_val_orig = label_encoder.inverse_transform(y_val)
        #     y_pred_orig = label_encoder.inverse_transform(y_pred)
        #     print("\nClassification report:\n")
        #     print(classification_report(y_val_orig, y_pred_orig, zero_division=0))
        # except Exception:
        #     pass
    else:
        pass

    # ======================
    # Clustering par Dev_EUI
    # ======================

    agg = df.groupby("Dev_EUI").agg({
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

    num_cols = ["SF", "Bandwidth", "BitRate", "Airtime", "freq", "rssi", "lsnr", "size"]
    for col in num_cols:
        try:
            med = df.groupby("Dev_EUI")[col].median()
            iqr = df.groupby("Dev_EUI")[col].quantile(0.75) - df.groupby("Dev_EUI")[col].quantile(0.25)
            med = med.rename(f"{col}_median")
            iqr = iqr.rename(f"{col}_iqr")
            agg = agg.merge(med.reset_index(), on="Dev_EUI", how="left")
            agg = agg.merge(iqr.reset_index(), on="Dev_EUI", how="left")
        except Exception:
            pass

    try:
        pkt_cnt = df.groupby("Dev_EUI").size().rename("packet_count")
        agg = agg.merge(pkt_cnt.reset_index(), on="Dev_EUI", how="left")
    except Exception:
        pass

    cat_cols = [
        c for c in agg.columns
        if ("Type" in c) or ("Coding_rate" in c) or (agg[c].dtype == object)
    ]

    device_features = [c for c in agg.columns if c != "Dev_EUI" and c not in cat_cols]

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

        top_devs = df["Dev_EUI"].value_counts().nlargest(max_devices_for_clustering).index
        agg = agg[agg["Dev_EUI"].isin(top_devs)].reset_index(drop=True)

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

    unique_devices_total = df["Dev_EUI"].nunique()
    device_packet_counts = pd.Series(y).value_counts()
    devices_with_at_least_min_samples = (device_packet_counts >= 10).sum()

    agg_dev_vals = agg["Dev_EUI"].values
    devices_assigned_to_clusters = len(np.unique(agg_dev_vals[clusters != -1]))
    devices_marked_noise = len(np.unique(agg_dev_vals[clusters == -1]))

    print(f"Total unique Dev_EUI in data: {unique_devices_total}")
    print(f"Devices with >=10 packets: {devices_with_at_least_min_samples}")
    print(f"Devices assigned to clusters (non-noise): {devices_assigned_to_clusters}")
    print(f"Devices marked as noise: {devices_marked_noise}")

    # ======================
    # 3. Correspondance cluster → Dev_EUI
    # ======================

    cluster_map = {}
    cluster_distribution = {}
    agg_devices = agg["Dev_EUI"].values
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

    print("Modèle sauvegardé dans:", output_dir)
    print("Clusters détectés :", len(cluster_map))

if __name__ == "__main__":
    default_data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "preprocessing", "Data"))
    print(f"Using data folder: {default_data_dir}")
    train(default_data_dir)