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
from kivy.uix.gridlayout import GridLayout

# Todo: Show ALL saved data for each book. Including rating, name, Author. Also modify font size

class BookCard(BoxLayout):
    def __init__(self, book, images_dir, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(130), padding=dp(10), spacing=dp(12), **kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1)  # very light blue
            self.bg = RoundedRectangle(radius=[14], pos=self.pos, size=self.size)
        def update_bg(instance, value):
            self.bg.pos = self.pos
            self.bg.size = self.size
        self.bind(pos=update_bg, size=update_bg)

        # Book image
        if book.get("image"):
            img_path = os.path.join(images_dir, book["image"])
            self.add_widget(Image(source=img_path, size_hint=(None, None), size=(dp(80), dp(110))))
        else:
            self.add_widget(Label(text="No Image", size_hint=(None, None), size=(dp(80), dp(110)), color=(0.5,0.5,0.5,1)))

        # Book info
        info_box = BoxLayout(orientation="vertical", spacing=dp(2))
        # Title at the top, bigger and bold
        info_box.add_widget(Label(
            text=f"[b]{book.get('title', '')}[/b]",
            markup=True,
            font_size=22,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(30)
        ))
        # Author
        info_box.add_widget(Label(
            text=f"by {book.get('author', '')}",
            font_size=16,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22)
        ))
        # Genre
        info_box.add_widget(Label(
            text=f"Genre: {book.get('genre','')}",
            font_size=14,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        ))
        # Finished date
        info_box.add_widget(Label(
            text=f"Finished: {book.get('date','')}",
            font_size=14,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        ))
        # Format
        info_box.add_widget(Label(
            text=f"Format: {book.get('format','')}",
            font_size=14,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        ))
        # Rating
        info_box.add_widget(Label(
            text=f"Rating: {book.get('rating','')}/10",
            font_size=14,
			color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        ))
        # Notes
        notes = book.get("notes", "")
        if notes:
            info_box.add_widget(Label(
                text=f"[i]{notes}[/i]",
                markup=True,
                font_size=13,
                color=(0.3,0.3,0.3,1),
                halign="left",
                valign="top",
                size_hint_y=None,
                height=dp(20)
            ))
        self.add_widget(info_box)

class BookTrackerPage(Screen):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/book_tracker")
    ENTRIES_FILE = os.path.join(DATA_DIR, "book_entries.json")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.IMAGES_DIR, exist_ok=True)
        self.books = self.load_entries()
        self.current_sort = "Date (Newest)"
        self.current_genre_filter = "All"

        main_layout = BoxLayout(orientation="vertical", padding=24, spacing=18)

        # Header with "Add Book" button
        header_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54))
        header = Label(
            text="Book Tracker",
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
        filter_sort_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(38), padding=[0, 8, 0, 8])
        #filter_sort_box.add_widget(Label(text="Sort", font_size=32, color=(0.2, 0.4, 0.7, 1), size_hint_x=None, width=dp(30)))

        # Sort Spinner
        sort_spinner = Spinner(
            text="Date (Newest)",
            values=["Date (Newest)", "Date (Oldest)", "Rating (High)", "Rating (Low)", "Title (A-Z)", "Title (Z-A)"],
            size_hint_x=None,
            width=dp(130),
            size_hint_y=None,
            height=dp(25),
        )
        filter_sort_box.add_widget(sort_spinner)

        # Genre Filter Spinner
        def get_genres():
            genres = set(book.get("genre", "") for book in self.books if book.get("genre", ""))
            return ["All"] + sorted(genres)

        genre_spinner = Spinner(
            text="Genre: All",
            values=get_genres(),
            size_hint_x=None,
            width=dp(130),
            size_hint_y=None,
            height=dp(25),
        )
        filter_sort_box.add_widget(genre_spinner)

        main_layout.add_widget(filter_sort_box)

        # Book List (Scrollable, now using GridLayout for cards)
        self.book_list_grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, padding=[0,0,0,0])
        self.book_list_grid.bind(minimum_height=self.book_list_grid.setter("height"))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.book_list_grid)
        main_layout.add_widget(self.scroll)

        # Statistics Section
        self.stats_card = BoxLayout(orientation="vertical", padding=12, spacing=6, size_hint_y=None, height=60)
        with self.stats_card.canvas.before:
            Color(1, 1, 1, 1)  # White background for statistics card
            self.stats_card.bg = RoundedRectangle(radius=[14], pos=self.stats_card.pos, size=self.stats_card.size)
        def update_stats_bg(instance, value):
            self.stats_card.bg.pos = self.stats_card.pos
            self.stats_card.bg.size = self.stats_card.size
        self.stats_card.bind(pos=update_stats_bg, size=update_stats_bg)
        self.stats_label = Label(
            text="📊 [Statistics Here]",
            font_size=16,
            color=(0.2, 0.4, 0.7, 1)  # Dark blue text for readability
        )
        self.stats_card.add_widget(self.stats_label)
        main_layout.add_widget(self.stats_card)

        self.add_widget(main_layout)
        self.sort_spinner = sort_spinner
        self.genre_spinner = genre_spinner
        self.sort_spinner.bind(text=self.on_sort_filter_changed)
        self.genre_spinner.bind(text=self.on_sort_filter_changed)
        self.refresh_book_list()

    def on_sort_filter_changed(self, *args):
        self.current_sort = self.sort_spinner.text.replace("Sort: ", "")
        self.current_genre_filter = self.genre_spinner.text.replace("Genre: ", "")
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
        self.book_list_grid.clear_widgets()
        # Filter by genre
        filtered_books = [
            book for book in self.books
            if self.current_genre_filter in ("All", "", None) or book.get("genre", "") == self.current_genre_filter
        ]
        # Sort
        if self.current_sort == "Date (Newest)":
            filtered_books.sort(key=lambda b: b.get("date", ""), reverse=True)
        elif self.current_sort == "Date (Oldest)":
            filtered_books.sort(key=lambda b: b.get("date", ""))
        elif self.current_sort == "Rating (High)":
            filtered_books.sort(key=lambda b: float(b.get("rating", "0") or 0), reverse=True)
        elif self.current_sort == "Rating (Low)":
            filtered_books.sort(key=lambda b: float(b.get("rating", "0") or 0))
        elif self.current_sort == "Title (A-Z)":
            filtered_books.sort(key=lambda b: b.get("title", "").lower())
        elif self.current_sort == "Title (Z-A)":
            filtered_books.sort(key=lambda b: b.get("title", "").lower(), reverse=True)

        if not filtered_books:
            self.book_list_grid.add_widget(Label(
                text="[Book List Here]",
                font_size=16,
                color=(0.4, 0.4, 0.4, 1),
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(60)
            ))
        else:
            for book in filtered_books:
                self.book_list_grid.add_widget(BookCard(book, self.IMAGES_DIR))

        # Update genre spinner values if new genres were added
        genres = set(book.get("genre", "") for book in self.books if book.get("genre", ""))
        genre_values = ["All"] + sorted(genres)
        if tuple(self.genre_spinner.values) != tuple(genre_values):
            self.genre_spinner.values = genre_values

        # --- Statistics Section ---
        total_books = len(filtered_books)
        genre_counts = {}
        rating_sum = 0
        rating_count = 0
        dates = []
        for book in filtered_books:
            genre = book.get("genre", "")
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            try:
                rating = float(book.get("rating", "0") or 0)
                rating_sum += rating
                rating_count += 1
            except Exception:
                pass
            try:
                dates.append(book.get("date", ""))
            except Exception:
                pass
        favorite_genre = max(genre_counts, key=genre_counts.get) if genre_counts else "-"
        avg_rating = round(rating_sum / rating_count, 2) if rating_count else "-"
        # Reading streaks: count consecutive days with at least one book finished
        streak = 0
        if dates:
            date_objs = sorted([datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates])
            streak = 1
            max_streak = 1
            for i in range(1, len(date_objs)):
                if (date_objs[i] - date_objs[i-1]).days == 1:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1
            streak = max_streak
        # Update statistics label directly
        stats_text = (
            f"Total books: {total_books}   |   "
            f"Favorite genre: {favorite_genre}   |   "
            f"Average rating: {avg_rating}   |   "
            f"Longest reading streak: {streak} days"
        )
        self.stats_label.text = stats_text

    def open_add_popup(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        title_input = TextInput(hint_text="Title", size_hint_y=None, height=38, font_size=16)
        author_input = TextInput(hint_text="Author", size_hint_y=None, height=38, font_size=16)
        # --- Genre selection with dropdown ---
        common_genres = [
            "Fiction", "Non-Fiction", "Mystery", "Fantasy", "Science Fiction", "Biography",
            "Romance", "Thriller", "Self-Help", "History", "Children", "Young Adult", "Other"
        ]
        genre_spinner = Spinner(
            text="Select Genre",
            values=common_genres,
            size_hint_y=None,
            height=38,
            font_size=16
        )
        # --- End genre selection ---
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
            font_size=16
        )
        # --- End book format spinner ---
        # --- Rating dropdown 0-10 ---
        rating_spinner = Spinner(
            text="Rating: 0",
            values=[str(i) for i in range(0, 11)],
            size_hint_y=None,
            height=38,
            font_size=16
        )
        # --- End rating dropdown ---
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
            color=(0.2, 0.4, 0.7, 1),
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
            height=dp(30)
        ))
        content.add_widget(title_input)
        content.add_widget(author_input)
        content.add_widget(genre_spinner)
        content.add_widget(date_btn)
        content.add_widget(format_spinner)
        content.add_widget(rating_spinner)
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
                "genre": genre_spinner.text if genre_spinner.text != "Select Genre" else "",
                "date": selected_date[0].isoformat(),
                "format": format_spinner.text.replace("Format: ", ""),
                "rating": rating_spinner.text,
                "notes": notes_input.text.strip(),
                "image": image_filename if image_filename else None,
            }
            self.books.append(book)
            self.save_entries()
            genres = set(b.get("genre", "") for b in self.books if b.get("genre", ""))
            self.genre_spinner.values = ["All"] + sorted(genres)
            self.refresh_book_list()
            popup.dismiss()

        def cancel_entry(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        cancel_btn.bind(on_release=cancel_entry)
        popup.open()
