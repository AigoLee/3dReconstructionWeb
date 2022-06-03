# 基于迁移学习的三维重建系统
## 环境配置
- Node.js v16.14.0
    - http-server@14.1.0
- python v3.9.7
    - tensorflow==2.6.0
    - keras==2.6.0
    - numpy==1.22.3
    - Pillow==9.1.0
    - matplotlib==3.5.1
    - open3d==0.15.1
    - Flask==2.1.1
    - waitress==2.1.1
## 项目结构
```
├── readme.md                       
├── app.py                          
├── conf.py                         
├── data            服务端接收和生成的资源
│   ├── pcds        点云文件pcd格式
│   ├── plys        点云文件ply格式   
│   ├── pngs_depth  生成的深度图        
│   └── pngs_rgb    接收的rgb图像           
├── modules         处理模块
│   ├── conf.py
│   ├── layers.py
│   ├── model.h5    模型文件
│   ├── predict.py
│   ├── utils.py
│   └── __init__.py
├── static                        
│   ├── css
│   ├── js          渲染点云的js脚本
│   └── exhibit
└── templates
    ├── exhibit.html
    ├── index.html
    ├── layout.html
    ├── result.html
    └── upload.html
```
## 使用说明
1. 首先确保服务端和测试端连接同一个局域网，可通过```ipconfig```查看所在局域网IP
2. 修改根目录下```conf.py```配置文件，将```server_model_ip```和```server_3d_ip```改为局域网IP
3. 在根目录下打开终端，输入```python app.py```
4. 在根目录下打开另一个终端，输入```http-server -p 8080```
5. 在PC的浏览器或手机浏览器输入 ```局域网IP:5000```，例如```192.168.3.3:5000```，即可使用该系统
