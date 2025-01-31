from weasyprint import HTML, CSS
import os
import shutil
from datetime import datetime, timedelta

def html_to_pdf(html_content, output_pdf):
    """
    Convert HTML content (with embedded CSS) to a PDF.

    :param html_content: HTML content as a string with embedded CSS.
    :param output_pdf: Path to save the generated PDF.
    """
    try:
        # Generate the PDF directly from the HTML content
        HTML(string=html_content).write_pdf(output_pdf)
        print(f"PDF successfully saved at {output_pdf}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


def clean_date(iso_date):
    """
    Clean the ISO date to a more readable format.
    
    :param iso_date: ISO 8601 date string.
    :return: Formatted date string (e.g., "January 13, 2025").
    """
    date_obj = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date_obj.strftime("%B %d, %Y")


def get_date_range():
    """
    Get the date range for the email subject (last month to today).
    
    :return: String representing the date range.
    """
    today = datetime.today()
    last_month = today - timedelta(days=30)
    return f"{last_month.strftime('%B %d, %Y')} - {today.strftime('%B %d, %Y')}"


def cleanup_old_files():
    # Get the date for yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Construct the filename for yesterday
    filename = f"jobs_{yesterday}.json"

    # Check if the file exists and remove it
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Removed file: {filename}")
    else:
        print(f"File not found: {filename}")

    # Directory to be removed
    directory = "output_cover_letters"

    # Check if the directory exists and remove it (even if non-empty)
    if os.path.exists(directory) and os.path.isdir(directory):
        try:
            shutil.rmtree(directory)  # Removes non-empty directories
            print(f"Removed directory: {directory}")
        except Exception as e:
            print(f"Failed to remove directory '{directory}'. Error: {e}")
    else:
        print(f"Directory not found: {directory}")


def generate_cover_letters(resume_text, ranked_jobs, style_manager, resume_generator, output_dir):
    """
    Generates cover letters for the ranked jobs and saves them as PDF files.
    
    Args:
        resume_text (str): The text of the resume.
        ranked_jobs (list): Ranked job data.
        style_manager (StyleManager): Instance of the StyleManager class.
        resume_generator (ResumeGenerator): Instance of the ResumeGenerator class.
        output_dir (str): Directory where cover letters will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

    cover_letters = []

    # Get the style path for the cover letter
    style_manager.set_selected_style("Cloyola Grey")  # Example style
    style_path = style_manager.get_style_path()

    for i, job in enumerate(ranked_jobs, start=1):
        job_description = job["description"]
        resume_generator.set_resume_object(resume_text)

        # Generate a unique filename for each cover letter
        filename = f"cover_letter_{i}_{job['title'].replace(' ', '_')}.pdf"
        output_path = os.path.join(output_dir, filename)

        # Generate and save the cover letter as a PDF
        resume_generator.create_cover_letter_job_description(
            style_path, job_description_text=job_description, output_path=output_path
        )

        cover_letters.append({
            "job_id": job["id"],
            "job_title": job["title"],
            "cover_letter_path": output_path,
            "url": job["url"],
            "matched_keywords": job.get("matched_keywords",""),
            "missing_keywords": job.get("missing_keywords",""),
            "employment_type": job["employment_type"],
            "published_since": clean_date(job["published_since"])
        })

    return cover_letters







