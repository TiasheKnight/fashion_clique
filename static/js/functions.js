// User info login
function loginUser() {
    const emailElement = document.getElementById('login-email');
    const passwordElement = document.getElementById('login-password');
  
    // Check if the elements exist
    console.log(emailElement, passwordElement);
  
    const email = emailElement.value;
    const password = passwordElement.value;
  
    if (!email || !password) {
      alert('Please fill in both fields');
      return;
    }
  
    fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        window.location.href = '/';
      } else {
        alert(data.message || 'Login failed. Please try again.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

// User logout
function logoutUser() {
  // Show the loading popup
  document.getElementById("loadingPopup").style.display = "flex";

  // Simulate processing (loading) for 2 seconds
  setTimeout(function() {
      // Hide the loading popup
      document.getElementById("loadingPopup").style.display = "none";

      // Show the success popup
      document.getElementById("successPopup").style.display = "flex";

      // Redirect to the login page after 2 seconds
      setTimeout(function() {
          window.location.href = "/login_P";  // Navigate to the login page
      }, 2000);
  }, 2000);

  // Simulate logout by clearing session data
  sessionStorage.setItem('isLoggedIn', 'false');
  window.location.href = "/login_P";  // Ensure redirection happens even if async delay is used
}

// Check if the user is logged in
function checkLoginStatus() {
    fetch('/check_login')
      .then(response => response.json())
      .then(data => {
          const accountLink = document.getElementById('accountLink');
          
          // Check if the user is logged in by looking at 'logged_in' status
          if (data.logged_in) {
              accountLink.href = "/account";  // Redirect to account page if logged in
              accountLink.textContent = "Account";  // Optionally change the text to "Account"
          } else {
              accountLink.href = "/login_P";  // Redirect to login page if not logged in
              accountLink.textContent = "Login";  // Change text to "Login"
          }
      })
      .catch(error => console.error('Error checking login status:', error));
  }
  
  // Call this function on page load or when necessary
  checkLoginStatus();
  
// Call checkLoginStatus after the page loads
window.onload = function() {
    checkLoginStatus();
};
  

// Register a new account
function registerAccount() {
  const form = document.getElementById('register-form');
  const name = form['register-name'].value;
  const email = form['register-email'].value;
  const password = form['register-password'].value;
  const cPassword = form['register-confirm-password'].value;

  if (password !== cPassword) {
      alert("Passwords do not match.");
      return;
  }

  if (name && email && password && cPassword) {
      // Show the loading popup
      document.getElementById("loadingPopup").style.display = "flex";

      // Send registration data to Flask using AJAX
      fetch('/register', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: name, email: email, password: password })
      })
      .then(response => response.json())
      .then(data => {
          // Hide the loading popup
          document.getElementById("loadingPopup").style.display = "none";

          if (data.success) {
              // Show the success popup
              document.getElementById("successPopup").style.display = "flex";

              // Redirect to the login page after 2 seconds
              setTimeout(function() {
                  window.location.href = "/login_P";  // Navigate to login page
              }, 2000);
          } else {
              alert("Registration failed. Please try again.");
          }
      })
      .catch(error => {
          alert("An error occurred.");
          console.log(error);
      });
  } else {
      alert("Please fill in all account details.");
  }
}

function sendMessage() {
  const fullName = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;

  fetch('/send_message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      full_name: fullName,
      email: email,
      message: message,
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert(data.message);
      document.querySelector('form').reset();
    } else {
      alert('Error: ' + data.message);
    }
  })
  .catch(error => console.error('Error:', error));
}

// Remove item from the list (example for cart or other list management)
function removeItem(button) {
  var row = button.closest('tr');
  row.classList.add('animate__fadeOutRight'); // Add animation

  setTimeout(function() {
      row.remove();
  }, 500); // Delay for animation
}

// Show shipping confirmation popup
function showShippingPopup() {
  document.getElementById("shippingPopup").style.display = "flex";
}

// Close shipping popup
function closeShippingPopup() {
  document.getElementById("shippingPopup").style.display = "none";
}
document.querySelectorAll('.remove-item').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();  // Prevent default form submission
        const productId = this.getAttribute('data-product-id');  // Get product_id from button's data attribute
        
        // Send a POST request to remove the product from the cart
        fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'product_id=' + productId
        })
        .then(response => response.json())
        .then(data => {
            // Optionally, update the cart page or show a success message
            console.log('Product removed from cart!');
            location.reload();  // Reload the page to reflect changes
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

// Proceed to checkout after confirming shipping info
function Checkout() {
  const name = document.getElementById("name").value;
  const address = document.getElementById("address").value;
  const phone = document.getElementById("phone").value;

  if (name && address && phone) {
      closeShippingPopup();  // Close the shipping details popup
      
      // Show the loading popup
      document.getElementById("loadingPopup").style.display = "flex";

      // Prepare the order data to send to the backend
      const orderData = {
          address: address,
          phone: phone
      };

      // Send the order details to the backend using fetch
      fetch('/submit_order', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(orderData)  // Send order data as JSON
      })
      .then(response => response.json())
      .then(data => {
          // If the order is successful, show success popup
          if (data.status === 'success') {
              setTimeout(function() {
                  document.getElementById("loadingPopup").style.display = "none";  // Hide loading popup
                  document.getElementById("successPopup").style.display = "flex";  // Show success popup

                  // Redirect to the home page or another page after a short delay
                  setTimeout(function() {
                      window.location.href = "/";  // Navigate to the home page or any other page
                  }, 2000);
              }, 2000);
          } else {
              alert("There was an error with your order. Please try again.");
          }
      })
      .catch(error => {
          console.error('Error:', error);
          alert("An error occurred while placing the order.");
      });
  } else {
      alert("Please fill in all shipping details.");
  }
}


// Newsletter submission
function newsletter() {
  setTimeout(function() {
      document.getElementById("successPopup").style.display = "flex";

      setTimeout(function() {
          window.location.href = "/";  // Navigate to homepage
      }, 1000);
  }, 1000);
}

// Contact submission
function contact() {
  setTimeout(function() {
      document.getElementById("successPopup").style.display = "flex";

      setTimeout(function() {
          window.location.href = "/";  // Navigate to homepage
      }, 1000);
  }, 1000);
}