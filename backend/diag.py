from app import app

with app.app_context():
    from models.db import get_db
    db = get_db()

    # DB
    print(f"[DB] students: {db.students.count_documents({})}, users: {db.users.count_documents({})}")

    # ML
    try:
        from ml.predictor import get_model_info
        info = get_model_info()
        print(f"[ML] ready=True  version={info['version']}  accuracy={info['accuracy']}")
    except Exception as e:
        print(f"[ML] FAIL: {e}")

    # Face recognition
    try:
        from ai_service import face_recognizer
        print(f"[FACE_RECOG] ready={face_recognizer.ready}")
    except Exception as e:
        print(f"[FACE_RECOG] FAIL: {e}")

    # Emotion model
    try:
        from ai_service import emotion_predictor
        print(f"[EMOTION] ready={emotion_predictor.ready}")
    except Exception as e:
        print(f"[EMOTION] FAIL: {e}")

    # Parent children
    from models.user import User
    parent = User.get_by_email('parent2@nexus.edu')
    children = list(db.students.find({'parent_ids': parent._id})) if parent else []
    print(f"[PARENT] parent2 linked children: {len(children)}")

    # Teacher students
    teacher = User.get_by_email('sana@nexus.edu')
    assigned = db.students.count_documents({'teacher_ids': teacher._id}) if teacher else 0
    print(f"[TEACHER] sana assigned students: {assigned}")

    # Student profile
    student_user = User.get_by_email('samankhan2093@gmail.com')
    if student_user:
        s = db.students.find_one({'user_id': student_user._id})
        print(f"[STUDENT] saman profile: {'found' if s else 'MISSING'}")
    else:
        print("[STUDENT] saman user MISSING")
