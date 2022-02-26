import sys
from typing import Dict, BinaryIO

import requests
from bs4 import BeautifulSoup

import secrets
from utils import get_cookies


class AutolabAssignment:

    # url should be like https://autograder.cse.buffalo.edu/courses/DevUTestCourse/assessments/pdftest/submissions/new
    # You can get this by navigating to an assignment, then Admin Options > Manage Submissions > Create new submission
    def __init__(self, url):
        self.url: str = url
        self.user_id_map: Dict[str, str] = {}  # Map all usernames to their user ID which is necessary to submit something on their behalf
        self.assignment_id: str = ""  # I have no idea why Autolab needs the assignment ID when it's already uniquely identifiable in the URL, but it does :)
        self.is_loaded: bool = False  # Are all the necessary values set from an initial GET request?
        self.authenticity_token: str = ""

    # Make a GET request to get information about the assignment
    def load_data(self):
        response = requests.get(self.url, cookies=get_cookies())
        assert response.status_code == 200, "GET request unsuccessful. Are your authentication secrets set properly in secrets.py?"
        body: bytes = response.content
        soup: BeautifulSoup = BeautifulSoup(body, "html.parser")
        options = soup.find("select", {"name": "submission[course_user_datum_id]"})

        # Handle mapping username to uid
        self.user_id_map = {}

        for op in options.findAll("option"):
            if op["value"]:
                uid: str = op["value"]
                username: str = op.text.split(secrets.EMAIL_ADDRESS_ENDING)[0].split("(")[-1]
                self.user_id_map[username] = uid

        # Get the assignment ID
        assignment_id_element = soup.find("input", {"name": "submission[assessment_id]"})
        self.assignment_id = assignment_id_element["value"]

        # Get the authenticity token
        authenticity_token_element = soup.find("input", {"name": "authenticity_token"})
        self.authenticity_token = authenticity_token_element["value"]

        assert self.user_id_map
        assert self.authenticity_token
        self.is_loaded = True

    def __str__(self):
        return f"Assignment ID {self.assignment_id} ({self.url}) {self.user_id_map}"

    def make_submission(self, student_username: str, file_location: str, note=""):
        assert self.is_loaded, "Assignment hasn't been loaded. You must call load_data() before making submissions!"

        try:
            uid: str = self.user_id_map[student_username]
        except KeyError:
            print(f"ERROR: {student_username} is not a valid username in this course. Halting.")
            sys.exit(1)
        print(f"Making submission for {student_username} with ID {uid} -> {file_location}")

        files: Dict[str, BinaryIO] = {"submission[file]": open(file_location, "rb")}

        form_values: Dict[str, str] = {
            "authenticity_token": self.authenticity_token,
            "commit": "Create Submission",
            "submission[assessment_id]": self.assignment_id,
            "submission[course_user_datum_id]": uid,
            "submission[file]": "submission.pdf",
            "submission[notes]": note,
            "submission[tweak_attributes][kind]": "points",
            "submission[tweak_attributes][value]": "",
            "utf8": "✓"
        }

        post_url: str = self.url[:-4]  # Remove the "/new" from the url because the POST location doesn't have it
        response = requests.post(post_url, cookies=get_cookies(), files=files, data=form_values)
        assert response.status_code == 200, f"{response.content}\n\nSubmission failed."
        print("Submission successful!")
