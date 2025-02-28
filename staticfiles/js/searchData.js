// This file contains the JavaScript code to filter a table based on a search input.
document.addEventListener('DOMContentLoaded', function () {
  function initializeSearch(searchInputId, tableBodyId, columnsToSearch, noResultsMessageId, noResultsRowId) {
    const searchInput = document.getElementById(searchInputId);
    const tableBody = document.getElementById(tableBodyId);
    const noDataMessage = document.getElementById(noResultsMessageId);

    function filterTableBySearch() {
      const searchTerm = searchInput.value;
      const searchTermNoSpaces = searchTerm.replace(/\s+/g, '').toLowerCase();

      const rows = tableBody.querySelectorAll(`tr:not(#${noResultsRowId})`);
      let hasVisibleRows = false;
      let noResultsForSearch = true;

      rows.forEach(row => {
        let matchesSearch = false;

        // Iterate over the custom columns passed to the function
        columnsToSearch.forEach(columnIndex => {
          const cellText = row.cells[columnIndex].textContent;
          const cellTextNoSpaces = cellText.replace(/\s+/g, '').toLowerCase();

          if (cellTextNoSpaces.includes(searchTermNoSpaces)) {
            matchesSearch = true;
          }
        });

        if (matchesSearch) {
          row.style.display = '';
          hasVisibleRows = true;
          noResultsForSearch = false;
        } else {
          row.style.display = 'none';
        }
      });

      if (noResultsForSearch) {
        noDataMessage.innerHTML = `No results found for <strong>"${searchTerm}"</strong>`;
      } else {
        noDataMessage.textContent = '';
      }

      document.getElementById(noResultsRowId).style.display = hasVisibleRows ? 'none' : '';
    }

    searchInput.addEventListener('input', filterTableBySearch);
  }

  window.initializeSearch = initializeSearch;
});

