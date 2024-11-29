import io
import os
from datetime import datetime
import json
import logging
import matplotlib.pyplot as plt
import base64

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder='templates')
print("Flask is looking for templates in:", app.template_folder)
app.secret_key = 'hemmelig'

weekly_planner = {}

# Logging-configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data():
    global weekly_planner
    try:
        if os.path.exists("data.json"):
            with open("data.json", 'r') as file:
                content = file.read()
                if content.strip() == '':
                    raise json.JSONDecodeError("Empty file", '', 0)
                weekly_planner = json.loads(content)
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


def calculate_performance():
    total_quests = 0
    completed_quests = 0
    quests_per_day = {}

    # Iterate over all days in the weekly-planner
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        quests = weekly_planner.get(day, [])
        quests_per_day[day] = {'total': len(quests), 'completed': 0}
        total_quests += len(quests)
        for quest in quests:
            if quest.get('completed'):
                completed_quests += 1
                quests_per_day[day]['completed'] += 1

    # Calculate average of quests per week
    average_completed_per_day = completed_quests / 7
    performance_data = {
        'total_quests': total_quests,
        'completed_quests': completed_quests,
        'average_completed_per_day': average_completed_per_day,
        'quests_per_day': quests_per_day,
    }
    return performance_data


# Helper function to generate graphs and encode them
def generate_graphs(performance_data):
    graph_urls = {}

    # Generated bar-charts of quests_per_day
    days = list((performance_data['quests_per_day'].keys()))
    total_quests = [performance_data['quests_per_day'][day]['total'] for day in days]
    completed_quests = [performance_data['quests_per_day'][day]['completed'] for day in days]

    # Bar-chart for total quests completed
    fig1, ax1 = plt.subplots()
    ax1.bar(days, total_quests, color='skyblue')
    ax1.set_title('Total quests per day')
    ax1.set_ylabel('Number of quests')
    fig1.tight_layout()
    img1 = io.BytesIO()
    fig1.savefig(img1, format='png')
    img1.seek(0)
    graph_urls['total_quests'] = base64.b64encode(img1.getvalue()).decode()

    plt.close(fig1)

    # Bar-chart of completed quests
    fig2, ax2 = plt.subplots()
    ax2.bar(days, completed_quests, color='green')
    ax2.set_title('Completed Quests per Day')
    ax2.set_ylabel('Number of completed quests')
    fig2.tight_layout()
    img2 = io.BytesIO()
    fig2.savefig(img2, format='png')
    img2.seek(0)
    graph_urls['completed_quests'] = base64.b64encode(img2.getvalue()).decode()

    plt.close(fig2)

    return graph_urls


# Home page displaying a single weekly planner
@app.route("/")
def home():
    return render_template('index.html', planner=weekly_planner)


# Route to add a new quest
@app.route('/add_quest/<day>', methods=['POST'])
def add_quest(day):
    # day = request.form.get('day')
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


@app.route('/evaluate')
def evaluate_performance():
    # Calculate performance metrics
    performance_data = calculate_performance()
    # Generate visual graphs
    graph_urls = generate_graphs(performance_data)
    return render_template('evaluate.html', performance_data=performance_data, graph_urls=graph_urls)


@app.route('/quest/edit/<day>/<int:quest_index>', methods=['GET', 'POST'])
def edit_quest(day, quest_index):
    # Check if quest_index is valid for the given day
    if 0 <= quest_index < len(weekly_planner[day]):
        quest = weekly_planner[day][quest_index]
        if request.method == 'POST':
            # Get updated quest data from the form
            title = request.form.get('title')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            location = request.form.get('location')
            description = request.form.get('description')
            # Validate required fields
            if not title or not start_time or not end_time:
                flash('Title, start time, and end time are required!', 'error')
                return redirect(url_for('edit_quest', day=day, quest_index=quest_index))
            # Validate time format
            try:
                datetime.strptime(start_time, '%H:%M')
                datetime.strptime(end_time, '%H:%M')
            except ValueError:
                flash('Invalid time format!')
                return redirect(url_for('edit_quest', day=day, quest_index=quest_index))
            if start_time >= end_time:
                flash('End time must be after start time.', 'error')
                return redirect(url_for('edit_quest', day=day, quest_index=quest_index))
            # Update the quest with new data
            quest.update({
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "location": location,
                "description": description
            })
            flash('Quest updated successfully!')
            return redirect(url_for('home'))  # Redirect to the homepage or planner
        # Render the template and pass the quest, day, quest_index, and weekly_planner
        return render_template('index.html', quest=quest, day=day, quest_index=quest_index, planner=weekly_planner)
    else:
        flash('Invalid quest index!')
        return redirect(url_for('home'))  # Redirect if invalid index


if __name__ == '__main__':
    load_data()
    app.run(debug=True)
