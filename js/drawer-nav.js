// Drawer Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
  const drawer = document.getElementById('drawer-nav');
  const overlay = document.getElementById('drawer-overlay');
  const toggleButton = document.getElementById('mobile-menu-toggle');
  const closeButton = document.getElementById('drawer-close');
  
  // Open drawer when menu button is clicked
  toggleButton.addEventListener('click', function() {
    openDrawer();
  });
  
  // Close drawer when close button is clicked
  closeButton.addEventListener('click', function() {
    closeDrawer();
  });
  
  // Close drawer when overlay is clicked
  overlay.addEventListener('click', function() {
    closeDrawer();
  });
  
  // Function to open the drawer
  function openDrawer() {
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden'; // Prevent scrolling behind drawer
  }
  
  // Function to close the drawer
  function closeDrawer() {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = ''; // Restore scrolling
  }
  
  // Make the closeDrawer function available globally
  window.closeDrawer = closeDrawer;
  
  // Handle swipe to open the drawer
  let touchStartX = 0;
  let touchEndX = 0;
  
  document.addEventListener('touchstart', function(event) {
    touchStartX = event.changedTouches[0].screenX;
  }, false);
  
  document.addEventListener('touchend', function(event) {
    touchEndX = event.changedTouches[0].screenX;
    handleSwipe();
  }, false);
  
  function handleSwipe() {
    const swipeThreshold = 70; // Minimum distance to consider it a swipe
    const edgeThreshold = 30; // Distance from screen edge to start swipe
    
    // If drawer is closed and user swipes right from left edge
    if (!drawer.classList.contains('open') && 
        touchStartX < edgeThreshold && 
        touchEndX - touchStartX > swipeThreshold) {
      openDrawer();
    }
    
    // If drawer is open and user swipes left
    if (drawer.classList.contains('open') && 
        touchStartX - touchEndX > swipeThreshold) {
      closeDrawer();
    }
  }
  
  // Add active class to current section in drawer
  function updateActiveNavItem() {
    const hash = window.location.hash || '#dashboard';
    const sectionId = hash.substring(1);
    
    // Remove active class from all items
    document.querySelectorAll('.drawer-nav-item').forEach(item => {
      item.classList.remove('active');
    });
    
    // Add active class to current section
    const activeItem = document.getElementById('nav-' + sectionId);
    if (activeItem) {
      activeItem.classList.add('active');
    }
  }
  
  // Update active nav item on page load
  updateActiveNavItem();
  
  // Update active nav item when hash changes
  window.addEventListener('hashchange', updateActiveNavItem);
}); 