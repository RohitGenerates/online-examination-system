document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const examTitleDisplay = document.getElementById('examTitleDisplay');
    const examSubjectDisplay = document.getElementById('examSubjectDisplay');
    const examDurationDisplay = document.getElementById('examDurationDisplay');
    const totalQuestionsDisplay = document.getElementById('totalQuestionsDisplay');
    const examTotalMarksDisplay = document.getElementById('examTotalMarksDisplay');
    const questionText = document.getElementById('questionText');
    const optionsContainer = document.querySelector('.options-container');
    const currentQuestionNumber = document.getElementById('currentQuestionNumber');
    const questionCountDisplay = document.getElementById('questionCountDisplay');
    const progressBar = document.getElementById('progressBar');
    const prevQuestionBtn = document.getElementById('prevQuestion');
    const nextQuestionBtn = document.getElementById('nextQuestion');
    const addOptionBtn = document.getElementById('addOptionBtn');
    const deleteQuestionBtn = document.getElementById('deleteQuestionBtn');
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    const resetBtn = document.getElementById('resetBtn');
    const saveBtn = document.getElementById('saveBtn');
    const backBtn = document.getElementById('backBtn');
    const toastContainer = document.getElementById('toastContainer');


    let currentQuestionIndex = 0;
    let originalExamData = JSON.parse(JSON.stringify(examData));

    // Initialize the page
    function init() {
        loadExamData();
        renderQuestion(currentQuestionIndex);
        updateNavigation();
        updateProgress();
    }

    // Load exam data into the header
    function loadExamData() {
        examTitleDisplay.textContent = examData.title;
        examSubjectDisplay.textContent = `Subject: ${examData.subject}`;
        examDurationDisplay.textContent = `Duration: ${examData.duration} mins`;
        totalQuestionsDisplay.textContent = `Questions: ${examData.questions.length}`;
        
        // Calculate total marks
        const totalMarks = examData.questions.reduce((sum, question) => sum + question.marks, 0);
        examTotalMarksDisplay.textContent = `Total Marks: ${totalMarks}`;
    }

    // Render question and options
    function renderQuestion(index) {
        if (index < 0 || index >= examData.questions.length) return;
        
        const question = examData.questions[index];
        questionText.value = question.text;
        
        // Clear existing options
        optionsContainer.innerHTML = '';
        
        // Render each option (max 4)
        const maxOptions = 4;
        for (let i = 0; i < Math.min(maxOptions, question.options.length); i++) {
            const optionItem = document.createElement('div');
            optionItem.className = `option-item ${i === question.correctAnswer ? 'correct' : ''}`;
            
            optionItem.innerHTML = `
                <button class="remove-option">
                    <i class="fas fa-times"></i>
                </button>
                <div class="option-content">
                    <span class="option-label">${String.fromCharCode(65 + i)}</span>
                    <input type="text" class="option-input" value="${question.options[i]}" 
                        placeholder="Option ${String.fromCharCode(65 + i)}">
                    <button class="correct-toggle">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            `;
            
            optionsContainer.appendChild(optionItem);
        }

        // Render each option
        question.options.forEach((option, optIndex) => {
            const optionItem = document.createElement('div');
            optionItem.className = `option-item ${optIndex === question.correctAnswer ? 'correct' : ''}`;
            optionItem.dataset.option = String.fromCharCode(65 + optIndex);
            
            optionItem.innerHTML = `
                <div class="option-content">
                    <span class="option-label">${String.fromCharCode(65 + optIndex)}</span>
                    <input type="text" class="option-input" value="${option}" placeholder="Option ${String.fromCharCode(65 + optIndex)}">
                    <button class="remove-option">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <button class="set-correct-btn">
                    ${optIndex === question.correctAnswer ? '✓ Correct Answer' : 'Set as Correct'}
                </button>
            `;
            
            optionsContainer.appendChild(optionItem);
        });
        
        currentQuestionNumber.textContent = index + 1;
    }

    // Update navigation buttons state
    function updateNavigation() {
        prevQuestionBtn.disabled = currentQuestionIndex === 0;
        nextQuestionBtn.disabled = currentQuestionIndex === examData.questions.length - 1;
    }

    // In your updateProgress function:
    function updateProgress() {
        const progress = ((currentQuestionIndex + 1) / examData.questions.length) * 100;
        progressBar.style.width = `${progress}%`;
        questionCountDisplay.textContent = `${currentQuestionIndex + 1} of ${examData.questions.length}`;
    }

    // Save current question data before navigating away
    function saveCurrentQuestion() {
        const question = examData.questions[currentQuestionIndex];
        question.text = questionText.value;
        
        // Update options
        question.options = [];
        const optionInputs = document.querySelectorAll('.option-input');
        optionInputs.forEach(input => {
            question.options.push(input.value);
        });
    }

    // Show toast notification
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                           type === 'error' ? 'fa-exclamation-circle' : 
                           'fa-info-circle'}"></i>
            ${message}
        `;
        
        toastContainer.appendChild(toast);
        
        // Remove toast after animation
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Event Listeners
    prevQuestionBtn.addEventListener('click', () => {
        saveCurrentQuestion();
        currentQuestionIndex--;
        renderQuestion(currentQuestionIndex);
        updateNavigation();
        updateProgress();
    });

    nextQuestionBtn.addEventListener('click', () => {
        saveCurrentQuestion();
        currentQuestionIndex++;
        renderQuestion(currentQuestionIndex);
        updateNavigation();
        updateProgress();
    });

    // Add new option
    addOptionBtn.addEventListener('click', () => {
        const question = examData.questions[currentQuestionIndex];
        if (question.options.length >= 10) {
            showToast('Maximum 10 options allowed', 'error');
            return;
        }
        
        const newOptionLetter = String.fromCharCode(65 + question.options.length);
        question.options.push(`New ${newOptionLetter} Option`);
        renderQuestion(currentQuestionIndex);
        showToast('Option added', 'success');
    });

    // Delete current question
    deleteQuestionBtn.addEventListener('click', () => {
        if (examData.questions.length <= 1) {
            showToast('Exam must have at least one question', 'error');
            return;
        }
        
        examData.questions.splice(currentQuestionIndex, 1);
        
        if (currentQuestionIndex >= examData.questions.length) {
            currentQuestionIndex = examData.questions.length - 1;
        }
        
        renderQuestion(currentQuestionIndex);
        updateNavigation();
        updateProgress();
        loadExamData(); // Update total questions count
        showToast('Question deleted', 'success');
    });

    // Add new question
    addQuestionBtn.addEventListener('click', () => {
        const newQuestionId = examData.questions.length > 0 
            ? Math.max(...examData.questions.map(q => q.id)) + 1 
            : 1;
            
        examData.questions.push({
            id: newQuestionId,
            text: "New question text",
            options: ["Option A", "Option B"],
            correctAnswer: 0,
            marks: 5
        });
        
        currentQuestionIndex = examData.questions.length - 1;
        renderQuestion(currentQuestionIndex);
        updateNavigation();
        updateProgress();
        loadExamData(); // Update total questions count
        showToast('New question added', 'success');
    });

    // Set correct answer
    optionsContainer.addEventListener('click', (e) => {
        // Set correct answer
        const correctToggle = e.target.closest('.correct-toggle');
        if (correctToggle) {
            const optionItem = correctToggle.closest('.option-item');
            const optionIndex = Array.from(optionItem.parentElement.children).indexOf(optionItem);
            examData.questions[currentQuestionIndex].correctAnswer = optionIndex;
            renderQuestion(currentQuestionIndex);
            return;
        }
        
        // Remove option
        const removeBtn = e.target.closest('.remove-option');
        if (removeBtn) {
            const optionItem = removeBtn.closest('.option-item');
            const optionIndex = Array.from(optionItem.parentElement.children).indexOf(optionItem);
            const question = examData.questions[currentQuestionIndex];
            
            if (question.options.length <= 2) {
                showToast('Question must have at least 2 options', 'error');
                return;
            }
            
            question.options.splice(optionIndex, 1);
            
            // Adjust correct answer if needed
            if (question.correctAnswer === optionIndex) {
                question.correctAnswer = 0;
                showToast('Correct answer reset to Option A', 'info');
            } else if (question.correctAnswer > optionIndex) {
                question.correctAnswer--;
            }
            
            renderQuestion(currentQuestionIndex);
            showToast('Option removed', 'success');
        }
    });

    // Reset all changes
    resetBtn.addEventListener('click', () => {
        examData = JSON.parse(JSON.stringify(originalExamData));
        currentQuestionIndex = 0;
        init();
        showToast('All changes reset', 'success');
    });

    // Save exam
    saveBtn.addEventListener('click', () => {
        saveCurrentQuestion();
        originalExamData = JSON.parse(JSON.stringify(examData));
        showToast('Exam saved successfully', 'success');
        
        // In real app, would send to API here
        console.log('Exam data saved:', examData);
    });

    // Back to dashboard
    backBtn.addEventListener('click', () => {
        showToast('Returning to dashboard', 'info');
        // In real app, would redirect to dashboard
        setTimeout(() => {
            window.location.href = '/accounts/teacher/dashboard/';
        }, 1000);
    });

    // Initialize the page
    init();
});

// Add to your existing event listeners section
document.getElementById('editExamTitle').addEventListener('input', (e) => {
    examData.title = e.target.value;
    updateExamHeader();
});

document.getElementById('editExamSubject').addEventListener('input', (e) => {
    examData.subject = e.target.value;
    updateExamHeader();
});

document.getElementById('editExamDuration').addEventListener('input', (e) => {
    examData.duration = parseInt(e.target.value) || 0;
    updateExamHeader();
});

// Add this helper function
function updateExamHeader() {
    document.getElementById('editExamTitle').value = examData.title;
    document.getElementById('editExamSubject').value = examData.subject;
    document.getElementById('editExamDuration').value = examData.duration;
    
    // Calculate total marks
    const totalMarks = examData.questions.reduce((sum, q) => sum + q.marks, 0);
    document.getElementById('editExamTotalMarks').value = totalMarks;
}