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


class OpencvLaneDetector:

    def __init__(self):
      self.M = np.array([
        [-6.41880794e-01, -1.24369760e+00, 9.24683130e+02],
        [ 3.76135112e-16, -2.37041692e+00,  1.19943096e+03],
        [ 9.07563501e-19, -2.36741748e-03,  1.00000000e+00]
      ])
  
  # M = np.array([
  #     [-6.95903151e-01, -1.49139920e+00,  1.06312034e+03],
  #     [-4.10051714e-16, -1.90491462e+00,  8.40067345e+02],
  #     [ 0.00000000e+00, -2.41410335e-03,  1.00000000e+00]
  #   ]
  # )
      self.M_inverse = np.array([
              [ 3.08333333e-01, -6.21359062e-01,  4.60166667e+02],
              [ 1.68598765e-16, -4.21866715e-01,  5.06000000e+02],
              [ 2.27219166e-19, -9.98734635e-04,  1.00000000e+00]
            ])
  
  # M_inverse = np.array([
  #     [ 9.28571429e-02, -8.10994201e-01,  5.82571429e+02],
  #     [ 1.46749489e-16, -5.24957912e-01,  4.41000000e+02],
  #     [ 2.11164675e-19, -1.26730266e-03,  1.00000000e+00]
  #   ]
  # )

    def detect(self, frame):
      frame_gray = self.pipeline(frame, s_thresh=(60, 255), sx_thresh=(40, 200))
      transform_frame = self.img_perspect_transform(frame_gray, self.M)
      left_fit, right_fit = self.cal_line_param(transform_frame)
      out_frame = self.fill_lane_poly(transform_frame, left_fit, right_fit)
      transform_frame_inverse = self.img_perspect_transform(out_frame, self.M_inverse)
      # 将图像转换为RGB颜色空间
      transform_frame_inverse = cv2.addWeighted(frame, 1, transform_frame_inverse, 0.3, 0)

      return transform_frame_inverse
    
    # ⻋道线提取代码
    def pipeline(self, img, s_thresh=(170, 255), sx_thresh=(40, 200)):
      img = np.copy(img)
      #1.将图像转换为HLS⾊彩空间，并分离各个通道
      hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(np.float)
      h_channel = hls[:, :, 0]
      l_channel = hls[:, :, 1]
      s_channel = hls[:, :, 2]
      #2.利⽤sobel计算x⽅向的梯度
      sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0)
      abs_sobelx = np.absolute(sobelx) 
      # 将导数转换为8bit整数
      scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))
      sxbinary = np.zeros_like(scaled_sobel)
      sxbinary[(scaled_sobel >= sx_thresh[0]) & (scaled_sobel <= sx_thresh[1])]
      # 3.对s通道进⾏阈值处理
      s_binary = np.zeros_like(s_channel)
      s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 1
      # 4. 将边缘检测的结果和颜⾊空间阈值的结果合并，并结合l通道的取值，确定⻋道提取的⼆值图结
      color_binary = np.zeros_like(sxbinary)
      color_binary[((sxbinary == 1) | (s_binary == 1)) & (l_channel > 100)] = 1
      return color_binary

    def cal_perspective_params(self, img, points):
      offset_x = 220
      offset_y = 0
      img_size = (img.shape[1], img.shape[0])
      src = np.float32(points)
      # 俯视图中四点的位置
      
      dst = np.float32([
        [offset_x, offset_y], 
        [img_size[0] - offset_x, offset_y],
        [offset_x, img_size[1] - offset_y], 
        [img_size[0] - offset_x, img_size[1] - offset_y]
      ])

      # 从原始图像转换为俯视图的透视变换的参数矩阵
      M = cv2.getPerspectiveTransform(src, dst)
      # 从俯视图转换为原始图像的透视变换参数矩阵
      M_inverse = cv2.getPerspectiveTransform(dst, src)
      return M, M_inverse


    def img_perspect_transform(self, img, M):
      img_size = (img.shape[1], img.shape[0])
      return cv2.warpPerspective(img, M, img_size)


    def cal_line_param(self, binary_warped):
      # 1.确定左右⻋道线的位置
      # 统计直⽅图
      histogram = np.sum(binary_warped[:, :], axis=0)
      # 在统计结果中找到左右最⼤的点的位置，作为左右⻋道检测的开始点
      # 将统计结果⼀分为⼆，划分为左右两个部分，分别定位峰值位置，即为两条⻋道的搜索位置
      midpoint = np.int(histogram.shape[0] / 2)
      leftx_base = np.argmax(histogram[:midpoint])
      rightx_base = np.argmax(histogram[midpoint:]) + midpoint
      # 2.滑动窗⼝检测⻋道线
      # 设置滑动窗⼝的数量，计算每⼀个窗⼝的⾼度
      nwindows = 9
      window_height = np.int(binary_warped.shape[0] / nwindows)
      # 获取图像中不为0的点
      nonzero = binary_warped.nonzero()
      nonzeroy = np.array(nonzero[0])
      nonzerox = np.array(nonzero[1])
      # ⻋道检测的当前位置
      leftx_current = leftx_base
      rightx_current = rightx_base
      # 设置x的检测范围，滑动窗⼝的宽度的⼀半，⼿动指定
      margin = 100
      # 设置最⼩像素点，阈值⽤于统计滑动窗⼝区域内的⾮零像素个数，⼩于50的窗⼝不对x的中⼼值进⾏
      minpix = 50
      # ⽤来记录搜索窗⼝中⾮零点在nonzeroy和nonzerox中的索引
      left_lane_inds = []
      right_lane_inds = []
      # 遍历该副图像中的每⼀个窗⼝
      for window in range(nwindows):
        # 设置窗⼝的y的检测范围，因为图像是（⾏列）,shape[0]表示y⽅向的结果，上⾯是0
        win_y_low = binary_warped.shape[0] - (window + 1) * window_height
        win_y_high = binary_warped.shape[0] - window * window_height
        # 左⻋道x的范围
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        # 右⻋道x的范围
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        # 确定⾮零点的位置x,y是否在搜索窗⼝中，将在搜索窗⼝内的x,y的索引存⼊left_lane_ind
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high))
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
          (nonzerox >= win_xright_low) & (nonzerox < win_xright_high))
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        # 如果获取的点的个数⼤于最⼩个数，则利⽤其更新滑动窗⼝在x轴的位置
        if np.sum(good_left_inds) > minpix:
          leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if np.sum(good_right_inds) > minpix:
          rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
      
      # 将left_lane_inds 中的数组进行 logical_or 操作，将⾮零点的索引取出
      # 创建一个全为Falsed的数组，数组的⻓度为nonzerox的⻓度
      left_lane_inds1 = np.zeros_like(nonzerox)
      right_lane_inds1 = np.zeros_like(nonzerox)
      for i in range(len(left_lane_inds)):
        left_lane_inds1 = np.logical_or(left_lane_inds1, left_lane_inds[i])
      for i in range(len(right_lane_inds)):
        right_lane_inds1 = np.logical_or(right_lane_inds1, right_lane_inds[i])

      # 获取检测出的左右⻋道点在图像中的位置
      leftx = nonzerox[left_lane_inds1]
      lefty = nonzeroy[left_lane_inds1]
      rightx = nonzerox[right_lane_inds1]
      righty = nonzeroy[right_lane_inds1]

      # 3.⽤曲线拟合检测出的点,⼆次多项式拟合，返回的结果是系数
      left_fit = np.polyfit(lefty, leftx, 2)
      right_fit = np.polyfit(righty, rightx, 2)
      return left_fit, right_fit

    def fill_lane_poly(self, img, left_fit, right_fit):
      # 获取图像的⾏数
      y_max = img.shape[0]
      # 设置输出图像的⼤⼩，并将⽩⾊位置设为255
      out_img = np.dstack((img, img, img)) * 255
      # 在拟合曲线中获取左右⻋道线的像素位置
      left_points = [[left_fit[0] * y ** 2 + left_fit[1] * y + left_fit[2], y] for y in range(y_max)]
      right_points = [[right_fit[0] * y ** 2 + right_fit[1] * y + right_fit[2], y] for y in range(y_max -1, -1, -1)]
      # 将左右⻋道的像素点进⾏合并
      line_points = np.vstack((left_points, right_points))
      # 根据左右⻋道线的像素位置绘制多边形
      cv2.fillPoly(out_img, np.int_([line_points]), (0, 255, 0))
      return out_img