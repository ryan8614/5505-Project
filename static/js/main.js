/* 
Implement user registration and login functions

interface: form
*/

// Using Google CDN import jQuery
import $ from "https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js";


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
            // Check if password and confirm-password match
            if (formData.psw !== formData['pwd-check']) {
                alert('Password and confirmation password do not match.');
            }
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
