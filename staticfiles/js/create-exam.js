// Get exam ID from URL path instead of query parameters
const examId = window.location.pathname.split('/').filter(Boolean).pop();

// Exam data structure with enhanced storage capabilities
let examData = {
    id: examId,
    title: '',
    subject: '',
    semester: '',
    duration: 60,
    totalQuestions: 10,
    createdAt: new Date().toISOString(),
    questions: []
};

// Current question position
let currentQuestionIndex = 0;
let draftKey = `examDraft_${examId}`;

// Initialize the editor
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading exam data for ID:', examId); // Debug log
    
    // Load exam data from server first
    loadExamData();
    
    // Setup event listeners
    document.getElementById('prevQuestion').addEventListener('click', prevQuestion);
    document.getElementById('nextQuestion').addEventListener('click', nextQuestion);
    document.getElementById('createExamBtn').addEventListener('click', createExam);
    document.getElementById('backToDashboardTop').addEventListener('click', goToDashboard);
    document.getElementById('backToDashboard').addEventListener('click', goToDashboard);

    // Set correct answer
    document.querySelectorAll('.set-correct-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Remove selected class from all options
            document.querySelectorAll('.answer-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            // Add selected class to parent option
            this.closest('.answer-option').classList.add('selected');
            // Save the question after setting correct answer
            saveQuestion();
        });
    });

    // Remove option
    document.querySelectorAll('.remove-option').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const option = this.closest('.answer-option');
            if (document.querySelectorAll('.answer-option').length > 2) {
                option.remove();
                // Save the question after removing option
                saveQuestion();
            } else {
                showToast('Must have at least 2 options', 'error');
            }
        });
    });

    // Add new option
    document.getElementById('addOptionBtn').addEventListener('click', function() {
        const optionsContainer = document.querySelector('.answer-options');
        const currentOptions = document.querySelectorAll('.answer-option');
        if (currentOptions.length >= 10) {
            showToast('Maximum 10 options allowed', 'error');
            return;
        }
        
        const newOptionLetter = String.fromCharCode(65 + currentOptions.length);
        const newOption = document.createElement('div');
        newOption.className = 'answer-option';
        newOption.innerHTML = `
            <span class="option-letter">${newOptionLetter}</span>
            <input type="text" class="option-input" placeholder="Option ${newOptionLetter}">
            <button class="set-correct-btn">
                <i class="fas fa-check"></i>
            </button>
            <button class="remove-option">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        optionsContainer.appendChild(newOption);
        
        // Add event listeners to new buttons
        newOption.querySelector('.set-correct-btn').addEventListener('click', function(e) {
            e.stopPropagation();
            document.querySelectorAll('.answer-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.closest('.answer-option').classList.add('selected');
            saveQuestion();
        });
        
        newOption.querySelector('.remove-option').addEventListener('click', function(e) {
            e.stopPropagation();
            if (document.querySelectorAll('.answer-option').length > 2) {
                this.closest('.answer-option').remove();
                saveQuestion();
            } else {
                showToast('Must have at least 2 options', 'error');
            }
        });
        
        showToast('Option added', 'success');
    });

    // Auto-save when leaving the page
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Initialize first question
    initializeQuestion();
    
    // Update progress bar
    updateProgress();
});

function loadExamData() {
    console.log('Fetching exam data from:', `/api/exams/${examId}/`); // Debug log
    
    // Fetch exam data from server
    fetch(`/api/exams/${examId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('Response status:', response.status); // Debug log
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received exam data:', data); // Debug log
        if (data.success) {
            examData = {
                ...examData,
                title: data.data.title,
                subject: data.data.subject, // Now contains {id, name} object
                subjectName: data.data.subject.name, // For display purposes
                semester: data.data.semester,
                duration: data.data.duration,
                totalQuestions: data.data.totalQuestions
            };
            
            // Make sure the totalQuestions input is updated if it exists
            if (document.getElementById('totalQuestions')) {
                document.getElementById('totalQuestions').value = examData.totalQuestions;
            }
            console.log('Updated exam data:', examData); // Debug log
            
            // Load any saved progress
            loadSavedProgress();
            
            // Display exam info
            displayExamInfo();
            
            // Initialize first question
            initializeQuestion();
            
            // Update progress bar
            updateProgress();
        } else {
            showToast('Failed to load exam data: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error loading exam data:', error);
        showToast('Error loading exam data. Please try again.', 'error');
    });
}

function goToDashboard() {
    if (examData.questions.length > 0) {
        if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
            window.location.href = '/accounts/teacher/dashboard/';
        }
    } else {
        window.location.href = '/accounts/teacher/dashboard/';
    }
}

function displayExamInfo() {
    document.getElementById('examTitleDisplay').textContent = examData.title;
    document.getElementById('examSubjectDisplay').textContent = `Subject: ${examData.subjectName || (examData.subject && examData.subject.name) || examData.subject || ''}`;
    document.getElementById('examDurationDisplay').textContent = `Duration: ${examData.duration} mins`;
    document.getElementById('totalQuestionsDisplay').textContent = `Questions: ${examData.totalQuestions}`;
}

function loadSavedProgress() {
    // First check localStorage for any draft
    const savedDraft = localStorage.getItem(draftKey);
    if (savedDraft) {
        try {
            const parsed = JSON.parse(savedDraft);
            examData.questions = parsed.questions || [];
            
            // Show info toast if questions were loaded
            if (examData.questions.length > 0) {
                showToast(`Loaded ${examData.questions.length} saved questions from draft`, 'info');
            }
        } catch (e) {
            console.error("Failed to load saved exam draft", e);
            showToast("Failed to load saved draft", 'error');
        }
    }
}

function saveProgress() {
    localStorage.setItem(draftKey, JSON.stringify(examData));
    console.log("Progress auto-saved");
}

function handleBeforeUnload(e) {
    if (examData.questions.length > 0) {
        saveQuestion();
        saveProgress();
        e.preventDefault();
        e.returnValue = 'You have unsaved exam questions. Are you sure you want to leave?';
    }
}

function initializeQuestion() {
    // Load existing question if available
    const existingQuestion = examData.questions[currentQuestionIndex];
    
    document.getElementById('questionText').value = existingQuestion?.text || '';
    
    // Clear existing options
    const optionsContainer = document.querySelector('.answer-options');
    optionsContainer.innerHTML = '';
    
    // Add options from existing question or default options
    const options = existingQuestion?.options || {
        A: '',
        B: '',
        C: '',
        D: ''
    };
    
    Object.entries(options).forEach(([letter, value]) => {
        const option = document.createElement('div');
        option.className = `answer-option ${letter === existingQuestion?.correctAnswer ? 'selected' : ''}`;
        option.innerHTML = `
            <span class="option-letter">${letter}</span>
            <input type="text" class="option-input" placeholder="Option ${letter}" value="${value}">
            <button class="set-correct-btn">
                <i class="fas fa-check"></i>
            </button>
            <button class="remove-option">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        optionsContainer.appendChild(option);
        
        // Add event listeners to new buttons
        option.querySelector('.set-correct-btn').addEventListener('click', function(e) {
            e.stopPropagation();
            document.querySelectorAll('.answer-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.closest('.answer-option').classList.add('selected');
            saveQuestion();
        });
        
        option.querySelector('.remove-option').addEventListener('click', function(e) {
            e.stopPropagation();
            if (document.querySelectorAll('.answer-option').length > 2) {
                this.closest('.answer-option').remove();
                saveQuestion();
            } else {
                showToast('Must have at least 2 options', 'error');
            }
        });
    });
    
    document.getElementById('currentQuestionNumber').textContent = currentQuestionIndex + 1;
    updateNavigationButtons();
}

function saveQuestion() {
    const question = {
        text: document.getElementById('questionText').value,
        options: {},
        correctAnswer: null
    };

    // Get all options
    document.querySelectorAll('.answer-option').forEach((option, index) => {
        const letter = String.fromCharCode(65 + index);
        question.options[letter] = option.querySelector('.option-input').value;
        
        // Check if this is the correct answer
        if (option.classList.contains('selected')) {
            question.correctAnswer = letter;
        }
    });

    // Update or add question
    examData.questions[currentQuestionIndex] = question;
    
    // Save to localStorage
    saveProgress();
    
    // Show temporary save confirmation
    showToast('Question saved successfully!', 'success');
}

function nextQuestion() {
    saveQuestion();
    if (currentQuestionIndex < examData.totalQuestions - 1) {
        currentQuestionIndex++;
        initializeQuestion();
        updateProgress();
        
        // Show final actions if on last question
        if (currentQuestionIndex === examData.totalQuestions - 1) {
            document.getElementById('finalActions').style.display = 'block';
            document.getElementById('nextQuestion').textContent = 'Finish';
        }
    } else {
        finishExamCreation();
    }
}

function prevQuestion() {
    saveQuestion();
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        initializeQuestion();
        updateProgress();
        document.getElementById('finalActions').style.display = 'none';
        document.getElementById('nextQuestion').textContent = 'Next';
    }
}

function updateNavigationButtons() {
    document.getElementById('prevQuestion').disabled = currentQuestionIndex === 0;
    document.getElementById('nextQuestion').disabled = 
        currentQuestionIndex === examData.totalQuestions - 1;
    
    // Show finish button on last question
    if (currentQuestionIndex === examData.totalQuestions - 1) {
        document.getElementById('createExamBtn').style.display = 'block';
    } else {
        document.getElementById('createExamBtn').style.display = 'none';
    }
}

function updateProgress() {
    const progress = ((currentQuestionIndex + 1) / examData.totalQuestions) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('questionCountDisplay').textContent =
        `${currentQuestionIndex + 1} of ${examData.totalQuestions}`;
}

async function finishExamCreation() {
    // Final save
    saveQuestion();
    
    try {
        // Send questions to the server
        const response = await fetch(`/api/exams/${examId}/questions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                questions: examData.questions
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to add questions');
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Failed to add questions');
        }

        // Show success message
        showToast('Questions added successfully!', 'success');
        
        // Show completion UI
        document.querySelector('.exam-creation-container').style.display = 'none';
        document.getElementById('completionScreen').style.display = 'block';
        
        // Add a button to go back to dashboard
        const completionScreen = document.getElementById('completionScreen');
        completionScreen.innerHTML = `
            <div class="completion-message">
                <h2><i class="fas fa-check-circle"></i> Exam Created Successfully!</h2>
                <p>All questions have been added to the exam.</p>
                <button id="goToDashboardBtn" class="btn primary-btn">
                    <i class="fas fa-home"></i> Return to Dashboard
                </button>
            </div>
        `;
        
        // Add event listener to the new button
        document.getElementById('goToDashboardBtn').addEventListener('click', function() {
            window.location.href = '/accounts/teacher/dashboard/';
        });
        
        // Clear local storage
        localStorage.removeItem(draftKey);
        
    } catch (error) {
        console.error('Error adding questions:', error);
        showToast('Failed to add questions: ' + error.message, 'error');
    }
}

async function createExam() {
    saveQuestion(); // Save the last question
    
    try {
        // Send exam data to server
        const response = await fetch('/api/exams/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                title: examData.title,
                subject: (typeof examData.subject === 'object' && examData.subject !== null) ? examData.subject.id : examData.subject,
                semester: examData.semester,
                duration: examData.duration,
                deadline: new Date().toISOString(), // Default to now if not available
                totalQuestions: examData.totalQuestions
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to create exam');
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Failed to create exam');
        }

        const examId = result.data.exam_id;
        
        // Now add the questions to the exam
        const questionsResponse = await fetch(`/api/exams/${examId}/questions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                questions: examData.questions
            })
        });

        if (!questionsResponse.ok) {
            const errorData = await questionsResponse.json();
            throw new Error(errorData.message || 'Failed to add questions');
        }

        const questionsResult = await questionsResponse.json();
        if (!questionsResult.success) {
            throw new Error(questionsResult.message || 'Failed to add questions');
        }

        // Show success message with deadlines
        const endTime = new Date(result.data.end_time);
        const lateDeadline = new Date(result.data.late_submission_end);
        
        showToast(
            `Exam created successfully! Regular deadline: ${endTime.toLocaleString()}\nLate submissions until: ${lateDeadline.toLocaleString()}`,
            'success'
        );

        // Show success modal
        document.getElementById('successModal').style.display = 'flex';
        document.querySelector('.exam-creation-container').style.display = 'none';
        
        // Clear client-side storage
        clearExamData();
        
        // Explicitly redirect to dashboard after short delay
        setTimeout(function() {
            window.location.href = '/accounts/teacher/dashboard/';
        }, 1200);
    } catch (error) {
        console.error('Error creating exam:', error);
        showToast('Failed to create exam: ' + error.message, 'error');
        
        // Enable retry button
        document.getElementById('createExamBtn').disabled = false;
        document.getElementById('createExamBtn').innerHTML = 
            '<i class="fas fa-redo"></i> Try Again';
    }
}

// Helper function to clear exam data
function clearExamData() {
    localStorage.removeItem(`examDraft_${examData.meta.title}`);
    sessionStorage.removeItem('examTitle');
    sessionStorage.removeItem('examSubject');
    sessionStorage.removeItem('examSemester');
    sessionStorage.removeItem('examDuration');
    sessionStorage.removeItem('examDeadline');
    sessionStorage.removeItem('totalQuestions');
    examData.questions = [];
}

// Helper function to get CSRF token
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function clearExamData() {
    // Clear only this exam's data
    localStorage.removeItem(draftKey);
    examData.questions = [];
    currentQuestionIndex = 0;
    updateProgress();
    initializeQuestion();
}

// Enhanced Toast notification function
function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Add icon based on type
    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="fas ${iconMap[type] || 'fa-check-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'toastFadeOut 0.5s ease forwards';
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}