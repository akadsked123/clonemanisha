// Function to format phone number input
function formatPhoneNumber(input) {
  // Remove all non-digit characters
  let value = input.value.replace(/\D/g, '');

  // Format the value with hyphens
  if (value.length > 7) {
    value = value.slice(0, 4) + '-' + value.slice(4, 7) + '-' + value.slice(7);
  } else if (value.length > 4) {
    value = value.slice(0, 4) + '-' + value.slice(4);
  }

  // Set the formatted value back to the input
  input.value = value;

  // Validate the phone number
  validatePhoneNumber(input, false);
}

// Function to validate the phone number
function validatePhoneNumber(input, showSuccessMessage = true) {
  const phoneHelper = document.getElementById('phone-helper');
  const phoneValue = input.value.replace(/-/g, ''); // Remove hyphens
  const validLength = 11;

  // Reset styles and messages
  phoneHelper.classList.remove('text-red-600');
  phoneHelper.textContent = '';

  let isValid = true;

  // Check if phone number is valid
  if (phoneValue.length !== 0 && (phoneValue.length !== validLength || !phoneValue.startsWith('09'))) {
    phoneHelper.textContent = 'Phone number must be valid and 11 digits long.';
    phoneHelper.classList.add('text-red-600', 'mt-2');
    isValid = false;
  } else if (phoneValue.length !== 0 && showSuccessMessage) {
    // Add logic if needed
  }
  return isValid;
}

// Function to validate the email
function validateEmail(showSuccessMessage = true) {
  const emailInput = document.getElementById('email');
  const emailHelper = document.getElementById('email-helper');
  const emailValue = emailInput.value;
  const domain = '@dnsc.edu.ph';

  // Reset styles and messages
  emailHelper.classList.remove('text-red-600');
  emailHelper.textContent = '';

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  let isValid = true;

  if (emailValue === '') {
    emailHelper.textContent = 'Email cannot be blank.';
    emailHelper.classList.add('text-red-600', 'mt-2');
    isValid = false;
  } else if (!emailRegex.test(emailValue) || !emailValue.endsWith(domain)) {
    emailHelper.textContent = `Email must end with ${domain}.`;
    emailHelper.classList.add('text-red-600', 'mt-2');
    isValid = false;
  } else if (showSuccessMessage) {
    // add logic if needed
  }
  return isValid;
}

// Function to update the submit button state based on input validations
function updatePersonalInfoButtonState() {
  const firstNameInput = document.getElementById('first_name');
  const lastNameInput = document.getElementById('last_name');
  const emailInput = document.getElementById('email');
  const phoneInput = document.getElementById('phone_number');
  const personalInfoButton = document.getElementById('personalInfoButton');
  const fullNameHelper = document.getElementById('full-name-helper');

  const firstName = firstNameInput.value.trim();
  const lastName = lastNameInput.value.trim();
  const email = emailInput.value.trim();
  const isValidEmail = validateEmail(false);
  const isValidPhone = validatePhoneNumber(phoneInput, false);

  // Validate the name fields
  if (!firstName && !lastName) {
    fullNameHelper.textContent = 'First and last name cannot be blank.';
    fullNameHelper.classList.add('text-xs', 'mt-2', 'text-red-600');
  } else if (!firstName) {
    fullNameHelper.textContent = 'First name cannot be blank.';
    fullNameHelper.classList.add('text-xs', 'mt-2', 'text-red-600');
  } else if (!lastName) {
    fullNameHelper.textContent = 'Last name cannot be blank.';
    fullNameHelper.classList.add('text-xs', 'mt-2', 'text-red-600');
  } else {
    fullNameHelper.textContent = '';
    fullNameHelper.classList.remove('text-xs', 'mt-2', 'text-red-600');
  }

  // Enable/Disable button based on inputs
  personalInfoButton.disabled = !(firstName && lastName && isValidEmail && (phoneInput.value.trim() === '' || isValidPhone));
}

// Attach event listeners to input fields
document.addEventListener('DOMContentLoaded', function () {
  const firstNameInput = document.getElementById('first_name');
  const lastNameInput = document.getElementById('last_name');
  const emailInput = document.getElementById('email');
  const phoneInput = document.getElementById('phone_number');

  firstNameInput.addEventListener('input', updatePersonalInfoButtonState);
  lastNameInput.addEventListener('input', updatePersonalInfoButtonState);
  emailInput.addEventListener('input', updatePersonalInfoButtonState);
  phoneInput.addEventListener('input', function () {
    formatPhoneNumber(this);
    updatePersonalInfoButtonState();
  });

  // Initial validation
  updatePersonalInfoButtonState();
});

// Event listener for form submission
document.getElementById('personalInformation').addEventListener('submit', function (event) {
  const phoneInput = document.getElementById('phone_number');
  const phoneValue = phoneInput.value.trim();

  // Remove hyphens for final validation
  phoneInput.value = phoneValue.replace(/-/g, '');

  // Prevent form submission if phone number or email is invalid
  if (phoneValue !== '' && !validatePhoneNumber(phoneInput, false) || !validateEmail(false)) {
    event.preventDefault();
  }
});