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

class BookTrackerPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            # Here you would save the book entry, including format_spinner.text
            popup.dismiss()

        def cancel_entry(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        cancel_btn.bind(on_release=cancel_entry)
        popup.open()
