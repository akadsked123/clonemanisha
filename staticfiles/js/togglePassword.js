document.addEventListener('DOMContentLoaded', function () {
  const password1 = document.getElementById('signup-password1');
  const password2 = document.getElementById('signup-password2');
  const togglePasswordCheckbox = document.getElementById('toggle-password');

  function togglePasswordVisibility() {
    const type = togglePasswordCheckbox.checked ? 'text' : 'password';
    password1.type = type;
    password2.type = type;
  }

  // Initialize the toggle functionality
  togglePasswordCheckbox.addEventListener('change', togglePasswordVisibility);

  // Set the initial visibility state
  togglePasswordVisibility();
});