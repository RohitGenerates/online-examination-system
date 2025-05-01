document.addEventListener('DOMContentLoaded', function() {
    const teacherDetailsForm = document.getElementById('teacherDetailsForm');
    const errorMessage = document.getElementById('error-message');

    teacherDetailsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(teacherDetailsForm);
        
        // Send data to server
        fetch('/accounts/teacher-details/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/accounts/login/';
            } else {
                errorMessage.textContent = data.error || 'An error occurred while saving your details';
            }
        })
        .catch(error => {
            errorMessage.textContent = 'An error occurred while saving your details';
            console.error('Error:', error);
        });
    });
}); 