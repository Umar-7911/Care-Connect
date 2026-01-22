// Compare page functionality
document.addEventListener('DOMContentLoaded', function () {
    const selectButton = document.getElementById('selectHospitalBtn');

    if (selectButton) {
        selectButton.addEventListener('click', function () {
            const selectedRadio = document.querySelector('input[name="selectedHospital"]:checked');

            if (!selectedRadio) {
                alert('Please select ONE hospital to continue');
                return;
            }

            const hospitalId = selectedRadio.value;

            // Redirect to ambulance booking page with hospital ID
            window.location.href = `/user/ambulances/?hospital_id=${hospitalId}`;
        });
    }
});
