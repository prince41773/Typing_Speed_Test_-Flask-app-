from flask import Flask, render_template_string, request, redirect, url_for
import random
import time

app = Flask(__name__)

class TypingSpeedTest:
    def __init__(self):
        self.sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "She sells seashells by the seashore.",
            "Peter Piper picked a peck of pickled peppers.",
            "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
            "The cat in the hat came back.",
            "A stitch in time saves nine.",
            "All that glitters is not gold.",
            "Better late than never."
        ]
        self.timer_running = False
        self.duration_mapping = {'30 sec': 30, '1 min': 60, '2 min': 120}
        self.test_text = ""
        self.start_time = 0
        self.end_time = 0
        self.remaining_time = 0  # Initialize remaining time

    def generate_text(self, duration):
        return ' '.join(random.choices(self.sentences, k=8))

    def start_test(self, duration):
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration_mapping[duration]
        self.timer_running = True
        self.test_text = self.generate_text(duration)
        self.remaining_time = self.duration_mapping[duration]  # Set remaining time to the selected duration
        return self.test_text

    def update_time(self):
        if self.timer_running:
            remaining_time = max(0, self.end_time - time.time())
            if remaining_time <= 0:
                self.timer_running = False
                return "Time's up!"
            else:
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                self.remaining_time = f"{minutes:02d}:{seconds:02d}"  # Format remaining time
                return self.remaining_time
        return ""

    def display_results(self, typed_text):
        accuracy = self.calculate_accuracy(typed_text)
        wpm = self.calculate_wpm(typed_text)
        return f"Accuracy: {accuracy:.2f}%  WPM: {wpm:.2f}"

    def calculate_accuracy(self, typed_text):
        typed_words = typed_text.split()
        test_words = self.test_text.split()
        correct_words = sum(1 for typed, test in zip(typed_words, test_words) if typed == test)
        return (correct_words / len(typed_words)) * 100 if typed_words else 0

    def calculate_wpm(self, typed_text):
        words_typed = len(typed_text.split())
        time_taken = time.time() - self.start_time
        wpm = (words_typed / time_taken) * 60
        return wpm

typing_test = TypingSpeedTest()

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Typing Speed Test</title>
    <style>
        body {
            background: linear-gradient(135deg, #FFD9FF 0%, #FFC9C9 50%, #AFC0FF 100%);
            font-family: Arial, sans-serif;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        form {
            text-align: center;
            margin-top: 20px;
        }
        label {
            font-weight: bold;
        }
        select, button {
            padding: 10px;
            margin: 5px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #019806;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        select:hover, button:hover {
            background-color: #006D59;
        }
        p {
            text-align: center;
            margin-top: 20px;
        }
        #remaining_time {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        #result_form {
            text-align: center;
            margin-top: 20px;
        }
        #result_form input[type="text"], #result_form button[type="submit"] {
            padding: 10px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #028CB9;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        #result_form input[type="text"]:hover, #result_form button[type="submit"]:hover {
            background-color: #003652;
        }
    </style>
</head>
<body>
    <h1>Typing Speed Test</h1>
    <form method="POST" action="/">
        <label for="duration">Select Duration:</label>
        <select name="duration" id="duration">
            <option value="30 sec" {% if duration == '30 sec' %}selected{% endif %}>30 sec</option>
            <option value="1 min" {% if duration == '1 min' %}selected{% endif %}>1 min</option>
            <option value="2 min" {% if duration == '2 min' %}selected{% endif %}>2 min</option>
        </select>
        <button type="submit">Start Test</button>
    </form>
    <br>
    <p>{{ test_text }}</p>
    <p> Remaining Time  </p>
    <p id="remaining_time">{{ remaining_time }}</p>
    <form id="result_form" method="POST" action="/result">
        <label for="typed_text">Type here:</label>
        <input type="text" name="typed_text" id="typed_text">
        <button type="submit">Submit</button>
    </form>
    <form method="POST" action="/reset">
        <button type="submit">Reset</button>
    </form>
    <script>
        function updateTimer() {
            var remainingTimeElement = document.getElementById("remaining_time");
            var remainingTimeParts = remainingTimeElement.textContent.split(':');
            var minutes = parseInt(remainingTimeParts[0]);
            var seconds = parseInt(remainingTimeParts[1]);
            if (minutes == 0 && seconds == 0) {
                clearInterval(timerInterval);
                remainingTimeElement.textContent = "Time's up!";
                document.getElementById("result_form").submit(); // Submit the form
            } else {
                if (seconds == 0) {
                    minutes--;
                    seconds = 59;
                } else {
                    seconds--;
                }
                remainingTimeElement.textContent = minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
            }
        }
        var timerInterval = setInterval(updateTimer, 1000);
    </script>
</body>
</html>
"""
result_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Typing Speed Test Result</title>
    <style>
        body {
            background: linear-gradient(135deg, #FFD9FF 0%, #FFC9C9 50%, #AFC0FF 100%);
            font-family: Arial, sans-serif;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        p {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Typing Speed Test Result</h1>
    <p>{{ result }}</p>
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        duration = request.form['duration']
        test_text = typing_test.start_test(duration)
        return render_template_string(index_html, test_text=test_text, duration=duration, remaining_time=typing_test.update_time())
    return render_template_string(index_html, test_text="", duration="30 sec", remaining_time="")

@app.route('/result', methods=['POST'])
def result():
    typed_text = request.form['typed_text']
    result = typing_test.display_results(typed_text)
    return render_template_string(result_html, result=result)

@app.route('/reset', methods=['POST'])
def reset():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
