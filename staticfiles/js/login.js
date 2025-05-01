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
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
                userType: userType.toUpperCase()
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Login failed');
        }
        
        localStorage.setItem('token', data.token);
        localStorage.setItem('userType', userType.toUpperCase());
        
        // Redirect based on user type
        switch(userType.toUpperCase()) {
            case 'STUDENT':
                window.location.href = '/student-dashboard.html';
                break;
            case 'TEACHER':
                window.location.href = '/teacher-dashboard.html';
                break;
            case 'ADMIN':
                window.location.href = '/admin-dashboard.html';
                break;
            default:
                throw new Error('Invalid user type');
        }
        
    } catch (error) {
        console.error('Error during login:', error);
        document.getElementById('error-message').textContent = error.message || 'Invalid credentials';
    }
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
    userTypes.forEach(element => {
        element.addEventListener('click', function() {
            selectUserType(this.dataset.type);
        });
    });
    
    // Handle form submission
    document.getElementById('loginForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const userType = document.getElementById('userType').value;
        if (!userType) {
            document.getElementById('error-message').textContent = 'Please select a user type';
            return;
        }
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        await loginUser(userType, username, password);
    });

    // Password visibility toggle
    const passwordToggle = document.querySelector('.password-toggle');
    const passwordInput = document.querySelector('#password');

    passwordToggle.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type');
        if (type === 'password') {
            passwordInput.setAttribute('type', 'text');
            this.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
        } else {
            passwordInput.setAttribute('type', 'password');
            this.innerHTML = '<i class="fa-solid fa-eye"></i>';
        }
    });
});