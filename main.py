
# -*- coding: utf-8 -*-
__version__ = "1.0.0"

import json, os
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def ar(s):
        try:
            return get_display(arabic_reshaper.reshape(str(s)))
        except Exception:
            return str(s)
except Exception:
    def ar(s):
        return str(s)

KV = r'''
#:import dp kivy.metrics.dp

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(8)
        Label:
            text: root.title
            font_size: '25sp'
            size_hint_y: None
            height: dp(55)
        ScrollView:
            GridLayout:
                cols: 2
                spacing: dp(8)
                padding: dp(4)
                size_hint_y: None
                height: self.minimum_height
                Button:
                    text: root.ar('المبيعات')
                    on_release: app.show('sales')
                Button:
                    text: root.ar('الطلبات الخاصة')
                    on_release: app.show('orders')
                Button:
                    text: root.ar('المنتجات والمخزون')
                    on_release: app.show('products')
                Button:
                    text: root.ar('العملاء')
                    on_release: app.show('customers')
                Button:
                    text: root.ar('الصندوق')
                    on_release: app.show('cash')
                Button:
                    text: root.ar('التقارير')
                    on_release: app.show('reports')
                Button:
                    text: root.ar('الموظفون والصلاحيات')
                    on_release: app.show('employees')
                Button:
                    text: root.ar('الإعدادات')
                    on_release: app.show('settings')
        Label:
            text: root.summary
            size_hint_y: None
            height: dp(90)
            halign: 'center'
            valign: 'middle'

<FormScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(7)
        Label:
            text: root.title
            font_size: '23sp'
            size_hint_y: None
            height: dp(48)
        ScrollView:
            GridLayout:
                id: fields
                cols: 2
                spacing: dp(6)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(6)
            Button:
                text: root.ar('حفظ')
                on_release: root.save_record()
            Button:
                text: root.ar('الرئيسية')
                on_release: app.show('main')
        Label:
            id: status
            size_hint_y: None
            height: dp(35)

<ListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(7)
        Label:
            text: root.title
            font_size: '23sp'
            size_hint_y: None
            height: dp(48)
        ScrollView:
            Label:
                id: listing
                text: root.items_text
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
                halign: 'right'
                valign: 'top'
                padding: dp(5), dp(5)
        Button:
            text: root.ar('الرئيسية')
            size_hint_y: None
            height: dp(50)
            on_release: app.show('main')
'''

class MainScreen(Screen):
    title = StringProperty("إطارك")
    summary = StringProperty("")
    def ar(self, s): return ar(s)

class FormScreen(Screen):
    title = StringProperty("")
    kind = StringProperty("")
    fields = []
    def ar(self, s): return ar(s)

    def setup(self, title, kind, names):
        self.title = ar(title)
        self.kind = kind
        self.fields = []
        box = self.ids.fields
        box.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        for name in names:
            box.add_widget(Label(text=ar(name), size_hint_y=None, height=45))
            e = TextInput(multiline=False, size_hint_y=None, height=45)
            self.fields.append((name, e))
            box.add_widget(e)

    def save_record(self):
        vals = {name: e.text.strip() for name, e in self.fields}
        if not any(vals.values()):
            self.ids.status.text = ar("اكتب البيانات أولاً")
            return
        app = App.get_running_app()
        app.add_record(self.kind, vals)
        for _, e in self.fields:
            e.text = ""
        self.ids.status.text = ar("تم الحفظ بنجاح")

class ListScreen(Screen):
    title = StringProperty("")
    items_text = StringProperty("")
    def ar(self, s): return ar(s)

class ItarakApp(App):
    def build(self):
        self.title = "إطارك"
        self.path = os.path.join(self.user_data_dir, "itarak_data.json")
        self.data = self.load_data()
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(FormScreen(name="sales"))
        sm.add_widget(FormScreen(name="orders"))
        sm.add_widget(FormScreen(name="products"))
        sm.add_widget(FormScreen(name="customers"))
        sm.add_widget(FormScreen(name="cash"))
        sm.add_widget(ListScreen(name="reports"))
        sm.add_widget(FormScreen(name="employees"))
        sm.add_widget(ListScreen(name="settings"))
        self.sm = sm
        self.refresh_main()
        return sm

    def load_data(self):
        default = {
            "sales": [], "orders": [], "products": [], "customers": [],
            "cash": [], "employees": [{"name":"المدير","pin":"1234","role":"مدير"}]
        }
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                x = json.load(f)
                for k, v in default.items():
                    x.setdefault(k, v)
                return x
        except Exception:
            return default

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def show(self, name):
        if name == "main":
            self.refresh_main()
        elif name == "sales":
            self.sm.get_screen(name).setup("المبيعات", "sales", ["المنتج","الكمية","السعر","الخصم"])
        elif name == "orders":
            self.sm.get_screen(name).setup("الطلبات الخاصة", "orders", ["العميل","الهاتف","النوع","المقاس","الكمية","الإجمالي","العربون","موعد التسليم"])
        elif name == "products":
            self.sm.get_screen(name).setup("المنتجات والمخزون", "products", ["المنتج","الكمية","السعر"])
        elif name == "customers":
            self.sm.get_screen(name).setup("العملاء", "customers", ["الاسم","الهاتف"])
        elif name == "cash":
            self.sm.get_screen(name).setup("الصندوق", "cash", ["الحركة (إيداع/مصروف)","المبلغ","البيان"])
        elif name == "employees":
            self.sm.get_screen(name).setup("الموظفون والصلاحيات", "employees", ["الاسم","PIN","الصلاحية (مدير/كاشير)"])
        elif name == "reports":
            self.refresh_reports()
        elif name == "settings":
            self.refresh_settings()
        self.sm.current = name

    def add_record(self, kind, vals):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        if kind == "sales":
            try:
                q = int(vals.get("الكمية") or 1)
                p = float(vals.get("السعر") or 0)
                d = float(vals.get("الخصم") or 0)
            except Exception:
                q, p, d = 1, 0, 0
            total = max(0, q * p - d)
            vals.update({"الكمية": q, "السعر": p, "الخصم": d, "الإجمالي": total, "التاريخ": now})
        else:
            vals["التاريخ"] = now
        self.data[kind].append(vals)
        self.save()
        self.refresh_main()

    def refresh_main(self):
        total = sum(float(x.get("الإجمالي", 0) or 0) for x in self.data["sales"])
        s = [
            f"المبيعات: {len(self.data['sales'])}",
            f"الطلبات: {len(self.data['orders'])}",
            f"المنتجات: {len(self.data['products'])}",
            f"العملاء: {len(self.data['customers'])}",
            f"إجمالي المبيعات: {total:.3f} د.ل"
        ]
        self.sm.get_screen("main").summary = ar("\n".join(s))

    def refresh_reports(self):
        total = sum(float(x.get("الإجمالي", 0) or 0) for x in self.data["sales"])
        text = (
            f"إجمالي المبيعات: {total:.3f} د.ل\n"
            f"عدد الفواتير: {len(self.data['sales'])}\n"
            f"عدد الطلبات: {len(self.data['orders'])}\n"
            f"عدد المنتجات: {len(self.data['products'])}\n"
            f"عدد العملاء: {len(self.data['customers'])}"
        )
        self.sm.get_screen("reports").title = ar("التقارير")
        self.sm.get_screen("reports").items_text = ar(text)

    def refresh_settings(self):
        screen = self.sm.get_screen("settings")
        screen.title = ar("الإعدادات")
        screen.items_text = ar("حذف جميع الفواتير\n\nهذه نسخة الهاتف الأولية.")

ItarakApp().run()
