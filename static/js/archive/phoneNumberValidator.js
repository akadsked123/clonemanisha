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
  const submitButton = document.getElementById('personalInfoButton');

  // Reset styles and messages
  input.classList.remove('border-red-500', 'ring-red-500', 'border-green-500', 'ring-green-500');
  input.classList.add('border-gray-300', 'ring-blue-500');
  phoneHelper.classList.remove('text-red-600', 'text-green-600');
  phoneHelper.textContent = '';

  let isValid = true;

  // Check if phone number is valid
  if (phoneValue.length !== 0 && (phoneValue.length !== validLength || !phoneValue.startsWith('09'))) {
    phoneHelper.textContent = 'Phone number must be valid and 11 digits long';
    phoneHelper.classList.add('text-red-600', 'mt-2');
    input.classList.add('border-red-500', 'ring-red-500');
    isValid = false;
  } else if (phoneValue.length !== 0 && showSuccessMessage) {
    phoneHelper.textContent = 'Looks good!';
    phoneHelper.classList.add('text-green-600', 'mt-2');
    input.classList.add('border-green-500', 'ring-green-500');
  }

  // Disable or enable the submit button based on the validity of the phone number
  submitButton.disabled = !isValid && phoneValue.length > 0;
  return isValid;
}

// Event listener for phone number input
document.getElementById('phone_number').addEventListener('input', function () {
  formatPhoneNumber(this);
  validatePhoneNumber(this, false);
});

// Event listener for form submission
document.getElementById('personalInformation').addEventListener('submit', function (event) {
  const phoneInput = document.getElementById('phone_number');
  const phoneValue = phoneInput.value.trim();

  // Remove hyphens for final validation
  phoneInput.value = phoneValue.replace(/-/g, '');

  // Prevent form submission if phone number is invalid
  if (phoneValue !== '' && !validatePhoneNumber(phoneInput, false)) {
    event.preventDefault();
  }
});