from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/codex', methods=['POST'])
def codex():
    data = request.json
    prompt = data.get('prompt', '')
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=prompt,
        max_tokens=100
    )
    return jsonify({'result': response.choices[0].text})

if __name__ == '__main__':
    app.run(debug=True)
