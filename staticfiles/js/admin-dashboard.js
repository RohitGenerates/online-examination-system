$(document).ready(function() {
    // Constants
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;
    
    // State management
    let originalProfileData = {};
    let retryCount = 0;
    
    // Initialize dashboard
    initDashboard();

    function initDashboard() {
        setupEventHandlers();
        // Load default data if needed
    }

    function setupEventHandlers() {
        // Logout handler
        $("#logoutBtn").click(handleLogout);
        
        // Option card handlers
        $(".option-card").click(function() {
            $(".option-card").removeClass("active");
            $(this).addClass("active");
            
            const optionId = $(this).attr("id");
            loadContent(optionId);
        });
    }

    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('userType');
        window.location.href = '/login.html';
    }

    function loadContent(optionId) {
        $("#dynamicContentContainer").empty().hide();
        
        switch(optionId) {
            case "manageUsersOption":
                loadUserManagement();
                break;
            case "systemSettingsOption":
                loadSystemSettings();
                break;
            case "systemLogsOption":
                loadSystemLogs();
                break;
            case "updateProfileOption":
                loadProfileForm();
                break;
            default:
                showWelcomeMessage();
        }
    }

    function showWelcomeMessage() {
        $("#dynamicContentContainer").html(`
            <div class="welcome-message">
                <h2>Welcome to Admin Dashboard</h2>
                <p>Select an option from the menu above to manage the system.</p>
            </div>
        `).slideDown(300);
    }

    function loadUserManagement() {
        $("#dynamicContentContainer").html(`
            <div class="user-management-container">
                <h2>User Management</h2>
                <div class="user-controls">
                    <div class="search-container">
                        <i class="fas fa-search"></i>
                        <input type="text" id="userSearch" placeholder="Search users...">
                    </div>
                    <button id="addUserBtn" class="btn primary-btn">
                        <i class="fas fa-user-plus"></i> Add User
                    </button>
                </div>
                <div class="user-table-container">
                    <table class="user-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="5" class="loading">Loading users...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `).slideDown(300);

        // Simulate loading users
        setTimeout(() => {
            loadUsersData();
        }, 1000);
        
        // Add search handler
        $("#userSearch").on("input", function() {
            filterUsers($(this).val());
        });
        
        // Add new user handler
        $("#addUserBtn").click(showAddUserForm);
    }

    function loadUsersData() {
        const token = localStorage.getItem('token');
        
        fetch('/api/admin/users', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch users');
            }
            return response.json();
        })
        .then(users => {
            displayUsers(users);
        })
        .catch(error => {
            console.error('Error loading users:', error);
            $(".user-table tbody").html(`
                <tr>
                    <td colspan="5" class="error">
                        Failed to load users. Please try again later.
                    </td>
                </tr>
            `);
        });
    }

    function displayUsers(users) {
        let tableHTML = '';
        
        users.forEach(user => {
            tableHTML += `
                <tr data-user-id="${user.id}">
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td><span class="user-status ${user.status.toLowerCase()}">${user.status}</span></td>
                    <td>
                        <div class="user-actions">
                            <button class="action-btn edit-btn" data-user-id="${user.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn delete-btn" data-user-id="${user.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        $(".user-table tbody").html(tableHTML);
        
        // Add action handlers
        $(".edit-btn").click(function() {
            const userId = $(this).data('user-id');
            editUser(userId);
        });
        
        $(".delete-btn").click(function() {
            const userId = $(this).data('user-id');
            deleteUser(userId);
        });
    }

    function loadSystemSettings() {
        $("#dynamicContentContainer").html(`
            <div class="settings-container">
                <h2>System Settings</h2>
                
                <div class="setting-item">
                    <label class="setting-label">Maintenance Mode</label>
                    <div class="setting-control">
                        <label class="toggle-switch">
                            <input type="checkbox" id="maintenanceMode">
                            <span class="toggle-slider"></span>
                        </label>
                        <span>Enable maintenance mode</span>
                    </div>
                </div>
                
                <div class="setting-item">
                    <label class="setting-label">Exam Registration</label>
                    <div class="setting-control">
                        <label class="toggle-switch">
                            <input type="checkbox" id="examRegistration" checked>
                            <span class="toggle-slider"></span>
                        </label>
                        <span>Allow exam registration</span>
                    </div>
                </div>
                
                <div class="setting-item">
                    <label class="setting-label">Result Publishing</label>
                    <div class="setting-control">
                        <label class="toggle-switch">
                            <input type="checkbox" id="resultPublishing" checked>
                            <span class="toggle-slider"></span>
                        </label>
                        <span>Allow result publishing</span>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn reset-btn" id="resetSettings">
                        Reset to Defaults
                    </button>
                    <button type="button" class="btn primary-btn" id="saveSettings">
                        Save Settings
                    </button>
                </div>
            </div>
        `).slideDown(300);
        
        // Load current settings
        loadCurrentSettings();
        
        // Add handlers
        $("#saveSettings").click(saveSystemSettings);
        $("#resetSettings").click(resetSystemSettings);
    }

    function loadSystemLogs() {
        $("#dynamicContentContainer").html(`
            <div class="logs-container">
                <h2>System Logs</h2>
                <div class="log-controls">
                    <select id="logLevelFilter">
                        <option value="all">All Levels</option>
                        <option value="info">Info Only</option>
                        <option value="warning">Warnings</option>
                        <option value="error">Errors</option>
                    </select>
                    <button id="refreshLogs" class="btn primary-btn">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
                <div class="log-entries">
                    <div class="loading">Loading system logs...</div>
                </div>
            </div>
        `).slideDown(300);
        
        // Load logs
        setTimeout(() => {
            loadLogData();
        }, 800);
        
        // Add handlers
        $("#refreshLogs").click(loadLogData);
        $("#logLevelFilter").change(filterLogs);
    }

    function loadProfileForm() {
        $("#dynamicContentContainer").html(`
            <div class="profile-container">
                <h2>Update Your Profile</h2>
                <form id="adminProfileForm" class="profile-form">
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input type="text" id="fullName" name="fullName" placeholder="Full Name" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-envelope"></i>
                            <input type="email" id="email" name="email" placeholder="Email Address" required readonly>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-phone"></i>
                            <input type="tel" id="phoneNumber" name="phoneNumber" placeholder="Phone Number" pattern="[0-9]{10}" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="input-with-icon">
                            <i class="fas fa-id-card"></i>
                            <input type="text" id="adminId" name="adminId" placeholder="Admin ID" readonly>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn reset-btn" id="resetForm" style="display: none;">Reset Changes</button>
                        <button type="submit" class="btn primary-btn" id="saveChanges" disabled>Save Changes</button>
                    </div>
                </form>
                <div id="profileUpdateMessage" class="message-container"></div>
            </div>
        `).slideDown(300);

        loadProfileData();
        setupProfileFormHandlers();
    }

    function loadProfileData() {
        // Simulated API call
        setTimeout(() => {
            const dummyProfile = {
                fullName: "Admin User",
                email: "admin@university.edu",
                phoneNumber: "1234567890",
                adminId: "ADM-1001"
            };
            
            $("#fullName").val(dummyProfile.fullName);
            $("#email").val(dummyProfile.email);
            $("#phoneNumber").val(dummyProfile.phoneNumber);
            $("#adminId").val(dummyProfile.adminId);
            
            originalProfileData = {
                fullName: dummyProfile.fullName,
                phoneNumber: dummyProfile.phoneNumber
            };
            
            checkFormChanges();
        }, 500);
    }

    function setupProfileFormHandlers() {
        $("#adminProfileForm").on('input change', checkFormChanges);
        
        $("#resetForm").click(function() {
            $("#fullName").val(originalProfileData.fullName);
            $("#phoneNumber").val(originalProfileData.phoneNumber);
            checkFormChanges();
            $("#profileUpdateMessage").empty();
        });
        
        $("#adminProfileForm").submit(function(e) {
            e.preventDefault();
            updateProfile();
        });
    }

    function checkFormChanges() {
        const currentData = {
            fullName: $("#fullName").val(),
            phoneNumber: $("#phoneNumber").val()
        };

        const hasChanges = Object.keys(originalProfileData).some(
            key => originalProfileData[key] !== currentData[key]
        );
        
        $("#saveChanges").prop('disabled', !hasChanges);
        $("#resetForm").toggle(hasChanges);
    }

    function updateProfile() {
        const formData = {
            fullName: $("#fullName").val(),
            phoneNumber: $("#phoneNumber").val()
        };

        $("#saveChanges").prop('disabled', true);
        $("#profileUpdateMessage").html('<div class="info">Updating profile...</div>');

        // Simulate API call
        setTimeout(() => {
            $("#profileUpdateMessage").html('<div class="success">Profile updated successfully!</div>');
            originalProfileData = { ...formData };
            checkFormChanges();
        }, 1000);
    }

    // Utility functions
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Placeholder functions for future implementation
    function filterUsers(searchTerm) {
        const token = localStorage.getItem('token');
        
        fetch(`/api/admin/users/search?query=${encodeURIComponent(searchTerm)}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(users => {
            displayUsers(users);
        })
        .catch(error => {
            console.error('Error filtering users:', error);
        });
    }

    function showAddUserForm() {
        console.log("Showing add user form");
    }

    function editUser(userId) {
        const token = localStorage.getItem('token');
        
        fetch(`/api/admin/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(user => {
            showEditUserForm(user);
        })
        .catch(error => {
            console.error('Error fetching user details:', error);
        });
    }

    function deleteUser(userId) {
        if (confirm('Are you sure you want to delete this user?')) {
            const token = localStorage.getItem('token');
            
            fetch(`/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (response.ok) {
                    loadUsersData(); // Refresh the user list
                } else {
                    throw new Error('Failed to delete user');
                }
            })
            .catch(error => {
                console.error('Error deleting user:', error);
                alert('Failed to delete user. Please try again.');
            });
        }
    }

    function showEditUserForm(user) {
        const modal = $(`
            <div class="modal">
                <div class="modal-content">
                    <h3>Edit User</h3>
                    <form id="editUserForm">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" id="editFullName" value="${user.name}" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="editEmail" value="${user.email}" required>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select id="editStatus">
                                <option value="Active" ${user.status === 'Active' ? 'selected' : ''}>Active</option>
                                <option value="Inactive" ${user.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                            </select>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn cancel-btn" onclick="$(this).closest('.modal').remove()">Cancel</button>
                            <button type="submit" class="btn primary-btn">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        `);

        modal.find('#editUserForm').on('submit', function(e) {
            e.preventDefault();
            const token = localStorage.getItem('token');
            
            const updatedUser = {
                id: user.id,
                fullName: $('#editFullName').val(),
                email: $('#editEmail').val(),
                isActive: $('#editStatus').val() === 'Active'
            };

            fetch(`/api/admin/users/${user.id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedUser)
            })
            .then(response => {
                if (response.ok) {
                    modal.remove();
                    loadUsersData(); // Refresh the user list
                } else {
                    throw new Error('Failed to update user');
                }
            })
            .catch(error => {
                console.error('Error updating user:', error);
                alert('Failed to update user. Please try again.');
            });
        });

        $('body').append(modal);
    }

    function loadCurrentSettings() {
        console.log("Loading current system settings");
    }

    function saveSystemSettings() {
        console.log("Saving system settings");
    }

    function resetSystemSettings() {
        console.log("Resetting system settings to defaults");
    }

    function loadLogData() {
        console.log("Loading system logs");
    }

    function filterLogs() {
        console.log("Filtering system logs");
    }
});