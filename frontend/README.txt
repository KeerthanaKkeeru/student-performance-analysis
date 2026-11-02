ABA dashboard frontend
======================

1. Extract the files into your existing project:
   student-performance-analysis/frontend/
2. Replace index.html, style.css and script.js with these files.
3. Keep the Flask backend running at http://localhost:5000.
4. From the Ubuntu/WSL terminal:
   cd ~/student-performance-analysis/frontend
   python3 -m http.server 5500
5. Open http://localhost:5500
6. Upload students.csv and click Run Analysis.

Charts are populated from the JSON returned by POST /analyze.
Expected student JSON fields: id, activity_score, academic_average,
category, recommendation.
Expected summary fields: excellent, good, average, needs_improvement.

Chart.js is loaded from jsDelivr, so an internet connection is needed
for the charts. The frontend does not change your Hadoop mapper/reducer.
