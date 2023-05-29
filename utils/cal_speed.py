import math

carwidth = 1.7 #1.7m
def Speed(location_one, location_two, frame_number):
  #location_one 形式为（t,l,w,h）->主要指的是前10帧的目标的像素坐标 
  #location_two 形式为 (t,l,w,h) ->主要指的是本帧的目标的像素坐标
	d_pixels = math.sqrt(math.pow(location_two[0] - location_one[0], 2) + math.pow(location_two[1] - location_one[1], 2)) #像素级位移 这里就是进行了个勾股定理
	print('d_pixels = ', d_pixels)
	if location_two[2] > location_two[3]: #这里是我认为如果w>h的话 那么车辆有可能是横向行驶的，因为我的映射是利用车辆的宽度映射 像素级车辆宽度与现实世界车辆宽度的比值
		ppm = location_two[3] / carwidth
	else:  #w<=h 则相反
		ppm = location_two[2] / carwidth
		
	d_meters = d_pixels / ppm #进行转换
	time = 1/25 * frame_number
	
	# if time == 0:
  #   return 0
  # else:
	#   return d_meters / time * 3.6 #返回速度值