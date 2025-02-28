
// Get current year
document.addEventListener('DOMContentLoaded', function () {
  var currentYear = new Date().getFullYear();
  document.getElementById('current-year').textContent = currentYear;
});

// Store the scroll position
window.addEventListener('beforeunload', () => {
  sessionStorage.setItem('scrollPosition', window.scrollY);
});

// Restore the scroll position
window.addEventListener('load', () => {
  const scrollPosition = sessionStorage.getItem('scrollPosition');
  if (scrollPosition !== null) {
    window.scrollTo(0, parseInt(scrollPosition, 10));
    // Remove the stored position after restoring to avoid applying it on subsequent reloads
    sessionStorage.removeItem('scrollPosition');
  }
});
