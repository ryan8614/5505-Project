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
        
        