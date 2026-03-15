import cv2 as cv
import numpy as np
from datetime import datetime


def apply_brightness_contrast(img, contrast=1.0, brightness=0):
    """
    I' = alpha * I + beta
    contrast -> alpha
    brightness -> beta
    """
    out = contrast * img.astype(np.float32) + brightness
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


def apply_center_bulge(img, strength=0.7, radius_ratio=0.6):

    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2

    radius = min(cx, cy) * radius_ratio

    map_x = np.zeros((h, w), np.float32)
    map_y = np.zeros((h, w), np.float32)

    for y in range(h):
        for x in range(w):

            dx = x - cx
            dy = y - cy

            r = np.sqrt(dx*dx + dy*dy)

            if r < radius:
                factor = 1 + strength * (1 - r/radius)**2
            else:
                factor = 1

            map_x[y,x] = cx + dx / factor
            map_y[y,x] = cy + dy / factor

    return cv.remap(img, map_x, map_y, cv.INTER_LINEAR)


def draw_status_panel(img, is_recording, is_flip, is_distortion, contrast, brightness, fps):
    canvas = img.copy()

    mode_text = "RECORD" if is_recording else "PREVIEW"
    mode_color = (0, 0, 255) if is_recording else (150, 150, 150)

    if is_recording:
        cv.circle(canvas, (30, 30), 10, (0, 0, 255), -1)

    lines = [
        f"Mode       : {mode_text}",
        f"Flip       : {'ON' if is_flip else 'OFF'}",
        f"Distortion : {'ON' if is_distortion else 'OFF'}",
        f"Contrast   : {contrast:.1f}",
        f"Brightness : {brightness}",
        f"FPS        : {fps:.1f}",
        "Space: Record Toggle | ESC: Quit",
        "F: Flip | D: neoptteogi | [ ]: Brightness | - =: Contrast",
    ]

    y = 30
    for i, text in enumerate(lines):
        shadow_color = (255, 255, 255)
        text_color = mode_color if i == 0 else (0, 0, 0)

        cv.putText(canvas, text, (50, y), cv.FONT_HERSHEY_DUPLEX, 0.6, shadow_color, 2)
        cv.putText(canvas, text, (50, y), cv.FONT_HERSHEY_DUPLEX, 0.6, text_color, 1)
        y += 28

    return canvas


def main():
    video = cv.VideoCapture(0)

    if not video.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    fps = video.get(cv.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0

    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    writer = None
    is_recording = False

    # 추가 기능 상태
    is_flip = False
    is_distortion = False
    contrast = 1.0
    brightness = 0

    window_name = "My Video Recorder"

    while True:
        valid, frame = video.read()
        if not valid:
            print("프레임을 읽을 수 없습니다.")
            break

        # 1. 좌우 반전
        if is_flip:
            frame = cv.flip(frame, 1)

        # 2. 넙떠기 필터
        if is_distortion:
            frame = apply_center_bulge(frame, strength=2, radius_ratio=1.5)

        # 3. 밝기 / 대비
        frame_edit = apply_brightness_contrast(frame, contrast, brightness)

        # 4. 상태 정보 표시
        frame_show = draw_status_panel(
            frame_edit,
            is_recording=is_recording,
            is_flip=is_flip,
            is_distortion=is_distortion,
            contrast=contrast,
            brightness=brightness,
            fps=fps
        )

        cv.imshow(window_name, frame_show)

        # 녹화 중이면 편집된 프레임 저장
        if is_recording and writer is not None:
            writer.write(frame_edit)

        key = cv.waitKey(1) & 0xFF

        # ESC : 종료
        if key == 27:
            break

        # Space : 녹화 시작/종료
        elif key == ord(' '):
            is_recording = not is_recording

            if is_recording:
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"record_{now}.avi"

                writer = cv.VideoWriter(
                    output_file,
                    fourcc,
                    fps,
                    (width, height),
                    True
                )

                if not writer.isOpened():
                    print("동영상 파일을 생성할 수 없습니다.")
                    is_recording = False
                    writer = None
                else:
                    print(f"녹화 시작: {output_file}")

            else:
                if writer is not None:
                    writer.release()
                    writer = None
                print("녹화 종료")

        # F : 좌우 반전 토글
        elif key == ord('f') or key == ord('F'):
            is_flip = not is_flip

        # D : 넙떠기 필터 토글
        elif key == ord('d') or key == ord('D'):
            is_distortion = not is_distortion

        # 밝기 감소
        elif key == ord('[') or key == ord('{'):
            brightness -= 5

        # 밝기 증가
        elif key == ord(']') or key == ord('}'):
            brightness += 5

        # 대비 감소
        elif key == ord('-') or key == ord('_'):
            contrast = max(0.1, contrast - 0.1)

        # 대비 증가
        elif key == ord('=') or key == ord('+'):
            contrast = min(3.0, contrast + 0.1)

    if writer is not None:
        writer.release()

    video.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()