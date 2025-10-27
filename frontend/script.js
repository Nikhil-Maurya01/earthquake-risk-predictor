document.addEventListener('DOMContentLoaded', () => {

    // --- Get Element References ---
    const inputCard = document.getElementById('input-card');
    const resultsCard = document.getElementById('results-card');

    const placeNameInput = document.getElementById('placeName');
    const submitNameBtn = document.getElementById('btn-submit-name');
    const getLocationBtn = document.getElementById('btn-get-location');
    const goBackBtn = document.getElementById('btn-go-back');
    
    const loadingEl = document.getElementById('loading');
    const resultsContentEl = document.getElementById('results-content');
    const errorMessageEl = document.getElementById('error-message');
    const riskEl = document.getElementById('result-risk');
    const magEl = document.getElementById('result-mag');

    // --- Core UI Functions ---
    function showInputCard() {
        resultsCard.classList.add('hidden');
        inputCard.classList.remove('hidden');
        clearResults(); 
    }

    function showResultsCard() {
        inputCard.classList.add('hidden');
        resultsCard.classList.remove('hidden');
    }

    function clearResults() {
        loadingEl.classList.add('hidden');
        resultsContentEl.classList.add('hidden');
        errorMessageEl.classList.add('hidden');
        riskEl.textContent = '---';
        magEl.textContent = '---';
        riskEl.style.color = '';
        riskEl.style.backgroundColor = '';
        riskEl.style.border = '';
    }

    function showError(message) {
        clearResults(); 
        errorMessageEl.textContent = message;
        errorMessageEl.classList.remove('hidden');
        showResultsCard(); 
    }

    // --- Geocoding & Validation ---

    // Step 1: Get coordinates for a place name
    async function geocodeAddress(address) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Geocoding service not available.');
            const data = await response.json();
            if (data && data.length > 0) {
                return { lat: parseFloat(data[0].lat), long: parseFloat(data[0].lon) };
            } else {
                return null;
            }
        } catch (error) {
            console.error("Geocoding error:", error);
            showError("Could not find location or geocoding service error.");
            return null;
        }
    }

    // Step 2: NEW function to check the country at given coordinates
    async function isLocationInIndia(lat, long) {
        // Use the 'reverse' endpoint. zoom=3 asks for country-level details.
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${long}&zoom=3`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Reverse geocoding service not available.');
            const data = await response.json();
            
            // Check if the address and country_code exist
            if (data && data.address && data.address.country_code) {
                return data.address.country_code === 'in'; // Returns true or false
            }
            return false; // Could not determine country
        } catch (error) {
            console.error("Reverse geocoding error:", error);
            showError("Could not verify location's country. Please try again.");
            return false; // Error, assume not India
        }
    }

    // --- API Call Function ---
    // This function is now async because it awaits the country check
    async function fetchPrediction(lat, long) {
        // 1. Show results card with loading spinner
        showResultsCard();
        clearResults(); 
        loadingEl.classList.remove('hidden');

        // 2. Await the new, robust country check
        const isIndia = await isLocationInIndia(lat, long);

        if (!isIndia) {
            showError("The detected location is outside India. Please provide an Indian location.");
            return; // Stop execution
        }

        // 3. Make API call (Only if isIndia is true)
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "lat": lat, "long": long })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            // 4. Success! Show results
            loadingEl.classList.add('hidden');
            
            riskEl.textContent = data.risk_level;
            magEl.textContent = data.predicted_magnitude;

            // Style the risk level
            if (data.risk_level === 'High') {
                riskEl.style.color = '#d93025'; // Red
                riskEl.style.backgroundColor = 'rgba(217, 48, 37, 0.2)';
                riskEl.style.border = '1px solid #d93025';
            } else if (data.risk_level === 'Medium') {
                riskEl.style.color = '#f29900'; // Orange
                riskEl.style.backgroundColor = 'rgba(242, 153, 0, 0.2)';
                riskEl.style.border = '1px solid #f29900';
            } else {
                riskEl.style.color = '#1a73e8'; // Blue
                riskEl.style.backgroundColor = 'rgba(26, 115, 232, 0.2)';
                riskEl.style.border = '1px solid #1a73e8';
            }
            
            resultsContentEl.classList.remove('hidden');
        })
        .catch(error => {
            // 5. Error
            console.error('Fetch Error:', error);
            showError('Error: Could not connect to the server. Is the backend running?');
        });
    }

    // --- Event Listeners ---
    
    // 1. Submit Place Name (must be async to await geocodeAddress)
    submitNameBtn.addEventListener('click', async () => {
        const placeName = placeNameInput.value.trim();
        if (!placeName) {
            alert("Please enter a place name.");
            return;
        }
        
        // Show loading spinner *while geocoding*
        showResultsCard();
        clearResults();
        loadingEl.classList.remove('hidden');

        // Get coords first
        const coords = await geocodeAddress(placeName);
        
        if (coords) {
            // Now let fetchPrediction handle the rest (including the country check)
            fetchPrediction(coords.lat, coords.long); // This is async but we don't need to await it
        } else {
            // Geocoding failed
            showError("Could not find coordinates for the entered place name.");
        }
    });

    // 2. Get Current Location
    getLocationBtn.addEventListener('click', () => {
        if (navigator.geolocation) {
            // Show loading spinner
            showResultsCard();
            clearResults();
            loadingEl.classList.remove('hidden');

            navigator.geolocation.getCurrentPosition((position) => {
                const lat = position.coords.latitude;
                const long = position.coords.longitude;
                // Fetch prediction, which will handle the country check
                fetchPrediction(lat, long);
            }, (error) => {
                showError(`Error getting location: ${error.message}`);
            }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
        } else {
            showError("Geolocation is not supported by this browser.");
        }
    });

    // 3. Go Back
    goBackBtn.addEventListener('click', () => {
        showInputCard();
    });


});
