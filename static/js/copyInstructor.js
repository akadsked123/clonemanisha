function insertSelectedInstructorIds(form, checkboxClass) {
  const checkboxes = document.querySelectorAll(checkboxClass);
  const selectedInstructorIds = Array.from(checkboxes)
    .filter(checkbox => checkbox.checked)
    .map(checkbox => checkbox.value);

  // Clear existing hidden inputs
  const existingInputs = form.querySelectorAll('input[name="selected_instructors[]"]');
  existingInputs.forEach(input => input.remove());

  // Create new hidden inputs for each selected instructor ID
  selectedInstructorIds.forEach(memberId => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'selected_instructors[]';
    input.value = memberId;
    form.appendChild(input);
  });
}

// Attach the form submission logic
document.getElementById('copy-instructor-form').addEventListener('submit', function (event) {
  insertSelectedInstructorIds(this, '.instructor-checkbox'); // Pass the form and checkbox class
});
