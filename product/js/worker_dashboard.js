document.addEventListener('DOMContentLoaded', () => {
    const tasksContent = document.getElementById('tasks-content');
    const paymentsContent = document.getElementById('payments-content');
    const tasksLink = document.getElementById('tasks-link');
    const paymentsLink = document.getElementById('payments-link');
    const addAccountBtn = document.getElementById('add-account-btn');
    const accountDialog = document.getElementById('account-dialog');
    const cancelDialogBtn = document.getElementById('cancel-dialog-btn');
    const bankAccountForm = document.getElementById('bank-account-form');
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    const deleteAccountDialog = document.getElementById('delete-account-dialog');
    const deleteAccountSelect = document.getElementById('delete-account-select');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const updateBalanceDialog = document.getElementById('update-balance-dialog');
    const updateBalanceForm = document.getElementById('update-balance-form');
    const accountNameUpdate = document.getElementById('account-name-update');
    const updateDate = document.getElementById('update-date');
    const updateAmount = document.getElementById('update-amount');
    const cancelUpdateBtn = document.getElementById('cancel-update-btn');
    ////////////////////////////////////////////////////////////////////

    

    ////////////////////////////////////////////////////////

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
        const accountId = button.dataset.id;
        const accountName = button.dataset.name;

        // Populate dialog fields
        accountNameUpdate.value = accountName;
        updateDate.value = new Date().toISOString().split('T')[0];
        updateAmount.value = '';

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

    // --------------------------------------------------------------------------------------------------
    // Add Panel functionality
    // Add Panel functionality
    const addPanelBtn = document.getElementById('panel-add-task-btn');
    const addPanelDialog = document.getElementById('add-panel-dialog');
    const panelNameInput = document.getElementById('panel-name');
    const panelPointsInput = document.getElementById('panel-points');
    const panelSubmitBtn = document.getElementById('panel-submit-btn');
    const panelCancelBtn = document.getElementById('panel-cancel-btn');
    const panelTable = document.getElementById('panel-table');

    addPanelBtn.addEventListener('click', () => {
        addPanelDialog.showModal();
    });

    panelCancelBtn.addEventListener('click', () => {
        addPanelDialog.close();
        panelNameInput.value = '';
        panelPointsInput.value = '';
    });

    panelSubmitBtn.addEventListener('click', () => {
        const panelName = panelNameInput.value;
        const panelPoints = panelPointsInput.value;

        // Send a POST request to the Flask backend
        fetch('/add_panel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: panelName, points: panelPoints })
        })
        .then(response => {
        if (response.ok) {
            // Handle successful response (e.g., update the UI)
            addPanelDialog.close();
            panelNameInput.value = '';
            panelPointsInput.value = '';
            // Refresh the panel list (optional)
            fetch('/get_panels')
            .then(response => response.json())
            .then(data => {
                // Clear existing rows
                panelTable.querySelector('tbody').innerHTML = '';
                // Create and append new rows
                data.forEach(panel => {
                const row = panelTable.querySelector('tbody').insertRow();
                const nameCell = row.insertCell();
                const pointsCell = row.insertCell();
                const actionCell = row.insertCell();
                nameCell.textContent = panel.name;
                pointsCell.textContent = panel.points;
                actionCell.innerHTML = `
                    <button class="update-btn">Update</button>
                    <button class="delete-btn">Delete</button>
                `; 
                });
            });
        } else {
            // Handle error (e.g., display an error message)
            console.error('Error adding panel:', response.statusText);
        }
        })
        .catch(error => {
        console.error('Error:', error);
        });
    });

    // Handle delete button clicks
    panelTable.addEventListener('click', event => {
        if (event.target.classList.contains('delete-btn')) {
        const row = event.target.closest('tr');
        const panelName = row.cells[0].textContent; 

        // Send a DELETE request to the Flask backend
        fetch('/delete_panel', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: panelName })
        })
        .then(response => {
            if (response.ok) {
            // Remove the row from the table
            row.remove();
            } else {
            console.error('Error deleting panel:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        }
    });
});