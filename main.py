from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'hemmelig'

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
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    location = request.form.get('location')
    description = request.form.get('description')

    # Server-side validation of required fields
    if not title or not start_time or not end_time:
        flash('Title, start time, and end time are required!')
        return redirect(url_for('home'))

    # Validate time-format
    try:
        start_dt = datetime.strptime(start_time, '%H:%M')
        end_dt = datetime.strptime(end_time, '%H:%M')
    except ValueError:
        flash('Invalid time format!')
        return redirect(url_for('home'))

    # Time-input validation
    if start_time >= end_time:
        flash('End time must be after start time.')
        return redirect(url_for('home'))

    # Quest structure definition
    quest = {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "location": location,
        "description": description,
        "completed": False
    }

    weekly_planner[day].append(quest)
    flash('Quest added successfully!')
    return redirect(url_for('home'))


# Route to mark a quest as "completed"
@app.route('/complete_quest/<day>/<int:quest_index>', methods=['POST'])
def complete_quest(day, quest_index):
    if 0 <= quest_index < len(weekly_planner[day]):
        weekly_planner[day][quest_index]['completed'] = True
        flash('Quest marked as completed!')
    else:
        flash('Invalid quest index!')
    return redirect(url_for('home'))


@app.route('/quest/delete/<day>/<int:quest_index>', methods=['POST'])
def delete_quest(day, quest_index):
    try:
        if 0 <= quest_index < len(weekly_planner[day]):
            del weekly_planner[day][quest_index]
            flash('Quest was deleted successfully!')
        else:
            flash('Invalid quest index!')
    except Exception as e:
        flash(f'An error occurred: {e}')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
