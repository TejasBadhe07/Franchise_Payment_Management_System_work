function logoutUser() {
    fetch('/logout', {
        method: 'POST', // Match the backend route method
        credentials: 'include', // Include cookies for session handling
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // Redirect to the login page after successful logout
            window.location.href = '/';
        } else {
            alert('Logout failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
    });
}
