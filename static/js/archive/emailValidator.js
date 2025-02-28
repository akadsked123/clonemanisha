function validateEmail(showSuccessMessage = true) {
  const emailInput = document.getElementById('email');
  const emailHelper = document.getElementById('email-helper');
  const emailValue = emailInput.value;
  const domain = '@dnsc.edu.ph';

  emailInput.classList.remove('focus:border-red-500', 'focus:ring-red-500', 'focus:border-green-500', 'focus:ring-green-500');
  emailInput.classList.add('focus:border-gray-300', 'focus:ring-gray-500');
  emailHelper.classList.remove('text-red-600', 'text-green-600');
  emailHelper.textContent = '';

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (emailValue === '') {
    emailInput.classList.add('focus:border-red-500', 'focus:ring-red-500');
    emailHelper.textContent = 'Email cannot be blank';
    emailHelper.classList.add('text-red-600', 'mt-2');
    return false;
  } else if (!emailRegex.test(emailValue) || !emailValue.endsWith(domain)) {
    emailInput.classList.add('focus:border-red-500', 'focus:ring-red-500');
    emailHelper.textContent = `Email must end with ${domain}`;
    emailHelper.classList.add('text-red-600', 'mt-2');
    return false;
  } else if (showSuccessMessage) {
    emailInput.classList.add('focus:border-green-500', 'focus:ring-green-500');
    emailHelper.textContent = 'Looks good!';
    emailHelper.classList.add('text-green-600', 'mt-2');
    return true;
  } else {
    return true;
  }
}

document.getElementById('email').addEventListener('input', function () {
  validateEmail();
});
document.getElementById('personalInformation').addEventListener('submit', function (event) {
  if (!validateEmail(false)) {
    event.preventDefault();
  }
});
