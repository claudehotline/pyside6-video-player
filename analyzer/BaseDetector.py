# from utils.tracker import update_tracker


# class baseDet(object):

#     def __init__(self):
#         self.frameCounter = 0

#     def detect(self, im):

#         retDict = {
#             'frame': None,
#             'faces': None,
#             'list_of_ids': None,
#             'face_bboxes': []
#         }
#         self.frameCounter += 1

#         im, faces, face_bboxes = update_tracker(self, im)

#         retDict['frame'] = im
#         retDict['faces'] = faces
#         retDict['face_bboxes'] = face_bboxes

#         return retDict['frame']

#     def getbox(self):
#         raise EOFError("Undefined model type.")
