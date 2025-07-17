import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Полные абсолютные пути для Render
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'static', 'processed')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаем директории при запуске
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_color_histogram(img, title):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    pixels = list(img.getdata())
    r = [pixel[0] for pixel in pixels]
    g = [pixel[1] for pixel in pixels]
    b = [pixel[2] for pixel in pixels]
    
    plt.figure(figsize=(10, 5))
    plt.hist(r, bins=256, color='red', alpha=0.5, label='Red')
    plt.hist(g, bins=256, color='green', alpha=0.5, label='Green')
    plt.hist(b, bins=256, color='blue', alpha=0.5, label='Blue')
    plt.title(title)
    plt.xlabel('Color Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.read()).decode('utf-8')

def apply_periodic_function(img, func_type, period):
    img_array = np.array(img) / 255.0
    
    x = np.arange(img_array.shape[1])
    y = np.arange(img_array.shape[0])
    xx, yy = np.meshgrid(x, y)
    
    if func_type == 'sin':
        periodic = np.sin(2 * np.pi * (xx + yy) / period)
    else:
        periodic = np.cos(2 * np.pi * (xx + yy) / period)
    
    periodic = (periodic + 1) / 2
    
    for i in range(3):
        img_array[:, :, i] = img_array[:, :, i] * periodic
    
    return Image.fromarray((img_array * 255).astype(np.uint8))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Сохраняем оригинал
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(original_path)
            
            # Получаем параметры
            func_type = request.form.get('func_type', 'sin')
            period = float(request.form.get('period', 10))
            
            # Обрабатываем изображение
            original_img = Image.open(original_path)
            processed_img = apply_periodic_function(original_img, func_type, period)
            
            # Сохраняем результат
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            
            # Определяем формат из расширения файла
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.jpg':
                file_ext = '.jpeg'
            
            processed_img.save(processed_path, format=file_ext[1:])  # Убираем точку
            
            # Создаем гистограммы
            original_hist = create_color_histogram(original_img, 'Original Image Color Distribution')
            processed_hist = create_color_histogram(processed_img, 'Processed Image Color Distribution')
            
            return render_template('result.html', 
                               original_image=os.path.join('uploads', filename),
                               processed_image=os.path.join('processed', processed_filename),
                               original_hist=original_hist,
                               processed_hist=processed_hist)
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)