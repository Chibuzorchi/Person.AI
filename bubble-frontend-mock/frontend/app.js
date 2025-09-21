// Person.ai Mock Frontend Application
class PersonAIApp {
    constructor() {
        this.currentUser = null;
        this.apiBaseUrl = 'http://localhost:5001/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Schedule briefing form
        document.getElementById('schedule-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleScheduleBriefing();
        });

        // Integration setup form
        document.getElementById('integration-setup-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleIntegrationSetup();
        });

        // Test connection button
        document.getElementById('test-connection-button').addEventListener('click', (e) => {
            e.preventDefault();
            this.handleTestConnection();
        });

        // Preferences form
        document.getElementById('preferences-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePreferencesUpdate();
        });
    }

    async checkAuthStatus() {
        // Check if user is already logged in
        const token = localStorage.getItem('auth_token');
        if (token) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/user/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    this.currentUser = await response.json();
                    this.showPage('dashboard-page');
                    return;
                }
            } catch (error) {
                console.log('Auth check failed:', error);
            }
        }
        
        this.showPage('login-page');
    }

    async handleLogin() {
        const email = document.getElementById('email-input').value;
        const password = document.getElementById('password-input').value;
        const errorDiv = document.getElementById('login-error');

        try {
            const response = await fetch(`${this.apiBaseUrl}/user/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('auth_token', data.session_token);
                this.currentUser = data.user;
                this.showPage('dashboard-page');
                errorDiv.style.display = 'none';
            } else {
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        }
    }

    async handleScheduleBriefing() {
        const formData = {
            title: document.getElementById('briefing-title').value,
            time: document.getElementById('time-select').value,
            frequency: document.getElementById('frequency-select').value,
            channels: []
        };

        // Get selected channels
        if (document.getElementById('slack-channel').checked) {
            formData.channels.push('slack');
        }
        if (document.getElementById('email-channel').checked) {
            formData.channels.push('email');
        }
        if (document.getElementById('sms-channel').checked) {
            formData.channels.push('sms');
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/briefings/schedule`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccessMessage('success-message', 'Briefing scheduled successfully!');
                // Reset form
                document.getElementById('schedule-form').reset();
            } else {
                this.showErrorMessage('Error scheduling briefing: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    async handleIntegrationSetup() {
        const integrationType = this.currentIntegrationType;
        const formData = {};

        if (integrationType === 'slack') {
            formData.webhook_url = document.getElementById('webhook-url').value;
            formData.channel = document.getElementById('channel-name').value;
        } else if (integrationType === 'email') {
            formData.smtp_server = document.getElementById('smtp-server').value;
            formData.smtp_port = document.getElementById('smtp-port').value;
            formData.email_address = document.getElementById('email-address').value;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/integrations/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    integration_type: integrationType,
                    config: formData
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccessMessage('success-message', 'Integration configured successfully!');
                this.closeIntegrationModal();
            } else {
                this.showErrorMessage('Error configuring integration: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    async handleTestConnection() {
        const integrationType = this.currentIntegrationType;
        const formData = {};

        if (integrationType === 'slack') {
            formData.webhook_url = document.getElementById('webhook-url').value;
            formData.channel = document.getElementById('channel-name').value;
        } else if (integrationType === 'email') {
            formData.smtp_server = document.getElementById('smtp-server').value;
            formData.smtp_port = document.getElementById('smtp-port').value;
            formData.email_address = document.getElementById('email-address').value;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/integrations/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    integration_type: integrationType,
                    config: formData
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showTestResult('Connection successful!');
            } else {
                this.showTestResult('Connection failed: ' + (data.error || 'Unknown error'), false);
            }
        } catch (error) {
            this.showTestResult('Network error. Please try again.', false);
        }
    }

    async handlePreferencesUpdate() {
        const preferences = {
            slack_notifications: document.getElementById('slack-notifications-toggle').checked,
            email_notifications: document.getElementById('email-notifications-toggle').checked,
            sms_notifications: document.getElementById('sms-notifications-toggle').checked
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/user/preferences`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(preferences)
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccessMessage('preferences-success-message', 'Preferences saved successfully!');
            } else {
                this.showErrorMessage('Error saving preferences: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Update page content
        document.querySelectorAll('.page-content').forEach(content => {
            content.classList.remove('active');
        });

        if (pageId === 'login-page') {
            // Show login page
            document.getElementById('login-page').classList.add('active');
        } else if (pageId === 'dashboard' || pageId === 'dashboard-page') {
            // Show dashboard page (main container)
            document.getElementById('dashboard-page').classList.add('active');
            document.querySelector('[onclick="showPage(\'dashboard\')"]').classList.add('active');
            document.getElementById('dashboard-content').classList.add('active');
        } else if (pageId === 'briefings' || pageId === 'briefings-page') {
            // Show dashboard page with briefings content
            document.getElementById('dashboard-page').classList.add('active');
            document.querySelector('[onclick="showPage(\'briefings\')"]').classList.add('active');
            document.getElementById('briefings-content').classList.add('active');
        } else if (pageId === 'schedule-briefing') {
            // Show dashboard page with schedule briefing content
            document.getElementById('dashboard-page').classList.add('active');
            document.getElementById('schedule-briefing-content').classList.add('active');
        } else if (pageId === 'integrations' || pageId === 'integrations-page') {
            // Show dashboard page with integrations content
            document.getElementById('dashboard-page').classList.add('active');
            document.querySelector('[onclick="showPage(\'integrations\')"]').classList.add('active');
            document.getElementById('integrations-content').classList.add('active');
        } else if (pageId === 'settings' || pageId === 'settings-page') {
            // Show dashboard page with settings content
            document.getElementById('dashboard-page').classList.add('active');
            document.querySelector('[onclick="showPage(\'settings\')"]').classList.add('active');
            document.getElementById('settings-content').classList.add('active');
        }
    }

    setupIntegration(integrationType) {
        this.currentIntegrationType = integrationType;
        
        // Update modal title
        document.getElementById('integration-modal-title').textContent = `Setup ${integrationType.charAt(0).toUpperCase() + integrationType.slice(1)} Integration`;
        
        // Show/hide relevant setup forms
        document.querySelectorAll('.integration-setup').forEach(form => {
            form.style.display = 'none';
        });
        
        if (integrationType === 'slack') {
            document.getElementById('slack-setup').style.display = 'block';
        } else if (integrationType === 'email') {
            document.getElementById('email-setup').style.display = 'block';
        }
        
        // Show modal
        document.getElementById('integration-setup-modal').classList.add('active');
    }

    closeIntegrationModal() {
        document.getElementById('integration-setup-modal').classList.remove('active');
        // Reset form
        document.getElementById('integration-setup-form').reset();
        document.getElementById('connection-test-result').style.display = 'none';
    }

    showSuccessMessage(elementId, message) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.style.display = 'block';
        
        // Hide after 3 seconds
        setTimeout(() => {
            element.style.display = 'none';
        }, 3000);
    }

    showErrorMessage(message) {
        const errorDiv = document.getElementById('login-error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    showTestResult(message, success = true) {
        const resultDiv = document.getElementById('connection-test-result');
        resultDiv.textContent = message;
        resultDiv.style.display = 'block';
        
        if (success) {
            resultDiv.className = 'test-result';
        } else {
            resultDiv.className = 'test-result error';
        }
        
        // Hide after 5 seconds
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 5000);
    }
}

// Global functions for HTML onclick handlers
function showPage(pageId) {
    if (window.app) {
        window.app.showPage(pageId);
    }
}

function setupIntegration(integrationType) {
    if (window.app) {
        window.app.setupIntegration(integrationType);
    }
}

function closeIntegrationModal() {
    if (window.app) {
        window.app.closeIntegrationModal();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PersonAIApp();
});

// Add data-testid attributes dynamically for better testing
document.addEventListener('DOMContentLoaded', () => {
    // Add test IDs to elements that don't have them
    const elementsToTag = [
        { selector: '.dashboard-card:first-child', testId: 'dashboard' },
        { selector: '.briefings-list', testId: 'briefings-list' },
        { selector: '.integrations-list', testId: 'integrations-list' }
    ];

    elementsToTag.forEach(({ selector, testId }) => {
        const element = document.querySelector(selector);
        if (element && !element.getAttribute('data-testid')) {
            element.setAttribute('data-testid', testId);
        }
    });
});
