from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.metrics import dp
import os

class BookTrackerPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation="vertical", padding=24, spacing=18)

        # Header
        header = Label(
            text="📚 Book Tracker",
            font_size=32,
            bold=True,
            color=(0.2, 0.4, 0.7, 1),
            size_hint_y=None,
            height=54,
        )
        main_layout.add_widget(header)

        # Card-like Book Entry Form
        form_card = BoxLayout(orientation="vertical", padding=18, spacing=10, size_hint_y=None, height=300)
        with form_card.canvas.before:
            Color(0.90, 0.95, 1, 1)  # light blue
            form_card.bg = RoundedRectangle(radius=[18], pos=form_card.pos, size=form_card.size)
        def update_bg(instance, value):
            form_card.bg.pos = form_card.pos
            form_card.bg.size = form_card.size
        form_card.bind(pos=update_bg, size=update_bg)

        self.title_input = TextInput(hint_text="Title", size_hint_y=None, height=38, font_size=16)
        self.author_input = TextInput(hint_text="Author", size_hint_y=None, height=38, font_size=16)
        self.genre_input = TextInput(hint_text="Genre", size_hint_y=None, height=38, font_size=16)
        self.end_date_input = TextInput(hint_text="Finished Date (YYYY-MM-DD)", size_hint_y=None, height=38, font_size=16)
        self.rating_input = TextInput(hint_text="Rating (1-5)", size_hint_y=None, height=38, font_size=16)
        self.notes_input = TextInput(hint_text="Notes", size_hint_y=None, height=38, font_size=16)

        self.selected_image_path = [None]
        image_box = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=60)
        self.image_preview = Image(size_hint=(None, None), size=(50, 50))
        choose_img_btn = Button(
            text="Choose Image",
            size_hint_y=None,
            height=38,
            size_hint_x=None,
            width=120,
            color=(0.2, 0.4, 0.7, 1)
        )

        # Remove any background color or set background_normal to '' to avoid default grey
        choose_img_btn.background_normal = ''
        choose_img_btn.background_color = (1, 1, 1, 0)  # Transparent background

        def open_file_chooser(instance):
            fc_layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
            filechooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg", "*.bmp"], size_hint_y=1)
            btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
            ok_btn = Button(text="OK")
            cancel_btn = Button(text="Cancel")
            btns.add_widget(ok_btn)
            btns.add_widget(cancel_btn)
            fc_layout.add_widget(filechooser)
            fc_layout.add_widget(btns)
            # Set popup size to match diary_page (500x400)
            popup = Popup(title="Choose Book Image", content=fc_layout, size_hint=(None, None), size=(dp(500), dp(500)),)

            def set_image(instance):
                if filechooser.selection:
                    self.selected_image_path[0] = filechooser.selection[0]
                    self.image_preview.source = self.selected_image_path[0]
                popup.dismiss()

            def cancel(instance):
                popup.dismiss()

            ok_btn.bind(on_release=set_image)
            cancel_btn.bind(on_release=cancel)
            popup.open()

        choose_img_btn.bind(on_release=open_file_chooser)
        image_box.add_widget(self.image_preview)
        image_box.add_widget(choose_img_btn)

        form_card.add_widget(self.title_input)
        form_card.add_widget(self.author_input)
        form_card.add_widget(self.genre_input)
        form_card.add_widget(self.end_date_input)
        form_card.add_widget(self.rating_input)
        form_card.add_widget(self.notes_input)
        form_card.add_widget(image_box)

        add_btn = Button(
            text="Add Book",
            size_hint_y=None,
            height=42,
            background_color=(0.2, 0.4, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=17,
            bold=True,
        )
        form_card.add_widget(add_btn)
        main_layout.add_widget(form_card)

        # Filter/Sort Options
        filter_sort_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=38, padding=[0, 8, 0, 8])
        filter_sort_box.add_widget(Label(text="🔎 Filter/Sort Options", font_size=16, color=(0.2, 0.4, 0.7, 1)))
        main_layout.add_widget(filter_sort_box)

        # Book List (Scrollable)
        book_list_card = BoxLayout(orientation="vertical", padding=12, spacing=8, size_hint_y=1)
        with book_list_card.canvas.before:
            Color(0.97, 0.97, 1, 1)  # very light blue
            book_list_card.bg = RoundedRectangle(radius=[14], pos=book_list_card.pos, size=book_list_card.size)
        def update_list_bg(instance, value):
            book_list_card.bg.pos = book_list_card.pos
            book_list_card.bg.size = book_list_card.size
        book_list_card.bind(pos=update_list_bg, size=update_list_bg)
        scroll = ScrollView(size_hint=(1, 1))
        book_list_placeholder = Label(
            text="[Book List Here]",
            font_size=16,
            color=(0.4, 0.4, 0.4, 1),
            halign="center",
            valign="middle"
        )
        book_list_placeholder.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        book_list_card.add_widget(book_list_placeholder)
        scroll.add_widget(book_list_card)
        main_layout.add_widget(scroll)

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
