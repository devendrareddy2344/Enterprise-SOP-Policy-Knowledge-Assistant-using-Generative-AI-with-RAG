import csv
import os
from datetime import datetime

LOG_PATH = "logs/query_logs.csv"

def log_query(question, role, confidence, response_time):
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["timestamp", "question", "role", "confidence", "response_time"])

        writer.writerow([
            datetime.utcnow(),
            question,
            role,
            confidence,
            response_time
        ])
