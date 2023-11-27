from bs4 import BeautifulSoup

from resources.models import (
    JobsAndProfileSchema,
    JobSchema,
    JobsSchemaList,
    ProfileSchema,
)
from settings import BASE_DIR
from utils.file_utils import remove_folder


class TestParserHtml:
    def test_prepare_data_files_folder_when_doesnt_exists(self, upwork_scanner):
        """Test the pre"""
        folder_files = BASE_DIR / 'files'
        if folder_files.exists():
            remove_folder(folder_files)

        soup = upwork_scanner.prepare_data('this is the html content', 'foo_page')
        try:
            assert soup
        finally:
            remove_folder(folder_files)

    def test_type_return_prepare_data(self, jobs_page):
        """Test instance of prepare data is a BeautifulSoup instance"""
        assert isinstance(jobs_page, BeautifulSoup)

    def test_quantity_jobs(self, jobs):
        """"Test capturing jobs information"""
        assert len(jobs) > 1

    def test_generating_schemajob_from_scanned_data(self, upwork_scanner, jobs):
        """"Test the creation of schema with information"""
        assert [JobSchema(**upwork_scanner.parse_job(job)) for job in jobs]

    def test_generating_schemajobs_from_scanned_data(self, upwork_scanner, jobs):
        """"Test the creation of schema with information"""
        jobs = [upwork_scanner.parse_job(job) for job in jobs]
        assert JobsSchemaList(jobs=jobs)

    def test_generating_schemaprofile_from_scanned_data(self, profile_content):
        """"Test the creation of schema with information"""
        assert ProfileSchema(**profile_content)

    def test_exporting_jobs_and_profile_information(self, upwork_scanner, jobs, profile_content):
        jobs = [upwork_scanner.parse_job(job) for job in jobs]
        JobsAndProfileSchema(jobs=jobs, profile=profile_content)
