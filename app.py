import os
import io
import base64
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Важно для сервера
import matplotlib.pyplot as plt

app = Flask(__name__)

# Конфигурация
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB лимит
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Создаем директории при старте
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_color_histogram(img, title):
    # Оптимизированная версия с очисткой памяти
    plt.figure(figsize=(10, 5))
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Используем numpy для эффективного расчета
    arr = np.array(img)
    plt.hist(arr[:,:,0].ravel(), bins=256, color='red', alpha=0.5, label='Red')
    plt.hist(arr[:,:,1].ravel(), bins=256, color='green', alpha=0.5, label='Green')
    plt.hist(arr[:,:,2].ravel(), bins=256, color='blue', alpha=0.5, label='Blue')
    
    plt.title(title)
    plt.xlabel('Color Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80)  # Уменьшаем dpi
    plt.close()  # Важно: закрываем figure для освобождения памяти
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def apply_periodic_function(img, func_type, period):
    # Оптимизированная обработка с контролем памяти
    img_arr = np.array(img, dtype=np.float32) / 255.0  # Используем float32 вместо float64
    
    h, w = img_arr.shape[:2]
    x = np.linspace(0, 2*np.pi, w)
    y = np.linspace(0, 2*np.pi, h)
    xx, yy = np.meshgrid(x, y)
    
    periodic = np.sin(xx + yy) if func_type == 'sin' else np.cos(xx + yy)
    periodic = (periodic + 1) / 2
    
    # Применяем к каждому каналу с освобождением памяти
    result = np.empty_like(img_arr)
    for i in range(3):
        result[:,:,i] = img_arr[:,:,i] * periodic
    
    return Image.fromarray((result * 255).astype(np.uint8))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Сохраняем оригинал
                file.save(original_path)
                
                # Обработка
                with Image.open(original_path) as img:
                    # Ресайз для больших изображений
                    if max(img.size) > 2000:
                        img.thumbnail((2000, 2000))
                    
                    processed_img = apply_periodic_function(
                        img,
                        request.form.get('func_type', 'sin'),
                        float(request.form.get('period', 10))
                    )
                    # Сохранение результата
                    processed_filename = f"processed_{filename}"
                    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
                    processed_img.save(processed_path, quality=85)  # Уменьшаем качество
                    
                    # Гистограммы
                    original_hist = create_color_histogram(img, 'Original Image')
                    processed_hist = create_color_histogram(processed_img, 'Processed Image')
                
                return render_template('result.html',
                                   original_image=f"uploads/{filename}",
                                   processed_image=f"processed/{processed_filename}",
                                   original_hist=original_hist,
                                   processed_hist=processed_hist)
            
            except Exception as e:
                # Логирование ошибки
                app.logger.error(f"Error processing image: {str(e)}")
                return "Error processing image", 500
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)