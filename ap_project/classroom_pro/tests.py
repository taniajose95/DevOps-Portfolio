from django.test import TestCase
from django.urls import reverse


class SignUpFormTest(TestCase):
    def test_valid_form_submission(self):
        # Create a dictionary with sample valid form data
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'name': 'Test User',
            'role': 'Student',
            'department': 'Computer Science'
        }

        # Simulate a POST request with the form data
        response = self.client.post(reverse('signup'), form_data)

        # Check if the form submission was successful (HTTP status code 302)
        self.assertEqual(response.status_code, 302)

        # Check if the user was redirected to the login page (assuming successful signup redirects to login)
        self.assertRedirects(response, reverse('login'))
