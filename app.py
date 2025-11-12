# FLASK APP - Resume Parser using Groq AI
# Run the app using: python app.py
import os, sys
from flask import Flask, request, render_template
from pypdf import PdfReader 
import json
import uuid
from werkzeug.utils import secure_filename
from resumeparser import ats_extractor, calculate_job_match, calculate_ats_score

sys.path.insert(0, os.path.abspath(os.getcwd()))


UPLOAD_PATH = r"__DATA__"
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload size

# Ensure upload directory exists
os.makedirs(UPLOAD_PATH, exist_ok=True)


# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Content Security Policy - allows Tailwind CDN
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "img-src 'self' https://res.cloudinary.com data:; "
        "font-src 'self' data:;"
    )
    return response


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    # Validate file upload
    if 'pdf_doc' not in request.files:
        return render_template('index.html', error="No file uploaded")
    
    doc = request.files['pdf_doc']
    
    if doc.filename == '':
        return render_template('index.html', error="No file selected")
    
    if not allowed_file(doc.filename):
        return render_template('index.html', error="Invalid file type. Please upload a PDF file.")
    
    # Get job description if provided with length validation
    job_description = request.form.get('job_description', '').strip()
    if job_description and len(job_description) > 10000:  # Limit to 10K characters
        return render_template('index.html', error="Job description is too long (max 10,000 characters)")
    
    # Generate unique filename to avoid overwrites
    original_filename = secure_filename(doc.filename)
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    doc_path = os.path.join(UPLOAD_PATH, unique_filename)
    
    try:
        # Save and process the file
        doc.save(doc_path)
        data = _read_file_from_path(doc_path)
        
        if not data.strip():
            return render_template('index.html', error="No text could be extracted from the PDF")
        
        # Validate extracted text length (prevent token overflow)
        if len(data) > 50000:  # Limit to ~50K characters
            return render_template('index.html', error="Resume is too long. Please use a shorter resume (max ~10 pages)")
        
        # Call the ATS extractor
        result = ats_extractor(data)
        
        # Debug: Print the raw result
        print("="*80)
        print("RAW AI RESPONSE:")
        print(result)
        print("="*80)
        
        # Try to parse the result as JSON
        try:
            parsed_data = json.loads(result)
            print("Successfully parsed JSON!")
            print("Keys in parsed data:", list(parsed_data.keys()))
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            # Try to extract JSON from the response if wrapped in text
            parsed_data = _extract_json_from_text(result)
            if parsed_data is None:
                return render_template('index.html', error="Failed to parse response from AI model")
            print("Extracted JSON from text. Keys:", list(parsed_data.keys()))
        
        # Calculate job match if job description provided
        job_match_data = None
        if job_description:
            print("Calculating job match...")
            try:
                job_match_data = calculate_job_match(data, parsed_data, job_description)
                print("Job match calculated successfully!")
                if job_match_data:
                    print(f"Match score: {job_match_data.get('overall_match_score', 'N/A')}")
            except Exception as e:
                print(f"Error calculating job match: {str(e)}")
                # Don't fail the entire request if job matching fails
                job_match_data = {"error": str(e)}
        
        # Calculate ATS score
        ats_score_data = None
        print("Calculating ATS score...")
        try:
            ats_score_data = calculate_ats_score(data, parsed_data)
            print("ATS score calculated successfully!")
            if ats_score_data:
                print(f"ATS score: {ats_score_data.get('overall_ats_score', 'N/A')}")
        except Exception as e:
            print(f"Error calculating ATS score: {str(e)}")
            # Don't fail the entire request if ATS scoring fails
            ats_score_data = {"error": str(e)}
        
        return render_template('index.html', data=parsed_data, job_match=job_match_data, ats_score=ats_score_data)
    
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error processing resume: {str(e)}")
        return render_template('index.html', error=f"An error occurred while processing your resume: {str(e)}")
    
    finally:
        # Clean up: remove the uploaded file after processing
        if os.path.exists(doc_path):
            try:
                os.remove(doc_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {doc_path}: {str(e)}")

 
def _read_file_from_path(path):
    reader = PdfReader(path) 
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no] 
        data += page.extract_text()

    return data 


def _extract_json_from_text(text):
    """
    Attempt to extract JSON from text that may contain extra content.
    Returns parsed JSON dict or None if extraction fails.
    """
    import re
    
    # Try to find JSON object in the text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON array in the text
    json_array_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_array_match:
        try:
            return json.loads(json_array_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None


if __name__ == "__main__":
    # Read debug mode from environment variable (default: False for safety)
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    port = int(os.getenv("FLASK_PORT", "8000"))
    app.run(port=port, debug=debug_mode)

