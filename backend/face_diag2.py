import sys, traceback

try:
    from ai_service import face_recognizer, emotion_predictor
    print("face ready:", face_recognizer.ready)
    print("emotion ready:", emotion_predictor.ready)
except Exception as e:
    print("IMPORT ERROR:", e)
    traceback.print_exc()

# Also test via app context
try:
    from app import app
    with app.app_context():
        from ai_service import face_recognizer as fr2
        print("face ready (app ctx):", fr2.ready)
except Exception as e:
    print("APP CTX ERROR:", e)
    traceback.print_exc()
