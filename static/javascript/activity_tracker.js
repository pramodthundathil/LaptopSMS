// static/js/activity_tracker.js

let activityTimeout;
const timeoutDuration = 15 * 60 * 10000; // 15 minutes in milliseconds

function resetActivityTimeout() {
    clearTimeout(activityTimeout);
    activityTimeout = setTimeout(logoutUser, timeoutDuration);
}

function logoutUser() {
    window.location.href = '/logout/';
}

function sendKeepAlive() {
    fetch('/keep-alive/', {
        method: 'GET',
        credentials: 'same-origin'
    }).then(response => {
        if (response.status === 200) {
            resetActivityTimeout();
        }
    });
}

// Event listeners to reset the timer on user activity
window.onload = resetActivityTimeout;
document.onmousemove = resetActivityTimeout;
document.onkeypress = resetActivityTimeout;
document.onscroll = resetActivityTimeout;
document.onclick = resetActivityTimeout;
document.onkeydown = resetActivityTimeout;

// Periodically send keep-alive requests to the server
setInterval(sendKeepAlive, 5 * 60 * 1000); // Every 5 minutes
