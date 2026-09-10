import urllib.request
import urllib.parse
import json
import http.cookiejar
import time

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

# Generate unique username
username = f"user_{int(time.time())}"
email = f"{username}@campus.edu"

print(f"Testing with new student account: {username}")

# 1. Register student
reg_data = urllib.parse.urlencode({
    'username': username,
    'email': email,
    'password': 'testpassword123',
    'confirm_password': 'testpassword123'
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:5000/register', data=reg_data)
res = opener.open(req)
print('Register status:', res.status)

# 2. Check initial stats (MUST BE 0 - No static/dummy data)
stats_res = opener.open('http://127.0.0.1:5000/api/stats')
stats = json.loads(stats_res.read().decode('utf-8'))
print('Initial zero stats:', stats)
assert stats['total'] == 0, f"Expected 0 total tasks, got {stats['total']}"
assert stats['completed'] == 0
assert stats['pending'] == 0
assert stats['overdue'] == 0
assert len(stats['subjects']) == 0

# 3. Create a real task
task_data = json.dumps({
    'title': 'Quantum Physics Problem Set 2',
    'description': 'Solve Schrödinger equation for particle in a box.',
    'subject': 'Physics',
    'priority': 'High',
    'due_date': '2026-11-01'
}).encode('utf-8')

task_req = urllib.request.Request('http://127.0.0.1:5000/api/tasks', data=task_data, headers={'Content-Type': 'application/json'})
task_res = opener.open(task_req)
new_task = json.loads(task_res.read().decode('utf-8'))['task']
task_id = new_task['id']
print(f"Created task: {task_id}, '{new_task['title']}' ({new_task['priority']} Priority)")

# 4. Toggle task
toggle_req = urllib.request.Request(f'http://127.0.0.1:5000/api/tasks/{task_id}/toggle', data=b'', headers={'Content-Type': 'application/json'})
toggle_res = opener.open(toggle_req)
toggled = json.loads(toggle_res.read().decode('utf-8'))['task']
print('Toggled status to:', toggled['status'])
assert toggled['status'] == 'Completed'

# 5. Delete task
del_req = urllib.request.Request(f'http://127.0.0.1:5000/api/tasks/{task_id}', headers={'Content-Type': 'application/json'})
del_req.get_method = lambda: 'DELETE'
del_res = opener.open(del_req)
print('Delete result:', json.loads(del_res.read().decode('utf-8')))

# 6. Verify empty again
final_stats = json.loads(opener.open('http://127.0.0.1:5000/api/stats').read().decode('utf-8'))
assert final_stats['total'] == 0
print("Workspace cleanly empty after deletion. ALL E2E TESTS PASSED!")
