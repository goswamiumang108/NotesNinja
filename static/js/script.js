// Get DOM elements
const pdfFileInput = document.getElementById('pdf-file');
const syllabusTextarea = document.getElementById('syllabus-topics');
const generateNotesButton = document.getElementById('generate-notes-button');
const loadingIndicator = document.createElement('i');
const downloadNotesButton = document.getElementById('download-generated-notes-button');
const formData = new FormData();

function submitFormData() {
	formData.append('pdf-file', pdfFileInput.files[0]);
	formData.append('syllabus-topics', syllabusTextarea.value);
	
	// Validate form values
	if (syllabusTextarea.value && pdfFileInput.files[0]) {
		generateNotesButton.disabled = true;
		generateNotesButton.textContent = 'Uploading...';
		generateNotesButton.appendChild(loadingIndicator);
		loadingIndicator.classList.add('fas', 'fa-spinner', 'fa-pulse')
		
		// Send form data to server
		fetch("/uploads", {method: 'POST', body: formData})
			.then(response => response.text()).then(data => {
			if (data === "success") {
				alert('Your PDF is successfully uploaded. Generating study notes...');
				
				generateNotesButton.textContent = 'Generating Your Notes...';
				generateNotesButton.appendChild(loadingIndicator);
				loadingIndicator.classList.add('fas', 'fa-spinner', 'fa-pulse')
				ProcessTheDocs()
			} else {
				alert(data);
			}
			
		}).catch(error => console.error(error));
	}
}


function ProcessTheDocs() {
	fetch("/process-docs", {method: 'POST'})
		.then(response => response.text())
		.then(data => {
				if (data === "success") {
					generateNotesButton.textContent = 'Notes Generated Successfully ==>';
					generateNotesButton.disabled = true;
					alert('Your PDF is successfully processed and notes are ready to be downloaded');
					downloadNotesButton.disabled = false;
				} else {
					alert(data);
				}
			}
		).catch(error => console.error(error));
}


function DownloadNotes() {
	window.open("/download-generated-notes", "_blank");
	window.open("./", "_self");
}