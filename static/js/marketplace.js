$(document).ready(function() {
    // Handle modal show event and update modal content
    $('button[data-bs-target="#BuyModal"]').click(function(event) {
        event.preventDefault();
        checkLoginStatus_fragment($(this));
    });


    $('button[data-bs-target="#RedeemModal"]').click(function(event) {
        event.preventDefault();
        checkLoginStatus_nft($(this));
    });


    function checkLoginStatus_fragment(button) {
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
                    var frgconfirmButton = $('#frg-confirmButton');
                    frgconfirmButton.data('fragment_id', fragmentId);

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
    

    function checkLoginStatus_nft(button) {
        $.ajax({
            url: '/check_login',
            method: 'GET',
            success: function(data) {
                if (data.is_logged_in) {
                    // User is logged in, show the modal
                    var nftId = button.data('nft-id')
                    var nftBonus = button.data('nft-bonus')
                    var nftName = button.data('nft-name')
                    
                    var modal = $('#RedeemModal');
                    modal.find('.name').text(nftName);
                    modal.find('.bonus').text(nftBonus);
                    modal.modal('show');

                    // Set the properties of the Confirm button in the modal box
                    var nftconfirmButton = $('#nft-confirmButton');
                    nftconfirmButton.data('nftId', nftId);

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

    $('#frg-confirmButton').on('click', function() {
        frgconfirmTransaction($(this));
    });

    function frgconfirmTransaction(button) {
        var fragment_id = button.data('fragment_id');
        var buyer = button.data('buyer');

        $('#buyForm input[name="fragment_id"]').val(fragment_id);
        $('#buyForm input[name="buyer"]').val(buyer);
        $('#buyForm').submit();
    }

    $('#nft-confirmButton').on('click', function() {
        nftconfirmTransaction($(this));
    });

    function nftconfirmTransaction(button) {
        var nft_id = button.data('nftId');
        var user = button.data('user');
        console.log(nft_id)
        console.log(user)
        $('#redeemForm input[name="nft_id"]').val(nft_id);
        $('#redeemForm input[name="user"]').val(user);
        $('#redeemForm').submit();
    }

});
        