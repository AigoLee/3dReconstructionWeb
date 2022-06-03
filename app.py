"""
2022-04-15
"""
import webbrowser
from threading import Timer
from PIL import Image
from flask import Flask, send_file, render_template, request, jsonify, abort, flash, redirect, url_for
from waitress import serve
import base64
from conf import host, port, server_model_ip, server_3d_ip, port_model, port_3d
from modules import utils, conf, predict
import os 

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

# log = open('./log.txt', 'a')

# @app.before_request
# def before():
#     log.write('%s %s %s\n' % (
#         datetime.today().strftime('%Y-%m-%d %H:%M:%S'), request.method, request.path))
#     if request.json is not None:
#         log.write('Req: %s\n' % str(request.json))
#     else:
#         log.write('\n')
#     log.flush()


# @app.after_request
# def after(response: Response):
#     if request.method == 'POST':
#         try:
#             log.write('Res: %s\n\n' % str(json.loads(response.data)))
#         except Exception:
#             log.write('Res: %s\n\n' % str(response.data)[2:-1])
#         log.flush()
#     return response


@app.route('/')
def index():
    return render_template('index.html', 
                    upload_ip='http://'+ server_model_ip + port_model+'/upload',
                    home_ip='http://'+ server_model_ip + port_model,
                    exhibit_ip='http://'+ server_model_ip + port_model+'/exhibit')

@app.route('/exhibit')
def exhibit():
    return render_template('exhibit.html', 
                    home_ip='http://'+ server_model_ip + port_model, 
                    server_3d_ip=server_3d_ip + port_3d,
                    server_model_ip=server_model_ip + port_model)


@app.route('/upload')
def upload():
    return render_template('upload.html', 
                    home_ip='http://'+ server_model_ip + port_model)


@app.route('/predication', methods=['POST'])
def predication():
    """
    预测深度图，生成点云模型
    """
    file = request.files['file']
    filename = file.filename 

    if filename == '':
        flash('Error: 没有文件上传或选中！')
        return redirect(url_for('upload'))
    if 'png' in filename.lower(): 
        format_ = 'PNG' 
    elif 'jpg' in filename.lower() or 'jpeg' in filename.lower():
        format_ = 'JPEG'
    else:
        flash('Error: 请上传图片！')
        return redirect(url_for('upload'))

    #得到rgb图像 并保存
    img = Image.open(file.stream)
    img = utils.resize_Image(img, (640, 480))   #重设分辨率
    img_save_path = '{0}/rgb_{1}.png'.format(conf.rgb_input_dir, filename.split('.')[0])
    img.save(img_save_path)

    #得到depth图像 并保存
    img_depth = predict.get_img_depth(img)
    img_depth_save_path = '{0}/depth_{1}.png'.format(conf.depth_output_dir, filename.split('.')[0])
    img_depth.resize((640, 480)).save(img_depth_save_path)

    #根据depth和rgb生成ply和pcd点云文件 并保存
    save_path_cpd = '{0}/{1}.pcd'.format(conf.ply_path, filename.split('.')[0])
    utils.depth_to_CloudPoints(img_depth_save_path, img_save_path, filename.split('.')[0])

    # 将rgb和depth图像转为二进制流 传到前端
    data_depth = utils.Image_to_Bytes(img_depth, format_)
    data_depth_str = base64.b64encode(data_depth).decode('ascii') #byte类型转换为str  

    data = utils.Image_to_Bytes(img, format_)
    data_str = base64.b64encode(data).decode('ascii') #byte类型转换为str 
    
    return render_template('result.html',
            img_stream=data_str, 
            depth_stream=data_depth_str, 
            model_path='http://'+ server_3d_ip + port_3d +'/viewer.html?load=data/pcds/'+save_path_cpd.split('/')[-1]+'&homeIP='+ server_model_ip + port_model, 
            depth_path='http://'+ server_model_ip +port_model+'/depth/'+img_depth_save_path.split('/')[-1], 
            pcd_path='http://'+ server_model_ip +port_model+'/pcd/'+save_path_cpd.split('/')[-1],
            home_ip='http://'+ server_model_ip +port_model)


@app.route('/pcd/<filename>')
def get_pcd(filename: str):
    '''
    展示pcd点云模型文件
    '''
    try:
        return send_file('./data/pcds/' + filename)
    except Exception:
        abort(404)


@app.route('/depth/<filename>')
def get_depth(filename: str):
    '''
    展示深度图
    '''
    try:
        return send_file('./data/pngs_depth/' + filename)
    except Exception:
        abort(404)


def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')


if __name__ == '__main__':
    if conf.debug:
        app.run(host, port, conf.debug)
    else:
        Timer(1, open_browser).start()
        serve(app, host=host, port=port)
