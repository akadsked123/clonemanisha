// This script is used to change the number of items displayed per page in the list of items.
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('items-per-page-form');
  if (!form) return;

  const select = form.querySelector('select[name="items_per_page"]');
  const currentPage = new URLSearchParams(window.location.search).get('page') || 1;

  select.addEventListener('change', function () {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', currentPage);
    urlParams.set('items_per_page', this.value);
    window.location.search = urlParams.toString();
  });
});
