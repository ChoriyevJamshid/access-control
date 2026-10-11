import os
import json
import random
import requests
from datetime import datetime, timedelta

base_url = 'http://127.0.0.1:8000/api/v1/'


def search_employee(code: str | int):
    url = base_url + 'employees/search/'
    data = {'code': code}
    auth = ('admin', 'admin')
    response = requests.post(url=url, json=data, auth=auth)

    if response.status_code == 200:
        response_data = response.json()
        return response_data['id']
    return None


def create_employee_access_event(employee_id):
    url = base_url + 'access-controls/create/'
    employee_worksheet = read_employee_worksheet(employee_id)

    for payload in employee_worksheet:
        _id = payload.pop('id')
        payload.update(employee=int(_id))
        response = requests.post(url=url,
                                 json=payload,
                                 auth=('admin', 'admin'))

        print(response.status_code)
        print(response.text)
        # input(">>> ")


def create_employee_worksheet(employee_id: int):
    employee = []

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    current_date = start_date

    while current_date <= end_date:
        employee.extend([
            {
                'id': employee_id,
                'timestamp': str(current_date.replace(hour=8, minute=random.randint(30, 59), second=0)),
                'type': 'enter'
            },
            {
                'id': employee_id,
                'timestamp': str(current_date.replace(hour=11, minute=random.randint(30, 59), second=0)),
                'type': 'leave'
            },
            {
                'id': employee_id,
                'timestamp': str(current_date.replace(hour=13, minute=random.randint(1, 30), second=0)),
                'type': 'enter'
            },
            {
                'id': employee_id,
                'timestamp': str(current_date.replace(hour=17, minute=random.randint(50, 59), second=0)),
                'type': 'leave'
            },
        ])

        current_date += timedelta(days=1)

    os.makedirs("employees", exist_ok=True)

    with open(f"employees/employee_{employee_id}.json", "w") as json_file:
        json.dump(employee, json_file, indent=4, ensure_ascii=False)


def read_employee_worksheet(employee_id: int):
    with open(f"employees/employee_{employee_id}.json", "r") as json_file:
        data = json.load(json_file)
    return data


for i in range(1, 51):
    # create_employee_worksheet(i)
    create_employee_access_event(i)
