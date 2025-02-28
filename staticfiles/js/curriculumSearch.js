document.addEventListener('DOMContentLoaded', function () {
  // Initialize search for all tables
  const searchInput = document.getElementById('search-data');
  // Select all table bodies
  const tables = document.querySelectorAll('tbody[id^="table-body-"]');

  function filterTableBySearch() {
    const searchTerm = searchInput.value.toLowerCase().trim().replace(/\s+/g, '');

    tables.forEach(tableBody => {
      const rows = tableBody.querySelectorAll('tr:not([id^="no-results-row"]):not(.exclude-from-search)');
      let hasVisibleRows = false;

      rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        // Check if any cell matches the search term
        let matchesSearch = Array.from(cells).some(cell => {
          const cellText = cell.textContent.toLowerCase().replace(/\s+/g, '');
          return cellText.includes(searchTerm);
        });

        if (matchesSearch) {
          row.style.display = '';
          hasVisibleRows = true;
        } else {
          row.style.display = 'none';
        }
      });

      // Hide the Total Units row unconditionally during search
      const totalUnitsRow = tableBody.querySelector('.exclude-from-search');
      totalUnitsRow.style.display = 'none';

      // Show the "No Results Found" row based on visible rows
      const noResultsRow = tableBody.querySelector('[id^="no-results-row"]');
      if (hasVisibleRows) {
        noResultsRow.style.display = 'none';
      } else {
        noResultsRow.style.display = '';
        // Update the text content to reflect the search term
        const noResultsMessage = noResultsRow.querySelector('span');
        noResultsMessage.innerHTML = '"' + searchInput.value + '"';
      }
    });
  }
  searchInput.addEventListener('input', filterTableBySearch);
});