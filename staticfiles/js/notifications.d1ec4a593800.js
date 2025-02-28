document.addEventListener('DOMContentLoaded', function () {

  function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds === 0) seconds = 1;
    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) return `${interval} year${interval > 1 ? 's' : ''} ago`;
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) return `${interval} month${interval > 1 ? 's' : ''} ago`;
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) return `${interval} day${interval > 1 ? 's' : ''} ago`;
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return `${interval} hour${interval > 1 ? 's' : ''} ago`;
    interval = Math.floor(seconds / 60);
    if (interval >= 1) return `${interval} minute${interval > 1 ? 's' : ''} ago`;

    return `${seconds} second${seconds !== 1 ? 's' : ''} ago`;
  }

  function updateTimeAgo() {
    const timeElements = document.querySelectorAll('.time-ago');
    timeElements.forEach(el => {
      const date = el.getAttribute('data-time');
      el.innerText = timeAgo(date);
    });
  }

  function fetchNotifications() {
    fetch('/api/notifications/?limit=10')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        const notificationsContainer = document.getElementById('notificationsContainer');
        const notificationCount = document.getElementById('notification_count');
        const totalUnreadElement = document.getElementById('total_unread');

        notificationsContainer.innerHTML = '';

        if (data.total_unread === 0) {
          // Hide notification count if there are no unread notifications
          notificationCount.style.display = 'none';
        } else {
          notificationCount.style.display = 'block';
          totalUnreadElement.innerText = data.total_unread;
        }

        if (data.notifications.length === 0) {
          // Display message if there are no notifications
          notificationsContainer.innerHTML = `
            <div class="flex flex-auto flex-col justify-center items-center p-4 md:p-5">
              <svg xmlns="http://www.w3.org/2000/svg" class="size-10 text-gray-500 bi bi-bell-slash" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5.164 14H15c-.299-.199-.557-.553-.78-1-.9-1.8-1.22-5.12-1.22-6q0-.396-.06-.776l-.938.938c.02.708.157 2.154.457 3.58.161.767.377 1.566.663 2.258H6.164zm5.581-9.91a4 4 0 0 0-1.948-1.01L8 2.917l-.797.161A4 4 0 0 0 4 7c0 .628-.134 2.197-.459 3.742q-.075.358-.166.718l-1.653 1.653q.03-.055.059-.113C2.679 11.2 3 7.88 3 7c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0c.942.19 1.788.645 2.457 1.284zM10 15a2 2 0 1 1-4 0zm-9.375.625a.53.53 0 0 0 .75.75l14.75-14.75a.53.53 0 0 0-.75-.75z" />
              </svg>
              <p class="mt-2 text-sm text-gray-800">No notifications</p>
            </div>
          `;
        } else {
          data.notifications.forEach((notification, index) => {
            const notificationElement = document.createElement('a');
            notificationElement.className = 'p-3 flex gap-x-4 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 rounded-lg';
            notificationElement.href = notification.notification_url;

            const senderFirstName = notification.sender.first_name;
            const senderMiddleName = notification.sender.middle_name;
            const senderLastName = notification.sender.last_name;
            const profileImage = notification.sender.profile_image;

            const avatarUrl = profileImage || `https://ui-avatars.com/api/?name=${senderFirstName.replace(/\s+/g, '')}${senderMiddleName ? senderMiddleName.replace(/\s+/g, '') : ''}${senderLastName.replace(/\s+/g, '')}&background=random`;

            notificationElement.innerHTML = `
              <div class="flex items-start gap-x-3">
                <img class="inline-block flex-shrink-0 size-[38px] rounded-full" src="${avatarUrl}" 
                 alt="${senderFirstName} ${senderMiddleName || ''} ${senderLastName}">
                 <div class="grow">
                  <div class="flex items-center">
                    ${notification.is_read === false ? '<span class="max-w-40 truncate whitespace-nowrap inline-block py-1.5 px-3 rounded-lg text-xs font-medium bg-blue-100 text-blue-800 me-2">Unread</span>' : ''}
                    <span class="block text-xs text-gray-500 time-ago" data-time="${notification.created_at}">${timeAgo(notification.created_at)}</span>
                  </div>
                  <span class="block text-sm font-semibold text-gray-800 uppercase">
                    ${senderFirstName} ${senderMiddleName ? senderMiddleName + ' ' : ''}${senderLastName}
                  </span>
                  <span class="block text-sm text-gray-500">${notification.message || 'No message available'}</span>
                </div>
              </div>
            `;

            notificationsContainer.appendChild(notificationElement);

            // Add line divider if there is more than one notification
            if (data.notifications.length > 1 && index < data.notifications.length - 1) {
              const divider = document.createElement('div');
              divider.className = 'my-2 border-t border-gray-100';
              notificationsContainer.appendChild(divider);
            }
          });
        }
        updateTimeAgo();
      })
      .catch(error => console.error('There was a problem with the fetch operation:', error));
  }

  updateTimeAgo();
  setInterval(updateTimeAgo, 60000);
  fetchNotifications();
  setInterval(fetchNotifications, 60000);
});