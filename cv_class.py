"""
This creates the cover letter (in html, utils will then convert in PDF) matching with job description and plain-text resume
"""


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv, find_dotenv
from requests.exceptions import HTTPError as HTTPStatusError

from prompts import COVER_LETTER_TEMPLATE, SUMMARIZE_PROMPT_TEMPLATE


import re
import textwrap
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv(), override=True)


class LLMCoverLetterJobDescription:
    def __init__(self):
        self.llm_cheap = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', temperature=0.9)
        self.llm_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        """
        Preprocess the template string by removing leading whitespace and indentation.
        Args:
            template (str): The template string to preprocess.
        Returns:
            str: The preprocessed template string.
        """
        return textwrap.dedent(template)

    def set_resume(self, resume) -> None:
        """
        Set the resume text to be used for generating the cover letter.
        Args:
            resume (str): The plain text resume to be used.
        """
        self.resume = resume

    def set_job_description_from_text(self, job_description_text) -> None:
        """
        Set the job description text to be used for generating the cover letter.
        Args:
            job_description_text (str): The plain text job description to be used.
        """
        logger.debug("Starting job description summarization...")
        prompt = ChatPromptTemplate.from_template(SUMMARIZE_PROMPT_TEMPLATE)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"text": job_description_text})
        self.job_description = output
        logger.debug(f"Job description summarization complete: {self.job_description}")

    def clean_html_output(self, html_content):
        """
        Removes unwanted ```html at the beginning of the HTML string.
        
        :param html_content: The raw HTML string.
        :return: The cleaned HTML string.
        """
        # Use regex to remove ```html at the beginning
        cleaned_content = re.sub(r"^```html\s*|\s*```$", "", html_content, flags=re.IGNORECASE)
        return cleaned_content

    def generate_cover_letter(self) -> str:
        """
        Generate the cover letter based on the job description and resume.
        Returns:
            str: The generated cover letter
        """
        logger.debug("Starting cover letter generation...")
        prompt_template = self._preprocess_template_string(COVER_LETTER_TEMPLATE)
        logger.debug(f"Cover letter template after preprocessing: {prompt_template}")

        prompt = ChatPromptTemplate.from_template(prompt_template)
        logger.debug(f"Prompt created: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "job_description": self.job_description,
            "resume": self.resume
        }
        logger.debug(f"Input data: {input_data}")

        output = chain.invoke(input_data)
        cleaned_output = self.clean_html_output(output)


        logger.debug(f"Cover letter generation result: {cleaned_output}")

        logger.debug("Cover letter generation completed")
        return cleaned_output
