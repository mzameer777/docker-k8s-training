from flask import Flask, jsonify, request
import os
import socket
import datetime

app = Flask(__name__)

# In-memory store (for demo purposes)
tasks = []


@app.route("/")
def home():
    return jsonify({
        "service": "Task API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.now().isoformat(),
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "done": False,
        "created_at": datetime.datetime.now().isoformat(),
    }
    tasks.append(task)
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "task not found"}), 404

    data = request.get_json()
    if "title" in data:
        task["title"] = data["title"]
    if "done" in data:
        task["done"] = data["done"]
    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": "deleted"}), 200


@app.route("/env")
def show_env():
    """Show select environment variables (useful for ConfigMap/Secret demos)."""
    return jsonify({
        "APP_VERSION": os.getenv("APP_VERSION", "not set"),
        "DB_HOST": os.getenv("DB_HOST", "not set"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "not set"),
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "false").lower() == "true")
