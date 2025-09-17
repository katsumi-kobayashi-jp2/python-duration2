import ctypes
import time
import pyautogui

class LASTINPUTINFO(ctypes.Structure):
    """
    Windows APIのLASTINPUTINFO構造体を表すクラス。

    cbSize: 構造体のサイズ（バイト単位）
    dwTime: 最後の入力イベントからの時間（ミリ秒単位）
    """
    _fields_ = [
        ('cbSize', ctypes.wintypes.UINT), # pylint: disable=invalid-name
        ('dwTime', ctypes.wintypes.DWORD), # pylint: disable=invalid-name
    ]

def get_idle_duration():
    """現在の無操作時間（秒）を取得するWindows専用関数"""
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
        raise ctypes.WinError()
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0

def wait_for_idle(threshold_sec=5, check_interval=0.5):
    """
    指定秒数以上の無操作状態になるまで無限ループで待機する関数。
    返り値はありません。

    Args:
        threshold_sec (float): 無操作検知閾値（秒）
        check_interval (float): チェック間隔（秒）
    """
    while True:
        idle = get_idle_duration()
        if idle >= threshold_sec:
            break
        time.sleep(check_interval)

# メイン処理例
if __name__ == "__main__":
    wait_for_idle(threshold_sec=3, check_interval=0.5)
    print("無操作状態を検出しました。クリックを実行します。")
    current_pos = pyautogui.position()
    pyautogui.moveTo(100, 200, duration=0)
    pyautogui.click()
    pyautogui.moveTo(current_pos, duration=0)



    # 検出したい画像ファイルのパス
    image_path = 'edgeIcon.png'

    from PIL import Image

    img = Image.open(image_path)
    resized = img.resize((int(img.width * 1.25), int(img.height * 1.25)), Image.LANCZOS)
    resized.save('capture_scaled.png')
    image_path = 'capture_scaled.png'

    # 画面から画像を探して、位置の情報を取得する
    location = pyautogui.locateOnScreen(image_path, confidence=0.5)  # confidenceは精度調整用

    if location is not None:
        print(f"画像が見つかりました： {location}")
        # 例：中央の座標を取得
        center = pyautogui.center(location)
        print(f"中央座標： {center}")
        # クリックなどの操作も可能
        # pyautogui.click(center)
    else:
        print("画像は見つかりませんでした。")    