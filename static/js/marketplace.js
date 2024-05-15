//fragments on sale section buttons change content when click
function showContent(id) {
    // Hide all contents
    const contents = document.querySelectorAll('.btn-content');
    contents.forEach(content => {
        content.classList.remove('active');
    });

    // Show the clicked content
    const targetContent = document.getElementById(id);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}
        
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.collap-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const content = this.nextElementSibling;
            if (content.style.display === 'block') {
                content.style.display = 'none';
            } else {
                content.style.display = 'block';
            }
        });
    });
});