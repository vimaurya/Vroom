from flask import request, jsonify, g
from dbconfig import app, db
from models import Task, User
from auth import signup, login
from auth import jwt_required


with app.app_context():
    db.create_all()
    
    
    
@app.route('/')
@jwt_required
def home():
    return jsonify({"context": g.user})



@app.route('/sign-up/', methods=['POST'])
def signup_user():
    json = request.get_json()
    
    username = json['username']
    password = str(json['password'])
    
    res, flag = signup(username, password)
    
    if not flag:
        return jsonify(res)
    
    return jsonify(res)


@app.route('/login/', methods=['POST'])
def login_user():
    json = request.get_json()
    username = json['username']
    password = str(json['password'])
    
    res, flag = login(username, password)
    
    if not flag:
        return jsonify({"jwt":res, "token_type":"bearer"})
    else:
        return jsonify({"Error":f"res"})
    

@app.route('/create-task/', methods=['POST'])
@jwt_required
def create_task():
    if request.method == 'POST':
        json = request.get_json()
        new_task = Task(
        task = json.get('task'),
        definition = json.get('definition'),
        deadline = json.get('deadline') if json.get('deadline') else None,
        is_completed = json.get('is_completed'),
        username = g.user['username']
        )
        
        try:
            db.session.add(new_task)
            db.session.commit()  
            return json, 201
        except Exception as e:
            return jsonify({"Error":f"{e}"}), 500
        
        
@app.route('/get-task/<int:task_id>/', methods=['GET'])
@jwt_required
def get_task(task_id):
    try:
        task = db.session.execute(db.select(Task).filter_by(id=task_id, username=g.user['username'])).scalar_one()
    
        return jsonify({
            "task" : task.task,
            "definition" : task.definition,
            "deadline" : task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
            "is_completed" : task.is_completed
        })
    
    except Exception as e:
        return jsonify({"Error":f"{e}"}), 404


@app.route('/all-tasks/',methods=['GET'])
@jwt_required
def all_tasks():
    try:
        tasks = Task.query.filter_by(username=g.user['username']).all()
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
@jwt_required
def update_task(task_id):
    try:
        username = g.username
        task = db.session.execute(db.select(Task).filter_by(id=task_id), username=username).scalar_one()
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
@jwt_required
def mark(task_id):
    try:
        username = g.user['username']
        task = db.session.execute(db.select(Task).filter_by(id=task_id), username=username).scalar_one_or_none()
        if task:
            task.is_completed = not task.is_completed
            db.session.commit()
            
            return jsonify([{
                "success" : f"task marked as {'completed' if task.is_completed else 'not completed'}",
                "id" : task.id,
                "task" : task.task,
                "definition" : task.definition,
                "deadline" : task.deadline,
                "is_completed" : task.is_completed,
                "username" : task.username
            }])
           
        else:
            return jsonify({"Error":"task does not exist"})
        
    except Exception as e:
        return jsonify({"Error":f"{e}"})


@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete(task_id):
    try:
        username = username
        task = db.session.execute(db.select(Task).filter_by(id=task_id), username=username).scalar_one()
        
        if not task:
            return jsonify({"Error":"task does not exist"})
        
        else:
            db.session.delete(task)
            db.session.commit()
            
            return jsonify({"success":"task deleted successfully"})
        
    except Exception as e:
        return jsonify({"Error":f"{e}"})



if __name__ == "__main__":
    app.run(debug=True)
