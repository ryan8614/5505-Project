$(document).ready(function() {
    // Handle modal show event and update modal content
    $('button[data-bs-target="#BuyModal"]').click(function(event) {
        event.preventDefault();
        checkLoginStatus($(this));
    });

    function checkLoginStatus(button) {
        $.ajax({
            url: '/check_login',
            method: 'GET',
            success: function(data) {
                if (data.is_logged_in) {
                    // User is logged in, show the modal
                    var fragmentId = button.data('fragment-id')
                    var fragmentPath = button.data('fragment-path');
                    var fragmentName = button.data('fragment-name');
                    var fragmentPrice = button.data('fragment-price');
                    var fragmentReleaseTime = button.data('fragment-release-time');

                    var modal = $('#BuyModal');
                    modal.find('img').attr('src', fragmentPath);
                    modal.find('h5').text(fragmentName);
                    modal.find('.price').text('Price: ' + fragmentPrice + ' ETH');
                    modal.find('.release-time').text('Release Time: ' + fragmentReleaseTime);
                    modal.modal('show');

                    // Set the properties of the Confirm button in the modal box
                    var confirmButton = $('#confirmButton');
                    confirmButton.data('fragment_id', fragmentId);

                } else {
                    // User is not logged in, redirect to login page
                    window.location.href = '/login';
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    }
    
    $('#confirmButton').on('click', function() {
        confirmTransaction($(this));
    });

    function confirmTransaction(button) {
        var fragment_id = button.data('fragment_id');
        var buyer = button.data('buyer');

        $('#buyForm input[name="fragment_id"]').val(fragment_id);
        $('#buyForm input[name="buyer"]').val(buyer);
        $('#buyForm').submit();
    }

});
        