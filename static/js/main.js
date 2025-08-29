console.log("Main JavaScript file loaded.");

// Main JavaScript file for Real Estate Management System
document.addEventListener("DOMContentLoaded", function() {
    // Dark mode toggle functionality
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;
    
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        htmlElement.setAttribute('data-bs-theme', 'dark');
        darkModeToggle.checked = true;
        updateDarkModeIcon(true);
    }
    
    // Toggle dark mode when the switch is clicked
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                htmlElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('darkMode', 'enabled');
                updateDarkModeIcon(true);
                showToast('Dark mode enabled', 'dark');
            } else {
                htmlElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('darkMode', 'disabled');
                updateDarkModeIcon(false);
                showToast('Light mode enabled', 'light');
            }
        });
    }
    
    // Update the dark mode toggle icon
    function updateDarkModeIcon(isDarkMode) {
        const iconElement = darkModeToggle.nextElementSibling.querySelector('i');
        if (isDarkMode) {
            iconElement.classList.remove('bi-moon');
            iconElement.classList.add('bi-sun');
        } else {
            iconElement.classList.remove('bi-sun');
            iconElement.classList.add('bi-moon');
        }
    }
    // Toggle sidebar on mobile
    const sidebarWrapper = document.getElementById("sidebar-wrapper");
    const menuToggle = document.getElementById("menu-toggle");
    const wrapper = document.getElementById("wrapper");

    if (menuToggle && sidebarWrapper) {
        menuToggle.addEventListener("click", function(e) {
            e.preventDefault();
            wrapper.classList.toggle("toggled");
        });
    }
    
    // Hide sidebar when clicking outside on mobile
    const pageContentWrapper = document.getElementById("page-content-wrapper");
    if (pageContentWrapper) {
        pageContentWrapper.addEventListener("click", function() {
            if (window.innerWidth < 768 && wrapper && wrapper.classList.contains("toggled")) {
                wrapper.classList.remove("toggled");
            }
        });
    }
    
    // Handle window resize events for responsive behavior
    window.addEventListener('resize', function() {
        // Close sidebar on small screens when resizing
        if (window.innerWidth < 768 && wrapper && wrapper.classList.contains("toggled")) {
            wrapper.classList.remove("toggled");
        }
        
        // Switch between table and card views based on screen size
        const tableViews = document.querySelectorAll('.table-view');
        const cardViews = document.querySelectorAll('.mobile-card-view');
        const tableViewBtns = document.querySelectorAll('#table-view-btn');
        const cardViewBtns = document.querySelectorAll('#card-view-btn');
        
        if (window.innerWidth < 576) {
            // Switch to card view on small screens
            tableViews.forEach(view => view.classList.add('d-none'));
            cardViews.forEach(view => view.classList.remove('d-none'));
            tableViewBtns.forEach(btn => btn.classList.remove('active'));
            cardViewBtns.forEach(btn => btn.classList.add('active'));
        } else if (window.innerWidth >= 768) {
            // Switch to table view on larger screens
            tableViews.forEach(view => view.classList.remove('d-none'));
            cardViews.forEach(view => view.classList.add('d-none'));
            tableViewBtns.forEach(btn => btn.classList.add('active'));
            cardViewBtns.forEach(btn => btn.classList.remove('active'));
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date picker initialization for date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        input.classList.add('form-control');
    });

    // Handle property image preview
    const propertyImageInput = document.querySelector('#id_image');
    const imagePreview = document.querySelector('#image-preview');
    
    if (propertyImageInput && imagePreview) {
        propertyImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Handle dynamic form fields (for multiple units in a property)
    const addUnitButton = document.querySelector('#add-unit');
    if (addUnitButton) {
        addUnitButton.addEventListener('click', function() {
            const unitContainer = document.querySelector('#units-container');
            const unitCount = unitContainer.querySelectorAll('.unit-row').length;
            
            const unitRow = document.createElement('div');
            unitRow.className = 'unit-row row mb-3';
            unitRow.innerHTML = `
                <div class="col-md-3">
                    <input type="text" name="unit_number_${unitCount}" class="form-control" placeholder="Unit Number">
                </div>
                <div class="col-md-3">
                    <input type="number" name="unit_size_${unitCount}" class="form-control" placeholder="Size (sq ft)">
                </div>
                <div class="col-md-3">
                    <input type="number" name="unit_rent_${unitCount}" class="form-control" placeholder="Monthly Rent">
                </div>
                <div class="col-md-2">
                    <select name="unit_status_${unitCount}" class="form-control">
                        <option value="available">Available</option>
                        <option value="occupied">Occupied</option>
                        <option value="maintenance">Maintenance</option>
                    </select>
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-danger remove-unit"><i class="bi bi-trash"></i></button>
                </div>
            `;
            
            unitContainer.appendChild(unitRow);
            
            // Add event listener to the remove button
            unitRow.querySelector('.remove-unit').addEventListener('click', function() {
                this.closest('.unit-row').remove();
                showToast('Unit removed successfully', 'success');
            });
            
            // Show a toast notification
            showToast('New unit added', 'info');
        });
    }
    
    // Handle existing remove unit buttons
    document.querySelectorAll('.remove-unit').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.unit-row').remove();
            showToast('Unit removed successfully', 'success');
        });
    });
    
    // Toast notification system
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Initialize and show the toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    }
});
