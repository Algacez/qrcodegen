#!/usr/bin/env python3
"""
本地二维码生成器 WebUI
"""

import io
import base64
from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
)

app = Flask(__name__)

# 模块样式映射
MODULE_STYLES = {
    'square': SquareModuleDrawer(),
    'rounded': RoundedModuleDrawer(),
    'circle': CircleModuleDrawer(),
    'vertical': VerticalBarsDrawer(),
    'horizontal': HorizontalBarsDrawer(),
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # 获取参数
    data = request.form.get('data', '')
    size = int(request.form.get('size', 300))
    border = int(request.form.get('border', 4))
    fill_color = request.form.get('fill_color', '#000000')
    back_color = request.form.get('back_color', '#ffffff')
    error_correction = request.form.get('error_correction', 'M')
    module_style = request.form.get('module_style', 'square')

    if not data:
        return {'error': '请输入要生成的内容'}, 400

    # 错误纠正级别
    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }

    # 创建二维码
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction_map.get(error_correction),
        box_size=10,
        border=border,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # 根据样式创建图片
    drawer = MODULE_STYLES.get(module_style, SquareModuleDrawer())

    img = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
        image_factory=StyledPilImage,
        module_drawer=drawer,
    )

    # 调整大小
    img = img.resize((size, size))

    # 转换为base64用于预览
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    img_data = f'data:image/png;base64,{img_str}'

    return {'image': img_data}


@app.route('/download', methods=['POST'])
def download():
    data = request.form.get('data', '')
    size = int(request.form.get('size', 300))
    border = int(request.form.get('border', 4))
    fill_color = request.form.get('fill_color', '#000000')
    back_color = request.form.get('back_color', '#ffffff')
    error_correction = request.form.get('error_correction', 'M')
    module_style = request.form.get('module_style', 'square')

    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction_map.get(error_correction),
        box_size=10,
        border=border,
    )

    qr.add_data(data)
    qr.make(fit=True)

    drawer = MODULE_STYLES.get(module_style, SquareModuleDrawer())
    img = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
        image_factory=StyledPilImage,
        module_drawer=drawer,
    )
    img = img.resize((size, size))

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='qrcode.png')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
