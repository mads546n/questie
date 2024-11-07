from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# (very) early data structure for Questie's weekly planner.
# Dictionary format: {'day': [list_of_quests]}

weekly_planner = {
    "Monday": [],
    "Tuesday": [],
    "Wednesday": [],
    "Thursday": [],
    "Friday": [],
    "Saturday": [],
    "Sunday": []
}


# Home page displaying a single weekly planner
@app.route("/")
def home():
    return render_template('index.html', planner=weekly_planner)


# Route to add a new quest
@app.route('/add_quest/<day>', methods=['POST'])
def add_quest(day):
    title = request.form.get('title')
    time = request.form.get('time')
    location = request.form.get('location')
    description = request.form.get('description')

    # Quest structure definition
    quest = {
        "title": title,
        "time": time,
        "location": location,
        "description": description,
        "completed": False
    }

    weekly_planner[day].append(quest)
    return redirect(url_for('home'))


# Route to mark a quest as "completed"
@app.route('/complete_quest/<day>/<int:quest_index>', methods=['POST'])
def complete_quest(day, quest_index):
    if 0 <= quest_index < len(weekly_planner[day]):
        weekly_planner[day][quest_index]['completed'] = True
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

