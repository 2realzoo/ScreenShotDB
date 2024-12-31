import cv2

def remove_status_bar(image_path):
    image = cv2.imread(image_path)
    height, _ = image.shape[:2]
    
    # 대략적인 비율로 상단 5%를 확인 (스테이터스 바가 포함된 영역)
    status_bar_height = int(height * 0.05)
    status_bar_area = image[:status_bar_height, :]

    # 그레이스케일로 변환
    gray = cv2.cvtColor(status_bar_area, cv2.COLOR_BGR2GRAY)

    # 어두운 부분을 강조
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    # 컨투어 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_area = max(contours, key=cv2.contourArea) if contours else None

    if contour_area is not None:
        x, y, w, h = cv2.boundingRect(contour_area)
        cropped_image = image[h:, :]
    else:
        cropped_image = image

    return cropped_image

    