$(document).ready(function() {
    // Show instructions first, hide exam content
    $("#examContent").hide();
    $("#instructionsSection").show();

    // Start Exam button logic
    $("#startExamBtn").click(function() {
        $("#instructionsSection").fadeOut(300, function() {
            $("#examContent").fadeIn(300);
            initializeExam();
        });
    });

    // Exam data structure
    let answers = {};
    let timerInterval;
    let examData = {
        id: null,
        title: $('#examContent h2').text().trim(),
        timeRemaining: window.REMAINING_TIME || 0
    };

    // Initialize exam with server-provided data
    function initializeExam() {
        // Use the server-provided remaining time
        examData.timeRemaining = window.REMAINING_TIME || 0;
        
        // Start timer
        startTimer();
        
        // Load saved progress
        loadProgress();
        
        // Set up answer change listeners
        $("input[type='radio']").change(function() {
            const questionId = $(this).attr('name');
            const selectedOption = $(this).val();
            answers[questionId] = selectedOption;
            saveProgress();
        });
    }

    // Timer functions
    function startTimer() {
        updateTimerDisplay();
        timerInterval = setInterval(function() {
            examData.timeRemaining--;
            updateTimerDisplay();
            
            if (examData.timeRemaining <= 0) {
                clearInterval(timerInterval);
                showToast("Time's up! Your exam will be submitted.", "warning");
                submitExam();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const minutes = Math.floor(examData.timeRemaining / 60);
        const seconds = examData.timeRemaining % 60;
        $("#timer").text(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
        
        // Add warning class when less than 5 minutes remaining
        if (examData.timeRemaining <= 300) {
            $("#timer").addClass("warning");
        }
    }

    // Progress saving/loading
    function saveProgress() {
        localStorage.setItem(`exam_answers`, JSON.stringify(answers));
    }

    function loadProgress() {
        const savedAnswers = localStorage.getItem(`exam_answers`);
        if (savedAnswers) {
            answers = JSON.parse(savedAnswers);
            // Set the checked state for saved answers
            for (const [name, value] of Object.entries(answers)) {
                $(`input[name="${name}"][value="${value}"]`).prop('checked', true);
            }
        }
    }

    // Form submission
    $("#exam-form").on("submit", function(e) {
        // Check for unanswered questions
        const totalQuestions = $('.question-container').length;
        const answeredQuestions = Object.keys(answers).length;
        
        if (answeredQuestions < totalQuestions) {
            if (!confirm(`You have ${totalQuestions - answeredQuestions} unanswered questions. Are you sure you want to submit?`)) {
                e.preventDefault();
                return false;
            }
        }
        
        // Clear saved answers on successful submit
        localStorage.removeItem('exam_answers');
        return true;
    });

    // Submit exam function
    function submitExam() {
        // Auto-submit the form when time runs out
        $("#exam-form").submit();
    }

    // Toast notification
    function showToast(message, type = 'success') {
        // Remove existing toasts
        $(".toast").remove();
        
        // Create new toast
        const toast = $("<div>").addClass(`toast ${type}`);
        
        // Add icon based on type
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle'
        };
        
        toast.html(`
            <i class="fas ${iconMap[type] || 'fa-check-circle'}"></i>
            <span>${message}</span>
        `);
        
        $("body").append(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.css("animation", "toastFadeOut 0.5s ease forwards");
            toast.on("animationend", () => toast.remove());
        }, 3000);
    }

    // Utility function to get CSRF token
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