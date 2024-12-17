// User info login
function loginUser() {
  const form = document.getElementById('login-form');
  const email = form['login-email'].value;
  const password = form['login-password'].value;

  if (email && password) {
      // Show the loading popup
      document.getElementById("loadingPopup").style.display = "flex";

      // Send login data to Flask using AJAX
      fetch('/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: email, password: password })
      })
      .then(response => response.json())
      .then(data => {
          // Hide the loading popup
          document.getElementById("loadingPopup").style.display = "none";

          if (data.success) {
              // Show the success popup
              document.getElementById("successPopup").style.display = "flex";

              // Redirect to the account page after 2 seconds
              setTimeout(function() {
                  window.location.href = "/account";  // Navigate to account page
              }, 2000);
          } else {
              alert("Invalid login credentials.");
          }
      })
      .catch(error => {
          alert("An error occurred.");
          console.log(error);
      });
  } else {
      alert("Please fill in all login details.");
  }
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
          if (data.logged_in) {
              accountLink.href = "/account";  // Redirect to account page if logged in
          } else {
              accountLink.href = "/login_P";  // Redirect to login page if not logged in
          }
      });
}

// Call checkLoginStatus when the page loads
window.onload = checkLoginStatus;

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
function removeItem(productId) {
    // Send the product ID to the server to remove it from the session
    fetch('/remove_from_cart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'product_id=' + productId,  // Send product ID in the body
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Reload the cart page to reflect the changes
        window.location.reload();
      } else {
        alert('Failed to remove item');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
// Proceed to checkout after confirming shipping info
function proceedToCheckout() {
  const name = document.getElementById("name").value;
  const address = document.getElementById("address").value;
  const phone = document.getElementById("phone").value;

  if (name && address && phone) {
      closeShippingPopup();

      document.getElementById("loadingPopup").style.display = "flex";

      setTimeout(function() {
          document.getElementById("loadingPopup").style.display = "none";
          document.getElementById("successPopup").style.display = "flex";

          setTimeout(function() {
              window.location.href = "/checkout";  // Navigate to checkout page
          }, 2000);
      }, 2000);
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