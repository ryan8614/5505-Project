/* 
Implement user registration and login functions

interface: form
*/

$(document).ready(function() {
    $('form').submit(function(event) {
        event.preventDefault();
        const path = window.location.pathname;
        let url = '';
        let data = {};

        // Use jQuery's serializeArray() to get form data and reduce it to an object 
        const formData = $(this).serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});

        // Determine the logic based on the current page
        if (path.includes('login.html')) {
            url = '/login';
            data = {
                username: formData.username,
                password: formData.psw
            };
        } else if (path.includes('register.html')) {
            url = '/register';
            data = {
                username: formData.uname,
                email: formData.email,
                password: formData.psw,
                confirmPassword: formData['pwd-check']
            };
        }

        // Send data
        $.ajax({
            type: 'POST',
            url: url,
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                console.log('Success:', response);
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});
