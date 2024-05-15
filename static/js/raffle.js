$(document).ready(function() {
    $('#raffleButton').click(function() {
        $.post('/raffle', function(data) {
            $('#winningSplitImage').attr('src', data.fragment_path); 
            $('#winningSplitName').text('Congratulations! You won: ' + data.fragment_name);
            $('#raffleModal').modal('show');
        }).fail(function(jqXHR) {
            if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
                $('#errorMessage').text(jqXHR.responseJSON.error);
            } else {
                $('#errorMessage').text('Error: An unexpected error occurred. Please try again.');
            }
            $('#errorModal').modal('show');
        });
    });
});
