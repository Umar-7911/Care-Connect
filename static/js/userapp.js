// CareConnect User App JavaScript

// Checkbox toggle functionality
function toggleCheckbox(label) {
    const checkbox = label.querySelector('input[type="checkbox"]');
    if (checkbox.checked) {
        label.classList.add('checked');
    } else {
        label.classList.remove('checked');
    }
}

// View toggle (list/map)
let currentView = 'list';

function toggleView(view) {
    currentView = view;
    const hospitalGrid = document.getElementById('hospitalGrid');
    const mapSection = document.getElementById('mapSection');
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    if (view === 'map') {
        hospitalGrid.style.display = 'none';
        mapSection.classList.add('show');
        toggleBtns.forEach(btn => {
            if (btn.textContent.includes('Map')) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    } else {
        hospitalGrid.style.display = 'grid';
        mapSection.classList.remove('show');
        toggleBtns.forEach(btn => {
            if (btn.textContent.includes('List')) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
}

// Hospital selection for comparison
let selectedHospitals = [];

function toggleSelectHospital(hospitalId, hospitalName) {
    const card = document.getElementById(`hospital-${hospitalId}`);
    if (!card) {
        console.error('Hospital card not found:', hospitalId);
        return;
    }
    
    // Try to find select button by class or ID
    let selectBtn = card.querySelector('.select-btn') || card.querySelector('#select-btn-' + hospitalId);
    if (!selectBtn) {
        // Fallback: find any button in hospital-actions
        const actionsDiv = card.querySelector('.hospital-actions');
        if (actionsDiv) {
            selectBtn = actionsDiv.querySelector('.action-btn.select') || actionsDiv.querySelector('button');
        }
    }
    
    if (!selectBtn) {
        console.error('Select button not found for hospital:', hospitalId);
        return;
    }

    const index = selectedHospitals.findIndex(h => h.id === hospitalId);

    if (index > -1) {
        // Deselect
        selectedHospitals.splice(index, 1);
        card.classList.remove('selected');
        // Update button text while preserving SVG icon
        const textSpan = selectBtn.querySelector('span#select-text-' + hospitalId) || selectBtn.querySelector('span');
        if (textSpan) {
            textSpan.textContent = 'Select';
        } else {
            // Fallback: update innerHTML
            selectBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg><span id="select-text-' + hospitalId + '">Select</span>';
        }
        selectBtn.classList.remove('selected');
    } else {
        // Select (limit to 4)
        if (selectedHospitals.length >= 4) {
            alert('You can compare up to 4 hospitals at a time');
            return;
        }
        selectedHospitals.push({ id: hospitalId, name: hospitalName });
        card.classList.add('selected');
        // Update button text while preserving SVG icon
        const textSpan = selectBtn.querySelector('span#select-text-' + hospitalId) || selectBtn.querySelector('span');
        if (textSpan) {
            textSpan.textContent = 'Selected';
        } else {
            // Fallback: update innerHTML
            selectBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg><span id="select-text-' + hospitalId + '">Selected</span>';
        }
        selectBtn.classList.add('selected');
    }

    updateCompareSection();
}

// Update compare section
function updateCompareSection() {
    const compareSection = document.getElementById('compareSection');
    const compareCount = document.getElementById('compareCount');
    const compareBtn = document.getElementById('compareBtn');

    if (!compareSection || !compareCount || !compareBtn) return;

    compareCount.textContent = selectedHospitals.length;

    if (selectedHospitals.length === 1) {
        // If only 1 hospital selected, show option to go to ambulance booking
        compareSection.classList.add('show');
        compareBtn.textContent = 'Book Ambulance →';
        compareBtn.disabled = false;
    } else if (selectedHospitals.length >= 2) {
        compareSection.classList.add('show');
        compareBtn.textContent = 'Compare Hospitals →';
        compareBtn.disabled = false;
    } else {
        if (selectedHospitals.length === 0) {
            compareSection.classList.remove('show');
        }
        compareBtn.disabled = true;
    }
}

// Navigate to comparison page or ambulance booking
function goToComparison() {
    if (!selectedHospitals || selectedHospitals.length === 0) {
        alert('Please select at least 1 hospital');
        return;
    }

    if (selectedHospitals.length === 1) {
        // If only 1 hospital selected, go directly to ambulance booking
        const hospitalId = selectedHospitals[0].id;
        window.location.href = `/user/ambulances/?hospital_id=${hospitalId}`;
    } else if (selectedHospitals.length >= 2) {
        // If 2-4 hospitals selected, go to compare page
        // Build URL with hospital IDs
        const ids = selectedHospitals.map(h => h.id).join(',');
        window.location.href = `/user/compare/?ids=${ids}`;
    }
}

// View hospital on map
function viewOnMap(hospitalId) {
    // Switch to map view
    toggleView('map');

    // Scroll to map section
    const mapSection = document.getElementById('mapSection');
    if (mapSection) {
        mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // In a real implementation, this would center the map on the hospital
    console.log(`Viewing hospital ${hospitalId} on map`);
}

// Scroll to search
function scrollToSearch() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Initialize checkbox states on page load
document.addEventListener('DOMContentLoaded', function () {
    // Set up checkbox listeners
    const checkboxItems = document.querySelectorAll('.checkbox-item');
    checkboxItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    item.classList.add('checked');
                } else {
                    item.classList.remove('checked');
                }
            });
        }
    });

    // Live availability polling (results page)
    // Updates visible hospital cards without a full page refresh.
    try {
        const hospitalCards = Array.from(document.querySelectorAll('[data-hospital-id]'));
        const hospitalIds = hospitalCards.map(el => el.getAttribute('data-hospital-id')).filter(Boolean);
        if (hospitalIds.length > 0) {
            startLiveAvailabilityPolling(hospitalIds);
        }
    } catch (e) {
        console.warn('Live availability polling init failed:', e);
    }
});

function startLiveAvailabilityPolling(hospitalIds) {
    const endpoint = `/user/live-availability/?ids=${encodeURIComponent(hospitalIds.join(','))}`;

    async function tick() {
        try {
            const res = await fetch(endpoint, { headers: { 'Accept': 'application/json' } });
            if (!res.ok) return;
            const data = await res.json();
            if (!data || !Array.isArray(data.hospitals)) return;
            data.hospitals.forEach(updateHospitalCardAvailability);
        } catch (e) {
            // swallow errors; next tick will retry
        }
    }

    // Initial fetch + then poll
    tick();
    setInterval(tick, 5000);
}

function updateHospitalCardAvailability(hospital) {
    const card = document.querySelector(`[data-hospital-id="${hospital.id}"]`);
    if (!card || !hospital.beds) return;

    const mapLabel = (status) => {
        switch (status) {
            case 'good': return 'Good';
            case 'limited': return 'Limited';
            case 'very_limited': return 'Very Limited';
            case 'full': return 'Full';
            default: return '';
        }
    };

    ['icu', 'oxygen', 'ventilator', 'isolation'].forEach((type) => {
        const bed = hospital.beds[type];
        if (!bed) return;

        const item = card.querySelector(`[data-bed-type="${type}"]`);
        if (!item) return;
        const statusEl = item.querySelector('[data-availability-status]');
        const countEl = item.querySelector('[data-availability-count]');

        // Update classes for background + text
        item.classList.remove('good', 'limited', 'very_limited', 'full', 'none');
        item.classList.add(bed.status);

        if (statusEl) {
            statusEl.classList.remove('good', 'limited', 'very_limited', 'full', 'none');
            statusEl.classList.add(bed.status);
            const label = mapLabel(bed.status);
            statusEl.childNodes.forEach(() => {}); // no-op; keep structure stable
            // Preserve existing label + count layout
            if (countEl) {
                statusEl.firstChild && (statusEl.firstChild.textContent = `${label} `);
            } else {
                statusEl.textContent = `${label} ${bed.available}/${bed.total}`;
            }
        }

        if (countEl) {
            countEl.textContent = `${bed.available}/${bed.total}`;
        }
    });
}
