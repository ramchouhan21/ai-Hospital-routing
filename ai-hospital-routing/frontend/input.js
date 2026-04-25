document.addEventListener('DOMContentLoaded', () => {
    
    const form = document.getElementById('routing-form');
    const voiceBtn = document.getElementById('voice-btn');
    const voiceStatus = document.getElementById('voice-status');
    const symptomsInput = document.getElementById('symptoms');
    const gpsBtn = document.getElementById('gps-btn');
    const locationInput = document.getElementById('location');
    const ageInput = document.getElementById('age');
    const genderInput = document.getElementById('gender');
    
    const resultsSection = document.getElementById('results-section');
    const loadingState = document.getElementById('loading-state');
    const hospitalList = document.getElementById('hospital-list');
    const severityBadge = document.getElementById('severity-badge');
    const reportSection = document.getElementById('report-section');
    const backToResultsBtn = document.getElementById('back-to-results');
    const reportContent = document.getElementById('report-content');
    const startNavigationBtn = document.getElementById('start-navigation-btn');
    const downloadReportBtn = document.getElementById('download-report-btn');

    // Default Fallback coordinates (Bangalore) if GPS fails
    let currentLat = 12.9716;
    let currentLng = 77.5946;

    // --- 1. Voice Recognition ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isRecording = false;

        voiceBtn.addEventListener('click', () => {
            if (!isRecording) {
                try {
                    recognition.start();
                    isRecording = true;
                    voiceBtn.classList.add('recording');
                    voiceStatus.textContent = "Listening... Speak now";
                    voiceStatus.style.color = "var(--clr-red)";
                } catch(e) {
                    console.error(e);
                }
            } else {
                recognition.stop();
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (symptomsInput.value) {
                symptomsInput.value += ' ' + transcript;
            } else {
                symptomsInput.value = transcript;
            }
        };

        recognition.onspeechend = () => {
            recognition.stop();
        };

        recognition.onend = () => {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceStatus.textContent = "Tap microphone to speak";
            voiceStatus.style.color = "var(--clr-text-muted)";
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error detected: ' + event.error);
            isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceStatus.textContent = "Error: " + event.error;
            setTimeout(() => {
                voiceStatus.textContent = "Tap microphone to speak";
                voiceStatus.style.color = "var(--clr-text-muted)";
            }, 3000);
        };
    } else {
        voiceBtn.style.display = 'none';
        voiceStatus.textContent = "Voice input not supported in this browser.";
    }


    // --- 2. GPS Location ---
    gpsBtn.addEventListener('click', () => {
        const originalText = gpsBtn.innerHTML;
        gpsBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Locating...';
        gpsBtn.disabled = true;

        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    currentLat = position.coords.latitude;
                    currentLng = position.coords.longitude;
                    locationInput.value = `📍 Coordinates: ${currentLat.toFixed(4)}, ${currentLng.toFixed(4)}`;
                    
                    gpsBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Detected';
                    gpsBtn.classList.replace('btn-secondary', 'btn-primary');
                    
                    setTimeout(() => {
                        gpsBtn.innerHTML = originalText;
                        gpsBtn.classList.replace('btn-primary', 'btn-secondary');
                        gpsBtn.disabled = false;
                    }, 2000);
                },
                (error) => {
                    // Fallback to simulated location for testing without HTTPS
                    console.warn("Geolocation blocked/failed. Using fallback location (Bangalore Central).");
                    currentLat = 12.9716;
                    currentLng = 77.5946;
                    locationInput.value = `M.G. Road, Bangalore (Simulated Location)`;
                    
                    gpsBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Simulated';
                    gpsBtn.classList.replace('btn-secondary', 'btn-primary');
                    
                    setTimeout(() => {
                        gpsBtn.innerHTML = originalText;
                        gpsBtn.classList.replace('btn-primary', 'btn-secondary');
                        gpsBtn.disabled = false;
                    }, 2000);
                },
                { timeout: 5000 }
            );
        } else {
            alert("Geolocation is not supported. Type it manually.");
            gpsBtn.innerHTML = originalText;
            gpsBtn.disabled = false;
        }
    });


    // --- 3. Form Submission (Live Backend API) ---
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if(!symptomsInput.value || !locationInput.value) {
                alert("Please fill in your symptoms and location.");
                return;
            }

            resultsSection.style.display = 'block';
            reportSection.style.display = 'none';
            loadingState.style.display = 'block';
            hospitalList.innerHTML = '';
            severityBadge.innerHTML = '';
            severityBadge.className = 'severity-badge';
            
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

            const payload = {
                age: parseInt(ageInput.value) || 30,
                gender: genderInput.value || "unknown",
                symptoms: symptomsInput.value,
                latitude: currentLat,
                longitude: currentLng
            };

            try {
                // Call FastAPI backend
                const response = await fetch("http://127.0.0.1:8050/api/v1/predict", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error("Server error - is the backend running?");
                }

                const json = await response.json();
                renderResults(json.data);

            } catch (error) {
                console.error(error);
                loadingState.style.display = 'none';
                hospitalList.innerHTML = `
                    <div style="color: var(--clr-red); padding: 20px; text-align: center; border: 1px solid var(--clr-red); border-radius: 8px;">
                        <h4><i class="bi bi-exclamation-octagon-fill"></i> Connection Failed</h4>
                        <p>Could not connect to the AI Backend API.</p>
                        <p style="font-size: 0.9em; margin-top: 10px;">Please ensure your Python FastAPI server is running on port 8050:<br><code>python -m uvicorn backend.main:app --reload --port 8050</code></p>
                    </div>`;
            }
        });
    }

    // Render Live API Results
    function renderResults(data) {
        loadingState.style.display = 'none';

        const severity = data.severity; // "High", "Medium", "Low"
        
        let severityClass = "severity-mild";
        let urgencyText = "Standard care recommended based on symptoms.";

        if (severity === "High") {
            severityClass = "severity-critical";
            urgencyText = "🚨 CRITICAL CONDITION: Immediate attention required! Routing past traffic to nearest ICU-equipped facility.";
        } else if (severity === "Medium") {
            severityClass = "severity-moderate";
            urgencyText = "Needs timely medical evaluation.";
        }

        // Render Badge
        severityBadge.className = `severity-badge ${severityClass}`;
        severityBadge.innerHTML = `Severity Level: ${severity}`;

        let htmlContent = '';
        
        if (!data.recommendations || data.recommendations.length === 0) {
            hospitalList.innerHTML = `<p style="color:var(--clr-red)">No hospitals available meeting your criteria (ICU/Beds).</p>`;
            return;
        }

        data.recommendations.forEach((hospital, index) => {
            const isTopMatch = index === 0;
            
            // Traffic color indicator
            let trafficColor = "green";
            if(hospital.traffic_level === "Medium") trafficColor = "orange";
            if(hospital.traffic_level === "High") trafficColor = "red";

            htmlContent += `
                <div class="hospital-card ${isTopMatch ? 'recommended' : ''}">
                    ${isTopMatch ? '<div style="color: var(--clr-deep-blue); font-size: 0.8rem; font-weight: 700; margin-bottom: 8px;"><i class="bi bi-star-fill"></i> TOP MATCH</div>' : ''}
                    <div class="hospital-card-header">
                        <div class="hospital-name">${hospital.name}</div>
                        <div class="hospital-dist" style="color: ${trafficColor};">
                            <i class="bi bi-car-front-fill"></i> ${hospital.estimated_time_mins} mins (${hospital.distance_km} km)
                        </div>
                    </div>
                    
                    <div class="hospital-stats" style="margin-bottom: 8px;">
                        <div class="hospital-stat-item" style="color: var(--clr-text-main); font-weight: 600;">
                            <i class="bi bi-hospital"></i> Gen Beds: ${hospital.available_beds}
                        </div>
                        <div class="hospital-stat-item" style="color: ${hospital.available_icu_beds > 0 ? 'var(--clr-red)' : 'var(--clr-text-muted)'}; font-weight: ${hospital.available_icu_beds > 0 ? '700' : 'normal'};">
                            <i class="bi bi-heart-pulse-fill"></i> ICU Beds: ${hospital.available_icu_beds}
                        </div>
                    </div>

                    <div class="hospital-stats" style="margin-top: 0;">
                        <div class="hospital-stat-item" style="font-size: 0.85rem;"><i class="bi bi-shield-plus"></i> ${hospital.specialties}</div>
                    </div>

                    <button type="button" class="btn btn-outline view-report-btn" data-lat="${hospital.latitude}" data-lng="${hospital.longitude}" data-name="${hospital.name}" data-icu="${hospital.available_icu_beds}" data-beds="${hospital.available_beds}" data-dist="${hospital.distance_km}">
                        <i class="bi bi-file-earmark-medical"></i> View Report
                    </button>
                </div>
            `;
        });

        hospitalList.innerHTML = `
            <p style="margin-bottom: 20px; color: var(--clr-text-muted); font-weight: 500;">${urgencyText}</p>
            ${htmlContent}
        `;
        
        // Add event listeners to the view report buttons
        document.querySelectorAll('.view-report-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const dataset = e.currentTarget.dataset;
                const symptoms = symptomsInput.value;
                
                // Show loading on button
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
                btn.disabled = true;

                try {
                    const res = await fetch("http://127.0.0.1:8050/api/v1/generate_report", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({
                            symptoms: symptoms,
                            severity: severity,
                            hospital_name: dataset.name,
                            icu_available: parseInt(dataset.icu) || 0,
                            beds_available: parseInt(dataset.beds) || 0,
                            distance_km: parseFloat(dataset.dist) || 0
                        })
                    });
                    
                    const data = await res.json();
                    
                    if(data.status === "success") {
                        // Switch slides
                        resultsSection.style.display = 'none';
                        reportSection.style.display = 'block';
                        
                        // Set report content
                        reportContent.textContent = data.report;
                        
                        // Setup Navigation Button
                        startNavigationBtn.onclick = () => {
                            window.open(`https://maps.google.com/?q=${dataset.lat},${dataset.lng}`, '_blank');
                        };
                        
                        // Setup Download Button
                        downloadReportBtn.onclick = () => {
                            const blob = new Blob([data.report], { type: 'text/plain' });
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `Patient_Report_${dataset.name.replace(/\s+/g, '_')}.txt`;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                        };
                    } else {
                        alert("Failed to generate report.");
                    }
                } catch(err) {
                    console.error("Report generation failed:", err);
                    alert("Error generating report. Check console.");
                } finally {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                }
            });
        });
        
        // Back button logic
        if(backToResultsBtn) {
            backToResultsBtn.onclick = () => {
                reportSection.style.display = 'none';
                resultsSection.style.display = 'block';
            };
        }
    }
});
