"""
Tests for the projects application.
"""
from django.test import TestCase
from projects.models import Project


# Create your tests here.
class ProjectTestCase(TestCase):
    """
    Tests for the projects application.
    """
    def test_project_creation(self):
        """
        Test the creation of a project.
        """
        project = Project.objects.create(name="Test Project")
        self.assertEqual(project.name, "Test Project")
