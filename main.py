# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from ui.diary_page import DiaryPage
from home.start_page import StartPage
from ui.book_tracker_page import BookTrackerPage  # <-- Add this import
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
import datetime



# Nutrition Page
class NutritionPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text="Nutrition Page", font_size=20))
        # Add nutrition widgets here
        self.add_widget(layout)


# Main App Layout with Sidebar
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        # Sidebar
        sidebar = BoxLayout(orientation="vertical", size_hint=(0.2, 1))
        btn_start = Button(text="Start")
        btn_diary = Button(text="Diary")
        btn_nutrition = Button(text="Nutrition")
        btn_books = Button(text="Books")  # <-- Add button for Book Tracker
        sidebar.add_widget(btn_start)
        sidebar.add_widget(btn_diary)
        sidebar.add_widget(btn_nutrition)
        sidebar.add_widget(btn_books)  # <-- Add to sidebar
        # Screen Manager
        self.sm = ScreenManager()
        self.sm.add_widget(StartPage(name="start"))
        self.sm.add_widget(DiaryPage(name="diary"))
        self.sm.add_widget(NutritionPage(name="nutrition"))
        self.sm.add_widget(BookTrackerPage(name="books"))  # <-- Add BookTrackerPage

        # Bind buttons
        def switch_to_start(instance):
            self.sm.current = "start"

        def switch_to_diary(instance):
            self.sm.current = "diary"

        def switch_to_nutrition(instance):
            self.sm.current = "nutrition"

        def switch_to_books(instance):  # <-- Add handler
            self.sm.current = "books"

        btn_start.bind(on_release=switch_to_start)
        btn_diary.bind(on_release=switch_to_diary)
        btn_nutrition.bind(on_release=switch_to_nutrition)
        btn_books.bind(on_release=switch_to_books)  # <-- Bind books button
        # Add to layout
        self.add_widget(sidebar)
        self.add_widget(self.sm)


class TrackerApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    TrackerApp().run()
