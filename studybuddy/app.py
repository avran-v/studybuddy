from flask import Flask, render_template, request, jsonify

import openai
import json 
import re
import random

app = Flask(__name__)

# Configure your OpenAI API key
openai.api_key = 'API-KEY'

advice_array = [
    "Don't give up now.",
    "Stay focused.",
    "Finish strong.",
    "Push through the struggle.",
    "Keep your eye on the prize.",
    "Persevere through the challenges.",
    "Just a little more effort.",
    "One step at a time.",
    "Embrace the grind.",
    "You've got this!",
    "Stay determined.",
    "Stay committed to your goals.",
    "Believe in yourself.",
    "Your efforts will pay off.",
    "Keep moving forward.",
    "Don't stop now.",
    "It's within reach.",
    "Stay motivated.",
    "Keep the momentum going.",
    "Stay on course.",
    "You're on the right track.",
    "Stay resilient.",
    "Success is near.",
    "Keep your spirits high.",
    "Trust the process.",
    "Stay dedicated.",
    "The finish line is in sight.",
    "Keep your head up.",
    "Perseverance leads to victory.",
    "You're almost at the finish line."
]

assignmentGiven = 0
outlineFound = 0
tasks = []
times = []
current_timer = 0
current_task = -1
initial_goal = ""

@app.route('/')
def index():
    return render_template('index.html', data=current_timer)

@app.route('/get_updated_data')
def get_updated_data():
    updated_data = current_timer; 
    return jsonify(updated_data)

@app.route('/get_updated_tasks')
def get_updated_tasks():
    updated_tasks = tasks
    return jsonify(updated_tasks)

@app.route('/ask', methods=['POST'])
def ask():

    global current_timer
    global assignmentGiven
    global outlineFound
    global current_task
    global initial_goal
    user_message = request.form['user_message']
    if assignmentGiven == 0:
        initial_goal = user_message
        assignmentGiven = 1
        user_message+="An assignment has been given, the assignment must be completed in 1 day. Return an outline of tasks numbered, in the format: \
        1. task - time to complete the task in minutes Do not give any additional background for the tasks, \
        just the task and the estimated time. Do not do any additional separations by day or time, just a simple \
        outline with tasks numbered. Start the outline with the header \"Outline\" . Make sure that none of the tasks \
        are more than 60 minutes, if so, break them down into two tasks."

    prompt = f"You: {user_message}\nStudyBuddy:"

    if current_task>=0:
        if current_task >= len(tasks):
            user_message="Congratulate me on finishing " + initial_goal + " and give me some motivation for doing more of my work in 2-3 sentences."
        else:
            user_message="Give a one-sentence motivational message for me to finish my work. An example is \"You can do it!\" or \"I believe in you\"" 
            print(user_message)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )

    chatbot_message = response.choices[0].text

    if outlineFound == 0:
        outlineFound = 1 
        outline = json.dumps(chatbot_message,indent=None).strip()
        task_matches = re.findall(r'\d+\.\s(.*?)\s-\s(\d+)\sminutes', outline)
        for task, time in task_matches:
            tasks.append(task)
            times.append(int(time))
        
        current_timer = times[0]
        
    print(outlineFound)
    if current_task == -1:
        chatbot_message += ". Let's get started on the first task! I'll set a timer for " + str(current_timer) + " minutes. \
        Click start whenever you feel ready. Type \"done\" into chat when you're done!"
        current_task = 1
    elif current_task < len(tasks):
        chatbot_message = "Your next task is: " + tasks[current_task] + "." + advice_array[random.randint(0,29)] + "Type \"done\" into chat when you're done!"
        current_timer=times[current_task]
        current_task+=1
    else:
        chatbot_message += " I'm always here for you, come back any time and get some more work done!"

    return jsonify({'message':chatbot_message})

if __name__ == '__main__':
    app.run(debug=True)
