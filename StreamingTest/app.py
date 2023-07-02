import sys
from flask import Flask, render_template, Response, request
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
        :return: A generator that yields tokens as they are generated
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
            yield 'data: ' + token + '\n\n'
        yield 'data: ' + "[STOPCODE]" + '\n\n'

    return Response(generate_tokens(), mimetype='text/event-stream')


@app.route('/test', methods=['GET', 'POST'])
def test():
    chatHistory = {"Prompt1": "Ja das ist eine Antwort", "Prompt2": "Neee das ist keine Antwort"}
    if request.method == 'GET':
        # prompt = request.form['prompt']
        return render_template('index.html', chatHistory=chatHistory, currentPrompt="Please tell me a joke", promptGenerated=True)
    else:
        return render_template('index.html', chatHistory=chatHistory, currentPrompt="User Prompt", promptGenerated=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    chatHistory = {"Prompt1": "Ja das ist eine Antwort", "Prompt2": "Neee das ist keine Antwort"}
    if request.method == 'POST':
        prompt = request.form['prompt']
        print(prompt)
        return render_template('index.html', chatHistory=chatHistory, currentPrompt=prompt, promptGenerated=True)
    else:
        return render_template('index.html', chatHistory=chatHistory, currentPrompt="User Prompt", promptGenerated=False)


if __name__ == '__main__':
    app.run()
