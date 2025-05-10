// Get exam ID from URL
const urlParams = new URLSearchParams(window.location.search);
const examId = urlParams.get('id');

// Exam data structure with enhanced storage capabilities
let examData = {
    id: examId,
    title: '',
    subject: '',
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
    // Load exam data from server first
    loadExamData();
    
    // Setup event listeners
    document.getElementById('prevQuestion').addEventListener('click', prevQuestion);
    document.getElementById('nextQuestion').addEventListener('click', nextQuestion);
    document.getElementById('createExamBtn').addEventListener('click', createExam);
    document.getElementById('backToDashboard').addEventListener('click', goToDashboard);
    document.getElementById('backToDashboardTop').addEventListener('click', goToDashboard);

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
    // Fetch exam data from server
    fetch(`/api/exams/${examId}/`, {
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
        if (data.success) {
            examData = {
                ...examData,
                title: data.data.title,
                subject: data.data.subject,
                duration: data.data.duration,
                totalQuestions: data.data.totalQuestions
            };
            
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
            window.location.href = '/accounts/teacher-dashboard/';
        }
    } else {
        window.location.href = '/accounts/teacher-dashboard/';
    }
}

function displayExamInfo() {
    document.getElementById('examTitleDisplay').textContent = examData.title;
    document.getElementById('examSubjectDisplay').textContent = `Subject: ${examData.subject}`;
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

function finishExamCreation() {
    // Final save
    saveQuestion();
    
    // Show completion UI
    document.querySelector('.exam-creation-container').style.display = 'none';
    document.getElementById('completionScreen').style.display = 'block';
}

async function createExam() {
    saveQuestion(); // Save the last question
    
    try {
        // Send exam data to server
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
            throw new Error(errorData.message || 'Failed to create exam');
        }
        
        const result = await response.json();
        if (result.success) {
            // Show success modal
            document.getElementById('successModal').style.display = 'flex';
            document.querySelector('.exam-creation-container').style.display = 'none';
            
            // Clear client-side storage
            clearExamData();
            
            showToast('Exam created successfully!', 'success');
        } else {
            throw new Error(result.message || 'Failed to create exam');
        }
    } catch (error) {
        console.error('Error creating exam:', error);
        showToast('Failed to create exam: ' + error.message, 'error');
    }
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