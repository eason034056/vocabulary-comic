from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import uuid
import boto3  # 如果你用 S3，記得安裝 pip install boto3

app = Flask(__name__)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.get_json()
    word = data.get('word')
    if not word:
        return jsonify({'error': 'Missing word'}), 400

    prompt = f"Create a 1024x1024 px 4-panel comic strip (2x2 layout) in black-and-white Notion style that explains the meaning of the English word “{word}”..."

    # Setup Selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('/usr/bin/chromedriver')  # Railway image 路徑

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get('https://chat.openai.com')  
        time.sleep(10)  # 網頁載入與登入（⚠ 需要你事先處理好 session/cookies）

        # 找到輸入框並輸入 prompt
        input_box = driver.find_element(By.TAG_NAME, 'textarea')
        input_box.send_keys(prompt)
        input_box.submit()
        time.sleep(30)  # 等待生成圖片（可視情況調整）

        # 抓到圖片元素
        image_element = driver.find_element(By.CSS_SELECTOR, 'img')  # 可能需要你調整 selector
        image_url = image_element.get_attribute('src')

        # 下載圖片 + 上傳 S3
        filename = f"{uuid.uuid4()}.png"
        s3 = boto3.client('s3', aws_access_key_id='YOUR_KEY', aws_secret_access_key='YOUR_SECRET')
        s3.upload_file('/local/path.png', 'your-bucket-name', filename)
        public_url = f"https://your-bucket-name.s3.amazonaws.com/{filename}"

        return jsonify({'image_url': public_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
