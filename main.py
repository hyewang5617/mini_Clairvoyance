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


def draw_status_panel(img, is_recording, is_flip, contrast, brightness, fps):
    """
    현재 상태 정보를 화면에 표시
    """
    canvas = img.copy()

    mode_text = "RECORD" if is_recording else "PREVIEW"
    rec_color = (0, 0, 255) if is_recording else (180, 180, 180)

    # 녹화 중 표시용 빨간 원
    if is_recording:
        cv.circle(canvas, (30, 30), 10, (0, 0, 255), -1)

    # 상태 텍스트
    lines = [
        f"Mode       : {mode_text}",
        f"Flip       : {'ON' if is_flip else 'OFF'}",
        f"Contrast   : {contrast:.1f}",
        f"Brightness : {brightness}",
        f"FPS        : {fps:.1f}",
        "Space: Record Toggle | ESC: Quit",
        "F: Flip | [ ]: Brightness | - =: Contrast",
    ]

    y = 30
    for text in lines:
        cv.putText(canvas, text, (50, y), cv.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 2)
        cv.putText(canvas, text, (50, y), cv.FONT_HERSHEY_DUPLEX, 0.6, rec_color if "Mode" in text else (0, 0, 0), 1)
        y += 28

    return canvas


def main():
    # 0번 카메라 열기
    video = cv.VideoCapture(0)

    if not video.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    # 카메라 정보 얻기
    fps = video.get(cv.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0

    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

    # 저장 관련 설정
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    writer = None
    is_recording = False

    # 추가 기능 상태
    is_flip = False
    contrast = 1.0
    brightness = 0

    window_name = "My Video Recorder"

    while True:
        valid, frame = video.read()
        if not valid:
            print("프레임을 읽을 수 없습니다.")
            break

        # 좌우 반전
        if is_flip:
            frame = cv.flip(frame, 1)

        # 밝기 / 대비 적용
        frame_edit = apply_brightness_contrast(frame, contrast, brightness)

        # 화면 표시용 오버레이
        frame_show = draw_status_panel(
            frame_edit,
            is_recording=is_recording,
            is_flip=is_flip,
            contrast=contrast,
            brightness=brightness,
            fps=fps
        )

        cv.imshow(window_name, frame_show)

        # 녹화 중이면 저장
        if is_recording and writer is not None:
            writer.write(frame_edit)

        key = cv.waitKey(1) & 0xFF

        # ESC: 종료
        if key == 27:
            break

        # Space: 녹화 모드 전환
        elif key == ord(' '):
            is_recording = not is_recording

            if is_recording:
                # 녹화 시작 시점에 새 파일 생성
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
                # 녹화 종료
                if writer is not None:
                    writer.release()
                    writer = None
                print("녹화 종료")

        # f: 좌우 반전
        elif key == ord('f') or key == ord('F'):
            is_flip = not is_flip

        # brightness 감소
        elif key == ord('[') or key == ord('{'):
            brightness -= 5

        # brightness 증가
        elif key == ord(']') or key == ord('}'):
            brightness += 5

        # contrast 감소
        elif key == ord('-') or key == ord('_'):
            contrast = max(0.1, contrast - 0.1)

        # contrast 증가
        elif key == ord('=') or key == ord('+'):
            contrast = min(3.0, contrast + 0.1)

    # 자원 해제
    if writer is not None:
        writer.release()
    video.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()