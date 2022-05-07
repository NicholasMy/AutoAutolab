# AutoAutolab
### Make bulk submissions to AUTOlab AUTOmatically!

Instructors can save **hours** of time by automatically uploading student submissions to the right place.

No more uploading hundreds of assignments individually by hand and waiting for the page to load each time! No more scrolling through a massive list of students only to choose the wrong one!

## It's easy to get started!

1. Load `secrets.py` with your Autolab session cookie and university email suffix.

2. Create an assignment with the Autolab submission URL (not the assignment URL). You can find this by navigating to an assignment, then `Admin Options` > `Manage Submissions` > `Create new submission`. Ensure it matches the format below.
```python
assignment = AutolabAssignment("https://autograder.cse.buffalo.edu/courses/DevUTestCourse/assessments/pdftest/submissions/new")
```

3. Automatically load assignment information directly from Autolab.
```python
assignment.load_data()
```

4. Make a submission for a student via only their username and a file path!
```python
assignment.make_submission("student2", "data/PDF B.pdf")
```

If any errors are detected, the program will halt and provide feedback to help you troubleshoot it.

## Examples
Examples are provided in `AutoAutolab.py`, but you'll need to adapt them to fit your usecase.
