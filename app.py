from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import Bug model
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(50), default="Open")  # Custom workflow
    regression_risk = db.Column(db.String(10), default="Low")
    sprint_flag = db.Column(db.Boolean, default=False)
    duplicate = db.Column(db.Boolean, default=False)
    escalated = db.Column(db.Boolean, default=False)
    repro_steps = db.Column(db.Text)
    browser_info = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sla_breach = db.Column(db.Boolean, default=False)
    patch_ready = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route('/')
def index():
    bugs = Bug.query.all()
    return render_template('index.html', bugs=bugs)


@app.route('/bug/<int:bug_id>')
def bug_detail(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    return render_template('bug_detail.html', bug=bug)


@app.route('/api/bugs', methods=['GET', 'POST'])
def bugs_api():
    if request.method == 'GET':
        bugs = Bug.query.all()
        return jsonify([bug.to_dict() for bug in bugs])

    if request.method == 'POST':
        data = request.get_json()
        new_bug = Bug(
            title=data.get('title'),
            description=data.get('description'),
            state=data.get('state', "Open"),
            regression_risk=data.get('regression_risk', "Low"),
            sprint_flag=data.get('sprint_flag', False),
            duplicate=data.get('duplicate', False),
            escalated=data.get('escalated', False),
            repro_steps=data.get('repro_steps', ""),
            browser_info=data.get('browser_info', ""),
            sla_breach=data.get('sla_breach', False),
            patch_ready=data.get('patch_ready', False)
        )
        db.session.add(new_bug)
        db.session.commit()
        return jsonify({"message": "Bug created", "bug": new_bug.to_dict()}), 201


@app.route('/api/bugs/<int:bug_id>', methods=['PUT', 'DELETE'])
def bug_modify(bug_id):
    bug = Bug.query.get_or_404(bug_id)

    if request.method == 'PUT':
        data = request.get_json()
        for field in data:
            setattr(bug, field, data[field])
        db.session.commit()
        return jsonify({"message": "Bug updated", "bug": bug.to_dict()})

    if request.method == 'DELETE':
        db.session.delete(bug)
        db.session.commit()
        return jsonify({"message": "Bug deleted"})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
