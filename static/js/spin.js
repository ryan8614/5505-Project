//spin wheel

let spin_wheel = document.querySelector(".spin-wheel");
let btn = document.getElementById("spin");
let number = Math.ceil(Math.random() * 10000);

btn.onclick = function () {
    spin_wheel.style.transform = "rotate(" + number + "deg)";
    number += Math.ceil(Math.random() * 10000);
}