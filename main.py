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
    if not gif_path.endswith(".gif"):
        gif_path += ".gif"
    
    gif_path = "images/" + gif_path

    # GIFファイルが存在するか確認
    if not os.path.exists(gif_path):
        print(f"エラー: '{gif_path}' が見つかりません。")
        gif_path = "images/bird_rainbow.gif"
image_folder = "images"

files = [f for f in os.listdir(image_folder) if f.endswith('.gif')]

menu_win = None

class GifDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Viewer")
        self.menu_timer = None  # タイマーのIDを管理
        self.slide_show_timer = None  # スライドショーのタイマーIDを管理

        # 全画面表示を有効化
        if "-f" in args:
            self.root.attributes('-fullscreen', True)

        # キーボードイベントを設定
        self.root.bind("<f>", self.toggle_fullscreen)  # F11でフルスクリーン切り替え
        self.root.bind("<m>", self.show_menu)
        self.root.bind("<q>", self.quit_program)  # 'q'で終了
        self.root.bind("<Configure>", self.on_resize)  # ウィンドウサイズ変更時
        self.root.bind("<KeyPress-n>", self.next_gif)

        #左クリックでメニュー表示
        self.root.bind("<Button-1>", self.show_menu)

        filename = os.path.basename(gif_path)
        self.label = tk.Label(root, text=filename, bg="black", fg="white")
        self.label.pack(fill="x")
        # ラベルを作成（画像を表示）
        self.label = tk.Label(root, bg="black")
        self.label.pack(expand=1, fill="both")

        # GIFを非同期に表示
        self.frames = []
        self.original_frames = []  # オリジナルのフレームを保持
        self.current_frame = 0
        self.is_loading = True
        self.delays = []  # 遅延時間を保持
        self.load_gif()

        # ウィンドウを閉じる処理（ウィンドウの右上の×ボタンも有効）
        self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

        # ウィンドウを最前面に表示
        self.root.attributes("-topmost", True)

        # ウィンドウを右下に移動
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"+{screen_width-400}+{screen_height-300}")

        self.reset_slide_show_timer()

    def load_gif(self):
        global gif_path
        global menu_win
        if menu_win != None:
            menu_win.destroy()

        """GIF画像を非同期で読み込む"""
        def load_frames():
            global gif_path
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
        """Fでフルスクリーン切り替え"""
        state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not state)

    def quit_program(self, event=None):
        """qキーまたはウィンドウの閉じるボタンで終了"""
        self.root.quit()

    def show_menu(self, event=None):
        global menu_win
        if menu_win == None or not menu_win.winfo_exists():
            menu_win = tk.Toplevel()
            menu_win.attributes("-topmost", True)  # 最前面に表示
            menu_win.bind("<m>", self.show_menu)
            menu_win.bind("<q>", self.quit_program)  # 'q'で終了
            menu_win.bind("<Configure>", self.on_resize)  # ウィンドウサイズ変更時
            #menu_win.geometry("400x800")
            label_menu = tk.Label(menu_win, text="メニュー")
            label_menu.pack()
            description = tk.Label(menu_win, text="行いたい操作を選択してください。")
            description.pack()
            button = tk.Button(menu_win, text="GIFを変更", command=self.show_files)
            button.pack()
            button = tk.Button(menu_win, text="終了", command=self.quit_program)
            button.pack()

            # タイマーをリセットして自動閉じる処理を開始
            self.reset_menu_timer()

            # メニューウィンドウ内の操作でもタイマーをリセット
            menu_win.bind("<Motion>", self.reset_menu_timer)

        else:
            menu_win.destroy()
            menu_win = None

    def show_files(self, event=None):
        global menu_win

        # メニューのラベルとボタンを削除
        for widget in menu_win.winfo_children():
            widget.destroy()

        # 各ファイル名のボタンを作成
        for filename in files:
            button = tk.Button(menu_win, text=filename, command=lambda f=filename: self.change_gif(f))
            button.pack()

    def reset_menu_timer(self, event=None):
        """メニューの自動閉じるタイマーをリセット"""
        if self.menu_timer:
            self.root.after_cancel(self.menu_timer)  # 以前のタイマーをキャンセル
        self.menu_timer = self.root.after(5000, self.close_menu)  # 5秒後に閉じる

    def reset_slide_show_timer(self):
        """スライドショーの自動切り替えタイマーをリセット"""
        if self.slide_show_timer:
            self.root.after_cancel(self.slide_show_timer)
        self.slide_show_timer = self.root.after(20000, self.next_gif)

    def next_gif(self, event=None):
        self.reset_slide_show_timer()
        """次のGIFに切り替え"""
        global gif_path
        filename = os.path.basename(gif_path) # 現在のGIFファイル名(拡張子あり)
        global files
        if filename in files:
            index = files.index(filename)
            next_index = (index + 1) % len(files)
            gif_path = os.path.join(image_folder, files[next_index])
            self.load_gif()
            print("次のGIFに切り替えました。")
        else:
            print("エラー: GIFが見つかりません。filename=", filename, "files=", files[-1])

    def close_menu(self):
        """メニューウィンドウを閉じる"""
        global menu_win
        if menu_win and menu_win.winfo_exists():
            menu_win.destroy()
            menu_win = None

    def change_gif(self, filename):
        """GIFを変更"""
        global gif_path
        gif_path = os.path.join(image_folder, filename)
        self.load_gif()

def listen_for_input(app):
    """ターミナルからの入力を監視し 'c 画像名.gif' でGIFを変更"""
    while True:
        try:
            command = input().strip()
            if command.startswith("c "):  # "c " で始まる場合、画像を変更
                filename = command[2:].strip()
                global gif_path
                gif_path = os.path.join(image_folder, filename)
                if os.path.exists(gif_path):
                    app.load_gif()  # GIFを読み込み直して表示
                    print("成功!")
                else:
                    print(f"エラー: '{filename}' が見つかりません。")
            elif command == "q":
                app.quit_program()
            elif command == "r":
                # ランダムなGIFファイルを選択（pngファイルは除外）
                filename = random.choice(files)
                gif_path = os.path.join(image_folder, filename)
                # ファイルが存在する場合、GIFを変更
                if os.path.exists(gif_path):
                    app.load_gif()
                    print("成功!")
                else:
                    print(f"エラー: '{filename}' が見つかりません。")
            elif command == "s":
                print(files)
            elif command == "full":
                app.toggle_fullscreen()
            elif command == "n":
                app.next_gif()
        
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
