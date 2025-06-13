// Single-page navigation functionality
document.addEventListener('DOMContentLoaded', function() {
  // Get all navigation items
  const drawerNavItems = document.querySelectorAll('.drawer-nav-item a');
  const mobileNavItems = document.querySelectorAll('.mobile-nav .nav-item');
  const contentSections = document.querySelectorAll('.content-section');
  
  // Function to show a specific section
  function showSection(sectionId) {
    // Hide all sections
    contentSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the selected section
    const targetSection = document.getElementById(sectionId + '-section');
    if (targetSection) {
      targetSection.classList.add('active');
      
      // Update active state in drawer navigation
      document.querySelectorAll('.drawer-nav-item').forEach(item => {
        item.classList.remove('active');
      });
      
      const activeNavItem = document.getElementById('nav-' + sectionId);
      if (activeNavItem) {
        activeNavItem.classList.add('active');
      }
      
      // Update active state in mobile bottom navigation
      document.querySelectorAll('.mobile-nav .nav-item').forEach(item => {
        item.classList.remove('active');
      });
      
      const activeMobileNavItem = document.querySelector(`.mobile-nav .nav-item[data-section="${sectionId}"]`);
      if (activeMobileNavItem) {
        activeMobileNavItem.classList.add('active');
      }
      
      // Close the drawer after selection on mobile
      closeDrawer();
    }
  }
  
  // Add click event listeners to drawer navigation items
  drawerNavItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const sectionId = this.getAttribute('href').substring(1); // Remove the # from href
      showSection(sectionId);
    });
  });
  
  // Add click event listeners to mobile navigation items
  mobileNavItems.forEach(item => {
    item.addEventListener('click', function() {
      const sectionId = this.getAttribute('data-section');
      showSection(sectionId);
    });
  });
  
  // Function to close the drawer
  function closeDrawer() {
    const drawer = document.getElementById('drawer-nav');
    const overlay = document.getElementById('drawer-overlay');
    
    if (drawer && overlay) {
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = ''; // Restore scrolling
    }
  }
  
  // Check URL hash on page load
  function checkUrlHash() {
    const hash = window.location.hash;
    if (hash) {
      const sectionId = hash.substring(1); // Remove the # from hash
      showSection(sectionId);
    } else {
      // Default to dashboard if no hash
      showSection('dashboard');
    }
  }
  
  // Run on page load
  checkUrlHash();
  
  // Listen for hash changes
  window.addEventListener('hashchange', checkUrlHash);
}); 