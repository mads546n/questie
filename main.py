import os
from datetime import datetime
import json

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder='templates')
print("Flask is looking for templates in:", app.template_folder)
app.secret_key = 'hemmelig'


def load_data():
    global weekly_planner
    try:
        if os.path.exists("data.json"):
            with open("data.json", 'r') as file:
                weekly_planner = json.load(file)
        else:
            reset_planner()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        reset_planner()

    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        reset_planner()


def save_data():
    global weekly_planner
    try:
        with open('data.json', 'w') as file:
            json.dump(weekly_planner, file, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")


def reset_planner():
    global weekly_planner
    weekly_planner = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": [],
        "metadata": {"completed_quests_count": 0}
    }

load_data()

# (very) early data structure for Questie's weekly planner.
# Dictionary format: {'day': [list_of_quests]}


# Home page displaying a single weekly planner
@app.route("/")
def home():
    return render_template('index.html', planner=weekly_planner)


# Route to add a new quest
@app.route('/add_quest/<day>', methods=['POST'])
def add_quest(day):
    try:
        if day not in weekly_planner or day == "metadata":
            flash("Invalid day specified!")
            return redirect(url_for('home'))

        title = request.form.get('title', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()

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

        save_data()

        flash('Quest added successfully!')
        return redirect(url_for('home'))

    except Exception as e:
        flash(f"An error occured: {e}")
        return redirect(url_for('home'))


# Route to mark a quest as "completed"
@app.route('/complete_quest/<day>/<int:quest_index>', methods=['POST'])
def complete_quest(day, quest_index):
    try:
        if 0 <= quest_index < len(weekly_planner[day]):
            weekly_planner[day][quest_index]['completed'] = True
            weekly_planner["metadata"]["completed_quests_count"] += 1
            save_data()
            flash('Quest marked as completed!')
        else:
            flash('Invalid quest index!')
    except Exception as e:
        flash(f"An error occurred: {e}")
    return redirect(url_for('home'))


@app.route('/quest/delete/<day>/<int:quest_index>', methods=['POST'])
def delete_quest(day, quest_index):
    try:
        if 0 <= quest_index < len(weekly_planner[day]):
            del weekly_planner[day][quest_index]
            flash('Quest was deleted successfully!')
            save_data()
        else:
            flash('Invalid quest index!')
    except Exception as e:
        flash(f'An error occurred: {e}')
    return redirect(url_for('home'))


@app.route('/reset', methods=['POST'])
def reset():
    reset_planner()
    save_data()
    flash("Reset was successful!")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
