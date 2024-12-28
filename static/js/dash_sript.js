document.addEventListener("DOMContentLoaded", function () {
    // Add event listeners to export links
    const exportLinks = document.querySelectorAll('.export-link');

    exportLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent the default behavior to manage loading state

            // Change link text to show loading
            link.innerHTML = 'Loading...';
            link.style.pointerEvents = 'none'; // Disable further clicks on this link

            // Simulate an export action (replace with actual logic)
            simulateExport(link.href);
        });
    });

    function simulateExport(url) {
        // Simulate an export process with a delay (use actual export code in the backend)
        setTimeout(() => {
            // If successful, show confirmation message
            showConfirmationModal('Export Successful!');
            // Optionally redirect to the URL after success (this would be your export URL in a real scenario)
            window.location.href = url;
        }, 2000); // Simulated delay
    }

    function showConfirmationModal(message) {
        const modal = document.getElementById('confirmation-modal');
        const messageElem = document.getElementById('confirmation-message');
        messageElem.innerHTML = message;
        modal.style.display = 'block'; // Show the modal
    }

    function closeModal() {
        const modal = document.getElementById('confirmation-modal');
        modal.style.display = 'none'; // Hide the modal
    }

    // Close modal when clicking outside the modal content
    window.onclick = function (event) {
        const modal = document.getElementById('confirmation-modal');
        if (event.target === modal) {
            closeModal();
        }
    }
});
