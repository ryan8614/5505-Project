
//https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_collapsible

document.addEventListener("DOMContentLoaded", function() {
    var coll = document.getElementsByClassName("collap-btn");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            content.classList.toggle("active");
        });
    }
});

        
        