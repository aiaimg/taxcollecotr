from django.test.runner import DiscoverRunner


class NoCheckTestRunner(DiscoverRunner):
    def run_checks(self, databases=None):
        return []
