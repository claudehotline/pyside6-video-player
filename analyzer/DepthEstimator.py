import cv2
import os
import json
import numpy as np
import PIL.Image as pil
import matplotlib as mpl
import matplotlib.cm as cm

import torch
from torchvision import transforms

from utils.manydepth import networks
from utils.manydepth.layers import transformation_from_parameters

class DepthEstimator:
    
    def __init__(self, model_path):
        self.prve_frame = None
        self.frame_num = 0

        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

        self.encoder_dict = torch.load(os.path.join(model_path, 'encoder.pth'), map_location=device)
        self.encoder = networks.ResnetEncoderMatching(18, False,
                                        input_width=self.encoder_dict['width'],
                                        input_height=self.encoder_dict['height'],
                                        adaptive_bins=True,
                                        min_depth_bin=self.encoder_dict['min_depth_bin'],
                                        max_depth_bin=self.encoder_dict['max_depth_bin'],
                                        depth_binning='linear',
                                        num_depth_bins=96)
        filtered_dict_enc = {k: v for k, v in self.encoder_dict.items() if k in self.encoder.state_dict()}
        self.encoder.load_state_dict(filtered_dict_enc)

        print("   Loading pretrained decoder")

        self.depth_decoder = networks.DepthDecoder(num_ch_enc=self.encoder.num_ch_enc, scales=range(4))

        loaded_dict = torch.load(os.path.join(model_path, "depth.pth"), map_location=device)
        self.depth_decoder.load_state_dict(loaded_dict)

        print("   Loading pose network")
        self.pose_enc_dict = torch.load(os.path.join(model_path, "pose_encoder.pth"),
                                  map_location=device)
        self.pose_dec_dict = torch.load(os.path.join(model_path, "pose.pth"), map_location=device)

        self.pose_enc = networks.ResnetEncoder(18, False, num_input_images=2)
        self.pose_dec = networks.PoseDecoder(self.pose_enc.num_ch_enc, num_input_features=1,
                                        num_frames_to_predict_for=2)

        self.pose_enc.load_state_dict(self.pose_enc_dict, strict=True)
        self.pose_dec.load_state_dict(self.pose_dec_dict, strict=True)

        # Setting states of networks
        self.encoder.eval()
        self.depth_decoder.eval()
        self.pose_enc.eval()
        self.pose_dec.eval()
        if torch.cuda.is_available():
            self.encoder.cuda()
            self.depth_decoder.cuda()
            self.pose_enc.cuda()
            self.pose_dec.cuda()

    def load_and_preprocess_image(self, image, resize_width, resize_height):
        image = pil.fromarray(image).convert('RGB')
        original_width, original_height = image.size
        image = image.resize((resize_width, resize_height), pil.LANCZOS)
        image = transforms.ToTensor()(image).unsqueeze(0)
        if torch.cuda.is_available():
            return image.cuda(), (original_height, original_width)
        return image, (original_height, original_width)


    def load_and_preprocess_intrinsics(self, intrinsics_path, resize_width, resize_height):
        K = np.eye(4)
        with open(intrinsics_path, 'r') as f:
            K[:3, :3] = np.array(json.load(f))

        # Convert normalised intrinsics to 1/4 size unnormalised intrinsics.
        # (The cost volume construction expects the intrinsics corresponding to 1/4 size images)
        K[0, :] *= resize_width // 4
        K[1, :] *= resize_height // 4

        invK = torch.Tensor(np.linalg.pinv(K)).unsqueeze(0)
        K = torch.Tensor(K).unsqueeze(0)

        if torch.cuda.is_available():
            return K.cuda(), invK.cuda()
        return K, invK


    def detect(self, current_frame):
        
        if self.frame_num != 0:
            # Load input data
            input_image, original_size = self.load_and_preprocess_image(current_frame,
                                                                  resize_width=self.encoder_dict['width'],
                                                                  resize_height=self.encoder_dict['height'])

            source_image, _ = self.load_and_preprocess_image(self.prve_frame,
                                                        resize_width=self.encoder_dict['width'],
                                                        resize_height=self.encoder_dict['height'])

            K, invK = self.load_and_preprocess_intrinsics('model/depth/manydepth/KITTI_MR/test_sequence_intrinsics.json',
                                                    resize_width=self.encoder_dict['width'],
                                                    resize_height=self.encoder_dict['height'])

            with torch.no_grad():

                # Estimate poses
                pose_inputs = [source_image, input_image]
                pose_inputs = [self.pose_enc(torch.cat(pose_inputs, 1))]
                axisangle, translation = self.pose_dec(pose_inputs)
                pose = transformation_from_parameters(axisangle[:, 0], translation[:, 0], invert=True)

                # Estimate depth
                output, lowest_cost, _ = self.encoder(current_image=input_image,
                                                lookup_images=source_image.unsqueeze(1),
                                                poses=pose.unsqueeze(1),
                                                K=K,
                                                invK=invK,
                                                min_depth_bin=self.encoder_dict['min_depth_bin'],
                                                max_depth_bin=self.encoder_dict['max_depth_bin'])

                output = self.depth_decoder(output)

                sigmoid_output = output[("disp", 0)]
                sigmoid_output_resized = torch.nn.functional.interpolate(
                    sigmoid_output, original_size, mode="bilinear", align_corners=False)
                sigmoid_output_resized = sigmoid_output_resized.cpu().numpy()[:, 0]

                toplot = sigmoid_output_resized.squeeze()
                normalizer = mpl.colors.Normalize(vmin=toplot.min(), vmax=np.percentile(toplot, 95))
                mapper = cm.ScalarMappable(norm=normalizer, cmap='magma')
                colormapped_im = (mapper.to_rgba(toplot)[:, :, :3] * 255).astype(np.uint8)

            self.frame_num += 1
            self.prve_frame = current_frame
            return colormapped_im
        else: 
            self.frame_num += 1
            self.prve_frame = current_frame
            return current_frame