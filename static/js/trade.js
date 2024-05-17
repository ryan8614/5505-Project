$(document).ready(function() {
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
            console.error("Error: 'name' is undefined.");
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

        console.log("Fragment ID:", fragment_id);
        console.log("Current Status:", current_status);
        console.log("New Status:", new_status);
        console.log("New Price:", newPrice);

        // Verify that newPrice is a valid number and does not contain e
        if (newPrice === '' || isNaN(newPrice) || newPrice.indexOf('e') !== -1) {
            alert("Please enter a valid price.");
            return;
        }

        function handleAjaxError(xhr) {
            var errorMessage = "Unknown error";
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.responseText) {
                errorMessage = xhr.responseText;
            } else if (xhr.status) {
                errorMessage = "Error " + xhr.status + ": " + xhr.statusText;
            }
            alert(errorMessage);
        }
    
        // Send different requests based on current state and user-selected state
        if (current_status === 'Not For Sale' && new_status === 'for_sale') {
            // The current status is "Not Sold", and the user selects "Sell", a transaction is created.
            $.ajax({
                url: "/trade",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    fragment_id: fragment_id,
                    owner: $("#currentUserId").val(), // current_user ID
                    price: newPrice
                }),
                success: function(response) {
                    alert("Change sucessfully!");
                    location.reload();
                },
                error: handleAjaxError
            });
        } else if (current_status === 'For Sale' && new_status === 'not_for_sale') {
            // If the current status is "Sold" and the user selects "Not Sold", the transaction will be cancelled.
            $.ajax({
                url: "/trade/update_price/" + fragment_id,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    price: -1,
                    status: 'cancel',
                    owner: $("#currentUserId").val()
                }),
                success: function(response) {
                    alert("Change sucessfully!");
                    location.reload();
                },
                error: handleAjaxError
            });
        } else if (current_status === 'For Sale' && new_status === 'for_sale') {
            // The current status is "Sell", if the user selects "Sell", the price will be updated
            $.ajax({
                url: "/trade/update_price/" + fragment_id,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    price: newPrice,
                    status: 'update',
                    owner: $("#currentUserId").val()
                }),
                success: function(response) {
                    alert("Change sucessfully!");
                    location.reload();
                },
                error: handleAjaxError
            });
        }
        $('#myFragmentModal').modal('hide');
    });
});
