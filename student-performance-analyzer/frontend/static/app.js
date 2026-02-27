// File upload handling
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const sampleBtn = document.getElementById("sampleBtn");
const fileNameDiv = document.getElementById("fileName");
const loadingSpinner = document.getElementById("loadingSpinner");
const errorMessage = document.getElementById("errorMessage");
const successMessage = document.getElementById("successMessage");

let selectedFile = null;
const API_BASE =
  window.location.protocol === "file:" ? "http://127.0.0.1:5000" : "";

function getDashboardUrl() {
  return window.location.protocol === "file:" ? "dashboard.html" : "/dashboard";
}

// Browse button click
browseBtn.addEventListener("click", () => {
  fileInput.click();
});

// File input change
fileInput.addEventListener("change", (e) => {
  handleFileSelect(e.target.files[0]);
});

// Drag and drop
uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
  handleFileSelect(e.dataTransfer.files[0]);
});

function handleFileSelect(file) {
  if (!file) return;

  if (file.type !== "text/csv" && !file.name.endsWith(".csv")) {
    showError("Please select a valid CSV file");
    return;
  }

  selectedFile = file;
  fileNameDiv.textContent = `✓ File selected: ${file.name}`;
  fileNameDiv.classList.add("show");
  analyzeBtn.disabled = false;
  clearMessages();
}

// Analyze button click
analyzeBtn.addEventListener("click", analyzeFile);

// Sample button click
sampleBtn.addEventListener("click", loadSampleData);

async function analyzeFile() {
  if (!selectedFile) {
    showError("Please select a file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  showLoading(true);
  clearMessages();

  try {
    const response = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Analysis failed");
    }

    // Store data and redirect
    sessionStorage.setItem("analysisData", JSON.stringify(data));
    showSuccess("Analysis complete! Redirecting to dashboard...");

    setTimeout(() => {
      window.location.href = getDashboardUrl();
    }, 1500);
  } catch (error) {
    showError(`Error: ${error.message}`);
    showLoading(false);
  }
}

async function loadSampleData() {
  showLoading(true);
  clearMessages();

  try {
    const response = await fetch(`${API_BASE}/api/sample`);
    const data = await response.json();

    sessionStorage.setItem("analysisData", JSON.stringify(data));
    showSuccess("Sample data loaded! Redirecting to dashboard...");

    setTimeout(() => {
      window.location.href = getDashboardUrl();
    }, 1500);
  } catch (error) {
    showError(`Error loading sample data: ${error.message}`);
    showLoading(false);
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.style.display = "block";
}

function showLoading(show) {
  loadingSpinner.style.display = show ? "block" : "none";
  analyzeBtn.disabled = show;
}

function clearMessages() {
  errorMessage.style.display = "none";
  successMessage.style.display = "none";
}
