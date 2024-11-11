from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import qrcode
import uuid
import os
import cv2

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Set the folder where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists
os.makedirs(STATIC_FOLDER, exist_ok=True)  # Ensure the static directory exists

# Set the allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generateQRCode(data):
    # Generate a unique filename using UUID
    filename = f"qrcode_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_FOLDER, filename)

    # Create a QR code object with the specified data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill="black", back_color="white")

    # Save the image with the unique filename
    qr_image.save(filepath)

    # Return the full file path to the file
    return filepath

def decodeQRCode(image_path):
    # Initialize the QRCodeDetector
    detector = cv2.QRCodeDetector()
    
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    
    # Detect and decode the QR code
    data, points, _ = detector.detectAndDecode(image)
    
    # Return the decoded data if QR code is found
    return data if data else None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/decoder')
def decoder():
    return render_template('decoder.html')

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        data = request.form.get('info')
        if data:
            filepath = generateQRCode(data)
            return send_file(filepath, as_attachment=True)
        else:
            flash("Please enter data to generate QR code")
            return redirect(url_for('generator'))
    return render_template('generator.html')

@app.route('/decode', methods=['POST'])
def decode():
    if 'qrImage' not in request.files:
        flash("No file part")
        return redirect(request.url)
    
    qrImage = request.files['qrImage']

    if qrImage and allowed_file(qrImage.filename):
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], qrImage.filename)
        qrImage.save(filepath)
        
        # Decode QR code
        qrData = decodeQRCode(filepath)
        
        if qrData:
            return render_template('decoded.html',data=qrData)
        else:
            flash("No QR code detected in the image.")
            return redirect(url_for('decoder'))
    else:
        flash("Invalid file type. Please upload a PNG, JPG, or JPEG file.")
        return redirect(url_for('decoder'))

if __name__ == "__main__":
    app.run(debug=True)
