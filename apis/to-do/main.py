from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.json.sort_keys = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vikash@localhost/todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(500), nullable=True)
    deadline = db.Column(db.DateTime, nullable = True)
    is_completed = db.Column(db.Boolean, nullable = False, default = False)


with app.app_context():
    db.create_all()
    
    
    
@app.route('/')
def home():
    return jsonify({"Hello person!" : "Are you ready to make a to-do"})


@app.route('/create-task/', methods=['POST'])
def create_task():
    if request.method == 'POST':
        json = request.get_json()
        new_task = Task(
        task = json.get('task'),
        definition = json.get('definition'),
        deadline = json.get('deadline') if json.get('deadline') else None,
        is_completed = json.get('is_completed')
        )
        
        try:
            db.session.add(new_task)
            db.session.commit()  
            return json, 201
        except Exception as e:
            return jsonify({"Error":f"{e}"}), 500
        
        
@app.route('/get-task/<int:task_id>/', methods=['GET'])
def get_task(task_id):
    try:
        task = db.session.execute(db.select(Task).filter_by(id=task_id)).scalar_one()
    
        return jsonify({
            "task" : task.task,
            "definition" : task.definition,
            "deadline" : task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
            "is_completed" : task.is_completed
        })
    
    except Exception as e:
        return jsonify({"Error":f"{e}"}), 404


@app.route('/all-tasks/',methods=['GET'])
def all_tasks():
    try:
        tasks = db.session.execute(db.select(Task).order_by(Task.is_completed.asc(), Task.deadline.asc())).scalars()
        tasks_list = []
        
        for task in tasks:
            new_task = {
                "id" : task.id,
                "task" : task.task,
                "definition" : task.definition,
                "deadline" : task.deadline,
                "is_completed" : task.is_completed
            }
            tasks_list.append(new_task)
        
        return jsonify(tasks_list)
    
    except Exception as e:
        return jsonify({"Error":f"{e}"})
    

@app.route('/update-task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = db.session.execute(db.select(Task).filter_by(id=task_id)).scalar_one()
        if task: 
            json = request.get_json()
    
            if "task" in json:
                task.task = json["task"]  
            if "definition" in json:
                task.definition = json["definition"]
            if "deadline" in json:
                task.deadline = json["deadline"]
            if "is_completed" in json:
                task.is_completed = json["is_completed"]
                
            try:
                db.session.commit()
                task = db.session.get(Task, task_id)
                return jsonify({
                            "task" : task.task,
                            "definition" : task.definition,
                            "deadline" : task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
                            "is_completed" : task.is_completed
                        })
            except Exception as e:
                return jsonify({"Error":f"{e}"})
        else:
            return jsonify({"Error" : "task_id does not exist"})
    
    except Exception as e:
        return jsonify({"Error":f"{e}"})
    
    
@app.route('/mark/<int:task_id>', methods=['PUT'])
def mark(task_id):
    try:
        task = db.session.execute(db.select(Task).filter_by(id=task_id)).scalar_one()
        if task:
            task.is_completed = not task.is_completed
            db.session.commit()
            
            return jsonify([{
                "success" : f"task marked as {'completed' if task.is_completed else 'not completed'}",
                "id" : task.id,
                "task" : task.task,
                "definition" : task.definition,
                "deadline" : task.deadline,
                "is_completed" : task.is_completed
            }])
           
        else:
            return jsonify({"Error":"task does not exist"})
        
    except Exception as e:
        return jsonify({"Error":f"{e}"})


@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete(task_id):
    try:
        task = db.session.execute(db.select(Task).filter_by(id=task_id)).scalar_one()
        
        if not task:
            return jsonify({"Error":"task does not exist"})
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({"success":"task deleted successfully"})
    
    except Exception as e:
        return jsonify({"Error":f"{e}"})



if __name__ == "__main__":
    app.run(debug=True)
