// Content script for Gmail integration
;(() => {
  // Declare chrome variable
  const chrome = window.chrome

  // Add capture button to Gmail interface
  function addCaptureButton() {
    if (document.querySelector(".legal-billing-capture")) return

    const toolbar = document.querySelector('[role="toolbar"]')
    if (!toolbar) return

    const captureBtn = document.createElement("button")
    captureBtn.className = "legal-billing-capture"
    captureBtn.innerHTML = "⚖️ Capture for Billing"
    captureBtn.style.cssText = `
            background: #1a73e8;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            margin-left: 8px;
            cursor: pointer;
            font-size: 14px;
        `

    captureBtn.addEventListener("click", captureCurrentEmail)
    toolbar.appendChild(captureBtn)
  }

  // Capture current email
  async function captureCurrentEmail() {
    try {
      const emailData = extractEmailData()
      if (!emailData) {
        alert("Could not extract email data")
        return
      }

      // Send to server
      const serverUrl = await getServerUrl()
      const response = await fetch(`${serverUrl}/api/extension/capture`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(emailData),
      })

      if (response.ok) {
        showNotification("Email captured successfully!", "success")
      } else {
        throw new Error("Server error")
      }
    } catch (error) {
      showNotification("Failed to capture email: " + error.message, "error")
    }
  }

  // Extract email data from Gmail DOM
  function extractEmailData() {
    const subject = document.querySelector("[data-thread-perm-id] h2")?.textContent || ""
    const sender = document.querySelector("[email]")?.getAttribute("email") || ""
    const body = document.querySelector("[data-message-id] .ii.gt div")?.textContent || ""

    return {
      id: Date.now().toString(),
      subject: subject,
      sender: sender,
      recipient: "extracted@gmail.com", // Simplified
      body: body,
      date_sent: new Date().toISOString(),
      source: "chrome_extension",
    }
  }

  // Show notification
  function showNotification(message, type) {
    const notification = document.createElement("div")
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            background: ${type === "success" ? "#4caf50" : "#f44336"};
        `
    notification.textContent = message

    document.body.appendChild(notification)

    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  // Get server URL from storage
  function getServerUrl() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(["serverUrl"], (result) => {
        resolve(result.serverUrl || "https://gracious-celebration.railway.internal")
      })
    })
  }

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "captureEmail") {
      captureCurrentEmail()
        .then(() => {
          sendResponse({ success: true })
        })
        .catch((error) => {
          sendResponse({ success: false, error: error.message })
        })
      return true // Keep message channel open
    }
  })

  // Initialize
  function init() {
    // Wait for Gmail to load
    const observer = new MutationObserver(() => {
      if (document.querySelector('[role="toolbar"]')) {
        addCaptureButton()
      }
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    })

    // Try to add button immediately
    addCaptureButton()
  }

  // Start when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init)
  } else {
    init()
  }
})()
