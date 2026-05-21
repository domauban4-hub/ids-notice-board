function showStatusMessage(message, success = true) {
    const messageBox = document.getElementById('status-message');
    if (!messageBox) return;
    messageBox.textContent = message;
    messageBox.style.color = success ? '#a7f3d0' : '#fecaca';
}

window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.status-action').forEach(button => {
        button.addEventListener('click', async () => {
            const staffId = button.dataset.id;
            const status = button.dataset.status;
            const url = `/api/status/${staffId}`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status })
                });
                const result = await response.json();
                if (result.success) {
                    showStatusMessage(`${result.name} status updated to ${result.status}.`);
                    document.querySelectorAll(`.staff-row-${staffId} .status-action`).forEach(btn => btn.classList.remove('active'));
                    document.querySelector(`.staff-row-${staffId} .status-action[data-status='${status}']`)?.classList.add('active');
                } else {
                    showStatusMessage(result.message || 'Update failed.', false);
                }
            } catch (error) {
                showStatusMessage('Unable to update status.', false);
            }
        });
    });
});
