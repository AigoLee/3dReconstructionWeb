from keras.models import load_model
from .layers import BilinearUpSampling2D
import numpy as np
from PIL import Image
import os
from .conf import model_path

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"  # 使用第二块GPU（从0开始
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'


custom_objects = {'BilinearUpSampling2D': BilinearUpSampling2D, 'depth_loss_function': None}
model = load_model(model_path, custom_objects=custom_objects, compile=False)


def __to_multichannel(i):
    if i.shape[2] == 3: return i
    i = i[:,:,0]
    return np.stack((i,i,i), axis=2)

def __DepthNorm(x, maxDepth):
    return maxDepth / x


def predict(model, images, minDepth=10, maxDepth=1000, batch_size=2):
    # Support multiple RGBs, one RGB image, even grayscale 
    if len(images.shape) < 3: images = np.stack((images,images,images), axis=2)#灰度图拓展为3通道?
    if len(images.shape) < 4: images = images.reshape((1, images.shape[0], images.shape[1], images.shape[2]))
    # Compute predictions
    predictions = model.predict(images, batch_size=batch_size)
    # Put in expected range
    return np.clip(__DepthNorm(predictions, maxDepth=maxDepth), minDepth, maxDepth) / maxDepth


def load_images(file: Image):
    loaded_images = []
    # 把数组中小于min的值设置为min，大于max的值设置为max。
    x = np.clip(np.asarray(file, dtype=float) / 255, 0, 1)#归一化
    loaded_images.append(x)
    return np.stack(loaded_images, axis=0)


def get_img_depth(input: Image) -> Image:
    '''
    param input: rgb Image格式
    outputs shape: (1, 240, 320, 1)
    '''
    inputs = load_images(input)
    outputs = predict(model, inputs)
    img_depth_np = __to_multichannel(outputs[0])
    img_depth_im= Image.fromarray(np.uint8(img_depth_np*255))
    return img_depth_im

