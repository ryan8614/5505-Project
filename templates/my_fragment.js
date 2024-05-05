document.addEventListener("DOMContentLoaded", function() {
    const fragmentCards = document.querySelectorAll(".fragment-card");
    const fragmentModal = document.querySelector("#fragmentModal");
    const modalImage = fragmentModal.querySelector(".modal-body img");

    fragmentCards.forEach(function(card) {
        card.addEventListener("click", function() {
            const imgSrc = this.querySelector("img").getAttribute("src");
            modalImage.setAttribute("src", imgSrc);
        });
    });
});