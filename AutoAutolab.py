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

    course =    input("Please enter the course you are working with (ex. CSE116-s23): ")
    submit_to = input("Please enter the (unique) assignment name (ex. classes2)     : ")
    assignment = AutolabAssignment(f"https://autograder.cse.buffalo.edu/courses/{course}/assessments/{submit_to}/submissions/new")
    assignment.load_data()

    directory = "data"

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            continue  # Ignore directories if you want to do some additional organization
        username = filename.split(" ")[0].split(".")[0].lower()
        assignment.make_submission(username, file_path)
        print("-" * 30)

    print("\nDone!")


if __name__ == '__main__':
    main()
