from preprocessing.useData import Choose_Open
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
    Construit des modèles de régression pour prédire le RSSI et le SNR, puis évalue, analyse et visualise leurs performances. 
"""

def plot_feature_importance(
          model, 
          X_test, 
          y_test, 
          title, 
          file_name,
          save_path):
    """
    Calculate feature importance using permutation method
    """
    print(f"\nCalculating importance for {title}")
    
    from sklearn.inspection import permutation_importance
    
    result = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, n_jobs=-1)
    
    feature_names = model.named_steps["prep"].get_feature_names_out()
    importances = result.importances_mean
    
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
    
    os.makedirs(save_path, exist_ok=True)
    save_path_final = os.path.join(save_path, file_name)

    if save_path_final:
        plt.savefig(save_path_final, dpi=150)
    
    return save_path_final

def run_signal_models(
          year: int, 
          month: int, 
          data_type: str, 
          save_path: str = None):
    """
    Trains and evaluates regression models for RSSI and SNR. 
    """

    # LOAD DATA
    df = Choose_Open(year, month, (data_type,))

    # TIME FEATURES
    df["timestamp"] = pd.to_datetime(df.index)
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.weekday

    # PAIR COUNTS
    df_temp = df.dropna(subset=['rssi'])
    pair_counts = df_temp.groupby(['Dev_Add', 'GW_EUI']).size()

    # FEATURES
    num_features = ["Bandwidth", "SF", "size", "hour", "weekday"]
    cat_features = ["freq", "Coding_rate", "Dev_Add", "GW_EUI", "Type"]

    # RSSI MODEL
    df_rssi = df[df["rssi"].notna()].copy()

    devs = df_rssi["Dev_Add"].unique()
    train_devs, test_devs = train_test_split(devs, test_size=0.2, random_state=42)

    train_mask = df_rssi["Dev_Add"].isin(train_devs)
    test_mask = df_rssi["Dev_Add"].isin(test_devs)

    df_train = df_rssi.loc[train_mask]
    df_test = df_rssi.loc[test_mask]

    X_train = df_train[num_features + cat_features]
    X_test = df_test[num_features + cat_features]
    y_train = df_train["rssi"]
    y_test_rssi = df_test["rssi"]

    general_stats = {
        "records": str(len(df)),
        "unique_devices": str(df['Dev_Add'].nunique()),
        "unique_gateways": str(df['GW_EUI'].nunique()),
        "device-gw_pairs": str(len(pair_counts))
    }

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

    # RSSI ERROR ANALYSIS
    results_df = X_test.copy()
    results_df["rssi_true"] = y_test_rssi.values
    results_df["rssi_pred"] = y_pred_rssi
    results_df["error"] = np.abs(y_test_rssi.values - y_pred_rssi)

    # ---- Baseline
    baseline_pred = np.full_like(y_test_rssi, y_train.mean())
    baseline_mae = mean_absolute_error(y_test_rssi, baseline_pred)

    rssi_stats = {
        "mean": f"{round(df_rssi['rssi'].mean(),2)}",
        "std": f"{round(df_rssi['rssi'].std(),2)}",
        "range": f"[{round(df_rssi['rssi'].min(),2)}, {round(df_rssi['rssi'].max(),2)}]",
        "mae": f"{round(mean_absolute_error(y_test_rssi, y_pred_rssi),2)}",
        "r2": f"{round(r2_score(y_test_rssi, y_pred_rssi),3)}",
        "baseline_mae": f"{round(baseline_mae,2)}",
        "improvement_pct": f"{round((1 - mean_absolute_error(y_test_rssi, y_pred_rssi)/baseline_mae)*100,1)} %",
        "mae_as_pctage_of_std_dev": f"{round(mean_absolute_error(y_test_rssi, y_pred_rssi)/y_train.std()*100,1)} %"
    }

    # SNR MODEL
    df_snr = df[df["lsnr"].notna()].copy()

    devs = df_snr["Dev_Add"].unique()
    train_devs, test_devs = train_test_split(devs, test_size=0.2, random_state=42)

    train_mask = df_snr["Dev_Add"].isin(train_devs)
    test_mask = df_snr["Dev_Add"].isin(test_devs)

    df_train = df_snr.loc[train_mask]
    df_test = df_snr.loc[test_mask]

    X_train = df_train[num_features + cat_features]
    X_test = df_test[num_features + cat_features]
    y_train = df_train["lsnr"]
    y_test_snr = df_test["lsnr"]

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

    baseline_pred = np.full_like(y_test_snr, y_train.mean())
    baseline_mae = mean_absolute_error(y_test_snr, baseline_pred)

    snr_stats = {
        "mean": f"{round(df_snr['lsnr'].mean(),2)}",
        "std": f"{round(df_snr['lsnr'].std(),2)}",
        "range": f"[{round(df_snr['lsnr'].min(),2)}, {round(df_snr['lsnr'].max(),2)}]",
        "mae": f"{round(mean_absolute_error(y_test_snr, y_pred_snr),2)}",
        "r2": f"{round(r2_score(y_test_snr, y_pred_snr),3)}",
        "baseline_mae": f"{round(baseline_mae,2)}",
        "improvement_pct": f"{round((1 - mean_absolute_error(y_test_snr, y_pred_snr)/baseline_mae)*100,1)} %",
        "mae_as_pctage_of_std_dev": f"{round(mean_absolute_error(y_test_snr, y_pred_snr)/y_train.std()*100,1)} %"
    }

    # FEATURE IMPORTANCE
    print("\nGenerating feature importance plots")

    # Nettoie le nom du fichier pour qu'il soit valide
    def _sanitize(s: str) -> str:
        keep = []
        for ch in s:
            if ch.isalnum() or ch in ('-', '_'):
                keep.append(ch)
            elif ch.isspace():
                keep.append('_')
        return ''.join(keep)
    
    # Génère le nom de fichier par défaut
    def _make_default_filename(title) -> str:
        dt = _sanitize(data_type.replace(' ', '_'))
        return f"{title}_{dt}_{year:04d}-{int(month):02d}.png"

    # Default images folder: ../../Images
    if save_path:
        images_dir = save_path
    else:
        images_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Images'))

    rssi_plot_path = plot_feature_importance(model_rssi, X_test, y_test_rssi.values, "RSSI", _make_default_filename("feature_importance_rssi"), images_dir)
    snr_plot_path = plot_feature_importance(model_snr, X_test, y_test_snr.values, "SNR", _make_default_filename("feature_importance_snr"), images_dir)

    # RESIDUAL PLOTS
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # RSSI residuals
    residuals_rssi = y_test_rssi.values - y_pred_rssi
    residuals_snr = y_test_snr.values - y_pred_snr

    axes[0].scatter(y_pred_rssi, residuals_rssi, alpha=0.3, s=10)
    axes[0].axhline(0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Predicted RSSI', fontsize=12)
    axes[0].set_ylabel('Residuals', fontsize=12)
    axes[0].set_title('RSSI Model - Residual Plot', fontsize=14, fontweight='bold')
    axes[0].grid(alpha=0.3)

    # SNR residuals
    axes[1].scatter(y_pred_snr, residuals_snr, alpha=0.3, s=10)
    axes[1].axhline(0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Predicted SNR', fontsize=12)
    axes[1].set_ylabel('Residuals', fontsize=12)
    axes[1].set_title('SNR Model - Residual Plot', fontsize=14, fontweight='bold')
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    residuals_path = os.path.join(images_dir, _make_default_filename("residual_plots"))
    plt.savefig(residuals_path, dpi=150)
    plt.close(fig)

    return {
        "images": {
            "rssi_plot": rssi_plot_path,
            "snr_plot": snr_plot_path,
            "residual_plots": residuals_path
        },
        "stats": {
            "general": general_stats,
            "rssi": rssi_stats,
            "snr": snr_stats
        }
    }

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