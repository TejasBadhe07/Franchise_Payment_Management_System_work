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

    // paymentsLink.addEventListener('click', (event) => {
    //     event.preventDefault();
    //     showContent('payments-content');
    //     paymentsLink.classList.add('active');
    //     tasksLink.classList.remove('active');
    // });

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

    // Show Task content by default
    showContent('tasks-content');
    tasksLink.classList.add('active');

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
    // Expense Management
    const expenseTableBody = document.getElementById('expense-table-body');
    const expenseSelect = document.getElementById('expense-select');

    // Handle save expense
    document.getElementById('save-expense-btn').addEventListener('click', () => {
        const category = document.getElementById('expense-name').value;
        const amount = document.getElementById('expense-amount').value;
        const transactionType = document.querySelector('input[name="transaction-type"]:checked').value;
    
        if (category && amount && transactionType) {
            const formData = new FormData();
            formData.append('expense_category', category);
            formData.append('expense_amount', amount);
            formData.append('transaction_type', transactionType);
    
            fetch('/add_expense', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
    
                    // Add new expense entry dynamically
                    const tableBody = document.getElementById('expense-table-body');
                    const row = document.createElement('tr');
    
                    row.innerHTML = `
                        <td>${category}</td>
                        <td>${amount}</td>
                        <td>${transactionType}</td>
                    `;
    
                    tableBody.appendChild(row);  // Append new expense row to table
    
                    // Close dialog
                    document.getElementById('add-expense-dialog').style.display = 'none';
                } else {
                    alert(data.message);
                }
            });
        }
    });
    
    

    // Handle delete expense
    document.getElementById('delete-expense-btn').addEventListener('click', () => {
        const selectedExpenseId = document.getElementById('delete-expense-select').value;
    
        if (selectedExpenseId) {
            fetch(`/delete_expense/${selectedExpenseId}`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
    
                    // Remove the deleted expense from the table
                    const tableBody = document.getElementById('expense-table-body');
                    tableBody.querySelectorAll('tr').forEach(row => {
                        if (row.cells[0].textContent === document.getElementById('delete-expense-select').selectedOptions[0].text) {
                            row.remove();
                        }
                    });
    
                    // Remove the deleted expense from the dropdown
                    document.getElementById('delete-expense-select').removeChild(
                        document.getElementById('delete-expense-select').selectedOptions[0]
                    );
    
                    // Close the delete dialog automatically
                    document.getElementById('delete-expense-dialog').style.display = 'none';
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            alert('Please select an expense to delete.');
        }
    });
    
    

/////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Get references to dialog elements
    const expenseDialog = document.getElementById('expense-dialog');
    const dialogExpenseName = document.getElementById('dialog-expense-name');
    const dialogDate = document.getElementById('dialog-date');
    const dialogAmount = document.getElementById('dialog-amount');
    const saveTransactionBtn = document.getElementById('save-transaction');
    const cancelTransactionBtn = document.getElementById('cancel-transaction');

    // Open the dialog when Sent or Receive is clicked
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('expense-action-btn')) {
            const row = event.target.closest('tr'); // Get the row of the clicked button
            const expenseName = row.cells[0].textContent; // Get expense name

            dialogExpenseName.value = expenseName; // Set expense name in dialog
            dialogDate.value = new Date().toISOString().split('T')[0]; // Set today's date

            expenseDialog.showModal(); // Open dialog
        }
    });

    // Close the dialog on Cancel
    cancelTransactionBtn.addEventListener('click', () => {
        expenseDialog.close();
    });

    // Handle Save Transaction (For now, just log values)
    saveTransactionBtn.addEventListener('click', () => {
        const expenseName = dialogExpenseName.value;
        const date = dialogDate.value;
        const amount = dialogAmount.value;

        if (amount) {
            console.log(`Transaction Saved: ${expenseName}, ${date}, ${amount}`);
            alert(`Transaction Saved: ${expenseName}, ${date}, ${amount}`);
            expenseDialog.close();
        } else {
            alert("Please enter an amount!");
        }
    });

    // Open and close Update Points dialog
    function openUpdatePanelDialog(panelName) {
        document.getElementById('update-panel-name').value = panelName;
        document.getElementById('update-panel-date').value = new Date().toISOString().split('T')[0]; // Autofill date
        document.getElementById('update-points-dialog').showModal();
    }

    document.getElementById('cancel-update-panel-btn').addEventListener('click', () => {
        document.getElementById('update-points-dialog').close();
    });

    // Handle "Update Points" button click
    document.getElementById('save-update-panel-btn').addEventListener('click', () => {
        const panelName = document.getElementById('update-panel-name').value;
        const updateDate = document.getElementById('update-panel-date').value;
        const updatedPoints = document.getElementById('update-panel-points').value;

        if (panelName && updateDate && updatedPoints) {
            const formData = new FormData();
            formData.append('panel_name', panelName);
            formData.append('update_date', updateDate);
            formData.append('updated_points', updatedPoints);

            fetch('/update_panel_points', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    document.getElementById('update-points-dialog').close();
                    window.location.reload();
                } else {
                    alert(data.message);
                }
            });
        }
    });

    // Modify panel table to include Update Points button
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
    
                    // Add new panel entry to the table
                    const tableBody = document.getElementById('panel-table-body');
                    const row = document.createElement('tr');
    
                    row.innerHTML = `
                        <td>${name}</td>
                        <td>${points}</td>
                        <td><button class="update-points-btn" data-panel="${name}">Update</button></td>
                    `;
    
                    tableBody.appendChild(row);
    
                    // Add new panel entry to the dropdown
                    const panelSelect = document.getElementById('panel-select');
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    panelSelect.appendChild(option);
    
                    document.getElementById('add-panel-dialog').style.display = 'none';
                } else {
                    alert(data.message);
                }
            });
        }
    });

    document.getElementById('delete-panel-btn').addEventListener('click', () => {
        const deletePanelDialog = document.getElementById('delete-panel-dialog');
        const panelSelect = document.getElementById('delete-panel-select');
    
        const selectedPanelId = panelSelect.value;
    
        if (!selectedPanelId) {
            alert('Please select a panel to delete.');
            return;
        }
    
        fetch(`/delete_panel/${selectedPanelId}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Panel deleted successfully!');
                deletePanelDialog.close();
                window.location.reload(); // ✅ Refresh page to update UI
            } else {
                alert('Error deleting panel.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    
    
    

});