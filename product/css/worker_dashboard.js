document.addEventListener('DOMContentLoaded', () => {
    // Get the elements we need
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
    // Handle the task completion functionality
    // Function to open and close dialogs
    function openDialog(id) {
        document.getElementById(id).style.display = 'block';
    }
    function closeDialog(id) {
        document.getElementById(id).style.display = 'none';
    }

    // Event Listeners for opening dialogs
    document.getElementById('open-add-panel-dialog').addEventListener('click', () => openDialog('add-panel-dialog'));
    document.getElementById('open-delete-panel-dialog').addEventListener('click', () => openDialog('delete-panel-dialog'));
    document.getElementById('open-add-expense-dialog').addEventListener('click', () => openDialog('add-expense-dialog'));
    document.getElementById('open-delete-expense-dialog').addEventListener('click', () => openDialog('delete-expense-dialog'));

    // Event Listeners for cancel buttons
    document.getElementById('cancel-add-panel-btn').addEventListener('click', () => closeDialog('add-panel-dialog'));
    document.getElementById('cancel-delete-panel-btn').addEventListener('click', () => closeDialog('delete-panel-dialog'));
    document.getElementById('cancel-add-expense-btn').addEventListener('click', () => closeDialog('add-expense-dialog'));
    document.getElementById('cancel-delete-expense-btn').addEventListener('click', () => closeDialog('delete-expense-dialog'));

    // Panel Management
    const panelTableBody = document.getElementById('panel-table-body');
    const panelSelect = document.getElementById('panel-select');
    
    // Handle save panel
    document.getElementById('save-panel-btn').addEventListener('click', () => {
        const name = document.getElementById('panel-name').value;
        const points = document.getElementById('panel-points').value;
        if (name && points) {
            const formData = new FormData();
            formData.append('panel_name', name);
            formData.append('panel_points', points);

            fetch('/add_panel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    const row = document.createElement('tr');

                    row.innerHTML = `
                        <td>${name}</td>
                        <td>${points}</td>
                        <td>
                            <button class="update-balance-btn">Update Balance</button>
                        </td>
                    `;

                    panelTableBody.appendChild(row);
                    panelSelect.innerHTML += `<option value="${name}">${name}</option>`;
                    closeDialog('add-panel-dialog');
                } else {
                    alert(data.message);
                }
            });
        }
    });


    // Handle delete panel
    document.getElementById('delete-panel-btn').addEventListener('click', () => {
        const selected = panelSelect.value;
        if (selected && confirm(`Are you sure you want to delete panel '${selected}'?`)) {
            const formData = new FormData();
            formData.append('panel_name', selected);

            fetch('/delete_panel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    panelTableBody.querySelectorAll('tr').forEach(row => {
                        if (row.cells[0].textContent === selected) row.remove();
                    });
                    panelSelect.querySelector(`option[value="${selected}"]`).remove();
                    closeDialog('delete-panel-dialog');
                } else {
                    alert(data.message);
                }
            });
        }
    });

    // Expense Management
    const expenseTableBody = document.getElementById('expense-table-body');
    const expenseSelect = document.getElementById('expense-select');

    // Handle save expense
    document.getElementById('save-expense-btn').addEventListener('click', () => {
        const name = document.getElementById('expense-name').value;
        const amount = document.getElementById('expense-amount').value;
        if (name && amount) {
            const formData = new FormData();
            formData.append('expense_name', name);
            formData.append('expense_amount', amount);
    
            fetch('/add_expense', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    
                    // Add the new row with the Sent/Received buttons
                    expenseTableBody.innerHTML += `
                        <tr>
                            <td>${name}</td>
                            <td>${amount}</td>
                            <td>
                                <button class="sent-btn">Sent</button>
                                <button class="received-btn">Received</button>
                            </td>
                        </tr>
                    `;
                    
                    // Add the new option to the select dropdown
                    expenseSelect.innerHTML += `<option value="${name}">${name}</option>`;
                    
                    closeDialog('add-expense-dialog');
                } else {
                    alert(data.message);
                }
            });
        }
    });
    

    // Handle delete expense
    document.getElementById('delete-expense-btn').addEventListener('click', () => {
        const selected = expenseSelect.value;
        if (selected && confirm(`Are you sure you want to delete expense '${selected}'?`)) {
            const formData = new FormData();
            formData.append('expense_name', selected);

            fetch('/delete_expense', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    expenseTableBody.querySelectorAll('tr').forEach(row => {
                        if (row.cells[0].textContent === selected) row.remove();
                    });
                    expenseSelect.querySelector(`option[value="${selected}"]`).remove();
                    closeDialog('delete-expense-dialog');
                } else {
                    alert(data.message);
                }
            });
        }
    });

});