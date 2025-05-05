function selectUserType(type) {
    // Remove 'selected' class from all user types
    const userTypes = document.querySelectorAll('.user-type');
    userTypes.forEach(element => {
        element.classList.remove('selected');
    });
    
    // Add 'selected' class to clicked element
    const selectedElement = event.currentTarget;
    selectedElement.classList.add('selected');
    
    // Update hidden input value
    document.getElementById('userType').value = type.toUpperCase();
}

async function loginUser(userType, username, password) {
    try {
        const response = await fetch('/accounts/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                username: username,
                password: password,
                userType: userType.toUpperCase()
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }
        
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            throw new Error(data.error || 'Login failed');
        }
        
    } catch (error) {
        console.error('Error during login:', error);
        document.getElementById('error-message').textContent = error.message;
    }
}

// Helper function to get CSRF token from cookies
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

document.addEventListener('DOMContentLoaded', function() {
    // Clear form fields and localStorage on page load
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('userType').value = '';
    
    // Remove selected class from all user types
    document.querySelectorAll('.user-type').forEach(element => {
        element.classList.remove('selected');
    });

    // Add click handlers to all user type options
    const userTypes = document.querySelectorAll('.user-type');
    const userTypeInput = document.getElementById('userType');
    
    userTypes.forEach(type => {
        type.addEventListener('click', function() {
            userTypes.forEach(t => t.classList.remove('selected'));
            this.classList.add('selected');
            userTypeInput.value = this.dataset.type;
        });
    });
    
    // Password visibility toggle
    const passwordToggle = document.querySelector('.password-toggle');
    const passwordInput = document.getElementById('password');
    
    passwordToggle.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });

    // Form submission
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginButton');
    const buttonText = loginButton.querySelector('.button-text');
    const loadingSpinner = loginButton.querySelector('.loading-spinner');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate user type selection
        if (!userTypeInput.value) {
            toastr.error('Please select a user type');
            return;
        }

        // Show loading state
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
        loginButton.disabled = true;

        // Submit the form
        fetch(this.action, {
            method: 'POST',
            body: new FormData(this),
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(async response => {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.indexOf('application/json') !== -1) {
                const data = await response.json();
                if (data.success) {
                    toastr.success('Login successful! Redirecting...');
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                } else {
                    toastr.error(data.error || 'Login failed. Please try again.');
                    // Reset loading state
                    buttonText.style.display = 'inline-block';
                    loadingSpinner.style.display = 'none';
                    loginButton.disabled = false;
                }
            } else {
                // Not JSON, probably HTML error page
                toastr.error('Unexpected server response. Please try again or contact support.');
                buttonText.style.display = 'inline-block';
                loadingSpinner.style.display = 'none';
                loginButton.disabled = false;
            }
        })
        .catch(error => {
            toastr.error('An error occurred. Please try again.');
            buttonText.style.display = 'inline-block';
            loadingSpinner.style.display = 'none';
            loginButton.disabled = false;
        });
    });
});