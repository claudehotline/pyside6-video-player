from analyzer.TrackingDetector import TrackingDetector
import cv2
from mmdeploy_python import TextDetector
from mmdeploy_python import TextRecognizer
import numpy as np
from analyzer import device
from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape, load_config

class CarRecognitionDetector(TrackingDetector):

    def __init__(self, model_path1, model_path2, tracking_class=[]):
        super(CarRecognitionDetector, self).__init__(model_path1, model_path2, tracking_class)
        self.car_count_up = []
        self.car_count_down = []

        deploy_config = 'I:/mmdeploy/configs/mmocr/text-recognition/text-recognition_onnxruntime_dynamic.py'
        model_cfg = 'I:/mmocr/configs/textrecog/sar/sar_resnet31_parallel-decoder_5e_st-sub_mj-sub_sa_real.py'
        device = 'cpu'
        backend_model = ['model/ocr/sar/end2end.onnx']
        deploy_cfg, model_cfg = load_config(deploy_config, model_cfg)
        self.task_processor = build_task_processor(model_cfg, deploy_cfg, device)
        self.text_recognizer = self.task_processor.build_backend_model(backend_model)
        self.input_shape = get_input_shape(deploy_cfg)


        self.text_detector = TextDetector(
            'model/ocr/dbnet',
            device,
            0)
        
        # self.text_recognizer = TextRecognizer(
        #     'model/ocr/sar',
        #     device,
        #     0)
    
    def drawbox(self, image, bboxes, line_thickness=None):

        # Plots one bounding box on image img
        tl = line_thickness or round(
            0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, cls_id, track_id) in bboxes:
            # # 截取x1,y1, x2, y2 范围内的图像
            single_car = image[y1:y2,x1:x2]
            
            # do model inference
            bboxes = self.text_detector(single_car)
            # draw detected bbox into the input image
            pts = []
            if len(bboxes) > 0:
                pts = ((bboxes[:, 0:8] + 0.5).reshape(len(bboxes), -1,
                                                    2).astype(int))
            for pt in pts:
                # cv2.rectangle(single_car, pt[0], pt[2], color, -1, cv2.LINE_AA)
                x1 = np.min(pt[:, 0])
                x2 = np.max(pt[:, 0])
                y1 = np.min(pt[:, 1])
                y2 = np.max(pt[:, 1])
                license = single_car[y1:y2,x1:x2]
                cv2.imwrite('license.jpg', license)
                model_inputs, _ = self.task_processor.create_input(license, self.input_shape)
                result = self.text_recognizer.test_step(model_inputs)
                print(result[0].pred_text.item)