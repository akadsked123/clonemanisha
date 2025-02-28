document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('delSessionModal');
  const sessionKeyInput = document.getElementById('sessionKeyInput');

  // Open modal and set session key
  document.querySelectorAll('button[data-hs-overlay="#delSessionModal"]').forEach(button => {
    button.addEventListener('click', function () {
      sessionKeyInput.value = this.getAttribute('data-session-key');
      modal.classList.remove('hidden');
    });
  });
});

