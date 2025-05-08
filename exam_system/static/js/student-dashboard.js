// Profile Functions
function loadProfileData() {
    console.log('Loading profile data...'); // Debug log
    return fetch('/api/student/profile', {  // Changed URL to match backend
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received profile data:', data); // Debug log
        if (data.success) {
            // Set form values
            const fullName = `${data.data.first_name || ''} ${data.data.last_name || ''}`.trim();
            $('#fullName').val(fullName);
            $('#email').val(data.data.email || '');
            $('#phoneNumber').val(data.data.phone_number || '');
            $('#department').val(data.data.department || '');
            $('#semester').val(data.data.semester || '');
            $('#studentId').val(data.data.username || '');
            
            // Return data for change tracking
            return {
                fullName: fullName,
                phoneNumber: data.data.phone_number || '',
                department: data.data.department || '',
                semester: data.data.semester || ''
            };
        }
        throw new Error(data.message || 'Failed to load profile data');
    });
}

function updateProfile(formData) {
    // Split full name into first and last name
    const nameParts = formData.fullName.trim().split(/\s+/);
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';

    const data = {
        first_name: firstName,
        last_name: lastName,
        phone_number: formData.phoneNumber || '',
        department: formData.department || '',
        semester: formData.semester || ''
    };

    console.log('Sending update data:', data); // Debug log

    return fetch('/api/student/profile', {  // Changed URL to match backend
        method: 'PUT',  // Changed to PUT
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Update response status:', response.status); // Debug log
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Update response data:', data); // Debug log
        if (data.success) {
            // Update form with returned data
            const fullName = `${data.data.first_name || ''} ${data.data.last_name || ''}`.trim();
            $('#fullName').val(fullName);
            $('#phoneNumber').val(data.data.phone_number || '');
            $('#department').val(data.data.department || '');
            $('#semester').val(data.data.semester || '');
            return data;
        }
        throw new Error(data.message || 'Failed to update profile');
    });
}

function loadProfileForm() {
    $("#dynamicContentContainer").hide().html(`
        <div class="profile-container">
            <h2>Update Your Profile</h2>
            <form id="studentProfileForm" class="profile-form">
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-user"></i>
                        <input type="text" id="fullName" name="fullName" placeholder="Full Name" required>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-envelope"></i>
                        <input type="email" id="email" name="email" placeholder="Email Address" required readonly>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-phone"></i>
                        <input type="tel" id="phoneNumber" name="phoneNumber" placeholder="Phone Number" pattern="[0-9]{10}" title="Please enter a valid 10-digit phone number" required>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-building"></i>
                        <input type="text" id="department" name="department" placeholder="Department" readonly>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-clock"></i>
                        <select id="semester" name="semester" required>
                            <option value="">Select Semester</option>
                            <option value="1">1st Semester</option>
                            <option value="2">2nd Semester</option>
                            <option value="3">3rd Semester</option>
                            <option value="4">4th Semester</option>
                            <option value="5">5th Semester</option>
                            <option value="6">6th Semester</option>
                            <option value="7">7th Semester</option>
                            <option value="8">8th Semester</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-with-icon">
                        <i class="fas fa-id-card"></i>
                        <input type="text" id="studentId" name="studentId" placeholder="Student ID" readonly>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn reset-btn" id="resetForm" style="display: none;">Reset Changes</button>
                    <button type="submit" class="btn submit-btn" id="saveChanges" disabled>
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                </div>
            </form>
            <div id="profileUpdateMessage" class="message-container"></div>
        </div>
    `).slideDown(300);

    let originalData = {};
    let retryCount = 0;
    const MAX_RETRIES = 3;

    // Load initial profile data
    loadProfileData()
        .then(data => {
            console.log('Loaded initial data:', data); // Debug log
            originalData = data;
            $('#profileUpdateMessage').empty();
            retryCount = 0;
        })
        .catch(error => {
            console.error('Error loading profile:', error);
            const errorMessage = error.message.includes('502') 
                ? 'Server is temporarily unavailable. Please try again in a moment.'
                : 'Failed to load profile data. Please refresh the page.';
            $('#profileUpdateMessage').html(`<div class="error">${errorMessage}</div>`);
            
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                setTimeout(() => loadProfileData(), 2000 * retryCount);
            }
        });

    // Form change handlers
    function checkFormChanges() {
        const currentData = {
            fullName: $('#fullName').val(),
            phoneNumber: $('#phoneNumber').val(),
            department: $('#department').val(),
            semester: $('#semester').val()
        };

        const hasChanges = Object.keys(originalData).some(key => originalData[key] !== currentData[key]);
        $('#saveChanges').prop('disabled', !hasChanges);
        $('#resetForm').toggle(hasChanges);
    }

    $('#studentProfileForm input, #studentProfileForm select').on('input change', checkFormChanges);

    $('#resetForm').click(function() {
        $('#fullName').val(originalData.fullName);
        $('#phoneNumber').val(originalData.phoneNumber);
        $('#department').val(originalData.department);
        $('#semester').val(originalData.semester);
        checkFormChanges();
        $('#profileUpdateMessage').empty();
    });

    $('#studentProfileForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            fullName: $('#fullName').val(),
            phoneNumber: $('#phoneNumber').val(),
            department: $('#department').val(),
            semester: $('#semester').val()
        };

        console.log('Submitting form data:', formData); // Debug log

        $('#saveChanges').prop('disabled', true);
        $('#profileUpdateMessage').html('<div class="info">Updating profile...</div>');

        updateProfile(formData)
            .then(data => {
                console.log('Profile update successful:', data); // Debug log
                $('#profileUpdateMessage').html('<div class="success">Profile updated successfully!</div>');
                originalData = {
                    fullName: data.data.first_name + ' ' + data.data.last_name,
                    phoneNumber: data.data.phone_number || '',
                    department: data.data.department || '',
                    semester: data.data.semester || ''
                };
                checkFormChanges();
                retryCount = 0;
            })
            .catch(error => {
                console.error('Error updating profile:', error);
                const errorMessage = error.message.includes('502')
                    ? 'Server is temporarily unavailable. Your changes will be saved when connection is restored.'
                    : 'Failed to update profile. Please try again.';
                
                $('#profileUpdateMessage').html(`<div class="error">${errorMessage}</div>`);
                $('#saveChanges').prop('disabled', false);

                if (error.message.includes('502') && retryCount < MAX_RETRIES) {
                    retryCount++;
                    setTimeout(() => updateProfile(formData), 2000 * retryCount);
                }
            });
    });
} 