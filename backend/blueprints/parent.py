from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from decorators import role_required
from models.assignment import AssignmentModel
from models.attendance import AttendanceModel
from models.db import get_db
from models.prediction import PredictionModel
from models.marks import MarksModel
from models.alert import AlertModel
from models.report import ReportModel

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')


@parent_bp.route('/dashboard')
@login_required
@role_required('parent')
def dashboard():
    db = get_db()
    children = list(db.students.find({'parent_ids': current_user._id}).sort('name', 1))
    result = []
    for child in children:
        user = db.users.find_one({'_id': child.get('user_id')})
        child_name = user.get('name', 'Student') if user else 'Student'
        assignments = AssignmentModel.get_by_student(child['_id'])[:6]
        attendance_records = AttendanceModel.get_records(child['_id'], limit=10)
        latest_prediction = PredictionModel.get_latest_by_student(child['_id'])
        marks_analytics = MarksModel.get_analytics(child['_id'])
        alerts = AlertModel.get_by_student(child['_id'], limit=5)
        subjects = AttendanceModel.get_subjects(child['_id'])
        subjects_data = [{
            'subject': s.get('subject', ''),
            'total_classes': s.get('total_classes', 0),
            'attended': s.get('attended', 0),
            'percentage': round((s.get('attended', 0) / s.get('total_classes', 1)) * 100, 1)
                          if s.get('total_classes', 0) > 0 else 0.0
        } for s in subjects]
        result.append({
            '_id': str(child['_id']),
            'name': child_name,
            'roll_no': child.get('roll_no', ''),
            'department': child.get('department', ''),
            'semester': child.get('semester', 1),
            'gpa': round(float(child.get('gpa', 0)), 2),
            'attendance_pct': round(float(child.get('attendance_pct', 0)), 2),
            'risk_level': child.get('risk_level', 'LOW'),
            'subjects': subjects_data,
            'assignments': [{
                '_id': str(a['_id']), 'title': a.get('title', ''),
                'subject': a.get('subject', ''), 'due_date': str(a.get('due_date', ''))[:10],
                'status': a.get('status', 'pending')
            } for a in assignments],
            'attendance_records': [{
                'subject': r.get('subject', ''), 'status': r.get('status', ''),
                'date': str(r.get('date', r.get('created_at', '')))[:10]
            } for r in attendance_records],
            'latest_prediction': {
                'risk_level': latest_prediction.get('risk_level', ''),
                'risk_score': latest_prediction.get('risk_score', 0),
                'confidence': latest_prediction.get('confidence', 0),
                'recommendations': latest_prediction.get('recommendations', []),
            } if latest_prediction else None,
            'marks_analytics': marks_analytics,
            'alerts': alerts,
        })
    return jsonify({'success': True, 'children': result})


@parent_bp.route('/api/child/<student_id>/report')
@login_required
@role_required('parent')
def child_report(student_id):
    """Parent can view their child's full report."""
    db = get_db()
    from bson.objectid import ObjectId
    try:
        sid = ObjectId(student_id)
    except Exception:
        return jsonify({'error': 'Invalid student ID'}), 400

    # Verify this child belongs to this parent
    child = db.students.find_one({'_id': sid, 'parent_ids': current_user._id})
    if not child:
        return jsonify({'error': 'Access denied'}), 403

    report = ReportModel.get_student_report(sid)
    return jsonify({'report': report})


@parent_bp.route('/api/alerts')
@login_required
@role_required('parent')
def parent_alerts():
    """Get all alerts for children linked to this parent."""
    alerts = AlertModel.get_parent_alerts(current_user._id)
    return jsonify({'alerts': alerts})


@parent_bp.route('/api/child/<student_id>/marks')
@login_required
@role_required('parent')
def child_marks(student_id):
    db = get_db()
    from bson.objectid import ObjectId
    try:
        sid = ObjectId(student_id)
    except Exception:
        return jsonify({'error': 'Invalid student ID'}), 400

    child = db.students.find_one({'_id': sid, 'parent_ids': current_user._id})
    if not child:
        return jsonify({'error': 'Access denied'}), 403

    marks = MarksModel.get_by_student(sid)
    analytics = MarksModel.get_analytics(sid)
    return jsonify({
        'marks': [{
            **m,
            '_id': str(m['_id']),
            'student_id': str(m['student_id']),
            'teacher_id': str(m.get('teacher_id') or ''),
            'created_at': m['created_at'].strftime('%Y-%m-%d') if m.get('created_at') else ''
        } for m in marks],
        'analytics': analytics
    })
