import pyautogui
import time
import cv2
import numpy as np
import mss
from paddleocr import PaddleOCR

class ScreenOCR:
    def __init__(self, lang='en', confidence_threshold=0.5, monitor_number=0):
        """Initializes the OCR tool with specified language and confidence threshold."""
        self.monitor_number = monitor_number  # Store the monitor number
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        self.confidence_threshold = confidence_threshold
        self.text_bboxes = []
        
    def _get_monitor_offset(self):
        """Get current monitor offset coordinates."""
        with mss.mss() as sct:
            if self.monitor_number != 0 and self.monitor_number < len(sct.monitors):
                # Return the monitor's offset to adjust click coordinates
                return (
                    sct.monitors[self.monitor_number]["left"],
                    sct.monitors[self.monitor_number]["top"]
                )
        return (0, 0)  # Default offset for primary monitor or monitor 0 (all screens)

    def transform_big_contrast(self, image):
        """enhances the contrast of the image for better ocr results."""
        if len(image.shape) == 3:  # check if the image has 3 channels
            gray = cv2.cvtcolor(image, cv2.color_bgr2gray)
        else:
            gray = image  # image is already grayscale
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def take_screenshot(self, monitor_number=None, grayscale=True, transform_contrast=False):
        """Captures a screenshot of the specified monitor and converts it to OpenCV format."""
        if monitor_number is None:
            monitor_number = self.monitor_number
            
        with mss.mss() as sct:
            if monitor_number >= len(sct.monitors):
                print(f"Monitor {monitor_number} not found. Using primary monitor.")
                monitor_number = 1  # Default to primary monitor
                
            screenshot = sct.grab(sct.monitors[monitor_number])
            image_np = np.array(screenshot)
            if grayscale:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2GRAY)
            else:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
            if transform_contrast:
                image_np = self.transform_big_contrast(image_np)
            return image_np

    def extract_text(self, image=None):
        """Runs OCR on the screenshot and stores detected text with bounding boxes."""
        if image is None:
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
        
        if not self.text_bboxes:
            print("No text detected. Running extract_text() first.")
            self.extract_text()
        
        for (x1, y1, x2, y2), text in self.text_bboxes:
            if keyword.lower() in text.lower():
                return (x1, y1, x2, y2)
        return None
        
    def click_text(self, keyword, sleep_time=0.5):
        """Clicks at the center of the first detected keyword, adjusting for monitor offset."""
        bbox = self.search_text(keyword)
        if bbox:
            time.sleep(sleep_time)
            x1, y1, x2, y2 = bbox
            
            # Calculate center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Add monitor offset if not using the primary monitor
            if self.monitor_number != 0:
                offset_x, offset_y = self._get_monitor_offset()
                center_x += offset_x
                center_y += offset_y
                
            pyautogui.click(center_x, center_y)
            return True
        return False

    def draw_bboxes(self, image=None):
        """Displays the screenshot with detected text and bounding boxes in a colorful image."""
        if image is None:
            image = self.take_screenshot(grayscale=False)  # Ensure the image is in color
        
        if len(image.shape) < 3:  # If the image is grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert to 3 color channels

        for (x1, y1, x2, y2), text in self.text_bboxes:
            green_color = (0, 255, 0)  # Green for bounding boxes
            red_color = (0, 0, 255)  # Red for text
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), green_color, 1)
            cv2.putText(image, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, red_color, 1)

        cv2.imshow("OCR Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def show_image(image, window_name="Image", window_size=(800, 600)):
    """Helper function to display an image with scrollable support for large images."""
    if image is None:
        print("Image not found")
        return

    if not isinstance(image, np.ndarray):
        image = np.array(image)

    # Resize the window to fit the specified size
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, *window_size)

    # Display the image
    cv2.imshow(window_name, image)
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
