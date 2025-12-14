document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('.file-input');
    const dropArea = document.querySelector('.file-drop-area');
    const previewImage = document.querySelector('.preview-image');
    const calorieToggle = document.getElementById('calorie-toggle');
    const userForm = document.getElementById('user-form');
    const uploadForm = document.getElementById('upload-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Drag & Drop
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
            dropArea.addEventListener(e, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(e => {
            dropArea.addEventListener(e, () => dropArea.classList.add('is-active'), false);
        });

        ['dragleave', 'drop'].forEach(e => {
            dropArea.addEventListener(e, () => dropArea.classList.remove('is-active'), false);
        });

        dropArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (fileInput) {
                fileInput.files = files;
                handleFiles(files);
            }
        }, false);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    if (fileInput) {
        fileInput.addEventListener('change', function () {
            handleFiles(this.files);
        });
    }

    function handleFiles(files) {
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (previewImage) {
                    previewImage.src = e.target.result;
                    previewImage.classList.remove('hidden');
                    // Tailwind specific: handle placeholder visibility if needed
                    const placeholder = document.querySelector('.preview-placeholder');
                    if (placeholder) placeholder.classList.add('hidden');
                }
            }
            reader.readAsDataURL(files[0]);
        }
    }

    // Toggle Form
    if (calorieToggle) {
        calorieToggle.addEventListener('change', function () {
            if (this.checked) {
                userForm.style.display = 'block'; // Or remove hidden class
                userForm.classList.remove('hidden');
                document.querySelectorAll('.user-input').forEach(i => i.required = true);
            } else {
                userForm.style.display = 'none';
                userForm.classList.add('hidden');
                document.querySelectorAll('.user-input').forEach(i => i.required = false);
            }
        });
    }

    // Submit
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please upload an image.');
                return;
            }
            if (loadingOverlay) loadingOverlay.style.display = 'flex'; // Or remove hidden class
            if (loadingOverlay) loadingOverlay.classList.remove('hidden');
            if (loadingOverlay) loadingOverlay.classList.add('flex');
        });
    }
});
