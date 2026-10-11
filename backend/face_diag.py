import sys
print("Python:", sys.version)

try:
    from mtcnn import MTCNN
    d = MTCNN()
    print("MTCNN: OK")
except Exception as e:
    print(f"MTCNN FAIL: {e}")

import os
BASE = os.path.join(os.path.dirname(__file__), 'face_attendance_models')
facenet = os.path.join(BASE, 'best_facenet_model.keras')
facenet_fixed = os.path.join(BASE, 'best_facenet_model_fixed.keras')
print(f"facenet exists: {os.path.exists(facenet)}")
print(f"facenet_fixed exists: {os.path.exists(facenet_fixed)}")

try:
    import tensorflow as tf
    import numpy as np
    if os.path.exists(facenet_fixed):
        model = tf.keras.models.load_model(facenet_fixed, compile=False)
        dummy = np.zeros((1, 160, 160, 3), dtype='float32')
        out = model.predict(dummy, verbose=0)
        print(f"FaceNet fixed model: OK, output shape={out.shape}")
    elif os.path.exists(facenet):
        from ai_service.face_recognition import _build_model_without_lambda
        model = _build_model_without_lambda()
        import numpy as np
        dummy = np.zeros((1, 160, 160, 3), dtype='float32')
        out = model.predict(dummy, verbose=0)
        print(f"FaceNet model built: OK, output shape={out.shape}")
    else:
        print("FaceNet model file MISSING")
except Exception as e:
    import traceback
    print(f"FaceNet FAIL: {e}")
    traceback.print_exc()
