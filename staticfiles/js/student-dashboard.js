$(document).ready(function() {
    // Add logout handler
    $("#logoutBtn").click(function() {
        localStorage.removeItem('token');
        localStorage.removeItem('userType');
        window.location.href = '/login.html';
    });

    // When any dashboard option is clicked
    $(".option-card").click(function() {
        $(".option-card").removeClass("active");
        $("#dynamicContentContainer").empty();
        $(this).addClass("active");
        
        var optionId = $(this).attr("id");
        
        if (optionId === "takeExamOption") {
            loadExamList();
        } else if (optionId === "viewResultsOption") {
            loadResultsList();
        } else if (optionId === "updateProfileOption") {
            loadProfileForm();
        }
    });

    // Function to load exam list
    function loadExamList() {
        var examListHTML = `
            <div class="exam-list-container">
                <div class="exam-list-header">
                    <h2>Available Exams</h2>
                    <div class="exam-filters">
                        <select id="subjectFilter">
                            <option value="">All Subjects</option>
                        </select>
                    </div>
                </div>
                <div class="exam-list-scrollable">
                    <div class="loading">Loading available exams...</div>
                </div>
            </div>
        `;
        
        $("#dynamicContentContainer").hide().html(examListHTML).slideDown(300);
        
        // Fetch real exams from the database
        fetch('/api/student/exams', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch exams');
            }
            return response.json();
        })
        .then(exams => {
            // Update subject filter options based on available exams
            const subjects = [...new Set(exams.map(exam => exam.subject))];
            const subjectFilter = $('#subjectFilter');
            subjectFilter.empty();
            subjectFilter.append('<option value="">All Subjects</option>');
            subjects.forEach(subject => {
                subjectFilter.append(`<option value="${subject.toLowerCase()}">${subject}</option>`);
            });
            
            displayExams(exams);
        })
        .catch(error => {
            console.error('Error loading exams:', error);
            $(".exam-list-scrollable").html('<div class="error">Failed to load exams. Please try again later.</div>');
        });
    }

    function displayExams(exams) {
        var examListHTML = '';
        
        if (exams.length === 0) {
            examListHTML = '<div class="no-exams">No exams available at this time.</div>';
        } else {
            $.each(exams, function(i, exam) {
                examListHTML += `
                    <div class="exam-tile" data-exam-id="${exam.id}">
                        <h3>${exam.title}</h3>
                        <div class="exam-details">
                            <span class="subject">${exam.subject}</span>
                            <span class="duration"><i class="fa fa-clock"></i> ${exam.duration} minutes</span>
                        </div>
                        <div class="exam-meta">
                            <span class="questions"><i class="fa fa-tasks"></i> ${exam.totalQuestions} questions</span>
                            <span class="deadline"><i class="fa fa-calendar"></i> Due: ${formatDate(exam.deadline)}</span>
                        </div>
                        <button class="start-exam-btn">Start Exam</button>
                    </div>
                `;
            });
        }
        
        $(".exam-list-scrollable").html(examListHTML);
        
        $(".start-exam-btn").click(function(e) {
            e.stopPropagation();
            var examId = $(this).closest(".exam-tile").data("exam-id");
            console.log("Starting exam #" + examId);
        });
        
        $("#subjectFilter").change(function() {
            var selected = $(this).val();
            if (selected === "") {
                $(".exam-tile").show();
            } else {
                $(".exam-tile").hide();
                $(".exam-tile").each(function() {
                    if ($(this).find(".subject").text().toLowerCase().includes(selected)) {
                        $(this).show();
                    }
                });
            }
        });
    }

    function loadResultsList() {
        $("#dynamicContentContainer").hide().html(
            `<div class="results-container">
                <h2>Your Exam Results</h2>
                <p>Past exam results will appear here.</p>
            </div>`
        ).slideDown(300);
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
                            <select id="department" name="department" required>
                                <option value="">Select Department</option>
                                <option value="CS">Computer Science</option>
                                <option value="IT">Information Technology</option>
                                <option value="CE">Computer Engineering</option>
                                <option value="EE">Electrical Engineering</option>
                                <option value="ME">Mechanical Engineering</option>
                            </select>
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
                        <button type="submit" class="btn primary-btn" id="saveChanges" disabled>Save Changes</button>
                    </div>
                </form>
                <div id="profileUpdateMessage" class="message-container"></div>
            </div>
        `).slideDown(300);

        let originalData = {};
        let retryCount = 0;
        const MAX_RETRIES = 3;

        function loadProfileData() {
            fetch('/api/student/profile', {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                $('#fullName').val(data.fullName);
                $('#email').val(data.email);
                $('#phoneNumber').val(data.phoneNumber);
                $('#department').val(data.department);
                $('#semester').val(data.semester);
                $('#studentId').val(data.studentId);
                
                originalData = {
                    fullName: data.fullName,
                    phoneNumber: data.phoneNumber,
                    department: data.department,
                    semester: data.semester
                };

                $('#profileUpdateMessage').empty();
                retryCount = 0;
            })
            .catch(error => {
                console.error('Error loading profile:', error);
                const errorMessage = error.response?.status === 502 
                    ? 'Server is temporarily unavailable. Please try again in a moment.'
                    : 'Failed to load profile data. Please refresh the page.';
                $('#profileUpdateMessage').html(`<div class="error">${errorMessage}</div>`);
                
                if (retryCount < MAX_RETRIES) {
                    retryCount++;
                    setTimeout(loadProfileData, 2000 * retryCount); // Exponential backoff
                }
            });
        }

        function updateProfile(formData) {
            $('#saveChanges').prop('disabled', true);
            $('#profileUpdateMessage').html('<div class="info">Updating profile...</div>');

            fetch('/api/student/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 502) {
                        throw new Error('SERVER_ERROR');
                    }
                    throw new Error('UPDATE_FAILED');
                }
                return response.json();
            })
            .then(data => {
                $('#profileUpdateMessage').html('<div class="success">Profile updated successfully!</div>');
                originalData = { ...formData };
                checkFormChanges();
                retryCount = 0;
            })
            .catch(error => {
                console.error('Error updating profile:', error);
                const errorMessage = error.message === 'SERVER_ERROR'
                    ? 'Server is temporarily unavailable. Your changes will be saved when connection is restored.'
                    : 'Failed to update profile. Please try again.';
                
                $('#profileUpdateMessage').html(`<div class="error">${errorMessage}</div>`);
                $('#saveChanges').prop('disabled', false);

                if (error.message === 'SERVER_ERROR' && retryCount < MAX_RETRIES) {
                    retryCount++;
                    setTimeout(() => updateProfile(formData), 2000 * retryCount);
                }
            });
        }

        // Initial profile data load
        loadProfileData();

        // Add form change handlers
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
                semester: parseInt($('#semester').val())
            };

            updateProfile(formData);
        });
    }

    function formatDate(dateString) {
        var date = new Date(dateString);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
});