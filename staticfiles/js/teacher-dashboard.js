function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    // Constants
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;
    
    // State management
    let originalProfileData = {};
    let retryCount = 0;
    
    // Initialize dashboard
    // initDashboard();

    // function initDashboard() {
    //     setupEventHandlers();
    // }  // AI DRUNK

        // Logout handler
    $("#logoutBtn").click(function() {
        localStorage.removeItem('token');
        localStorage.removeItem('userType');
        window.location.href = '/login.html';
    });
    
    // Option card handlers
    $(".option-card").click(function() {
        $(".option-card").removeClass("active");
        $(this).addClass("active");
        
        const optionId = $(this).attr("id");
        loadContent(optionId);
    });

    function loadContent(optionId) {
        $("#dynamicContentContainer").empty().hide();
        
        switch(optionId) {
            case "createExamOption":
                loadCreateExamForm();
                break;
            case "manageExamOption":
                loadManageExams();
                break;
            case "viewResultsOption":
                loadStudentResults();
                break;
            case "generateReportsOption":
                loadReportGenerator();
                break;
            case "updateProfileOption":
                loadProfileForm();
                break;
            default:
                showWelcomeMessage();
        }
    }

    function showWelcomeMessage() {
        // Get the full name from localStorage or use username as fallback
        const fullName = localStorage.getItem('fullName');
        const displayName = fullName ? fullName : localStorage.getItem('username');
        
        $("#dynamicContentContainer").html(`
            <div class="welcome-message">
                <h2>Welcome, ${displayName}</h2>
                <p>Select an option from the menu above to get started.</p>
            </div>
        `).slideDown(300);
    }

    function loadCreateExamForm() {
        // Show loading state
        $("#dynamicContentContainer").html('<div class="loading">Loading form...</div>').slideDown(300);
        
        // Fetch subjects from API
        $.ajax({
            url: '/api/subjects/',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            success: function(response) {
                if (response.success) {
                    const subjects = response.data;
                    let subjectOptions = '<option value="">Select Subject</option>';
                    subjects.forEach(subject => {
                        subjectOptions += `<option value="${subject.id}">${subject.name}</option>`;
                    });

                    const formHTML = `
                        <div class="create-exam-container">
                            <h2>Create New Exam</h2>
                            <form id="createExamForm" class="exam-form">
                                <div class="form-row">
                                    <div class="form-group">
                                        <div class="input-with-icon">
                                            <i class="fas fa-heading"></i>
                                            <input type="text" id="examTitle" placeholder="Exam Title" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <div class="input-with-icon">
                                            <i class="fas fa-book"></i>
                                            <select id="subject" required>
                                                ${subjectOptions}
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <div class="input-with-icon">
                                            <i class="fas fa-clock"></i>
                                            <input type="number" id="duration" min="15" placeholder="Duration (minutes)" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-row">
                                    <div class="form-group">
                                        <div class="input-with-icon">
                                            <i class="fas fa-calendar-alt"></i>
                                            <input type="datetime-local" id="deadline" required>
                                        </div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <div class="input-with-icon">
                                            <i class="fas fa-question-circle"></i>
                                            <input type="number" id="totalQuestions" min="1" placeholder="Total Questions" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="form-actions">
                                    <button type="submit" class="btn primary-btn">
                                        <i class="fas fa-plus-circle"></i> Create Exam & Add Questions
                                    </button>
                                </div>
                            </form>
                        </div>
                    `;
                    
                    $("#dynamicContentContainer").html(formHTML);
                    
                    // Set default deadline to tomorrow at 9 AM
                    const tomorrow = new Date();
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    tomorrow.setHours(9, 0, 0, 0);
                    const formattedDate = tomorrow.toISOString().slice(0, 16);
                    $("#deadline").val(formattedDate);
                    
                    // Form submission handler
                    $("#createExamForm").submit(function(e) {
                        e.preventDefault();
                        createExam();
                    });
                } else {
                    showToast('Failed to load subjects: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showToast('Error loading subjects: ' + error, 'error');
            }
        });
    }

    function createExam() {
        // Get form values
        const examData = {
            title: $("#examTitle").val(),
            subject: $("#subject").val(),
            duration: $("#duration").val(),
            deadline: $("#deadline").val(),
            totalQuestions: $("#totalQuestions").val(),
            status: "draft"
        };
        
        // Validate inputs
        if (!examData.title || !examData.subject || !examData.duration || !examData.deadline || !examData.totalQuestions) {
            showMessage("Please fill in all fields", "error");
            return;
        }
        
        // Show loading state
        $(".primary-btn").html('<i class="fas fa-spinner fa-spin"></i> Creating...').prop('disabled', true);
        
        // Make API call to create exam
        $.ajax({
            url: '/api/exams/create/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: JSON.stringify(examData),
            success: function(response) {
                if (response.success) {
                    showToast('Exam created successfully!', 'success');
                    // After successful creation, redirect to question editor
                    window.location.href = `/exams/manage/${response.data.exam_id}/`;
                } else {
                    showToast(response.message || 'Failed to create exam', 'error');
                    $(".primary-btn").html('<i class="fas fa-plus-circle"></i> Create Exam & Add Questions').prop('disabled', false);
                }
            },
            error: function(xhr, status, error) {
                showToast(error || 'Error creating exam', 'error');
                $(".primary-btn").html('<i class="fas fa-plus-circle"></i> Create Exam & Add Questions').prop('disabled', false);
            }
        });
    }

    function showMessage(message, type) {
        const messageHTML = `<div class="message-container ${type}">${message}</div>`;
        $("#createExamForm").prepend(messageHTML);
        
        // Remove message after 5 seconds
        setTimeout(() => {
            $(".message-container").fadeOut(300, function() {
                $(this).remove();
            });
        }, 5000);
    }

    function loadManageExams() {
        $("#dynamicContentContainer").html(`
            <div class="exam-management-container">
                <h2>Manage Exams</h2>
                <div class="exam-controls">
                    <button id="refreshExams" class="btn primary-btn">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
                <div class="exam-list">
                    <div class="loading">Loading exams...</div>
                </div>
            </div>
        `).slideDown(300);

        // Add refresh handler
        $("#refreshExams").click(fetchExams);
        
        // Initial load
        fetchExams();
    }

    function fetchExams() {
        // Show loading state
        $(".exam-list").html('<div class="loading">Loading exams...</div>');
        
        // Make API call to fetch exams
        $.ajax({
            url: '/api/exams/',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    displayExams(response.data);
                } else {
                    showToast(response.message || 'Failed to fetch exams', 'error');
                    $(".exam-list").html('<div class="no-exams">Failed to load exams.</div>');
                }
            },
            error: function(xhr, status, error) {
                showToast(error || 'Error fetching exams', 'error');
                $(".exam-list").html('<div class="no-exams">Error loading exams.</div>');
            }
        });
    }

    function displayExams(exams) {
        if (!exams || exams.length === 0) {
            $(".exam-list").html('<div class="no-exams">No exams found.</div>');
            return;
        }

        let examHTML = '';
        exams.forEach(exam => {
            examHTML += `
                <div class="exam-item" data-exam-id="${exam.id}">
                    <div class="exam-info">
                        <h3>${exam.title}</h3>
                        <p>Subject: ${exam.subject} | Questions: ${exam.totalQuestions}</p>
                        <p>Duration: ${exam.duration} mins | Deadline: ${formatDate(exam.deadline)}</p>
                        <span class="exam-status ${exam.status}">${exam.status}</span>
                    </div>
                    <div class="exam-actions">
                        <button class="action-btn edit-btn" data-exam-id="${exam.id}">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" data-exam-id="${exam.id}">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            `;
        });

        $(".exam-list").html(examHTML);
        
        // Add action handlers
        $(".edit-btn").click(function() {
            const examId = $(this).data('exam-id');
            editExam(examId);
        });
        
        $(".delete-btn").click(function() {
            const examId = $(this).data('exam-id');
            deleteExam(examId);
        });
    }

    function loadStudentResults() {
        $("#dynamicContentContainer").html(`
            <div class="results-container">
                <h2>Student Results</h2>
                <div class="results-controls">
                    <select id="examFilter" class="form-control">
                        <option value="">All Exams</option>
                        <option value="recent">Recent Exams</option>
                    </select>
                    <button id="exportResults" class="btn primary-btn">
                        <i class="fas fa-download"></i> Export
                    </button>
                </div>
                <div class="results-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Student</th>
                                <th>Exam</th>
                                <th>Score</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="4" class="loading">Loading results...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `).slideDown(300);

        // Simulate loading results
        setTimeout(() => {
            loadResultsData();
        }, 1000);
    }

    function loadResultsData() {
        // Show loading state
        $(".results-container").html('<div class="loading">Loading results...</div>');
        
        // Make API call to fetch student results
        $.ajax({
            url: '/api/student-results/',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    displayResults(response.data);
                } else {
                    showToast(response.message || 'Failed to fetch results', 'error');
                    $(".results-container").html('<div class="no-results">Failed to load results.</div>');
                }
            },
            error: function(xhr, status, error) {
                showToast(error || 'Error fetching results', 'error');
                $(".results-container").html('<div class="no-results">Error loading results.</div>');
            }
        });
    }

    function displayResults(results) {
        if (!results || results.length === 0) {
            $(".results-table tbody").html('<tr><td colspan="4" class="no-results">No results found.</td></tr>');
            return;
        }

        let tableHTML = '';
        results.forEach(result => {
            tableHTML += `
                <tr>
                    <td>${result.student}</td>
                    <td>${result.exam}</td>
                    <td>${result.score}</td>
                    <td>${result.date}</td>
                </tr>
            `;
        });
        
        $(".results-table tbody").html(tableHTML);
    }

    function loadReportGenerator() {
        $("#dynamicContentContainer").html(`
            <div class="reports-container">
                <h2>Generate Reports</h2>
                <div class="report-cards">
                    <div class="report-card" data-report-type="performance">
                        <i class="fas fa-chart-line"></i>
                        <h3>Performance Report</h3>
                        <p>View student performance metrics</p>
                    </div>
                    <div class="report-card" data-report-type="attendance">
                        <i class="fas fa-user-check"></i>
                        <h3>Attendance Report</h3>
                        <p>Track student attendance</p>
                    </div>
                    <div class="report-card" data-report-type="analysis">
                        <i class="fas fa-question-circle"></i>
                        <h3>Question Analysis</h3>
                        <p>Analyze question performance</p>
                    </div>
                </div>
            </div>
        `).slideDown(300);
        
        $(".report-card").click(function() {
            const reportType = $(this).data('report-type');
            generateReport(reportType);
        });
    }

    function generateReport(reportType) {
        // Show loading state
        $(".report-card").prop('disabled', true);
        
        // Make API call to generate report
        $.ajax({
            url: `/api/reports/${reportType}/`,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    // Handle report data based on type
                    switch(reportType) {
                        case 'performance':
                            displayPerformanceReport(response.data);
                            break;
                        case 'attendance':
                            displayAttendanceReport(response.data);
                            break;
                        case 'analysis':
                            displayQuestionAnalysis(response.data);
                            break;
                    }
                } else {
                    showToast(response.message || 'Failed to generate report', 'error');
                }
            },
            error: function(xhr, status, error) {
                showToast(error || 'Error generating report', 'error');
            },
            complete: function() {
                $(".report-card").prop('disabled', false);
            }
        });
    }

    function loadProfileForm() {
        $("#dynamicContentContainer").html(`
            <div class="profile-container">
                <h2>Update Your Profile</h2>
                <form id="teacherProfileForm" class="profile-form">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input type="text" id="teacherName" name="name" placeholder="Full Name" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-envelope"></i>
                            <input type="email" id="teacherEmail" name="email" placeholder="Email Address" required readonly>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-phone"></i>
                            <input type="tel" id="teacherPhone" name="phone" placeholder="Phone Number" pattern="[0-9]{10}" title="Please enter a valid 10-digit phone number" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-building"></i>
                            <input type="text" id="teacherDepartment" name="department" placeholder="Department" readonly>
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

        loadProfileData();
        setupProfileFormHandlers();
    }

    function loadProfileData() {
        // Show loading state
        $("#profileForm").html('<div class="loading">Loading profile...</div>');
        
        // Make API call to fetch teacher profile
        $.ajax({
            url: '/api/teacher/profile/',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            success: function(response) {
                if (response.success) {
                    originalProfileData = response.data;
                    displayProfileData(response.data);
                } else {
                    showToast('Failed to load profile: ' + response.message, 'error');
                    $("#profileForm").html('<div class="error">Failed to load profile.</div>');
                }
            },
            error: function(xhr, status, error) {
                showToast('Error loading profile: ' + error, 'error');
                $("#profileForm").html('<div class="error">Error loading profile.</div>');
            }
        });
    }

    function setupProfileFormHandlers() {
        $("#teacherProfileForm").on('input change', checkFormChanges);
        
        $("#teacherProfileForm").submit(function(e) {
            e.preventDefault();
            updateProfile();
        });
    }

    function checkFormChanges() {
        const currentData = {
            name: $("#teacherName").val(),
            phone: $("#teacherPhone").val(),
            department: $("#teacherDepartment").val()
        };

        const hasChanges = Object.keys(originalProfileData).some(
            key => originalProfileData[key] !== currentData[key]
        );
        
        $(".save-profile-btn").prop('disabled', !hasChanges);
    }

    function updateProfile() {
        const updatedData = {
            name: $("#teacherName").val(),
            email: $("#teacherEmail").val(),
            phone: $("#teacherPhone").val(),
            department: $("#teacherDepartment").val()
        };
        
        // Show loading state
        $(".save-profile-btn").html('<i class="fas fa-spinner fa-spin"></i> Saving...').prop('disabled', true);
        
        // Make API call to update profile
        $.ajax({
            url: '/api/teacher/profile/',
            method: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            data: updatedData,
            success: function(response) {
                if (response.success) {
                    originalProfileData = updatedData;
                    showToast('Profile updated successfully', 'success');
                    $(".save-profile-btn").html('<i class="fas fa-save"></i> Save Changes').prop('disabled', false);
                } else {
                    showToast('Failed to update profile: ' + response.message, 'error');
                    $(".save-profile-btn").html('<i class="fas fa-save"></i> Save Changes').prop('disabled', false);
                }
            },
            error: function(xhr, status, error) {
                showToast('Error updating profile: ' + error, 'error');
                $(".save-profile-btn").html('<i class="fas fa-save"></i> Save Changes').prop('disabled', false);
            }
        });
    }

    function displayProfileData(profileData) {
        $("#teacherName").val(profileData.name);
        $("#teacherEmail").val(profileData.email);
        $("#teacherPhone").val(profileData.phone);
        $("#teacherDepartment").val(profileData.department);
        
        originalProfileData = {
            name: profileData.name,
            phone: profileData.phone,
            department: profileData.department
        };
        
        checkFormChanges();
    }

    // Utility functions
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    function editExam(examId) {
        // Show loading state
        $(".edit-btn").prop('disabled', true);
        
        // Make API call to get exam details
        $.ajax({
            url: `/api/exams/${examId}/`,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            success: function(response) {
                if (response.success) {
                    // Redirect to edit page with exam data
                    window.location.href = `/exams/manage/${examId}/`;
                } else {
                    showToast('Failed to load exam: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showToast('Error loading exam: ' + error, 'error');
            },
            complete: function() {
                $(".edit-btn").prop('disabled', false);
            }
        });
    }

    function deleteExam(examId) {
        if (!confirm('Are you sure you want to delete this exam? This action cannot be undone.')) {
            return;
        }
        
        // Show loading state
        $(".delete-btn").prop('disabled', true);
        
        // Make API call to delete exam
        $.ajax({
            url: `/api/exams/${examId}/`,
            method: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            success: function(response) {
                if (response.success) {
                    showToast('Exam deleted successfully', 'success');
                    // Refresh exam list
                    fetchExams();
                } else {
                    showToast('Failed to delete exam: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showToast('Error deleting exam: ' + error, 'error');
            },
            complete: function() {
                $(".delete-btn").prop('disabled', false);
            }
        });
    }

    function fetchPerformanceReport() {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: '/api/performance-report/',
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': csrftoken,
            },
            success: function(response) {
                if (response.success) {
                    displayPerformanceReport(response.data);
                } else {
                    showError('Failed to load performance report');
                }
            },
            error: function() {
                showError('Failed to load performance report');
            }
        });
    }
    
    function displayPerformanceReport(data) {
        // Clear previous content
        $('#mainContent').empty();
        
        // Create report container
        const reportDiv = $('<div>').addClass('performance-report');
        
        // Add title
        reportDiv.append($('<h2>').text('=== Exam Results Report ==='));
        
        // Add metrics
        const metrics = [
            `Total students: ${data.totalStudents}`,
            `Pass Rate: ${data.passRate}%`,
            `Average Mark: ${data.averageMark}`,
            `Highest Mark: ${data.highestMark}`,
            `Lowest Mark: ${data.lowestMark}`
        ];
        
        metrics.forEach(metric => {
            reportDiv.append($('<p>').text(metric));
        });
        
        // Add grade distribution
        reportDiv.append($('<h3>').text('Grade Distribution:'));
        const grades = [
            { grade: 'A', range: '85%+', count: data.gradeDistribution.A },
            { grade: 'B', range: '70-84%', count: data.gradeDistribution.B },
            { grade: 'C', range: '55-69%', count: data.gradeDistribution.C },
            { grade: 'D', range: '35-54%', count: data.gradeDistribution.D },
            { grade: 'F', range: '0-34%', count: data.gradeDistribution.F }
        ];
        
        grades.forEach(grade => {
            reportDiv.append($('<p>').text(
                `${grade.grade} Grade (${grade.range}): ${grade.count}`
            ));
        });
        
        // Add some basic styling
        $('<link>', {
            rel: 'stylesheet',
            type: 'text/css',
            href: 'teacher-dashboard.css'
        }).appendTo('head');

        $('#mainContent').append(reportDiv);
    }

    function fetchAttendanceReport(examId) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: `/api/attendance-report/${examId}/`,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': csrftoken,
            },
            success: function(response) {
                if (response.success) {
                    displayAttendanceReport(response.data);
                } else {
                    showError('Failed to load attendance report');
                }
            },
            error: function() {
                showError('Failed to load attendance report');
            }
        });
    }

    function displayAttendanceReport(data) {
        // Clear previous content
        $('#mainContent').empty();
        
        // Create report container
        const reportDiv = $('<div>').addClass('attendance-report');
        
        // Add title
        reportDiv.append($('<h2>').text('=== Exam Attendance Report ==='));
        
        // Add metrics
        const metrics = [
            `Total Registered Students: ${data.totalRegistered}`,
            `Students Present: ${data.present}`,
            `Students Absent: ${data.absent}`,
            `Attendance Rate: ${data.attendanceRate}%`
        ];
        
        metrics.forEach(metric => {
            reportDiv.append($('<p>').text(metric));
        });
        
        // Add late submissions if any
        if (data.lateSubmissions > 0) {
            reportDiv.append($('<p>').text(`Late Submissions: ${data.lateSubmissions}`));
        }
        
        // Add some basic styling
        $('<link>', {
            rel: 'stylesheet',
            type: 'text/css',
            href: 'teacher-dashboard.css'
        }).appendTo('head');
        
        // Add to main content
        $('#mainContent').append(reportDiv);
    }

    function fetchQuestionAnalysis(examId) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: `/api/question-analysis/${examId}/`,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'X-CSRFToken': csrftoken,
            },
            success: function(response) {
                if (response.success) {
                    displayQuestionAnalysis(response.data);
                } else {
                    showError('Failed to load question analysis');
                }
            },
            error: function() {
                showError('Failed to load question analysis');
            }
        });
    }
    
    function displayQuestionAnalysis(data) {
        // Clear previous content
        $('#mainContent').empty();
        
        // Create report container
        const reportDiv = $('<div>').addClass('question-analysis');
        
        // Add title
        reportDiv.append($('<h2>').text('=== Question Analysis Report ==='));
        reportDiv.append($('<p>').text(`Total Questions: ${data.totalQuestions}`));
        
        if (data.questionAnalysis.length === 0) {
            reportDiv.append($('<p>').text('No submissions yet'));
            $('#mainContent').append(reportDiv);
            return;
        }
        
        // Add analysis for each question
        data.questionAnalysis.forEach((question, index) => {
            const questionDiv = $('<div>').addClass('question-item');
            
            // Question header
            questionDiv.append($('<h3>').text(`Question ${index + 1}`));
            questionDiv.append($('<p>').text(question.questionText));
            
            // Statistics
            const statsDiv = $('<div>').addClass('question-stats');
            statsDiv.append($('<p>').text(`Accuracy: ${question.accuracy}%`));
            statsDiv.append($('<p>').text(`Correct Answers: ${question.correctAnswers}/${question.totalAnswers}`));
            
            // Common wrong answers
            if (question.commonWrongAnswers.length > 0) {
                const wrongAnswersDiv = $('<div>').addClass('wrong-answers');
                wrongAnswersDiv.append($('<h4>').text('Common Wrong Answers:'));
                question.commonWrongAnswers.forEach(wrong => {
                    wrongAnswersDiv.append($('<p>').text(
                        `Answer ${wrong.answer}: ${wrong.count} students`
                    ));
                });
                statsDiv.append(wrongAnswersDiv);
            }
            
            // Correct answer
            statsDiv.append($('<p>').text(`Correct Answer: ${question.correctAnswer}`));
            
            questionDiv.append(statsDiv);
            reportDiv.append(questionDiv);
        });
        
        // Add styling
        $('<link>', {
            rel: 'stylesheet',
            type: 'text/css',
            href: 'teacher-dashboard.css'
        }).appendTo('head');
        
        // Add to main content
        $('#mainContent').append(reportDiv);
    }
    

    // Add this function for toast notifications
    function showToast(message, type = 'success') {
        // Remove any existing toasts
        $('.toast-container').remove();
        
        // Create toast container if it doesn't exist
        if ($('.toast-container').length === 0) {
            $('body').append('<div class="toast-container"></div>');
        }
        
        // Create toast element
        const toast = $(`
            <div class="toast ${type}">
                <div class="toast-content">
                    <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                    <span>${message}</span>
                </div>
                <div class="toast-progress"></div>
            </div>
        `);
        
        // Add toast to container
        $('.toast-container').append(toast);
        
        // Show toast with animation
        setTimeout(() => {
            toast.addClass('show');
        }, 100);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.removeClass('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    document.addEventListener('DOMContentLoaded', function() {
        // ...existing code...

        document.getElementById('loginForm').addEventListener('submit', async function(event) {
            event.preventDefault();

            const loginBtn = this.querySelector('button[type="submit"]');
            const originalBtnHtml = loginBtn.innerHTML;
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

            const userType = document.getElementById('userType').value;
            if (!userType) {
                document.getElementById('error-message').textContent = 'Please select a user type';
                loginBtn.disabled = false;
                loginBtn.innerHTML = originalBtnHtml;
                return;
            }

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                await loginUser(userType, username, password);
                showToast('Login successful! Redirecting...', 'success');
            } catch (error) {
                showToast(error.message || 'Login failed', 'error');
            } finally {
                loginBtn.disabled = false;
                loginBtn.innerHTML = originalBtnHtml;
            }
        });
    });
});