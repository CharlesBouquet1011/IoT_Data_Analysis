import joblib
import pandas as pd
import hdbscan
import numpy as np
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

# Le modèle a été entraîné sur les Join Requests avec Dev_EUI
# Il peut maintenant prédire le Dev_EUI d'un dispositif à partir des caractéristiques radio

def load_model():
    preprocessor = None
    classifier = None
    label_encoder = None

    try:
        preprocessor = joblib.load(f"{MODEL_DIR}/preprocessor.pkl")
    except Exception:
        preprocessor = None

    try:
        classifier = joblib.load(f"{MODEL_DIR}/classifier.pkl")
    except Exception:
        classifier = None

    try:
        label_encoder = joblib.load(f"{MODEL_DIR}/label_encoder.pkl")
    except Exception:
        label_encoder = None

    device_preprocessor = None
    device_clusterer = None
    cluster_map = None
    cluster_distribution = None
    try:
        device_preprocessor = joblib.load(f"{MODEL_DIR}/device_preprocessor.pkl")
    except Exception:
        device_preprocessor = None
    try:
        device_clusterer = joblib.load(f"{MODEL_DIR}/device_clusterer.pkl")
    except Exception:
        try:
            device_clusterer = joblib.load(f"{MODEL_DIR}/clusterer.pkl")
        except Exception:
            device_clusterer = None
    try:
        cluster_map = joblib.load(f"{MODEL_DIR}/cluster_map.pkl")
    except Exception:
        cluster_map = None
    try:
        cluster_distribution = joblib.load(f"{MODEL_DIR}/cluster_distribution.pkl")
    except Exception:
        cluster_distribution = None

    return {
        "preprocessor": preprocessor,
        "classifier": classifier,
        "label_encoder": label_encoder,
        "device_preprocessor": device_preprocessor,
        "device_clusterer": device_clusterer,
        "cluster_map": cluster_map,
        "cluster_distribution": cluster_distribution,
    }


def predict_device(packet: dict, top_k: int = 10):
    """
    Prédit le Dev_EUI associé aux caractéristiques radio d'un paquet.
    
    Le modèle a été entraîné sur les paquets Join Request qui contiennent le Dev_EUI.
    Pour les autres types de paquets (Data Up/Down), on extrapole le Dev_EUI en se basant
    sur les caractéristiques radio similaires aux Join Requests connus.
    
    Args:
        packet: Dictionnaire contenant les caractéristiques radio (SF, RSSI, LSNR, freq, etc.)
        top_k: Nombre de candidats Dev_EUI à retourner
    
    Returns:
        Dictionnaire avec la prédiction du Dev_EUI et les candidats possibles
    """
    models = load_model()

    preprocessor = models["preprocessor"]
    classifier = models["classifier"]
    label_encoder = models["label_encoder"]
    device_preprocessor = models["device_preprocessor"]
    device_clusterer = models["device_clusterer"]
    cluster_map = models["cluster_map"]
    cluster_distribution = models["cluster_distribution"]

    df = pd.DataFrame([packet])

    if classifier is not None and preprocessor is not None and label_encoder is not None:
        X = preprocessor.transform(df)
        probs = classifier.predict_proba(X)[0]
        class_labels = classifier.classes_
        top_idx = np.argsort(probs)[::-1][:top_k]
        candidates = []
        for idx in top_idx:
            enc_label = class_labels[idx]
            try:
                device = label_encoder.inverse_transform([enc_label])[0]
            except Exception:
                device = str(enc_label)
            candidates.append({"device": device, "proportion": float(probs[idx])})

        top = candidates[0] if len(candidates) > 0 else {"device": "unknown", "proportion": 0.0}
        return {
            "prediction": top["device"],
            "confidence": float(top["proportion"]),
            "candidates": candidates
        }

    if device_clusterer is not None and device_preprocessor is not None and cluster_distribution is not None:
        try:
            X_dev = device_preprocessor.transform(df)
            cluster, strength = hdbscan.approximate_predict(device_clusterer, X_dev)
            cluster_id = int(cluster[0])
            if cluster_id == -1:
                return {"prediction": "unknown", "confidence": float(strength[0])}
            dist = cluster_distribution.get(cluster_id, None)
            if dist:
                candidates = [{"device": dev, "proportion": float(prop)} for dev, prop in sorted(dist.items(), key=lambda x: x[1], reverse=True)]
            else:
                candidates = [{"device": cluster_map.get(cluster_id, "unknown") if cluster_map else "unknown", "proportion": 1.0}]
            return {"candidates": candidates}
        except Exception:
            return {"prediction": "unknown", "confidence": 0.0}

    # final fallback
    return {"prediction": "unknown", "confidence": 0.0}


# ======================
# Exemple d’utilisation
# ======================

if __name__ == "__main__":

    packet = {
        "SF": 7,
        "Bandwidth": 125,
        "BitRate": 5468.75,
        "Coding_rate": "4/5",
        "Airtime": 54.528,
        "freq": 868.1,
        "rssi": -106,
        "lsnr": 6.5,
        "size": 21,
        "Type": "Join Request"
    }

    result = predict_device(packet)
    print("Prédiction du Dev_EUI:")
    print(f"  Dev_EUI prédit: {result.get('prediction', 'N/A')}")
    print(f"  Confiance: {result.get('confidence', 0):.2%}")
    if 'candidates' in result:
        print(f"\n  Top candidats Dev_EUI:")
        for i, cand in enumerate(result['candidates'][:5], 1):
            print(f"    {i}. {cand['device']} (proportion: {cand['proportion']:.2%})")