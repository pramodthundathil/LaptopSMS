import { Dropdown, Collapse, initMDB } from "mdb-ui-kit";

initMDB({ Dropdown, Collapse });

// Make link active
var path = window.location.pathname;

var navLinks = document.querySelectorAll('.navbar-nav a');
navLinks.forEach(function(link) {
    if (link.getAttribute('href') === path) {
        link.classList.add('active');
    }
});
