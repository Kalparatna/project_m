
// Toggle Button 
document.querySelector('.navbar-toggle').addEventListener('click', function () {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
    this.classList.toggle('active');
});



// Add smooth scroll effect to navbar links
document.querySelectorAll('.nav-links ul li a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        const offsetTop = document.querySelector(href).offsetTop;

        window.scrollTo({
            top: offsetTop - 80, // Adjust for the navbar height
            behavior: 'smooth'
        });
    });
});


//  Fag Section
document.addEventListener('DOMContentLoaded', function() {
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const parentItem = this.parentNode;
            parentItem.classList.toggle('open'); // Toggle the open class

            // Close other answers
            document.querySelectorAll('.faq-item').forEach(item => {
                if (item !== parentItem) {
                    item.classList.remove('open');
                }
            });
        });
    });
});



//Contact 
document.addEventListener('DOMContentLoaded', function () {
    const latitude = 20.9032;  // Latitude of Dhule, Maharashtra
    const longitude = 74.7749; // Longitude of Dhule, Maharashtra

    const map = L.map('map').setView([latitude, longitude], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    L.marker([latitude, longitude]).addTo(map)
        .bindPopup('Dhule, Maharashtra, India ')
        .openPopup();
});






 // Show the button when scrolling down
 window.onscroll = function () {
    scrollFunction();
};

function scrollFunction() {
    const backToTopButton = document.getElementById("back-to-top-btn");
    if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
        backToTopButton.style.display = "block"; // Show the button after 200px of scrolling
    } else {
        backToTopButton.style.display = "none"; // Hide the button when near the top
    }
}

// Smooth scroll to the top when the button is clicked
document.getElementById("back-to-top-btn").addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});