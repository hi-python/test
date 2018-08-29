import os
import numpy as np
import cv2
import tensorflow as tf
import random

# 画像表示用に追加
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#Jupyterでインライン表示するための宣言
%matplotlib inline

# 重み変数
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

# バイアス変数
def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

# 畳み込み
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

# プーリング
def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')


NUM_CLASSES = 2 # 分類するクラス数
IMG_SIZE = 75 # 画像の1辺の長さ

# 画像のあるディレクトリ
train_img_dirs = ['fox', 'racoon']

# 学習画像データ
train_image = []
# 学習データのラベル
train_label = []
# test画像データ
test_image = []
# testデータのラベル
test_label = []

# ここからテスト出力
# filesにはファイル各DIR配下のファイル一覧が1次元配列で格納される
files = os.listdir('C:/Users/hiadachi/python/image-data/' + train_img_dirs[1])
#print(files)

# imgにはファイルが3次元配列（75*75*3)で格納される。[[R,G.B],[R,G.B],[R,G.B],･･･75個] * 75のような形
img = cv2.imread('C:/Users/hiadachi/python/image-data/' + train_img_dirs[1] + '/' + files[0])
print(img.shape)

# 1辺がIMG_SIZEの正方形にリサイズ
img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
print(img.shape)

# 一次元配列に変換
img = img.flatten().astype(np.float32)/255.0
print(img.shape)
# ここまでテスト出力

# train_img_dirsの数（今回だと2回）繰り返す
for i, d in enumerate(train_img_dirs):
    # ./data/以下の各ディレクトリ内のファイル名取得
    files = os.listdir('C:/Users/hiadachi/python/image-data/' + d)
    # それぞれのファイルに対する処理
    for f in files:
        # 画像読み込み
        img = cv2.imread('C:/Users/hiadachi/python/image-data/' + d + '/' + f)
        # 1辺がIMG_SIZEの正方形にリサイズ
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        # 1列にして
        img = img.flatten().astype(np.float32)/255.0
        train_image.append(img)

        # one_hot_vectorを作りラベルとして追加
        # iはtrain_img_dirsの数、今回だと0がfox, 1がothers
        tmp = np.zeros(NUM_CLASSES)
        tmp[i] = 1
        train_label.append(tmp)

# train_image.shape

# numpy配列に変換
# 一次元にした配列数　* 画像数で格納される
train_image = np.asarray(train_image)
train_label = np.asarray(train_label)

COLOR_CHANNELS = 3 # RGB
IMG_PIXELS = IMG_SIZE * IMG_SIZE * COLOR_CHANNELS # 画像のサイズ*RGB

# Placeholderの定義
x = tf.placeholder(tf.float32, shape=[None, IMG_PIXELS])
y_ = tf.placeholder(tf.float32, shape=[None, NUM_CLASSES])

W_conv1 = weight_variable([5, 5, COLOR_CHANNELS, 32])
b_conv1 = bias_variable([32])

# 元の形に戻している（75*75*3)
x_image = tf.reshape(x, [-1, IMG_SIZE, IMG_SIZE, COLOR_CHANNELS])

# convolution層とpool層を適用。
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

print("h_pool1 : ", h_pool1.shape)

# 第２層のconvolutionとPool
# 1層と同様5*5のパッチを動かしていく、ただしinputは第一層の出力結果32に、Otuputは2倍の64にしている
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

print("h_pool2 : ", h_pool2.shape)

# 配列を1次元配列に戻す
# h_pool2は1,19,19,64の配列。1024個の特徴変数があることとする（1024は決め）
# 最終的にはh_fc1に写真数 * 1024配列が出力される
W_fc1 = weight_variable([19 * 19 * 64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 19*19*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

print("h_fc1 : ", h_fc1.shape)

# 過学習を防ぐDropout処理
# keep_prob = 0.5なら半分の特徴量が無くなる
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# readoutレイヤ, softmaxを使用する
W_fc2 = weight_variable([1024, NUM_CLASSES])
b_fc2 = bias_variable([NUM_CLASSES])

y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

# トレーニング方法定義
cross_entropy = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

# 評価関数定義
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

print("end")

#学習データの保存
saver = tf.train.Saver()

# training実行
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    cwd = os.getcwd()
    
    if os.path.exists(cwd+"\\CNN.ckpt.meta"): # 学習データがある場合
        saver.restore(sess, cwd+"\\CNN.ckpt") # データの読み込み
        print("学習データを読み込みました")

        #テスト出力
        print("W_fc2 = ", sess.run(W_fc2[0,0]))
        print("b_fc2 = ", sess.run(b_fc2[0]))
        print("W_fc2 = ", sess.run(W_fc2[1,1]))
        print("b_fc2 = ", sess.run(b_fc2[1]))
               
    # ここからtest実施

    # ./data/以下の各ディレクトリ内のファイル名取得
    files = os.listdir('C:/Users/hiadachi/python/image-data/test')
    # それぞれのファイルに対する処理
    for f, value in enumerate(files):
        # 画像読み込み
        img = cv2.imread('C:/Users/hiadachi/python/image-data/test/' + value)
        # 1辺がIMG_SIZEの正方形にリサイズ
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        # 1列にして
        img = img.flatten().astype(np.float32)/255.0

        test_image.append(img)
        #print("test_image_all=" ,test_image)
        #print("test_image=" ,test_image[f])
                
        p = sess.run(y_conv, feed_dict={x: [test_image[f]], y_: [[0.0] * 2], keep_prob: 1.0})

#        print("ファイル名 : ", value)
#        print(p)
        print(np.argmax(p))

print("end")

    