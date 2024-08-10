// Function to create and display the popup
function showPopup() {
  // Create overlay
  const overlay = document.createElement("div");
  overlay.className = "popup-overlay";

  // Create popup content
  const popup = document.createElement("div");
  popup.className = "popup-content";
  popup.innerHTML = `
      <img src="./icons/icon16.png" alt="warning" /><br />
      <h1>Warning</h1>
      <p>This website has been reported as a phishing site.</p>
      <button id="close-popup">Close</button>
    `;

  // Append popup to overlay
  overlay.appendChild(popup);

  // Append overlay to body
  document.body.appendChild(overlay);

  // Add event listener to close button
  document.getElementById("close-popup").addEventListener("click", () => {
    document.body.removeChild(overlay);
  });
}
showPopup();
