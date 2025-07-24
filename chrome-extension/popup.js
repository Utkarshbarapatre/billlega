document.addEventListener("DOMContentLoaded", () => {
  const statusDiv = document.getElementById("status")
  const captureBtn = document.getElementById("capture-btn")
  const dashboardBtn = document.getElementById("dashboard-btn")
  const settingsBtn = document.getElementById("settings-btn")

  // Check server status
  checkServerStatus()

  captureBtn.addEventListener("click", captureEmail)
  dashboardBtn.addEventListener("click", openDashboard)
  settingsBtn.addEventListener("click", openSettings)

  async function checkServerStatus() {
    try {
      const serverUrl = await getServerUrl()
      const response = await fetch(`${serverUrl}/api/extension/status`)

      if (response.ok) {
        statusDiv.textContent = "✅ Connected to server"
        statusDiv.className = "status connected"
        captureBtn.disabled = false
      } else {
        throw new Error("Server not responding")
      }
    } catch (error) {
      statusDiv.textContent = "❌ Server disconnected"
      statusDiv.className = "status disconnected"
      captureBtn.disabled = true
    }
  }

  async function captureEmail() {
    try {
      // Send message to content script
      const [tab] = await window.chrome.tabs.query({ active: true, currentWindow: true })

      window.chrome.tabs.sendMessage(tab.id, { action: "captureEmail" }, (response) => {
        if (response && response.success) {
          alert("Email captured successfully!")
        } else {
          alert("Failed to capture email. Make sure you are on Gmail.")
        }
      })
    } catch (error) {
      alert("Error capturing email: " + error.message)
    }
  }

  async function openDashboard() {
    const serverUrl = await getServerUrl()
    window.chrome.tabs.create({ url: serverUrl })
  }

  function openSettings() {
    window.chrome.runtime.openOptionsPage()
  }

  async function getServerUrl() {
    return new Promise((resolve) => {
      window.chrome.storage.sync.get(["serverUrl"], (result) => {
        resolve(result.serverUrl || "https://gracious-celebration.railway.internal")
      })
    })
  }
})
