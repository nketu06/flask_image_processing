# Image Processing Application with Webhook Integration

This Flask application allows you to upload a CSV file containing image URLs, processes these images asynchronously by compressing them, stores the results in a MongoDB database, and triggers a webhook upon completion of the processing.

## Features

- **CSV Upload**: Accepts a CSV file containing image URLs for processing.
- **Asynchronous Processing**: Images are processed asynchronously to improve performance and responsiveness.
- **Image Compression**: Images are downloaded, compressed, and saved locally.
- **MongoDB Integration**: Request statuses and image processing results are stored in MongoDB.
- **Webhook Notification**: A specified webhook URL is triggered upon completion of image processing, sending the status and results.
- **Status API**: Allows users to check the processing status using a unique request ID.

## Prerequisites

- Python 3.x
- MongoDB (running locally or accessible via a URI)
- Required Python packages listed in `requirements.txt`

## Installation

1. **Clone the Repository**:

   git clone https://github.com/nketu06/flask_image_processing.git
   cd flask_image_processing

2. **Create a Virtual Environment:**:  
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **pip install -r requirements.txt**:  
    pip install -r requirements.txt

4. **Start MongoDB**:
    Ensure MongoDB is running locally on the default port (27017), or update the connection string in the code to match your MongoDB configuration.

## How to use

1. **Start the Flask Application**
    python3 app.py or python app.py

2. **Upload a CSV File**
    - sample csv is already present in our application as my_data.csv
    Use the following curl command to upload a CSV file for processing

    curl -F "file=@my_data.csv" -F "webhook_url=http://127.0.0.1:5000/webhook" http://127.0.0.1:5000/upload

    - file=@my_data.csv: Uploads the CSV file containing the image URLs.
    - webhook_url=http://127.0.0.1:5000/webhook: Specifies the webhook endpoint to receive notifications upon processing completion.

3. **Check the Processing Status:**
    - Retrieve the status of your processing job using the request_id returned from the upload

    curl http://127.0.0.1:5000/status/<request_id>

4. **Webhook Receiver:**
    The webhook receiver is set up at /webhook. When processing completes, the application will send a POST request to this endpoint with the processing results.

## Endpoints
1. **Upload Endpoint - /upload (POST)**
    - Uploads a CSV file for processing.

    - Parameters:
    file (required): CSV file containing image URLs.
    webhook_url (optional): URL to be triggered upon completion of processing.

    - Response:
    202 Accepted: Returns a JSON object with a request_id for tracking status.

2. **Status Endpoint - /status/<request_id> (GET)**
    - Checks the processing status of a request.

    -Parameters:
    request_id (required): The unique ID returned from the upload endpoint.

    -Response:
    200 OK: Returns the status and results of the processing request.
    404 Not Found: If the request_id is invalid.

3.  **Webhook Receiver - /webhook (POST)**

    - Receives notifications upon completion of image processing.

    - Request Body:
    JSON payload containing the processing results, including request ID, status, and image data.

    - Response:
    200 OK: Acknowledges receipt of the webhook data.








