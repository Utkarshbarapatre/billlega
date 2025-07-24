// Background script for the extension
const chrome = window.chrome // Declare the chrome variable

chrome.runtime.onInstalled.addListener(() => {
  console.log("Legal Billing Email Summarizer extension installed")

  // Set default server URL to Railway domain
  chrome.storage.sync.set({
    serverUrl: "https://gracious-celebration.railway.internal",
  })
})

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Open popup (this is handled automatically by manifest)
})

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getServerUrl") {
    chrome.storage.sync.get(["serverUrl"], (result) => {
      sendResponse({ serverUrl: result.serverUrl || "https://gracious-celebration.railway.internal" })
    })
    return true
  }
})
