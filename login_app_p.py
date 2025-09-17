import tkinter as tk
from tkinter import messagebox
import datetime
import subprocess
import os
import tempfile
import json  # 保存用にJSONを使います

import time
import mss
import numpy as np
import cv2
import pyautogui as pg
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import random
import ctypes
import threading

# DPI 対応
ctypes.windll.user32.SetProcessDPIAware()
log_file_in = "log_buffer.txt"
log_file_out = "log_buffer2.txt"
log_file_box = "log_buffer_box.txt"

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

class ImageClicker:
    def __init__(self, confidence=0.8, max_attempts=5, wait_time=2, log_file="log_buffer.txt"):
        self.confidence = confidence
        self.max_attempts = max_attempts
        self.wait_time = wait_time
        self.log_file = log_file

    # def log_match(self, label):
    #     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     with open(self.log_file, "a", encoding="utf-8") as f:
    #         f.write(f"{now}, 記録 {label}\n")
    #     print(f"ログ記録: {now}, 記録 {label}")

    # def log_match(self, label):
    #     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     log_file_in = "log_buffer.txt"
    #     log_file_out = "log_buffer2.txt"
    #     if label != '' and label != None:
    #         # 末尾に新しい記録を追加
    #         data = f"{now}, 記録 {label}\n"
    #         # log_buffer2.txt に書き込み
    #         with open(log_file_in, "a", encoding="utf-8") as f:
    #                 f.write(data)
    #         print(f"ログ記録(X): {now}, 記録 {label} + 黒・黄・赤 → {log_file_in}")        
    #         if label == "ｘ":
    #             # 元ファイルを読み込む（存在しない場合は空にする）
    #             try:
    #                 with open(log_file_in, "r", encoding="utf-8") as f:
    #                     data = f.read()
    #             except FileNotFoundError:
    #                 data = ""

    def log_match(self, label):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if label not in ("", None, "40"):
            # 通常の記録
            with open(log_file_in, "a", encoding="utf-8") as f:
                f.write(f"{now}, 記録 {label}\n")
            print(f"ログ記録: {now}, 記録 {label} → {log_file_in}")

            # 特別処理: "X" のとき
            if label == 'ｘ':
                try:
                    with open(log_file_in, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    lines = []

                # "記録 X" を含む行を削除
                filtered = [line for line in lines if "記録 ｘ" not in line]

                # log_buffer2.txt に保存
                with open(log_file_out, "w", encoding="utf-8") as f:
                    f.writelines(filtered)

                print(f"→ '記録 X' を削除して {log_file_out} を作成しました")
        elif label not in ("", None):
            with open(log_file_box, "a", encoding="utf-8") as f:
                f.write(f"{now}, 記録 {label}\n")
            print(f"ログ記録: {now}, 記録 {label} → {log_file_in}")            

    def find_image_on_monitor(self, monitor, image_path):
        """クリックせず、画像の有無だけを判定"""
        template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template is None:
            print(f"画像が読み込めません: {image_path}")
            return False
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

        with mss.mss() as sct:
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        return max_val >= self.confidence

    def click_image_on_monitor(self, monitor, image_path, label="", option=None, offset=(0,0)):
        """指定したモニタ領域で画像を検索してクリック。optionでクリック座標を優先指定可能。offsetで補正可能"""
        offset_x, offset_y = offset

        if option is not None:
            # 座標が指定された場合は、画像検索をスキップしてクリック
            click_x = monitor['left'] + option[0] + offset_x
            click_y = monitor['top'] + option[1] + offset_y

            time.sleep(0.2)
            if wait_for_idle_flag==1:
                wait_for_idle(threshold_sec=2, check_interval=0.5)    
                current_pos = pg.position()
                pg.moveTo(click_x, click_y, duration=0)
                pg.doubleClick()
                pg.moveTo(current_pos, duration=0)
            else:
                pg.moveTo(click_x, click_y, duration=0)
                pg.doubleClick()

            print(f"オプション座標をクリックしました: ({click_x}, {click_y}) [補正 {offset}]")
            if label:
                self.log_match(label)
            return True

        # 画像マッチング処理
        template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template is None:
            print(f"画像が読み込めません: {image_path}")
            return False
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
        template_h, template_w = template.shape[:2]

        with mss.mss() as sct:
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= self.confidence:
            click_x = monitor['left'] + max_loc[0] + template_w // 2 + offset_x
            click_y = monitor['top'] + max_loc[1] + template_h // 2 + offset_y

            time.sleep(0.2)
            if wait_for_idle_flag==1:
                wait_for_idle(threshold_sec=3, check_interval=0.5)    
                time.sleep(0.2)
                current_pos = pg.position()
                pg.moveTo(click_x, click_y, duration=0)
                pg.doubleClick()
                pg.moveTo(current_pos, duration=0)
            else:
                pg.moveTo(click_x, click_y, duration=0)
                pg.doubleClick()                

            print(f"画像 {image_path} をクリックしました: ({click_x}, {click_y}) [補正 {offset}]")

            if label:
                self.log_match(label)
            return True
        return False

    # def attempt_click_on_monitor(self, monitor, image_path, label="", option=None, offset=(0,0)):
    #     """リトライ付きクリック処理。optionがあれば座標優先。offsetで補正可能"""
    #     for attempt in range(self.max_attempts):
    #         if self.click_image_on_monitor(monitor, image_path, label, option, offset):
    #             return True
    #         else:
    #             print(f"リトライ {attempt + 1}/{self.max_attempts}")
    #             time.sleep(self.wait_time)
    #     print("最大試行回数に達しました。")
    #     return False

    def attempt_click_on_monitor(self, monitor, image_path, label="", option=None, offset=(0,0), retry=3):
        """リトライ付きクリック処理。optionがあれば座標優先。offsetで補正可能
        retry: リトライ回数（指定なしなら self.max_attempts を使用）
        """
        attempts = retry if retry is not None else self.max_attempts

        for attempt in range(attempts):
            if self.click_image_on_monitor(monitor, image_path, label, option, offset):
                return True
            else:
                print(f"リトライ {attempt + 1}/{attempts}")
                time.sleep(self.wait_time)
        print("最大試行回数に達しました。")
        return False
    
def get_lines_since_yellow(filename):
    """
    ログファイルを読み込み、最後から「黄」が含まれる行までの行数をカウントして返す。
    見つからない場合はNoneを返す。

    Args:
        filename (str): ログファイルのパス

    Returns:
        int or None: 最後の行からさかのぼって「黄」のある行までの行数（0行目含む）、
                    見つからなければ None
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 後ろから走査し、「黄」が含まれる行を探す
    for i in range(len(lines)-1, -1, -1):
        if '黄' in lines[i]:
            # 最後の行からこの行までの行数を算出
            # i 行目 (0オリジン)、最終行は len(lines)-1
            return (len(lines) - 1) - i
    return None

class LoginApp:
    BASE_WIDTH = 600
    BASE_HEIGHT = 480
    SETTINGS_FILE = "settings.json"  # 保存用ファイル名

    def __init__(self, root, login_info):
        self.root = root
        self.login_info = login_info

        self.root.title("Custom TK Window")
        self.root.geometry(f"{self.BASE_WIDTH}x{self.BASE_HEIGHT}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # --- 1. 上段ボタン "Go" と "End" ---
        top_button_frame = tk.Frame(self.root)
        top_button_frame.pack(pady=5)

        self.go_button = tk.Button(
            top_button_frame,
            text="Go",
            bg="green",
            fg="white",
            width=10,
            font=("Arial", 12, "bold"),
            command=self.on_go_clicked
        )
        self.go_button.pack(side=tk.LEFT, padx=10)

        self.end_button = tk.Button(
            top_button_frame,
            text="End",
            bg="orange",
            fg="white",
            width=10,
            font=("Arial", 12, "bold"),
            command=self.root.destroy
        )
        self.end_button.pack(side=tk.LEFT, padx=10)

        # --- 2. チェックボタン群(青色)、重複除く ---
        options = [
            "Ignore sales", "empty box open", "target only empty box",
            "open victory box",
            "50 challenge", "70 challenge", "75 challenge",
            "100 challenge", "130 challenge"
        ]

        option_frame = tk.Frame(self.root)
        option_frame.pack(pady=10, fill='x')

        self.option_vars = []
        # for i, opt in enumerate(options):
        #     var = tk.BooleanVar(value=False)
        #     cb = tk.Checkbutton(
        #         option_frame, text=opt, variable=var,
        #         fg="blue", font=("Arial", 11)
        #     )
        #     cb.grid(row=i // 2, column=i % 2, sticky='w', padx=10, pady=2)
        #     self.option_vars.append((opt, var))

        for i, opt in enumerate(options):
            # "Ignore sales" はデフォルト True、それ以外は False
            initial_value = True if opt == "Ignore sales" else False
            var = tk.BooleanVar(value=initial_value)
            cb = tk.Checkbutton(
                option_frame, text=opt, variable=var,
                fg="blue", font=("Arial", 11)
            )
            cb.grid(row=i // 2, column=i % 2, sticky='w', padx=10, pady=2)
            self.option_vars.append((opt, var))


        # --- 3. 色付きラベル ---
        self.altnum = 45  # 初期値。後で main から変更可能。

        color_label_frame = tk.Frame(self.root)
        color_label_frame.pack(pady=10, fill='x', padx=10)

        self.yellow_text_label = tk.Label(
            color_label_frame, text="Appearance of Yellow", font=("Arial", 12)
        )
        self.yellow_text_label.pack(side=tk.LEFT, padx=(0, 10))

        self.color_label = tk.Label(
            color_label_frame, text=f"Value: {self.altnum}", font=("Arial", 12, "bold")
        )
        self.color_label.pack(side=tk.LEFT)

        self.update_color_label()  # 初回色設定

        # --- 4. 解像度ラベル ---
        resolution_label = tk.Label(
            self.root,
            text="Resolution: Only supports 1920x1080",
            font=("Arial", 10)
        )
        resolution_label.pack(side=tk.BOTTOM, pady=10)

        # --- 5. 4つのボタン ---
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        self.all_result_btn = tk.Button(
            button_frame, text="All Result", width=12, command=self.open_all_result
        )
        self.all_result_btn.pack(side=tk.LEFT, padx=5)

        self.today_result_btn = tk.Button(
            button_frame, text="Today Result", width=12, command=self.open_today_result
        )
        self.today_result_btn.pack(side=tk.LEFT, padx=5)

        self.all_close_gage_btn = tk.Button(
            button_frame, text="All Close gage", width=12, command=self.open_all_close_gage
        )
        self.all_close_gage_btn.pack(side=tk.LEFT, padx=5)

        self.today_close_gage_btn = tk.Button(
            button_frame, text="Today Close gage", width=12, command=self.open_today_close_gage
        )
        self.today_close_gage_btn.pack(side=tk.LEFT, padx=5)

        # --- 7. テキストボックス ---
        textbox_frame = tk.Frame(self.root)
        textbox_frame.pack(side=tk.BOTTOM, pady=15)

        tk.Label(textbox_frame, text="Max entry times:", font=("Arial", 11)).grid(row=0, column=0, padx=5, sticky='e')
        self.max_active_entry = tk.Entry(textbox_frame, font=("Arial", 11), width=10)
        self.max_active_entry.grid(row=0, column=1, padx=5)

        tk.Label(textbox_frame, text="Challenge entry duration times:", font=("Arial", 11)).grid(row=1, column=0, padx=5, sticky='e')
        self.challenge_entry = tk.Entry(textbox_frame, font=("Arial", 11), width=10)
        self.challenge_entry.grid(row=1, column=1, padx=5)

        # Saveボタン（橙色背景）
        save_button = tk.Button(
            self.root,
            text="Save",
            font=("Arial", 11),
            bg="#FFA500",       # オレンジ色
            fg="black",
            command=self.save_settings
        )
        save_button.pack(side=tk.BOTTOM, pady=10)


        # 起動時に設定を読み込む
        self.load_settings()

    def update_color_label(self):
        num = self.altnum
        if num >= 80:
            color = "red"
        elif num >= 50:
            color = "dark goldenrod"
        else:
            color = "blue"
        self.color_label.config(fg=color, text=f"Value: {num}")

    def on_go_clicked(self):
        self.go_button.config(state=tk.DISABLED)
        self.login_info.append("hello")
        self.login_info.append("message")
        print("Go clicked: 'hello' and 'message' added to login_info")

    def open_file_with_notepad(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return
        try:
            subprocess.Popen(['notepad.exe', filename])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def open_all_result(self):
        self.open_file_with_notepad("log_buffer.txt")

    def open_all_close_gage(self):
        self.open_file_with_notepad("log_buffer2.txt")

    def open_today_filtered_file(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return

        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        filtered_lines = []

        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(today_str):
                        filtered_lines.append(line)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return

        if not filtered_lines:
            messagebox.showinfo("Info", f"No entries found for today ({today_str}) in {filename}.")
            return

        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as tmp_file:
                tmp_file.writelines(filtered_lines)
                tempname = tmp_file.name
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create temp file: {e}")
            return

        try:
            subprocess.Popen(['notepad.exe', tempname])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open temp file: {e}")

    def open_today_result(self):
        self.open_today_filtered_file("log_buffer.txt")

    def open_today_close_gage(self):
        self.open_today_filtered_file("log_buffer2.txt")

    def save_settings(self):
        data = {
            "check_states": {opt: var.get() for opt, var in self.option_vars},
            "max_entry_times": self.max_active_entry.get(),
            "challenge_entry_times": self.challenge_entry.get(),
            "altnum": self.altnum,
        }
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                import json
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Info", "Settings saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def load_settings(self):
        import json
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # チェックボックスの状態復元
                check_states = data.get("check_states", {})
                for opt, var in self.option_vars:
                    var.set(check_states.get(opt, False))
                # テキストボックスの値復元
                self.max_active_entry.delete(0, tk.END)
                self.max_active_entry.insert(0, data.get("max_entry_times", ""))
                self.challenge_entry.delete(0, tk.END)
                self.challenge_entry.insert(0, data.get("challenge_entry_times", ""))
                # altnum値復元し色更新
                self.altnum = data.get("altnum", 45)
                self.update_color_label()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load settings: {e}")
rescnt = 0

def tarrun(app, xxx=0, zzz=0,yyy=0,vvv=0,maxlimit=10):
    # 左モニタ取得
    with mss.mss() as sct:
        left_monitor = None
        for m in sct.monitors[1:]:
            if m['left'] < 0:
                left_monitor = m
                break
        if left_monitor is None:
            left_monitor = sct.monitors[1]

    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示

    clicker = ImageClicker(confidence=0.8, max_attempts=5, wait_time=1)
    
    maxcnt = 0
    # xxx = 0 #1:ON  0:OFF　空の時のみ　開ける

    # zzz = 1 #すべて空あける

    # yyy = 1 #buyキャンセル

    # vvv = 1 #Victory

    wait_for_idle_flag = 1 #wait 0:off

    # maxlimit = 44
    timespan = random.uniform(1.1, 2.2) 
    timespan_10 = random.uniform(1.5, 5.5) 
    timespan_20 = random.uniform(5.2, 30.5) 
    time.sleep(timespan-1)
    offx = random.uniform(0.5, 7.3)
    offy = random.uniform(0.2, 5.5)


    # if 1==zzz:
    #         image_path = r'D:\RustGo\image\open_box_black.PNG'
    #         # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
    #         res = clicker.find_image_on_monitor(left_monitor, image_path)
    #         if res == True:
    #             time.sleep(timespan_20)
    #             image_path = r'D:\RustGo\image\open_box_black.PNG'
    #             res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40" ,retry=2)
    #             time.sleep(timespan)  # 次のチェックまで1秒待機            
    #             if res== False:                
    #                 messagebox.showinfo("終了", "エラー終了しました")
    #                 exit()
    #             time.sleep(timespan)
    #             image_path = r'D:\RustGo\image\box_move.PNG'
    #             res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
    #             time.sleep(timespan)  # 次のチェックまで1秒待機            
    #             if res== False:                
    #                 messagebox.showinfo("終了", "エラー終了しました")
    #                 exit()                    




    images = [
        (r'D:\RustGo\image\black.png', "."),
        (r'D:\RustGo\image\yellow.png', "黄"),
        (r'D:\RustGo\image\red.png', "赤")
    ]
    if 1==1:
        image_path = r'D:\RustGo\image\buy_ok.PNG'
        # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
        res = clicker.find_image_on_monitor(left_monitor, image_path)
        if res == True:
            time.sleep(timespan)

            image_path = r'D:\RustGo\image\buy_ok_X.PNG'
            res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=1)
            time.sleep(timespan)  # 次のチェックまで1秒待機            
            if res== False:                
                messagebox.showinfo("終了", "エラー終了しました")
                exit()
    image_path = r'D:\RustGo\image\buttle5.PNG'
    # image_path = r'D:\RustGo\image\black.PNG'
    # image_path = r'D:\RustGo\image\red.PNG'
    # 左モニタで画像をクリック    
    res = clicker.attempt_click_on_monitor(left_monitor, image_path, offset=(offx, offy), retry=2)
    # res = clicker.attempt_click_on_monitor(left_monitor, image_path,option =(500,600))
    if res == True:
        while True:

            if 1==yyy: #買い
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\buy_ok.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan)

                    image_path = r'D:\RustGo\image\buy_ok_X.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=2)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()  

            if 1==1:
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\4499.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan)

                    image_path = r'D:\RustGo\image\buy_ok_X.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=1)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()



            # if vvv==1:
            #     time.sleep(timespan) 
            #     image_path = r'D:\RustGo\image\toribo.PNG'
            #     # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
            #     res = clicker.find_image_on_monitor(left_monitor, image_path)
            #     if res == True:
            #         time.sleep(timespan_20)
            #         image_path = r'D:\RustGo\image\toribo.PNG'
            #         res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=3)
            #         time.sleep(timespan)  # 次のチェックまで1秒待機            
            #         if res== False:                
            #             messagebox.showinfo("終了", "エラー終了しました")
            #             exit()
            #         time.sleep(timespan)
            #         image_path = r'D:\RustGo\image\box_move.PNG'
            #         res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
            #         time.sleep(timespan)  # 次のチェックまで1秒待機            
            #         if res== False:                                
            #             messagebox.showinfo("終了", "エラー終了しました")
            #             exit()
            if vvv==1:
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\vikutori.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan_20)
                    image_path = r'D:\RustGo\image\vikutori.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, offset=(offx, offy-75 ), retry=3)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False: 
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()

                    time.sleep(timespan) 
                    image_path = r'D:\RustGo\image\4499.PNG'
                    # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                    res = clicker.find_image_on_monitor(left_monitor, image_path)
                    if res == True:
                        time.sleep(timespan)
                        image_path = r'D:\RustGo\image\buy_ok_X.PNG'
                        res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=1)
                        time.sleep(timespan)  # 次のチェックまで1秒待機            
                        if res== False:                
                            messagebox.showinfo("終了", "エラー終了しました")
                            exit()  

                        # time.sleep(timespan) 
                        # image_path = r'D:\RustGo\image\vikutori.PNG'
                        # # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                        # res = clicker.find_image_on_monitor(left_monitor, image_path)
                        # if res == True:
                        #     time.sleep(timespan_20)
                        #     image_path = r'D:\RustGo\image\vikutori.PNG'
                        #     res = clicker.attempt_click_on_monitor(left_monitor, image_path, offset=(offx, offy-75 ), retry=3)
                        #     time.sleep(timespan)  # 次のチェックまで1秒待機            
                        #     if res== False: 
                        #         messagebox.showinfo("終了", "エラー終了しました")
                        #         exit()

                    time.sleep(timespan)
                    image_path = r'D:\RustGo\image\box_move.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()

            if zzz==1:
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\open_box_black.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan_20)
                    image_path = r'D:\RustGo\image\open_box_black.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=3)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()
                    time.sleep(timespan)
                    image_path = r'D:\RustGo\image\box_move.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()
                image_path = r'D:\RustGo\image\open_box_red.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan_20)
                    image_path = r'D:\RustGo\image\open_box_red.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=3)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()
                    time.sleep(timespan)
                    image_path = r'D:\RustGo\image\box_move.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()                        

            if 1==xxx :
                time.sleep(timespan) 
                while True: #空のビコトリBOXあり
                    image_path = r'D:\RustGo\image\BOX_emp.PNG'
                    # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                    res = clicker.find_image_on_monitor(left_monitor, image_path)
                    if res == True:
                        time.sleep(timespan)
                        break                    
                    if 1==1:
                        image_path = r'D:\RustGo\image\open_box_black.PNG'
                        # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                        res = clicker.find_image_on_monitor(left_monitor, image_path)
                        if res == True:
                            time.sleep(timespan_20)
                            image_path = r'D:\RustGo\image\open_box_black.PNG'
                            res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=2)
                            time.sleep(timespan)  # 次のチェックまで1秒待機            
                            if res== False:                
                                messagebox.showinfo("終了", "エラー終了しました")
                                exit()
                            time.sleep(timespan)
                            image_path = r'D:\RustGo\image\box_move.PNG'
                            res = clicker.attempt_click_on_monitor(left_monitor, image_path, label = "40",option =(500,600) ,retry=2)
                            time.sleep(timespan)  # 次のチェックまで1秒待機            
                            if res== False:                
                                messagebox.showinfo("終了", "エラー終了しました")
                                exit()


            if 1==yyy: #買い
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\buy_ok.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan)

                    image_path = r'D:\RustGo\image\buy_ok_X.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=2)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit() 

            time.sleep(timespan)  
            image_path = r'D:\RustGo\image\reage_down.PNG' #リーグダウン
            res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=1)
            time.sleep(timespan)  # 次のチェックまで1秒待機            
            # if res== False:                
            #     messagebox.showinfo("終了", "エラー終了しました")
            #     exit()   

            timespan = random.uniform(1.5, 2.5) 
            time.sleep(timespan)
            # timespan = 2
            image_path = r'D:\RustGo\image\buttle_true.PNG'
            # 左モニタで画像をクリック
            res = clicker.attempt_click_on_monitor(left_monitor, image_path, offset=(offx, offy))
            if res == False:
                messagebox.showinfo("終了", "エラー 終了しました:" + image_path)
                exit()
            time.sleep(10)

            if 1==1:
                time.sleep(timespan) 
                image_path = r'D:\RustGo\image\4499.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == True:
                    time.sleep(timespan)

                    image_path = r'D:\RustGo\image\buy_ok_X.PNG'
                    res = clicker.attempt_click_on_monitor(left_monitor, image_path, retry=1)
                    time.sleep(timespan)  # 次のチェックまで1秒待機            
                    if res== False:                
                        messagebox.showinfo("終了", "エラー終了しました")
                        exit()


            while True:
                image_path = r'D:\RustGo\image\tajayu.PNG'
                # res = clicker.attempt_click_on_monitor(left_monitor, image_path)
                res = clicker.find_image_on_monitor(left_monitor, image_path)
                if res == False:
                    time.sleep(timespan)
                    break
                time.sleep(timespan)
            time.sleep(timespan*3)
            offx = random.uniform(0.5, 7.3)
            offy = random.uniform(0.2, 5.5)            
            image_path = r'D:\RustGo\image\meisei_down.PNG'
            label = 'ｘ'
            res = clicker.attempt_click_on_monitor(left_monitor, image_path, label, offset=(offx, offy), retry=2)
            time.sleep(timespan)  # 次のチェックまで待機            
            if res== False: #
                for img_path, label in images:
                    res = clicker.attempt_click_on_monitor(left_monitor, img_path, label,option =(500,600), offset=(offx, offy), retry=2)
                    time.sleep(timespan)  # 次のチェックまで待機
                    if res==True:
                        break
                if res == False:
                    messagebox.showinfo("終了", "エラー 終了しました:" + str(images))
                    exit()

            # 読み込みたいログファイル名・パス
            rescnt = get_lines_since_yellow(log_file_out)
            app.altnum = rescnt

            maxcnt = maxcnt + 1
            if maxcnt > maxlimit:
                # app.root.after(0, app.root.destroy)
                # stop_event.set()  # スレッド側も終了指示                
                messagebox.showinfo("終了", "終了しました")
                exit()
            time.sleep(timespan)

stop_event = threading.Event()

if __name__ == "__main__":
    root = tk.Tk()
    login_info = []
    app = LoginApp(root, login_info)

    app.altnum = 70
    app.update_color_label()
    root.iconbitmap("lannister_115487.ico")

    def check_login_info():
        if login_info:
            print("login_info contents:", login_info)
        root.after(1000, check_login_info)

    root.after(1000, check_login_info)

    # tarrun を新スレッドで開始
    thread = threading.Thread(target=tarrun, args=(app,), kwargs=dict(xxx=0, zzz=0, yyy=0, vvv=0, maxlimit=10))
    thread.start()

    def on_closing():
        stop_event.set()     # スレッド停止指示
        thread.join(timeout=5)  # 最大5秒待機
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()