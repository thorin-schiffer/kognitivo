from kivy.app import App
from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, InterfaceWithNoMenu, SettingOptions, SettingItem, \
    SettingNumeric, SettingString, SettingBoolean, SettingSpacer, SettingsPanel
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from utils import _, import_kv

import_kv(__file__)


class KognitivoSettingsInterface(InterfaceWithNoMenu):
    pass


class KognitivoSettingTitle(Label):
    title = Label.text

    def on_title(self, instance, value):
        self.text = _(value)


class KognitivoSettingItem(SettingItem):
    pass


class KognitivoSettingString(SettingString, KognitivoSettingItem):
    pass


class KognitivoSettingNumeric(SettingNumeric, KognitivoSettingString):
    pass


class KognitivoSettingOptionsButton(ToggleButton):
    value = ObjectProperty()


class KognitivoSettingOptions(SettingOptions, KognitivoSettingItem):
    def _create_popup(self, instance):
        from kivy.core.window import Window
        from kivy.metrics import dp
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        popup.height = len(self.options) * dp(55) + dp(150)

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for option in self.options:
            state = 'down' if option == self.value else 'normal'
            btn = KognitivoSettingOptionsButton(value=option, state=state, group=uid)
            btn.bind(on_release=self._set_option)
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        btn = Button(text=_('Cancel'), size_hint_y=None, height=dp(50))
        content.add_widget(SettingSpacer())
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()

    def _set_option(self, instance):
        self.value = instance.value
        self.popup.dismiss()


class GroupToggle(SettingItem):
    def __init__(self, toggled_keys=None, **kwargs):
        self.toggled_item_keys = toggled_keys or []
        super(GroupToggle, self).__init__(**kwargs)

    def on_value(self, instance, value):
        super(GroupToggle, self).on_value(instance, value)
        for key in self.toggled_item_keys:
            item = self.panel.settings.get_item(key, self.panel)
            if item:
                item.disabled = int(value) == 0


class KognitivoSettingBoolean(SettingBoolean, GroupToggle, KognitivoSettingItem):
    pass


class TimeSettingLabel(Label):
    pass


class TimeSettingButton(Button):
    direction = OptionProperty('up', options=['up', 'down'])


class SettingTime(KognitivoSettingString):
    up_button = ObjectProperty(None)
    down_button = ObjectProperty(None)

    def _validate(self, instance):
        from datetime import datetime
        self._dismiss()
        try:
            datetime.strptime(self.textinput.text, '%H:%M')
            self.value = self.textinput.text
        except ValueError:
            return

    def on_button_press(self, instance):
        from datetime import datetime, timedelta
        interval = timedelta(minutes=30) if instance.direction == 'up' else timedelta(minutes=-30)
        current_datetime = datetime.strptime(self.textinput.text, '%H:%M')
        self.textinput.text = (current_datetime + interval).time().strftime('%H:%M')

    def _create_popup(self, instance):

        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title, content=content, size_hint=(.9, .6))

        self.textinput = TimeSettingLabel(text=self.value)
        self.textinput.bind(on_text_validate=self._validate)

        self.up_button = TimeSettingButton(direction='up')
        self.down_button = TimeSettingButton(direction='down')
        self.up_button.bind(on_press=self.on_button_press)
        self.down_button.bind(on_press=self.on_button_press)

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(self.up_button)
        content.add_widget(self.textinput)
        content.add_widget(self.down_button)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text=u"\uE013", font_name="glyphicons")
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text=u"\uE014", font_name="glyphicons")
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class KognitivoCheckBox(CheckBox):
    pass


class RateUsLabel(ButtonBehavior, Label):
    pass


class VersionLabel(Label):
    pass


class KognitivoSettingButton(ButtonBehavior, KognitivoSettingItem):
    def on_press(self):
        app = App.get_running_app()
        app.google_client.logout()
        self.parent.remove_widget(self)


class KognitivoSettings(Settings):
    def __init__(self, **kwargs):
        super(KognitivoSettings, self).__init__(**kwargs)
        self.register_type('title', KognitivoSettingTitle)
        self.register_type('options', KognitivoSettingOptions)
        self.register_type('numeric', KognitivoSettingNumeric)
        self.register_type('string', KognitivoSettingString)
        self.register_type('bool', KognitivoSettingBoolean)
        self.register_type('button', KognitivoSettingButton)
        self.register_type('time', SettingTime)

    def add_kivy_panel(self):
        pass

    def create_json_panel(self, title, config, filename=None, data=None):
        import settings as platform_settings
        from kivy.utils import platform

        import json
        sdata = [d for d in json.loads(data)]
        processed_data = []
        for d in sdata:
            platforms = d.get('platforms', None)
            profiles = d.get('profiles', None)
            to_add = bool(not platforms and not profiles)
            to_add |= bool(platforms and platform in platforms and not profiles)
            to_add |= bool(platforms and platform in platforms and platform_settings.PROFILE in profiles)

            if to_add:
                processed_data.append(d)

        panel = SettingsPanel(title=title, settings=self, config=config)

        for setting in processed_data:
            # determine the type and the class to use
            if 'type' not in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                str_settings[str(key)] = item

            instance = cls(panel=panel, **str_settings)

            # instance created, add to the panel
            panel.add_widget(instance)

        notification_toggle = self.get_item('enable_notifications', panel)

        # needed to trigger enabling/disabling the groups after the settings panel is built
        notification_toggle.on_value(self, notification_toggle.value)
        panel.add_widget(RateUsLabel())
        panel.add_widget(VersionLabel())

        return panel

    def get_item(self, key, panel=None):
        panel = panel or self.interface.panels[0]
        for child in panel.children:
            if isinstance(child, SettingItem) and getattr(child, 'key', None) == key:
                return child
