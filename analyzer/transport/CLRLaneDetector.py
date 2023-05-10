from PIL import Image
import onnxruntime
import numpy as np
import scipy
import cv2
from scipy.interpolate import InterpolatedUnivariateSpline


COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 255, 0),
    (255, 128, 0),
    (128, 0, 255),
    (255, 0, 128),
    (0, 128, 255),
    (0, 255, 128),
    (128, 255, 255),
    (255, 128, 255),
    (255, 255, 128),
    (60, 180, 0),
    (180, 60, 0),
    (0, 60, 180),
    (0, 180, 60),
    (60, 0, 180),
    (180, 0, 60),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 255, 0),
    (255, 128, 0),
    (128, 0, 255),
]

class Lane:
    def __init__(self, points=None, invalid_value=-2., metadata=None):
        super(Lane, self).__init__()
        self.curr_iter = 0
        self.points = points
        self.invalid_value = invalid_value
        self.function = InterpolatedUnivariateSpline(points[:, 1],
                                                     points[:, 0],
                                                     k=min(3,
                                                           len(points) - 1))
        self.min_y = points[:, 1].min() - 0.01
        self.max_y = points[:, 1].max() + 0.01

        self.metadata = metadata or {}

        self.sample_y = range(710, 150, -10)
        # self.sample_y = range(580, 150, -10)
        self.ori_img_w = 1280
        self.ori_img_h = 720
        # self.ori_img_w = 1640
        # self.ori_img_h = 590

    def __repr__(self):
        return '[Lane]\n' + str(self.points) + '\n[/Lane]'

    def __call__(self, lane_ys):
        lane_xs = self.function(lane_ys)

        lane_xs[(lane_ys < self.min_y) |
                (lane_ys > self.max_y)] = self.invalid_value
        return lane_xs

    def to_array(self):
        sample_y = self.sample_y
        img_w, img_h = self.ori_img_w, self.ori_img_h
        ys = np.array(sample_y) / float(img_h)
        xs = self(ys)
        valid_mask = (xs >= 0) & (xs < 1)
        lane_xs = xs[valid_mask] * img_w
        lane_ys = ys[valid_mask] * img_h
        lane = np.concatenate((lane_xs.reshape(-1, 1), lane_ys.reshape(-1, 1)),
                              axis=1)
        return lane

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_iter < len(self.points):
            self.curr_iter += 1
            return self.points[self.curr_iter - 1]
        self.curr_iter = 0
        raise StopIteration

class CLRLaneDetector:

    def __init__(self, model_path):
        self.ort_session = onnxruntime.InferenceSession(model_path)
        self.conf_threshold = 0.4
        self.nms_thres = 50
        self.max_lanes = 5
        self.sample_points = 36
        self.num_points = 72
        self.n_offsets = 72
        self.n_strips = 71
        self.img_w = 1280
        self.img_h = 720
        self.ori_img_w = 1280
        self.ori_img_h = 720
        self.cut_height = 280

        self.input_width = 800
        self.input_height = 320

        self.sample_x_indexs = (np.linspace(0, 1, self.sample_points) * self.n_strips)
        self.prior_feat_ys = np.flip((1 - self.sample_x_indexs / self.n_strips))
        self.prior_ys = np.linspace(1,0, self.n_offsets)
    def detect(self, frame):
        vis = self.forward(frame)

        return vis  
    
    def softmax(self, x, axis=None):
        x = x - x.max(axis=axis, keepdims=True)
        y = np.exp(x)
        return y / y.sum(axis=axis, keepdims=True)

    def predictions_to_pred(self, predictions):
        # print('predictions', predictions.shape)
        lanes = []
        for lane in predictions:
            lane_xs = lane[6:]  # normalized value
            # print('xs length: ', len(lane_xs))
            # 3 车道线
            start = min(max(0, int(round(lane[2].item() * self.n_strips))),
                        self.n_strips)
            # print('start', start)
            length = int(round(lane[5].item()))
            end = start + length - 1
            end = min(end, len(self.prior_ys) - 1)
            # print('end', end)
            # end = label_end
            # if the prediction does not start at the bottom of the image,
            # extend its prediction until the x is outside the image
            mask = ~((((lane_xs[:start] >= 0.) & (lane_xs[:start] <= 1.)
                       )[::-1].cumprod()[::-1]).astype(bool))

            lane_xs[end + 1:] = -2
            lane_xs[:start][mask] = -2
            lane_ys = self.prior_ys[lane_xs >= 0]
            lane_xs = lane_xs[lane_xs >= 0]

            lane_xs = np.double(lane_xs)
            lane_xs = np.flip(lane_xs, axis=0)
            lane_ys = np.flip(lane_ys, axis=0)
            lane_ys = (lane_ys * (self.ori_img_h - self.cut_height) +
                       self.cut_height) / self.ori_img_h
            if len(lane_xs) <= 1:
                continue

            points = np.stack(
                (lane_xs.reshape(-1, 1), lane_ys.reshape(-1, 1)),
                axis=1).squeeze(2)

            lane = Lane(points=points,
                        metadata={
                            'start_x': lane[3],
                            'start_y': lane[2],
                            'conf': lane[1]
                        })
            lanes.append(lane)
            print('lanes :', lanes)
        return lanes

    def get_lanes(self, output, as_lanes=True):
        '''
        Convert model output to lanes.
        '''
        decoded = []
        for predictions in output:
            # filter out the conf lower than conf threshold
            # print(self.softmax(predictions[:, :2], 1))
            scores = self.softmax(predictions[:, :2], 1)[:, 1]

            keep_inds = scores >= self.conf_threshold
            predictions = predictions[keep_inds]
            scores = scores[keep_inds]

            if predictions.shape[0] == 0:
                decoded.append([])
                continue
            #(11, 78)
            nms_predictions = predictions
            nms_predictions = np.concatenate(
                [nms_predictions[..., :4], nms_predictions[..., 5:]], axis=-1)
    
            nms_predictions[..., 4] = nms_predictions[..., 4] * self.n_strips
            nms_predictions[..., 5:] = nms_predictions[..., 5:] * (self.img_w - 1)
            # print(nms_predictions[..., 5:][1])

            # 将predictions的第6列至最后一列的值乘以img_w-1
            predictions[:, 6:] = predictions[..., 6:] * (self.img_w - 1)
            # print(predictions[..., 6:][1])

            # keep = keep[:num_to_keep].cpu().numpy()
            # predictions = predictions[keep]
            predictions = np.array(self.nms(predictions, scores, 0.4, self.max_lanes))
            predictions[:, 6:] = predictions[:, 6:] / (self.img_w - 1)
            # predictions = predictions
            
            if predictions.shape[0] == 0:
                decoded.append([])
                continue

            predictions[:, 5] = np.round(predictions[:, 5] * self.n_strips)
            pred = self.predictions_to_pred(predictions)
            decoded.append(pred)
            
        return decoded
    
    def imshow_lanes(self, img, lanes, show=False, out_file=None, width=4):
        lanes = [lane.to_array() for lane in lanes]
        
        lanes_xys = []
        for _, lane in enumerate(lanes):
            xys = []
            for x, y in lane:
                if x <= 0 or y <= 0:
                    continue
                x, y = int(x), int(y)
                xys.append((x, y))
            lanes_xys.append(xys)
        lanes_xys.sort(key=lambda xys : xys[0][0])

        for idx, xys in enumerate(lanes_xys):
            for i in range(1, len(xys)):
                cv2.line(img, xys[i - 1], xys[i], COLORS[idx], thickness=width)
        return img
   
    def forward(self, img):
        img_ = img.copy()
        h, w = img.shape[:2]
        img = img[self.cut_height:, :, :]
        img = cv2.resize(img, (self.input_width, self.input_height), cv2.INTER_CUBIC)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 

        img = img.astype(np.float32) / 255.0 

        img = np.transpose(np.float32(img[:,:,:,np.newaxis]), (3,2,0,1))

        ort_inputs = {self.ort_session.get_inputs()[0].name: img}
        ort_outs = self.ort_session.run(None, ort_inputs)
        output = ort_outs[0]
        
        output = self.get_lanes(output)

        res = self.imshow_lanes(img_, output[0])
        return res
    
    def distance(self, det1, det2):
        e = 15
        do = []
        du = []
        for i in range(6, len(det1)):
            do.append(min(det1[i] + e, det2[i] + e) - max(det1[i] - e, det2[i] - e))
            du.append(max(det1[i] + e, det2[i] + e) - min(det1[i] - e, det2[i] - e))
        distance = np.sum(do) / np.sum(du)

        return distance

    def nms(self, detections, scores, nms_thres, top_k):
        # 使用scores对detections进行降序排序
        indices = np.argsort(scores)[::-1]
        detections = detections[indices]

        result = []
        
        while detections.size > 0:
            # 保留第一个detection
            result.append(detections[0])
            if len(result) == top_k:
                return result
            # 计算第一个detection与其他detection的距离
            ious = np.array([self.distance(detections[0], detections[i]) for i in range(1, detections.shape[0])])
            # print(ious)
            # 将iou大于nms_thres的detection去除
            keep_indices = np.where(ious <= nms_thres)[0]
            # print(keep_indices)
            detections = detections[keep_indices + 1]
        return result