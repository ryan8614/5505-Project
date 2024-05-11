$(document).ready(function() {
    // Handle modal show event and update modal content
    $('#BuyModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var fragmentName = button.data('fragment-name'); // Extract info from data-* attributes
        var fragmentPrice = button.data('fragment-price');
        var fragmentReleaseTime = button.data('fragment-release-time');
        var fragmentPath = button.data('fragment-path')

        console.log(fragmentName)
        var modal = $(this);
        modal.find('.modal-body img').attr('src', fragmentPath)
        modal.find('.modal-body h5').text(fragmentName);
        modal.find('.modal-body p.price').text('Price: ' + fragmentPrice + ' ETH');
        modal.find('.modal-body p.release-time').text('Release Time: ' + fragmentReleaseTime);
    });

    // Handle collapse button click event
    $(".collap-btn").click(function() {
        $(this).toggleClass("active");
        $(this).next().toggleClass("active");
    });
});
        