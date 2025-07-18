import os
import io
import base64
import traceback
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# Конфигурация (ВАЖНО: без 'static/' в путях)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Создаем директории в static_folder
os.makedirs(os.path.join(app.static_folder, app.config['UPLOAD_FOLDER']), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, app.config['PROCESSED_FOLDER']), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_color_histogram(img, title):
    plt.figure(figsize=(10, 5))
    if img.mode != 'RGB':
        img = img.convert('RGB')
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
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def apply_periodic_function(img, func_type, period):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_arr = np.array(img, dtype=np.float32) / 255.0
    height, width = img_arr.shape[:2]
    x = np.linspace(0, 2*np.pi, width, dtype=np.float32)
    y = np.linspace(0, 2*np.pi, height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    if func_type == 'sin':
        pattern = np.sin((xx + yy) * (2*np.pi/max(1, period)))
    else:
        pattern = np.cos((xx + yy) * (2*np.pi/max(1, period)))
    pattern = (pattern + 1) * 0.3 + 0.2
    result = np.empty_like(img_arr)
    for i in range(3):
        result[:,:,i] = np.clip(img_arr[:,:,i] * pattern, 0, 1)
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
                original_path = os.path.join(app.static_folder, app.config['UPLOAD_FOLDER'], filename)
                file.save(original_path)

                with Image.open(original_path) as img:
                    if max(img.size) > 2000:
                        img.thumbnail((2000, 2000))
                    
                    func_type = request.form.get('func_type', 'sin')
                    try:
                        period = float(request.form.get('period', 10))
                        period = max(1, min(100, period))
                    except ValueError:
                        period = 10
                    
                    processed_img = apply_periodic_function(img, func_type, period)
                    processed_filename = f"processed_{filename}"
                    processed_path = os.path.join(app.static_folder, app.config['PROCESSED_FOLDER'], processed_filename)
                    
                    if processed_img.mode != 'RGB':
                        processed_img = processed_img.convert('RGB')
                    
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in ('.jpg', '.jpeg'):
                        processed_img.save(processed_path, format='JPEG', quality=85)
                    else:
                        processed_img.save(processed_path, format='PNG', optimize=True)
                    
                    if not os.path.exists(processed_path):
                        raise Exception("Processed image not saved")
                    if os.path.getsize(processed_path) == 0:
                        raise Exception("Processed image is empty")

                    original_hist = create_color_histogram(img, 'Original Image')
                    processed_hist = create_color_histogram(processed_img, 'Processed Image')

                return render_template(
    			'result.html',
    			original_image_url=url_for('static', filename=f'uploads/{filename}', _external=True),
    			processed_image_url=url_for('static', filename=f'processed/processed_{filename}', _external=True),
    			original_hist=original_hist or '',
    			processed_hist=processed_hist or ''
		)            
            except Exception as e:
                app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
                return render_template(
                    'result.html',
                    error=f"Ошибка обработки: {str(e)}"
                )
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)