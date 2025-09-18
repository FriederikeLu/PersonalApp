from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
import datetime

def open_date_picker(parent_btn, selected_date, on_date_selected):
    today = datetime.date.today()
    picker_content = BoxLayout(
        orientation="vertical", spacing=dp(10), padding=dp(10)
    )
    years = [str(y) for y in range(today.year - 5, today.year + 6)]
    months = [str(m).zfill(2) for m in range(1, 13)]
    days = [str(d).zfill(2) for d in range(1, 32)]
    year_spinner = Spinner(
        text=str(selected_date[0].year),
        values=years,
        size_hint_y=None,
        height=dp(40),
    )
    month_spinner = Spinner(
        text=str(selected_date[0].month).zfill(2),
        values=months,
        size_hint_y=None,
        height=dp(40),
    )
    day_spinner = Spinner(
        text=str(selected_date[0].day).zfill(2),
        values=days,
        size_hint_y=None,
        height=dp(40),
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
    picker_content.add_widget(
        Label(text="Select Date", font_size=16, size_hint_y=None, height=dp(30))
    )
    picker_content.add_widget(year_spinner)
    picker_content.add_widget(month_spinner)
    picker_content.add_widget(day_spinner)
    picker_content.add_widget(btns)
    picker_popup = Popup(
        title="",
        content=picker_content,
        size_hint=(None, None),
        size=(dp(250), dp(300)),
        auto_dismiss=False,
    )

    def set_date(instance):
        try:
            y = int(year_spinner.text)
            m = int(month_spinner.text)
            d = int(day_spinner.text)
            selected_date[0] = datetime.date(y, m, d)
            on_date_selected(selected_date[0])
        except Exception:
            pass
        picker_popup.dismiss()

    def cancel_picker(instance):
        picker_popup.dismiss()

    ok_btn.bind(on_release=set_date)
    cancel_btn.bind(on_release=cancel_picker)
    picker_popup.open()

def open_image_chooser(
    parent_btn,
    on_images_selected,
    multiselect=True,
    title="Choose Image(s)",
    max_select=4,
    popup_size=(500, 400)
):
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.filechooser import FileChooserIconView
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.metrics import dp

    fc_content = BoxLayout(
        orientation="vertical", spacing=dp(10), padding=dp(10)
    )
    filechooser = FileChooserIconView(
        filters=["*.png", "*.jpg", "*.jpeg", "*.bmp"],
        multiselect=multiselect,
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
            text=f"Select up to {max_select} image(s)",
            font_size=16,
            size_hint_y=None,
            height=dp(30),
        )
    )
    fc_content.add_widget(filechooser)
    fc_content.add_widget(btns)
    fc_popup = Popup(
        title=title,
        content=fc_content,
        size_hint=(None, None),
        size=(dp(popup_size[0]), dp(popup_size[1])),
        auto_dismiss=False,
    )

    def set_images(instance):
        selected = filechooser.selection[:max_select]
        on_images_selected(selected)
        fc_popup.dismiss()

    def cancel_fc(instance):
        fc_popup.dismiss()

    ok_btn.bind(on_release=set_images)
    cancel_btn.bind(on_release=cancel_fc)
    fc_popup.open()
