import sys

from flask import Flask, render_template, Response
from pygpt4all import GPT4All

app = Flask(__name__)

class Generator:
    model = GPT4All(model_path="static/models/snoozy.bin")
    @staticmethod
    def generate(prompt):
        """
        Generates text with the GPT4All model
        I have set some parameters, but I don't know if they can still be improved.
        :param prompt: The prompt to generate text from
        :return: A dictionary with the prompt and the generated text pairs.
        """

        try:
            print("in generation")
            for token in Generator.model.generate(prompt, temp=0.2, n_threads=8, n_predict=300, repeat_penalty=1.5):
                print(token)
                yield token
        except Exception as e:
            print(e)
            sys.exit(1)

@app.route('/stream/<prompt>')
def stream_tokens(prompt):
    def generate_tokens():
        for token in Generator.generate(prompt):
            yield token

    return Response(generate_tokens(), mimetype='text/plain')

@app.route('/test')
def test():
    return render_template('index.html', chatHistory=chatHistory, currentPrompt="User Prompt")

@app.route('/')
def index():
    return render_template('index.html', chatHistory=chatHistory, currentPrompt="User Prompt")

if __name__ == '__main__':
    app.run()

chatHistory = {"Prompt1": "Ja das ist eine Antwort", "Prompt2": "Neee das ist keine Antwort"}