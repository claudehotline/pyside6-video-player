import cv2
import onnxruntime
import numpy as np
from segment_anything import sam_model_registry, SamPredictor

if __name__ == '__main__':
    
    image = cv2.imread('pic/1.jpg')

    checkpoint = 'model/seg/sam/sam_vit_h_4b8939.pth'
    model_type = 'vit_h'
    sam = sam_model_registry[model_type](checkpoint=checkpoint)
    predictor = SamPredictor(sam)
    predictor.set_image(image)
    # 1, 256, 64, 64
    image_embedding = predictor.get_image_embedding().cpu().numpy()

    input_point = np.array([[500, 175]])
    input_label = np.array([1])

    onnx_coord = np.concatenate([input_point, np.array([[0.0, 0.0]])], axis=0)[None, :, :]
    onnx_label = np.concatenate([input_label, np.array([-1])], axis=0)[None, :].astype(np.float32)

    onnx_coord = predictor.transform.apply_coords(onnx_coord, image.shape[:2]).astype(np.float32)

    onnx_mask_input = np.zeros((1, 1, 256, 256), dtype=np.float32)
    onnx_has_mask_input = np.zeros(1, dtype=np.float32)

    ort_inputs = {
      "image_embeddings": image_embedding,
      "point_coords": onnx_coord,
      "point_labels": onnx_label,
      "mask_input": onnx_mask_input,
      "has_mask_input": onnx_has_mask_input,
      "orig_im_size": np.array(image.shape[:2], dtype=np.float32)
    }

    ort_session = onnxruntime.InferenceSession("model/seg/sam/sam_onnx_example.onnx")

    masks, _, low_res_logits = ort_session.run(None, ort_inputs)
    masks = masks > predictor.model.mask_threshold

    color = np.array([0, 255, 0])

    h, w = masks.shape[-2:]

    mask_image = masks.reshape(h, w, 1) * color.reshape(1, 1, 3)
    mask_image = mask_image.astype(np.uint8)
    cv2.imshow('mask', mask_image)

    print(mask_image.shape)

    cv2.imshow('image', image)

    result = cv2.addWeighted(image, 0.5, mask_image, 0.5, 0)

    cv2.circle(result, (input_point[0][0], input_point[0][1]), 5, (0, 0, 255), -1)

    cv2.imshow('result', result)

    cv2.waitKey(0)