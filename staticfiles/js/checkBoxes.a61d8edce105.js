function initializeCheckboxLogic(config) {
  const selectAllCheckbox = document.getElementById(config.selectAllId);
  const checkboxes = document.querySelectorAll(config.checkboxClass);
  const selectedCountSpan1 = document.getElementById(config.selectedCountId1);
  const selectedCountSpan2 = document.getElementById(config.selectedCountId2);
  const selectedCountSpan3 = document.getElementById(config.selectedCountId3);
  const selectedCountSpan4 = document.getElementById(config.selectedCountId4);
  const deleteButton = document.getElementById(config.deleteButtonId);
  const copyInstructorButton = document.getElementById("copy-instructor-button");

  function updateSelectAllCheckbox() {
    const checkedCheckboxes = document.querySelectorAll(`${config.checkboxClass}:checked`);
    const visibleCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.closest('tr').style.display !== 'none');
    selectAllCheckbox.checked = visibleCheckboxes.length === checkedCheckboxes.length;
    updateSelectedCount();
  }

  function updateSelectedCount() {
    const checkedCheckboxes = document.querySelectorAll(`${config.checkboxClass}:checked`);
    const count = checkedCheckboxes.length;
    deleteButton.disabled = count === 0;
    copyInstructorButton.disabled = count === 0; // Disable the button if no checkboxes are selected
    const countText = count > 0 ? `(${count})` : "";

    // Update the selected count in multiple locations
    selectedCountSpan1.textContent = countText;
    selectedCountSpan2.textContent = countText;
    selectedCountSpan3.textContent = countText;
    selectedCountSpan4.textContent = count;
  }

  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener("change", function () {
      const visibleCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.closest('tr').style.display !== 'none');
      visibleCheckboxes.forEach((checkbox) => {
        checkbox.checked = this.checked;
      });
      updateSelectedCount();
    });
  }

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateSelectAllCheckbox);
  });

  function handleDeletion() {
    const selectedItems = Array.from(checkboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    if (selectedItems.length > 0) {
      const classroomIdsInput = document.getElementById(config.classroomIdsInputId);
      classroomIdsInput.value = selectedItems.join(",");
    }
  }

  deleteButton.addEventListener("click", handleDeletion);

  // Disable delete button if there are no checkboxes
  if (checkboxes.length === 0) {
    deleteButton.disabled = true;
  }

  updateSelectedCount();
}
