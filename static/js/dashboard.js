$(document).ready(function() {
    // Trade.js
    $('#fragments').on('click', 'tr', function() {
        var fragid = $(this).data('id')
        var name = $(this).data('name');
        var price = $(this).data('price');
        var status = $(this).data('status');

        if (name) {
            $('#modalFragmentName').text(name);
            $('#modalFragmentStatus').text(status);
            $('#fragment-id').val(fragid);
            $('#fragment-status').val(status)

            if (status === 'For Sale') {
                $('#fragmentStatus').val('for_sale');
                $('#priceContainer').show();
                $('#modalFragmentPrice').text(price);
                $('#priceGroup').show();
                $('#newPrice').val(price);
            } else {
                $('#fragmentStatus').val('not_for_sale');
                $('#priceContainer').hide();
                $('#modalFragmentPrice').text('');
                $('#priceGroup').hide();
                $('#newPrice').val('');
            }
        } else {
            $('#messageModal .modal-body').text("Error: 'name' is undefined.");  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
        }
    });

    $('#fragmentStatus').on('change', function() {
        if ($(this).val() === 'for_sale') {
            $('#priceGroup').show();
        } else {
            $('#priceGroup').hide();
        }
    });

    $('#saveChangesButton').on('click', function() {
        var fragment_id = $('#fragment-id').val()
        var current_status = $("#fragment-status").val();
        var new_status = $("#fragmentStatus").val();
        var newPrice = $("#newPrice").val();

        // Verify that newPrice is a valid number and does not contain e
        if (newPrice === '' || isNaN(newPrice) || newPrice.indexOf('e') !== -1) {
            $('#messageModal .modal-body').text("Please enter a valid price.");  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
            return;
        }

        // Generic error handling for AJAX requests
        function handleAjaxError(xhr) {
            var errorMessage = "Unknown error";
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.responseText) {
                errorMessage = xhr.responseText;
            } else if (xhr.status) {
                errorMessage = "Error " + xhr.status + ": " + xhr.statusText;
            }
            $('#messageModal .modal-body').text(errorMessage);  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
        }

        function updateUI(response) {
            if (response.status === 'success') {
                $('#messageModal .modal-body').text(response.message);  // Set success message
                $('#messageModal').modal('show');  // Show modal box
                fetchFragments();  // Call function to re-fetch and render fragments
            } else {
                $('#messageModal .modal-body').text(response.message);  // Set error message
                $('#messageModal').modal('show');  // Show modal box
            }
        }
    
        // Determine which AJAX call to make based on the fragment's current and new status
        let url, data;
        if (current_status === 'Not For Sale' && new_status === 'for_sale') {
            url = "/trade";
            data = JSON.stringify({
                fragment_id: fragment_id,
                owner: $("#currentUserId").val(),
                price: newPrice
            });
        } else if (current_status === 'For Sale' && new_status === 'not_for_sale') {
            url = "/trade/update_price/" + fragment_id;
            data = JSON.stringify({
                price: -1, // Indicative of cancelling the sale
                status: 'cancel',
                owner: $("#currentUserId").val()
            });
        } else if (current_status === 'For Sale' && new_status === 'for_sale') {
            url = "/trade/update_price/" + fragment_id;
            data = JSON.stringify({
                price: newPrice,
                status: 'update',
                owner: $("#currentUserId").val()
            });
        } else {
            // No valid action determined
            $('#messageModal .modal-body').text("No valid action determined based on the current and new status."); 
            $('#messageModal').modal('show');  // Show modal box
            return;
        }
        // Execute the appropriate AJAX request
        $.ajax({
            url: url,
            type: "POST",
            contentType: "application/json",
            data: data,
            success: updateUI,
            error: handleAjaxError
        });

        // Hide the modal after processing
        $('#myFragmentModal').modal('hide');
    });

    function fetchFragments() {
        $.ajax({
            url: '/get_fragments',
            type: 'GET',
            success: function(fragments) {
                var tbody = $('#fragments');
                tbody.empty(); // Clear the current fragment list
                fragments.forEach(function(fragment) {
                    tbody.append(`
                        <tr data-bs-toggle="modal" data-bs-target="#myFragmentModal" data-id="${fragment.id}" data-name="${fragment.name}" data-status="${fragment.status}" data-price="${fragment.price}">
                            <td><img class="trade-img" src="${fragment.path}"></td>
                            <td>${fragment.id}</td>
                            <td>${fragment.name}</td>
                            <td>${fragment.status}</td>
                            <td>${fragment.price}</td>
                        </tr>
                    `);
                });
            },
            error: function(xhr) {
                console.error('Failed to fetch fragments:', xhr.responseText);
            }
        });
    }
});