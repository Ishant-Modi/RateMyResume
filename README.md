# AI-Powered Resume Parser & Analyzer

> **Transform your resume analysis with cutting-edge AI technology**

A comprehensive Flask-based web application that uses Groq AI (LLaMA 3.3 70B) to parse resumes, match them with job descriptions, and provide ATS (Applicant Tracking System) compatibility scores.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![Groq AI](https://img.shields.io/badge/Groq-AI-purple.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Features

### 1. **Enhanced Resume Parsing** 📄

Extract comprehensive information from resumes across **13 categories**:

- Personal Information (Name, Email, Phone, Location, Links)
- Education (Degrees, Institutions, GPA, Coursework)
- Work Experience (Companies, Roles, Responsibilities, Achievements)
- Projects (Descriptions, Technologies, Links)
- Leadership Roles & Responsibilities
- Volunteering Experience
- Technical Skills (Languages, Frameworks, Tools, Databases)
- Soft Skills
- Certifications
- Awards & Achievements
- Languages & Proficiency
- Publications

### 2. **Job Description Matching** 🎯

- Input any job description and get a **0-100 match score**
- Detailed category breakdown (Skills, Experience, Education, Keywords)
- **Matching skills** - What you have ✓
- **Missing skills** - What to add !
- **Actionable recommendations** to improve your match score
- AI-generated summary of compatibility

### 3. **ATS Compatibility Scoring** ✅

Get a comprehensive **0-100 ATS score** based on:

- Contact Information Completeness (10%)
- Keyword Density (25%)
- Format Compatibility (15%)
- Section Organization (15%)
- Experience Quantification (15%)
- Education Details (10%)
- Skills Presence (10%)

**Additional Analysis:**

- Strengths & Weaknesses identification
- Present & Missing keywords
- Format issue detection
- Specific improvement suggestions


---

## 🛠️ Tech Stack

- **Backend:** Flask 3.0.2 (Python)
- **AI Engine:** Groq API (LLaMA 3.3 70B Versatile)
- **PDF Processing:** pypdf 4.1.0
- **Frontend:** HTML5, Tailwind CSS
- **Configuration:** PyYAML 6.0.1

---

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Step-by-Step Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Ishant-Modi/RateMyResume.git
   cd resume-parser
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Groq API key**

   **Method 1 - Environment Variable (Recommended):**

   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your_api_key_here"

   # Windows Command Prompt
   set GROQ_API_KEY=your_api_key_here

   # Linux/Mac
   export GROQ_API_KEY=your_api_key_here
   ```

   **Method 2 - Config File:**

   - Open `config.yaml`
   - Replace `"YOUR_API_KEY_HERE"` with your actual key
   - ⚠️ **Warning:** Never commit your API key to version control!

4. **Run the application**

   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:8000
   ```

---

## 🎯 Usage

### Basic Usage

1. Navigate to `http://localhost:8000`
2. Upload your resume (PDF format, max 5MB)
3. Click **Submit** to get instant analysis

### Advanced Usage with Job Matching

1. Upload your resume
2. Paste a job description in the text area
3. Click **Submit**
4. Get three comprehensive analyses:
   - **ATS Compatibility Score** - How ATS-friendly your resume is
   - **Job Match Score** - How well you match the job
   - **Detailed Resume Analysis** - Complete structured data extraction

---

## 🔒 Security Features

- ✅ Safe YAML loading (prevents code injection)
- ✅ Input validation (size limits on uploads and text)
- ✅ Secure file handling (unique filenames, automatic cleanup)
- ✅ HTTP security headers (XSS, clickjacking protection)
- ✅ API timeout protection (30-second limits)
- ✅ Content Security Policy (CSP)
- ✅ Environment variable support for sensitive data

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_api_key_here

# Optional
FLASK_DEBUG=False              # Enable debug mode (default: False)
FLASK_PORT=8000               # Change server port (default: 8000)
```

### File Size Limits

- Maximum upload size: **5 MB**
- Maximum resume text: **50,000 characters** (~10 pages)
- Maximum job description: **10,000 characters**

---

## 📁 Project Structure

```
resume-parser/
├── app.py                 # Main Flask application
├── resumeparser.py        # AI parsing logic
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── templates/
│   └── index.html        # Main web interface
└── __DATA__/             # Temporary upload directory (auto-created)
```

---

## 🚀 Deployment

### Production Recommendations

1. **Use a production WSGI server:**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Enable HTTPS:** Use Let's Encrypt for free SSL certificates

3. **Set environment variables:**

   ```bash
   export FLASK_DEBUG=False
   export GROQ_API_KEY=your_production_key
   ```

4. **Consider adding:**
   - Rate limiting (Flask-Limiter)
   - CSRF protection (Flask-WTF)
   - Database for user management
   - Redis for caching

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for providing the powerful AI API
- [Flask](https://flask.palletsprojects.com/) for the excellent web framework
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI components

---

## 📧 Contact

For questions, suggestions, or support, please open an issue on GitHub.

---

## ⚠️ Disclaimer

This tool is designed to help job seekers optimize their resumes. While it provides valuable insights, it should not be the sole factor in resume preparation. Always have your resume reviewed by professionals in your field.

---

**Made with ❤️ using Groq AI and Flask**
