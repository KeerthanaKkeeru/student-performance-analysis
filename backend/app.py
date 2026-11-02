
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import subprocess
import csv
import re

app = Flask(__name__)
CORS(app)

PROJECT = Path(__file__).resolve().parent.parent
HADOOP_HOME = Path("/home/keert/hadoop")
HDFS_INPUT = "/student-analysis/input/students.csv"
HDFS_OUTPUT = "/student-analysis/output"

def run_command(command):
    result = subprocess.run(
        command,
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)

    return result.stdout

@app.get("/")
def home():
    return jsonify({"message": "Student Performance API is running"})

@app.post("/upload")
def upload():
    file = request.files.get("file")

    if not file or not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Please upload a CSV file"}), 400

    local_file = PROJECT / "input" / "students.csv"
    local_file.parent.mkdir(exist_ok=True)

    file.save(local_file)

    try:
        with local_file.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required = {
                "student_id", "attendance_pct", "study_hours",
                "assignments_submitted", "assignments_total",
                "quiz_score", "lms_logins", "final_marks"
            }

            if not required.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV headers do not match the required format")

            rows = list(reader)

            if not rows:
                raise ValueError("CSV contains no student records")

            if len({row["student_id"] for row in rows}) != len(rows):
                raise ValueError("Duplicate student IDs found")

        run_command([
            str(HADOOP_HOME / "bin/hdfs"),
            "dfs", "-mkdir", "-p", "/student-analysis/input"
        ])

        run_command([
            str(HADOOP_HOME / "bin/hdfs"),
            "dfs", "-put", "-f", str(local_file), HDFS_INPUT
        ])

        return jsonify({
            "message": f"Uploaded {len(rows)} student records to HDFS",
            "records": len(rows)
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 400

@app.post("/analyze")
def analyze():
    try:
        run_command([
            str(HADOOP_HOME / "bin/hdfs"),
            "dfs", "-rm", "-r", "-f", HDFS_OUTPUT
        ])

        run_command([
            str(HADOOP_HOME / "bin/hadoop"),
            "jar",
            str(HADOOP_HOME / "share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar"),
            "-files", "mapper.py,reducer.py",
            "-mapper", "python3 mapper.py",
            "-reducer", "python3 reducer.py",
            "-input", HDFS_INPUT,
            "-output", HDFS_OUTPUT
        ])

        output = run_command([
            str(HADOOP_HOME / "bin/hdfs"),
            "dfs", "-cat", f"{HDFS_OUTPUT}/part-*"
        ])

        students = []
        summary = {
            "total": 0,
            "excellent": 0,
            "good": 0,
            "average": 0,
            "needs_improvement": 0
        }

        for line in output.splitlines():
            parts = line.split()

            if len(parts) >= 6 and parts[0] == "STUDENT":
                if parts[4] == "Needs":
    category = "Needs Improvement"
    recommendation = " ".join(parts[6:])
else:
    category = parts[4]
    recommendation = " ".join(parts[5:])

students.append({
    "id": parts[1],
    "activity_score": parts[2],
    "academic_average": parts[3],
    "category": category,
    "recommendation": recommendation
})

            elif len(parts) >= 3 and parts[0] == "SUMMARY":
                category = " ".join(parts[1:-1]).lower()
                key = category.replace(" ", "_")
                if key in summary:
                    summary[key] = int(parts[-1])

        summary["total"] = len(students)

        return jsonify({
            "students": students,
            "summary": summary
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
