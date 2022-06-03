import numpy as np
import matplotlib.pyplot as plt
import open3d as o3d
from io import BytesIO
import PIL
from modules import conf


def resize_Image(img: PIL.Image, img_size: tuple):
    if img.size == img_size:
        return img
    else:
        return img.resize(img_size)


def depth_to_CloudPoints(depth_path: str, color_path: str, filename):
    '''
    根据深度图生成三维点云,，支持格式：pcb，ply
    '''
    color_raw = o3d.io.read_image(color_path)
    print(type(color_raw))
    depth_raw = o3d.io.read_image(depth_path)
    rgbd_img = o3d.geometry.RGBDImage.create_from_color_and_depth(color_raw, depth_raw)
    print(rgbd_img)
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_img,
        o3d.camera.PinholeCameraIntrinsic(
            o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault))
    # 翻转矩阵，不然的话点云是翻转的
    pcd.transform([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])
    bunny = 'outputs/plys/626_image.ply'
    pcd.scale(40000, pcd.get_center())
    # if conf.debug:
    #     o3d.visualization.draw_geometries([pcd])
    o3d.io.write_point_cloud('{0}/{1}.ply'.format(conf.ply_path, filename), pcd)
    o3d.io.write_point_cloud('{0}/{1}.pcd'.format(conf.pcb_path, filename), pcd)


def Image_to_Bytes(img: PIL.Image, format: str) -> bytes:
    '''
    image对象转为二进制流
    format: 'JPEG' / 'PNG'
    return: bytes
    '''
    new_img = img.convert("RGB")
    img_byte = BytesIO()
    new_img.save(img_byte, format=format)
    data = img_byte.getvalue()  
    return data