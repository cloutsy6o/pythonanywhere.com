document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
    }
    
    // Close mobile menu when clicking outside or on links
    document.addEventListener('click', function(event) {
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            if (!mobileMenu.contains(event.target) && 
                !mobileMenuBtn.contains(event.target)) {
                mobileMenu.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        }
    });
    
    // Close mobile menu when clicking on links
    const mobileLinks = document.querySelectorAll('.mobile-nav a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileMenu.classList.remove('active');
            document.body.classList.remove('menu-open');
        });
    });
    
    // Initialize cart count
    updateCartCountFromStorage();
    
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProducts();
                return false;
            }
        });
    }
    
    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            searchProducts();
        });
    }
    
    // Categories dropdown
    const allCategories = document.querySelector('.all-categories');
    const categoriesDropdown = document.querySelector('.categories-dropdown');
    
    if (allCategories && categoriesDropdown) {
        allCategories.addEventListener('click', function(e) {
            e.preventDefault();
            categoriesDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!allCategories.contains(event.target) && 
                !categoriesDropdown.contains(event.target)) {
                categoriesDropdown.classList.remove('show');
            }
        });
    }
});

// Add to cart function
function addToCart(productId, quantity = 1) {
    console.log('Adding to cart:', productId);
    
    // Get CSRF token
    const csrfToken = getCookie('csrftoken');
    if (!csrfToken) {
        console.error('CSRF token not found');
        showMessage('Sicherheitsfehler. Bitte Seite neu laden.', 'error');
        return;
    }
    
    fetch('/cart/add/' + productId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'success') {
            updateCartCount(data.cart_count || data.cart_count);
            showMessage('Produkt wurde zum Warenkorb hinzugefügt', 'success');
            
            // If on product page, update the cart button
            const cartBtn = document.querySelector('.btn-add-cart');
            if (cartBtn) {
                cartBtn.innerHTML = '<i class="fas fa-check"></i> Im Warenkorb';
                cartBtn.classList.add('added');
                setTimeout(() => {
                    cartBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> In den Warenkorb';
                    cartBtn.classList.remove('added');
                }, 2000);
            }
        } else {
            showMessage(data.message || 'Fehler beim Hinzufügen zum Warenkorb', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showMessage('Fehler beim Hinzufügen zum Warenkorb. Bitte versuchen Sie es erneut.', 'error');
    });
}

// Update cart count
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
    });
    localStorage.setItem('cart_count', count);
}

function updateCartCountFromStorage() {
    const count = localStorage.getItem('cart_count') || 0;
    updateCartCount(count);
}

// Show message/alert
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.alert-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert-message ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span>${message}</span>
            <button class="close-btn">&times;</button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Show message with animation
    setTimeout(() => {
        messageDiv.classList.add('show');
    }, 10);
    
    // Auto remove after 5 seconds
    const autoRemove = setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 300);
    }, 5000);
    
    // Close button functionality
    const closeBtn = messageDiv.querySelector('.close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            clearTimeout(autoRemove);
            messageDiv.classList.remove('show');
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 300);
        });
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Search functionality
function searchProducts() {
    const searchInput = document.querySelector('.search-input');
    const searchTerm = searchInput ? searchInput.value.trim() : '';
    
    if (searchTerm) {
        window.location.href = `/search/?q=${encodeURIComponent(searchTerm)}`;
    } else {
        showMessage('Bitte geben Sie einen Suchbegriff ein', 'error');
    }
}

// Product quantity controls
function increaseQuantity(button) {
    const input = button.parentElement.querySelector('.quantity-input');
    if (input) {
        input.value = parseInt(input.value) + 1;
    }
}

function decreaseQuantity(button) {
    const input = button.parentElement.querySelector('.quantity-input');
    if (input && parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// Add to wishlist
function addToWishlist(productId) {
    const csrfToken = getCookie('csrftoken');
    
    fetch('/wishlist/add/' + productId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage('Produkt zur Wunschliste hinzugefügt', 'success');
        } else {
            showMessage(data.message || 'Fehler beim Hinzufügen zur Wunschliste', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Fehler beim Hinzufügen zur Wunschliste', 'error');
    });
}

// Remove from cart
function removeFromCart(itemId) {
    const csrfToken = getCookie('csrftoken');
    
    fetch('/cart/remove/' + itemId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage('Produkt aus dem Warenkorb entfernt', 'success');
            // Reload or update cart
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Fehler beim Entfernen', 'error');
    });
}

// Update cart quantity
function updateCartQuantity(itemId, quantity) {
    if (quantity < 1) {
        removeFromCart(itemId);
        return;
    }
    
    const csrfToken = getCookie('csrftoken');
    
    fetch('/cart/update/' + itemId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update total
            document.querySelector('.cart-total').textContent = data.total + ' €';
            updateCartCount(data.cart_count);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Fehler beim Aktualisieren', 'error');
    });
}
