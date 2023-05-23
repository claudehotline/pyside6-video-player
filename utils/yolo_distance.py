# foc = 1810.0        # 镜头焦距
foc = 500
real_hight_person = 64.96   # 行人高度
real_hight_car = 59.08      # 轿车高度

# 自定义函数，单目测距
def detect_distance_person(h):
    dis_inch = (real_hight_person * foc) / (h - 2)
    dis_cm = dis_inch * 2.54
    dis_cm = int(dis_cm)
    dis_m = dis_cm/100
    return dis_m

def detect_distance_car(h):
    dis_inch = (real_hight_car * foc) / (h - 2)
    dis_cm = dis_inch * 2.54
    dis_cm = int(dis_cm)
    dis_m = dis_cm/100
    return dis_m
