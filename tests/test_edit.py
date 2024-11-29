import os
import unittest
from main import app
import main

class EditQuestTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_ENV'] = 'test'
        self.client = app.test_client()
        self.client.testing = True
        main.reset_planner()

    def tearDown(self):
        pass

    def test_edit_quest_success(self):
        # Add a quest to edit
        self.client.post('/add_quest/Monday', data={
            'title': 'Original Quest',
            'start_time': '10:00',
            'end_time': '12:00',
            'location': 'Original Location',
            'description': 'Original Description'
        }, follow_redirects=True)
        # Edit the quest with valid data
        response = self.client.post('/quest/edit/Monday/0', data={
            'title': 'Updated Quest',
            'start_time': '11:00',
            'end_time': '13:00',
            'location': 'Updated Location',
            'description': 'Updated Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quest updated successfully!', response.data)
        # Verify the quest was updated
        quest = main.weekly_planner['Monday'][0]
        self.assertEqual(quest['title'], 'Updated Quest')
        self.assertEqual(quest['start_time'], '11:00')
        self.assertEqual(quest['end_time'], '13:00')
        self.assertEqual(quest['location'], 'Updated Location')
        self.assertEqual(quest['description'], 'Updated Description')

    def test_edit_quest_invalid_time_format(self):
        # Add a quest to edit
        self.client.post('/add_quest/Tuesday', data={
            'title': 'Quest To Edit',
            'start_time': '10:00',
            'end_time': '12:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        # Attempt to edit the quest with an invalid time format
        response = self.client.post('/quest/edit/Tuesday/0', data={
            'title': 'Updated Quest',
            'start_time': 'invalid',  # Invalid time format
            'end_time': '12:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid time format!', response.data)
        # Ensure the quest remains unchanged
        quest = main.weekly_planner['Tuesday'][0]
        self.assertEqual(quest['title'], 'Quest To Edit')

    def test_edit_quest_end_time_before_start_time(self):
        # Add a quest to edit
        self.client.post('/add_quest/Wednesday', data={
            'title': 'Quest To Edit',
            'start_time': '09:00',
            'end_time': '11:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        # Attempt to edit the quest with end time before start time
        response = self.client.post('/quest/edit/Wednesday/0', data={
            'title': 'Updated Quest',
            'start_time': '10:00',
            'end_time': '09:00',  # Invalid time range
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'End time must be after start time.', response.data)
        # Ensure the quest remains unchanged
        quest = main.weekly_planner['Wednesday'][0]
        self.assertEqual(quest['end_time'], '11:00')

    def test_edit_quest_missing_required_fields(self):
        # Add a quest to edit
        self.client.post('/add_quest/Thursday', data={
            'title': 'Quest To Edit',
            'start_time': '08:00',
            'end_time': '10:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        # Attempt to edit the quest with missing required fields
        response = self.client.post('/quest/edit/Thursday/0', data={
            'title': '',  # Missing title
            'start_time': '08:00',
            'end_time': '10:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Title, start time, and end time are required!', response.data)
        # Ensure the quest remains unchanged
        quest = main.weekly_planner['Thursday'][0]
        self.assertEqual(quest['title'], 'Quest To Edit')

    def test_edit_nonexistent_quest(self):
        # Attempt to edit a quest with an invalid index
        response = self.client.post('/quest/edit/Friday/99', data={
            'title': 'Nonexistent Quest',
            'start_time': '09:00',
            'end_time': '10:00',
            'location': 'Location',
            'description': 'Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid quest index!', response.data)

if __name__ == '__main__':
    unittest.main()

