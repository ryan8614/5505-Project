$(document).ready(function() {

    // Handle fragments on sale section buttons change content when click
    $('.collap-btn').click(function() {
        var content = $(this).next();
        content.toggle();  // Toggle visibility
    });

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
        $('#buyForm input[name="fragment_id"]').val($(this).data('fragment_id'));
        $('#buyForm input[name="buyer"]').val($(this).data('buyer'));
        $('#buyForm').submit();
    });

    $('#nft-confirmButton').on('click', function() {
        $('#redeemForm input[name="nft_id"]').val($(this).data('nftId'));
        $('#redeemForm input[name="user"]').val($(this).data('user'));
        $('#redeemForm').submit();
    });

    $('#search-form').on('submit', function(event) {
        event.preventDefault();
        let query = $('#search-input').val();

        $.ajax({
            url: '{{ url_for("search_fragments") }}',
            method: 'GET',
            data: { query: query },
            success: function(response) {
                let fragmentsContainer = $('#fragments-container');
                fragmentsContainer.empty();

                response.trades.forEach(function(trade) {
                    let fragmentHtml = `
                    <div class="col fragment">
                        <div class="card h-100">
                            <img src="${trade.fragment.path}" class="card-img-top" alt="${trade.fragment.name}">
                            <div class="card-body container d-flex flex-row justify-content-around">
                                <div class="container d-flex flex-column">
                                    <h5 class="card-title">${trade.fragment.name}</h5>
                                    <p class="card-text">Price: ${trade.price} ETH</p>
                                    <p class="card-text">${new Date(trade.listed_time).toLocaleDateString()}</p>
                                </div>
                                <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#BuyModal"
                                data-fragment-id="${trade.fragment.id}"
                                data-fragment-path="${trade.fragment.path}"
                                data-fragment-name="${trade.fragment.name}"
                                data-fragment-price="${trade.price}"
                                data-fragment-release-time="${new Date(trade.listed_time).toLocaleDateString()}">
                                    Buy
                                </button>
                            </div>
                        </div>
                    </div>`;
                    fragmentsContainer.append(fragmentHtml);
                });
            }
        });
    });

});
        