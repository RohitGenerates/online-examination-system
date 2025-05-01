$(document).ready(function() {
    // Constants
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;
    
    // State management
    let originalProfileData = {};
    let retryCount = 0;
    
    // Initialize dashboard
    initDashboard();

    function initDashboard() {
        setupEventHandlers();
    }

    function setupEventHandlers() {
        // Logout handler
        $("#logoutBtn").click(handleLogout);
        
        // Option card handlers
        $(".option-card").click(function() {
            $(".option-card").removeClass("active");
            $(this).addClass("active");
            
            const optionId = $(this).attr("id");
            loadContent(optionId);
        });
    }

    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('userType');
        window.location.href = '/login.html';
    }

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
        $("#dynamicContentContainer").html(`
            <div class="welcome-message">
                <h2>Welcome to Teacher Dashboard</h2>
                <p>Select an option from the menu above to get started.</p>
            </div>
        `).slideDown(300);
    }

    function loadCreateExamForm() {
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
                                    <option value="">Select Subject</option>
                                    <option value="cs">Computer Science</option>
                                    <option value="it">Information Technology</option>
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
        
        $("#dynamicContentContainer").html(formHTML).slideDown(300);
        
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
        
        // Simulate API call
        setTimeout(() => {
            console.log("Exam created:", examData);
            
            // After successful creation, redirect to question editor
            redirectToQuestionEditor(examData);
        }, 1000);
    }

    function redirectToQuestionEditor(examData) {
        // Store exam data temporarily (in a real app, this would be saved to database)
        sessionStorage.setItem('currentExam', JSON.stringify(examData));
        
        // Redirect to question editor page
        window.location.href = '../../templates/exams/create-exam.html';
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
        // Simulated API call
        setTimeout(() => {
            const dummyExams = [
                {
                    id: 1,
                    title: "Midterm Examination",
                    subject: "Computer Science",
                    duration: 60,
                    totalQuestions: 30,
                    deadline: "2025-04-25T14:00:00",
                    status: "active"
                },
                {
                    id: 2,
                    title: "Final Assessment",
                    subject: "Information Technology",
                    duration: 120,
                    totalQuestions: 50,
                    deadline: "2025-05-05T11:00:00",
                    status: "draft"
                }
            ];
            
            displayExams(dummyExams);
        }, 800);
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
        // In a real app, this would be an API call
        const dummyResults = [
            { student: "John Doe", exam: "Midterm Exam", score: "85%", date: "2025-04-20" },
            { student: "Jane Smith", exam: "Midterm Exam", score: "92%", date: "2025-04-20" },
            { student: "Alex Johnson", exam: "Final Exam", score: "78%", date: "2025-05-10" }
        ];
        
        let tableHTML = '';
        dummyResults.forEach(result => {
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

    function loadProfileForm() {
        $("#dynamicContentContainer").html(`
            <div class="profile-container">
                <h2>Update Your Profile</h2>
                <form id="teacherProfileForm" class="form-grid">
                    <div class="form-group form-full-width">
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
                            <input type="tel" id="phoneNumber" name="phoneNumber" placeholder="Phone Number" pattern="[0-9]{10}" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-building"></i>
                            <select id="department" name="department" required>
                                <option value="">Select Department</option>
                                <option value="CS">Computer Science</option>
                                <option value="IT">Information Technology</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-id-card"></i>
                            <input type="text" id="teacherId" name="teacherId" placeholder="Teacher ID" readonly>
                        </div>
                    </div>
                    <div class="form-actions form-full-width">
                        <button type="button" class="btn reset-btn" id="resetForm" style="display: none;">Reset Changes</button>
                        <button type="submit" class="btn primary-btn" id="saveChanges" disabled>Save Changes</button>
                    </div>
                </form>
                <div id="profileUpdateMessage" class="message-container"></div>
            </div>
        `).slideDown(300);

        loadProfileData();
        setupProfileFormHandlers();
    }

    function loadProfileData() {
        // Simulated API call
        setTimeout(() => {
            const dummyProfile = {
                fullName: "Prof. Smith",
                email: "prof.smith@university.edu",
                phoneNumber: "1234567890",
                department: "CS",
                teacherId: "TEA-1001"
            };
            
            $("#fullName").val(dummyProfile.fullName);
            $("#email").val(dummyProfile.email);
            $("#phoneNumber").val(dummyProfile.phoneNumber);
            $("#department").val(dummyProfile.department);
            $("#teacherId").val(dummyProfile.teacherId);
            
            originalProfileData = {
                fullName: dummyProfile.fullName,
                phoneNumber: dummyProfile.phoneNumber,
                department: dummyProfile.department
            };
            
            checkFormChanges();
        }, 500);
    }

    function setupProfileFormHandlers() {
        $("#teacherProfileForm").on('input change', checkFormChanges);
        
        $("#resetForm").click(function() {
            $("#fullName").val(originalProfileData.fullName);
            $("#phoneNumber").val(originalProfileData.phoneNumber);
            $("#department").val(originalProfileData.department);
            checkFormChanges();
            $("#profileUpdateMessage").empty();
        });
        
        $("#teacherProfileForm").submit(function(e) {
            e.preventDefault();
            updateProfile();
        });
    }

    function checkFormChanges() {
        const currentData = {
            fullName: $("#fullName").val(),
            phoneNumber: $("#phoneNumber").val(),
            department: $("#department").val()
        };

        const hasChanges = Object.keys(originalProfileData).some(
            key => originalProfileData[key] !== currentData[key]
        );
        
        $("#saveChanges").prop('disabled', !hasChanges);
        $("#resetForm").toggle(hasChanges);
    }

    function updateProfile() {
        const formData = {
            fullName: $("#fullName").val(),
            phoneNumber: $("#phoneNumber").val(),
            department: $("#department").val()
        };

        $("#saveChanges").prop('disabled', true);
        $("#profileUpdateMessage").html('<div class="info">Updating profile...</div>');

        // Simulate API call
        setTimeout(() => {
            $("#profileUpdateMessage").html('<div class="success">Profile updated successfully!</div>');
            originalProfileData = { ...formData };
            checkFormChanges();
        }, 1000);
    }

    // Utility functions
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Placeholder functions for future implementation
    function editExam(examId) {
        console.log(`Editing exam ${examId}`);
        // Implementation would go here
    }

    function deleteExam(examId) {
        console.log(`Deleting exam ${examId}`);
        // Implementation would go here
    }

    function generateReport(reportType) {
        console.log(`Generating ${reportType} report`);
        // Implementation would go here
    }
});