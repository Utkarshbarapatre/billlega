"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Mail,
  Link,
  TestTube,
  Download,
  CheckSquare,
  Square,
  Bot,
  Wand2,
  Upload,
  ArrowUp,
  Puzzle,
  List,
  Search,
  MailOpen,
  FileText,
  Gavel,
  Edit,
  Eye,
  Clock,
} from "lucide-react"

interface Email {
  id: string
  subject: string
  sender: string
  recipient: string
  body: string
  date_sent: string
  summary?: string
  billing_hours?: number
  billing_description?: string
  pushed_to_clio?: boolean
}

interface Summary {
  id: number
  email_id: string
  subject: string
  summary: string
  billing_hours: number
  billing_description: string
  date_sent: string
  pushed_to_clio: boolean
}

interface ConnectionStatus {
  gmail: boolean
  clio: boolean
}

interface Counts {
  emails: number
  summaries: number
  selected: number
}

export default function LegalBillingSummarizer() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    gmail: false,
    clio: false,
  })

  const [counts, setCounts] = useState<Counts>({
    emails: 0,
    summaries: 0,
    selected: 0,
  })

  const [emails, setEmails] = useState<Email[]>([])
  const [summaries, setSummaries] = useState<Summary[]>([])
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set())
  const [activeTab, setActiveTab] = useState("emails")
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState("")
  const [editingSummary, setEditingSummary] = useState<Summary | null>(null)
  const [daysFilter, setDaysFilter] = useState("7")
  const [emailFilter, setEmailFilter] = useState("all")
  const [summaryFilter, setSummaryFilter] = useState("all")
  const [emailSearch, setEmailSearch] = useState("")
  const [summarySearch, setSummarySearch] = useState("")

  const API_BASE =
    typeof window !== "undefined"
      ? window.location.origin.includes("localhost")
        ? "http://localhost:8000/api"
        : `${window.location.origin}/api`
      : "/api"

  useEffect(() => {
    checkConnectionStatus()
    updateCounts()
  }, [])

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setConnectionStatus({
        gmail: data.gmail_connected || false,
        clio: data.clio_connected || false,
      })
    } catch (error) {
      console.error("Error checking connection status:", error)
      // Set default disconnected state on error
      setConnectionStatus({
        gmail: false,
        clio: false,
      })
    }
  }

  const updateCounts = async () => {
    try {
      const [emailsRes, summariesRes] = await Promise.all([
        fetch(`${API_BASE}/gmail/emails/stored`).catch(() => ({ json: () => ({ emails: [] }) })),
        fetch(`${API_BASE}/summarizer/summaries`).catch(() => ({ json: () => ({ summaries: [] }) })),
      ])

      const emailsData = await emailsRes.json()
      const summariesData = await summariesRes.json()

      setCounts({
        emails: emailsData.emails?.length || 0,
        summaries: summariesData.summaries?.length || 0,
        selected: selectedEmails.size,
      })
    } catch (error) {
      console.error("Error updating counts:", error)
      // Set default counts on error
      setCounts({
        emails: 0,
        summaries: 0,
        selected: selectedEmails.size,
      })
    }
  }

  const handleConnectGmail = async () => {
    setIsLoading(true)
    setLoadingMessage("Connecting to Gmail...")

    try {
      const response = await fetch(`${API_BASE}/gmail/authenticate`, {
        method: "POST",
      })
      const data = await response.json()

      if (data.success) {
        setConnectionStatus((prev) => ({ ...prev, gmail: true }))
        alert("Gmail connected successfully!")
      } else {
        alert("Gmail connection failed: " + data.message)
      }
    } catch (error) {
      console.error("Gmail connection error:", error)
      alert("Gmail connection failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleConnectClio = async () => {
    setIsLoading(true)
    setLoadingMessage("Redirecting to Clio...")

    try {
      const response = await fetch(`${API_BASE}/clio/auth`)
      const data = await response.json()

      if (data.auth_url) {
        window.location.href = data.auth_url
      } else {
        alert("Failed to get Clio auth URL")
      }
    } catch (error) {
      console.error("Clio connection error:", error)
      alert("Clio connection failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestClio = async () => {
    setIsLoading(true)
    setLoadingMessage("Testing Clio connection...")

    try {
      const response = await fetch(`${API_BASE}/clio/test`)
      const data = await response.json()

      if (data.connected) {
        alert(`Clio test successful!\nUser: ${data.user?.name || "Unknown"}\nMessage: ${data.message}`)
      } else {
        alert(`Clio test failed: ${data.message}`)
      }
    } catch (error) {
      console.error("Clio test error:", error)
      alert("Clio test failed. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleFetchEmails = async () => {
    setIsLoading(true)
    setLoadingMessage("Fetching emails from Gmail...")

    try {
      const response = await fetch(`${API_BASE}/gmail/emails?days_back=${daysFilter}&max_results=100`)
      const data = await response.json()

      if (data.success) {
        setEmails(data.emails || [])
        updateCounts()
        alert(`Fetched ${data.emails_fetched} emails (${data.new_emails} new)`)
      } else {
        alert("Failed to fetch emails: " + data.message)
      }
    } catch (error) {
      console.error("Email fetch error:", error)
      alert("Failed to fetch emails. Please check your Gmail connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateSummaries = async () => {
    setIsLoading(true)
    setLoadingMessage("Generating AI summaries...")

    try {
      const response = await fetch(`${API_BASE}/summarizer/generate`, {
        method: "POST",
      })
      const data = await response.json()

      if (data.success) {
        alert(`Generated ${data.summaries_generated} summaries successfully!`)
        updateCounts()
        loadSummaries()
      } else {
        alert("Failed to generate summaries: " + data.message)
      }
    } catch (error) {
      console.error("Summary generation error:", error)
      alert("Failed to generate summaries. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handlePushToClio = async () => {
    setIsLoading(true)
    setLoadingMessage("Pushing summaries to Clio...")

    try {
      const response = await fetch(`${API_BASE}/clio/push-entries`, {
        method: "POST",
      })
      const data = await response.json()

      if (data.success) {
        alert(`Successfully pushed ${data.pushed_count} entries to Clio!`)
        loadSummaries()
      } else {
        alert("Failed to push to Clio: " + data.message)
      }
    } catch (error) {
      console.error("Clio push error:", error)
      alert("Failed to push to Clio. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const loadStoredEmails = async () => {
    try {
      const response = await fetch(`${API_BASE}/gmail/emails/stored`)
      const data = await response.json()
      setEmails(data.emails || [])
    } catch (error) {
      console.error("Error loading stored emails:", error)
    }
  }

  const loadSummaries = async () => {
    try {
      const response = await fetch(`${API_BASE}/summarizer/summaries`)
      const data = await response.json()
      setSummaries(data.summaries || [])
    } catch (error) {
      console.error("Error loading summaries:", error)
    }
  }

  const handleEmailSelection = (emailId: string, checked: boolean) => {
    const newSelected = new Set(selectedEmails)
    if (checked) {
      newSelected.add(emailId)
    } else {
      newSelected.delete(emailId)
    }
    setSelectedEmails(newSelected)
    setCounts((prev) => ({ ...prev, selected: newSelected.size }))
  }

  const handleSelectAll = () => {
    const allEmailIds = new Set(emails.map((email) => email.id))
    setSelectedEmails(allEmailIds)
    setCounts((prev) => ({ ...prev, selected: allEmailIds.size }))
  }

  const handleClearSelection = () => {
    setSelectedEmails(new Set())
    setCounts((prev) => ({ ...prev, selected: 0 }))
  }

  const handleEditSummary = async (summary: Summary) => {
    try {
      const response = await fetch(`${API_BASE}/summarizer/summaries/${summary.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          billing_hours: summary.billing_hours,
          billing_description: summary.billing_description,
          summary: summary.summary,
        }),
      })

      const data = await response.json()

      if (data.success) {
        alert("Summary updated successfully!")
        loadSummaries()
        setEditingSummary(null)
      } else {
        alert("Failed to update summary: " + data.message)
      }
    } catch (error) {
      console.error("Error updating summary:", error)
      alert("Failed to update summary. Please try again.")
    }
  }

  const filteredEmails = emails.filter((email) => {
    const matchesFilter =
      emailFilter === "all" ||
      (emailFilter === "unsummarized" && !email.summary) ||
      (emailFilter === "summarized" && email.summary) ||
      (emailFilter === "unpushed" && !email.pushed_to_clio)

    const matchesSearch =
      emailSearch === "" ||
      email.subject.toLowerCase().includes(emailSearch.toLowerCase()) ||
      email.sender.toLowerCase().includes(emailSearch.toLowerCase()) ||
      email.body.toLowerCase().includes(emailSearch.toLowerCase())

    return matchesFilter && matchesSearch
  })

  const filteredSummaries = summaries.filter((summary) => {
    const matchesFilter =
      summaryFilter === "all" ||
      (summaryFilter === "unpushed" && !summary.pushed_to_clio) ||
      (summaryFilter === "pushed" && summary.pushed_to_clio)

    const matchesSearch =
      summarySearch === "" ||
      summary.subject.toLowerCase().includes(summarySearch.toLowerCase()) ||
      summary.summary.toLowerCase().includes(summarySearch.toLowerCase()) ||
      summary.billing_description.toLowerCase().includes(summarySearch.toLowerCase())

    return matchesFilter && matchesSearch
  })

  useEffect(() => {
    if (activeTab === "emails") {
      loadStoredEmails()
    } else if (activeTab === "summaries") {
      loadSummaries()
    }
  }, [activeTab])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-purple-800">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <Card className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-lg font-medium">{loadingMessage}</p>
          </Card>
        </div>
      )}

      <div className="container mx-auto p-6 max-w-7xl">
        {/* Header */}
        <header className="text-center mb-8 text-white">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Gavel className="w-10 h-10" />
            <h1 className="text-4xl font-bold">Legal Billing Email Summarizer</h1>
          </div>
          <p className="text-xl opacity-90 mb-6">
            Automatically fetch Gmail emails, generate AI summaries, and sync with Clio
          </p>
          <div className="flex justify-center gap-3 mb-4">
            <Button variant="secondary" size="sm" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
              <Puzzle className="w-4 h-4 mr-2" />
              Chrome Extension
            </Button>
            <Button variant="secondary" size="sm" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
              <List className="w-4 h-4 mr-2" />
              Bulk Actions
            </Button>
          </div>
          <div className="text-center">
            <Badge variant="outline" className="bg-white/10 text-white border-white/30">
              API: {API_BASE}
            </Badge>
          </div>
        </header>

        {/* Status Bar */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardContent className="p-4 flex justify-between items-center">
              <span className="font-semibold text-gray-600">Gmail:</span>
              <Badge
                variant={connectionStatus.gmail ? "default" : "destructive"}
                className={connectionStatus.gmail ? "bg-green-500" : ""}
              >
                {connectionStatus.gmail ? "Connected" : "Disconnected"}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 flex justify-between items-center">
              <span className="font-semibold text-gray-600">Clio:</span>
              <Badge
                variant={connectionStatus.clio ? "default" : "destructive"}
                className={connectionStatus.clio ? "bg-green-500" : ""}
              >
                {connectionStatus.clio ? "Connected" : "Disconnected"}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 flex justify-between items-center">
              <span className="font-semibold text-gray-600">Emails:</span>
              <Badge variant="outline" className="bg-gray-100">
                {counts.emails}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 flex justify-between items-center">
              <span className="font-semibold text-gray-600">Summaries:</span>
              <Badge variant="outline" className="bg-gray-100">
                {counts.summaries}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 flex justify-between items-center">
              <span className="font-semibold text-gray-600">Selected:</span>
              <Badge variant="outline" className="bg-gray-100">
                {counts.selected}
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Action Panels */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Connect Services */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">1. Connect Services</h3>
              <div className="space-y-3">
                <Button
                  onClick={handleConnectGmail}
                  className="w-full bg-blue-500 hover:bg-blue-600"
                  disabled={connectionStatus.gmail}
                >
                  <Mail className="w-4 h-4 mr-2" />
                  {connectionStatus.gmail ? "Gmail Connected" : "Connect Gmail"}
                </Button>
                <Button
                  onClick={handleConnectClio}
                  className="w-full bg-blue-500 hover:bg-blue-600"
                  disabled={connectionStatus.clio}
                >
                  <Link className="w-4 h-4 mr-2" />
                  {connectionStatus.clio ? "Clio Connected" : "Connect Clio"}
                </Button>
                <Button onClick={handleTestClio} variant="outline" size="sm" className="w-full bg-transparent">
                  <TestTube className="w-4 h-4 mr-2" />
                  Test Clio
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Email Management */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">2. Email Management</h3>
              <div className="space-y-3">
                <Button
                  onClick={handleFetchEmails}
                  variant="outline"
                  className="w-full bg-transparent"
                  disabled={!connectionStatus.gmail}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Fetch Emails
                </Button>
                <Button onClick={handleSelectAll} variant="outline" size="sm" className="w-full bg-transparent">
                  <CheckSquare className="w-4 h-4 mr-2" />
                  Select All
                </Button>
                <Button onClick={handleClearSelection} variant="outline" size="sm" className="w-full bg-transparent">
                  <Square className="w-4 h-4 mr-2" />
                  Clear Selection
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* AI Processing */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">3. AI Processing</h3>
              <div className="space-y-3">
                <Button
                  onClick={handleGenerateSummaries}
                  variant="outline"
                  className="w-full bg-transparent"
                  disabled={counts.emails === 0}
                >
                  <Bot className="w-4 h-4 mr-2" />
                  Generate Summaries
                </Button>
                <Button variant="outline" size="sm" className="w-full bg-transparent">
                  <Wand2 className="w-4 h-4 mr-2" />
                  Generate Selected
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Export to Clio */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">4. Export to Clio</h3>
              <div className="space-y-3">
                <Button
                  onClick={handlePushToClio}
                  className="w-full bg-green-500 hover:bg-green-600"
                  disabled={counts.summaries === 0 || !connectionStatus.clio}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Push All to Clio
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full bg-green-50 hover:bg-green-100 text-green-700 border-green-200"
                >
                  <ArrowUp className="w-4 h-4 mr-2" />
                  Push Selected
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Area */}
        <Card className="overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full bg-gray-50 p-1">
              <TabsTrigger value="emails" className="flex-1 data-[state=active]:bg-white">
                <Mail className="w-4 h-4 mr-2" />
                Emails ({counts.emails})
              </TabsTrigger>
              <TabsTrigger value="summaries" className="flex-1 data-[state=active]:bg-white">
                <FileText className="w-4 h-4 mr-2" />
                Summaries ({counts.summaries})
              </TabsTrigger>
              <TabsTrigger value="extension" className="flex-1 data-[state=active]:bg-white">
                <Puzzle className="w-4 h-4 mr-2" />
                Chrome Extension
              </TabsTrigger>
            </TabsList>

            <TabsContent value="emails" className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <h3 className="text-xl font-semibold">Email Management</h3>
                <div className="flex flex-wrap gap-3">
                  <Select value={daysFilter} onValueChange={setDaysFilter}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">Last 7 days</SelectItem>
                      <SelectItem value="14">Last 14 days</SelectItem>
                      <SelectItem value="30">Last 30 days</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select value={emailFilter} onValueChange={setEmailFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Emails</SelectItem>
                      <SelectItem value="unsummarized">Needs Summary</SelectItem>
                      <SelectItem value="summarized">Has Summary</SelectItem>
                      <SelectItem value="unpushed">Not Pushed to Clio</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input
                      placeholder="Search emails..."
                      className="pl-10 w-48"
                      value={emailSearch}
                      onChange={(e) => setEmailSearch(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {filteredEmails.length === 0 ? (
                  <div className="text-center py-16 text-gray-500">
                    <MailOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">No emails fetched yet. Click "Fetch Emails" to get started.</p>
                  </div>
                ) : (
                  filteredEmails.map((email) => (
                    <Card
                      key={email.id}
                      className={`border ${selectedEmails.has(email.id) ? "border-green-500 bg-green-50" : "border-gray-200"}`}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          <Checkbox
                            checked={selectedEmails.has(email.id)}
                            onCheckedChange={(checked) => handleEmailSelection(email.id, checked as boolean)}
                          />
                          <div className="flex-1">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h4 className="font-semibold text-gray-900">{email.subject || "No Subject"}</h4>
                                <p className="text-sm text-gray-600">
                                  From: {email.sender} | To: {email.recipient} |{" "}
                                  {new Date(email.date_sent).toLocaleString()}
                                </p>
                              </div>
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline">
                                  <Bot className="w-4 h-4 mr-1" />
                                  Generate Summary
                                </Button>
                                {email.summary && (
                                  <Button size="sm" variant="outline">
                                    <Eye className="w-4 h-4 mr-1" />
                                    View Summary
                                  </Button>
                                )}
                              </div>
                            </div>
                            <p className="text-sm text-gray-700 line-clamp-3">{email.body.substring(0, 200)}...</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="summaries" className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <h3 className="text-xl font-semibold">Generated Summaries</h3>
                <div className="flex flex-wrap gap-3">
                  <Select value={summaryFilter} onValueChange={setSummaryFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Summaries</SelectItem>
                      <SelectItem value="unpushed">Not Pushed to Clio</SelectItem>
                      <SelectItem value="pushed">Pushed to Clio</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input
                      placeholder="Search summaries..."
                      className="pl-10 w-48"
                      value={summarySearch}
                      onChange={(e) => setSummarySearch(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {filteredSummaries.length === 0 ? (
                  <div className="text-center py-16 text-gray-500">
                    <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">No summaries generated yet. Fetch emails and generate summaries first.</p>
                  </div>
                ) : (
                  filteredSummaries.map((summary) => (
                    <Card key={summary.id} className="border-gray-200">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold text-gray-900">{summary.subject || "No Subject"}</h4>
                            <p className="text-sm text-gray-600">
                              {new Date(summary.date_sent).toLocaleString()} | Clio:{" "}
                              {summary.pushed_to_clio ? "✅ Pushed" : "❌ Not pushed"}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button size="sm" variant="outline" onClick={() => setEditingSummary(summary)}>
                                  <Edit className="w-4 h-4 mr-1" />
                                  Edit
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-2xl">
                                <DialogHeader>
                                  <DialogTitle>Edit Summary</DialogTitle>
                                </DialogHeader>
                                {editingSummary && (
                                  <div className="space-y-4">
                                    <div>
                                      <label className="block text-sm font-medium mb-2">Billing Hours:</label>
                                      <Input
                                        type="number"
                                        step="0.25"
                                        min="0"
                                        max="24"
                                        value={editingSummary.billing_hours}
                                        onChange={(e) =>
                                          setEditingSummary({
                                            ...editingSummary,
                                            billing_hours: Number.parseFloat(e.target.value),
                                          })
                                        }
                                      />
                                    </div>
                                    <div>
                                      <label className="block text-sm font-medium mb-2">Billing Description:</label>
                                      <Textarea
                                        rows={4}
                                        value={editingSummary.billing_description}
                                        onChange={(e) =>
                                          setEditingSummary({
                                            ...editingSummary,
                                            billing_description: e.target.value,
                                          })
                                        }
                                      />
                                    </div>
                                    <div>
                                      <label className="block text-sm font-medium mb-2">Full Summary:</label>
                                      <Textarea
                                        rows={6}
                                        value={editingSummary.summary}
                                        onChange={(e) =>
                                          setEditingSummary({
                                            ...editingSummary,
                                            summary: e.target.value,
                                          })
                                        }
                                      />
                                    </div>
                                    <div className="flex gap-2">
                                      <Button onClick={() => handleEditSummary(editingSummary)}>Save Changes</Button>
                                      <Button variant="outline" onClick={() => setEditingSummary(null)}>
                                        Cancel
                                      </Button>
                                    </div>
                                  </div>
                                )}
                              </DialogContent>
                            </Dialog>
                            {!summary.pushed_to_clio && (
                              <Button size="sm" className="bg-green-500 hover:bg-green-600">
                                <Upload className="w-4 h-4 mr-1" />
                                Push to Clio
                              </Button>
                            )}
                          </div>
                        </div>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                          <div className="flex items-center gap-2 mb-2">
                            <Clock className="w-4 h-4 text-blue-600" />
                            <span className="font-semibold text-blue-800">
                              Hours: {summary.billing_hours || "0.25"}
                            </span>
                          </div>
                          <p className="text-sm">
                            <strong>Description:</strong> {summary.billing_description || ""}
                          </p>
                        </div>
                        <div className="text-sm text-gray-700">
                          <strong>Summary:</strong>
                          <br />
                          {summary.summary || ""}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="extension" className="p-6">
              <div className="max-w-4xl mx-auto">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <Puzzle className="w-6 h-6" />
                  Chrome Extension Setup
                </h3>

                <div className="grid md:grid-cols-2 gap-6">
                  <Card>
                    <CardContent className="p-6">
                      <h4 className="font-semibold mb-3">1. Install Extension</h4>
                      <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                        <li>
                          Open Chrome and go to <code className="bg-gray-100 px-1 rounded">chrome://extensions/</code>
                        </li>
                        <li>Enable "Developer mode" (top right toggle)</li>
                        <li>
                          Click "Load unpacked" and select the{" "}
                          <code className="bg-gray-100 px-1 rounded">chrome-extension</code> folder
                        </li>
                        <li>Pin the extension to your toolbar</li>
                      </ol>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <h4 className="font-semibold mb-3">2. Extension Features</h4>
                      <ul className="list-disc list-inside space-y-2 text-sm text-gray-600">
                        <li>
                          <strong>Auto-capture:</strong> Automatically capture sent emails
                        </li>
                        <li>
                          <strong>Manual capture:</strong> Click the capture button in Gmail
                        </li>
                        <li>
                          <strong>Quick summaries:</strong> Generate summaries from the extension
                        </li>
                        <li>
                          <strong>Dashboard access:</strong> Quick link to this dashboard
                        </li>
                      </ul>
                    </CardContent>
                  </Card>
                </div>

                <Card className="mt-6">
                  <CardContent className="p-6">
                    <h4 className="font-semibold mb-3">3. Extension Status</h4>
                    <Button variant="outline">
                      <TestTube className="w-4 h-4 mr-2" />
                      Check Extension Status
                    </Button>
                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-green-800">✅ Dashboard is running and ready</p>
                      <p className="text-green-700 text-sm mt-1">
                        📧 Server URL:{" "}
                        {typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}
                      </p>
                      <p className="text-green-700 text-sm">🔗 Make sure your extension points to this URL</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  )
}
