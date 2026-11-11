import base64
import json
import re
import secrets
from typing import BinaryIO

import requests
from bs4 import BeautifulSoup, Tag

from utils import get_cookies


class AutolabError(RuntimeError):
    """Raised when Autolab returns something unexpected (bad session, changed page layout, failed upload)."""


class AutolabAssignment:
    # url should be like https://autograder.cse.buffalo.edu/courses/DevUTestCourse/assessments/pdftest/submissions/new
    # You can get this by navigating to an assignment, then Admin Options > Manage Submissions > Create new submission
    def __init__(self, url):
        self.url: str = url
        # Map all usernames to their user ID, which is necessary to submit something on their behalf
        self.user_id_map: dict[str, str] = {}
        # Autolab needs the assignment ID even though it's already identifiable from the URL
        self.assignment_id: str = ""
        self.is_loaded: bool = False  # Are all the necessary values set from an initial GET request?
        self.authenticity_token: str = ""

    # Make a GET request to get information about the assignment
    def load_data(self):
        response = requests.get(self.url, cookies=get_cookies())
        if response.status_code != 200:
            raise AutolabError(
                f"GET request unsuccessful (HTTP {response.status_code}). "
                "Are your authentication secrets set properly in secrets.py?"
            )
        body: bytes = response.content
        soup: BeautifulSoup = BeautifulSoup(body, "html.parser")
        scripts = soup.find_all("script")
        script_identifier_string = (
            "/* requires @usersEncoded and @users to be set, i.e. via Course.get_autocomplete_data */"
        )

        options: dict[str, str] | None = None
        for script in scripts:
            if script.text and script_identifier_string in script.text:
                match_str: str = re.findall("const userData = ({.*});", script.text, re.S)[0]
                match_json: str = match_str.replace(",\n    }", "}")  # Remove the invalid trailing comma
                match_dict: dict = json.loads(match_json)
                options = {base64.b64decode(k).decode(): v for k, v in match_dict.items()}
                # Options is a dict with keys like "Student1 One (student1@buffalo.edu)" and values like "1234"
                break  # Don't look for more scripts once we found this one

        if options is None:
            raise AutolabError("Couldn't find the course roster on the page.")

        # Handle mapping username to uid
        self.user_id_map = {}
        # Capture username from the text within parentheses
        usrname_pat = re.compile(r"\(([^)]+)\)")

        for disp_name, uid in options.items():
            m = usrname_pat.search(disp_name)
            if not m:
                continue
            username = m.group(1).strip()
            self.user_id_map[username] = uid

        # Get the assignment ID
        assignment_id_element = soup.find("input", {"name": "submission[assessment_id]"})
        if not isinstance(assignment_id_element, Tag):
            raise AutolabError("Couldn't find the assessment_id input on the page.")
        self.assignment_id = str(assignment_id_element["value"])

        # Get the authenticity token
        authenticity_token_element = soup.find("input", {"name": "authenticity_token"})
        if not isinstance(authenticity_token_element, Tag):
            raise AutolabError("Couldn't find the authenticity_token input on the page.")
        self.authenticity_token = str(authenticity_token_element["value"])

        if not self.user_id_map:
            raise AutolabError("The course roster was found but no usernames could be parsed from it.")
        if not self.authenticity_token:
            raise AutolabError("The authenticity token on the page is empty.")
        self.is_loaded = True

    def __str__(self):
        return f"Assignment ID {self.assignment_id} ({self.url}) {self.user_id_map}"

    # Returns true if the username is valid for this course
    def check_username(self, username: str) -> bool:
        return username in self.user_id_map

    def make_submission(self, student_username: str, file_location: str, note=""):
        if not self.is_loaded:
            raise AutolabError("Assignment hasn't been loaded. You must call load_data() before making submissions!")

        # The roster is keyed by email address, so append the email ending (e.g. "@buffalo.edu") to the username
        if not student_username.endswith(secrets.EMAIL_ADDRESS_ENDING):
            student_username += secrets.EMAIL_ADDRESS_ENDING

        print(f"\nAttempting to make a submission for {student_username} using {file_location}")

        try:
            uid: str = self.user_id_map[student_username]
        except KeyError:
            print(f"Submission failed!\n{student_username} is not a valid username in this course.\n")
            new_username = input("Please enter a valid username for this submission: ")
            print("\n" + ("-" * 30))
            self.make_submission(new_username, file_location, note)
            return

        form_values: dict[str, str] = {
            "authenticity_token": self.authenticity_token,
            "commit": "Create Submission",
            "submission[assessment_id]": self.assignment_id,
            "submission[course_user_datum_id]": uid,
            "submission[file]": "submission.pdf",
            "submission[notes]": note,
            "submission[tweak_attributes][kind]": "points",
            "submission[tweak_attributes][value]": "",
            "utf8": "✓",
        }

        post_url: str = self.url[:-4]  # Remove the "/new" from the url because the POST location doesn't have it
        with open(file_location, "rb") as f:
            files: dict[str, BinaryIO] = {"submission[file]": f}
            response = requests.post(post_url, cookies=get_cookies(), files=files, data=form_values)
        if response.status_code != 200:
            raise AutolabError(f"{response.content!r}\n\nSubmission failed (HTTP {response.status_code}).")
        print("Submission successful!\n")
