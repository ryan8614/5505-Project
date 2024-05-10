$(document).ready(function() {
    $('#raffleButton').click(function() {
        $.post('/raffle', function(data) {
            if (data.error) {
                alert(data.error);
            } else {
                $('#winningSplitImage').attr('src', data.fragment_path); 
                $('#winningSplitName').text('Congratulations! You won: ' + data.fragment_name);
                $('#raffleModal').modal('show');
            }
        }).fail(function(response) {
            alert('Error: ' + response.responseText);
        });
    });
});