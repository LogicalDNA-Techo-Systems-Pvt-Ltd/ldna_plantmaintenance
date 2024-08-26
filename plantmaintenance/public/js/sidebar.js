
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let sidebar = $(".layout-side-section");
        let toggleButton = $(".sidebar-toggle-btn");
        sidebar.css("display", "none");

        // Attach the click event to the toggle button
        if (!window.sidebarToggleBound) {
            toggleButton.off("click").on("click", function() {
                sidebar.slideToggle(100); 
                console.log("dsdfsfdsfs")
            });

            window.sidebarToggleBound = true;
        }
    }); 
});
