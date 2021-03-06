from keras.models import Sequential
from keras.layers import Conv2D, Input, BatchNormalization
from keras.callbacks import ModelCheckpoint
from keras.optimizers import SGD, Adam
import numpy
import math
import os
from keras.models import load_model
from PIL import Image

patch_size = 100
input_size = 200
label_size = 200

def setup_session():
    import tensorflow as tf
    from keras.backend import tensorflow_backend
    config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
    session = tf.Session(config=config)
    tensorflow_backend.set_session(session)

def predict2(model, input_file, out_dir, scale = 2.0):
    basename = os.path.basename(input_file)
    filename, ext = os.path.splitext(basename)

    img = Image.open(input_file)
    img = img.convert('RGB')
    img.save('%s/%s_1_org%s' % (out_dir, filename, ext))

    lr_size = tuple([int(x/scale) for x in img.size])
    lr_img = img.resize(lr_size, Image.BICUBIC)
    lr_img.resize(img.size, Image.BICUBIC).save('%s/%s_3_lr%s' % (out_dir, filename, ext))

    lr_img = numpy.asarray(lr_img)
    hr_img = numpy.zeros((img.size[1], img.size[0], 3)) # h<->w exchanged
    print(hr_img.shape)
    print(lr_img.shape)

    h,w,c = lr_img.shape
    eh = h if h % patch_size == 0 else h + patch_size - (h % patch_size) # 240 % 100=40, 240+100-
    ew = w if w % patch_size == 0 else w + patch_size - (w % patch_size)
    print('extend:',eh,ew,c)
    lr_base = numpy.zeros((eh, ew, 3), dtype='uint8')
    lr_base[0:h, 0:w] = lr_img
    lr_img = lr_base
    hr_img = numpy.zeros((int(eh * scale), int(ew * scale), 3)) # h<->w exchanged

    for y in range(0, h, patch_size):
        for x in range(0, w, patch_size):
            patch = lr_img[y:y+patch_size, x:x+patch_size]
            save_as_img('lr',out_dir, patch, y, x)
            patch = patch/255.
            patch = patch.reshape(1, patch.shape[0],patch.shape[1],patch.shape[2])
            res = model.predict(patch, batch_size=1)
            res = res*255.
            res = numpy.clip(res, 0, 255) #important
            res = numpy.uint8(res)
            res = res.reshape(res.shape[1],res.shape[2],res.shape[3])
            save_as_img('hr',out_dir, res, y, x)
            dy = int(y * scale)
            dh = dy + int(patch_size * scale)
            dx = int(x * scale)
            dw = dx + int(patch_size * scale)
            hr_img[dy:dh,dx:dw] = res

    hr_img = numpy.uint8(hr_img)
    hr_img = Image.fromarray(hr_img)
    hr_img = hr_img.convert('RGB')
    h,w,c = numpy.asarray(img).shape
    hr_img = numpy.asarray(hr_img)[0:h,0:w]
    hr_img = Image.fromarray(hr_img)
    hr_img.save('%s/%s_2_hr%s' % (out_dir, filename, ext))

def save_as_img(prefix, out_dir, patch, y, x):
    img = Image.fromarray(patch)
    path = '%s/%s_patch_%d_%d.png' % (out_dir,prefix,y,x)
    img.save(path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("model", help="model file path")
    parser.add_argument("input", help="row res image path")
    parser.add_argument("out_dir", help="output dir")
    args = parser.parse_args()
    print(args)

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    setup_session()
    model = load_model(args.model)

    predict2(model, args.input, args.out_dir)
    print('fin')
