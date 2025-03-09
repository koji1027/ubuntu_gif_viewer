import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import threading
import random

# 特定のGIFファイルのパスを指定
gif_path = "images/meow_rave.gif"
image_folder = "images"

class GifDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Viewer")

        # 全画面表示を有効化
        self.root.attributes('-fullscreen', True)

        # キーボードイベントを設定
        self.root.bind("<F11>", self.toggle_fullscreen)  # F11でフルスクリーン切り替え
        self.root.bind("<q>", self.quit_program)  # 'q'で終了

        # ラベルを作成（画像を表示）
        self.label = tk.Label(root, bg="black")
        self.label.pack(expand=1, fill="both")

        # GIFを非同期に表示
        self.frames = []
        self.current_frame = 0
        self.is_loading = True
        self.load_gif(gif_path)

        # ウィンドウを閉じる処理（ウィンドウの右上の×ボタンも有効）
        self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

    def load_gif(self, gif_path):
        """GIF画像を非同期で読み込む"""
        def load_frames():
            image = Image.open(gif_path)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # GIFのフレームを取得し、リサイズしない
            self.frames = []
            delays = []  # 各フレームの遅延時間（ms）

            for img in ImageSequence.Iterator(image):
                # フレームをリサイズして保存
                self.frames.append(ImageTk.PhotoImage(img.resize((screen_width, screen_height), Image.NEAREST)))
                #self.frames.append(ImageTk.PhotoImage(img.resize((screen_width, screen_height), Image.LANCZOS)))
                # 各フレームの遅延時間を取得
                delays.append(image.info['duration'])

            self.is_loading = False
            self.current_frame = 1  # 新しいGIFに変更するためにフレームをリセット
            self.animate_gif(delays)  # 遅延時間を渡す

        # フレーム読み込みを別スレッドで実行
        threading.Thread(target=load_frames, daemon=True).start()

    def animate_gif(self, delays):
        """GIFアニメーションを表示"""
        if not self.is_loading and self.frames:
            self.label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            if self.current_frame == 0:
                self.current_frame = 1

            # 1フレームあたりの遅延時間（ms）を取得
            delay_time = delays[self.current_frame]

            # 次のフレームを表示するためにdelay_timeミリ秒後に呼び出し
            self.root.after(delay_time, self.animate_gif, delays)

    def toggle_fullscreen(self, event=None):
        """F11でフルスクリーン切り替え"""
        state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not state)

    def quit_program(self, event=None):
        """qキーまたはウィンドウの閉じるボタンで終了"""
        self.root.quit()

def listen_for_input(app):
    """ターミナルからの入力を監視し 'c 画像名.gif' でGIFを変更"""
    while True:
        try:
            command = input().strip()
            if command.startswith("c "):  # "c " で始まる場合、画像を変更
                filename = command[2:].strip()
                gif_path = os.path.join(image_folder, filename)
                if os.path.exists(gif_path):
                    app.load_gif(gif_path)  # GIFを読み込み直して表示
                    print("成功!")
                else:
                    print(f"エラー: '{filename}' が見つかりません。")
            elif command == "q":
                app.quit_program()
            elif command == "r":
                # ランダムなGIFファイルを選択（pngファイルは除外）
                files = [f for f in os.listdir(image_folder) if f.endswith('.gif')]
                filename = random.choice(files)
                gif_path = os.path.join(image_folder, filename)
                app.load_gif(gif_path)
                print("成功!")
            elif command == "s":
                files = [f for f in os.listdir(image_folder) if f.endswith('.gif')]
                print(files)

        except EOFError:
            break

if __name__ == "__main__":
    root = tk.Tk()
    app = GifDisplayApp(root)

    # 入力を別スレッドで監視（メインスレッドがTkinterをブロックしないように）
    input_thread = threading.Thread(target=listen_for_input, args=(app,), daemon=True)
    input_thread.start()

    root.mainloop()
