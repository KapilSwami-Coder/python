import os
import sys

from flask import Flask,render_template,request,redirect,url_for,session,jsonify 
from datetime import datetime ,timezone
from forms import Login,Logout
# from data import studentAccounts,professorAccounts
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "howknown"


# Override with env if MySQL user/password differs, e.g.:
# set DATABASE_URL=mysql+pymysql://root:YOURPASSWORD@127.0.0.1:3306/webdata
_default_db = "mysql+pymysql://root:@127.0.0.1:3306/webdata"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", _default_db)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)
  
# data = {"2024bcy0068":{"password" : "kapil68","name" : "Kapil Swami"} ,
#         "2024bcy0069":{"password":"robin69", "name": "robin" },  
#         "2024bcy0067":{"password":"sabir67","name": "sabir"}  
#        }
class User(db.Model):
    
    user_id = db.Column(db.String(100),primary_key = True, nullable=False)
    # roll_no = db.Column(db.String(100),unique = True)
    password = db.Column(db.String(100),nullable = False)
    name = db.Column(db.String(100),unique=True,nullable = False)
    role = db.Column(db.String(100),nullable = False)
    institute_name = db.Column(db.String(200),nullable = False)

    student_profile = db.relationship(
        "Student", back_populates="user", uselist=False, foreign_keys="Student.user_id"
    )
    professor_subjects = db.relationship(
        "Professor",
        back_populates="user",
        foreign_keys="Professor.user_id",
    )
 
class Subadmin(db.Model):
    said = db.Column(db.String(100),primary_key=True,nullable = False)
    password = db.Column(db.String(100),nullable=False)
    institute_name = db.Column(db.String(100),unique = True,nullable=False)

    professor_subjects = db.relationship(
        "Professor", back_populates="subadmin", foreign_keys="Professor.said"
    )


class Student(db.Model):
    """One row per student profile (links to user)."""

    __tablename__ = "student"

    user_id = db.Column(
        db.String(100),
        db.ForeignKey("user.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    admission_year = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    branch = db.Column(db.String(50), nullable=False)

    user = db.relationship("User", back_populates="student_profile", foreign_keys=[user_id])


class Professor(db.Model):
    """One row per subject/batch; same professor (user_id) can have many rows under one subadmin (said)."""

    __tablename__ = "professor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    said = db.Column(
        db.String(100),
        db.ForeignKey("subadmin.said", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.String(100),
        db.ForeignKey("user.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    course = db.Column(db.String(100), nullable=False)
    batch_year = db.Column(db.Integer, nullable=False)
    batch_no = db.Column(db.Integer, nullable=False)

    subadmin = db.relationship("Subadmin", back_populates="professor_subjects", foreign_keys=[said])
    user = db.relationship("User", back_populates="professor_subjects", foreign_keys=[user_id])


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    instructions = db.Column(db.Text, nullable=True)
    course = db.Column(db.String(100), nullable=True)
    # Targeting (Kisko dikhana hai)
    institute_name = db.Column(db.String(100) )
    year = db.Column(db.Integer)       # from professor.batch_year
    batch = db.Column(db.Integer)      # from professor.batch_no (INT)
    # branch = db.column(db.String(20))
    # Relationships
    professor_id = db.Column(db.String(100), db.ForeignKey('user.user_id'))
    # Ek quiz ke andar bahut saare questions ho sakte hain
    questions = db.relationship('Question', backref='quiz', lazy=True)   
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow) 
    end_time = db.Column(db.DateTime )
    duration = db.Column(db.Integer)
    
class Question(db.Model):
    """Matches MySQL: q_type, q_text, correct_ans NOT NULL."""

    question_no = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(
        db.Integer, db.ForeignKey("exam.id"), primary_key=True, nullable=False
    )
    q_type = db.Column(db.String(100), nullable=False)
    q_text = db.Column(db.Text, nullable=False)
    opt_a = db.Column(db.String(200))
    opt_b = db.Column(db.String(200))
    opt_c = db.Column(db.String(200))
    opt_d = db.Column(db.String(200))
    mark = db.Column(db.Integer)
    correct_ans = db.Column(db.String(150), nullable=False)
    user_response = db.Column(db.String(255), nullable=True)
        
    
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(
            "\n[MySQL] Connection failed — app cannot reach the database.\n"
            "  • Start MySQL (Windows: Services → MySQL, or XAMPP/WAMP MySQL).\n"
            "  • Create DB: CREATE DATABASE webdata;\n"
            "  • If root has a password, set env DATABASE_URL, e.g.\n"
            '    DATABASE_URL=mysql+pymysql://root:mypass@127.0.0.1:3306/webdata\n'
            f"  • Driver error: {e}\n",
            file=sys.stderr,
        )
        raise
    
# studentAccount = studentAccounts
# professorAccount = professorAccounts
@app.route("/",methods = ["POST","GET"])
def index():
    form = Login()
    # if request.method == "POST":       
    if form.validate_on_submit():
        #    hased_password = generate_password_hash(form.password.data) 
           user = User.query.filter_by(user_id= form.rollno.data).first()
           subadmin = Subadmin.query.filter_by(said = form.rollno.data).first()
           
           
           if user:                
            #    rollno = request.form["email"]
            #    if user and check_password_hash(user.password, form.password.data):
                if user and  (user.password == form.password.data):
                 session["user_id"] = user.user_id
                 input_uid = form.rollno.data
                 return redirect(url_for("login",input_uid = input_uid))
               
               
           if subadmin:
                input_uid = form.rollno.data
                if subadmin and (subadmin.password == form.password.data):
                  session["user_id"] = subadmin.said
                  return render_template("login",input_uid=input_uid)
                 
           else:
               return "invaild cardentials"
       
    return render_template("index.html",form=form)        
def _student_can_see_exam(user, student_row, exam):
    if not student_row or not exam:
        return False
    if exam.institute_name != user.institute_name:
        return False
    if exam.year != student_row.admission_year:
        return False
    try:
        batch_no = int(str(student_row.batch).strip())
        return exam.batch == batch_no
    except (TypeError, ValueError):
        return True


def _student_visible_exams(user, student_row):
    """Exams for same institute; year = admission_year; batch matches if numeric."""
    if not student_row:
        return []
    q = Exam.query.filter(
        Exam.institute_name == user.institute_name,
        Exam.year == student_row.admission_year,
    )
    try:
        batch_no = int(str(student_row.batch).strip())
        q = q.filter(Exam.batch == batch_no)
    except (TypeError, ValueError):
        pass
    return q.order_by(Exam.id.desc()).all()


def _safe_int(v, default=1):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


@app.route("/user-<input_uid>")
def login(input_uid):
    if "user_id" not in session:
        return redirect(url_for("index"))
    if session.get("user_id") != input_uid:
        return redirect(url_for("index"))

    user = User.query.filter_by(user_id=input_uid).first()
    if not user:
        return "User not found", 404

    if (user.role or "").lower() == "student":
        sp = Student.query.filter_by(user_id=user.user_id).first()
        profile = None
        if sp:
            profile = {
                "admission_year": sp.admission_year,
                "batch": sp.batch,
                "branch": sp.branch,
            }
        return render_template(
            "student.html",
            name=user.name,
            uid=user.user_id,
            profile=profile,
        )
    if (user.role or "").lower() == "professor":
        courses = [
            {
                "id": row.id,
                "course": row.course,
                "batch_year": row.batch_year,
                "batch_no": row.batch_no,
            }
            for row in Professor.query.filter_by(user_id=user.user_id)
            .order_by(Professor.course, Professor.batch_year)
            .all()
        ]
        return render_template("professor.html", name=user.name, courses=courses)
    return "User not found", 404
    
@app.route("/logout", methods= ["POST"])
def logout():
    session.clear()
    #   if form.validate_on_submit(
    #       return  redirect(url_for("/"))
    #   return "request rejected"
    return redirect(url_for("index"))


@app.route("/exam")
def exam():
    """Student: list exams (fixes url_for('exam') on student dashboard)."""
    if "user_id" not in session:
        return redirect(url_for("index"))
    uid = session["user_id"]
    user = db.session.get(User, uid)
    if not user or (user.role or "").lower() != "student":
        return redirect(url_for("index"))
    sp = Student.query.filter_by(user_id=uid).first()
    exams = _student_visible_exams(user, sp)
    return render_template(
        "student_exam_list.html",
        name=user.name,
        uid=uid,
        exams=exams,
        has_profile=bool(sp),
    )


@app.route("/exam/<int:exam_id>")
def exam_detail(exam_id):
    if "user_id" not in session:
        return redirect(url_for("index"))
    uid = session["user_id"]
    user = db.session.get(User, uid)
    if not user or (user.role or "").lower() != "student":
        return redirect(url_for("index"))
    sp = Student.query.filter_by(user_id=uid).first()
    exam = db.session.get(Exam, exam_id)
    if not exam or not _student_can_see_exam(user, sp, exam):
        return "Exam not found or access denied", 404
    questions = (
        Question.query.filter_by(exam_id=exam_id)
        .order_by(Question.question_no)
        .all()
    )
    return render_template(
        "student_exam_take.html",
        name=user.name,
        uid=uid,
        exam=exam,
        questions=questions,
    )


# @app.route("/upload_exam", methods=["POST"])
# def upload_exam():
#     if "user_id" not in session :
#         return jsonify({"message": "unauthorized" })
#     user = User.query.get(session["user_id"])
#     exam = Exam.query.get(session["user_id"])
#     question = Question.query.get(session["user_id"])
#     data = request.json
#     exam.organaztion_name = user["organaztion_name"]
#     exam.professor_id =  user["user_id"]
#     question.q_text = data["question"]
    
#     # user.username = data["username"]
#     db.session.commit()
    
# @app.route("/exam")
# def exam():
#     return render_template("exam.html")

# @app.route("/save-quiz", methods=["POST"])
# def save_quiz():
#     # Hum form keys ko iterate karenge
#     # example: type_1, type_2, type_3...
#     for key in request.form:
#         if key.startswith('type_'):
#             q_num = key.split('_')[1]
#             q_type = request.form.get(f'type_{q_num}')
#             pass
#     # return redirect(url_for('login'))              
#     # return render_template("professor.html")
#     return redirect(url_for('login', input_uid=session['user_id']))
#             # Ab yahan db.session.add() karke save karein


@app.route("/upload_exam", methods=["POST"])
def upload_exam():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    current_professor = db.session.get(User, session["user_id"])
    if not current_professor or (current_professor.role or "").lower() != "professor":
        return jsonify({"status": "error", "message": "Only professors can upload exams"}), 403

    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("questions"), list):
        return jsonify({"status": "error", "message": "Invalid JSON body"}), 400

    teaching_id = data.get("teaching_id")
    if teaching_id is None or teaching_id == "":
        return jsonify({"status": "error", "message": "teaching_id missing — pick course again"}), 400
    try:
        teaching_id = int(teaching_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Select a valid course"}), 400

    row = Professor.query.filter_by(
        id=teaching_id, user_id=current_professor.user_id
    ).first()
    if not row:
        return jsonify({"status": "error", "message": "Course not found for this account"}), 400

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"status": "error", "message": "Exam title is required"}), 400

    instructions = (data.get("instructions") or "").strip() or None
    year_val = row.batch_year
    batch_val = int(row.batch_no)

    try:
        new_exam = Exam(
            title=title,
            instructions=instructions,
            course=row.course,
            institute_name=current_professor.institute_name,
            year=year_val,
            batch=batch_val,
            professor_id=current_professor.user_id,
            # naive UTC avoids MySQL "datetime" / tz mismatch errors on some setups
            end_time=datetime.utcnow(),
            duration=20,
        )
        db.session.add(new_exam)
        db.session.flush()

        for idx, q in enumerate(data["questions"]):
            q_type = (q.get("type") or "written").strip()[:100]
            q_text = (q.get("text") or "").strip() or " "
            raw_correct = q.get("correct")
            if raw_correct is None:
                correct_ans = ""
            else:
                correct_ans = str(raw_correct).strip()
            correct_ans = correct_ans[:150] if correct_ans else ""

            new_q = Question(
                exam_id=new_exam.id,
                q_text=q_text,
                q_type=q_type,
                correct_ans=correct_ans,
                mark=_safe_int(q.get("mark"), 1),
                question_no=int(float(q.get("question_no", idx + 1))),
            )
            if q_type == "mcq":
                new_q.opt_a = q.get("optionA") or None
                new_q.opt_b = q.get("optionB") or None
                new_q.opt_c = q.get("optionC") or None
                new_q.opt_d = q.get("optionD") or None
            db.session.add(new_q)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        msg = str(e)
        if "Unknown column" in msg or "doesn't exist" in msg.lower():
            msg += (
                " — `exam` / `question` columns ORM se match karo (e.g. exam: instructions, course, "
                "year, batch INT). `question`: q_type, q_text, correct_ans NOT NULL."
            )
        if "cannot be null" in msg.lower():
            msg += " — NOT NULL column: check exam/question schema vs app.py models."
        print("[upload_exam]", msg, file=sys.stderr)
        return jsonify({"status": "error", "message": msg}), 500

    return jsonify({"status": "success", "message": "Quiz Created"}), 200
    
if __name__ == "__main__":
    # host="0.0.0.0" → same Wi‑Fi/LAN par phone/PC se http://<YOUR_LOCAL_IP>:5000 kholo
    app.run(debug=True, host="0.0.0.0", port=5000)