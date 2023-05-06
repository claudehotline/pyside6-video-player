import torch
import torchvision.transforms as transforms
from torch.onnx import export
from PIL import Image
import onnx
import onnxruntime
import numpy as np
import scipy
import cv2
from constant.constant import culane_row_anchor
from analyzer import device
from inferencer.inferener import inferencer


class LaneDetector:

    def __init__(self):
        self.canny_low = 50
        self.canny_high = 150

        self.hough_rho = 2
        self.hough_theta = np.pi / 180
        self.hough_threshold = 15
        self.hough_min_line_length = 40
        self.hough_max_line_gap = 20

    def detect(self, frame):
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        canny_image = cv2.Canny(gray, self.canny_low, self.canny_high)

        cv2.imwrite('canny.jpg', canny_image)

        # left_bottom = [0, canny_image.shape[0]]
        left_bottom = [0, 719]
        # right_bottom = [canny_image.shape[1], canny_image.shape[0]]
        right_bottom = [1279, 595]
        # apex = [canny_image .shape[1]/2, 310]
        apex = [610, 465]
        vertices = np.array([left_bottom, right_bottom, apex], dtype=np.int32)
        roi_image = self.region_of_interest(canny_image, vertices)

        cv2.imwrite('roi.jpg', roi_image)

        lines = cv2.HoughLinesP(roi_image, self.hough_rho, self.hough_theta, self.hough_threshold, np.array([]),
                            self.hough_min_line_length, self.hough_max_line_gap)
        
        line_image = np.copy(frame) # 复制一份原图，将线段绘制在这幅图上
        # print("frame.shape = ", frame.shape)
        # print('lines = ', lines)
        self.draw_lines(line_image, lines, [255, 0, 0], 6)

        return line_image  
    
    def region_of_interest(self, img, vertices):
      #定义一个和输入图像同样大小的全黑图像mask，这个mask也称掩膜
      #掩膜的介绍，可参考：https://www.cnblogs.com/skyfsm/p/6894685.html
      mask = np.zeros_like(img)   
  
      #根据输入图像的通道数，忽略的像素点是多通道的白色，还是单通道的白色
      if len(img.shape) > 2:
          channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
          ignore_mask_color = (255,) * channel_count
      else:
          ignore_mask_color = 255


      #[vertices]中的点组成了多边形，将在多边形内的mask像素点保留，
      cv2.fillPoly(mask, [vertices], ignore_mask_color)
  
      #与mask做"与"操作，即仅留下多边形部分的图像
      masked_image = cv2.bitwise_and(img, mask)

      return masked_image
    
    def draw_lines(self, img, lines, color=[255, 0, 0], thickness=2):
      left_lines_x = []
      left_lines_y = []
      right_lines_x = []
      right_lines_y = []
      line_y_max = 0
      line_y_min = 999

      for line in lines:
          for x1,y1,x2,y2 in line:
              if y1 > line_y_max:
                  line_y_max = y1
              if y2 > line_y_max:
                  line_y_max = y2
              if y1 < line_y_min:
                  line_y_min = y1
              if y2 < line_y_min:
                  line_y_min = y2
              k = (y2 - y1)/(x2 - x1)
              if k < -0.3:
                  left_lines_x.append(x1)
                  left_lines_y.append(y1)
                  left_lines_x.append(x2)
                  left_lines_y.append(y2)
              elif k > 0.3:
                  right_lines_x.append(x1)
                  right_lines_y.append(y1)
                  right_lines_x.append(x2)
                  right_lines_y.append(y2)
      #最小二乘直线拟合
      if(len(left_lines_x) > 0 and len(left_lines_y)) > 0:
        left_line_k, left_line_b = np.polyfit(left_lines_x, left_lines_y, 1)
        cv2.line(img,
              (int((line_y_max - left_line_b)/left_line_k), line_y_max),
              (int((line_y_min - left_line_b)/left_line_k), line_y_min),
              color, thickness)
      if(len(right_lines_x) > 0 and len(right_lines_y)) > 0:
        right_line_k, right_line_b = np.polyfit(right_lines_x, right_lines_y, 1)
        cv2.line(img,
              (int((line_y_max - right_line_b)/right_line_k), line_y_max),
              (int((line_y_min - right_line_b)/right_line_k), line_y_min),
                color, thickness)