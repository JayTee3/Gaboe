from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper import login_required, login_required_student

import pdfkit

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies) (from finance pset)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "thisistest"
Session(app)

# Configure CS50 Library to use SQLite database (from finance pset)
db = SQL("sqlite:///gradebook.db")

# db.execute("""CREATE TABLE scores ( score_id INTEGER NOT NULL, student_assignment_id INTEGER NOT NULL, teacher_id INTEGER NOT NULL,
#               student_id INTEGER NOT NULL, students_score INTEGER NOT NULL, PRIMARY KEY(score_id), FOREIGN KEY(teacher_id) REFERENCES teacher(id),
#               FOREIGN KEY(student_assignment_id) REFERENCES assignment (assignment_id), FOREIGN KEY(student_id) REFERENCES student(d))""")

   #continue from here with SQL to fix bug to include teacher_id
#   SELECT DISTINCT first_name, students_score, title, total_mark, date

#   FROM student
#   Inner JOIN scores ON scores.student_id = student.id
#   Inner JOIN assignment ON assignment.assignment_id =
#   scores.student_assignment_id GROUP BY score_id
#   HAVING student_assignment_id >0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register_student", methods=["GET", "POST"])
def register_student():
     # collect information from the forms
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        student_email = request.form.get("student_email").strip()
        parent = request.form.get("parent")
        parent_email = request.form.get("parent_email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password").strip()
        password_2 = request.form.get("confirm_password")

    # check form information to ensure the form was filled out

        if password != password_2:
            flash("Password did not match please try again.", "danger")
            return redirect("/register_student")


        # hash password
        hash_password = generate_password_hash(password)


        # commit the information to the database
        try:
            db.execute("""INSERT INTO student (first_name, last_name, email, parent, parent_email, phone_number, hash)
                    VALUES(?,?,?,?,?,?,?)""", first_name, last_name, student_email, parent, parent_email, phone_number, hash_password)
        except:
            error = "Email already in use"
            return render_template

        #redirectuser to login page
        flash("Account created successfully!", "sucess")
        return redirect("/sign_in")


    return render_template("register_student.html")

@app.route("/register_teacher" , methods= ["GET", "POST"])
def register_teacher():
     # collect information from the forms
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email").strip()
        subject = request.form.get("subject")
        password = request.form.get("password").strip()
        password_2 = request.form.get("confirm_password").strip()

    # check form information to ensure the form was filled out
        error = "Passwords did not match please try again"
        if password != password_2:
            flash("Passwords did not match please try again", "danger")
            return redirect("/register_teacher")


        # hash password
        hash_password = generate_password_hash(password)


        # commit the information to the database
        try:
            db.execute("""INSERT INTO teacher (first_name, last_name, email, subject,hash)
                    VALUES(?,?,?,?,?)""", first_name, last_name, email, subject, hash_password)
        except:
            error = "Email already in use"
            return render_template ("error.html",error=error)

        flash("Account created successfully", "success")
        return redirect("/sign_in/teacher")



    return render_template("register_teacher.html")

@app.route("/sign_in/teacher", methods=["GET", "POST"])
def sign_in_techer():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password = request.form.get("password").strip()
        email = request.form.get("email").strip()

        if not email:
            error = "must provide a email address"
            return render_template("error.html")

        # Ensure password was submitted
        elif not password:
            error = "must provide a password"
            return render_template("error.html")

        # Query database for email
        teachers = db.execute("SELECT * FROM teacher WHERE email= ?", email)


        # Ensure username exists and password is correct
        if len(teachers) != 1 or not check_password_hash(teachers[0]["hash"], password):
            return render_template("error.html", error="Password did not match")

        # Remember which user has logged in
        session["teacher_id"] = teachers[0]["id"]

        # Redirect user to home page
        return redirect("/profile")

    return render_template("teacher_signin.html")

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in_student():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password = request.form.get("password").strip()
        email = request.form.get("email")

        if not email:
            error = "must provide a email address"
            return render_template("error.html")

        # Ensure password was submitted
        elif not password:
            error = "must provide a password"
            return render_template("error.html")

        # Query database for email
        students = db.execute("SELECT * FROM student WHERE email= ?", email.strip())


        if len(students) != 1 or not check_password_hash(students[0]["hash"], password):
            return render_template("error.html", error="Password did not match")


        # Remember which user has logged in
        session["student_id"] = students[0]["id"]

        # Redirect user to home page
        return redirect("/home")


    return render_template("sign_in.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    current_user = session["teacher_id"]
    name = db.execute("SELECT first_name, subject FROM teacher WHERE id =? ", current_user)
    students = db.execute("SELECT first_name, last_name, std.id FROM student AS std INNER JOIN class AS cl ON cl.student_id = std.id WHERE cl.teacher_id = ? GROUP BY first_name ", current_user)
    details = db.execute("""SELECT DISTINCT std.first_name,std.last_name, scr.students_score, asign.title, asign.total_mark, asign.date, asign.teacher_id
                             FROM student AS std Inner JOIN scores AS scr ON scr.student_id = std.id Inner JOIN assignment AS asign
                             ON asign.assignment_id = scr.student_assignment_id WHERE asign.teacher_id = ? GROUP BY score_id
                             HAVING student_assignment_id > 0""", current_user)

    # scores = db.execute("SELECT student_score FROM scores WHERE teacher_id = ? GROUP BY id", current_user)
    assignment = db.execute("SELECT title, total_mark,assignment_id, category, date FROM assignment WHERE teacher_id = ? ORDER BY assignment_id DESC", current_user)





    return render_template("profile.html", name=name,details=details, students=students, assignments=assignment)

@app.route("/assignment/<int:assignment_id>")
@login_required
def assignment(assignment_id):

    current_user = session["teacher_id"]

    assignments  = db.execute("""SELECT DISTINCT std.first_name, std.last_name, scr.students_score, scr.student_assignment_id, scr.student_id, asign.assignment_id,
                           asign.title, asign.total_mark, asign.date
                           FROM   scores AS scr
                           INNER JOIN assignment AS asign
                           ON asign.assignment_id = scr.student_assignment_id
                           INNER JOIN student AS std
                           ON std.id = scr.student_id
                           WHERE asign.teacher_id = ? AND asign.assignment_id = ? GROUP BY score_id ORDER BY score_id,
                           student_id
                           DESC """, current_user, assignment_id)

    total = db.execute("""SELECT SUM(asign.total_mark), SUM(students_score) FROM scores
                                INNER JOIN assignment AS asign ON asign.assignment_id = scores.student_assignment_id
                                WHERE asign.teacher_id = ? AND asign.assignment_id = ? """, current_user, assignment_id)

    if total[0]["SUM(asign.total_mark)"] == None:
        flash("Student's assignment grade may need to be updated or entered in", "warning")
        return redirect("/profile")

    points = (total[0]["SUM(asign.total_mark)"])
    scores = (total[0]["SUM(students_score)"])

    avg = (scores/points) * 100/1



    return render_template ("assignment.html", assignments=assignments, avg=round(avg))


@app.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():

    current_user = session["teacher_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        title = request.form.get("title")
        total = request.form.get("total")
        category = request.form.get("category")
        date = request.form.get("date")

        #makes input uppercase to save in datebase
        category_list =["HOMEWORK", "QUIZ", "TEST", "CLASSWORK"]
        cat = category.upper().strip()

        if (cat not in category_list):
            flash("Category type not allowed", "danger")
            return redirect("/assessment")

        #adds data into the database
        db.execute("""INSERT INTO assignment (title, total_mark, category, date, teacher_id)
                    VALUES(?,?,?,?,?)""", title, total, cat , date, current_user    )

        flash("Assignment created successfully!", "success")
        return redirect("/post-grades")


    return render_template("assessment.html")

@app.route("/post-grades", methods=["GET", "POST"])
@login_required
def post_grades():

    current_user = session["teacher_id"]
    students = db.execute("SELECT first_name, last_name, std.id FROM student AS std INNER JOIN class AS cl ON cl.student_id = std.id WHERE cl.teacher_id = ? GROUP BY first_name ", current_user)
    assignment_detial = db.execute("SELECT title, total_mark, date FROM assignment WHERE teacher_id = ? ORDER BY assignment_id DESC", current_user)


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        score = request.form.get("score")
        student_id = request.form.get("student")


             #checks if the score inputted is greater than the assignment point total
        if request.form.get("student") == "Open this select menu":
            flash("Did not select student name!", "danger")
            return redirect("/post-grades")




        current_assignment = db.execute("SELECT assignment_id FROM assignment WHERE teacher_id = ? ORDER BY assignment_id DESC", current_user)
        total_point = db.execute("SELECT total_mark FROM assignment WHERE teacher_id = ? ORDER BY assignment_id DESC", current_user)
        #current_student_user = db.execute("SELECT id FROM student WHERE id =?", student_id)
        current_assignment_id = current_assignment[0]["assignment_id"]
        graded_student = db.execute("SELECT student_id FROM scores WHERE student_assignment_id=? AND teacher_id=?", current_assignment_id,current_user)


        #checks if the score inputted is greater than the assignment point total
        if int(score) > int(total_point[0]["total_mark"]):
            flash("Point total is greater than assignment point value", "warning")
            return redirect("/post-grades")

        if len(graded_student) > 0:
            flash("Student assignment grade as already been posted", "warning")
            return redirect("/post-grades")



        #add data to the database
        db.execute("""INSERT INTO scores (students_score, student_id, teacher_id, student_assignment_id)
                        VALUES(?,?,?,?)""", score,student_id,current_user, current_assignment_id)



        flash("assignment graded successfully!", "success")
        return redirect("/post-grades")



    return render_template("post-grades.html", students=students, detials=assignment_detial)




@app.route("/edit/<int:assignment_id>/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_grades(assignment_id, student_id):

    current_user = session["teacher_id"]
    #gets the records for the user/student in question
    students = db.execute("SELECT * FROM student WHERE id = ?", student_id)
    assignment_detial = db.execute("SELECT title, total_mark, date FROM assignment WHERE teacher_id = ? AND assignment_id = ? ", current_user, assignment_id)


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        score = request.form.get("score")
        student = request.form.get("student")

         #add data to the database
        db.execute("UPDATE scores SET students_score=?, student_id = ?, student_assignment_id = ?, teacher_id = ?"
                    , score, student_id, assignment_id, current_user)

        flash("Assignment UPDATED successfully", "success")
        return redirect("/profile")


    return render_template("edit.html", students=students, detials=assignment_detial)


@app.route("/edit/<int:assignment_id>", methods=["GET", "POST"])
@login_required
def edit_assignment(assignment_id):

    current_user = session["teacher_id"]
    #gets the records for the user/student in question
    students = db.execute("""SELECT first_name, last_name, std.id FROM student AS std
                           INNER JOIN class AS cl ON cl.student_id = std.id WHERE cl.teacher_id = ? GROUP BY first_name""", current_user)

    assignment_detial = db.execute("SELECT title, total_mark, date FROM assignment WHERE teacher_id = ? AND assignment_id = ? ", current_user, assignment_id)


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        score = request.form.get("score")
        student_id = request.form.get("student")

        student_grade = db.execute("SELECT students_score FROM scores WHERE student_assignment_id =? AND student_id=?", assignment_id, student_id)

        if student_grade == []:
            db.execute("INSERT INTO scores (students_score, student_id, student_assignment_id, teacher_id) VALUES(?,?,?,?)"
                        ,score, student_id, assignment_id, current_user)


         #add data to the database
        db.execute("UPDATE scores SET students_score = ? WHERE student_id = ? AND student_assignment_id = ? AND teacher_id = ?"
                    , score, student_id, assignment_id, current_user)

        flash("Assignment UPDATED successfully", "success")
        return redirect("/profile")


    return render_template("edit_assignment.html", students=students, detials=assignment_detial)




@app.route("/student_profile/<int:student_id>", methods=["GET", "POST"])
@login_required
def student_profile(student_id):

    current_user = session["teacher_id"]
    student = db.execute("SELECT * FROM student WHERE id = ?", student_id)

    if request.method == "POST":
        student_avg = request.form.get("score_avg")
        teacher_check = db.execute("SELECT teacher_id FROM records")

        for i in range(len(teacher_check)):
            if teacher_check[i]["teacher_id"] == current_user:
                flash("Student Term grade has already been saved", "warning")
                return redirect("/profile")

        db.execute("INSERT INTO records (student_id, teacher_id, term_avg ) VALUES(?,?,?)", student_id,current_user,student_avg)
        flash("Student term grade saved successfully", "success")


    #select the data from the database for the user/student in question in order to create an average
    #average is base on th sum and not base on the categories
    total = db.execute("""SELECT SUM(asign.total_mark), SUM(students_score), subject, first_name, last_name FROM scores
                           INNER JOIN assignment AS asign ON asign.assignment_id = scores.student_assignment_id
                           INNER JOIN teacher AS tech ON tech.id = asign.teacher_id
                           WHERE asign.teacher_id = ? AND student_id = ?""", current_user, student_id)

    weights = db.execute("""SELECT category, SUM(total_mark), SUM(students_score) FROM "assignment"
                            INNER JOIN scores AS scr ON scr.student_assignment_id =
                            assignment.assignment_id INNER JOIN student AS std ON std.id = scr.student_id
                            WHERE scr.teacher_id = ? AND std.id = ? GROUP BY category  """, current_user, student_id)


    if total[0]["first_name"] == None:
        return render_template("student_profile.html", student=student, message="Waiting for assignments to be graded")

    avg_list =[]
    weight_list =[]
    hw_weight = 0.10
    cw_weight = 0.20
    qz_weight = 0.30
    ts_weight = 0.40
    for i in range(len(weights)):

        if weights[i]["category"].strip() == "HOMEWORK":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            homework_grade  = round(check)
            homework_weight = homework_grade * hw_weight
            weight_list.append(hw_weight)
            homework = round(homework_weight)
            avg_list.append(homework)

        if weights[i]["category"].strip() == "QUIZ":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            quiz_weight = student_grade * qz_weight
            weight_list.append(qz_weight)
            quiz = round(quiz_weight)
            avg_list.append(quiz)

        if weights[i]["category"].strip() == "CLASSWORK":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            classwork_weight = student_grade * cw_weight
            weight_list.append(cw_weight)
            classwork = round(classwork_weight)
            avg_list.append(classwork)

        if weights[i]["category"].strip() == "TEST":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            test_weight = student_grade * ts_weight
            weight_list.append(ts_weight)
            test = round(test_weight)
            avg_list.append(test)



    #creates average to send to user
    running_avg = sum(avg_list)/sum(weight_list)

    if ((round(running_avg) >= 91) and (round(running_avg) <=100)):
        letter_grade = "A"

    elif ((round(running_avg) >= 73) and (round(running_avg) <=91)):
        letter_grade = "B"

    elif ((round(running_avg) >= 65) and (round(running_avg) <=72)):
        letter_grade = "C"

    elif ((round(running_avg) >=50 ) and (round(running_avg) <=64)):
        letter_grade = "D"

    elif ((round(running_avg) >= 0) and (round(running_avg) <=49)):
        letter_grade = "F"



    return render_template("student_profile.html", student=student, total=total, avg=round(running_avg), letter_grade=letter_grade)

@app.route("/home", methods=["GET","POST"])
@login_required_student
def student_home():

    current_user = session["student_id"]
    student = db.execute("SELECT * FROM student WHERE id=?", current_user)

    #Grabs records for student/ user in question to display in profile area
    #Update  to inculde profile pictures
    classes = db.execute("""SELECT class_name, class_code, teacher_id, first_name, last_name, class.id FROM class
                            INNER JOIN teacher ON teacher.id = class.teacher_id WHERE student_id = ?""", current_user)

    if classes == []:
        return render_template("student_home.html", student=student, message="Waiting to be placed in class")


    return render_template("student_home.html", student=student, classes=classes)



@app.route("/class_records/<int:class_id>/<int:teacher_id>")
@login_required_student
def class_records(class_id, teacher_id):

    current_user = session["student_id"]

    #Grabs records for student/ user in question to display in profile area
    #Update  to inculde profile pictures
    records = db.execute("""SELECT category, title, total_mark, students_score, subject, tech.first_name, tech.last_name FROM scores
                            INNER JOIN assignment AS asign ON asign.assignment_id =
                            scores.student_assignment_id
                            INNER JOIN teacher as tech ON tech.id = asign.teacher_id
                            INNER JOIN student AS std ON std.id = scores.student_id
                            INNER JOIN class ON class.teacher_id = tech.id
                            WHERE scores.student_id = ? AND class.id = ? GROUP BY category """, current_user, class_id)

    weights = db.execute("""SELECT category, SUM(total_mark), SUM(students_score) FROM "assignment"
                            INNER JOIN scores AS scr ON scr.student_assignment_id = assignment.assignment_id
                            INNER JOIN student AS std ON std.id = scr.student_id
                            INNER JOIN class ON class.student_id = scr.student_id
                            WHERE std.id = ? AND class.id = ? AND scr.teacher_id =? GROUP BY category """, current_user, class_id, teacher_id)

    if weights == []:
        flash("Waiting for assignments to be posted", "warning")
        return redirect("/home")

    avg_list =[]
    weight_list =[]
    hw_weight = 0.10
    cw_weight = 0.20
    qz_weight = 0.30
    ts_weight = 0.40
    for i in range(len(weights)):

        if weights[i]["category"].strip() == "HOMEWORK":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            homework_grade  = round(check)
            homework_weight = homework_grade * hw_weight
            weight_list.append(hw_weight)
            homework = round(homework_weight)
            avg_list.append(homework)

        if weights[i]["category"].strip() == "QUIZ":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            quiz_weight = student_grade * qz_weight
            weight_list.append(qz_weight)
            quiz = round(quiz_weight)
            avg_list.append(quiz)

        if weights[i]["category"].strip() == "CLASSWORK":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            classwork_weight = student_grade * cw_weight
            weight_list.append(cw_weight)
            classwork = round(classwork_weight)
            avg_list.append(classwork)

        if weights[i]["category"].strip() == "TEST":
            check = (weights[i]["SUM(students_score)"]/weights[i]["SUM(total_mark)"]) * 100/1
            student_grade  = round(check)
            test_weight = student_grade * ts_weight
            weight_list.append(ts_weight)
            test = round(test_weight)
            avg_list.append(test)



    #creates average to send to user
    running_avg = sum(avg_list)/sum(weight_list)

    if ((round(running_avg) >= 91) and (round(running_avg) <=100)):
        letter_grade = "A"

    elif ((round(running_avg) >= 73) and (round(running_avg) <=91)):
        letter_grade = "B"

    elif ((round(running_avg) >= 65) and (round(running_avg) <=72)):
        letter_grade = "C"

    elif ((round(running_avg) >=50 ) and (round(running_avg) <=64)):
        letter_grade = "D"

    elif ((round(running_avg) >= 0) and (round(running_avg) <=49)):
        letter_grade = "F"



    return render_template("student_records.html", records=records, avg=round(running_avg), letter_grade=letter_grade)





@app.route("/delete/<int:assignment_id>", methods=["GET", "POST"])
@login_required
def delete(assignment_id):

    if request.method == "POST":
        remove_record = request.form.get("student_record")

        delete_score = db.execute("DELETE FROM scores WHERE student_id=? AND student_assignment_id=?", remove_record, assignment_id)
        #delete_assignment = db.execute("DELETE FROM assignment WHERE assignment_id=?", assignment_id)

        return redirect("/profile  ")

     # delete the assignment score first and then the assignment
     # datebase will send an error if all instances of the data is not deleted
    delete_score = db.execute("DELETE FROM scores WHERE student_assignment_id=?", assignment_id)
    delete_assignment = db.execute("DELETE FROM assignment WHERE assignment_id=?", assignment_id)

     # returns user to profile page
    flash("Assignment DELETED successfully", "success")
    return redirect ("/profile")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    current_user = session["teacher_id"]
    teacher = db.execute("SELECT * FROM teacher WHERE id =?", current_user)
    student = db.execute("SELECT * FROM student")

    if request.method == "POST":
        class_code = request.form.get("class_code")
        class_name = request.form.get("class_name")
        email = request.form.get("email")


        student_id = db.execute("SELECT id FROM student WHERE email=? ", email.strip())
        current_id = db.execute("""SELECT std.id from student AS std INNER JOIN class ON class.student_id = std.id
                                    WHERE std.email = ? AND teacher_id =?""", email.strip(), current_user)

        if not student_id:
            flash("Student account not found, please check the email address.", "warning")
            return redirect("/account")

        if student_id == current_id:
            flash("Student account has already been added.", "warning")
            return redirect("/account")


        db.execute("INSERT INTO class (student_id, class_name, class_code, teacher_id) VALUES(?,?,?,?)",
                    student_id[0]["id"], class_name, class_code, current_user)

        flash("Student has been added successfully to class", "success")
        return redirect("/profile")



    return render_template("account.html", teacher=teacher, students=student)



@app.route("/report/<int:student_id>/")
def report(student_id):

    def gpa_calculator(grades):
        points = 0
        i = 0
        grade_scale = { "A":4, "B":3, "C":2, "D":1, "F":0}
        if grades != []:
            for grade in grades:
                points += grade_scale[grade]
            gpa = points/len(grades)
            return gpa
        else:
            return None

    current_user = session["teacher_id"]
    student = db.execute("SELECT * FROM student WHERE id =?", student_id)

    results = db.execute("""SELECT class_name, final_avg, letter_grade, exam_grade, teacher_comment, term_avg, first_name, last_name
                            FROM "class" INNER JOIN records ON records.teacher_id = class.teacher_id
                            INNER JOIN teacher ON teacher.id = class.teacher_id
                            WHERE class.student_id = ?""", student_id)

    letter_grades= db.execute("SELECT letter_grade FROM records WHERE student_id=?", student_id)

    grades = letter_grades[0]["letter_grade"]

    gpa = gpa_calculator(grades)



    return render_template("report.html", student=student, results=results, gpa=gpa)


@app.route("/exam", methods=["GET", "POST"])
@login_required
def exam():

    current_user = session["teacher_id"]
    students = db.execute("""SELECT first_name, last_name, std.id FROM student AS std
                           INNER JOIN class AS cl ON cl.student_id = std.id WHERE cl.teacher_id = ? GROUP BY first_name""", current_user)

    if request.method == "POST":
        student = request.form.get("student")
        comment = request.form.get("comment")
        exam_grade = request.form.get("exam_score")

        #error checking
        if  student == "Open this select menu":
            flash("Did not enter a student name", "danger")
            return redirect("/exam")

        if  comment == "":
            flash("Did not enter a student comment", "danger")
            return redirect("/exam")

        term_grade = db.execute("SELECT term_avg FROM records WHERE student_id=? AND teacher_id=?", student,current_user)
        grade = term_grade[0]["term_avg"]

        final_grade = (grade*0.6) + (round(int(exam_grade))*.40)


        if ((round(final_grade) >= 91) and (round(final_grade) <=100)):
            letter_grade = "A"

        elif ((round(final_grade) >= 73) and (round(final_grade) <=91)):
            letter_grade = "B"

        elif ((round(final_grade) >= 65) and (round(final_grade) <=72)):
            letter_grade = "C"

        elif ((round(final_grade) >=50 ) and (round(final_grade) <=64)):
            letter_grade = "D"

        elif ((round(final_grade) >= 0) and (round(final_grade) <=49)):
            letter_grade = "F"

        check = db.execute("SELECT exam_grade FROM records WHERE teacher_id =? ", current_user)
        data_check = check[0]["exam_grade"]

        if data_check != None:
            flash("Student exam record has already been submitted", "warning")
            return redirect("/exam")


        db.execute("""UPDATE records SET teacher_comment=?, exam_grade=?, final_avg=?, letter_grade=?
                      WHERE student_id =? AND teacher_id =?""",comment, exam_grade, round(final_grade), letter_grade, student, current_user)
        flash("Student exam grade saved successfully", "success")


    return render_template("exam.html", students=students)


@app.route("/error")
def error():
    return render_template("error.html")



@app.route("/sign_out")
def sign_out():

      # Forget any user_id
    session.clear()

    return redirect ("/")