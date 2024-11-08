import unittest
from main import app, weekly_planner
from datetime import datetime
from flask import url_for


class QuestieTestCase(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.client = app.test_client()
        self.client.testing = True

        # Reset weekly_planner before each test is conducted
        for day in weekly_planner:
            weekly_planner[day] = []

    def tearDown(self):
        # Clean up after each test
        pass

    def test_create_valid_quest(self):
        # Test creating a valid quest
        response = self.client.post('/add_quest/Monday', data={
            'title': 'Test Quest',
            'start_time': '10:00',
            'end_time': '12:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quest added successfully!', response.data)

        # Check the quest was added successfully
        self.assertEqual(len(weekly_planner['Monday']), 1)
        quest = weekly_planner['Monday'][0]
        self.assertEqual(quest['title'], 'Test Quest')
        self.assertEqual(quest['start_time'], '10:00')
        self.assertEqual(quest['end_time'], '12:00')
        self.assertEqual(quest['location'], 'Test Location')
        self.assertEqual(quest['description'], 'Test Description')
        self.assertFalse(quest['completed'])

    def test_create_quest_insufficient_input(self):
        # Test creating a quest with missing required inputs
        response = self.client.post('/add_quest/Tuesday', data={
            'title': '',
            'start_time': '10:00',
            'end_time': '12:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Title, start time, and end time are required!', response.data)

        # Ensure quest wasn't addded
        self.assertEqual(len(weekly_planner['Tuesday']), 0)

    def test_create_quest_end_time_before_start_time(self):
        # Test creating a quest where end_time is before start_time
        response = self.client.post('/add_quest/Wednesday', data={
            'title': 'Invalid Time Quest',
            'start_time': '14:00',
            'end_time': '12:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'End time must be after start time.', response.data)

        # Ensure quest wasn't added
        self.assertEqual(len(weekly_planner['Wednesday']), 0)

    def test_create_quest_invalid_time_format(self):
        # Test creating a quest with an invalid time format
        response = self.client.post('/add_quest/Thursday', data={
            'title': 'Invalid Time Format',
            'start_time': 'invalid',  # Invalid time format
            'end_time': '12:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)
        # Expecting server to handle invalid time format
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid time format!', response.data)

        # Ensure quest wasn't added
        self.assertEqual(len(weekly_planner['Thursday']), 0)

    def test_complete_quest(self):
        # Add a quest
        self.client.post('/add_quest/Friday', data={
            'title': 'Complete me',
            'start_time': '09:00',
            'end_time': '10:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)
        # Mark quest as "completed"
        response = self.client.post('/complete_quest/Friday/0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quest marked as completed!', response.data)
        # Check that quest is marked as "completed"
        quest = weekly_planner['Friday'][0]
        self.assertTrue(quest['completed'])

    def test_delete_quest(self):
        # Add a quest
        self.client.post('/add_quest/Saturday', data={
            'title': 'Delete Me',
            'start_time': '11:00',
            'end_time': '12:00',
            'location': 'Test Location',
            'description': 'Test Description'
        }, follow_redirects=True)

        # Delete the quest
        response= self.client.post('/quest/delete/Saturday/0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quest was deleted successfully!', response.data)

        # Ensure quest is deleted
        self.assertEqual(len(weekly_planner['Saturday']), 0)

    def test_delete_nonexistent_quest(self):
        # Attempt to delete a quest that doesn't exist
        response = self.client.post('/quest/delete/Sunday/0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid quest index!', response.data)

        # Ensure planner is still empty
        self.assertEqual(len(weekly_planner['Sunday']), 0)
