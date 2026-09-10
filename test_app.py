import unittest
import json
from app import create_app
from database import init_db

class StudentTaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        # Reset database cleanly before each test run
        init_db(reset=True)
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_user_registration_zero_static_data(self):
        """Verify user registration starts with a completely clean workspace (zero tasks)."""
        response = self.client.post('/register', data={
            'username': 'cleanstudent',
            'email': 'clean@student.edu',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check tasks endpoint - MUST BE ZERO (no dummy data)
        tasks_res = self.client.get('/api/tasks')
        self.assertEqual(tasks_res.status_code, 200)
        data = json.loads(tasks_res.data)
        self.assertEqual(len(data['tasks']), 0)

        # Check stats endpoint - MUST BE ZERO
        stats_res = self.client.get('/api/stats')
        self.assertEqual(stats_res.status_code, 200)
        stats = json.loads(stats_res.data)
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['completed'], 0)
        self.assertEqual(stats['pending'], 0)
        self.assertEqual(stats['overdue'], 0)
        self.assertEqual(stats['completion_rate'], 0)

    def test_02_task_crud_operations(self):
        """Verify creating, reading, updating, toggling, and deleting tasks dynamically."""
        # Register user
        self.client.post('/register', data={
            'username': 'activestudent',
            'email': 'active@student.edu',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        # 1. Create a task
        create_res = self.client.post('/api/tasks', json={
            'title': 'Operating Systems Virtual Memory Lab',
            'description': 'Implement page replacement algorithms (FIFO, LRU, Clock).',
            'subject': 'Computer Science',
            'priority': 'High',
            'due_date': '2026-10-15'
        })
        self.assertEqual(create_res.status_code, 201)
        created = json.loads(create_res.data)['task']
        task_id = created['id']
        self.assertEqual(created['title'], 'Operating Systems Virtual Memory Lab')
        self.assertEqual(created['status'], 'Pending')

        # 2. Stats reflect 1 total, 1 pending
        stats_res = self.client.get('/api/stats')
        stats = json.loads(stats_res.data)
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completed'], 0)

        # 3. Toggle task to Completed
        toggle_res = self.client.post(f'/api/tasks/{task_id}/toggle')
        self.assertEqual(toggle_res.status_code, 200)
        toggled = json.loads(toggle_res.data)['task']
        self.assertEqual(toggled['status'], 'Completed')

        # Check updated completion rate (100%)
        stats_res = self.client.get('/api/stats')
        stats = json.loads(stats_res.data)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['completion_rate'], 100)

        # 4. Update task details
        update_res = self.client.put(f'/api/tasks/{task_id}', json={
            'title': 'OS Virtual Memory Lab - Submission Ready',
            'description': 'Submitted benchmark logs.',
            'subject': 'Computer Science',
            'priority': 'Medium',
            'due_date': '2026-10-16',
            'status': 'Completed'
        })
        self.assertEqual(update_res.status_code, 200)
        updated = json.loads(update_res.data)['task']
        self.assertEqual(updated['title'], 'OS Virtual Memory Lab - Submission Ready')

        # 5. Delete task
        delete_res = self.client.delete(f'/api/tasks/{task_id}')
        self.assertEqual(delete_res.status_code, 200)

        # Confirm deleted and list is empty again
        check_res = self.client.get('/api/tasks')
        tasks = json.loads(check_res.data)['tasks']
        self.assertEqual(len(tasks), 0)

    def test_03_login_validation(self):
        """Verify wrong password cannot log in."""
        self.client.post('/register', data={
            'username': 'studentsec',
            'email': 'sec@student.edu',
            'password': 'validpassword',
            'confirm_password': 'validpassword'
        }, follow_redirects=True)

        # Log out first
        self.client.get('/logout', follow_redirects=True)

        res = self.client.post('/login', data={
            'identifier': 'studentsec',
            'password': 'invalidpassword'
        }, follow_redirects=True)
        self.assertIn(b'Incorrect password', res.data)

if __name__ == '__main__':
    unittest.main()
