FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "ab_test_analysis.py", "--input", "data/ab_test_data.csv", "--output", "results"]
