# Earthquake Risk Predictor 🌍

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-black.svg?style=for-the-badge&logo=flask&logoColor=ffdd54)
![Scikit-learn](https://img.shields.io/badge/SciKit%20Learn-ML%20Model-orange.svg?style=for-the-badge&logo=scikitlearn&logoColor=ffdd54)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-yellow.svg?style=for-the-badge&logo=javascript&logoColor=ffdd54)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

A full-stack web application that assesses the seismic risk for any location in India. This project uses a **Python/Flask** backend to serve a **Scikit-learn** machine learning model and a dynamic **JavaScript** frontend to provide a real-time risk analysis.

Users can input a place name or use their browser's current location to instantly receive a predicted risk level (Low, Medium, High) and a potential earthquake magnitude.

---

## ✨ Features

* **Real-time ML Predictions:** Get a predicted risk level and magnitude from a trained `RandomForestClassifier` and `RandomForestRegressor`.
* **Flexible Input:**
    * Enter any place name (e.g., "Mumbai", "Delhi").
    * Use the "Current Location" button for one-click analysis.
* **Robust Location Validation:** Uses the Nominatim (OpenStreetMap) API for both geocoding (place name → coordinates) and reverse geocoding (coordinates → country) to ensure all queries are for locations within India.
* **Dynamic UI:** A clean, responsive single-page application that switches between input and result "cards" without a page reload.
* **Single-Server Architecture:** The Flask backend serves both the machine learning API and all the frontend files (HTML/CSS/JS), simplifying deployment.

---

## ⚙️ Tech Stack

* **Backend:**
    * **Python 3.9+**
    * **Flask:** For the web server and API endpoints.
    * **Gunicorn:** As the production-ready web server.
* **Machine Learning:**
    * **Scikit-learn:** For training and serving the ML models.
    * **Pandas:** For data cleaning and feature preparation.
    * **Joblib:** For saving and loading the trained model files (`.pkl`).
* **Frontend:**
    * **HTML5**
    * **CSS3** (with Flexbox)
    * **JavaScript (ES6+):** For DOM manipulation, API calls (`fetch`), and validation logic.
* **APIs:**
    * **Nominatim (OpenStreetMap):** For all geocoding and reverse geocoding.
* **Data:**
    * Model trained on historical earthquake data from the **National Center of Seismology (NCS)**, India.

---

## 🔁 Application Flow (How it Works)

1.  **User Visits:** The user navigates to the root URL.
2.  **Flask Serves Page:** The Flask server's `@app.route('/')` catches the request and serves the `index.html` file from the `templates` folder.
3.  **User Input:** The user either types a place name (e.g., "Virar") or clicks "Use My Current Location".
4.  **Frontend Geocoding (JS):**
    * **If Place Name:** The app calls the Nominatim API to get coordinates (e.g., `19.47° N, 72.81° E`).
    * **If Current Location:** The browser's `navigator.geolocation` API provides the coordinates.
5.  **Frontend Validation (JS):**
    * The script sends the coordinates to Nominatim's **reverse geocoding** endpoint.
    * It checks the response for `country_code: 'in'`.
    * If the code is not `'in'` (e.g., the user typed "London"), it shows an "Outside India" error and stops.
6.  **API Call (JS → Flask):**
    * If the location is valid, the frontend sends a `POST` request to its own server at the `/predict` endpoint, containing a JSON body: `{"lat": 19.47, "long": 72.81}`.
7.  **Backend Prediction (Python/Flask):**
    * The `@app.route('/predict')` endpoint receives the JSON.
    * It creates a Pandas DataFrame with the `lat`, `long`, and the pre-loaded `MEAN_DEPTH` (from the `model_config.json`).
    * It feeds this DataFrame into the loaded `risk_model` and `mag_model`.
    * It returns the predictions as a JSON response: `{"risk_level": "Medium", "predicted_magnitude": 5.1}`.
8.  **Display Results (JS):**
    * The frontend's `fetch` function receives the JSON response.
    * It hides the input card, shows the results card, and populates the fields with the predicted risk and magnitude.

---

## 🚀 Local Setup & Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Nikhil-Maurya01/earthquake-risk-predictor.git](https://github.com/Nikhil-Maurya01/earthquake-risk-predictor.git)
    cd earthquake-risk-predictor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Train the Models (First-time setup):**
    * Place your raw `ncs_data.csv` (or `.xlsx`) inside the `model/` folder.
    * Run the training script to generate the `.pkl` and `.json` files:
    ```bash
    pip install pandas scikit-learn
    python model/train_models.py 
    ```
    *(Note: You only need to do this once.)*

4.  **Install the web app dependencies:**
    (The `requirements.txt` file should be in the `backend/` folder)
    ```bash
    pip install -r backend/requirements.txt
    ```

5.  **Run the Flask application:**
    ```bash
    python backend/app.py
    ```

6.  **Open the app in your browser:**
    Navigate to `http://127.0.0.1:5000`

---
