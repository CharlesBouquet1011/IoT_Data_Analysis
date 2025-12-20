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

# Load data
df = pd.read_json("flattened_datas.json") # Replace with the path to the json file
print(f"Total records: {len(df)}")

# Time features
df["timestamp"] = pd.to_datetime(df["@timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["weekday"] = df["timestamp"].dt.weekday

print(f"Unique devices: {df['Dev_Add'].nunique()}")
print(f"Unique gateways: {df['GW_EUI'].nunique()}")

# Check if we have enough samples per device-gateway pair
df_temp = df.dropna(subset=['rssi'])
pair_counts = df_temp.groupby([df_temp['Dev_Add'], df_temp['GW_EUI']]).size()
print(f"\nDevice-Gateway pairs: {len(pair_counts)}")

# Feature definitions
num_features = ["Bandwidth", "SF", "size", "hour", "weekday"]
cat_features = ["freq", "Coding_rate", "Dev_Add", "GW_EUI", "Type"]

# RSSI MODEL 
# Filter rows with valid RSSI
mask_rssi = df["rssi"].notna()
df_rssi = df.loc[mask_rssi].copy()

print(f"Valid RSSI records: {len(df_rssi)}")
print(f"RSSI - Mean: {df_rssi['rssi'].mean():.2f}, Std: {df_rssi['rssi'].std():.2f}")
print(f"RSSI - Range: [{df_rssi['rssi'].min():.2f}, {df_rssi['rssi'].max():.2f}]")

# Device-based split
dev_rssi = df_rssi["Dev_Add"]
train_devs, test_devs = train_test_split(
    dev_rssi.unique(), test_size=0.2, random_state=42
)

train_mask = dev_rssi.isin(train_devs)
test_mask = dev_rssi.isin(test_devs)

df_train = df_rssi.loc[train_mask]
df_test = df_rssi.loc[test_mask]

print(f"Train samples: {len(df_train)}, Test samples: {len(df_test)}")

# Prepare X and y
X_train = df_train[num_features + cat_features]
X_test = df_test[num_features + cat_features]
y_train = df_train['rssi']
y_test = df_test['rssi']

# Preprocessor
preprocessor = ColumnTransformer(
    [
        ("num", "passthrough", num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=50), cat_features),
    ]
)

print("\nTraining RSSI model")

model_rssi = Pipeline([
    ("prep", preprocessor),
    ("gbm", HistGradientBoostingRegressor(
        max_depth=10,
        learning_rate=0.1,      
        max_iter=500,
        min_samples_leaf=20,      
        l2_regularization=1.0,     
        random_state=42,
        verbose=0
    ))
])

model_rssi.fit(X_train, y_train)
y_pred_rssi = model_rssi.predict(X_test)

mae_rssi = mean_absolute_error(y_test, y_pred_rssi)
r2_rssi = r2_score(y_test, y_pred_rssi)

print(f"RSSI MAE: {mae_rssi:.2f}")
print(f"RSSI R²: {r2_rssi:.3f}")

# Baseline comparison
baseline_pred = np.full_like(y_test, y_train.mean())
baseline_mae_rssi = mean_absolute_error(y_test, baseline_pred)
print(f"Baseline MAE (predict mean): {baseline_mae_rssi:.2f}")
print(f"Improvement over baseline: {(1 - mae_rssi/baseline_mae_rssi)*100:.1f}%")
print(f"MAE as % of std dev: {mae_rssi/y_train.std()*100:.1f}%")

# SNR MODEL

mask_snr = df["lsnr"].notna()
df_snr = df.loc[mask_snr].copy()

print(f"\nValid SNR records: {len(df_snr)}")
print(f"SNR - Mean: {df_snr['lsnr'].mean():.2f}, Std: {df_snr['lsnr'].std():.2f}")
print(f"SNR - Range: [{df_snr['lsnr'].min():.2f}, {df_snr['lsnr'].max():.2f}]")

dev_snr = df_snr["Dev_Add"]
train_devs_snr, test_devs_snr = train_test_split(
    dev_snr.unique(), test_size=0.2, random_state=42
)

train_mask_snr = dev_snr.isin(train_devs_snr)
test_mask_snr = dev_snr.isin(test_devs_snr)

df_train_snr = df_snr.loc[train_mask_snr]
df_test_snr = df_snr.loc[test_mask_snr]

X_train_snr = df_train_snr[num_features + cat_features]
X_test_snr = df_test_snr[num_features + cat_features]
y_train_snr = df_train_snr['lsnr']
y_test_snr = df_test_snr['lsnr']

print(f"Train samples: {len(df_train_snr)}, Test samples: {len(df_test_snr)}")

print("\nTraining SNR model")

model_snr = Pipeline([
    ("prep", preprocessor),
    ("gbm", HistGradientBoostingRegressor(
        max_depth=10,
        learning_rate=0.1,
        max_iter=500,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42,
        verbose=0
    ))
])

model_snr.fit(X_train_snr, y_train_snr)
y_pred_snr = model_snr.predict(X_test_snr)

mae_snr = mean_absolute_error(y_test_snr, y_pred_snr)
r2_snr = r2_score(y_test_snr, y_pred_snr)

print(f"SNR MAE: {mae_snr:.2f}")
print(f"SNR R²: {r2_snr:.3f}")

baseline_pred_snr = np.full_like(y_test_snr, y_train_snr.mean())
baseline_mae_snr = mean_absolute_error(y_test_snr, baseline_pred_snr)
print(f"Baseline MAE (predict mean): {baseline_mae_snr:.2f}")
print(f"Improvement over baseline: {(1 - mae_snr/baseline_mae_snr)*100:.1f}%")
print(f"MAE as % of std dev: {mae_snr/y_train_snr.std()*100:.1f}%")

# ERROR ANALYSIS

# RSSI error by SF
results_df = X_test.copy()
results_df['rssi_true'] = y_test.values
results_df['rssi_pred'] = y_pred_rssi
results_df['error'] = np.abs(y_test.values - y_pred_rssi)

print("\nRSSI Error by Spreading Factor:")
print(results_df.groupby('SF')['error'].agg(['mean', 'std', 'count']).round(2))

print("\nRSSI Error by Bandwidth:")
print(results_df.groupby('Bandwidth')['error'].agg(['mean', 'std', 'count']).round(2))

# Top 5 worst devices
print("\nTop 5 devices with highest RSSI error:")
device_errors = results_df.groupby('Dev_Add')['error'].agg(['mean', 'count'])
print(device_errors[device_errors['count'] >= 10].sort_values('mean', ascending=False).head())

# Gateway comparison
print("\nGateway Performance Comparison:")
print(df_rssi.groupby('GW_EUI').agg({
    'rssi': ['mean', 'std', 'count'],
    'lsnr': ['mean', 'std']
}).round(2))

# FEATURE IMPORTANCE

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

print("\nGenerating feature importance plots")
plot_feature_importance(model_rssi, X_test, y_test.values, "RSSI Model")
plot_feature_importance(model_snr, X_test_snr, y_test_snr.values, "SNR Model")

# RESIDUAL PLOT

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# RSSI residuals
axes[0].scatter(y_pred_rssi, y_test - y_pred_rssi, alpha=0.3, s=10)
axes[0].axhline(0, color='red', linestyle='--', linewidth=2)
axes[0].set_xlabel('Predicted RSSI', fontsize=12)
axes[0].set_ylabel('Residuals', fontsize=12)
axes[0].set_title('RSSI Model - Residual Plot', fontsize=14, fontweight='bold')
axes[0].grid(alpha=0.3)

# SNR residuals
axes[1].scatter(y_pred_snr, y_test_snr - y_pred_snr, alpha=0.3, s=10)
axes[1].axhline(0, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Predicted SNR', fontsize=12)
axes[1].set_ylabel('Residuals', fontsize=12)
axes[1].set_title('SNR Model - Residual Plot', fontsize=14, fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()