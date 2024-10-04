from kivymd.app import MDApp
from kivy.core.window import Window
from pymongo import MongoClient
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import OneLineListItem
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button
from kivymd.uix.pickers import MDDatePicker
from pymongo import ReturnDocument
import datetime as dt
from kivy.clock import Clock
import time


class TimePickerDialog(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.7)
        self.auto_dismiss = False

        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        # Hour spinner
        self.from_hour_spinner = Spinner(text='00', values=[str(i).zfill(2) for i in range(9, 18)])
        layout.add_widget(MDLabel(text='From:'))
        layout.add_widget(MDLabel(text='Hour:'))
        layout.add_widget(self.from_hour_spinner)

        # Minute spinner
        self.from_minute_spinner = Spinner(text='00', values=[str(i).zfill(2) for i in range(60)])
        layout.add_widget(MDLabel(text='Minute:'))
        layout.add_widget(self.from_minute_spinner)

        # Hour spinner
        self.to_hour_spinner = Spinner(text='00', values=[str(i).zfill(2) for i in range(9, 18)])
        layout.add_widget(MDLabel(text='To:'))
        layout.add_widget(MDLabel(text='Hour:'))
        layout.add_widget(self.to_hour_spinner)

        # Minute spinner
        self.to_minute_spinner = Spinner(text='00', values=[str(i).zfill(2) for i in range(60)])
        layout.add_widget(MDLabel(text='Minute:'))
        layout.add_widget(self.to_minute_spinner)
        # OK and Cancel buttons
        button_layout = MDBoxLayout(size_hint_y=None, height=50, spacing=20)

        ok_button = Button(text='OK', on_release=self.on_ok)
        cancel_button = Button(text='Cancel', on_release=self.dismiss)

        button_layout.add_widget(ok_button)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_ok(self, instance):
        from_selected_hour = self.from_hour_spinner.text
        from_selected_minute = self.from_minute_spinner.text
        from_selected_time = f'{from_selected_hour}:{from_selected_minute}'
        self.dismiss()
        if self.from_on_time_selected:
            self.from_on_time_selected(from_selected_time)
        to_selected_hour = self.to_hour_spinner.text
        to_selected_minute = self.to_minute_spinner.text
        to_selected_time = f'{to_selected_hour}:{to_selected_minute}'
        self.dismiss()
        if self.to_on_time_selected:
            self.to_on_time_selected(to_selected_time)


class Login_scr(MDScreen):
    pass


class Home_scr(MDScreen):
    pass


class Hall_selection(MDScreen):
    pass


class Seat_selection1(MDScreen):
    pass


class Time_selection(MDScreen):
    pass


# global collection
class SeatbookerApp(MDApp):
    dialog = None
    client = None
    db = None
    collection = None
    collection1 = None
    from_selected_time = None
    to_selected_time = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.bldr = Builder.load_file("SeatbookerApp.kv")
        sm = MDScreenManager()
        sm.add_widget(Login_scr(name="login"))
        sm.add_widget(Home_scr(name="home"))
        sm.add_widget(Hall_selection(name="hall_selection"))
        sm.add_widget(Seat_selection1(name="seat_selection1"))
        sm.add_widget(Time_selection(name="time_selection"))
        return self.bldr

    def on_start(self):
        self.connect_to_mongo()# please give your mangodb atlas string 
        for i in range(1, 4):
            self.bldr.get_screen("hall_selection").ids.container.add_widget(
                OneLineListItem(
                    text=f"Hall{i}",
                    on_release=lambda x, i=i: self.seatselection(i)
                )
            )

    def connect_to_mongo(self):
        try:
            self.client = MongoClient('')
            self.client.admin.command('ismaster')
            self.db = self.client['user_detail']
            self.collection = self.db['library_details']
            self.collection1 = self.db['seat_detials']
        except Exception as e:
            self.show_error_dialog("Please connect to internet")

    def get_data(self):
        self.username = self.bldr.get_screen("login").ids.username.text
        self.password = self.bldr.get_screen("login").ids.passwd.text
        self.checkuser()

    def checkuser(self):
        if self.collection:
            self.user_id = self.collection.find_one({"USERNAME": str(self.username), "PASSWORD": str(self.password)},
                                                    {"_id": 1})
            user_name = self.collection.find_one({"USERNAME": str(self.username)},
                                                 {"_id": 0, "USERNAME": 1})  # ,"PASSWORD": str(self.password)
            user_pass = self.collection.find_one({"PASSWORD": str(self.password)}, {"_id": 0, "PASSWORD": 1})

            if (user_name):
                # print("Login Successful")
                if (user_pass):
                    self.login()
                else:
                    self.show_error_dialog("Please check your password")
            # Proceed to the next screen or action
            else:
                # print("Invalid username or password")
                self.show_error_dialog("User does not exist")
        else:
            self.show_error_dialog("Unable to perform operations due to connection issues.")

    def login(self):
        date_select = MDDatePicker()
        date_select.bind(on_save=self.on_date_selected, on_cancel=self.on_cancel)
        date_select.open()
        self.root.current = "home"

    def seatselection(self, other):
        if (other == 1):
            self.root.current = "seat_selection1"
        elif (other == 2):
            self.root.current = "seat_selection2"
        elif (other == 3):
            self.root.current = "seat_selection3"
        else:
            self.show_error_dialog("Please Select the hall number")

    def on_date_selected(self, instance, value, date_range):
        self.date_value = value
        self.root.current = "hall_selection"

    def on_cancel(self, instance, value):
        self.show_error_dialog("Please Select The Date")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.text = message
        self.dialog.open()

    def time_selection(self, other):
        time_picker = TimePickerDialog()
        time_picker.from_on_time_selected = self.from_on_time_selected
        time_picker.to_on_time_selected = self.to_on_time_selected
        time_picker.open()
        self.seat_id1 = other

    def from_on_time_selected(self, selected_time1):
        self.from_selected_time = dt.datetime.strptime(selected_time1, "%H:%M").time()

    def to_on_time_selected(self, selected_time2):
        self.to_selected_time = dt.datetime.strptime(selected_time2, "%H:%M").time()

        self.seat_booking()

    def seat_booking(self):
        now_time = dt.datetime.now()
        start_datetime = dt.datetime.combine(self.date_value, self.from_selected_time)
        end_datetime = dt.datetime.combine(self.date_value, self.to_selected_time)
        start_delay = (start_datetime - now_time).total_seconds()
        end_delay = (end_datetime - now_time).total_seconds()
        if self.date_value == dt.date.today():
            if start_datetime <= now_time <= end_datetime:
                if self.collection1:
                    result = self.collection1.find_one_and_update(
                        {"seat_id": str(self.seat_id1), "status": "available", "Booked_by": None},
                        {"$set": {"status": "Booked", "Booked_by": self.user_id["_id"]}},
                        return_document=ReturnDocument.AFTER
                    )
                time.sleep(5)
                if self.collection1:
                    self.seat_id = self.collection1.find_one(
                        {"seat_id": self.seat_id1, "status": "Booked", "Booked_by": self.user_id["_id"]},
                        {"_id": 0, "seat_id": 1})
                print(self.bldr.get_screen("seat_selection1").ids.seat2.name == self.seat_id["seat_id"])
                if self.bldr.get_screen("seat_selection1").ids.seat1.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat1.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat2.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat2.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat3.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat3.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat4.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat4.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat5.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat5.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat6.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat6.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat7.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat7.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat8.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat8.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat9.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat9.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat10.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat10.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat11.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat11.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat12.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat12.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat13.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat13.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat14.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat14.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat15.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat15.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat16.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat16.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat17.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat17.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat18.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat18.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat19.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat19.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat20.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat20.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat21.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat21.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat22.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat22.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat23.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat23.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat24.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat24.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat25.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat25.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat26.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat26.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat27.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat27.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat28.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat28.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat29.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat29.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat30.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat30.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat31.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat31.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat32.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat32.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat33.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat33.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat34.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat34.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat35.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat35.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat36.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat36.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat37.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat37.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat38.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat38.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat39.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat39.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat40.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat40.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat41.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat41.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat42.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat42.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat43.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat43.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat44.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat44.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat45.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat45.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat46.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat46.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat47.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat47.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat48.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat48.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat49.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat49.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat50.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat50.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat51.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat51.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat52.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat52.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat53.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat53.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat54.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat54.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat55.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat55.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat56.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat56.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat57.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat57.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat58.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat58.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat59.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat59.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat60.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat60.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat61.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat61.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat62.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat62.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat63.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat63.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat64.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat64.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat65.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat65.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat66.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat66.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat67.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat67.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat68.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat68.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat69.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat69.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat70.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat70.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat71.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat71.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat72.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat72.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat73.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat73.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat74.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat74.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat75.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat75.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat76.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat76.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat77.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat77.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat78.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat78.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat79.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat79.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat80.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat80.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat81.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat81.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat82.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat82.disabled = True
                elif self.bldr.get_screen("seat_selection1").ids.seat83.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat83.disabledd = True
                elif self.bldr.get_screen("seat_selection1").ids.seat84.name == self.seat_id["seat_id"]:
                    self.bldr.get_screen("seat_selection1").ids.seat84.disabledd = True
                else:
                    self.show_error_dialog("Please Select Seat")
                Clock.schedule_once(self.enable_seat, end_delay)
            else:
                Clock.schedule_once(self.disabled_seat_for_time, start_delay)
                Clock.schedule_once(self.enable_seat, end_delay)
        else:
            self.show_error_dialog("Please Select Date")

    def disabled_seat_for_time(self, disabled_datetime):
        if self.collection1:
            result = self.collection1.find_one_and_update(
                {"seat_id": str(self.seat_id1), "status": "available", "Booked_by": None},
                {"$set": {"status": "Booked", "Booked_by": self.user_id["_id"]}},
                return_document=ReturnDocument.AFTER
            )
        time.sleep(5)
        if self.collection1:
            self.seat_id = self.collection1.find_one(
                {"seat_id": self.seat_id1, "status": "Booked", "Booked_by": self.user_id["_id"]},
                {"_id": 0, "seat_id": 1})
        print(self.bldr.get_screen("seat_selection1").ids.seat2.name == self.seat_id["seat_id"])
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat1.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat2.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat3.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat4.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat5.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat6.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat7.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat8.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat9.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat10.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat11.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat12.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat13.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat14.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat15.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat16.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat17.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat18.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat19.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat20.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat21.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat22.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat23.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat24.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat25.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat26.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat27.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat28.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat29.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat30.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat31.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat32.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat33.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat34.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat35.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat36.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat37.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat38.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat39.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat40.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat41.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat42.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat43.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat44.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat45.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat46.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat47.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat48.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat49.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat50.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat51.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat52.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat53.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat54.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat55.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat56.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat57.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat58.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat59.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat60.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat61.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat62.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat63.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat64.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat65.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat66.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat67.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat68.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat69.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat70.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat71.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat72.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat73.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat74.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat75.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat76.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat77.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat78.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat79.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat80.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat81.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat82.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat83.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat84.disabled = True
        else:
            self.show_error_dialog("Please Select Seat")

    def enable_seat(self, enable_datetime):
        result = self.collection1.find_one_and_update(
            {"seat_id": self.seat_id1, "status": "Booked", "Booked_by": self.user_id["_id"]},
            {"$set": {"status": "available", "Booked_by": None}})
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat1.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat2.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat3.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat4.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat5.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat6.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat7.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat8.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat9.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat10.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat11.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat12.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat13.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat14.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat15.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat16.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat17.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat18.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat19.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat20.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat21.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat22.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat23.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat24.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat25.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat26.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat27.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat28.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat29.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat30.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat31.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat32.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat33.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat34.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat35.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat36.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat37.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat38.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat39.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat40.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat41.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat42.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat43.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat44.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat45.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat46.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat47.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat48.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat49.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat50.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat51.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat52.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat53.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat54.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat55.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat56.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat57.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat58.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat59.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat60.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat61.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat62.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat63.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat64.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat65.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat66.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat67.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat68.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat69.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat70.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat71.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat72.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat73.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat74.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat75.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat76.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat77.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat78.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat79.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat80.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat81.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat82.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat83.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == self.seat_id["seat_id"]:
            self.bldr.get_screen("seat_selection1").ids.seat84.disabled = False


if __name__ == '__main__':
    Window.size = (500, 600)
    SeatbookerApp().run()
