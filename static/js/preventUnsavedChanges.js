document.addEventListener('DOMContentLoaded', function () {
  var isFormDirty = {};

  function markFormDirty(event) {
    isFormDirty[event.target.form.id] = true;
    console.log('Form marked as dirty:', event.target.form.id);
  }

  function resetFormDirty(event) {
    isFormDirty[event.target.id] = false;
    console.log('Form reset as clean:', event.target.id);
  }

  // Attach event listeners to all form elements
  document.querySelectorAll('form input, form textarea, form select').forEach(function (element) {
    element.addEventListener('change', markFormDirty);
    element.addEventListener('input', markFormDirty);
  });

  // Attach event listener to each form for reset on submit
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', resetFormDirty);
  });

  // Attach event listener to the window for beforeunload
  window.addEventListener('beforeunload', function (e) {
    for (var formId in isFormDirty) {
      if (isFormDirty[formId]) {
        console.log('Unsaved changes detected in form:', formId);
        e.preventDefault();  // Standard way to trigger the dialog
        e.returnValue = '';  // Required by some browsers to display the dialog
        break;
      }
    }
  });
});
