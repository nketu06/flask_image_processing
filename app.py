from flask import Flask, request, jsonify
import csv
import os
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# In-memory database to store requests and statuses
requests_db = {}

# Create a thread pool for asynchronous tasks
executor = ThreadPoolExecutor(max_workers=5)

# Define directories
LOCAL_IMAGE_DIR = 'processed_images'
OUTPUT_CSV_DIR = 'output_csv'
os.makedirs(LOCAL_IMAGE_DIR, exist_ok=True)  # Create the directory for images if it doesn't exist
os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)   # Create the directory for output CSV files

def compress_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    output = BytesIO()
    img.save(output, format='JPEG', quality=50)  # Compress the image to 50% quality
    output.seek(0)
    return output


def process_images(request_id, product_data):
    input_output_mapping = []  # To store input and output URL mapping
    requests_db[request_id]={}
    for product in product_data:
        serial_number, product_name, input_urls = product
        input_urls_list = input_urls.split(',')
        output_urls = []

        for url in input_urls_list:
            compressed_image = compress_image(url.strip())

            # Create a unique filename for each image
            file_name = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(LOCAL_IMAGE_DIR, file_name)
            
            requests_db[request_id][url]={"status":"Processing"}
            # Save the compressed image to the local directory
            with open(file_path, 'wb') as f:
                f.write(compressed_image.read())

            # Store the local file path
            output_urls.append(file_path)
            requests_db[request_id][url] = {"status":"Done","output_img":file_path}

        # Add to mapping list
        input_output_mapping.append((serial_number, product_name, input_urls, ','.join(output_urls)))

    # Create the output CSV file
    create_output_csv(request_id, input_output_mapping)

def create_output_csv(request_id, input_output_mapping):
    output_csv_path = os.path.join(OUTPUT_CSV_DIR, f"output_{request_id}.csv")

    # Write to the output CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['S. No.', 'Product Name', 'Input Image Urls', 'Output Image Urls'])  # Header

        for serial_number, product_name, input_urls, output_urls in input_output_mapping:
            csv_writer.writerow([serial_number, product_name, input_urls, output_urls])

    print(f"Output CSV created at: {output_csv_path}")



@app.route('/upload', methods=['POST'])
def upload_csv():
    # Check if a file is provided in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Read the CSV file in text mode and decode it properly
    file.stream.seek(0)  # Reset file pointer to the beginning
    file_content = file.stream.read().decode('utf-8')
    
    # Print raw CSV content for debugging
    print("Raw CSV content:\n", file_content)
    
    # Use csv.reader to parse the CSV content
    csv_data = csv.reader(file_content.splitlines())
    next(csv_data)  # Skip header

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Extract image URLs and process them asynchronously
    product_data = []
    print(csv_data,'csv_data')
    for row in csv_data:
        print('Parsed row:', row,len(row))  # Debugging: Print each parsed row
        # Check if the row has at least 3 columns
        if len(row) != 3:
            print('Invalid row:', row)  # Debugging: Print invalid rows
            return jsonify({'error': 'Invalid CSV format. Each row must have at least 3 columns.'}), 400
        product_data.append(row)
    print(product_data)
    # Use the executor to process images asynchronously
    executor.submit(process_images, request_id, product_data)

    return jsonify({'request_id': request_id}), 202




@app.route('/status/<request_id>', methods=['GET'])
def check_status(request_id):
    if request_id not in requests_db:
        return jsonify({'error': 'Invalid request ID'}), 404

    return jsonify(requests_db[request_id]), 200

if __name__ == '__main__':
    app.run(debug=True)
