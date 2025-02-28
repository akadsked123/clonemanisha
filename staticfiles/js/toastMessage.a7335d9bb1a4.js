const parent = document.getElementById('toast-container');
const tpl = document.getElementById('toast-template').content.firstElementChild;

function showToast(message, { delay = 10000, colorClass = '', iconClass = '' } = {}) {
  let toast = tpl.cloneNode(true);
  toast.querySelector('.toast-message').textContent = message;

  // Apply the color class dynamically
  if (colorClass) {
    toast.classList.add(colorClass);
  }

  // Mapping of icon classes to SVG icons
  const iconClasses = {
    'error': '<svg class="shrink-0 size-4 mt-0.5" fill="currentColor" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path></svg>',
    'info': '<svg class="toast-icon shrink-0 size-4 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"></path></svg>',
    'success': '<svg class="shrink-0 size-4 mt-0.5" fill="currentColor" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"></path></svg>',
    'warning': '<svg class="shrink-0 size-4 mt-0.5" fill="currentColor" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"></path></svg>'
  };

  // Apply the icon class dynamically
  if (iconClass) {
    toast.querySelector('.toast-icon-container').innerHTML = iconClasses[iconClass] || iconClasses['info'];
  }

  // Add to the container
  parent.appendChild(toast);

  // Trigger reflow to ensure transition happens
  requestAnimationFrame(() => {
    toast.classList.remove('opacity-0', 'translate-y-4');
    toast.classList.add('opacity-100', 'translate-y-0');
  });

  // Animate the toast exit after a delay
  setTimeout(() => {
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-4');
    toast.addEventListener('transitionend', () => {
      toast.remove();
    });
  }, delay);
}

function hideToast(button) {
  const toast = button.closest('.max-w-xs');
  if (toast) {
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-4');
    toast.addEventListener('transitionend', () => {
      toast.remove();
    });
  }
}