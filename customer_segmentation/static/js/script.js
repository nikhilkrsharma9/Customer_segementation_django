document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here
    console.log('Customer Segmentation Tool loaded');
    
    // Example: Add a file name display when a file is selected
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0].name;
            const label = fileInput.nextElementSibling;
            if (label && label.classList.contains('form-text')) {
                label.textContent = `Selected file: ${fileName}`;
            }
        });
    }
});