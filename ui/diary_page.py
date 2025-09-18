from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import datetime
import os
import json
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
import shutil
from kivy.uix.videoplayer import VideoPlayer
import cv2
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as KivyImage
import io
from ui.utils import open_date_picker, open_image_chooser


class Card(BoxLayout):
    def __init__(self, date, text, images=None, videos=None, entry_index=None, diary_page=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(220) if (images or videos) else dp(100),
            padding=dp(12),
            spacing=dp(6),
            **kwargs,
        )
        # Card background with light blue and thin black border
        with self.canvas.before:
            Color(0.90, 0.95, 1, 1)  # Light blue
            self.bg = RoundedRectangle(
                radius=[dp(16)],
                pos=self.pos,
                size=self.size,
            )
            Color(0, 0, 0, 1)  # Black
            from kivy.graphics import Line
            self.border_line = Line(
                rounded_rectangle=[
                    self.x, self.y, self.width, self.height, dp(16)
                ],
                width=1.5
            )
        self.bind(pos=self.update_bg, size=self.update_bg)
        # Date header + Edit button
        header_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
        date_label = Label(
            text=date,
            bold=True,
            font_size=18,
            color=(0.2, 0.4, 0.7, 1),
            halign="left",
            valign="middle",
        )
        date_label.bind(size=date_label.setter("text_size"))
        edit_btn = Button(text="Edit", size_hint_x=None, width=dp(60), height=dp(28))
        if diary_page is not None and entry_index is not None:
            edit_btn.bind(on_release=lambda instance: diary_page.open_edit_popup(entry_index))
        header_layout.add_widget(date_label)
        header_layout.add_widget(edit_btn)
        self.add_widget(header_layout)

        # Images
        if images:
            from kivy.uix.gridlayout import GridLayout
            img_grid = GridLayout(
                cols=min(3, len(images)),
                spacing=dp(8),
                size_hint_y=None,
                row_default_height=dp(140),
                row_force_default=True,
                padding=[0, 0, 0, 0],
            )
            rows = (len(images) + 2) // 3
            img_grid.height = rows * (dp(140) + dp(8))
            for rel_img_path in images[:9]:
                img_path = os.path.join(DiaryPage.IMAGES_DIR, rel_img_path)
                thumb = Image(
                    source=img_path,
                    size_hint=(1, 1),
                    fit_mode="contain",
                )
                def open_img_popup(instance, path=img_path):
                    popup = Popup(
                        title="Image",
                        content=Image(source=path, fit_mode="contain"),
                        size_hint=(None, None),
                        size=(dp(500), dp(500)),
                        auto_dismiss=True,
                    )
                    popup.open()
                thumb.bind(
                    on_touch_down=lambda instance, touch, path=img_path: (
                        open_img_popup(instance, path)
                        if instance.collide_point(*touch.pos) and touch.button == 'left'
                        else None
                    )
                )
                img_grid.add_widget(thumb)
            self.add_widget(img_grid)

        # Videos
        if videos:
            from kivy.uix.gridlayout import GridLayout
            vid_grid = GridLayout(
                cols=min(3, len(videos)),
                spacing=dp(8),
                size_hint_y=None,
                row_default_height=dp(140),
                row_force_default=True,
                padding=[0, 0, 0, 0],
            )
            rows = (len(videos) + 2) // 3
            vid_grid.height = rows * (dp(140) + dp(8))
            for rel_vid_path in videos[:9]:
                vid_path = os.path.join(DiaryPage.VIDEOS_DIR, rel_vid_path)
                # Try to extract the first frame as a thumbnail
                thumbnail_widget = None
                try:
                    cap = cv2.VideoCapture(vid_path)
                    success, frame = cap.read()
                    cap.release()
                    if success:
                        # Convert BGR to RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Encode as PNG
                        _, buf = cv2.imencode('.png', frame)
                        data = io.BytesIO(buf.tobytes())
                        core_img = CoreImage(data, ext='png')
                        thumbnail_widget = KivyImage(
                            texture=core_img.texture,
                            size_hint=(1, 1),
                            fit_mode="contain",
                        )
                    else:
                        thumbnail_widget = KivyImage(
                            source="video_placeholder.png",
                            size_hint=(1, 1),
                            fit_mode="contain",
                        )
                except Exception as e:
                    thumbnail_widget = KivyImage(
                        source="video_placeholder.png",
                        size_hint=(1, 1),
                        fit_mode="contain",
                    )
                def open_video_popup(instance, path=vid_path):
                    player = VideoPlayer(source=path, state='play', options={'allow_stretch': True})
                    popup = Popup(
                        title="Video",
                        content=player,
                        size_hint=(None, None),
                        size=(dp(500), dp(500)),
                        auto_dismiss=True,
                    )
                    def on_dismiss(_):
                        player.state = 'stop'
                    popup.bind(on_dismiss=on_dismiss)
                    popup.open()
                thumbnail_widget.bind(
                    on_touch_down=lambda instance, touch, path=vid_path: (
                        open_video_popup(instance, path)
                        if instance.collide_point(*touch.pos) and touch.button == 'left'
                        else None
                    )
                )
                vid_grid.add_widget(thumbnail_widget)
            self.add_widget(vid_grid)

        # Entry text below images/videos with white background
        text_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(40),
            padding=[dp(8), dp(4), dp(8), dp(4)],
        )
        with text_box.canvas.before:
            Color(1, 1, 1, 1)  # White
            text_box.bg = RoundedRectangle(
                pos=text_box.pos,
                size=text_box.size,
                radius=[dp(8)]
            )
        def update_text_bg(instance, value):
            text_box.bg.pos = text_box.pos
            text_box.bg.size = text_box.size
        text_box.bind(pos=update_text_bg, size=update_text_bg)
        entry_label = Label(
            text=text,
            font_size=15,
            color=(0.1, 0.1, 0.1, 1), # Dark grey
            halign="left",
            valign="top",
        )
        entry_label.bind(size=entry_label.setter("text_size"))
        text_box.add_widget(entry_label)
        self.add_widget(text_box)
        # Adjust card height to fit images/videos and text
        self.height = (
            (img_grid.height if images else 0)
            + (vid_grid.height if videos else 0)
            + dp(40) + dp(28) + dp(24)
        )

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border_line.rounded_rectangle = [
            self.x, self.y, self.width, self.height, dp(16)
        ]


class DiaryPage(Screen):
    DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/diary_page/diary_entries.json")
    IMAGES_DIR = os.path.join(os.path.dirname(__file__), "../data/diary_page/diaries_images")
    VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "../data/diary_page/diary_videos")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entries = self.load_entries()
        # Main background
        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(16), dp(16), dp(16)],
            spacing=dp(12),
        )
        with main_layout.canvas.before:
            Color(0.2, 0.4, 0.7, 1) # Dark blue
            self.bg_rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size, radius=[0])

        def update_bg_rect(instance, value):
            self.bg_rect.pos = main_layout.pos
            self.bg_rect.size = main_layout.size

        main_layout.bind(pos=update_bg_rect, size=update_bg_rect)

        header_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(48)
        )
        header = Label(
            text="Diary Page", font_size=24, bold=True, color=(0.2, 0.4, 0.7, 1)
        )
        add_btn = Button(text="+ Add", size_hint_x=None, width=dp(80))
        add_btn.bind(on_release=self.open_add_popup)
        header_layout.add_widget(header)
        header_layout.add_widget(add_btn)
        main_layout.add_widget(header_layout)
        # Scrollable area
        self.scrollview = ScrollView()
        self.feed = GridLayout(
            cols=1, spacing=dp(16), size_hint_y=None, padding=[0, 0, 0, dp(16)]
        )
        self.feed.bind(minimum_height=self.feed.setter("height"))
        self.refresh_feed()
        self.scrollview.add_widget(self.feed)
        main_layout.add_widget(self.scrollview)
        self.add_widget(main_layout)

    def load_entries(self):
        path = os.path.abspath(self.DATA_FILE)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        else:
            return [
                {
                    "date": "2025-07-14",
                    "text": "😃 Today i started creating this new app.",
                },
            ]

    def save_entries(self):
        path = os.path.abspath(self.DATA_FILE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving diary entries: {e}")

    def refresh_feed(self):
        self.feed.clear_widgets()
        # Sort entries by date (descending, newest first)
        sorted_entries = sorted(
            self.entries,
            key=lambda entry: entry.get("date", ""),
            reverse=True
        )
        for idx, entry in enumerate(sorted_entries):
            images = entry.get("images", [])
            videos = entry.get("videos", [])
            self.feed.add_widget(Card(
                entry["date"], entry["text"], images=images, videos=videos,
                entry_index=self.entries.index(entry), diary_page=self
            ))

    def open_add_popup(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        entry_input = TextInput(
            hint_text="Write your diary entry...",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        today = datetime.date.today()
        selected_date = [today]
        selected_images = []
        selected_videos = []

        def update_date_btn_text():
            date_btn.text = selected_date[0].isoformat()

        date_btn = Button(text=today.isoformat(), size_hint_y=None, height=dp(40))
        def on_date_selected(new_date):
            selected_date[0] = new_date
            update_date_btn_text()
        date_btn.bind(on_release=lambda inst: open_date_picker(date_btn, selected_date, on_date_selected))

        # Image selection
        img_btn = Button(text="Add Photo(s)", size_hint_y=None, height=dp(40))
        img_thumbs_layout = BoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(70)
        )

        def open_image_chooser_wrapper(instance):
            def on_images_selected(selected):
                selected = selected[:4]
                selected_images.clear()
                os.makedirs(self.IMAGES_DIR, exist_ok=True)
                img_thumbs_layout.clear_widgets()
                for img_path in selected:
                    filename = os.path.basename(img_path)
                    dest_path = os.path.join(self.IMAGES_DIR, filename)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(self.IMAGES_DIR, filename)
                        counter += 1
                    try:
                        shutil.copy(img_path, dest_path)
                        rel_path = os.path.relpath(dest_path, self.IMAGES_DIR)
                        selected_images.append(rel_path)
                        img_thumbs_layout.add_widget(
                            Image(
                                source=dest_path,
                                size_hint=(None, None),
                                size=(dp(70), dp(70)),
                                allow_stretch=True,
                                keep_ratio=True,
                            )
                        )
                    except Exception as e:
                        print(f"Error copying image: {e}")
            open_image_chooser(
                img_btn, on_images_selected, multiselect=True, max_select=4, popup_size=(500, 400)
            )
        img_btn.bind(on_release=open_image_chooser_wrapper)

        # Video selection
        vid_btn = Button(text="Add Video(s)", size_hint_y=None, height=dp(40))
        vid_thumbs_layout = BoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(70)
        )

        def open_video_chooser(instance):
            fc_content = BoxLayout(
                orientation="vertical", spacing=dp(10), padding=dp(10)
            )
            filechooser = FileChooserIconView(
                filters=["*.mp4", "*.mov", "*.avi", "*.mkv"],
                multiselect=True,
                size_hint_y=None,
                height=dp(300),
            )
            btns = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10),
            )
            ok_btn = Button(text="OK")
            cancel_btn = Button(text="Cancel")
            btns.add_widget(ok_btn)
            btns.add_widget(cancel_btn)
            fc_content.add_widget(
                Label(
                    text="Select up to 4 videos",
                    font_size=16,
                    size_hint_y=None,
                    height=dp(30),
                )
            )
            fc_content.add_widget(filechooser)
            fc_content.add_widget(btns)
            fc_popup = Popup(
                title="",
                content=fc_content,
                size_hint=(None, None),
                size=(dp(500), dp(400)),
                auto_dismiss=False,
            )

            def set_videos(instance):
                selected = filechooser.selection[:4]
                selected_videos.clear()
                os.makedirs(self.VIDEOS_DIR, exist_ok=True)
                vid_thumbs_layout.clear_widgets()
                for vid_path in selected:
                    filename = os.path.basename(vid_path)
                    dest_path = os.path.join(self.VIDEOS_DIR, filename)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(self.VIDEOS_DIR, filename)
                        counter += 1
                    try:
                        shutil.copy(vid_path, dest_path)
                        rel_path = os.path.relpath(dest_path, self.VIDEOS_DIR)
                        selected_videos.append(rel_path)
                        placeholder_path = os.path.join(os.path.dirname(__file__), "video_placeholder.png")
                        vid_thumbs_layout.add_widget(
                            Image(
                                source=placeholder_path if os.path.exists(placeholder_path) else "",
                                size_hint=(None, None),
                                size=(dp(70), dp(70)),
                                allow_stretch=True,
                                keep_ratio=True,
                            )
                        )
                    except Exception as e:
                        print(f"Error copying video: {e}")
                fc_popup.dismiss()

            def cancel_fc(instance):
                fc_popup.dismiss()

            ok_btn.bind(on_release=set_videos)
            cancel_btn.bind(on_release=cancel_fc)
            fc_popup.open()

        vid_btn.bind(on_release=open_video_chooser)

        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10)
        )
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(
            Label(
                text="Add Diary Entry",
                font_size=18,
                bold=True,
                size_hint_y=None,
                height=dp(30),
            )
        )
        content.add_widget(entry_input)
        content.add_widget(date_btn)
        content.add_widget(img_btn)
        content.add_widget(img_thumbs_layout)
        content.add_widget(vid_btn)
        content.add_widget(vid_thumbs_layout)
        content.add_widget(btn_layout)
        popup = Popup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(600)),
            auto_dismiss=False,
        )

        def save_entry(instance):
            text = entry_input.text.strip()
            date = selected_date[0].isoformat()
            if text:
                self.entries.insert(
                    0, {
                        "date": date,
                        "text": text,
                        "images": list(selected_images),
                        "videos": list(selected_videos)
                    }
                )
                self.save_entries()
                self.refresh_feed()
            popup.dismiss()

        def cancel_entry(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        cancel_btn.bind(on_release=cancel_entry)
        popup.open()

    def open_edit_popup(self, entry_index):
        entry = self.entries[entry_index]
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        entry_input = TextInput(
            text=entry.get("text", ""),
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        # Date editing
        orig_date = entry.get("date", datetime.date.today().isoformat())
        selected_date = [datetime.date.fromisoformat(orig_date)]
        def update_date_btn_text():
            date_btn.text = selected_date[0].isoformat()
        date_btn = Button(text=selected_date[0].isoformat(), size_hint_y=None, height=dp(40))
        def on_date_selected(new_date):
            selected_date[0] = new_date
            update_date_btn_text()
        date_btn.bind(on_release=lambda inst: open_date_picker(date_btn, selected_date, on_date_selected))

        selected_images = entry.get("images", []).copy()
        selected_videos = entry.get("videos", []).copy()
        img_thumbs_layout = BoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(70)
        )
        vid_thumbs_layout = BoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(70)
        )

        def refresh_img_thumbs():
            img_thumbs_layout.clear_widgets()
            for rel_img_path in selected_images:
                img_path = os.path.join(self.IMAGES_DIR, rel_img_path)
                thumb = Image(
                    source=img_path,
                    size_hint=(None, None),
                    size=(dp(70), dp(70)),
                    allow_stretch=True,
                    keep_ratio=True,
                )
                remove_btn = Button(text="X", size_hint=(None, None), size=(dp(24), dp(24)))
                def remove_img(instance, img=rel_img_path):
                    if img in selected_images:
                        selected_images.remove(img)
                        refresh_img_thumbs()
                remove_btn.bind(on_release=remove_img)
                img_box = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(70), dp(94)))
                img_box.add_widget(thumb)
                img_box.add_widget(remove_btn)
                img_thumbs_layout.add_widget(img_box)

        def refresh_vid_thumbs():
            vid_thumbs_layout.clear_widgets()
            for rel_vid_path in selected_videos:
                placeholder_path = os.path.join(os.path.dirname(__file__), "video_placeholder.png")
                thumb = Image(
                    source=placeholder_path if os.path.exists(placeholder_path) else "",
                    size_hint=(None, None),
                    size=(dp(70), dp(70)),
                    allow_stretch=True,
                    keep_ratio=True,
                )
                remove_btn = Button(text="X", size_hint=(None, None), size=(dp(24), dp(24)))
                def remove_vid(instance, vid=rel_vid_path):
                    if vid in selected_videos:
                        selected_videos.remove(vid)
                        refresh_vid_thumbs()
                remove_btn.bind(on_release=remove_vid)
                vid_box = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(70), dp(94)))
                vid_box.add_widget(thumb)
                vid_box.add_widget(remove_btn)
                vid_thumbs_layout.add_widget(vid_box)

        refresh_img_thumbs()
        refresh_vid_thumbs()

        def open_image_chooser_wrapper(instance):
            def on_images_selected(selected):
                selected = selected[:4]
                os.makedirs(self.IMAGES_DIR, exist_ok=True)
                for img_path in selected:
                    filename = os.path.basename(img_path)
                    dest_path = os.path.join(self.IMAGES_DIR, filename)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(self.IMAGES_DIR, filename)
                        counter += 1
                    try:
                        shutil.copy(img_path, dest_path)
                        rel_path = os.path.relpath(dest_path, self.IMAGES_DIR)
                        if rel_path not in selected_images:
                            selected_images.append(rel_path)
                    except Exception as e:
                        print(f"Error copying image: {e}")
                refresh_img_thumbs()
            open_image_chooser(
                img_btn, on_images_selected, multiselect=True, max_select=4, popup_size=(500, 400)
            )
        img_btn = Button(text="Add Photo(s)", size_hint_y=None, height=dp(40))
        img_btn.bind(on_release=open_image_chooser_wrapper)

        def open_video_chooser(instance):
            fc_content = BoxLayout(
                orientation="vertical", spacing=dp(10), padding=dp(10)
            )
            filechooser = FileChooserIconView(
                filters=["*.mp4", "*.mov", "*.avi", "*.mkv"],
                multiselect=True,
                size_hint_y=None,
                height=dp(300),
            )
            btns = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10),
            )
            ok_btn = Button(text="OK")
            cancel_btn = Button(text="Cancel")
            btns.add_widget(ok_btn)
            btns.add_widget(cancel_btn)
            fc_content.add_widget(
                Label(
                    text="Select up to 4 videos",
                    font_size=16,
                    size_hint_y=None,
                    height=dp(30),
                )
            )
            fc_content.add_widget(filechooser)
            fc_content.add_widget(btns)
            fc_popup = Popup(
                title="",
                content=fc_content,
                size_hint=(None, None),
                size=(dp(500), dp(400)),
                auto_dismiss=False,
            )

            def set_videos(instance):
                selected = filechooser.selection[:4]
                os.makedirs(self.VIDEOS_DIR, exist_ok=True)
                for vid_path in selected:
                    filename = os.path.basename(vid_path)
                    dest_path = os.path.join(self.VIDEOS_DIR, filename)
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(self.VIDEOS_DIR, filename)
                        counter += 1
                    try:
                        shutil.copy(vid_path, dest_path)
                        rel_path = os.path.relpath(dest_path, self.VIDEOS_DIR)
                        if rel_path not in selected_videos:
                            selected_videos.append(rel_path)
                    except Exception as e:
                        print(f"Error copying video: {e}")
                refresh_vid_thumbs()
                fc_popup.dismiss()

            def cancel_fc(instance):
                fc_popup.dismiss()

            ok_btn.bind(on_release=set_videos)
            cancel_btn.bind(on_release=cancel_fc)
            fc_popup.open()

        vid_btn = Button(text="Add Video(s)", size_hint_y=None, height=dp(40))
        vid_btn.bind(on_release=open_video_chooser)

        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10)
        )
        save_btn = Button(text="Save")
        delete_btn = Button(text="Delete", background_color=(1, 0.3, 0.3, 1))
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(Label(
            text="Edit Diary Entry",
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))
        content.add_widget(entry_input)
        content.add_widget(date_btn)
        content.add_widget(img_btn)
        content.add_widget(img_thumbs_layout)
        content.add_widget(vid_btn)
        content.add_widget(vid_thumbs_layout)
        content.add_widget(btn_layout)
        popup = Popup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(600)),
            auto_dismiss=False,
        )

        def save_entry(instance):
            text = entry_input.text.strip()
            if text:
                self.entries[entry_index]["text"] = text
                self.entries[entry_index]["date"] = selected_date[0].isoformat()
                self.entries[entry_index]["images"] = list(selected_images)
                self.entries[entry_index]["videos"] = list(selected_videos)
                self.save_entries()
                self.refresh_feed()
            popup.dismiss()

        def delete_entry(instance):
            del self.entries[entry_index]
            self.save_entries()
            self.refresh_feed()
            popup.dismiss()

        def cancel_entry(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        delete_btn.bind(on_release=delete_entry)
        cancel_btn.bind(on_release=cancel_entry)
        popup.open()
