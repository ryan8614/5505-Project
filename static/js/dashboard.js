$(document).ready(function() {
    // Trade.js
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
            $('#messageModal .modal-body').text("Error: 'name' is undefined.");  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
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

        // Verify that newPrice is a valid number and does not contain e
        if (newPrice === '' || isNaN(newPrice) || newPrice.indexOf('e') !== -1) {
            $('#messageModal .modal-body').text("Please enter a valid price.");  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
            return;
        }

        // Generic error handling for AJAX requests
        function handleAjaxError(xhr) {
            var errorMessage = "Unknown error";
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.responseText) {
                errorMessage = xhr.responseText;
            } else if (xhr.status) {
                errorMessage = "Error " + xhr.status + ": " + xhr.statusText;
            }
            $('#messageModal .modal-body').text(errorMessage);  //Set the text in the modal box
            $('#messageModal').modal('show');  // show modal box
        }

        function updateUI(response) {
            if (response.status === 'success') {
                $('#messageModal .modal-body').text(response.message);  // Set success message
                $('#messageModal').modal('show');  // Show modal box
                fetchFragments();  // Call function to re-fetch and render fragments
            } else {
                $('#messageModal .modal-body').text(response.message);  // Set error message
                $('#messageModal').modal('show');  // Show modal box
            }
        }
    
        // Determine which AJAX call to make based on the fragment's current and new status
        let url, data;
        if (current_status === 'Not For Sale' && new_status === 'for_sale') {
            url = "/trade/trade";
            data = JSON.stringify({
                fragment_id: fragment_id,
                owner: $("#currentUserId").val(),
                price: newPrice
            });
        } else if (current_status === 'For Sale' && new_status === 'not_for_sale') {
            url = "/trade/update_price/" + fragment_id;
            data = JSON.stringify({
                price: -1, // Indicative of cancelling the sale
                status: 'cancel',
                owner: $("#currentUserId").val()
            });
        } else if (current_status === 'For Sale' && new_status === 'for_sale') {
            url = "/trade/update_price/" + fragment_id;
            data = JSON.stringify({
                price: newPrice,
                status: 'update',
                owner: $("#currentUserId").val()
            });
        } else {
            // No valid action determined
            $('#messageModal .modal-body').text("No valid action determined based on the current and new status."); 
            $('#messageModal').modal('show');  // Show modal box
            return;
        }
        // Execute the appropriate AJAX request
        $.ajax({
            url: url,
            type: "POST",
            contentType: "application/json",
            data: data,
            success: updateUI,
            error: handleAjaxError
        });

        // Hide the modal after processing
        $('#myFragmentModal').modal('hide');
    });

    function fetchFragments() {
        $.ajax({
            url: '/trade/get_fragments',
            type: 'GET',
            success: function(fragments) {
                var tbody = $('#fragments');
                tbody.empty(); // Clear the current fragment list
                fragments.forEach(function(fragment) {
                    tbody.append(`
                        <tr data-bs-toggle="modal" data-bs-target="#myFragmentModal" data-id="${fragment.id}" data-name="${fragment.name}" data-status="${fragment.status}" data-price="${fragment.price}" style="height: 100px;">
                            <td><img class="trade-img" src="${fragment.path}"></td>
                            <td>${fragment.name}</td>
                            <td>${fragment.status}</td>
                            <td>${fragment.price}</td>
                        </tr>
                    `);
                });
            },
            error: function(xhr) {
                console.error('Failed to fetch fragments:', xhr.responseText);
            }
        });
    }

    $('.lottery-button').on('click', function() {
        $.ajax({
            url: '/raffle/raffle', // raffle route
            type: 'POST',
            dataType: 'json', 
            success: function(response) {
                // Callback function after successful request
                if (response.fragment_path && response.fragment_name && response.fragment_id) {
                    $('#winningSplitImage').attr('src', response.fragment_path); 
                    $('#winningSplitName').text('Congratulations! You won: ' + response.fragment_name);
                    startAnimation(response.fragment_id)
                    fetchFragments()
                }
            },
            error: function(xhr) {
                var errorMessage = 'An unknown error occurred, please try again later.'; // Default error message
                if (xhr.status === 400) {
                    try {
                        var errorResponse = JSON.parse(xhr.responseText);
                        errorMessage = `Error: ${errorResponse.error}`; // Parsing the JSON error response
                    } catch (e) {
                        errorMessage = 'Error parsing the response, please try again.';
                    }
                } else if (xhr.status) {
                    errorMessage = `Error ${xhr.status}: ${xhr.statusText}`; // General HTTP error message
                }
                $('#messageModal .modal-body').text(errorMessage);
                $('#messageModal').modal('show')
            }
        });
    });


    function findItemIndexByFragmentId(fragment_id, items) {
        let index = -1; // The default index is -1, indicating not found
    
        items.some((item, idx) => { // Use the .some method to stop iteration as soon as a match is found
            const altValue = $(item).find('img').attr('alt'); // Get the alt attribute of the img element under the current item
            if (altValue === fragment_id.toString()) { 
                index = idx; 
                return true; 
            }
            return false; // Keep iterating
        });
    
        return index; // return index
    }

    let isAnimating = false;
    let animationFrameId;
    const duration = 3000; 
    const decelerationDuration = 2000;
    let position = 0;
    let speed = 110;

    function startAnimation(frag_id) {
        if (isAnimating) return;
        isAnimating = true;

        const itemList = $('.item-list');
        const items = $('.item').toArray();

        const itemWidth = items[0].offsetWidth;
        const itemCount = items.length;

        items.forEach(item => {
            $(item).css('width', `${itemWidth}px`);
        });
        index = findItemIndexByFragmentId(frag_id, items)

        const totalItems = itemCount * 3;
        const visibleItems = 5;
        const centerIndex = Math.floor(visibleItems / 2);
        const totalWidth = itemWidth * totalItems;
        var final_index = itemCount + index
        itemList.empty();
        [...items, ...items, ...items].forEach(item => {
            itemList.append($(item).clone(true));
        });

        const startTime = performance.now();

        function easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }

        function animate(time) {
            const elapsed = time - startTime;
            if (elapsed < duration) {
                position += speed;
                position %= totalWidth;
                itemList.css('transform', `translateX(${-position}px)`);
                animationFrameId = requestAnimationFrame(animate);
            } else {
                const decelerationStartTime = performance.now();
                const initialPosition = position;
                const randomIndex = final_index;
                const stopPosition = randomIndex * itemWidth - (itemWidth * centerIndex);
                const totalDistance = (stopPosition - initialPosition + totalWidth) % totalWidth;

                function decelerate(decelerateTime) {
                    const decelerationElapsed = decelerateTime - decelerationStartTime;
                    const t = Math.min(decelerationElapsed / decelerationDuration, 1);
                    const ease = easeOutCubic(t);
                    position = initialPosition + totalDistance * ease;
                    position %= totalWidth;
                    itemList.css('transform', `translateX(${-position}px)`);
                    if (t < 1) {
                        animationFrameId = requestAnimationFrame(decelerate);
                    } else {
                        isAnimating = false;
                        const prizeIndex = Math.floor((position + itemWidth * centerIndex) / itemWidth) % totalItems;
                        const prizeImage = $(items[prizeIndex]).find('img').attr('alt');
                        setTimeout(() => {
                            $('#lotteryModal').modal('show'); // Show the modal with the error message
                        }, 100);
                    }
                }
                animationFrameId = requestAnimationFrame(decelerate);
            }
        }

        cancelAnimationFrame(animationFrameId);
        animationFrameId = requestAnimationFrame(animate);
    }

    function stopAnimation() {
        cancelAnimationFrame(animationFrameId);
        isAnimating = false;
    }


});
