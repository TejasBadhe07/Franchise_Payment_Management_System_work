function logoutUser() {
    fetch('/logout', {
        method: 'POST', // Match the backend route method
        credentials: 'include', // Include cookies for session handling
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // Redirect to the login page after successful logout
            window.location.href = '/';
        } else {
            alert('Logout failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("Owner Dashboard Loaded");

    // Add Worker Function
    document.getElementById("add-worker-btn").addEventListener("click", function () {
        const workerName = prompt("Enter worker username:");
        if (workerName) {
            fetch("/add_worker", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: workerName }),
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload(); // Refresh to update worker list
            })
            .catch(error => console.error("Error:", error));
        }
    });

    // Delete Worker Function
    document.getElementById("delete-worker-btn").addEventListener("click", function () {
        const workerId = prompt("Enter Worker ID to delete:");
        if (workerId) {
            fetch(`/delete_worker/${workerId}`, { method: "POST" })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => console.error("Error:", error));
        }
    });

    // Toggle Submission Limit
    document.getElementById("submission-limit-toggle").addEventListener("change", function () {
        const isChecked = this.checked ? 1 : 0;
        fetch("/update_submission_limit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ limit: isChecked }),
        })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error("Error:", error));
    });

    // Fetch financial overview
    fetch("/get_financial_overview")
        .then(response => response.json())
        .then(data => {
            // Update summary cards
            document.getElementById("total-balance").innerText = `₹${data.total_balance}`;
            document.getElementById("total-sent").innerText = `₹${data.total_sent}`;
            document.getElementById("total-received").innerText = `₹${data.total_received}`;
            document.getElementById("profit-loss").innerText = `₹${data.profit_loss}`;

            // Populate transactions table
            const tableBody = document.getElementById("transactions-table-body");
            tableBody.innerHTML = "";  // Clear existing rows
            data.transactions.forEach(tx => {
                const row = `<tr>
                    <td>${tx.record_type}</td>
                    <td>${tx.record_name}</td>
                    <td>₹${tx.amount}</td>
                    <td>${tx.timestamp}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error("Error fetching financial overview:", error));
});



