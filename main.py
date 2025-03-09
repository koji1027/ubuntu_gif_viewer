import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import threading
import random
import sys

args = sys.argv

os.environ["DISPLAY"] = ":1"

# 特定のGIFファイルのパスを指定
gif_path = input("GIFファイル名を入力してください: ")
if gif_path == "":
    gif_path = "images/bird_rainbow.gif"
else:
    gif_path = "images/" + gif_path
image_folder = "images"

class GifDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Viewer")

        # 全画面表示を有効化
        if "-f" in args:
            self.root.attributes('-fullscreen', True)

        # キーボードイベントを設定
        self.root.bind("<F11>", self.toggle_fullscreen)  # F11でフルスクリーン切り替え
        self.root.bind("<q>", self.quit_program)  # 'q'で終了
        self.root.bind("<Configure>", self.on_resize)  # ウィンドウサイズ変更時

        # ラベルを作成（画像を表示）
        self.label = tk.Label(root, bg="black")
        self.label.pack(expand=1, fill="both")

        # GIFを非同期に表示
        self.frames = []
        self.original_frames = []  # オリジナルのフレームを保持
        self.current_frame = 0
        self.is_loading = True
        self.delays = []  # 遅延時間を保持
        self.load_gif(gif_path)

        # ウィンドウを閉じる処理（ウィンドウの右上の×ボタンも有効）
        self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

    def load_gif(self, gif_path):
        """GIF画像を非同期で読み込む"""
        def load_frames():
            image = Image.open(gif_path)

            # GIFのフレームを取得し、オリジナルサイズで保存
            self.original_frames = [img.copy() for img in ImageSequence.Iterator(image)]
            self.delays = [image.info['duration'] for _ in self.original_frames]

            self.is_loading = False
            self.current_frame = 0  # 新しいGIFに変更するためにフレームをリセット
            self.resize_frames()  # 初回リサイズ
            self.animate_gif()  # アニメーション開始

        # フレーム読み込みを別スレッドで実行
        threading.Thread(target=load_frames, daemon=True).start()

    def resize_frames(self):
        """アスペクト比を維持しながら、ウィンドウサイズにフィットするようにGIFをリサイズ"""
        if not self.original_frames:
            return

        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # ウィンドウがまだ小さい場合、デフォルトの画面サイズを取得
        if window_width < 10 or window_height < 10:
            window_width = self.root.winfo_screenwidth()
            window_height = self.root.winfo_screenheight()

        self.frames = []

        for img in self.original_frames:
            original_width, original_height = img.size

            # アスペクト比を維持してリサイズ
            ratio = min(window_width / original_width, window_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_img = img.resize((new_width, new_height), Image.NEAREST)

            # 黒背景のキャンバスを作成
            canvas = Image.new("RGBA", (window_width, window_height), "black")
            x_offset = (window_width - new_width) // 2
            y_offset = (window_height - new_height) // 2

            # 中央にリサイズした画像を貼り付け
            canvas.paste(resized_img, (x_offset, y_offset))

            self.frames.append(ImageTk.PhotoImage(canvas))

    def animate_gif(self):
        """GIFアニメーションを表示"""
        if not self.is_loading and self.frames:
            self.label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.root.after(self.delays[self.current_frame], self.animate_gif)

    def on_resize(self, event):
        """ウィンドウサイズ変更時にGIFをリサイズ"""
        self.resize_frames()

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
            elif command == "full":
                app.toggle_fullscreen()
        

        except EOFError:
            break

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    app = GifDisplayApp(root)

    # 入力を別スレッドで監視（メインスレッドがTkinterをブロックしないように）
    input_thread = threading.Thread(target=listen_for_input, args=(app,), daemon=True)
    input_thread.start()

    root.mainloop()
