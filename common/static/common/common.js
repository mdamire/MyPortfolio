window.onload = function() {
    // Get the current URL
    var currentUrl = window.location.href;

    // Find all navigation links
    var navLinks = document.querySelectorAll('.nav-link');

    // Loop through each navigation link
    navLinks.forEach(function(navLink) {
        // Check if the href attribute of the navigation link matches the current URL
        if (navLink.href === currentUrl && !navLink.classList.contains('active')) {
            // Add the "active" class to the navigation link
            navLink.classList.add('active');
        }
    });
};
