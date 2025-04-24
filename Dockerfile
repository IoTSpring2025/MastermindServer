FROM python:3.13-slim

# need to install for image processing
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

WORKDIR /app

# Set environment variables for Roboflow API
ENV ROBOFLOW_API_KEY="7HR1rjmO51BI81A3sdIP"
ENV ROBOFLOW_WORKSPACE="mastermind-rrqwi"
ENV ROBOFLOW_PROJECT="card-detection-zk7wu-3lymd"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]