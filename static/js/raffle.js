$(document).ready(function() {
    $('#raffleButton').click(function() {
        $.post('/raffle', function(data) {
            if (data.error) {
                // Update the text of the errorMessage span with the received error message
                $('#errorMessage').text(data.error);
                // Show the modal with the error message
                $('#errorModal').modal('show');
            } else {
                $('#winningSplitImage').attr('src', data.fragment_path); 
                $('#winningSplitName').text('Congratulations! You won: ' + data.fragment_name);
                $('#raffleModal').modal('show');
            }
        }).fail(function(response) {
            // In case the AJAX request itself fails, we provide a generic error message
            $('#errorMessage').text('Error: There are no more fragments.');
            $('#errorModal').modal('show');
        });
    });
});
