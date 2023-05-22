import cv2
import os
import json
import argparse
import numpy as np
import PIL.Image as pil
import matplotlib as mpl
import matplotlib.cm as cm

import torch
from torchvision import transforms

from utils.manydepth import networks
from utils.manydepth.layers import transformation_from_parameters

def load_and_preprocess_image(image, resize_width, resize_height):
    image = pil.fromarray(image).convert('RGB')
    # image = pil.open(image_path).convert('RGB')
    original_width, original_height = image.size
    image = image.resize((resize_width, resize_height), pil.LANCZOS)
    image = transforms.ToTensor()(image).unsqueeze(0)
    if torch.cuda.is_available():
        return image.cuda(), (original_height, original_width)
    return image, (original_height, original_width)


def load_and_preprocess_intrinsics(intrinsics_path, resize_width, resize_height):
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


def process_frame(current_frame, previous_frame):
    org_img = current_frame.copy()
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    model_path = 'model\depth\manydepth\KITTI_MR'

    encoder_dict = torch.load(os.path.join(model_path, 'encoder.pth'), map_location=device)
    encoder = networks.ResnetEncoderMatching(18, False,
                                    input_width=encoder_dict['width'],
                                    input_height=encoder_dict['height'],
                                    adaptive_bins=True,
                                    min_depth_bin=encoder_dict['min_depth_bin'],
                                    max_depth_bin=encoder_dict['max_depth_bin'],
                                    depth_binning='linear',
                                    num_depth_bins=96)
    filtered_dict_enc = {k: v for k, v in encoder_dict.items() if k in encoder.state_dict()}
    encoder.load_state_dict(filtered_dict_enc)

    print("   Loading pretrained decoder")

    depth_decoder = networks.DepthDecoder(num_ch_enc=encoder.num_ch_enc, scales=range(4))

    loaded_dict = torch.load(os.path.join(model_path, "depth.pth"), map_location=device)
    depth_decoder.load_state_dict(loaded_dict)

    print("   Loading pose network")
    pose_enc_dict = torch.load(os.path.join(model_path, "pose_encoder.pth"),
                               map_location=device)
    pose_dec_dict = torch.load(os.path.join(model_path, "pose.pth"), map_location=device)

    pose_enc = networks.ResnetEncoder(18, False, num_input_images=2)
    pose_dec = networks.PoseDecoder(pose_enc.num_ch_enc, num_input_features=1,
                                    num_frames_to_predict_for=2)

    pose_enc.load_state_dict(pose_enc_dict, strict=True)
    pose_dec.load_state_dict(pose_dec_dict, strict=True)

    # Setting states of networks
    encoder.eval()
    depth_decoder.eval()
    pose_enc.eval()
    pose_dec.eval()
    if torch.cuda.is_available():
        encoder.cuda()
        depth_decoder.cuda()
        pose_enc.cuda()
        pose_dec.cuda()

    # Load input data
    input_image, original_size = load_and_preprocess_image(current_frame,
                                                           resize_width=encoder_dict['width'],
                                                           resize_height=encoder_dict['height'])

    source_image, _ = load_and_preprocess_image(previous_frame,
                                                resize_width=encoder_dict['width'],
                                                resize_height=encoder_dict['height'])

    K, invK = load_and_preprocess_intrinsics('model/depth/manydepth/KITTI_MR/test_sequence_intrinsics.json',
                                             resize_width=encoder_dict['width'],
                                             resize_height=encoder_dict['height'])

    with torch.no_grad():

        # Estimate poses
        pose_inputs = [source_image, input_image]
        pose_inputs = [pose_enc(torch.cat(pose_inputs, 1))]
        axisangle, translation = pose_dec(pose_inputs)
        pose = transformation_from_parameters(axisangle[:, 0], translation[:, 0], invert=True)

        # if args.mode == 'mono':
        #     pose *= 0  # zero poses are a signal to the encoder not to construct a cost volume
        #     source_image *= 0

        # Estimate depth
        output, lowest_cost, _ = encoder(current_image=input_image,
                                         lookup_images=source_image.unsqueeze(1),
                                         poses=pose.unsqueeze(1),
                                         K=K,
                                         invK=invK,
                                         min_depth_bin=encoder_dict['min_depth_bin'],
                                         max_depth_bin=encoder_dict['max_depth_bin'])

        output = depth_decoder(output)

        sigmoid_output = output[("disp", 0)]
        sigmoid_output_resized = torch.nn.functional.interpolate(
            sigmoid_output, original_size, mode="bilinear", align_corners=False)
        sigmoid_output_resized = sigmoid_output_resized.cpu().numpy()[:, 0]

        # Saving numpy file
        # directory, filename = os.path.split(args.target_image_path)
        # directory = 
        # output_name = os.path.splitext(filename)[0]
        # name_dest_npy = os.path.join(directory, "{}_disp_{}.npy".format(output_name, 'multi'))
        # np.save(name_dest_npy, sigmoid_output.cpu().numpy())

        # Saving colormapped depth image and cost volume argmin
        # for plot_name, toplot in (('costvol_min', lowest_cost), ('disp', sigmoid_output_resized)):
        #     # print('plot_name: ', plot_name)
        #     # print('toplot: ', toplot)
        #     toplot = toplot.squeeze()
        #     normalizer = mpl.colors.Normalize(vmin=toplot.min(), vmax=np.percentile(toplot, 95))
        #     mapper = cm.ScalarMappable(norm=normalizer, cmap='magma')
        #     colormapped_im = (mapper.to_rgba(toplot)[:, :, :3] * 255).astype(np.uint8)
        #     im = pil.fromarray(colormapped_im)

        #     name_dest_im = os.path.join('I:/pyside6/pyside6-video-player',
        #                                 "{}_{}_{}.jpeg".format('test', plot_name, 'multi'))
            

        #     if plot_name == 'disp':
        #         cv2.imshow('frame', colormapped_im)
        #     im.save(name_dest_im)

        #     print("-> Saved output image to {}".format(name_dest_im))

        toplot = sigmoid_output_resized.squeeze()
        normalizer = mpl.colors.Normalize(vmin=toplot.min(), vmax=np.percentile(toplot, 95))
        mapper = cm.ScalarMappable(norm=normalizer, cmap='magma')
        colormapped_im = (mapper.to_rgba(toplot)[:, :, :3] * 255).astype(np.uint8)
        # im = pil.fromarray(colormapped_im)
        cv2.imshow('org_frame', org_img)
        cv2.imshow('frame', colormapped_im)
    # print('-> Done!')

if __name__ == '__main__':
    cap = cv2.VideoCapture('video/20.mp4')
    # 获取帧率
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 设置帧号
    cap.set(cv2.CAP_PROP_POS_FRAMES, fps * 50)
    previous_frame = None
    while True:
        ret, frame = cap.read()
        # cv2.imshow('frame', frame)
        if previous_frame is not None:
          process_frame(frame, previous_frame)
        previous_frame = frame
        if cv2.waitKey(int(1000/fps)) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()