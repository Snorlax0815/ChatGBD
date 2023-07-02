from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def generate_text():
        # Your function that generates text word by word
        text_generator = Generator.generate("Please tell me a joke.")

        for word in text_generator:
            yield f"data: {word}\n\n"  # Send the word as an SSE event

    return Response(generate_text(), mimetype='text/event-stream')


import sys

from flask import Flask, request, render_template
from pygpt4all.models.gpt4all import GPT4All
from markupsafe import escape

@app.get('/')
def hello_world():
    print(Generator.history)
    return render_template('index.html', title="ChatGBD", chatHistory=Generator.history)


@app.get('/test')
def test():
    s = "Hallo, hier sit der Code: \n```def clearhistory():\n\tprint(\"clearing history\")\n\tGenerator.clearhistory()\n\treturn hello_world()``` Das finde ich sehr cool!"
    Generator.history[0] = ["Prompt", Generator.separateCode(s)]
    return render_template('index.html', title="ChatGBD", chatHistory=Generator.history)


@app.template_filter('convert_spaces_to_tabs')
def convert_spaces_to_tabs_filter(s):
    return s.replace('    ', '\t')


@app.post('/')
def hallowithpost():
    Generator.generate(escape(request.form['Prompt']))
    print(Generator.history)
    return hello_world()


@app.post('/clearhistory')
def clearhistory():
    print("clearing history")
    Generator.clearhistory()
    return hello_world()


"""
@app.post('/generate')
def generate():
    Generator.generate(escape(request.form['prompt']))
    # print(Generator.history)
    return render_template('index.html', title="GPT4All", chatHistory=Generator.history)
"""


class Generator:
    """
    Diese Klasse generiert Texte mit dem GPT4All Modell
    Es wird auch ein Chatverlauf gespeichert
    """
    model = GPT4All(model_path="../static/models/snoozy.bin")
    # model = GPT4All(model_path="../static/models/ggml-gpt4all-l13b-snoozy.bin")
    # model = GPT4All(model_path="static/models/ggml-nous-gpt4-vicuna-13b.bin")
    # model = GPT4All("static/models/ggml-v3-13b-hermes-q5_1.bin")
    history = {}

    def __init__(self):
        pass

    @staticmethod
    def generate(prompt):
        returntext = ""
        print("in generation")
        try:
            for token in Generator.model.generate(prompt, temp=0.2, n_threads=8, n_predict=300, repeat_penalty=1.5):
                returntext += token
                print(token)
            if len(returntext) < 1:
                print(f"retrying {returntext}")
                return Generator.generate(prompt)
            print(f"Return Text: {returntext}")
        except Exception as e:
            print(e)
            sys.exit(1)
        Generator.history[len(Generator.history)] = [prompt, Generator.separateCode(returntext)]
        # print(returntext)
        # print(Generator.history)
        Generator.separateCode(returntext)
        return returntext

    @staticmethod
    def clearhistory():
        Generator.history = {}
        Generator.model.reset()

    @staticmethod
    def separateCode(text):
        returnList = []
        if text.count("```") < 1:
            if text.count("``") <1:
                sections = text.split("`")
            else:
                sections = text.split("``")
        else:
            sections = text.split("```")

        for i, section in enumerate(sections):
            if i % 2 == 0:
                # Text section
                returnList.append(section)
            else:
                # Code section
                returnList.append("```" + section + "```")
        print(returnList)
        return returnList


if __name__ == '__main__':
    app.run()
