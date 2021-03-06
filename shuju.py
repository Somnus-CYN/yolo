import argparse
import json
import matplotlib.pyplot as plt
import skimage.io as io
import cv2
from labelme import utils
import numpy as np
import glob
import PIL.Image


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class labelme2coco(object):
    def __init__(self, labelme_json=[], save_json_path='./tran.json'):
        '''
        :param labelme_json: 所有labelme的json文件路径组成的列表
        :param save_json_path: json保存位置
        '''
        self.labelme_json = labelme_json
        self.save_json_path = save_json_path
        self.images = []
        self.categories = []
        self.annotations = []
        # self.data_coco = {}
        self.label = []
        self.annID = 1
        self.height = 0
        self.width = 0

        self.save_json()

    def data_transfer(self):

        for num, json_file in enumerate(self.labelme_json):
            with open(json_file, 'r') as fp:
                data = json.load(fp)  # 加载json文件
                self.images.append(self.image(data, num))
                for shapes in data['shapes']:
                    label = shapes['label']
                    if label not in self.label:
                        self.categories.append(self.categorie(label))
                        self.label.append(label)
                    points = shapes['points']  # 这里的point是用rectangle标注得到的，只有两个点，需要转成四个点
                    # points.append([points[0][0],points[1][1]])
                    # points.append([points[1][0],points[0][1]])

                    self.annotations.append(self.annotation(points, label, num))
                    self.annID += 1

    def image(self, data, num):
        image = {}
        img = utils.img_b64_to_arr(data['imageData'])  # 解析原图片数据
        # img=io.imread(data['imagePath']) # 通过图片路径打开图片
        # img = cv2.imread(data['imagePath'], 0)
        height, width = img.shape[:2]
        img = None
        image['height'] = height
        image['width'] = width
        image['id'] = num + 1
        image['file_name'] = data['imagePath'].split('/')[-1]

        self.height = height
        self.width = width

        return image

    def categorie(self, label):
        categorie = {}
        categorie['supercategory'] = 'person'
        categorie['id'] = len(self.label) + 1  # 0 默认为背景
        categorie['name'] = label

        categorie['keypoints'] = ["head", "left_eye0", "left_eye1", "right_eye0", "right_eye1", "nose", "left_mouse",
                                  "right_mouse",
                                  "left_shoulder0", "left_shoulder1", "left_shoulder2",
                                  "left_elbow0", "left_elbow1", "left_elbow2", "left_elbow3",
                                  "left_wrist0", "left_wrist1",
                                  "left_hand",
                                  "left_wrist2", "left_wrist3",
                                  "left_elbow4", "left_elbow5", "left_elbow6",
                                  "left_chest0", "left_chest1", "left_chest2", "left_chest3", "left_chest4",
                                  "left_hip0", "left_hip1", "left_hip2",
                                  "left_knee0", "left_knee1",
                                  "left_ankle0", "left_ankle1",
                                  "left_knee2", "left_knee3",
                                  "left_hip3", "left_hip4", "left_hip5",
                                  "right_hip0", "right_hip1",
                                  "right_knee0", "right_knee1",
                                  "right_ankle0", "right_ankle1",
                                  "right_knee2", "right_knee3",
                                  "right_hip2", "right_hip3", "right_hip4",
                                  "right_chest0", "right_chest1", "right_chest2", "right_chest3", "right_chest4",
                                  "right_elbow4", "right_elbow5", "right_elbow6",
                                  "right_wrist2", "right_wrist3",
                                  "right_hand",
                                  "right_wrist0", "right_wrist1",
                                  "right_elbow0", "right_elbow1", "right_elbow2", "right_elbow3",
                                  "right_shoulder0", "right_shoulder1", "right_shoulder2"]

        categorie['skeleton'] = [[1, 2], [2, 3], [3, 4],
                                 [4, 5], [5, 6], [6, 7], [7, 8],
                                 [8, 9], [9, 10], [10, 11], [11, 12],
                                 [12, 13], [13, 14], [14, 15], [15, 16],
                                 [16, 17], [17, 18], [18, 19], [19, 20],
                                 [20, 21], [21, 22], [22, 23], [23, 24],
                                 [24, 25], [25, 26], [26, 27], [27, 28],
                                 [28, 29], [29, 30], [30, 31], [31, 32],
                                 [32, 33], [33, 34], [34, 35], [35, 36],
                                 [36, 37], [37, 38], [38, 39], [39, 40],
                                 [40, 41], [41, 42], [42, 43], [43, 44],
                                 [44, 45], [45, 46], [46, 47], [47, 48],
                                 [48, 49], [49, 50], [50, 51], [51, 52],
                                 [52, 53], [53, 54], [54, 55], [55, 56],
                                 [56, 57], [57, 58], [58, 59], [59, 60],
                                 [60, 61], [61, 62], [62, 63], [63, 64],
                                 [64, 65], [65, 66], [66, 67], [67, 68],
                                 [68, 69], [69, 70], [70, 71]]
        return categorie

    def annotation(self, points, label, num):
        annotation = {}
        annotation['segmentation'] = [list(np.asarray(points).flatten())]
        annotation['iscrowd'] = 0
        annotation['image_id'] = num + 1
        # annotation['bbox'] = str(self.getbbox(points)) # 使用list保存json文件时报错（不知道为什么）
        # list(map(int,a[1:-1].split(','))) a=annotation['bbox'] 使用该方式转成list
        annotation['bbox'] = list(map(float, self.getbbox(points)))
        annotation['area'] = annotation['bbox'][2] * annotation['bbox'][3]
        # annotation['category_id'] = self.getcatid(label)
        annotation['category_id'] = self.getcatid(label)  # 注意，源代码默认为1
        annotation['id'] = self.annID

        annotation['keypoints'] = []
        for p in points:
            annotation['keypoints'].extend([p[0], p[1], 2])
        annotation['num_keypoints'] = len(points)
        return annotation

    def getcatid(self, label):
        for categorie in self.categories:
            if label == categorie['name']:
                return categorie['id']
        return 1

    def getbbox(self, points):
        # img = np.zeros([self.height,self.width],np.uint8)
        # cv2.polylines(img, [np.asarray(points)], True, 1, lineType=cv2.LINE_AA)  # 画边界线
        # cv2.fillPoly(img, [np.asarray(points)], 1)  # 画多边形 内部像素值为1
        polygons = points

        mask = self.polygons_to_mask([self.height, self.width], polygons)
        return self.mask2box(mask)

    def mask2box(self, mask):
        '''从mask反算出其边框
        mask：[h,w]  0、1组成的图片
        1对应对象，只需计算1对应的行列号（左上角行列号，右下角行列号，就可以算出其边框）
        '''
        # np.where(mask==1)
        index = np.argwhere(mask == 1)
        rows = index[:, 0]
        clos = index[:, 1]
        # 解析左上角行列号
        left_top_r = np.min(rows)  # y
        left_top_c = np.min(clos)  # x

        # 解析右下角行列号
        right_bottom_r = np.max(rows)
        right_bottom_c = np.max(clos)

        # return [(left_top_r,left_top_c),(right_bottom_r,right_bottom_c)]
        # return [(left_top_c, left_top_r), (right_bottom_c, right_bottom_r)]
        # return [left_top_c, left_top_r, right_bottom_c, right_bottom_r]  # [x1,y1,x2,y2]
        return [left_top_c, left_top_r, right_bottom_c - left_top_c,
                right_bottom_r - left_top_r]  # [x1,y1,w,h] 对应COCO的bbox格式

    def polygons_to_mask(self, img_shape, polygons):
        mask = np.zeros(img_shape, dtype=np.uint8)
        mask = PIL.Image.fromarray(mask)
        xy = list(map(tuple, polygons))
        PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
        mask = np.array(mask, dtype=bool)
        return mask

    def data2coco(self):
        data_coco = {}
        data_coco['images'] = self.images
        data_coco['categories'] = self.categories
        data_coco['annotations'] = self.annotations
        return data_coco

    def save_json(self):
        self.data_transfer()
        self.data_coco = self.data2coco()
        # 保存json文件
        json.dump(self.data_coco, open(self.save_json_path, 'w'), indent=4, cls=MyEncoder)  # indent=4 更加美观显示


labelme_json = glob.glob('E:\水果\菠萝蜜')
# labelme_json=['./Annotations/*.json']


labelme2coco(labelme_json, 'E:\水果\菠萝蜜')
