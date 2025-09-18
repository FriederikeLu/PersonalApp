from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.metrics import dp
import os
from ui.utils import open_date_picker, open_image_chooser
import datetime
from kivy.uix.spinner import Spinner
import json
import shutil

class BookTrackerPage(Screen):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/book_tracker")
    ENTRIES_FILE = os.path.join(DATA_DIR, "book_entries.json")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.IMAGES_DIR, exist_ok=True)
        self.books = self.load_entries()

        main_layout = BoxLayout(orientation="vertical", padding=24, spacing=18)

        # Header with "Add Book" button
        header_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54))
        header = Label(
            text="📚 Book Tracker",
            font_size=32,
            bold=True,
            color=(0.2, 0.4, 0.7, 1),
        )
        add_btn = Button(text="+ Add Book", size_hint_x=None, width=dp(120))
        add_btn.bind(on_release=self.open_add_popup)
        header_layout.add_widget(header)
        header_layout.add_widget(add_btn)
        main_layout.add_widget(header_layout)

        # Filter/Sort Options
        filter_sort_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=38, padding=[0, 8, 0, 8])
        filter_sort_box.add_widget(Label(text="🔎 Filter/Sort Options", font_size=16, color=(0.2, 0.4, 0.7, 1)))
        main_layout.add_widget(filter_sort_box)

        # Book List (Scrollable)
        self.book_list_card = BoxLayout(orientation="vertical", padding=12, spacing=8, size_hint_y=1)
        with self.book_list_card.canvas.before:
            Color(0.97, 0.97, 1, 1)  # very light blue
            self.book_list_card.bg = RoundedRectangle(radius=[14], pos=self.book_list_card.pos, size=self.book_list_card.size)
        def update_list_bg(instance, value):
            self.book_list_card.bg.pos = self.book_list_card.pos
            self.book_list_card.bg.size = self.book_list_card.size
        self.book_list_card.bind(pos=update_list_bg, size=update_list_bg)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.book_list_card)
        main_layout.add_widget(self.scroll)

        # Statistics Section
        stats_card = BoxLayout(orientation="vertical", padding=12, spacing=6, size_hint_y=None, height=60)
        with stats_card.canvas.before:
            Color(0.9, 0.95, 1, 1)  # pastel blue
            stats_card.bg = RoundedRectangle(radius=[14], pos=stats_card.pos, size=stats_card.size)
        def update_stats_bg(instance, value):
            stats_card.bg.pos = stats_card.pos
            stats_card.bg.size = stats_card.size
        stats_card.bind(pos=update_stats_bg, size=update_stats_bg)
        stats_card.add_widget(Label(
            text="📊 [Statistics Here]",
            font_size=16,
            color=(0.2, 0.4, 0.7, 1)
        ))
        main_layout.add_widget(stats_card)

        self.add_widget(main_layout)
        self.refresh_book_list()

    def load_entries(self):
        path = os.path.abspath(self.ENTRIES_FILE)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        else:
            return []

    def save_entries(self):
        path = os.path.abspath(self.ENTRIES_FILE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving book entries: {e}")

    def refresh_book_list(self):
        self.book_list_card.clear_widgets()
        if not self.books:
            self.book_list_card.add_widget(Label(
                text="[Book List Here]",
                font_size=16,
                color=(0.4, 0.4, 0.4, 1),
                halign="center",
                valign="middle"
            ))
        else:
            for book in self.books:
                row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=70, padding=[0, 4, 0, 4])
                if book.get("image"):
                    img_path = os.path.join(self.IMAGES_DIR, book["image"])
                    row.add_widget(Image(source=img_path, size_hint=(None, None), size=(50, 50)))
                info = f"[b]{book['title']}[/b] by {book['author']} | {book['date']} | {book['format']} | Rating: {book['rating']}"
                row.add_widget(Label(text=info, markup=True, halign="left", valign="middle"))
                self.book_list_card.add_widget(row)

    def open_add_popup(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        title_input = TextInput(hint_text="Title", size_hint_y=None, height=38, font_size=16)
        author_input = TextInput(hint_text="Author", size_hint_y=None, height=38, font_size=16)
        genre_input = TextInput(hint_text="Genre", size_hint_y=None, height=38, font_size=16)
        # --- Date selection ---
        today = datetime.date.today()
        selected_date = [today]
        def update_date_btn_text():
            date_btn.text = selected_date[0].isoformat()
        date_btn = Button(text=today.isoformat(), size_hint_y=None, height=38)
        def on_date_selected(new_date):
            selected_date[0] = new_date
            update_date_btn_text()
        date_btn.bind(on_release=lambda inst: open_date_picker(date_btn, selected_date, on_date_selected))
        # --- End date selection ---
        # --- Book format spinner ---
        format_spinner = Spinner(
            text="Format: Paper",
            values=["Paper", "Ebook", "Audiobook"],
            size_hint_y=None,
            height=38,
            font_size=16,
        )
        # --- End book format spinner ---
        rating_input = TextInput(hint_text="Rating (1-5)", size_hint_y=None, height=38, font_size=16)
        notes_input = TextInput(hint_text="Notes", size_hint_y=None, height=38, font_size=16)

        selected_image_path = [None]
        image_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=60)
        image_preview = Image(size_hint=(None, None), size=(50, 50))
        choose_img_btn = Button(
            text="Choose Image",
            size_hint_y=None,
            height=38,
            size_hint_x=None,
            width=120,
            color=(0.2, 0.4, 0.7, 1)
        )
        choose_img_btn.background_normal = ''
        choose_img_btn.background_color = (1, 1, 1, 0)  # Transparent background

        def on_images_selected(selected):
            if selected:
                selected_image_path[0] = selected[0]
                image_preview.source = selected[0]

        choose_img_btn.bind(
            on_release=lambda instance: open_image_chooser(
                choose_img_btn, on_images_selected, multiselect=False, max_select=1, popup_size=(500, 500)
            )
        )
        image_box.add_widget(image_preview)
        image_box.add_widget(choose_img_btn)

        btn_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(Label(
            text="Add Book Entry",
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))
        content.add_widget(title_input)
        content.add_widget(author_input)
        content.add_widget(genre_input)
        content.add_widget(date_btn)
        content.add_widget(format_spinner)  # <-- Add format spinner here
        content.add_widget(rating_input)
        content.add_widget(notes_input)
        content.add_widget(image_box)
        content.add_widget(btn_layout)

        popup = Popup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(600)),
            auto_dismiss=False,
        )

        def save_entry(instance):
            # Save the book entry, including format_spinner.text
            image_filename = None
            if selected_image_path[0]:
                os.makedirs(self.IMAGES_DIR, exist_ok=True)
                src = selected_image_path[0]
                filename = os.path.basename(src)
                dest_path = os.path.join(self.IMAGES_DIR, filename)
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(self.IMAGES_DIR, filename)
                    counter += 1
                try:
                    shutil.copy(src, dest_path)
                    image_filename = filename
                except Exception as e:
                    print(f"Error copying image: {e}")
            book = {
                "title": title_input.text.strip(),
                "author": author_input.text.strip(),
                "genre": genre_input.text.strip(),
                "date": selected_date[0].isoformat(),
                "format": format_spinner.text.replace("Format: ", ""),
                "rating": rating_input.text.strip(),
                "notes": notes_input.text.strip(),
                "image": image_filename if image_filename else None,
            }
            self.books.append(book)
            self.save_entries()
            self.refresh_book_list()
            popup.dismiss()

        def cancel_entry(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        cancel_btn.bind(on_release=cancel_entry)
        popup.open()
