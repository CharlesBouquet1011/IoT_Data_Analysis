from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
from sklearn.inspection import permutation_importance
import numpy as np
import matplotlib.pyplot as plt
import os
import json

"""
	Charge les données LoRaWAN pré-traitées par type de paquet, mois et année. 
    Construit des modèles de régression pour prédire le RSSI et le SNR, puis évalue, analyse et visualise leurs performances. 
"""

def load_preprocessed_data(year, month, data_type):
    month_str = str(int(month))

    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "preprocessing", "Data")
    base_dir = os.path.normpath(base_dir)
    data_dir = os.path.join(base_dir, str(year), month_str)

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Directory does not exist: {data_dir}")

    known_files = {
        "confirmed data up": "Confirmed Data Up.json",
        "confirmed data down": "Confirmed Data Down.json",
        "join accept": "Join Accept.json",
        "join request": "Join Request.json",
        "proprietary": "Proprietary.json",
        "rfu": "RFU.json",
        "stat": "Stat.json",
        "unconfirmed data up": "Unconfirmed Data Up.json",
        "unconfirmed data down": "Unconfirmed Data Down.json"
    }

    key = data_type.strip().lower()
    filename = known_files.get(key)

    # Partial / fuzzy match
    if filename is None:
        for k, v in known_files.items():
            if k in key or key in k:
                filename = v
                break

    # Fallback: treat data_type as a filename
    if filename is None:
        maybe = data_type if data_type.lower().endswith(".json") else data_type + ".json"
        candidate = os.path.join(data_dir, maybe)
        if os.path.isfile(candidate):
            filename = maybe

    if filename is None:
        raise FileNotFoundError(f"Unknown data type: {data_type}")

    filepath = os.path.join(data_dir, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File does not exist: {filepath}")

    # Load JSON
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize data format
    if isinstance(data, dict):
        entries = list(data.values())
    elif isinstance(data, list):
        entries = data
    else:
        raise ValueError("Invalid JSON format")

    # Convert to DataFrame
    df = pd.DataFrame(entries)
    return df

def plot_feature_importance(model, X_test, y_test, title):
    """
    Calculate feature importance using permutation method
    """
    print(f"\nCalculating importance for {title}")
    
    # Use permutation importance but with fewer repeats for speed
    from sklearn.inspection import permutation_importance
    
    result = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, n_jobs=-1)
    
    feature_names = model.named_steps["prep"].get_feature_names_out()
    importances = result.importances_mean
    
    # Aggregate by base feature
    importance_dict = {}
    for name, imp in zip(feature_names, importances):
        if '__' in name:
            base_name = name.split("__")[-1].split("_")[0]
        else:
            base_name = name
        importance_dict.setdefault(base_name, 0)
        importance_dict[base_name] += imp
    
    names = list(importance_dict.keys())
    values = np.array(list(importance_dict.values()))
    idx = np.argsort(values)
    
    plt.figure(figsize=(10, 6))
    plt.barh(np.array(names)[idx], values[idx], color='steelblue')
    plt.xlabel("Increase in MAE (permutation)", fontsize=12)
    plt.ylabel("Feature", fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

def run_signal_models(year: int, month: int, data_type: str):
    """
    Trains and evaluates regression models for RSSI and SNR. 
    """

    # LOAD DATA
    df = load_preprocessed_data(year, month, data_type)
    print(f"Total records: {len(df)}")
    print(df.head())

    # TIME FEATURES
    df["timestamp"] = pd.to_datetime(df["@timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.weekday

    print(f"Unique devices: {df['Dev_Add'].nunique()}")
    print(f"Unique gateways: {df['GW_EUI'].nunique()}")

    # PAIR COUNTS
    df_temp = df.dropna(subset=['rssi'])
    pair_counts = df_temp.groupby(['Dev_Add', 'GW_EUI']).size()
    print(f"\nDevice-Gateway pairs: {len(pair_counts)}")

    # FEATURES
    num_features = ["Bandwidth", "SF", "size", "hour", "weekday"]
    cat_features = ["freq", "Coding_rate", "Dev_Add", "GW_EUI", "Type"]

    # RSSI MODEL
    df_rssi = df[df["rssi"].notna()].copy()

    print(f"\nValid RSSI records: {len(df_rssi)}")
    print(f"RSSI - Mean: {df_rssi['rssi'].mean():.2f}, Std: {df_rssi['rssi'].std():.2f}")
    print(f"RSSI - Range: [{df_rssi['rssi'].min():.2f}, {df_rssi['rssi'].max():.2f}]")

    devs = df_rssi["Dev_Add"].unique()
    train_devs, test_devs = train_test_split(devs, test_size=0.2, random_state=42)

    train_mask = df_rssi["Dev_Add"].isin(train_devs)
    test_mask = df_rssi["Dev_Add"].isin(test_devs)

    df_train = df_rssi.loc[train_mask]
    df_test = df_rssi.loc[test_mask]

    X_train = df_train[num_features + cat_features]
    X_test = df_test[num_features + cat_features]
    y_train = df_train["rssi"]
    y_test = df_test["rssi"]

    preprocessor = ColumnTransformer(
        [
            ("num", "passthrough", num_features),
            ("cat", OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
                max_categories=50
            ), cat_features),
        ]
    )

    model_rssi = Pipeline([
        ("prep", preprocessor),
        ("gbm", HistGradientBoostingRegressor(
            max_depth=10,
            learning_rate=0.1,
            max_iter=500,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42
        ))
    ])

    print("\nTraining RSSI model")
    model_rssi.fit(X_train, y_train)
    y_pred_rssi = model_rssi.predict(X_test)

    # ---- Baseline
    baseline_pred = np.full_like(y_test, y_train.mean())
    baseline_mae = mean_absolute_error(y_test, baseline_pred)

    print(f"RSSI MAE: {mean_absolute_error(y_test, y_pred_rssi):.2f}")
    print(f"RSSI R²: {r2_score(y_test, y_pred_rssi):.3f}")
    print(f"Baseline MAE: {baseline_mae:.2f}")
    print(f"Improvement over baseline: {(1 - mean_absolute_error(y_test, y_pred_rssi)/baseline_mae)*100:.1f}%")
    print(f"MAE as % of std dev: {mean_absolute_error(y_test, y_pred_rssi)/y_train.std()*100:.1f}%")

    # RSSI ERROR ANALYSIS
    results_df = X_test.copy()
    results_df["rssi_true"] = y_test.values
    results_df["rssi_pred"] = y_pred_rssi
    results_df["error"] = np.abs(y_test.values - y_pred_rssi)

    print("\nRSSI Error by SF:")
    print(results_df.groupby("SF")["error"].agg(["mean", "std", "count"]).round(2))

    print("\nRSSI Error by Bandwidth:")
    print(results_df.groupby("Bandwidth")["error"].agg(["mean", "std", "count"]).round(2))

    print("\nTop 5 devices with highest RSSI error:")
    device_errors = results_df.groupby("Dev_Add")["error"].agg(["mean", "count"])
    print(device_errors[device_errors["count"] >= 10]
          .sort_values("mean", ascending=False).head())
    
    print("\nGateway Performance Comparison:")
    print(df_rssi.groupby('GW_EUI').agg({
        'rssi': ['mean', 'std', 'count'],
        'lsnr': ['mean', 'std']
    }).round(2))

    # SNR MODEL
    df_snr = df[df["lsnr"].notna()].copy()

    print(f"\nValid SNR records: {len(df_snr)}")
    print(f"SNR - Mean: {df_snr['lsnr'].mean():.2f}, Std: {df_snr['lsnr'].std():.2f}")
    print(f"SNR - Range: [{df_snr['lsnr'].min():.2f}, {df_snr['lsnr'].max():.2f}]")

    devs = df_snr["Dev_Add"].unique()
    train_devs, test_devs = train_test_split(devs, test_size=0.2, random_state=42)

    train_mask = df_snr["Dev_Add"].isin(train_devs)
    test_mask = df_snr["Dev_Add"].isin(test_devs)

    df_train = df_snr.loc[train_mask]
    df_test = df_snr.loc[test_mask]

    X_train = df_train[num_features + cat_features]
    X_test = df_test[num_features + cat_features]
    y_train = df_train["lsnr"]
    y_test = df_test["lsnr"]

    model_snr = Pipeline([
        ("prep", preprocessor),
        ("gbm", HistGradientBoostingRegressor(
            max_depth=10,
            learning_rate=0.1,
            max_iter=500,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42
        ))
    ])

    print("\nTraining SNR model")
    model_snr.fit(X_train, y_train)
    y_pred_snr = model_snr.predict(X_test)

    baseline_pred = np.full_like(y_test, y_train.mean())
    baseline_mae = mean_absolute_error(y_test, baseline_pred)

    print(f"SNR MAE: {mean_absolute_error(y_test, y_pred_snr):.2f}")
    print(f"SNR R²: {r2_score(y_test, y_pred_snr):.3f}")
    print(f"Baseline MAE: {baseline_mae:.2f}")
    print(f"Improvement over baseline: {(1 - mean_absolute_error(y_test, y_pred_snr)/baseline_mae)*100:.1f}%")
    print(f"MAE as % of std dev: {mean_absolute_error(y_test, y_pred_snr) / baseline_mae * 100:.1f}%")

    # FEATURE IMPORTANCE
    print("\nGenerating feature importance plots")

    plot_feature_importance(model_rssi, X_test, y_test.values, "RSSI Model")
    plot_feature_importance(model_snr, X_test, y_test.values, "SNR Model")

    # RESIDUAL PLOTS
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # RSSI residuals
    axes[0].scatter(y_pred_rssi, y_test - y_pred_rssi, alpha=0.3, s=10)
    axes[0].axhline(0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Predicted RSSI', fontsize=12)
    axes[0].set_ylabel('Residuals', fontsize=12)
    axes[0].set_title('RSSI Model - Residual Plot', fontsize=14, fontweight='bold')
    axes[0].grid(alpha=0.3)

    # SNR residuals
    axes[1].scatter(y_pred_snr, y_test - y_pred_snr, alpha=0.3, s=10)
    axes[1].axhline(0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Predicted SNR', fontsize=12)
    axes[1].set_ylabel('Residuals', fontsize=12)
    axes[1].set_title('SNR Model - Residual Plot', fontsize=14, fontweight='bold')
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Entraîne des modèles RSSI et SNR à partir de données JSON LoRaWAN prétraitées"
    )

    parser.add_argument("year", type=int, help="Année des données")
    parser.add_argument("month", type=int, help="Mois des données (1-12)")
    parser.add_argument("data_type", type=str, help='Type de paquet (ex: "Confirmed Data Up")')

    args = parser.parse_args()

    run_signal_models(args.year, args.month, args.data_type)