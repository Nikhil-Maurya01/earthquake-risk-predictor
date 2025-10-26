from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. ADD THIS IMPORT
import joblib
import json
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# 1. Initialize the Flask App
app = Flask(__name__)
CORS(app)  # <-- 2. ADD THIS LINE

# 2. Load Models and Config
print("Loading models and config...")
try:
    risk_model = joblib.load('model/risk_level_model.pkl')
    mag_model = joblib.load('model/magnitude_model.pkl')
    
    with open('model/model_config.json', 'r') as f:
        config = json.load(f)
    
    MEAN_DEPTH = config['mean_depth']
    
    print("Models and config loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    print("Please make sure 'risk_level_model.pkl', 'magnitude_model.pkl', and 'model_config.json' are in the 'model/' folder.")
    exit()

# 3. Define the Prediction Route (The "Endpoint")
@app.route('/predict', methods=['POST'])
def predict():
    """
    Listens for a POST request with JSON data:
    { "lat": 19.46, "long": 72.80 }
    """
    try:
        # Get data from the user's request
        data = request.json
        lat = data['lat']
        long = data['long']
        
        # We only get lat/long from the user.
        # We must provide the 'Depth' our model was trained on.
        # We'll use the MEAN_DEPTH we saved from our training data.
        depth = MEAN_DEPTH 

        # 4. Create the Feature DataFrame
        # The model expects a pandas DataFrame in the *exact* format
        # it was trained on, including the column names.
        features_df = pd.DataFrame({
            'Lat': [lat],
            'Long': [long],
            'Depth': [depth]
        })

        # 5. Make Predictions
        risk_prediction = risk_model.predict(features_df)
        magnitude_prediction = mag_model.predict(features_df)

        # 6. Format the Response
        # The predictions are arrays (e.g., ['Medium']), 
        # so we take the first item [0].
        output = {
            'risk_level': risk_prediction[0],
            'predicted_magnitude': round(magnitude_prediction[0], 2) # Round to 2 decimal places
        }
        
        # Send the response back to the user as JSON
        return jsonify(output)

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

# 7. Run the App
if __name__ == '__main__':
    # debug=True means the server will auto-reload when you save the file
    app.run(debug=True, port=5000)