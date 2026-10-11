from app import app
from models.user import User
from models.db import get_db
from models.student import StudentModel
from ml.predictor import predict_student_risk

USERS = [
    ('admin',   'System Administrator', 'admin@nexus.edu',          'Admin123!'),
    ('parent',  'Parent Two',           'parent2@nexus.edu',        'Parent123!'),
    ('teacher', 'Sana',                 'sana@nexus.edu',           'sana123456'),
    ('student', 'Saman Khan',           'samankhan2093@gmail.com',  'saman123456'),
]

STUDENT_EXTRA = {
    'samankhan2093@gmail.com': {
        'roll_no': 'CS-010',
        'department': 'Computer Science & AI',
        'semester': 4,
        'gpa': 3.20,
        'attendance_pct': 80.0,
    }
}

def register():
    with app.app_context():
        db = get_db()
        for role, name, email, password in USERS:
            existing = User.get_by_email(email)
            if existing:
                print(f'[SKIP] {email} already exists (role={existing.role})')
                continue

            user, err = User.create(name, email, password, role=role)
            if err:
                print(f'[FAIL] {email}: {err}')
                continue

            print(f'[OK]   {role:<8} {email}')

            if role == 'student' and email in STUDENT_EXTRA:
                extra = STUDENT_EXTRA[email]
                pred = predict_student_risk({
                    'gpa': extra['gpa'],
                    'attendance_pct': extra['attendance_pct'],
                    'semester': extra['semester'],
                    'department': extra['department'],
                })
                StudentModel.create(
                    user_id=user._id,
                    roll_no=extra['roll_no'],
                    department=extra['department'],
                    semester=extra['semester'],
                    gpa=extra['gpa'],
                    attendance_pct=extra['attendance_pct'],
                    risk_level=pred['risk_level'],
                    risk_score=pred['risk_score'],
                    last_prediction=pred
                )
                print(f'         Student profile created → risk={pred["risk_level"]}')

if __name__ == '__main__':
    register()
