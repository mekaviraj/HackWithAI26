let analysisData = null;
let accuracyChart = null;
let timeChart = null;
let strengthChart = null;

// Initialize dashboard
document.addEventListener("DOMContentLoaded", () => {
  const data = sessionStorage.getItem("analysisData");
  if (!data) {
    window.location.href = "/";
    return;
  }

  analysisData = JSON.parse(data);
  renderDashboard();
});

function renderDashboard() {
  if (!analysisData || !analysisData.analysis) {
    console.error("No analysis data found");
    return;
  }

  const analysis = analysisData.analysis;
  const summary = analysis.summary;

  // Update stats
  document.getElementById("totalAttempts").textContent = summary.total_attempts;
  document.getElementById("overallAccuracy").textContent =
    summary.overall_accuracy.toFixed(1) + "%";
  document.getElementById("strengthScore").textContent =
    summary.strength_score.toFixed(1);
  document.getElementById("strengthLevel").textContent = summary.strength_level;

  // Render charts
  renderAccuracyChart(analysis.accuracy_by_difficulty);
  renderTimeChart(analysis.time_comparison);
  renderStrengthChart(analysis.strength_progression);

  // Render detailed analysis
  renderSummaryDetails(summary);
  renderSubtopicRanking(analysis.subtopic_ranking);

  // Render 7-day plan
  renderStudyPlan(analysisData.plan);

  // Render recommendations
  renderRecommendations(analysisData.recommendations);

  // Render study tips
  renderStudyTips(analysisData.study_tips);
}

function renderAccuracyChart(accuracyByDifficulty) {
  const ctx = document.getElementById("accuracyChart").getContext("2d");

  const labels = accuracyByDifficulty.map(
    (item) => `Difficulty ${item.difficulty}`,
  );
  const accuracies = accuracyByDifficulty.map((item) => item.accuracy);
  const colors = accuracies.map((score) =>
    score < 50 ? "#e74c3c" : score < 70 ? "#f39c12" : "#2ecc71",
  );

  accuracyChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Accuracy (%)",
          data: accuracies,
          backgroundColor: colors,
          borderColor: colors,
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function (value) {
              return value + "%";
            },
          },
        },
      },
    },
  });
}

function renderTimeChart(timeComparison) {
  const ctx = document.getElementById("timeChart").getContext("2d");

  const labels = ["Correct", "Incorrect"];
  const values = [
    timeComparison.avg_time_correct,
    timeComparison.avg_time_incorrect,
  ];

  timeChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Average Time (seconds)",
          data: values,
          backgroundColor: ["#2ecc71", "#e74c3c"],
          borderColor: ["#2ecc71", "#e74c3c"],
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

function renderStrengthChart(strengthProgression) {
  const ctx = document.getElementById("strengthChart").getContext("2d");

  const labels = strengthProgression.map((item) => item.test_id);
  const scores = strengthProgression.map((item) => item.strength_score);

  strengthChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Strength Score",
          data: scores,
          borderColor: "#3498db",
          backgroundColor: "rgba(52, 152, 219, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 6,
          pointBackgroundColor: "#3498db",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
        },
      },
    },
  });
}

function renderSummaryDetails(summary) {
  const container = document.getElementById("summaryDetails");

  container.innerHTML = `
        <div class="subject-stat">
            <h4>Summary</h4>
            <div class="stat-row">
                <span class="stat-label">Total Attempts</span>
                <span class="stat-value">${summary.total_attempts}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Overall Accuracy</span>
                <span class="stat-value">${summary.overall_accuracy.toFixed(1)}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Time (Correct)</span>
                <span class="stat-value">${summary.avg_time_correct.toFixed(1)}s</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Time (Incorrect)</span>
                <span class="stat-value">${summary.avg_time_incorrect.toFixed(1)}s</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Strength Score</span>
                <span class="stat-value">${summary.strength_score.toFixed(1)}</span>
            </div>
        </div>
    `;
}

function renderSubtopicRanking(ranking) {
  const container = document.getElementById("subtopicRanking");

  let html = "";
  for (const item of ranking) {
    html += `
            <div class="subject-stat">
                <h4>${item.subtopic}</h4>
                <div class="stat-row">
                    <span class="stat-label">Topic</span>
                    <span class="stat-value">${item.topic}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Accuracy</span>
                    <span class="stat-value">${item.accuracy.toFixed(1)}%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Attempts</span>
                    <span class="stat-value">${item.attempts}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Rank</span>
                    <span class="stat-value">${item.rank}</span>
                </div>
            </div>
        `;
  }
  container.innerHTML = html;
}

function renderStudyPlan(plan) {
  const container = document.getElementById("studyPlan");

  let html = "";
  for (const day of plan) {
    const focusText =
      day.focus && day.focus.length > 0 ? day.focus.join(", ") : "Revision";
    const activitiesHtml = day.activities
      .map((activity) => `<li>${activity}</li>`)
      .join("");
    const goalsHtml = day.goals.map((goal) => `<li>${goal}</li>`).join("");

    html += `
            <div class="day-plan">
                <h4>Day ${day.day}</h4>
                <div class="day-date">${day.date}</div>
                <div class="day-focus">
                    <strong>Focus:</strong>
                    ${focusText}
                </div>
                <div>
                    <strong style="display: block; margin-bottom: 0.5rem;">Study Time: ${day.study_time}</strong>
                    <strong style="display: block; margin-bottom: 0.5rem;">Activities:</strong>
                    <ul class="activities-list">
                        ${activitiesHtml}
                    </ul>
                </div>
            </div>
        `;
  }
  container.innerHTML = html;
}

function renderRecommendations(recommendations) {
  const container = document.getElementById("recommendations");

  let html = "";
  for (const [subject, resources] of Object.entries(recommendations)) {
    const resourcesHtml = resources
      .map(
        (resource) => `
            <div class="resource">
                <div class="resource-name">${resource.name}</div>
                <span class="resource-type">${resource.type}</span>
                <br>
                <a href="${resource.url}" target="_blank" class="resource-link">${resource.url}</a>
            </div>
        `,
      )
      .join("");

    html += `
            <div class="subject-recommendations">
                <h4>📚 ${subject}</h4>
                ${resourcesHtml}
            </div>
        `;
  }
  container.innerHTML = html;
}

function renderStudyTips(studyTips) {
  const container = document.getElementById("studyTips");

  let html = "";
  for (const [subject, tips] of Object.entries(studyTips)) {
    const tipsHtml = tips.map((tip) => `<li>${tip}</li>`).join("");

    html += `
            <div class="tips-card">
                <h4>💡 ${subject}</h4>
                <ul>
                    ${tipsHtml}
                </ul>
            </div>
        `;
  }
  container.innerHTML = html;
}

function goBack() {
  sessionStorage.clear();
  window.location.href = "/";
}

function exportToPDF() {
  alert(
    "PDF export feature coming soon! For now, use your browser's print function (Ctrl+P) to save as PDF.",
  );
}

function downloadPlan() {
  if (!analysisData || !analysisData.plan) return;

  let planText = "Student Performance Analysis - 7-Day Study Plan\n";
  planText += "=".repeat(50) + "\n\n";

  for (const day of analysisData.plan) {
    planText += `Day ${day.day} - ${day.date}\n`;
    planText += "-".repeat(30) + "\n";
    planText += `Focus: ${day.focus.join(", ")}\n`;
    planText += `Study Time: ${day.study_time}\n`;
    planText += `\nActivities:\n`;
    day.activities.forEach((activity) => {
      planText += `  • ${activity}\n`;
    });
    planText += `\nGoals:\n`;
    day.goals.forEach((goal) => {
      planText += `  • ${goal}\n`;
    });
    planText += "\n";
  }

  const element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(planText),
  );
  element.setAttribute("download", "study-plan.txt");
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}
