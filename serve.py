from flask import Flask, request, jsonify
# 假設 LLaVA 已在當前目錄中安裝
from llava import LLaVA

app = Flask(__name__)
model = LLaVA(model_path="/models")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    prompt = data.get('prompt')
    image = data.get('image')  # 假設是 base64 編碼圖像
    response = model.process_image(prompt, image)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

