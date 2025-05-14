$(document).ready(function() {
    let currentQuestion = 0;
    let answers = [];
    let timeLeft = 0; // Will be set from exam data
    let timerInterval;
    let questions = [];
    let examId = getExamIdFromUrl();
    let examData = {};

    // Get exam ID from URL
    function getExamIdFromUrl() {
        // First try to get from query parameters
        const urlParams = new URLSearchParams(window.location.search);
        const examIdFromQuery = urlParams.get('exam_id');
        if (examIdFromQuery) return examIdFromQuery;
        
        // If not in query, extract from path
        const pathParts = window.location.pathname.split('/');
        // Path format: /exams/take/123/
        for (let i = 0; i < pathParts.length; i++) {
            if (pathParts[i] === 'take' && i + 1 < pathParts.length) {
                return pathParts[i + 1];
            }
        }
        return null;
    }

    // Start exam button handler
    $("#startExamBtn").click(function() {
        $("#instructionsSection").fadeOut(300, function() {
            $("#examSection").fadeIn(300);
            initExam();
        });
    });

    // Load exam data when page loads
    loadExamData();

    // Fetch exam data from API
    function loadExamData() {
        if (!examId) {
            showError("No exam ID provided");
            return;
        }

        fetch(`/api/exams/${examId}/questions/`, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                examData = data.exam;
                questions = data.questions;
                
                // Update exam info in the UI
                updateExamInfo(examData);
            } else {
                showError(data.message || "Failed to load exam data");
            }
        })
        .catch(error => {
            console.error("Error loading exam:", error);
            showError("Failed to load exam data. Please try again.");
        });
    }

    // Update exam info in the UI
    function updateExamInfo(exam) {
        $("#examSection h1").text(exam.title);
        $("#totalQuestionsInfo").text(exam.total_questions);
        $("#totalQuestions").text(exam.total_questions);
        $(".exam-info p:nth-child(1)").html(`<i class="fas fa-clock"></i> Duration: ${exam.duration} minutes`);
        $(".exam-info p:nth-child(3)").html(`<i class="fas fa-book"></i> Subject: ${exam.subject}`);
        
        // Set timer duration
        timeLeft = exam.duration * 60; // Convert minutes to seconds
    }

    // Show error message
    function showError(message) {
        alert(message);
    }

    // Initialize exam
    function initExam() {
        if (questions.length === 0) {
            showError("No questions available for this exam");
            return;
        }

        loadQuestion(0);
        initQuestionDots();
        updateNavButtons();
        startTimer();
    }

    // Load question
    function loadQuestion(index) {
        const question = questions[index];
        $("#currentQuestionNum").text(index + 1);
        $("#questionContent").html(question.text);
        
        let optionsHTML = '';
        question.options.forEach((option, i) => {
            optionsHTML += `
                <div class="option ${answers[index] === i ? 'selected' : ''}" data-index="${i}">
                    ${option}
                </div>
            `;
        });
        $("#optionsContainer").html(optionsHTML);
    }

    // Handle option selection
    $(document).on('click', '.option', function() {
        const optionIndex = $(this).data('index');
        answers[currentQuestion] = optionIndex;
        
        // Update UI
        $('.option').removeClass('selected');
        $(this).addClass('selected');
        updateQuestionDots();
    });

    // Initialize question dots
    function initQuestionDots() {
        let dotsHTML = '';
        for (let i = 0; i < questions.length; i++) {
            dotsHTML += `<div class="question-dot" data-index="${i}"></div>`;
        }
        $("#questionDots").html(dotsHTML);
        updateQuestionDots();
    }

    // Update question dots
    function updateQuestionDots() {
        $(".question-dot").removeClass("current answered");
        $(".question-dot").each(function(index) {
            if (index === currentQuestion) {
                $(this).addClass("current");
            }
            if (answers[index] !== undefined) {
                $(this).addClass("answered");
            }
        });
    }

    // Navigation buttons
    $("#prevBtn").click(function() {
        if (currentQuestion > 0) {
            currentQuestion--;
            loadQuestion(currentQuestion);
            updateQuestionDots();
            updateNavButtons();
        }
    });

    $("#nextBtn").click(function() {
        if (currentQuestion < questions.length - 1) {
            currentQuestion++;
            loadQuestion(currentQuestion);
            updateQuestionDots();
            updateNavButtons();
        } else {
            // On last question, next becomes submit
            confirmSubmit();
        }
    });

    // Question dot navigation
    $(document).on('click', '.question-dot', function() {
        const index = $(this).data('index');
        currentQuestion = index;
        loadQuestion(currentQuestion);
        updateQuestionDots();
        updateNavButtons();
    });

    // Update navigation buttons
    function updateNavButtons() {
        $("#prevBtn").prop("disabled", currentQuestion === 0);
        
        if (currentQuestion === questions.length - 1) {
            $("#nextBtn").html('<i class="fas fa-check"></i> Submit');
        } else {
            $("#nextBtn").html('Next <i class="fas fa-arrow-right"></i>');
        }
    }

    // Start timer
    function startTimer() {
        updateTimerDisplay();
        timerInterval = setInterval(function() {
            timeLeft--;
            updateTimerDisplay();
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                alert("Time's up! Your exam will be submitted.");
                submitExam();
            }
        }, 1000);
    }

    // Update timer display
    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        $("#timer").text(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
    }

    // Confirm submit
    function confirmSubmit() {
        const unanswered = questions.length - answers.filter(a => a !== undefined).length;
        if (unanswered > 0) {
            if (confirm(`You have ${unanswered} unanswered questions. Are you sure you want to submit?`)) {
                submitExam();
            }
        } else {
            if (confirm("Are you sure you want to submit your exam?")) {
                submitExam();
            }
        }
    }

    // Submit exam
    function submitExam() {
        clearInterval(timerInterval);
        
        // Prepare submission data
        const submission = {
            exam_id: examId,
            answers: answers.map((answer, index) => ({
                question_id: questions[index].id,
                selected_option: answer
            }))
        };
        
        // Send to server
        fetch('/api/exams/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(submission)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Exam submitted successfully!");
                window.location.href = '/accounts/student/dashboard/';
            } else {
                alert(data.message || "Failed to submit exam");
            }
        })
        .catch(error => {
            console.error("Error submitting exam:", error);
            alert("Failed to submit exam. Please try again.");
        });
    }

    // Get CSRF token from cookies
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
});