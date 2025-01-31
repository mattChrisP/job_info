from string import Template
from typing import Any
# from resume_class import LLMResumeJobDescription
from cv_class import LLMCoverLetterJobDescription
from config import global_config
from utils import html_to_pdf

class ResumeGenerator:
    def __init__(self):
        pass

    def set_resume_object(self, resume_object):
        self.resume_object = resume_object

    def _create_resume(self, gpt_answerer: Any, style_path):
        gpt_answerer.set_resume(self.resume_object)

        template = Template(global_config.html_template)
        
        try:
            with open(style_path, "r") as f:
                style_css = f.read()  
        except FileNotFoundError:
            raise ValueError(f"Style Path not found: {style_path}")
        except Exception as e:
            raise RuntimeError(f"Error: {e}")

        body_html = gpt_answerer.generate_html_resume()

        return template.substitute(body=body_html, style_css=style_css)

    def create_cover_letter_job_description(self, style_path: str, job_description_text: str, output_path: str):
        gpt_answerer = LLMCoverLetterJobDescription()
        gpt_answerer.set_resume(self.resume_object)
        gpt_answerer.set_job_description_from_text(job_description_text)
        cover_letter_html = gpt_answerer.generate_cover_letter()
        template = Template(global_config.html_template)
        with open(style_path, "r") as f:
            style_css = f.read()
        
        final_html_content = template.substitute(body=cover_letter_html, style_css=style_css)
        print(f"Final html format: {final_html_content}")
        html_to_pdf(html_content=final_html_content, output_pdf=output_path)

