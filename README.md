# My Video Recorder

OpenCV와 Python을 이용하여 구현한 간단한 비디오 녹화 프로그램입니다.

## 기능 (Features)

- 웹캠을 이용한 실시간 카메라 화면 미리보기
- Space 키를 이용한 Preview / Record 모드 전환
- 녹화된 영상을 AVI 파일로 저장
- 녹화 중 화면에 빨간색 표시(Recording Indicator) 출력
- 좌우 반전(Horizontal Flip) 기능
- 밝기(Brightness) 조절 기능
- 대비(Contrast) 조절 기능
- **넙떠기 필터 (Face Bulge Filter)**  
  - 화면 중앙을 기준으로 얼굴이 넓어지도록 왜곡하는 필터
  - radial distortion 방식을 이용하여 중앙 부분을 확대하는 효과 구현

## 조작 방법 (Controls)

- **Space** : 녹화 시작 / 중지
- **ESC** : 프로그램 종료
- **F** : 좌우 반전 기능 켜기 / 끄기
- **D** : 넙떠기 필터 켜기 / 끄기
- **[** : 밝기 감소
- **]** : 밝기 증가
- **-** : 대비 감소
- **=** : 대비 증가