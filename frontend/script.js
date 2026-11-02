const API = "http://localhost:5000";
let categoryChart, activityChart, academicChart;
let currentStudents = [];

async function uploadDataset() {
  const file = document.getElementById("csvFile").files[0];
  const message = document.getElementById("message");
  if (!file) { message.textContent = "Please select a CSV file first."; return; }

  const form = new FormData();
  form.append("file", file);
  message.textContent = "Uploading dataset to HDFS…";

  try {
    const response = await fetch(`${API}/upload`, { method: "POST", body: form });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Upload failed");
    message.textContent = data.message || "Dataset uploaded successfully.";
  } catch (error) {
    message.textContent = `Upload error: ${error.message}`;
  }
}

async function runAnalysis() {
  const message = document.getElementById("message");
  const button = document.getElementById("runButton");
  button.disabled = true;
  message.textContent = "Hadoop is processing the student dataset…";

  try {
    const response = await fetch(`${API}/analyze`, { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed");
    currentStudents = data.students || [];
    if (!currentStudents.length) throw new Error("No student rows were returned. Check the Hadoop output.");
    renderDashboard(currentStudents, data.summary || {});
    message.textContent = `Analysis completed: ${currentStudents.length} student records received.`;
  } catch (error) {
    message.textContent = `Analysis error: ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

function renderDashboard(students, summary) {
  const counts = {
    excellent: Number(summary.excellent || 0),
    good: Number(summary.good || 0),
    average: Number(summary.average || 0),
    needs_improvement: Number(summary.needs_improvement || 0)
  };
  document.getElementById("totalStudents").textContent = students.length;
  document.getElementById("excellent").textContent = counts.excellent;
  document.getElementById("good").textContent = counts.good;
  document.getElementById("needsImprovement").textContent = counts.needs_improvement;

  const avgActivity = average(students, "activity_score");
  const avgAcademic = average(students, "academic_average");
  document.getElementById("averageActivity").textContent = `${avgActivity.toFixed(1)}%`;
  document.getElementById("averageAcademic").textContent = `${avgAcademic.toFixed(1)}%`;

  const topActivity = [...students].sort((a,b) => Number(b.activity_score)-Number(a.activity_score))[0];
  const topAcademic = [...students].sort((a,b) => Number(b.academic_average)-Number(a.academic_average))[0];
  document.getElementById("topActivity").textContent = topActivity ? `${topActivity.id} · ${topActivity.activity_score}` : "—";
  document.getElementById("topAcademic").textContent = topAcademic ? `${topAcademic.id} · ${topAcademic.academic_average}` : "—";

  renderTable(students);
  renderHighlights(students);
  renderCharts(students, counts);
}

function average(students, field) {
  return students.reduce((sum, s) => sum + Number(s[field] || 0), 0) / (students.length || 1);
}

function renderTable(students) {
  const tbody = document.getElementById("resultsTable");
  tbody.innerHTML = "";
  students.forEach(s => {
    const tr = document.createElement("tr");
    [s.id, s.activity_score, s.academic_average, s.category, s.recommendation]
      .forEach(value => {
        const td = document.createElement("td");
        td.textContent = value ?? "—";
        tr.appendChild(td);
      });
    tbody.appendChild(tr);
  });
}

function renderHighlights(students) {
  const container = document.getElementById("studentHighlights");
  container.innerHTML = "";
  [...students]
    .sort((a,b) => Number(b.activity_score)-Number(a.activity_score))
    .slice(0,5)
    .forEach(s => {
      const item = document.createElement("div");
      item.className = "student-item";
      const details = document.createElement("div");
      const id = document.createElement("h4");
      id.textContent = s.id;
      const category = document.createElement("p");
      category.textContent = `${s.category} · ${s.recommendation}`;
      details.append(id, category);
      const score = document.createElement("div");
      score.className = "student-score";
      score.textContent = `${s.activity_score}%`;
      item.append(details, score);
      container.appendChild(item);
    });
}

function renderCharts(students, counts) {
  [categoryChart, activityChart, academicChart].forEach(chart => chart && chart.destroy());

  categoryChart = new Chart(document.getElementById("categoryChart"), {
    type: "doughnut",
    data: {
      labels: ["Excellent", "Good", "Average", "Needs Improvement"],
      datasets: [{
        data: [counts.excellent, counts.good, counts.average, counts.needs_improvement],
        backgroundColor: ["#7042c5", "#3698e8", "#edb83e", "#e77b91"],
        borderColor: "#fff", borderWidth: 4
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: "66%",
      plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } }
    }
  });

  activityChart = new Chart(document.getElementById("activityChart"), {
    type: "bar",
    data: {
      labels: students.map(s => s.id),
      datasets: [{ label: "Activity Score", data: students.map(s => Number(s.activity_score)), backgroundColor: "#7042c5", borderRadius: 5 }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
  });

  academicChart = new Chart(document.getElementById("academicChart"), {
    type: "bar",
    data: {
      labels: students.map(s => s.id),
      datasets: [{ label: "Academic Average", data: students.map(s => Number(s.academic_average)), backgroundColor: "#3698e8", borderRadius: 5 }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
  });
}
