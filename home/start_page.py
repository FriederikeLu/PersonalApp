from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout


class StartPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grid = GridLayout(cols=3, rows=3, spacing=10, padding=20, size_hint=(1, 1))

        images = [
            "home/images/IMG_20231212_172302.jpg",
            "home/images/IMG_20231212_172302.jpg",
            "home/images/IMG_20231212_172302.jpg",
            "home/images/IMG_20231212_172302.jpg",
            "home/images/IMG_20231212_172302.jpg",
            "home/images/IMG_20231212_172302.jpg",
            "home/images/newplot (1).png",
            "home/images/IMG_20231212_172302.jpg"
        ]

        for i in range(9):
            if i == 4:
                box = BoxLayout(orientation="vertical", padding=10)
                with box.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.96, 0.96, 0.86, 1)  # beige
                    box.bg_rect = Rectangle(pos=box.pos, size=box.size)
                def update_bg_rect(instance, value):
                    box.bg_rect.pos = box.pos
                    box.bg_rect.size = box.size
                box.bind(pos=update_bg_rect, size=update_bg_rect)
                label = Label(
                    text="Hello! Welcome to your personal tracker app.",
                    font_size=24,
                    halign="center",
                    valign="middle",
                    color=(0, 0, 0, 1)
                )
                label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                box.add_widget(label)
                grid.add_widget(box)
            else:
                img_path = images[i if i < 4 else i-1]
                grid.add_widget(Image(source=img_path, size_hint=(1, 1), fit_mode="cover"))

        self.add_widget(grid)
