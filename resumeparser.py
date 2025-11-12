# import libraries

from openai import OpenAI
import yaml
import os
import json

api_key = None
CONFIG_PATH = r"config.yaml"

# Try to get API key from environment first, then fallback to config file
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        with open(CONFIG_PATH) as file:
            data = yaml.safe_load(file)  # Use safe_load to prevent code execution
            api_key = data.get('GROQ_API_KEY')
    except FileNotFoundError:
        print(f"Warning: Config file {CONFIG_PATH} not found and GROQ_API_KEY environment variable not set")
    except Exception as e:
        print(f"Warning: Error reading config file: {str(e)}")

if not api_key or api_key == "YOUR KEY HERE":
    raise ValueError(
        "Groq API key not configured. Please set the GROQ_API_KEY environment variable "
        "or update the key in config.yaml"
    )

def ats_extractor(resume_data):
    """
    Extract structured information from resume text using Groq AI.
    
    Args:
        resume_data: String containing the resume text
    
    Returns:
        JSON string with extracted information
    
    Raises:
        Exception: If Groq API call fails
    """
    if not resume_data or not resume_data.strip():
        raise ValueError("Resume data is empty")

    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. Extract ALL available information from the resume and return it in the following JSON format.

    IMPORTANT: Return ONLY valid JSON. No explanatory text before or after.

    {
      "full_name": "string",
      "email": "string",
      "phone": "string",
      "location": "string",
      "linkedin_url": "string",
      "github_url": "string",
      "portfolio_url": "string",
      "summary": "string",
      "education": [
        {
          "degree": "string",
          "institution": "string",
          "graduation_year": "string",
          "gpa": "string",
          "relevant_coursework": "string"
        }
      ],
      "work_experience": [
        {
          "company_name": "string",
          "job_title": "string",
          "start_date": "string",
          "end_date": "string",
          "responsibilities": ["string"],
          "achievements": ["string"]
        }
      ],
      "projects": [
        {
          "project_name": "string",
          "description": "string",
          "technologies_used": ["string"],
          "link": "string",
          "duration": "string"
        }
      ],
      "leadership_roles": [
        {
          "role_title": "string",
          "organization": "string",
          "duration": "string",
          "responsibilities": ["string"]
        }
      ],
      "volunteering_experience": [
        {
          "organization": "string",
          "role": "string",
          "duration": "string",
          "activities": ["string"]
        }
      ],
      "technical_skills": {
        "programming_languages": ["string"],
        "frameworks": ["string"],
        "tools": ["string"],
        "databases": ["string"],
        "cloud_platforms": ["string"],
        "other_technical_skills": ["string"]
      },
      "soft_skills": ["string"],
      "certifications": [
        {
          "certification_name": "string",
          "issuing_organization": "string",
          "date_obtained": "string"
        }
      ],
      "awards_and_achievements": [
        {
          "award_name": "string",
          "issuing_organization": "string",
          "date": "string",
          "description": "string"
        }
      ],
      "languages": [
        {
          "language_name": "string",
          "proficiency_level": "string"
        }
      ],
      "publications": [
        {
          "title": "string",
          "publication_venue": "string",
          "date": "string",
          "co_authors": "string"
        }
      ]
    }

    Extract as much detail as possible from the resume. If information is not available for a field, use empty string "" for strings or empty array [] for arrays.
    '''

    try:
        # Initialize Groq client with timeout
        groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0  # 30 second timeout
        )

        messages=[
            {"role": "system", "content": prompt}
        ]
        
        user_content = resume_data
        
        messages.append({"role": "user", "content": user_content})

        response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=3500)
            
        data = response.choices[0].message.content

        return data
    
    except Exception as e:
        raise Exception(f"Failed to extract resume information: {str(e)}")


def calculate_job_match(resume_data, parsed_resume, job_description):
    """
    Calculate how well the resume matches the job description.
    
    Args:
        resume_data: String containing the raw resume text
        parsed_resume: Dict with parsed resume data
        job_description: String containing the job description
    
    Returns:
        Dict with match score and detailed analysis
    """
    if not job_description or not job_description.strip():
        return None
    
    prompt = f'''
    You are an expert HR analyst. Analyze how well this resume matches the job description and provide a detailed assessment.

    RESUME DATA:
    {resume_data[:3000]}  # Limit to avoid token overflow

    JOB DESCRIPTION:
    {job_description}

    Provide a comprehensive analysis in the following JSON format:

    {{
      "overall_match_score": <number 0-100>,
      "category_scores": {{
        "skills_match": <number 0-100>,
        "experience_match": <number 0-100>,
        "education_match": <number 0-100>,
        "keyword_match": <number 0-100>
      }},
      "matching_skills": ["skill1", "skill2"],
      "missing_skills": ["skill1", "skill2"],
      "matching_keywords": ["keyword1", "keyword2"],
      "missing_keywords": ["keyword1", "keyword2"],
      "strengths": ["strength1", "strength2"],
      "recommendations": ["recommendation1", "recommendation2"],
      "summary": "Brief summary of the match"
    }}

    Be specific and actionable in your recommendations.
    '''

    try:
        groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0  # 30 second timeout
        )

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst specializing in resume-job matching."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            import json
            match_data = json.loads(result)
            return match_data
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                try:
                    match_data = json.loads(json_match.group(0))
                    return match_data
                except:
                    pass
            
            # If all fails, return a basic structure
            return {
                "overall_match_score": 50,
                "summary": "Unable to parse detailed analysis. Please try again.",
                "error": "JSON parsing failed"
            }
    
    except Exception as e:
        raise Exception(f"Failed to calculate job match: {str(e)}")


def calculate_ats_score(resume_data, parsed_resume):
    """
    Calculate ATS (Applicant Tracking System) score for a resume.
    Analyzes format, structure, keywords, and completeness.
    
    Args:
        resume_data: String containing the raw resume text
        parsed_resume: Dictionary with parsed resume data
    
    Returns:
        Dictionary containing ATS score and detailed breakdown
    
    Raises:
        Exception: If AI API call fails
    """
    if not resume_data or not resume_data.strip():
        raise ValueError("Resume data is empty")
    
    prompt = f'''
    You are an expert ATS (Applicant Tracking System) analyzer. Evaluate this resume and provide a comprehensive ATS compatibility score.

    Resume Data:
    {resume_data}

    Parsed Information:
    {json.dumps(parsed_resume, indent=2)}

    Analyze the resume based on these ATS criteria and provide scores (0-100) for each:

    1. **Contact Information Completeness (10%)**: Are name, email, phone, location provided?
    2. **Keyword Density (25%)**: Does it have relevant industry keywords, skills, and job-related terms?
    3. **Format Compatibility (15%)**: Is the structure clean, parseable, no complex formatting?
    4. **Section Organization (15%)**: Are standard sections present (Experience, Education, Skills)?
    5. **Experience Quantification (15%)**: Are achievements quantified with metrics and numbers?
    6. **Education Details (10%)**: Is education information complete (degree, institution, year)?
    7. **Skills Presence (10%)**: Are technical and soft skills clearly listed?

    Return your analysis in this EXACT JSON format (no additional text):
    {{
        "overall_ats_score": <number 0-100>,
        "category_scores": {{
            "contact_info": <number 0-100>,
            "keyword_density": <number 0-100>,
            "format_compatibility": <number 0-100>,
            "section_organization": <number 0-100>,
            "experience_quantification": <number 0-100>,
            "education_details": <number 0-100>,
            "skills_presence": <number 0-100>
        }},
        "strengths": [
            "List 3-5 specific strengths that make this resume ATS-friendly"
        ],
        "weaknesses": [
            "List 3-5 specific weaknesses that hurt ATS compatibility"
        ],
        "improvement_suggestions": [
            "Provide 5-7 specific, actionable suggestions to improve ATS score"
        ],
        "keyword_analysis": {{
            "present_keywords": ["list of 10-15 important keywords found in resume"],
            "missing_keywords": ["list of 10-15 common industry keywords that should be added"]
        }},
        "format_issues": [
            "List any formatting issues (tables, images, columns, special characters, etc.)"
        ],
        "summary": "2-3 sentence overall assessment of ATS readiness"
    }}
    '''

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0  # 30 second timeout
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an ATS expert. Return only valid JSON, no other text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.2
        )
        
        content = response.choices[0].message.content.strip()
        print(f"DEBUG - ATS Score Raw Response: {content[:500]}...")
        
        # Try to parse the JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            ats_data = json.loads(content)
            
            # Validate required fields
            if "overall_ats_score" not in ats_data:
                ats_data["overall_ats_score"] = 70
            
            return ats_data
            
        except json.JSONDecodeError as e:
            print(f"DEBUG - JSON Decode Error: {str(e)}")
            print(f"DEBUG - Failed content: {content}")
            
            # Try to extract JSON from the response using regex
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    ats_data = json.loads(json_match.group(0))
                    return ats_data
                except:
                    pass
            
            # If all fails, return a basic structure
            return {
                "overall_ats_score": 70,
                "summary": "Unable to generate detailed ATS analysis. Please try again.",
                "error": "JSON parsing failed"
            }
    
    except Exception as e:
        raise Exception(f"Failed to calculate ATS score: {str(e)}")