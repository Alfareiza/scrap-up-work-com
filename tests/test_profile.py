class TestEmploymentInformation:

    def test_employment_status_active_profile(self, fake_profile, job_history_active_profile):
        """Test the employment status according to a given job history"""
        fake_profile.set_employment_status(job_history_active_profile)
        assert 'active' == fake_profile.info['employment_status']

    def test_employment_termination_date_active_profile(self, fake_profile, job_history_active_profile):
        """Test the termination date according to a given job history"""
        fake_profile.set_employment_termination_date(job_history_active_profile)
        assert None is fake_profile.info['employment_termination_date']

    def test_employment_status_inactive_profile(self, fake_profile, job_history_inactive_profile):
        """Test the termination date according to a given job history"""
        fake_profile.set_employment_status(job_history_inactive_profile)
        assert 'inactive' == fake_profile.info['employment_status']

    def test_employment_termination_date_inactive_profile(self, fake_profile, job_history_inactive_profile):
        """Test the termination date according to a given job history"""
        fake_profile.set_employment_termination_date(job_history_inactive_profile)
        assert '2023-06-01' == fake_profile.info['employment_termination_date']
