$(document).ready(function() {
    let spinWheel = document.querySelector(".spin-wheel");
    let spinButton = $('#spin');

    spinButton.click(function() {
        let number = Math.ceil(Math.random() * 10000); 
        spinWheel.style.transition = "transform 3s ease"; 
        spinWheel.style.transform = "rotate(" + number + "deg)";

        setTimeout(function() {
            spinWheel.style.transition = ""; 
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
        }, 3000); 
    });

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
