import sys

from flask import Flask, request, render_template
from pygpt4all.models.gpt4all import GPT4All
from markupsafe import escape

app = Flask(__name__)


@app.get('/')
def render():
    print(Generator.history)
    return render_template('index.html', title="ChatGBD", chatHistory=Generator.history)


@app.template_filter('convert_spaces_to_tabs')
def convert_spaces_to_tabs_filter(s):
    return s.replace('    ', '\t')


@app.post('/')
def handleprompt():
    Generator.generate(escape(request.form['Prompt']))
    print(Generator.history)
    return render()


@app.post('/clearhistory')
def clearhistory():
    print("clearing history")
    Generator.clearhistory()
    return render()


class Generator:
    """
    Diese Klasse generiert Texte mit dem GPT4All Modell
    Es wird auch ein Chatverlauf gespeichert
    """
    model = GPT4All(model_path="static/models/snoozy.bin")
    history = {}

    def __init__(self):
        pass

    @staticmethod
    def generate(prompt):
        """
        Generates text with the GPT4All model
        I have set some parameters, but I don't know if they can still be improved.
        :param prompt: The prompt to generate text from
        :return: A dictionary with the prompt and the generated text pairs.
        """
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
        Generator.separateCode(returntext)
        return returntext

    @staticmethod
    def clearhistory():
        Generator.history = {}
        Generator.model.reset()

    @staticmethod
    def separateCode(text):
        """
        This function tries its best to separates code from text.
        Since the model generates code however it wants, it is not always possible to separate code from text.
        The code will be surrounded by ```.
        :param text: The text to separate
        :return: A list of strings, where every second string is code
        """
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
