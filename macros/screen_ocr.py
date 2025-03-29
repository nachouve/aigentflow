import pyautogui
import cv2
import numpy as np
import mss
from paddleocr import PaddleOCR

class ScreenOCR:
    def __init__(self, lang='en', confidence_threshold=0.5):
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        self.confidence_threshold = confidence_threshold
        self.text_bboxes = []

    def take_screenshot(self):
        """Captures a screenshot of all monitors and converts it to OpenCV format."""
        with mss.mss() as sct:
            screenshot = sct.shot(output=None)  # Capture all monitors
            image_np = np.array(screenshot)
            return cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)

    def extract_text(self):
        """Runs OCR on the screenshot and stores detected text with bounding boxes."""
        image = self.take_screenshot()
        results = self.ocr.ocr(image, cls=True)
        self.text_bboxes = []

        for res in results[0]:
            bbox, text_info = res
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
            text, confidence = text_info

            if confidence > self.confidence_threshold:
                self.text_bboxes.append(((x1, y1, x3, y3), text))

        return self.text_bboxes

    def search_text(self, keyword):
        """Finds the bounding box of the first occurrence of the keyword."""
        for (x1, y1, x2, y2), text in self.text_bboxes:
            if keyword.lower() in text.lower():
                return (x1, y1, x2, y2)
        return None

    def click_text(self, keyword):
        """Clicks at the center of the first detected keyword."""
        bbox = self.search_text(keyword)
        if bbox:
            x1, y1, x2, y2 = bbox
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            pyautogui.click(center_x, center_y)
            return True
        return False

    def draw_bboxes(self):
        """Displays the screenshot with detected text and bounding boxes."""
        image = self.take_screenshot()
        for (x1, y1, x2, y2), text in self.text_bboxes:
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(image, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("OCR Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    ocr_tool = ScreenOCR()
    ocr_tool.extract_text()
    ocr_tool.draw_bboxes()
    
    # Click on a specific word
    if ocr_tool.click_text("Login"):
        print("Clicked on 'Login'")
    else:
        print("'Login' not found")
