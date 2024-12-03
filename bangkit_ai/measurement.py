import requests
import cv2
import numpy as np
from ultralytics import YOLO


def coin_measurement(image, coin_results):
    coin_diameter_cm = 2.7
    if not coin_results:
        print("No coin results found")
        return None, image

    x_coin, y_coin, w_coin, h_coin = coin_results[0].boxes.xywh[0]
    x1 = int(x_coin - w_coin / 2)
    y1 = int(y_coin - h_coin / 2)
    x2 = int(x_coin + w_coin / 2)
    y2 = int(y_coin + h_coin / 2)
    crop_coin = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop_coin, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)

    detected_circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        1,
        20,
        param1=50,
        param2=30,
        minRadius=1,
        maxRadius=300,
    )

    if detected_circles is not None:
        detected_circles = np.uint16(np.around(detected_circles))
        a, b, r = detected_circles[0, 0, :]
        coin_diameter_px = 2 * r
        cv2.circle(image, (x1 + a, y1 + b), r, (255, 0, 0), 3)
        cv2.circle(image, (x1 + a, y1 + b), 1, (0, 0, 255), 3)
    else:
        print("No circles detected")
        coin_diameter_px = min(w_coin, h_coin)
    print(f"Coin diameter in pixels: {coin_diameter_px}")
    scale_factor = coin_diameter_cm / coin_diameter_px
    print(f"Scale factor: {scale_factor}")
    return scale_factor, image


def baby_measurement(image, scale_factor, pose_model):
    pose_results = pose_model(image, stream=False)
    image1 = pose_results[0].plot()
    keypoints = pose_results[0].keypoints.xy[0]
    indices = np.array([0, 5, 11, 13, 15])
    selected_keypoints = keypoints[indices]
    nose, left_shoulder, left_hip, left_knee, left_ankle = selected_keypoints
    _, y_baby, _, _ = pose_results[0].boxes.xyxy[0]
    y_to_nose = nose[1] - y_baby
    nose_to_shoulder = left_shoulder[1] - nose[1]
    shoulder_to_hip = left_hip[1] - left_shoulder[1]
    hip_to_knee = np.linalg.norm(left_knee - left_hip)
    knee_to_ankle = np.linalg.norm(left_ankle - left_knee)
    baby_length_px = (
        y_to_nose + nose_to_shoulder + shoulder_to_hip + hip_to_knee + knee_to_ankle
    )
    print(f"Baby length in pixels: {baby_length_px}")
    baby_length_cm = baby_length_px * scale_factor
    return baby_length_cm, image1


def measure_all(url):
    pose_model = YOLO("models/keypoint.pt")
    coin_model = YOLO("models/coin.pt")
    image = download_image(url)
    # if image is None:
    #     print("Failed to download the image.")
    #     return None
    if image is None or len(image.shape) != 3 or image.shape[-1] != 3:
        print("Invalid image format. Ensure the image is RGB or convertible to RGB.")
        return None

    coin_results = coin_model(image, stream=False)
    if not coin_results:
        print("No coin detected.")
        return None

    scale_factor, image2 = coin_measurement(image, coin_results)
    baby_length, image1 = baby_measurement(image2, scale_factor, pose_model)

    return baby_length


def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        if img is None:
            print("Image could not be decoded.")
            return None

        if len(img.shape) == 2:  # Grayscale (1 channel)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Konversi ke 3 channel (BGR)
        elif img.shape[-1] == 4:  # RGBA (4 channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Konversi ke 3 channel (BGR)
        elif img.shape[-1] != 3:  # Format tidak dikenal
            print(f"Unsupported image format with {img.shape[-1]} channels.")
            return None
        return img
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None
