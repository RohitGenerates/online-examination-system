$(document).ready(function() {
    console.log('Document ready'); // Debug log

    // Initialize form sections
    $("#signupFormSection").hide();
    $("#studentFields, #teacherFields").hide();

    // Handle user type selection with smooth transition
    $(".user-type").click(function() {
        console.log('User type clicked'); // Debug log
        $(".user-type").removeClass("selected");
        $(this).addClass("selected");
        
        const userType = $(this).data("type");
        console.log('Selected type:', userType); // Debug log
        
        $("#userType").val(userType);
        
        // Smooth transition between sections
        $("#userTypeSection").fadeOut(300, function() {
            $("#signupFormSection").fadeIn(300);
            
            // Show relevant additional fields with animation
            if (userType === "student") {
                $("#teacherFields").hide();
                $("#studentFields").fadeIn(300);
            } else {
                $("#studentFields").hide();
                $("#teacherFields").fadeIn(300);
            }
        });
    });

    // Handle back button with smooth transition
    $("#backToType").click(function() {
        console.log('Back button clicked'); // Debug log
        $("#signupFormSection").fadeOut(300, function() {
            $("#userTypeSection").fadeIn(300);
            // Reset form when going back
            $("#signupForm")[0].reset();
            $("#error-message").text("");
            $(".user-type").removeClass("selected");
        });
    });

    // Password visibility toggle
    $(".password-toggle").click(function() {
        const input = $(this).prev("input");
        const icon = $(this).find("i");
        
        if (input.attr("type") === "password") {
            input.attr("type", "text");
            icon.removeClass("fa-eye").addClass("fa-eye-slash");
        } else {
            input.attr("type", "password");
            icon.removeClass("fa-eye-slash").addClass("fa-eye");
        }
    });

    // Form validation and submission
    $("#signupForm").submit(function(e) {
        e.preventDefault();
        console.log('Form submitted'); // Debug log
        
        // Clear previous errors
        $("#error-message").text("");
        
        // Basic validation
        const userType = $("#userType").val();
        if (!userType) {
            $("#error-message").text("Please select a user type").fadeIn();
            return false;
        }

        const password = $("#password1").val();
        const confirmPassword = $("#password2").val();
        
        if (password !== confirmPassword) {
            $("#error-message").text("Passwords do not match").fadeIn();
            return false;
        }

        // Prepare form data with correct field names
        const formData = new FormData();
        formData.append('username', $("#username").val());
        formData.append('email', $("#email").val());
        formData.append('password', password);
        formData.append('role', userType);
        
        // Add additional fields based on user type
        if (userType === 'student') {
            formData.append('student_id', $("#student_id").val());
            formData.append('department', $("#student_department").val());
            formData.append('semester', $("#semester").val());
        } else if (userType === 'teacher') {
            formData.append('department', $("#department").val());
        }
        
        // Disable submit button and show loading state
        const submitBtn = $(this).find("button[type='submit']");
        const originalText = submitBtn.html();
        submitBtn.prop("disabled", true).html('<i class="fas fa-spinner fa-spin"></i> Signing up...');
        
        // Submit form
        $.ajax({
            url: "/accounts/signup/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Server response:', response); // Debug log
                if (response.redirect) {
                    // Show success toast notification
                    const toast = $('<div class="toast success">Account created successfully! Redirecting...</div>');
                    $('body').append(toast);
                    toast.fadeIn(300);
                    
                    // Redirect to the appropriate page
                    setTimeout(function() {
                        window.location.href = response.redirect;
                    }, 2000);
                } else {
                    // Show error toast notification
                    const toast = $('<div class="toast error">An error occurred during signup</div>');
                    $('body').append(toast);
                    toast.fadeIn(300);
                    setTimeout(() => toast.fadeOut(300, () => toast.remove()), 3000);
                    submitBtn.prop("disabled", false).html(originalText);
                }
            },
            error: function(xhr) {
                console.error('AJAX error:', xhr); // Debug log
                let errorMessage = "An error occurred during signup";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                // Show error toast notification
                const toast = $('<div class="toast error">' + errorMessage + '</div>');
                $('body').append(toast);
                toast.fadeIn(300);
                setTimeout(() => toast.fadeOut(300, () => toast.remove()), 3000);
                submitBtn.prop("disabled", false).html(originalText);
            }
        });
    });
});