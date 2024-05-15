let spin_wheel = document.querySelector(".spin-wheel");
let btn = document.getElementById("spin");
let number = 0; // angle starts from 0

btn.onclick = function () {
    number += Math.ceil(Math.random() * 10000); //update angle
    spin_wheel.style.transition = "transform 3s ease"; 
    spin_wheel.style.transform = "rotate(" + number + "deg)"; //rotate to new angle

    // show lottery result after spin wheel finish
    setTimeout(function() {
        spin_wheel.style.transition = ""; // remove transition
        $.post('/raffle', function(data) {
            $('#winningSplitImage').attr('src', data.fragment_path); 
            $('#winningSplitName').text('Congratulations! You won: ' + data.fragment_name);
            $('#raffleModal').modal('show');
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
                $('#errorMessage').text(jqXHR.responseJSON.error);
            } else {
                $('#errorMessage').text('Error: An unexpected error occurred. Please try again.');
            }
            $('#errorModal').modal('show');
        });
    }, 3000); //show message after 3s
};