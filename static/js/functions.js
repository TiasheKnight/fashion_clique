// User info login
function loginUser() {
    const emailElement = document.getElementById('login-email');
    const passwordElement = document.getElementById('login-password');
    
    // Check if the elements exist
    console.log(emailElement, passwordElement);
  
    const email = emailElement.value;
    // const password = passwordElement.value;
    const password = CryptoJS.SHA256(passwordElement.value).toString();

    if (email=='admin'&& password=='admin'){
      window.location.href = '/dashboard'; 
      return;  // Stop further execution if admin
    }

    if (!email || !password) {
      showAlert('error','Please fill in both fields');
      return;
    }

    // const hashedPassword = CryptoJS.SHA256(password).toString();
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
        if (data.success) {
            // Redirect to homepage
            document.getElementById("successPopup").style.display = "flex";
            setTimeout(function () {
              window.location.reload();
            }, 2000);
        } else {
            ShowAlert('success','Something went wrong. Please try again later.'); // Show error message if login fails
        }
    })
    .catch(error => {
      showAlert('Error:', 'Something went wrong. Please try again later.');
    });
  }

// User logout
function logoutUser() {
  // Show the loading popup
  document.getElementById("loadingPopup").style.display = "flex";
    // Send a GET request to the logout route
    fetch('/logout', {
      method: 'GET', // You can also use POST if needed
  // })
  // .then(response => {
  //     if (response.ok) {
  //         // After successful logout, redirect to the login page or update UI
  //         window.location.href = '/login'; // Redirect to login page
  //     } else {
  //         alert('Logout failed. Please try again.');
  //     }
  // })
  // .catch(error => {
  //     console.error('Error during logout:', error);
  //     alert('An error occurred during logout.');
  });
  
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

  // // Simulate logout by clearing session data
  // sessionStorage.setItem('isLoggedIn', 'false');
  // window.location.href = "/login_P";  // Ensure redirection happens even if async delay is used
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
  
// Call checkLoginStatus after the page loads
window.onload = function() {
    checkLoginStatus();
};
  

// Register a new account
function registerAccount() {
  const form = document.getElementById('register-form');
  const name = form['register-name'].value;
  const email = form['register-email'].value;
  const phone = form['register-phone'].value;
  const address = form['register-address'].value;
  // const password = form['register-password'].value;
  // const cPassword = form['register-confirm-password'].value;
  const password = CryptoJS.SHA256(form['register-password'].value).toString();
  const cPassword = CryptoJS.SHA256(form['register-confirm-password'].value).toString();
  // Check if passwords match
  if (password !== cPassword) {
    showAlert("error","Passwords do not match.");
      return;
  }

  // Check if all fields are filled
  if (name && email && password && cPassword) {
      // Show the loading popup
      document.getElementById("loadingPopup").style.display = "flex";
      // const hashedPassword = CryptoJS.SHA256(password).toString();
      // Prepare data to send to Flask using AJAX (using JSON body)
      const registrationData = {
          name: name,
          email: email,
          password: password,
          phone: phone,
          address:address
      };

      fetch('/register', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(registrationData)  // Send the registration data as JSON
      })
      .then(response => response.json())
      .then(data => {
          // Hide the loading popup
          document.getElementById("loadingPopup").style.display = "none";

          // Check if registration was successful
          if (data.success) {
              // Show the success popup
              document.getElementById("successPopup").style.display = "flex";

              // Redirect to the login page after 2 seconds
              setTimeout(function() {
                  window.location.href = "/login_P";  // Navigate to login page
              }, 2000);
          } else {
              // Show an error message if registration failed
              showAlert("Registration failed. " ,'Something went wrong. Please try again later.');
          }
      })
      .catch(error => {
          // Show error if request fails
          showAlert('error',"An error occurred during registration. Please try again.");
          console.log(error);
      });
  } else {
      // Alert the user if not all fields are filled
      showAlert('error', "Please fill in all account details.");
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
      console.log(data.message);
      setTimeout(function() {
        document.getElementById("successPopup").style.display = "flex";
  
        setTimeout(function() {
            window.location.href = "/";  // Navigate to homepage
        }, 2000);
    });
      document.querySelector('form').reset();
    } else {
      showAlert('Error:', data.message);
      console.log(data.message);
    }
  })
  .catch(error => showAlert('Error:', error));
  console.log(error);
}

// Remove item from the list (example for cart or other list management)
function removeItem(button) {
  var row = button.closest('tr');
  row.classList.add('animate__fadeOutRight'); // Add animation

  setTimeout(function() {
      row.remove();
  }, 1000); // Delay for animation
}
  
// Function to update the cart count in the circle
function updateCartCount(count) {
  document.getElementById("cartCount").innerText = count;
}

// Adding a product to the cart
function addToCart(productId, quantity) {
  // Send the request to the backend to add the product to the cart

  fetch('/add_to_cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      'product_id': productId,
      'quantity': quantity
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update the cart count in the circle after the product is added to the cart
      updateCartCount(data.cart_count);
      setTimeout(function() {
        document.getElementById("successPopup").style.display = "flex";
    
        setTimeout(function() {
          document.getElementById("successPopup").style.display = "none";
        }, 1000);
      }, 2000);
    }
  })
  .catch(error => {
    console.error('Error adding to cart:', error);
  });

}

// Show shipping confirmation popup
function showShippingPopup() {
    // Check if user_id is in the session
    fetch('/check_login')  // Assuming '/check_login' checks if the user is logged in
    .then(response => response.json())
    .then(data => {
        if (data.logged_in) {
    document.getElementById("shippingPopup").style.display = "flex";
} else {
    // User is not logged in, alert and redirect to login page
    setTimeout(function() {
      showAlert('error','Please log in first');
  
      setTimeout(function() {
        window.location.href = '/login_P';
      }, 1000);
    });
    
    
    
}
})
.catch(error => {
console.error('Error:', error);
showAlert(error,'Something went wrong. Please try again later.');
});
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
        .then( data=> {
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
  const total = parseFloat(document.getElementById("total").textContent.replace('$', '').trim()); // Extract total price
  
  if (name && address && phone && !isNaN(total)) {
    closeShippingPopup();  // Close the shipping details popup

    // Show the loading popup
    document.getElementById("loadingPopup").style.display = "flex";

    // Prepare the order data to send to the backend
    const orderData = {
      name: name,
      address: address,
      phone: phone,
      total: total
    };

    // Send the data using fetch
    fetch('/submit_order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById("loadingPopup").style.display = "none"; // Hide the loading popup

        if (data.status === 'success') {
          console.log('Order placed successfully!');
          document.getElementById("loadingPopup").style.display = "none";
          document.getElementById("successPopup").style.display = "flex";
          setTimeout(function () {
            window.location.reload();
          }, 3000);
          // Optionally, redirect or update the UI
        } else {
          console.log(`Error: ${data.message}`);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        document.getElementById("loadingPopup").style.display = "none";
        console.log('Failed to place the order.');
      });
  } else {
    console.log('Please fill out all required fields and ensure the total price is valid.');
  }
}



// Newsletter submission
function newsletter(event) {
  event.preventDefault();  // Prevent the default form submission

  const email = document.getElementById('email').value;
  document.getElementById('email').value = '';  // Clear the email input field
  fetch('/newsletter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email,
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log(data.message);
      setTimeout(function() {
        document.getElementById("successPopup").style.display = "flex";
  
        setTimeout(function() {
          document.getElementById("successPopup").style.display = "none"; // Navigate to homepage
        }, 1000);
      }, 2000);  // Added a delay before showing the success popup

      document.querySelector('form').reset(); // Reset the form after successful submission
    } else {
      console.log('Error: ' + data.message);
    }
  })
  .catch(error => console.error('Error:', error));
}


// // Contact submission
// function contact() {
//   setTimeout(function() {
//       document.getElementById("successPopup").style.display = "flex";

//       setTimeout(function() {
//           window.location.href = "/";  // Navigate to homepage
//       }, 1000);
//   }, 1000);
// }

// function showAlert(message) {
//   // const alertElement = document.getElementById('alert');
//   // alertElement.textContent = "Invalid credit card number";
//   // Show the alert and hide it after 3 seconds
//   // alertElement.style.display = 'block';
//   // setTimeout(function() {
//   //     alertElement.style.display = 'none';
//   // }, 3000);
//   const alertElement = document.getElementById('alert');
//   // alertElement.querySelector('strong').textContent = type === 'error' ? 'Error!' : 'Success!';
//   // alertElement.querySelector('strong').nextSibling.textContent = ' ' + message;
//   alertElement.querySelector('strong').textContent = ' ' + message;
//   // Show the alert and hide it after 3 seconds
//   alertElement.style.display = 'block';
//   setTimeout(function() {
//       alertElement.style.display = 'none';
//   }, 3000);
// }

function showAlert(type, message) {
  const popup = document.getElementById('alert-popup');
  const alertElement = popup.querySelector('.alert');
  
  // Change the alert message and type (success or error)
  // alertElement.className = 'alert alert-' + type; // Update class for success/error styling
  alertElement.querySelector('strong').textContent = type;
  // alertElement.querySelector('strong').nextSibling.textContent = message;
   alertElement.querySelector('h6').textContent = message;
  // Show the popup
  popup.style.display = 'block';
}

// Function to hide the popup
function hideAlert() {
  const popup = document.getElementById('alert-popup');
  popup.style.display = 'none';
}