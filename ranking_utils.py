import os
import json
import spacy
import logging
import pdfplumber

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from utils import generate_cover_letters
from yake import KeywordExtractor

from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from resume_generator import ResumeGenerator
from style_manager import StyleManager

# Load environment variables
load_dotenv(find_dotenv(), override=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load spaCy language model
nlp = spacy.load("en_core_web_sm")


def extract_keywords(job_description, top_n=10):
    """
    Extract essential keywords from the job description using YAKE.
    """
    kw_extractor = KeywordExtractor(lan="en", n=2, top=top_n)  # n=2 for bigrams
    keywords = kw_extractor.extract_keywords(job_description)
    return [keyword[0] for keyword in keywords]


def match_resume_keywords(resume, keywords):
    """
    Check which keywords from the job description are in the resume.
    """
    resume_doc = nlp(resume.lower())
    resume_tokens = [token.text for token in resume_doc if token.is_alpha]
    matched_keywords = [kw for kw in keywords if kw.lower() in resume_tokens]
    missing_keywords = [kw for kw in keywords if kw.lower() not in resume_tokens]
    return matched_keywords, missing_keywords


def parse_jobs(job_listings):
    parsed_jobs = []
    for job in job_listings:
        parsed_jobs.append({
            "id": job["id"],
            "title": job["title"],
            "description": job["description"],  # Complete description
            "keywords": extract_keywords(job["description"]),  # Extracted keywords for ranking
            "url": job.get("url", ""),  # Add URL
            "employment_type": job.get("employment_type", ""),  # Add employment type
            "published_since": job.get("published_since", ""),  # Add publication date
        })
    return parsed_jobs


def extract_text_from_pdf_plumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''.join(page.extract_text() for page in pdf.pages)
    return text


# Define ranking system
def rank_jobs(resume, jobs):

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Embed the resume
    resume_embedding = [embeddings.embed_query(resume)]

    ranked_jobs = []
    for job in jobs:
        # Embed the job description
        job_embedding = [embeddings.embed_query(job["description"])]
        
        # Calculate similarity score
        similarity_score = cosine_similarity(resume_embedding, job_embedding)

        # Extract keywords and check match
        keywords = job["keywords"]
        matched_keywords = [kw for kw in keywords if kw.lower() in resume.lower()]
        keyword_score = len(matched_keywords) / len(keywords) if keywords else 0

        # Combine scores
        final_score = 0.5 * similarity_score + 0.5 * keyword_score

        ranked_jobs.append({
            "id": job["id"],
            "title": job["title"],
            "description": job["description"],
            "score": final_score,
            "url": job.get("url", ""),
            "employment_type": job.get("employment_type", ""),  
            "published_since": job.get("published_since", ""),
            "matched_keywords": matched_keywords,
            "missing_keywords": [kw for kw in keywords if kw.lower() not in resume.lower()]
        })

    # Sort jobs by score
    return sorted(ranked_jobs, key=lambda x: x["score"], reverse=True)


def generate_ranking_and_save_cv():
    today = datetime.now().strftime("%Y-%m-%d")
    job_filename = f"jobs_{today}.json"

    with open(job_filename, "r") as file:
        job_listings = json.load(file)

    jobs = job_listings.get("hits", None)

    parsed_jobs = parse_jobs(jobs)
    resume_text = extract_text_from_pdf_plumber("Resume.pdf")

    # Example: Rank jobs
    ranked_jobs = rank_jobs(resume_text, parsed_jobs)

    # Generate cover letters and save as PDFs
    style_manager = StyleManager()
    resume_generator = ResumeGenerator()
    output_directory = "output_cover_letters"  # Specify the directory for PDFs

    cover_letters = generate_cover_letters(
        resume_text, ranked_jobs, style_manager, resume_generator, output_directory
    )

    # Save metadata about generated cover letters
    with open("generated_cover_letters.json", "w") as file:
        json.dump(cover_letters, file, indent=4)

    print(f"Cover letters saved in: {output_directory}")



