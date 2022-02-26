import os

from AutolabAssignment import AutolabAssignment


def main():
    # Sample usage for individual uploads
    # assignment = AutolabAssignment("https://autograder.cse.buffalo.edu/courses/DevUTestCourse/assessments/pdftest/submissions/new")
    # assignment.load_data()
    # print(assignment)
    # assignment.make_submission("student1", "data/PDF A.pdf")
    # assignment.make_submission("student2", "data/PDF B.pdf")
    # assignment.make_submission("student3", "data/PDF C.pdf", "here's a note")

    # Sample usage for bulk uploads from the "data" directory where the file name starts with the student's username followed by a space

    assignment = AutolabAssignment("https://autograder.cse.buffalo.edu/courses/DevUTestCourse/assessments/pdftest/submissions/new")
    assignment.load_data()

    directory = "data"

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        username = filename.split(" ")[0].split(".")[0].lower()
        print(f"{filename} belongs to {username}")
        assignment.make_submission(username, file_path)
        print("-" * 30)

    print("Done!")


if __name__ == '__main__':
    main()
