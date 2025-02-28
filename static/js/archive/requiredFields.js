document.getElementById('save_to_draft').addEventListener('click', function () {
  const formData = gatherFormData();

  const day = formData.day || '';
  const classGroupId = formData.classGroupId !== 'Select class group' ? formData.classGroupId : '';
  const startTime = formData.startTime !== 'Start time' ? formData.startTime : '';
  const endTime = formData.endTime !== 'End time' ? formData.endTime : '';
  const classroomId = formData.classroomId !== 'Select classroom' ? formData.classroomId : '';

  const modalTrigger = document.querySelector('[data-hs-overlay="#required-fields-modal"]');
  const requiredFieldsInfo = document.getElementById('required-fields-info');

  let message = '';

  if (!classGroupId) {
    message = 'Please select a class group.';
  } else if (!classroomId && !formData.isOnlineMeeting) {
    message = 'Please select a classroom.';
  } else if (!day) {
    message = 'Please select a day.';
  } else if (!startTime) {
    message = 'Please select a start time.';
  } else if (!endTime) {
    message = 'Please select an end time.';
  }

  if (message) {
    if (requiredFieldsInfo) {
      requiredFieldsInfo.textContent = message;
    }
    if (modalTrigger) {
      modalTrigger.click();
    }
    return;
  }

  displayDraftSchedule(formData);
});