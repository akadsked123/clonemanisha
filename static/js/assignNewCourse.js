document.addEventListener("DOMContentLoaded", function () {
  const courseListContainer = document.getElementById('course-list-container');
  const searchInput = document.getElementById('search-courses');
  const removeAllButton = document.getElementById('remove-all-courses');
  const courseList = document.getElementById('course-list');
  const noCourseMessage = document.getElementById('no-course-message');

  // Track selected courses
  let selectedCourses = new Set();

  function fetchAllCourses(resultId, programId) {
    const cachedCourses = localStorage.getItem(`courses_${resultId}`);
    if (cachedCourses) {
      renderCourses(JSON.parse(cachedCourses));
    } else {
      const url = `/api/v2/courses/${resultId}/${programId}/`;
      console.log(url)
      fetch(url)
        .then(response => response.json())
        .then(data => {
          localStorage.setItem(`courses_${resultId}`, JSON.stringify(data.courses));
          renderCourses(data.courses);
        })
        .catch(error => console.error('Error fetching all courses:', error));
    }
  }

  function renderCourses(courses) {
    courseList.innerHTML = '';

    if (courses.length > 0) {
      courses.forEach(course => {
        const courseElement = createCourseElement(course);
        courseList.appendChild(courseElement);
      });
      updateCourseElements();
    } else {
      courseList.innerHTML = '<p>No courses available.</p>';
    }

    updateSelectedCourses();
  }

  function createCourseElement(course) {
    const isSelected = selectedCourses.has(course.course_id);
    const courseElement = document.createElement('div');
    courseElement.classList.add('course-item', 'py-2', 'px-4', 'w-full', 'text-sm', 'text-gray-800', 'cursor-pointer', 'hover:bg-gray-100', 'rounded-lg', 'flex', 'items-center', 'relative');
    courseElement.innerHTML = `
      <div class="flex items-center w-full">
        <div class="course_description flex-1 text-sm text-gray-800">
          <p>${course.course_code}&nbsp-&nbsp${course.course_description}</p>
        </div>
        <input type="hidden" name="course_id" value="${course.course_id}">
        <div class="check-icon ${isSelected ? '' : 'hidden'}">
          <svg class="shrink-0 size-4 text-primary-600" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z" />
          </svg>
        </div>
      </div>
    `;

    courseElement.addEventListener('click', () => {
      const courseId = course.course_id;
      if (selectedCourses.has(courseId)) {
        selectedCourses.delete(courseId);
      } else {
        selectedCourses.add(courseId);
      }
      updateSelectedCourses();
      updateCourseElements();
    });

    return courseElement;
  }

  function updateSelectedCourses() {
    courseListContainer.innerHTML = '';

    if (selectedCourses.size > 0) {
      selectedCourses.forEach(courseId => {
        const courseElement = Array.from(courseList.children).find(el => {
          const idElement = el.querySelector('input[name="course_id"]');
          return idElement && parseInt(idElement.value, 10) === courseId;
        });

        if (courseElement) {
          const courseDescription = courseElement.querySelector('.course_description').textContent.trim();
          const selectedItem = document.createElement('div');
          selectedItem.classList.add('inline-flex', 'items-center', 'bg-white', 'border', 'border-gray-200', 'rounded-full', 'p-1.5', 'max-h-full', 'me-2', 'mb-2');
          selectedItem.innerHTML = `
            <input type="hidden" required name="selected_course_id" value="${courseId}">
            <div class="px-2 whitespace-nowrap text-sm font-medium text-gray-800">
                ${courseDescription}
            </div>
            <div class="remove-item ms-2.5 inline-flex justify-center items-center size-5 rounded-full text-gray-800 bg-gray-200 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 cursor-pointer" data-value="${courseId}">
                <svg class="shrink-0 size-3" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6 6 18"></path>
                    <path d="m6 6 12 12"></path>
                </svg>
            </div>
          `;

          selectedItem.querySelector('.remove-item').addEventListener('click', (event) => {
            event.stopImmediatePropagation();
            selectedCourses.delete(courseId);
            updateSelectedCourses();
            updateCourseElements();
          });

          courseListContainer.appendChild(selectedItem);
        }
      });

      courseListContainer.style.display = 'block';
      noCourseMessage.style.display = 'none';
    } else {
      courseListContainer.style.display = 'none';
      noCourseMessage.style.display = 'flex';
    }

    updateButtonStates();
  }

  function updateCourseElements() {
    courseList.querySelectorAll('.course-item').forEach(courseElement => {
      const courseId = parseInt(courseElement.querySelector('input[name="course_id"]').value, 10);
      const checkIcon = courseElement.querySelector('.check-icon');
      if (checkIcon) {
        checkIcon.classList.toggle('hidden', !selectedCourses.has(courseId));
      }
    });
  }

  function updateButtonStates() {
    const selectedCount = selectedCourses.size;
    const removeAllDesign = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dash" viewBox="0 0 16 16">
        <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8" />
      </svg> Remove all (${selectedCount})
    `;

    if (selectedCount > 0) {
      removeAllButton.innerHTML = removeAllDesign;
      removeAllButton.disabled = false;
    } else {
      removeAllButton.innerHTML = removeAllDesign.replace(/(\(\d+\))/, '');
      removeAllButton.disabled = true;
    }
  }

  // Search functionality
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.toLowerCase().replace(/\s+/g, '');
    let hasResults = false;

    // Remove any existing "No results" message
    const existingMessage = document.getElementById('no-results-course');
    if (existingMessage) {
      existingMessage.remove();
    }

    // Filter course list based on query
    courseList.querySelectorAll('.course-item').forEach(courseElement => {
      const text = courseElement.textContent.toLowerCase().replace(/\s+/g, '');
      if (text.includes(query)) {
        courseElement.style.display = '';
        hasResults = true;
      } else {
        courseElement.style.display = 'none';
      }
    });

    // If no results found, display the "No results" message
    if (!hasResults) {
      const noResultsMessage = document.createElement('div');
      noResultsMessage.id = 'no-results-course';
      noResultsMessage.classList.add('flex', 'items-center', 'bg-white', 'h-72', 'flex-col', 'justify-center', 'p-4', 'md:p-5');
      noResultsMessage.innerHTML = `
        <p class="text-sm text-gray-800">
            No results for <span class="font-bold text-black">"${searchInput.value}"</span>
        </p>
      `;
      courseList.appendChild(noResultsMessage);
    }
  });

  // Remove all button functionality
  removeAllButton.addEventListener('click', () => {
    selectedCourses.clear();
    updateSelectedCourses();
    updateCourseElements();
  });

  // Fetch and render all courses immediately
  const resultId = document.querySelector('.assignCourseButton').getAttribute('data-result-identification');
  const programId = document.querySelector('.assignCourseButton').getAttribute('data-user-program');
  fetchAllCourses(resultId, programId);
});