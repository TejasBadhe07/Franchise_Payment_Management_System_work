document.addEventListener('DOMContentLoaded', () => {
    const tasksContent = document.getElementById('tasks-content');
    const paymentsContent = document.getElementById('payments-content');
    const tasksLink = document.getElementById('tasks-link');
    const paymentsLink = document.getElementById('payments-link');
    const addAccountBtn = document.getElementById('add-account-btn');
    const accountDialog = document.getElementById('account-dialog');
    const cancelDialogBtn = document.getElementById('cancel-dialog-btn');
    const bankAccountForm = document.getElementById('bank-account-form');
    const deleteAccountBtn = document.getElementById('delete-account-btn');  // Delete Account button
    const deleteAccountDialog = document.getElementById('delete-account-dialog'); // Modal dialog for delete
    const deleteAccountSelect = document.getElementById('delete-account-select'); // Dropdown for accounts
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn'); // Confirm delete button
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn'); // Cancel button for delete dialog
    const updateBalanceDialog = document.getElementById('update-balance-dialog'); // Dialog for updating balance
    const updateBalanceForm = document.getElementById('update-balance-form'); // Form inside update dialog
    const accountNameUpdate = document.getElementById('account-name-update'); // Account Name field in update dialog
    const updateDate = document.getElementById('update-date'); // Date field in update dialog
    const updateAmount = document.getElementById('update-amount'); // Amount field in update dialog
    const cancelUpdateBtn = document.getElementById('cancel-update-btn'); // Cancel button in update dialog

    // Handle navigation between tasks and payments sections
    tasksLink.addEventListener('click', (event) => {
        event.preventDefault();
        showContent('tasks-content');
        tasksLink.classList.add('active');
        paymentsLink.classList.remove('active');
    });

    paymentsLink.addEventListener('click', (event) => {
        event.preventDefault();
        showContent('payments-content');
        paymentsLink.classList.add('active');
        tasksLink.classList.remove('active');
    });

    // Show content based on the selected tab
    function showContent(contentId) {
        const contentAreas = document.querySelectorAll('.content-area');
        contentAreas.forEach(area => area.style.display = 'none');
        document.getElementById(contentId).style.display = 'block';
    }

    // Show the Add Account dialog
    addAccountBtn.addEventListener('click', () => {
        accountDialog.showModal();
    });

    // Close the Add Account dialog
    cancelDialogBtn.addEventListener('click', () => {
        accountDialog.close();
    });

    // Handle Add Account form submission
    bankAccountForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(bankAccountForm);

        fetch('/add_accounts', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Account added successfully!');
                accountDialog.close();
                window.location.reload();
            } else {
                alert('Error adding account.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Logout functionality
    document.getElementById('logout-btn').addEventListener('click', () => {
        fetch('/logout', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('Logout failed.');
            }
        })
        .catch(error => {
            console.error('Error logging out:', error);
        });
    });

    // Show Delete Account dialog
    deleteAccountBtn.addEventListener('click', () => {
        deleteAccountDialog.showModal();
    });

    // Close the Delete Account dialog
    cancelDeleteBtn.addEventListener('click', () => {
        deleteAccountDialog.close();
    });

    // Confirm deletion of an account
    confirmDeleteBtn.addEventListener('click', () => {
        const selectedAccountId = deleteAccountSelect.value;

        if (selectedAccountId) {
            fetch(`/delete_account/${selectedAccountId}`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (response.ok) {
                    alert('Account deleted successfully!');
                    deleteAccountDialog.close();
                    window.location.reload();
                } else {
                    alert('Error deleting account.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            alert('Please select an account to delete.');
        }
    });

    // Open Update Balance dialog
    document.querySelectorAll('.update-balance-btn').forEach(button => {
        button.addEventListener('click', () => {
            const accountId = button.dataset.id; // Account ID
            const accountName = button.dataset.name; // Account Name

            // Populate dialog fields
            accountNameUpdate.value = accountName;
            updateDate.value = new Date().toISOString().split('T')[0]; // Set current date
            updateAmount.value = ''; // Clear the amount field

            // Store account ID in the form for submission
            updateBalanceForm.dataset.accountId = accountId;

            // Show the dialog
            updateBalanceDialog.showModal();
        });
    });

    // Handle Update Balance form submission
    updateBalanceForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const accountId = updateBalanceForm.dataset.accountId;
        const amount = updateAmount.value;

        // Validate amount
        if (!amount || amount <= 0) {
            alert('Please enter a valid amount.');
            return;
        }

        // Send the updated balance to the server
        fetch(`/update_balance/${accountId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: updateDate.value,
                amount: amount
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Balance updated successfully!');
                updateBalanceDialog.close();
                window.location.reload();
            } else {
                alert('Error updating balance.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Close the Update Balance dialog
    cancelUpdateBtn.addEventListener('click', () => {
        updateBalanceDialog.close();
    });

    // Show payments content by default
    showContent('payments-content');

    //////////////////////////////////////////////////
    const taskList = document.getElementById('task-list');
    const addPanelDialog = document.getElementById('add-panel-dialog');
    const deletePanelDialog = document.getElementById('delete-panel-dialog');
    const panelSelect = document.getElementById('panel-select');
    const panelTableBody = document.getElementById('panel-table-body');

    // Function to open a dialog
    function openDialog(dialog) {
        dialog.style.display = 'block';
    }

    // Function to close a dialog
    function closeDialog(dialog) {
        dialog.style.display = 'none';
    }

    // Function to add a new panel
    function addPanel(panelName, panelPoints) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${panelName}</td>
            <td>${panelPoints}</td>
        `;
        panelTableBody.appendChild(row);

        // Add the new panel to the delete dropdown
        const option = document.createElement('option');
        option.value = panelName;
        option.textContent = panelName;
        panelSelect.appendChild(option);
    }

    // Function to delete a panel
    function deletePanel(panelName) {
        const rows = panelTableBody.querySelectorAll('tr');
        rows.forEach(row => {
            if (row.querySelector('td').textContent === panelName) {
                panelTableBody.removeChild(row);
            }
        });

        // Remove the panel from the delete dropdown
        const options = panelSelect.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === panelName) {
                panelSelect.removeChild(option);
            }
        });
    }

    // Add event listeners to the initial buttons
    document.querySelector('.task-card-panel .add-task-btn').addEventListener('click', () => openDialog(addPanelDialog));
    document.querySelector('.task-card-panel .delete-task-btn').addEventListener('click', () => openDialog(deletePanelDialog));

    // Add event listeners to the dialog buttons
    document.getElementById('save-panel-btn').addEventListener('click', () => {
        const panelName = document.getElementById('panel-name').value;
        const panelPoints = document.getElementById('panel-points').value;
        addPanel(panelName, panelPoints);
        closeDialog(addPanelDialog);
    });

    document.getElementById('cancel-add-panel-btn').addEventListener('click', () => closeDialog(addPanelDialog));
    document.getElementById('delete-panel-btn').addEventListener('click', () => {
        const panelName = panelSelect.value;
        deletePanel(panelName);
        closeDialog(deletePanelDialog);
    });

    document.getElementById('cancel-delete-panel-btn').addEventListener('click', () => closeDialog(deletePanelDialog));
    

});
