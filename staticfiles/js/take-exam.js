$(document).ready(function() {
    let currentQuestion = 0;
    let answers = [];
    let timeLeft = 3600; // 1 hour in seconds
    let timerInterval;

    // Start exam button handler
    $("#startExamBtn").click(function() {
        $("#instructionsSection").fadeOut(300, function() {
            $("#examSection").fadeIn(300);
            initExam();
        });
    });

    // Dummy questions array
    const questions = [
        {
            question: "What is the capital of France?",
            options: ["London", "Berlin", "Paris", "Madrid"],
            correct: 2
        },
        // Add more questions here
    ];

    // Initialize exam
    function initExam() {
        $("#totalQuestions").text(questions.length);
        loadQuestion(0);
        initQuestionDots();
        updateNavButtons();
        startTimer();
    }

    // Load question
    function loadQuestion(index) {
        const question = questions[index];
        $("#currentQuestionNum").text(index + 1);
        $("#questionContent").html(question.question);
        
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
        
        // Auto-advance to next question after brief delay
        setTimeout(() => {
            if (currentQuestion < questions.length - 1) {
                currentQuestion++;
                loadQuestion(currentQuestion);
                updateNavButtons();
            }
        }, 500);
    });

    // Navigation buttons
    $("#prevBtn").click(() => {
        if (currentQuestion > 0) {
            currentQuestion--;
            loadQuestion(currentQuestion);
            updateNavButtons();
        }
    });

    $("#nextBtn").click(() => {
        if (currentQuestion < questions.length - 1) {
            currentQuestion++;
            loadQuestion(currentQuestion);
            updateNavButtons();
        }
    });

    // Question dots navigation
    function initQuestionDots() {
        let dotsHTML = '';
        for (let i = 0; i < questions.length; i++) {
            dotsHTML += `<div class="dot" data-index="${i}"></div>`;
        }
        $("#questionDots").html(dotsHTML);
        updateQuestionDots();
    }

    function updateQuestionDots() {
        $(".dot").each(function(index) {
            $(this).toggleClass('answered', answers[index] !== undefined)
                  .toggleClass('current', index === currentQuestion);
        });
    }

    // Timer functionality
    function startTimer() {
        timerInterval = setInterval(function() {
            timeLeft--;
            updateTimerDisplay();
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                submitExam(true);
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const timerElement = $("#timer");
        
        timerElement.text(`${minutes}:${seconds < 10 ? '0' : ''}${seconds}`);
        
        // Update timer color based on time remaining
        if (timeLeft <= 300) { // 5 minutes
            timerElement.removeClass('warning').addClass('danger');
        } else if (timeLeft <= 600) { // 10 minutes
            timerElement.removeClass('success').addClass('warning');
        }
    }

    // Submit exam
    $("#submitExam").click(() => {
        const unanswered = questions.length - answers.filter(a => a !== undefined).length;
        
        if (unanswered > 0) {
            if (!confirm(`You have ${unanswered} unanswered questions. Are you sure you want to submit?`)) {
                return;
            }
        }
        
        submitExam(false);
    });

    function submitExam(isAutoSubmit) {
        // Here you would typically send the answers to your server
        if (isAutoSubmit) {
            alert("Time's up! Your exam has been automatically submitted.");
        }
        // Redirect to results page or show results
        console.log('Submitted answers:', answers);
    }

    // Initialize the exam
    initExam();
});