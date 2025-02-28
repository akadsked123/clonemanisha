document.addEventListener('DOMContentLoaded', function () {
  const currentUrl = window.location.pathname;

  // Function to normalize URL by removing query parameters
  function normalizeUrl(url) {
    return url.split('?')[0];
  }

  const sidebarLinks = document.querySelectorAll('#sidebar a');

  // Highlight the sidebar link based on the current URL
  sidebarLinks.forEach(link => {
    const linkHref = normalizeUrl(link.getAttribute('href'));

    // Check if the current URL matches the link's href
    if (normalizeUrl(currentUrl) === linkHref || normalizeUrl(currentUrl).startsWith(linkHref)) {
      link.classList.add('bg-gray-200');
    } else {
      link.classList.remove('bg-gray-200');
    }
  });

  // Open accordion based on the current URL
  const accordionItems = document.querySelectorAll('.hs-accordion');

  accordionItems.forEach(item => {
    const links = item.querySelectorAll('a');
    const button = item.querySelector('.hs-accordion-toggle');
    const content = item.querySelector('.hs-accordion-content');
    let matchFound = false;

    links.forEach(link => {
      const linkHref = normalizeUrl(link.getAttribute('href'));

      // Check if the current URL matches any link's href within the accordion item
      if (normalizeUrl(currentUrl) === linkHref || normalizeUrl(currentUrl).startsWith(linkHref)) {
        matchFound = true;
      }
    });

    if (button && content) {
      if (matchFound) {
        // Open the accordion item
        button.setAttribute('aria-expanded', 'true');
        content.classList.remove('hidden');
      } else {
        // Ensure it's closed if it doesn't match
        button.setAttribute('aria-expanded', 'false');
        content.classList.add('hidden');
      }
    }
  });

  // Restore scroll position
  const scrollPosition = localStorage.getItem('scrollPosition');
  if (scrollPosition) {
    window.scrollTo(0, parseInt(scrollPosition, 10));
  }

  // Save scroll position before the page unloads
  window.addEventListener('beforeunload', function () {
    localStorage.setItem('scrollPosition', window.scrollY);
  });
});