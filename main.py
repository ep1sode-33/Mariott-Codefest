from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy_garden.mapview import MapView, MapMarker
import api
from io import BytesIO
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.image import Image as KivyImage
import numpy as np
from pytrends.request import TrendReq
from modelDeploy import get_ai
from modelDeploy import predict
import matplotlib.pyplot as plt


KV = '''
ScreenManager:
    MainScreen:
    MapScreen:
    GraphScreen:

<MainScreen>:
    name: 'main'
    FloatLayout:
        orientation: 'vertical'
        MDLabel:
            text: "SiteScout"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1  
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            font_name: "Arial"
        MDTextField:
            id: search_field
            hint_text: "Enter State"
            pos_hint: {"center_x": 0.51, "center_y": 0.6}
            size_hint_x: None
            icon_left: "layers-search-outline"
            width: 300
            on_text: app.give_suggestions()
            font_name: "Roboto-Regular"
        MDRectangleFlatButton:
            text: "Submit"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            size_hint: None, None
            width: 300
            height: 50
            on_release: app.create_map()
            font_name: "Roboto-Regular"
        MDTextField:
            id: search_field_2
            hint_text: "Enter County"
            pos_hint: {"center_x": 0.51, "center_y": 0.5}
            size_hint_x: None
            icon_left: "layers-search-outline"
            width: 300
            on_text: app.give_suggestions2()
            font_name: "Roboto-Regular"
        MDRectangleFlatButton:
            text: "Open Graph"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            size_hint_x: None
            width: 300
            on_release: app.open_graph()
            font_name: "Roboto-Regular"

<MapScreen>:
    name: 'map'
    FloatLayout:
        orientation: 'vertical'
        FloatLayout:
            id: map_box
            size_hint_y: 0.5  
        MDIconButton:
            icon: "close"
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {"x": 0, "y": 0.9}
            on_release: app.root.current = 'main'
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

<GraphScreen>:
    name: 'graph'
    FloatLayout:
        orientation: 'vertical'
        id: graph_box
    MDIconButton:
        icon: "close"
        size_hint: None, None
        size: dp(48), dp(48)
        pos_hint: {"x": 0, "y": 0.9}
        on_release: app.root.current = 'main'
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
'''

class MainScreen(Screen):
    pass
class MapScreen(Screen):
    def on_enter(self):
        main_screen = self.manager.get_screen('main')
        state_text = main_screen.ids.search_field.text
        county_text = main_screen.ids.search_field_2.text

        lats = api.get_latitude(county_text, state_text)
        long = api.get_longtitude(county_text, state_text)
        lats = float(lats)
        long = float(long)
        map_view = MapView(zoom=10, lat=lats, lon=long)  
        map_marker = MapMarker(lat=lats, lon=long)
        map_view.add_marker(map_marker)
        self.ids.map_box.add_widget(map_view)

class GraphScreen(Screen):
    def on_enter(self):
        pytrends = TrendReq(hl='en-US', tz=360)


        main_screen = self.manager.get_screen('main')
        state_text = main_screen.ids.search_field.text
        county_text = main_screen.ids.search_field_2.text
        pytrends.build_payload(kw_list=[state_text], timeframe='today 12-m', geo='US')
        interest_over_time_df = pytrends.interest_over_time()


        screen_width, screen_height = Window.size

        dpi = 100  
        fig_width = screen_width / dpi
        fig_height = screen_height / dpi

        plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        plt.plot(interest_over_time_df.index, interest_over_time_df[state_text])
       
        plt.title(f'Google Trends Data for {state_text}')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.tight_layout()
        plt.xticks(rotation=45)


        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        texture = CoreImage(buf, ext='png').texture

        graph_image = KivyImage(texture=texture)

        # Add the Kivy Image widget to the graph_box
        self.ids.graph_box.add_widget(graph_image)

  



Window.size = (360, 640) 


class MainApp(MDApp):
    suggestions_source = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
    'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
    'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
    'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
    'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
    'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

    def build(self):
        self.theme_cls.theme_style = "Dark"  
        self.theme_cls.primary_palette = "Gray"
 
        self.menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Item {i}",
                "height": dp(56),
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        
        self.menu = MDDropdownMenu(
            caller=self.root,  
            items=self.menu_items,
            width_mult=4,
        )
        
        return Builder.load_string(KV)


    def create_map(self):
        state = self.root.get_screen('main').ids.search_field
        state_text = state.text
        state1 = self.root.get_screen('main').ids.search_field_2
        state_text1 = state1.text

        
        input_x = get_ai(f'{state_text1}', f'{state_text}')
        prediction = predict(input_x)
        lol = float(prediction)
        lol = round(lol, 2)


        if hasattr(self, 'state_label') and self.state_label:
            self.root.get_screen('map').remove_widget(self.state_label)

        
        esg_score = api.get_score(state_text)
        if esg_score == "State not found":
            esg_score = "does not exist"
        else:
            esg_score = round(esg_score, 2)
        self.state_label = MDLabel(
            text=f"[color=#AAAAAA]ESG Score: {esg_score}/10[/color]",
            markup=True,
            halign="center",
            theme_text_color="Primary",
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            font_name="Roboto-Regular",
            font_size="120sp"  # Increased font size
        )
        

        if hasattr(self, 'state_label3') and self.state_label3:
            self.root.get_screen('map').remove_widget(self.state_label3)

        self.state_label3 = MDLabel(
            text=f"[color=#AAAAAA]Predicted Location Score: {lol}/10[/color]",
            markup=True,
            halign="center",
            theme_text_color="Primary",
            pos_hint={"center_x": 0.5, "center_y": 0.9},
            font_name="Roboto-Regular",
            font_size="120sp"  # Increased font size
        )
        self.root.get_screen('map').add_widget(self.state_label)
        self.root.get_screen('map').add_widget(self.state_label3)
        self.root.current = 'map'
        map_box = self.root.get_screen('map').ids.map_box
        map_box.clear_widgets()

        map_label = MDLabel(
            halign="center",
            theme_text_color="Primary"
        )
        map_box.add_widget(map_label)

    def open_graph(self):
        self.root.current = 'graph'
        graph_box = self.root.get_screen('graph').ids.graph_box
        graph_box.clear_widgets()
        map_label = MDLabel(
            
            halign="center",
            theme_text_color="Primary"
        )
        graph_box.add_widget(map_label)

    

    def give_suggestions(self):
        if hasattr(self, 'dropdown'):
            self.dropdown.dismiss()
        self.dropdown = DropDown()
        box = self.root.get_screen('main').ids.search_field
        user_input = self.root.get_screen('main').ids.search_field
        suggestions = []

        user_input_text = user_input.text.lower()
        for word in self.suggestions_source:
            if user_input_text in word.lower():
                suggestions.append(word)

        for suggestion in suggestions[:4]:  
            btn = Button(
                text=suggestion,
                size_hint_y=None,
                height='44dp',
                background_normal='',
                background_color=(0.5, 0.5, 0.5, 1),  
                color=(1, 1, 1, 1),
                font_size='16sp',
                border=(16, 16, 16, 16) 
            )
            btn.bind(on_release=lambda btn: select_suggestion(self, btn.text))
            
            self.dropdown.add_widget(btn)
        self.dropdown.open(user_input)

        def select_suggestion(self, text):
            self.root.get_screen('main').ids.search_field.text = text
            self.dropdown.dismiss()


    def give_suggestions2(self):
        if hasattr(self, 'dropdown'):
            self.dropdown.dismiss()
        self.dropdown = DropDown()
        box = self.root.get_screen('main').ids.search_field_2
        user_input = self.root.get_screen('main').ids.search_field_2
        suggestions = []

        user_input_text = user_input.text.lower()
        for word in api.get_county(self.root.get_screen('main').ids.search_field.text):
            if user_input_text in word.lower():
                suggestions.append(word)

        for suggestion in suggestions[:4]:  
            btn = Button(
                text=suggestion,
                size_hint_y=None,
                height='44dp',
                background_normal='',
                background_color=(0.5, 0.5, 0.5, 1),  
                color=(1, 1, 1, 1),
                font_size='16sp',
                border=(16, 16, 16, 16) 
            )
            btn.bind(on_release=lambda btn: select_suggestion(self, btn.text))
            
            self.dropdown.add_widget(btn)
        self.dropdown.open(user_input)

        def select_suggestion(self, text):
            self.root.get_screen('main').ids.search_field_2.text = text
            self.dropdown.dismiss()




if __name__ == '__main__':
    MainApp().run()
