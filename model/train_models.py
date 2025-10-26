import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, r2_score
import joblib
import json
import warnings

# Suppress warnings for a cleaner output
warnings.filterwarnings('ignore')

print("Script started...")
print("Loading data from 'model/ncs_data.csv'...")

# --- 1. Load Data ---
try:
    df = pd.read_csv('model/ncs_data.csv', encoding='utf-8')
    print("Data loaded successfully.")
except FileNotFoundError:
    print("Error: ncs_data.csv not found in 'model' folder.")
    exit()

# --- 2. Data Cleaning ---

# 2a. Clean 'Magnitude' column
# We convert it to a string, split it at the '[' bracket, take the first part,
# and then convert that part to a number.
print("Cleaning 'Magnitude' column...")
df['mag_value'] = df['Magnitude'].astype(str).str.split('[').str[0]
df['mag_value'] = pd.to_numeric(df['mag_value'], errors='coerce')

# 2b. Clean 'Depth' column
# We find the average depth...
depth_mean = df['Depth'].mean()
# ...and fill any empty (NaN) cells with that average.
print(f"Cleaning 'Depth' column. Missing values will be filled with mean: {depth_mean:.2f}")
df['Depth'] = df['Depth'].fillna(depth_mean)

# 2c. Drop any rows that couldn't be cleaned
# (e.g., if magnitude was just '[ML]' and became NaN)
original_count = len(df)
df = df.dropna(subset=['mag_value', 'Lat', 'Long'])
print(f"Dropped {original_count - len(df)} rows with bad data.")

# --- 3. Create Target Variables (The "answers") ---

# This function turns a number (e.g., 5.3) into a category (e.g., "Medium")
def create_risk_level(mag):
    if mag < 4.0:
        return "Low"
    elif 4.0 <= mag < 6.0:
        return "Medium"
    else:
        return "High"

df['risk_level'] = df['mag_value'].apply(create_risk_level)
print("Created 'risk_level' target variable.")

# --- 4. Define Features (X) and Targets (y) ---

# X = The "clues" our model will use
features = ['Lat', 'Long', 'Depth']
X = df[features]

# y = The "answers" our model will try to guess
y_risk = df['risk_level']      # The categorical target (Low, Medium, High)
y_mag = df['mag_value']       # The numerical target (e.g., 5.1, 6.2)

# --- 5. Split Data for Testing ---
X_train, X_test, y_risk_train, y_risk_test, y_mag_train, y_mag_test = train_test_split(
    X, y_risk, y_mag, test_size=0.2, random_state=42
)
print(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")

# --- 6. Train & Test the RISK LEVEL Model (Classifier) ---
print("\n--- Training Risk Model (Classifier) ---")
# n_estimators=100 means it builds 100 "decision trees"
risk_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
risk_model.fit(X_train, y_risk_train)

risk_predictions = risk_model.predict(X_test)
risk_accuracy = accuracy_score(y_risk_test, risk_predictions)
print(f"Risk Model Accuracy on Test Data: {risk_accuracy * 100:.2f}%")

# --- 7. Train & Test the MAGNITUDE Model (Regressor) ---
print("\n--- Training Magnitude Model (Regressor) ---")
mag_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
mag_model.fit(X_train, y_mag_train)

mag_predictions = mag_model.predict(X_test)
mag_r2 = r2_score(y_mag_test, mag_predictions)
print(f"Magnitude Model R-squared on Test Data: {mag_r2:.2f}")

# --- 8. Save the Final Models & Config ---
print("\nRetraining models on ALL data for final save...")
# We retrain on 100% of the data now
final_risk_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
final_risk_model.fit(X, y_risk)

final_mag_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
final_mag_model.fit(X, y_mag)

# Save the models
joblib.dump(final_risk_model, 'model/risk_level_model.pkl')
joblib.dump(final_mag_model, 'model/magnitude_model.pkl')

# Save the mean depth for our backend to use
config_data = {'mean_depth': depth_mean}
with open('model/model_config.json', 'w') as f:
    json.dump(config_data, f)

print("\nAll done! Three files have been saved in 'model/':")
print("1. risk_level_model.pkl (your risk classifier)")
print("2. magnitude_model.pkl (your magnitude regressor)")
print("3. model_config.json (stores the average depth for predictions)")