# globalPlugins__init__.py
# Ethiopian Calendar & Bahire Hasab NVDA Plugin

import os
import json
import datetime
import math
import functools
import re
from pathlib import Path
import globalPluginHandler
import scriptHandler
import ui
import gui
import api
import config
import globalVars
from gui import guiHelper
import wx
import logHandler

# ============================================================
# CONSTANTS
# ============================================================
MONTHS = ["", "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት", "መጋቢት",
          "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"]

WEEKDAYS = ["ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ", "እሁድ"]

ISLAMIC_MONTHS = [
    "", "ሙሐረም", "ሰፈር", "ረቢዑል አወል", "ረቢዑል ሳኒ", "ጀማደል አወል", "ጀማደል ሳኒ",
    "ረጀብ", "ሻእባን", "ረመዳን", "ሸዋል", "ዙልቂዳህ", "ዙልሒጃህ"
]

ISLAMIC_EPOCH = 1948440
HEBREW_EPOCH = 347998

MONTHLY_FEAST_PREFIX = "ወርኃዊ በዓል፦ "

# ============================================================
# GREAT LENT WEEK NAMES (from web app)
# ============================================================
GREAT_LENT_WEEK_KEYS = ["lent_week_1", "lent_week_2", "lent_week_3", "lent_week_4",
                        "lent_week_5", "lent_week_6", "lent_week_7", "lent_week_8"]

GREAT_LENT_WEEK_NAMES_AM = [
    "ዘወረደ (Zewerede)",
    "ቅድስት (Qidist)",
    "ምኵራብ (Mikurab)",
    "መጻጉዕ (Metsagu)",
    "ደብረ ዘይት (Debre Zeyit)",
    "ገብር ኄር (Gebre Hier)",
    "ኒቆዲሞስ (Nikodimos)",
    "ሆሳዕና (Hosanna)"
]

GREAT_LENT_WEEK_NAMES_EN = [
    "Zewerede",
    "Qidist",
    "Mikurab",
    "Metsagu",
    "Debre Zeyit",
    "Gebre Hier",
    "Nikodimos",
    "Hosanna"
]

# ============================================================
# SHORTCUT REGISTRY
# ============================================================
SHORTCUT_REGISTRY = {
    "fullInfo": {"label": "የዛሬ ሙሉ መረጃ (ባሕረ ሐሳብ)", "default": True, "gesture": "kb:control+shift+e"},
    "fullDateHtml": {"label": "የዛሬ ሙሉ መረጃ በመስኮት", "default": True, "gesture": "kb:control+shift+f"},
    "fdreHolidays": {"label": "ብሔራዊ በዓላት", "default": True, "gesture": "kb:control+shift+a"},
    "ethiopianLocalTime": {"label": "የኢትዮጵያ ሰዓት", "default": True, "gesture": "kb:control+shift+t"},
    "kekrosTime": {"label": "የኬክሮስ ሰዓት", "default": True, "gesture": "kb:control+shift+q"},
    "copyDate": {"label": "ቀኑን ኮፒ አድርግ", "default": True, "gesture": "kb:control+shift+c"},
    "upcomingEvent": {"label": "ቀጣይ በዓላትና አጽዋማት", "default": True, "gesture": "kb:control+shift+u"},
    "movableFeasts": {"label": "የዘንድሮ ተንቀሳቃሽ በዓላት", "default": True, "gesture": "kb:control+shift+m"},
    "readSynaxarium": {"label": "የዛሬ ዓመታዊ በዓላት", "default": True, "gesture": "kb:control+shift+s"},
    "readMonthlyFeasts": {"label": "የዛሬ ወርኃዊ በዓላት", "default": True, "gesture": "kb:control+shift+w"},
    "searchSynaxarium": {"label": "በስንክሳር ውስጥ ፈልግ", "default": True, "gesture": "kb:control+shift+k"},
    "yearlyFeasts": {"label": "የዓመቱ ሙሉ መረጃ", "default": True, "gesture": "kb:control+shift+y"},
    "searchDate": {"label": "የኢትዮጵያ ቀን ፈልግ", "default": True, "gesture": "kb:control+shift+d"},
    "searchGregorianDate": {"label": "የግሪጎሪያን ቀን ቀይር", "default": True, "gesture": "kb:control+shift+g"},
    "islamicInfo": {"label": "የዛሬ ሂጅሪ መረጃ", "default": True, "gesture": "kb:control+shift+i"},
    "islamicFullHtml": {"label": "ሙሉ ሂጅሪ መረጃ በመስኮት", "default": True, "gesture": "kb:control+alt+i"},
    "searchIslamicDate": {"label": "ሂጅሪ ቀን ፈልግ", "default": True, "gesture": "kb:control+shift+h"},
    "copyIslamicDate": {"label": "ሂጅሪ ቀን ኮፒ አድርግ", "default": True, "gesture": "kb:control+shift+b"},
    "searchHebrewDate": {"label": "የዕብራውያን ቀን ፈልግ", "default": True, "gesture": "kb:control+shift+l"},
    "periodicSettings": {"label": "የወር አበባ ማቀናበሪያ", "default": True, "gesture": "kb:control+alt+p"},
    "announcePeriodic": {"label": "የወር አበባ ሁኔታ", "default": True, "gesture": "kb:control+shift+p"},
    "clearPeriodicData": {"label": "የወር አበባ መረጃ አጥፋ", "default": True, "gesture": "kb:control+alt+shift+p"},
    "calculatePregnancy": {"label": "የእርግዝና እና የወሊድ ጊዜ መገመቻ", "default": True, "gesture": "kb:control+alt+n"},
    "calculateAge": {"label": "ዕድሜ ማስያ", "default": True, "gesture": "kb:control+shift+n"},
    "gitsaweReadings": {"label": "የዕለቱ ግጻዌ (የቤተክርስቲያን ንባቦች)", "default": True, "gesture": "kb:control+shift+r"},
    "synaxariumByDate": {"label": "በስንክሳር በቀን ፈልግ", "default": True, "gesture": "kb:control+shift+alt+s"},
    "gitsaweSearch": {"label": "በግጻዌ ውስጥ ፈልግ", "default": True, "gesture": "kb:control+alt+r"},
    "planning": {"label": "ዕቅድ አዘጋጅ", "default": True, "gesture": "kb:control+alt+y"},
    "agenda": {"label": "አጀንዳ", "default": True, "gesture": "kb:control+alt+a"},
    "agendaPage": {"label": "አጀንዳ በመስኮት", "default": True, "gesture": "kb:control+shift+alt+a"},
    "dayAgenda": {"label": "የቀን አጀንዳ", "default": True, "gesture": "kb:control+alt+d"},
    "gitsaweByDate": {"label": "በግጻዌ በቀን ፈልግ", "default": True, "gesture": ""},
    "gitsaweStructure": {"label": "የግጻዌ መጽሐፍ ማውጫ", "default": True, "gesture": "kb:control+alt+s"},
    "holidaysIcal": {"label": "የዓመቱን በዓላት ወደ iCal ላክ", "default": True, "gesture": "kb:control+alt+h"},
}

# ============================================================
# SHORTCUT DECORATOR
# ============================================================
def guarded_by_shortcut_setting(script_id=None):
    """
    Decorator that checks if a specific shortcut is enabled before executing the script.
    If script_id is None, uses the function name as the ID.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, gesture, *args, **kwargs):
            sid = script_id if script_id is not None else func.__name__.replace("script_", "")
            if gesture is not None:
                if not getattr(self, "shortcuts_enabled", True) or not self.is_shortcut_enabled(sid):
                    logHandler.log.info(f"Ethiopian Calendar: shortcut '{sid}' is turned off; key passed through")
                    try:
                        gesture.send()
                    except Exception:
                        pass
                    return
            logHandler.log.info(f"Ethiopian Calendar: running '{sid}'")
            return func(self, gesture, *args, **kwargs)
        return wrapper
    return decorator

# ============================================================
# AMHARIC TEXT UTILITIES
# ============================================================
_AMHARIC_HOMOPHONE_GROUPS = [
    ["ሀሁሂሃሄህሆ", "ሐሑሒሓሔሕሖ", "ኀኁኂኃኄኅኆ"],
    ["ሰሱሲሳሴስሶ", "ሠሡሢሣሤሥሦ"],
    ["አኡኢኣኤእኦ", "ዐዑዒዓዔዕዖ"],
    ["ጸጹጺጻጼጽጾ", "ፀፁፂፃፄፅፆ"],
]

_AMHARIC_HOMOPHONE_MAP = {}
for _group in _AMHARIC_HOMOPHONE_GROUPS:
    _canonical_row = _group[0]
    for _row in _group[1:]:
        for _i in range(len(_canonical_row)):
            _AMHARIC_HOMOPHONE_MAP[_row[_i]] = _canonical_row[_i]

def normalize_amharic(text):
    return "".join(_AMHARIC_HOMOPHONE_MAP.get(ch, ch) for ch in text)

# ============================================================
# MONTH ALIASES
# ============================================================
MONTH_NAME_EXTRA_ALIASES = {
    3: ["ህዳር", "ሕዳር"],
    4: ["ታህሳስ", "ታሕሳስ"],
    11: ["ሃምሌ", "ኃምሌ"],
    12: ["ነሃሴ", "ነኃሴ"],
    13: ["ጳጐሜ", "ጳጎሜ", "ጳጉሜን", "ጳጐሜን", "ጳጎሜን"],
}

ENGLISH_MONTHS = [
    "", "Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yekatit", "Megabit",
    "Miazia", "Ginbot", "Sene", "Hamle", "Nehase", "Pagume"
]

ENGLISH_MONTH_EXTRA_ALIASES = {
    1: ["Maskaram", "Maskarem"],
    2: ["Tikemt", "Tekemt", "Tiqimt"],
    3: ["Hedar"],
    4: ["Tahesas", "Tachesas"],
    5: ["Ter"],
    6: ["Yekatit", "Yekattit"],
    7: ["Magabit"],
    8: ["Miyazya", "Miyazia"],
    9: ["Genbot"],
    10: ["Sane"],
    11: ["Hamlie"],
    12: ["Nehasse", "Nehase"],
    13: ["Pagumen", "Paguemen", "Paguemien"],
}

# ============================================================
# SHORTCUT SETTINGS DIALOG
# ============================================================
class ShortcutSettingsDialog(wx.Dialog):
    """Dialog for managing individual shortcut enable/disable settings."""

    def __init__(self, parent, plugin):
        super().__init__(parent, title="የቁልፍ ሰሌዳ አቋራጭ መንገዶች ማቀናበሪያ")
        self.plugin = plugin

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        self.globalCheckbox = wx.CheckBox(self, label="ሁሉንም አቋራጭ መንገዶች አንቃ (Enable all shortcuts)")
        self.globalCheckbox.SetValue(plugin.shortcuts_enabled)
        sHelper.addItem(self.globalCheckbox)

        sHelper.addItem(wx.StaticText(self, label="\nበተናጥል ማብራት/ማጥፋት የሚችሏቸው አቋራጭ መንገዶች፦"))

        self.shortcut_checkboxes = {}
        self.shortcut_ids = []

        categories = {
            "የኢትዮጵያ ቀን አቆጣጠር": ["fullInfo", "fullDateHtml", "fdreHolidays", "holidaysIcal", "ethiopianLocalTime",
                                       "kekrosTime", "copyDate", "upcomingEvent", "movableFeasts",
                                       "readSynaxarium", "readMonthlyFeasts", "searchSynaxarium",
                                       "yearlyFeasts", "searchDate", "searchGregorianDate",
                                       "gitsaweReadings", "synaxariumByDate"],
            "የእስልምና ቀን አቆጣጠር": ["islamicInfo", "islamicFullHtml", "searchIslamicDate", "copyIslamicDate"],
            "የዕብራውያን ቀን አቆጣጠር": ["searchHebrewDate"],
            "የወር አበባ፣ እርግዝና እና ዕድሜ": ["periodicSettings", "announcePeriodic", "clearPeriodicData",
                                               "calculatePregnancy", "calculateAge"],
            "የግጻዌ፣ ዕቅድ እና አጀንዳ": ["gitsaweSearch", "gitsaweByDate", "gitsaweStructure", "planning", "agenda",
                                          "agendaPage", "dayAgenda"],
        }

        current_settings = plugin.load_shortcut_settings()

        for category, ids in categories.items():
            sHelper.addItem(wx.StaticText(self, label=f"\n{category}"))
            for sid in ids:
                if sid in SHORTCUT_REGISTRY:
                    label = SHORTCUT_REGISTRY[sid]["label"]
                    gesture = SHORTCUT_REGISTRY[sid].get("gesture", "")

                    if gesture:
                        display_gesture = gesture.replace("kb:", "")
                        display_gesture = display_gesture.replace("control", "Ctrl")
                        display_gesture = display_gesture.replace("shift", "Shift")
                        display_gesture = display_gesture.replace("alt", "Alt")
                        display_gesture = display_gesture.upper()
                        display_gesture = display_gesture.replace("CTRL", "Ctrl")
                        display_gesture = display_gesture.replace("SHIFT", "Shift")
                        display_gesture = display_gesture.replace("ALT", "Alt")
                        parts = display_gesture.split('+')
                        unique_parts = []
                        for p in parts:
                            if p not in unique_parts:
                                unique_parts.append(p)
                        display_gesture = '+'.join(unique_parts)
                    else:
                        display_gesture = ""

                    full_label = label
                    if display_gesture:
                        full_label = f"{label}  [ {display_gesture} ]"

                    cb = wx.CheckBox(self, label=full_label)
                    enabled = current_settings.get(sid, True)
                    cb.SetValue(enabled)
                    self.shortcut_checkboxes[sid] = cb
                    self.shortcut_ids.append(sid)
                    sHelper.addItem(cb)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        enable_all_btn = wx.Button(self, label="ሁሉንም አንቃ (Enable All)")
        disable_all_btn = wx.Button(self, label="ሁሉንም አጥፋ (Disable All)")
        restore_defaults_btn = wx.Button(self, label="ነባር አስቀምጥ (Restore Defaults)")

        btn_sizer.Add(enable_all_btn, 0, wx.ALL, 5)
        btn_sizer.Add(disable_all_btn, 0, wx.ALL, 5)
        btn_sizer.Add(restore_defaults_btn, 0, wx.ALL, 5)
        sHelper.addItem(btn_sizer)

        enable_all_btn.Bind(wx.EVT_BUTTON, self.on_enable_all)
        disable_all_btn.Bind(wx.EVT_BUTTON, self.on_disable_all)
        restore_defaults_btn.Bind(wx.EVT_BUTTON, self.on_restore_defaults)

        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))

        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()

    def on_enable_all(self, evt):
        for cb in self.shortcut_checkboxes.values():
            cb.SetValue(True)

    def on_disable_all(self, evt):
        for cb in self.shortcut_checkboxes.values():
            cb.SetValue(False)

    def on_restore_defaults(self, evt):
        for sid, cb in self.shortcut_checkboxes.items():
            cb.SetValue(SHORTCUT_REGISTRY.get(sid, {}).get("default", True))

    def get_results(self):
        results = {}
        for sid, cb in self.shortcut_checkboxes.items():
            results[sid] = cb.GetValue()
        return results

# ============================================================
# SYNAXARIUM BY DATE DIALOG
# ============================================================
class SynaxariumByDateDialog(wx.Dialog):
    def __init__(self, parent, year="", month="", day=""):
        super().__init__(parent, title="በስንክሳር በቀን ፈልግ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        sHelper.addItem(wx.StaticText(self, label="የሚፈልጉትን የኢትዮጵያ ቀን ያስገቡ፦"))

        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ም)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (ቁጥር ከ1-13፣ ወይም ስም)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን (1-30 ወይም 1-6 ለጳጉሜ)፦", wx.TextCtrl)

        if year: self.yearCtrl.SetValue(str(year))
        if month: self.monthCtrl.SetValue(str(month))
        if day: self.dayCtrl.SetValue(str(day))

        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

# ============================================================
# DIALOG CLASSES
# ============================================================
class DateSearchDialog(wx.Dialog):
    def __init__(self, parent, year="", month="", day=""):
        super().__init__(parent, title="የኢትዮጵያ ቀን ፍለጋ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ም፣ ካልገባ የአሁኑ ዓመት ጥቅም ላይ ይውላል)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (ቁጥር ከ1-13፣ ወይም ስም/ምህጻረ ቃል)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን (ካልገባ የወር ወይም የዓመት አጠቃላይ መረጃ ይታያል)፦", wx.TextCtrl)
        if year: self.yearCtrl.SetValue(str(year))
        if month: self.monthCtrl.SetValue(str(month))
        if day: self.dayCtrl.SetValue(str(day))
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class GregorianSearchDialog(wx.Dialog):
    def __init__(self, parent, year="", month="", day=""):
        super().__init__(parent, title="የግሪጎሪያን (ፈረንጅ) ቀን ወደ ኢትዮጵያ መቀየሪያ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (Gregorian Year)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (Gregorian Month 1-12)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን (Gregorian Day 1-31)፦", wx.TextCtrl)
        if year: self.yearCtrl.SetValue(str(year))
        if month: self.monthCtrl.SetValue(str(month))
        if day: self.dayCtrl.SetValue(str(day))
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class IslamicSearchDialog(wx.Dialog):
    def __init__(self, parent, year="", month="", day=""):
        super().__init__(parent, title="የሂጅሪ (እስላማዊ) ቀን ወደ ኢትዮጵያ መቀየሪያ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ሂ - Hijri Year)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (Hijri Month 1-12)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን (Hijri Day 1-30)፦", wx.TextCtrl)
        if year: self.yearCtrl.SetValue(str(year))
        if month: self.monthCtrl.SetValue(str(month))
        if day: self.dayCtrl.SetValue(str(day))
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class HebrewSearchDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="የዕብራውያን ቀን ወደ ኢትዮጵያ መቀየሪያ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (Hebrew Year)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (Hebrew Month 1-13)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን (Hebrew Day 1-30)፦", wx.TextCtrl)
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class AgeCalculatorDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="ትክክለኛ ዕድሜ ማስያ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        sHelper.addItem(wx.StaticText(self, label="የትውልድ ቀንዎን በኢትዮጵያ አቆጣጠር ያስገቡ፦"))
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ም)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (1-13)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን፦", wx.TextCtrl)
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class PregnancyCalculatorDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="የእርግዝና እና የወሊድ ጊዜ መገመቻ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        sHelper.addItem(wx.StaticText(self, label="የመጨረሻው የወር አበባ የታየበትን የመጀመሪያ ቀን (LMP) ያስገቡ፦"))
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ም)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (1-13)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን፦", wx.TextCtrl)
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class PeriodicSettingsDialog(wx.Dialog):
    def __init__(self, parent, year="", month="", day="", cycle_len="28", period_len="5"):
        super().__init__(parent, title="የወር አበባ ዑደት ማቀናበሪያ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        sHelper.addItem(wx.StaticText(self, label="የመጨረሻው የወር አበባ የታየበትን ቀን በኢትዮጵያ አቆጣጠር ያስገቡ፦"))
        self.yearCtrl = sHelper.addLabeledControl("ዓመት (ዓ.ም)፦", wx.TextCtrl)
        self.monthCtrl = sHelper.addLabeledControl("ወር (1-13)፦", wx.TextCtrl)
        self.dayCtrl = sHelper.addLabeledControl("ቀን፦", wx.TextCtrl)
        sHelper.addItem(wx.StaticText(self, label="\nየዑደትዎን መረጃ ያስገቡ፦"))
        self.cycleCtrl = sHelper.addLabeledControl("የዑደት ርዝመት (በቀናት፣ አብዛኛውን ጊዜ 28)፦", wx.TextCtrl)
        self.periodCtrl = sHelper.addLabeledControl("የወር አበባ የሚቆይበት ጊዜ (በቀናት፣ አብዛኛውን ጊዜ 5)፦", wx.TextCtrl)
        if year: self.yearCtrl.SetValue(str(year))
        if month: self.monthCtrl.SetValue(str(month))
        if day: self.dayCtrl.SetValue(str(day))
        if cycle_len: self.cycleCtrl.SetValue(str(cycle_len))
        if period_len: self.periodCtrl.SetValue(str(period_len))
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.yearCtrl.SetFocus()

class SynaxariumSearchDialog(wx.Dialog):
    def __init__(self, parent, query=""):
        super().__init__(parent, title="በስንክሳር ውስጥ ፍለጋ")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.queryCtrl = sHelper.addLabeledControl("የቅዱስ ወይም የበዓል ስም (ወይም የስሙ ክፍል) ያስገቡ፦", wx.TextCtrl)
        if query: self.queryCtrl.SetValue(str(query))
        sHelper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        self.SetSizerAndFit(mainSizer)
        self.CentreOnScreen()
        self.queryCtrl.SetFocus()

# ============================================================
# GITSAWE DIALOGS (search only; readings are HTML pages now)
# ============================================================
class GitsaweSearchDialog(wx.Dialog):
    def __init__(self, parent, plugin=None):
        super().__init__(parent, title="በግጻዌ ውስጥ ፍለጋ")
        self.plugin = plugin
        helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        label = wx.StaticText(
            self,
            label="የመጻሕፍት፣ የምስባክ፣ የወንጌል ወይም የመታሰቢያ ፍለጋ፦"
        )
        label.SetName("የፍለጋ መግለጫ")
        helper.addItem(label)

        self.query = helper.addLabeledControl("ፍለጋ፦", wx.TextCtrl)
        self.query.SetName("የፍለጋ ሳጥን")
        self.query.SetHelpText("የሚፈልጉትን ቃል ያስገቡ። Enter ይጫኑ።")

        helper.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizerAndFit(helper.sizer)
        self.CentreOnScreen()
        self.query.SetFocus()


class GitsaweSearchResultsDialog(wx.Dialog):
    def __init__(self, parent, plugin, query, results):
        super().__init__(parent, title=f"የግጻዌ ፍለጋ ውጤት — {query}")
        self.plugin = plugin
        self.results = results

        main = wx.BoxSizer(wx.VERTICAL)
        helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        heading = wx.StaticText(
            self,
            label=f"'{query}' — {len(results)} ውጤቶች ተገኝተዋል"
        )
        heading.SetName("የውጤት ብዛት")
        helper.addItem(heading)

        list_label = wx.StaticText(self, label="&ውጤቶች፦")
        helper.addItem(list_label)
        self.list = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.list.InsertColumn(0, "ወር", width=140)
        self.list.InsertColumn(1, "ቀን", width=70)
        self.list.InsertColumn(2, "የተገኘበት ክፍል", width=520)
        self.list.SetName("የፍለጋ ውጤቶች")
        self.list.SetHelpText("አንድ ውጤት ይምረጡ፤ Enter ይጫኑ ለማየት።")
        for idx, r in enumerate(results):
            item = self.list.InsertItem(idx, r.get("month_name", ""))
            self.list.SetItem(item, 1, str(r.get("day_index", "")))
            self.list.SetItem(item, 2, " | ".join(r.get("matches", []) or []))
        if results:
            self.list.Select(0)
            self.list.Focus(0)
        helper.addItem(self.list, proportion=1, flag=wx.EXPAND)

        self.status = wx.StaticText(self, label="")
        self.status.SetName("ሁኔታ")
        helper.addItem(self.status)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_open = wx.Button(self, wx.ID_OK, label="ግጻዌ &ክፈት")
        self.btn_open.SetName("ግጻዌ ክፈት")
        self.btn_open.SetHelpText("የተመረጠውን የግጻዌ ቀን ይክፈታል።")
        self.btn_open.SetDefault()
        btn_sizer.Add(self.btn_open, 0, wx.ALL, 4)

        self.btn_close = wx.Button(self, wx.ID_CANCEL, label="&ዝጋ")
        self.btn_close.SetName("ዝጋ")
        self.btn_close.SetHelpText("መስኮቱን ይዘጋል።")
        btn_sizer.Add(self.btn_close, 0, wx.ALL, 4)
        helper.addItem(btn_sizer)

        self.btn_open.Bind(wx.EVT_BUTTON, self._on_open)
        self.btn_close.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_open)

        main.Add(helper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(main)
        self.SetMinSize((760, 480))
        self.SetSize((820, 520))
        self.CentreOnScreen()

    def _on_open(self, evt):
        i = self.list.GetFirstSelected()
        if i < 0 or i >= len(self.results):
            return
        r = self.results[i]
        em = r.get("month_index")
        ed = r.get("day_index")
        reading = self.plugin.get_day_reading(em, ed)
        if not reading:
            self.status.SetLabel("ውጤቱ ሊከፈት አልተቻለም።")
            return
        # Close this dialog first, then show the HTML page in the main window.
        self.EndModal(wx.ID_OK)
        wx.CallAfter(self.plugin._open_gitsawe_page, em, ed, reading)


# ============================================================
# BIBLE TEXT DIALOG (on-demand focused viewer; no "ጽሑፍ" wording)
# ============================================================
class BibleTextDialog(wx.Dialog):
    def __init__(self, parent, plugin, result):
        v_first = result["verses"][0]["verse"]
        v_last = result["verses"][-1]["verse"]
        v_range = str(v_first) if v_first == v_last else f"{v_first}-{v_last}"
        title = f"{result['book_name_am']} {result['chapter']}:{v_range}"
        if result.get("corrected"):
            title += " (በማስተካከያ)"
        super().__init__(parent, title=title)
        self.plugin = plugin
        self.result = result

        main = wx.BoxSizer(wx.VERTICAL)
        helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        header = wx.StaticText(self, label=title)
        font = header.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 2)
        header.SetFont(font)
        header.SetName("የጥቅስ ርዕስ")
        helper.addItem(header)

        if result.get("corrected"):
            note = wx.StaticText(
                self,
                label="ማስታወሻ፦ ይህ ጥቅስ ከላይ ከተጠቀሰው ሊለያይ ይችላል (የማስተካከያ ሠንጠረዥ)።"
            )
            note.SetName("የማስተካከያ ማስታወሻ")
            helper.addItem(note)

        # Verse list: column 0 = verse number, column 1 = verse (no header word).
        list_label = wx.StaticText(self, label="&ቁጥሮች፦")
        helper.addItem(list_label)
        self.verse_list = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.verse_list.InsertColumn(0, "ቁጥር", width=80)
        self.verse_list.InsertColumn(1, "", width=620)
        self.verse_list.SetName("የቁጥሮች ዝርዝር")
        self.verse_list.SetHelpText("በየቁጥሩ የተከፋፈለው የመጽሐፍ ቅዱስ ንባብ።")
        for idx, v in enumerate(result["verses"]):
            item = self.verse_list.InsertItem(idx, str(v.get("verse", "")))
            self.verse_list.SetItem(item, 1, v.get("text", "") or "")
        if result["verses"]:
            self.verse_list.Select(0)
            self.verse_list.Focus(0)
        helper.addItem(self.verse_list, proportion=2, flag=wx.EXPAND)

        read_label = wx.StaticText(self, label="ሙሉ &ንባብ፦")
        helper.addItem(read_label)
        continuous = " ".join(
            f"{v.get('verse','')}። {v.get('text','')}" for v in result["verses"]
        )
        self.full_text = wx.TextCtrl(
            self, value=continuous,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_SUNKEN,
        )
        self.full_text.SetName("ሙሉ ንባብ")
        self.full_text.SetHelpText("ሙሉ ንባቡ በተከታታይ ተቀምጧል።")
        helper.addItem(self.full_text, proportion=2, flag=wx.EXPAND)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        copy_btn = wx.Button(self, wx.ID_ANY, label="ሁሉንም &ኮፒ")
        copy_btn.SetName("ሁሉንም ኮፒ")
        copy_btn.SetHelpText("ሙሉውን ንባብ ወደ ቅንጥብ ሰሌዳ ይቀዳል።")
        copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)
        btn_sizer.Add(copy_btn, 0, wx.ALL, 4)

        read_btn = wx.Button(self, wx.ID_ANY, label="ጮህ ብለህ &አንብብ")
        read_btn.SetName("ጮህ ብለህ አንብብ")
        read_btn.SetHelpText("ሙሉውን ንባብ በድምፅ ያነባል።")
        read_btn.Bind(wx.EVT_BUTTON, self._on_read)
        btn_sizer.Add(read_btn, 0, wx.ALL, 4)

        close_btn = wx.Button(self, wx.ID_CANCEL, label="&ዝጋ")
        close_btn.SetName("ዝጋ")
        close_btn.SetHelpText("የንባቡን መስኮት ይዘጋል።")
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(close_btn, 0, wx.ALL, 4)
        helper.addItem(btn_sizer)

        main.Add(helper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(main)
        self.SetMinSize((720, 520))
        self.SetSize((820, 580))
        self.CentreOnScreen()
        self.verse_list.SetFocus()

    def _passage_text(self):
        return "\n".join(
            f"{v.get('verse','')}። {v.get('text','')}" for v in self.result["verses"]
        )

    def _on_copy(self, evt):
        text = self._passage_text()
        if not text:
            ui.message("የሚቀዳ ንባብ የለም።")
            return
        payload = f"{self.GetTitle()}\n{text}"
        if api.copyToClip(payload):
            ui.message("ንባቡ ተቀድቷል።")
        else:
            ui.message("ኮፒ ማድረግ አልተቻለም።")

    def _on_read(self, evt):
        if not self.result["verses"]:
            ui.message("የሚነበብ ንባብ የለም።")
            return
        ui.message(f"{self.GetTitle()}። " + self._passage_text())


# ============================================================
# GITSAWE HTML PAGE RENDERER
# ============================================================
def render_gitsawe_html(plugin, blocks, title, em, ed, commemoration=""):
    """
    Build a fully navigable HTML page for a day's Gitsawe readings.

    Structure:
      <h1>  title (date + optional commemoration)
      <h2>  service name  (ዘነግህ / ዘቅዳሴ / ዘሠርክ)
      <h3>  section name  (ምስባክ / መልእክታትና ግብረ ሐዋርያት / ወንጌል / ቅዳሴ)
      <h4>  citation line (book + chapter:verse)
      <ul>  psalm verses (for ምስባክ)
      <ul style="list-style-type:none">  inlined Bible passage (one verse per list item)

    Every citation's full Bible text is inlined via resolve_and_fetch
    so the page is self-contained; users navigate it with H / L / O.
    """
    def esc(s):
        return (str(s or "")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    parts = ["<main lang='am' style='line-height:1.6;'>"]
    parts.append(f"<h1>{esc(title)}</h1>")
    if commemoration:
        parts.append(f"<p><strong>መታሰቢያ፦</strong> {esc(commemoration)}</p>")

    for blk in blocks:
        kind = blk.get("kind")

        if kind == "service_header":
            parts.append(f"<h2>{esc(blk['text'])}</h2>")

        elif kind == "mesbak_header":
            cv = blk.get("cv", "")
            book = blk.get("book") or "መዝሙር"
            pm = blk.get("psalm_masoretic")
            heading = f"ምስባክ — {book} {cv}"
            if pm:
                heading += f" (መዝ. {pm})"
            parts.append(f"<h3>{esc(heading)}</h3>")

            verses = blk.get("verses") or []
            if verses:
                parts.append("<ul>")
                for v in verses:
                    parts.append(f"<li>{esc(v)}</li>")
                parts.append("</ul>")

            full = plugin.resolve_and_fetch(
                blk.get("book_raw", ""), blk.get("cv_raw", ""),
                blk.get("context"),
                {"month": blk.get("month"), "day": blk.get("day"),
                 "slot": blk.get("slot"), "role": blk.get("role")},
            )
            _append_bible_passage_html(parts, full, esc)

        elif kind == "epistles_header":
            parts.append(f"<h3>{esc(blk['text'])}</h3>")

        elif kind == "epistle":
            heading = f"{blk.get('reading_type','')} — {blk.get('cv','')}"
            parts.append(f"<h4>{esc(heading)}</h4>")
            if blk.get("incipit"):
                parts.append(f"<blockquote>{esc(blk['incipit'])}</blockquote>")
            full = plugin.resolve_and_fetch(
                blk.get("book_raw", ""), blk.get("cv_raw", ""),
                blk.get("context"),
                {"month": blk.get("month"), "day": blk.get("day"),
                 "slot": blk.get("slot"), "role": blk.get("role")},
            )
            _append_bible_passage_html(parts, full, esc)

        elif kind == "gospel":
            heading = f"ወንጌል — {blk.get('book','')} {blk.get('cv','')}"
            parts.append(f"<h3>{esc(heading)}</h3>")
            if blk.get("incipit"):
                parts.append(f"<blockquote>{esc(blk['incipit'])}</blockquote>")
            full = plugin.resolve_and_fetch(
                blk.get("book_raw", ""), blk.get("cv_raw", ""),
                blk.get("context"),
                {"month": blk.get("month"), "day": blk.get("day"),
                 "slot": blk.get("slot"), "role": blk.get("role")},
            )
            _append_bible_passage_html(parts, full, esc)

        elif kind == "anaphora":
            parts.append(f"<h3>ቅዳሴ</h3><p>{esc(blk.get('text',''))}</p>")

        elif kind == "commemoration":
            parts.append(f"<p><strong>መታሰቢያ፦</strong> {esc(blk['text'])}</p>")

        elif kind == "empty":
            parts.append(f"<p>{esc(blk['text'])}</p>")

    parts.append("</main>")
    return "".join(parts)


def _append_bible_passage_html(parts, result, esc):
    """
    Append the resolved Bible passage as a list of verses.
    Use an unordered list with list-style-type:none so the renderer
    does NOT add its own numbering — otherwise each verse shows two
    numbers (the auto list marker plus the verse's own '12።').
    """
    if not result or not result.get("verses"):
        return
    book = result.get("book_name_am") or ""
    chapter = result.get("chapter")
    verses = result["verses"]
    v_first = verses[0].get("verse")
    v_last = verses[-1].get("verse")
    v_range = str(v_first) if v_first == v_last else f"{v_first}–{v_last}"

    # Heading so users can jump to the passage via H navigation.
    parts.append(f"<h4>{esc(book)} {chapter}:{v_range}</h4>")

    if result.get("corrected"):
        parts.append("<p><em>ማስታወሻ፦ ይህ ጥቅስ ከላይ ከተጠቀሰው ሊለያይ ይችላል።</em></p>")

    # Unordered list, no bullet, so only the verse's own number shows.
    parts.append('<ul style="list-style-type:none; padding-left:1em; margin-top:0.2em;">')
    for v in verses:
        num = v.get("verse", "")
        txt = v.get("text", "") or ""
        parts.append(f'<li style="margin-bottom:0.3em;"><strong>{esc(num)}።</strong> {esc(txt)}</li>')
    parts.append("</ul>")


# ============================================================
# PLANNING / AGENDA HTML RENDERERS
# ============================================================
PLAN_STATUS_KEYS = ["planned", "in-progress", "done", "skipped"]

PLAN_STATUS_LABELS = {
    "planned": "ታቅዷል",
    "in-progress": "በሂደት",
    "done": "ተጠናቋል",
    "skipped": "ተዘለለ",
}

PLAN_UNIT_LABELS = {
    "day": "ቀን",
    "week": "ሳምንት",
    "month": "ወር",
    "year": "ዓመት",
    "custom": "የተወሰነ የቀን ክልል",
}

PLAN_FAMILY_KEYS = ["all", "none", "climatic", "fasting", "liturgical", "lent-week"]

PLAN_FAMILY_LABELS = {
    "all": "ሁሉም ቀናት",
    "none": "ምንም",
    "climatic": "የአየር ወቅት",
    "fasting": "የጾም ወቅት",
    "liturgical": "የቤተክርስቲያን ዘመን",
    "lent-week": "የዐቢይ ጾም ሳምንት",
}

PLAN_COLUMNS = [
    ("climatic", "climatic", "የአየር ወቅት"),
    ("fasting", "fasting", "የጾም ወቅት"),
    ("liturgical", "liturgical", "የቤተክርስቲያን ዘመን"),
    ("lent", "greatLentWeek", "የዐቢይ ጾም ሳምንት"),
]

PLAN_SEASON_CATALOGS = {
    "climatic": [("autumn", "መፀው (Autumn)"), ("summer", "በጋ (Summer)"),
                 ("spring", "በልግ (Spring)"), ("winter", "ክረምት (Winter)")],
    "fasting": [("none", "የአጽዋም ዘመን አይደለም"), ("abiy", "ዐቢይ ጾም"),
                ("nebiyat", "ጾመ ነቢያት"), ("filseta", "ጾመ ፍልሰታ"),
                ("hawaryat", "ጾመ ሐዋርያት"), ("nenewe", "ጾመ ነነዌ"),
                ("gehad", "ጾመ ገሀድ"), ("hamsa", "ኀምሳ ዕለት"), ("dihnet", "ጾመ ድኅነት")],
    "liturgical": [(x, x) for x in ["ዘመነ ዮሐንስ", "ዘካርያስ", "ዘመነ ፍሬ", "ዘመነ መስቀል",
                                     "ዘመነ ጽጌ", "ዘመነ አስተምሕሮ", "ዘመነ ስብከት",
                                     "ዘመነ ብርሃን", "ዘመነ ኖላዊ", "ዘመነ መርዓዊ",
                                     "አማኑኤል", "ዘመነ ልደት", "ናዝሬት", "ገሐድ",
                                     "ዘመነ ጥምቀት", "ዘመነ ነነዌ", "ዘመነ ጾም",
                                     "ዘመነ ትንሣኤ", "ዘመነ ዕርገት", "ዘመነ ጰራቅሊጦስ",
                                     "ደመና፣ ዘርዕ፣ ዝናም", "መብረቅ፣ ባሕር",
                                     "ዐይነ ኵሉ፣ ዕጕለ ቋዓት", "ጎሕ፣ ነግሕ"]],
    "lent-week": list(zip(GREAT_LENT_WEEK_KEYS, GREAT_LENT_WEEK_NAMES_AM)),
}


def plan_status_label(key):
    return PLAN_STATUS_LABELS.get(key, key or "")


def plan_season_filter_label(category, season_id):
    family = PLAN_FAMILY_LABELS.get(category, str(category))
    if category in PLAN_SEASON_CATALOGS and season_id not in (None, "", "all"):
        names = dict(PLAN_SEASON_CATALOGS[category])
        return f"{family}፦ {names.get(season_id, season_id)}"
    return family


def _html_escape(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def eth_date_label(plugin, d):
    try:
        weekday = WEEKDAYS[plugin.eth_to_gregorian(d["ey"], d["em"], d["ed"]).weekday()]
        return f"{weekday}፣ {plugin.get_month_name(d['em'])} {d['ed']} {d['ey']}"
    except Exception:
        return f"{plugin.get_month_name(d.get('em') or 0)} {d.get('ed', '')} {d.get('ey', '')}"


def _month_group_label(plugin, key):
    ey, em = key
    return f"{plugin.get_month_name(em or 0)} {ey if ey is not None else ''}".strip()


def _group_by_month(items):
    groups = []
    for it in items:
        d = it.get("date") or {}
        key = (d.get("ey"), d.get("em"))
        if groups and groups[-1][0] == key:
            groups[-1][1].append(it)
        else:
            groups.append((key, [it]))
    return groups


def _html_table(caption, headers, rows):
    out = ["<table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse;'>",
           f"<caption>{_html_escape(caption)}</caption>", "<thead><tr>"]
    for h in headers:
        out.append(f"<th scope='col'>{_html_escape(h)}</th>")
    out.append("</tr></thead><tbody>")
    for cells in rows:
        out.append("<tr>")
        for i, c in enumerate(cells):
            if i == 0:
                out.append(f"<th scope='row'>{_html_escape(c)}</th>")
            else:
                out.append(f"<td>{_html_escape(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _html_month_nav(label, prefix, groups, plugin):
    if len(groups) < 2:
        return ""
    links = "".join(
        f"<li><a href='#{prefix}-{n}'>{_html_escape(_month_group_label(plugin, key))} ({len(members)})</a></li>"
        for n, (key, members) in enumerate(groups)
    )
    return f"<nav aria-label='{_html_escape(label)}'><ul>{links}</ul></nav>"


def render_plan_html(plugin, plan, columns=None):
    columns = columns or {}
    shown = [c for c in PLAN_COLUMNS if columns.get(c[0], True)]
    name = plan.get("name") or "Ethiopian Plan"
    rows = plan.get("rows", [])
    period_mode = plan.get("periodMode", "duration")
    period_value = plan.get("periodValue", 1)
    period_unit = plan.get("periodUnit", "day")
    interval_value = plan.get("intervalValue", 1)
    interval_unit = plan.get("intervalUnit", "day")

    parts = ["<main lang='am'>", f"<h1>{_html_escape(name)}</h1>"]

    parts.append("<h2>የዕቅዱ ማጠቃለያ</h2><ul>")
    if period_mode == "date-range":
        end = plan.get("endDate") or {}
        end_label = eth_date_label(plugin, end) if end else "—"
        parts.append(f"<li><strong>የዕቅድ ዓይነት፦</strong> እስከ ተወሰነ ቀን ({_html_escape(end_label)})</li>")
    else:
        unit_label = PLAN_UNIT_LABELS.get(period_unit, period_unit)
        parts.append(f"<li><strong>የዕቅድ ጊዜ፦</strong> {_html_escape(period_value)} {_html_escape(unit_label)}</li>")
    interval_label = PLAN_UNIT_LABELS.get(interval_unit, interval_unit)
    parts.append(f"<li><strong>የድግግሞሽ ክፍተት፦</strong> በየ {_html_escape(interval_value)} {_html_escape(interval_label)}</li>")
    parts.append("<li><strong>የወቅት ማጣሪያ፦</strong> "
                 + _html_escape(plan_season_filter_label(plan.get("seasonCategory", "all"),
                                                         plan.get("seasonId", "all")))
                 + "</li>")
    parts.append(f"<li><strong>የቀናት ብዛት፦</strong> {len(rows)}</li>")
    parts.append("</ul>")

    if not rows:
        parts.append("<p>ምንም ቀን አልተፈጠረም።</p></main>")
        return "".join(parts)

    groups = _group_by_month(rows)
    parts.append("<h2>የዕቅድ ቀናት</h2>")
    parts.append(_html_month_nav("የወራት ማውጫ", "plan-month", groups, plugin))

    head = ["ቀን", "የዕቅድ ነገር", "ዝርዝር", "ሁኔታ"] + [c[2] for c in shown]
    for n, (key, members) in enumerate(groups):
        month_label = _month_group_label(plugin, key)
        parts.append(f"<h3 id='plan-month-{n}'>{_html_escape(month_label)} ({len(members)} ቀናት)</h3>")
        table_rows = []
        for r in members:
            season = r.get("season") or {}
            table_rows.append([
                eth_date_label(plugin, r.get("date") or {}),
                r.get("title", ""),
                r.get("details", ""),
                plan_status_label(r.get("status", "planned")),
            ] + [season.get(c[1], "") for c in shown])
        parts.append(_html_table(f"{month_label} ዕቅድ ቀናት", head, table_rows))

    parts.append("</main>")
    return "".join(parts)


AGENDA_BUCKETS = [
    ("overdue", "ያለፈ ጊዜው"),
    ("today", "ዛሬ"),
    ("upcoming", "መጪ"),
]


def render_agenda_html(plugin, buckets):
    total = sum(len(buckets[k]) for k, _ in AGENDA_BUCKETS)
    events = sum(1 for k, _ in AGENDA_BUCKETS for i in buckets[k] if i.get("type") == "event")
    tasks = total - events
    ey, em, ed = plugin.get_ethiopian_date()

    parts = ["<main lang='am'>", "<h1>አጀንዳ</h1>"]
    parts.append(f"<p><strong>ዛሬ፦</strong> {_html_escape(eth_date_label(plugin, {'ey': ey, 'em': em, 'ed': ed}))}</p>")
    parts.append(f"<p><strong>ጠቅላላ የተመዘገቡ፦</strong> {total} "
                 f"(የግል ክንውኖች {events}፣ የዕቅድ ተግባራት {tasks})</p>")
    parts.append("<nav aria-label='የአጀንዳ ክፍሎች'><ul>"
                 + "".join(f"<li><a href='#agenda-{k}'>{label} ({len(buckets[k])})</a></li>"
                           for k, label in AGENDA_BUCKETS)
                 + "</ul></nav>")

    head = ["ቀን", "ዓይነት", "ነገር", "ዝርዝር", "ሁኔታ", "የአየር ወቅት", "የጾም ወቅት",
            "የቤተክርስቲያን ዘመን", "ዐቢይ ጾም"]
    for k, label in AGENDA_BUCKETS:
        items = buckets[k]
        parts.append(f"<h2 id='agenda-{k}'>{label} ({len(items)})</h2>")
        if not items:
            parts.append("<p>የሚታይ ተግባር የለም።</p>")
            continue
        groups = _group_by_month(items)
        parts.append(_html_month_nav(f"{label} — የወራት ማውጫ", f"agenda-{k}-month", groups, plugin))
        for n, (key, members) in enumerate(groups):
            month_label = _month_group_label(plugin, key)
            if len(groups) > 1:
                parts.append(f"<h3 id='agenda-{k}-month-{n}'>{_html_escape(month_label)} ({len(members)})</h3>")
            rows = [[eth_date_label(plugin, t.get("date") or {}),
                     "ክንውን" if t.get("type") == "event" else (t.get("planName") or "ተግባር"),
                     t.get("title", ""), t.get("details", ""),
                     plan_status_label(t.get("status", "")), t.get("climatic", ""),
                     t.get("fasting", ""), t.get("liturgical", ""),
                     t.get("greatLentWeek", "")] for t in members]
            parts.append(_html_table(f"{label} — {month_label}", head, rows))

    parts.append("</main>")
    return "".join(parts)


def render_day_agenda_html(plugin, ey, em, ed, day):
    date_label = eth_date_label(plugin, {"ey": ey, "em": em, "ed": ed})
    parts = ["<main lang='am'>", f"<h1>{_html_escape(date_label)}</h1>",
             "<nav aria-label='የቀኑ ክፍሎች'><ul>"
             "<li><a href='#day-holidays'>በዓላት</a></li>"
             "<li><a href='#day-synax'>ስንክሳር</a></li>"
             "<li><a href='#day-gitsawe'>ግጻዌ</a></li>"
             "<li><a href='#day-season'>ወቅት</a></li>"
             "<li><a href='#day-events'>የግል ክንውኖች</a></li></ul></nav>"]

    parts.append("<h2 id='day-holidays'>በዓላት</h2>")
    if day["holidays"]:
        parts.append("<ul>" + "".join(f"<li>{_html_escape(h)}</li>" for h in day["holidays"]) + "</ul>")
    else:
        parts.append("<p>በዚህ ቀን ምንም ብሔራዊ ወይም ሃይማኖታዊ በዓል የለም።</p>")

    parts.append("<h2 id='day-synax'>ስንክሳር</h2>")
    if day["synax_annual"] or day["synax_monthly"]:
        if day["synax_annual"]:
            parts.append("<h3>ዓመታዊ በዓላት</h3><ul>"
                         + "".join(f"<li>{_html_escape(e)}</li>" for e in day["synax_annual"]) + "</ul>")
        if day["synax_monthly"]:
            parts.append("<h3>ወርኃዊ በዓላት</h3><ul>"
                         + "".join(f"<li>{_html_escape(e)}</li>" for e in day["synax_monthly"]) + "</ul>")
    else:
        parts.append("<p>ለዚህ ቀን የስንክሳር መረጃ አልተገኘም።</p>")

    parts.append("<h2 id='day-gitsawe'>ግጻዌ</h2>")
    if day["gitsawe"]:
        parts.append("<ul>" + "".join(f"<li>{_html_escape(g)}</li>" for g in day["gitsawe"]) + "</ul>")
    else:
        parts.append("<p>ለዚህ ቀን የግጻዌ መረጃ አልተገኘም።</p>")

    parts.append("<h2 id='day-season'>ወቅት</h2><ul>")
    for label, value in day["season"]:
        parts.append(f"<li>{_html_escape(label)}፦ {_html_escape(value)}</li>")
    parts.append("</ul>")

    parts.append("<h2 id='day-events'>የግል ክንውኖች</h2>")
    if day["events"]:
        parts.append("<ul>" + "".join(
            f"<li><strong>{_html_escape(e.get('title', ''))}</strong>"
            + (f" — {_html_escape(e.get('details'))}" if e.get("details") else "") + "</li>"
            for e in day["events"]) + "</ul>")
    else:
        parts.append("<p>ምንም የግል ክንውን የለም።</p>")

    parts.append("</main>")
    return "".join(parts)


def render_gitsawe_structure_html(structure):
    if not structure or not structure.get("parts"):
        return "<main lang='am'><p>ምንም ውጤት አልተገኘም።</p></main>"

    def page_range(pages):
        if isinstance(pages, list) and len(pages) == 2:
            return f" (ገጽ {_html_escape(pages[0])}–{_html_escape(pages[1])})"
        return ""

    book = structure.get("book") or {}
    parts = ["<main lang='am'>", f"<h1>{_html_escape(book.get('title') or 'የመጽሐፉ ማውጫ')}</h1><ol>"]
    for part in structure["parts"]:
        parts.append(f"<li><strong>{_html_escape(part.get('title') or '')}</strong>")
        if part.get("description"):
            parts.append(f" — {_html_escape(part['description'])}")
        parts.append(page_range(part.get("printed_pages")))
        if isinstance(part.get("seasons"), list):
            parts.append("<ul>")
            for season in part["seasons"]:
                parts.append(f"<li>{_html_escape(season.get('season') or '')}<ul>")
                for m in season.get("months") or []:
                    parts.append(f"<li>{_html_escape(m.get('month') or '')}{page_range(m.get('printed_pages'))}</li>")
                parts.append("</ul></li>")
            parts.append("</ul>")
        elif isinstance(part.get("sections"), list):
            parts.append("<ul>" + "".join(f"<li>{_html_escape(s.get('section') or '')}</li>"
                                          for s in part["sections"]) + "</ul>")
        elif isinstance(part.get("chapters"), list):
            parts.append("<ul>" + "".join(
                f"<li>{_html_escape(c.get('title') or '')}"
                + (f" — {_html_escape(c['sub'])}" if c.get("sub") else "") + "</li>"
                for c in part["chapters"]) + "</ul>")
        parts.append("</li>")
    parts.append("</ol></main>")
    return "".join(parts)


# ============================================================
# SHARED DIALOG HELPERS
# ============================================================
def _add_date_fields(helper, prefix, year_suffix=""):
    year = helper.addLabeledControl(f"{prefix}ዓመት{year_suffix}፦", wx.SpinCtrl, min=1, max=9999)
    month = helper.addLabeledControl(f"{prefix}ወር፦", wx.Choice, choices=MONTHS[1:])
    day = helper.addLabeledControl(f"{prefix}ቀን፦", wx.SpinCtrl, min=1, max=30)
    return year, month, day


def _set_date_fields(year, month, day, ey, em, ed):
    year.SetValue(ey)
    month.SetSelection(em - 1)
    day.SetValue(ed)


def _get_date_fields(year, month, day):
    return {'ey': year.GetValue(), 'em': max(0, month.GetSelection()) + 1, 'ed': day.GetValue()}


def _button_row(parent, specs):
    row = wx.BoxSizer(wx.HORIZONTAL)
    for label, handler in specs:
        b = wx.Button(parent, label=label)
        b.Bind(wx.EVT_BUTTON, handler)
        row.Add(b, 0, wx.ALL, 2)
    return row


class DateChoiceDialog(wx.Dialog):
    def __init__(self, parent, plugin, title, ey, em, ed, with_year=True):
        super().__init__(parent, title=title)
        self.plugin = plugin
        h = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.y = h.addLabeledControl("ዓመት፦", wx.SpinCtrl, min=1, max=9999) if with_year else None
        self.m = h.addLabeledControl("ወር፦", wx.Choice, choices=MONTHS[1:])
        self.d = h.addLabeledControl("ቀን፦", wx.SpinCtrl, min=1, max=30)
        h.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        if self.y is not None:
            self.y.SetValue(ey)
        self.m.SetSelection(em - 1)
        self.d.SetValue(ed)
        self.ey = ey
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.SetSizerAndFit(h.sizer)
        self.CentreOnScreen()
        (self.y or self.m).SetFocus()

    def date(self):
        ey = self.y.GetValue() if self.y is not None else self.ey
        return ey, max(0, self.m.GetSelection()) + 1, self.d.GetValue()

    def on_ok(self, event):
        ey, em, ed = self.date()
        limit = self.plugin.get_month_length(ey, em) if self.y is not None else (6 if em == 13 else 30)
        if ed > limit:
            wx.MessageBox(f"{self.plugin.get_month_name(em)} {limit} ቀናት ብቻ አሉት።",
                          "ስህተት", wx.OK | wx.ICON_ERROR, self)
            self.d.SetFocus()
            return
        event.Skip()


# ============================================================
# PLANNING DIALOG
# ============================================================
class PlanDayDialog(wx.Dialog):
    def __init__(self, parent, plugin, row):
        super().__init__(parent, title="የዕቅድ ቀን አርም")
        h = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        h.addItem(wx.StaticText(self, label=eth_date_label(plugin, row['date'])))
        self.title = h.addLabeledControl("ነገር፦", wx.TextCtrl)
        self.details = h.addLabeledControl("ዝርዝር፦", wx.TextCtrl)
        self.status = h.addLabeledControl("ሁኔታ፦", wx.Choice,
                                          choices=[PLAN_STATUS_LABELS[k] for k in PLAN_STATUS_KEYS])
        key = row.get('status', 'planned')
        self.status.SetSelection(PLAN_STATUS_KEYS.index(key) if key in PLAN_STATUS_KEYS else 0)
        self.title.SetValue(row.get('title', ''))
        self.details.SetValue(row.get('details', ''))
        h.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizerAndFit(h.sizer)
        self.CentreOnScreen()
        self.title.SetFocus()

    def status_key(self):
        return PLAN_STATUS_KEYS[max(0, self.status.GetSelection())]


class PlanningDialog(wx.Dialog):
    def __init__(self, parent, plugin):
        super().__init__(parent, title="የኢትዮጵያ ዕቅድ")
        self.plugin = plugin
        self.action = None
        self.next_edit = 0
        draft = getattr(plugin, "planning_draft", None)
        self.plan = draft
        self.rows = draft.get("rows", []) if draft else []

        helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.name = helper.addLabeledControl("የዕቅድ ስም፦", wx.TextCtrl)
        self.sy, self.sm, self.sd = _add_date_fields(helper, "መጀመሪያ ")
        self.period = helper.addLabeledControl("የዕቅድ ጊዜ ብዛት፦", wx.SpinCtrl, min=1, max=9999, initial=1)
        self.periodUnit = helper.addLabeledControl(
            "የዕቅድ ጊዜ ክፍል፦", wx.Choice,
            choices=["ቀን", "ሳምንት", "ወር", "ዓመት", "የተወሰነ የቀን ክልል"])
        self.periodUnit.SetSelection(2)
        self.ey, self.em, self.ed = _add_date_fields(helper, "መጨረሻ ", " (ለተወሰነ የቀን ክልል ብቻ)")
        self.interval = helper.addLabeledControl("የድግግሞሽ ክፍተት ብዛት፦", wx.SpinCtrl, min=1, max=9999, initial=1)
        self.intervalUnit = helper.addLabeledControl("የድግግሞሽ ክፍተት ክፍል፦", wx.Choice,
                                                     choices=["ቀን", "ሳምንት", "ወር", "ዓመት"])
        self.intervalUnit.SetSelection(0)
        self.seasonFamily = helper.addLabeledControl(
            "የወቅት ቤተሰብ፦", wx.Choice, choices=[PLAN_FAMILY_LABELS[k] for k in PLAN_FAMILY_KEYS])
        self.seasonFamily.SetSelection(0)
        self.season = helper.addLabeledControl("የተመረጠ ወቅት፦", wx.Choice)
        self.fill_seasons()
        saved_columns = getattr(plugin, "planning_columns", None) or {}
        self.columnChecks = {}
        for key, field, label in PLAN_COLUMNS:
            cb = wx.CheckBox(self, label=f"{label} አምድ በሠንጠረዡ ላይ አሳይ")
            cb.SetValue(bool(saved_columns.get(key, True)))
            helper.addItem(cb)
            self.columnChecks[key] = cb

        helper.addItem(_button_row(self, [
            ("ዕቅድ አስላ", self.generate),
            ("አጽዳ", self.clear),
            ("ውጤቱን በመስኮት አሳይ", self.show_page),
            ("ቀን አርም", self.edit_day),
            ("አስቀምጥ", self.save),
            ("የተቀመጠ ዕቅድ ጫን", self.load_saved),
            ("ከፋይል አስገባ", self.import_file),
        ]))
        export_row = _button_row(self, [
            ("ወደ CSV ላክ", lambda e: self.export('csv')),
            ("ወደ TSV ላክ", lambda e: self.export('tsv')),
            ("ወደ JSON ላክ", lambda e: self.export('json')),
            ("ወደ Markdown ላክ", lambda e: self.export('md')),
            ("ወደ HTML ላክ", lambda e: self.export('html')),
            ("ወደ iCal ላክ", self.export_ical),
        ])
        close = wx.Button(self, wx.ID_CANCEL, label="ዝጋ")
        export_row.Add(close, 0, wx.ALL, 2)
        helper.addItem(export_row)
        self.status = wx.StaticText(self, label="")
        helper.addItem(self.status)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(helper.sizer, 1, wx.EXPAND | wx.ALL, guiHelper.BORDER_FOR_DIALOGS)
        self.SetSizerAndFit(outer)
        self.CentreOnScreen()

        ey, em, ed = plugin.get_ethiopian_date()
        _set_date_fields(self.sy, self.sm, self.sd, ey, em, ed)
        _set_date_fields(self.ey, self.em, self.ed, ey, em, ed)
        if draft:
            self.populate(draft)
            self.status.SetLabel(f"የቀድሞ ዕቅድ፦ {len(self.rows)} ቀናት።")
        self.seasonFamily.Bind(wx.EVT_CHOICE, lambda e: self.on_family())
        self.name.SetFocus()

    def say(self, text):
        self.status.SetLabel(text)
        ui.message(text)

    def unit(self, sel):
        return ['day', 'week', 'month', 'year', 'custom'][sel]

    def family(self, sel):
        return PLAN_FAMILY_KEYS[sel]

    def fill_seasons(self):
        self.season.Clear()
        self.season.Append('ሁሉም', 'all')
        for k, label in PLAN_SEASON_CATALOGS.get(self.family(self.seasonFamily.GetSelection()), []):
            self.season.Append(label, k)
        self.season.SetSelection(0)

    def on_family(self):
        self.fill_seasons()
        if self.family(self.seasonFamily.GetSelection()) == 'none':
            for cb in self.columnChecks.values():
                cb.SetValue(False)

    def columns(self):
        return {key: cb.GetValue() for key, cb in self.columnChecks.items()}

    def populate(self, p):
        try:
            self.name.SetValue(p.get('name') or 'Ethiopian Plan')
            st = p.get('start')
            if st:
                _set_date_fields(self.sy, self.sm, self.sd, st['ey'], st['em'], st['ed'])
            self.period.SetValue(int(p.get('periodValue') or 1))
            units = ['day', 'week', 'month', 'year', 'custom']
            unit = p.get('periodUnit') or 'month'
            self.periodUnit.SetSelection(units.index(unit) if unit in units else 2)
            end = p.get('endDate')
            if unit == 'custom' and end:
                _set_date_fields(self.ey, self.em, self.ed, end['ey'], end['em'], end['ed'])
            self.interval.SetValue(int(p.get('intervalValue') or 1))
            iunit = p.get('intervalUnit') or 'day'
            self.intervalUnit.SetSelection(units.index(iunit) if iunit in units[:4] else 0)
            fam = p.get('seasonCategory') or 'all'
            self.seasonFamily.SetSelection(PLAN_FAMILY_KEYS.index(fam) if fam in PLAN_FAMILY_KEYS else 0)
            self.fill_seasons()
            ids = [k for k, _ in PLAN_SEASON_CATALOGS.get(fam, [])]
            sid = p.get('seasonId') or 'all'
            if sid in ids:
                self.season.SetSelection(ids.index(sid) + 1)
        except Exception:
            logHandler.log.error("Plan form restore failed", exc_info=True)

    def clear(self, event=None):
        self.plan = None
        self.rows = []
        self.next_edit = 0
        self.plugin.planning_draft = None
        ey, em, ed = self.plugin.get_ethiopian_date()
        _set_date_fields(self.sy, self.sm, self.sd, ey, em, ed)
        self.seasonFamily.SetSelection(0)
        self.fill_seasons()
        for cb in self.columnChecks.values():
            cb.SetValue(True)
        self.say("ተጠርጓል።")

    def commit(self):
        if self.plan is None:
            return
        self.plan['name'] = self.name.GetValue().strip() or 'Ethiopian Plan'
        self.plan['rows'] = self.rows
        self.plugin.planning_draft = self.plan
        self.plugin.planning_columns = self.columns()

    def generate(self, event=None):
        try:
            unit = self.unit(self.periodUnit.GetSelection())
            fam = self.family(self.seasonFamily.GetSelection())
            sid = self.season.GetClientData(self.season.GetSelection()) or 'all'
            end = _get_date_fields(self.ey, self.em, self.ed) if unit == 'custom' else None
            ui.message("በማስላት ላይ።")
            self.plan = self.plugin.generate_plan(
                self.name.GetValue().strip(), _get_date_fields(self.sy, self.sm, self.sd),
                self.period.GetValue(), unit, self.interval.GetValue(),
                self.unit(self.intervalUnit.GetSelection()), fam, sid, end)
            self.rows = self.plan['rows']
            self.next_edit = 0
            self.commit()
            if self.rows:
                self.say(f"ዕቅድ፦ {len(self.rows)} ቀናት። «ውጤቱን በመስኮት አሳይ» ወይም «ቀን አርም» ይጫኑ።")
            else:
                self.say("ምንም ቀን አልተገኘም። የወቅት ማጣሪያውን ወይም የዕቅድ ጊዜውን ይቀይሩ።")
        except Exception as e:
            self.say(f"ስህተት፦ {e}")

    def edit_day(self, event=None):
        if not self.rows:
            self.say('መጀመሪያ ዕቅድ ያስሉ።')
            return
        choices = []
        for n, r in enumerate(self.rows, 1):
            line = f"{n}. {eth_date_label(self.plugin, r['date'])}"
            if r.get('title'):
                line += f" — {r['title']}"
            choices.append(f"{line} ({plan_status_label(r.get('status', 'planned'))})")
        pick = wx.SingleChoiceDialog(self, 'የሚያርሙትን ቀን ይምረጡ፣', 'ቀን አርም', choices)
        pick.SetSelection(min(self.next_edit, len(choices) - 1))
        if pick.ShowModal() != wx.ID_OK:
            pick.Destroy()
            return
        i = pick.GetSelection()
        pick.Destroy()
        row = self.rows[i]
        dlg = PlanDayDialog(self, self.plugin, row)
        if dlg.ShowModal() == wx.ID_OK:
            row['title'] = dlg.title.GetValue().strip()
            row['details'] = dlg.details.GetValue().strip()
            row['status'] = dlg.status_key()
            self.next_edit = i + 1
            self.commit()
            self.say(f"ተቀምጧል፦ {eth_date_label(self.plugin, row['date'])}")
        dlg.Destroy()

    def save(self, event=None):
        if not self.plan:
            self.say('መጀመሪያ ዕቅድ ያስሉ።')
            return
        self.commit()
        existing = self.plugin._load_plans()
        if any(str(p.get('id')) == str(self.plan.get('id')) for p in existing):
            existing = [self.plan if str(p.get('id')) == str(self.plan.get('id')) else p for p in existing]
        else:
            existing = existing + [self.plan]
        self.plugin._save_plans(existing)
        self.say('ዕቅዱ ተቀምጧል።')

    def load_saved(self, event=None):
        plans = self.plugin._load_plans()
        if not plans:
            self.say('የተቀመጠ ዕቅድ የለም።')
            return
        dlg = wx.SingleChoiceDialog(self, 'የተቀመጠ ዕቅድ ይምረጡ፣', 'ዕቅድ ጫን',
                                     [f"{p.get('name', 'Ethiopian Plan')} ({len(p.get('rows', []))} ቀናት)"
                                      for p in plans])
        if dlg.ShowModal() == wx.ID_OK:
            self.plan = plans[dlg.GetSelection()]
            self.rows = self.plan.get('rows', [])
            self.next_edit = 0
            self.populate(self.plan)
            self.commit()
            self.say(f"{len(self.rows)} ቀናት ተጫነ።")
        dlg.Destroy()

    def import_file(self, event=None):
        dlg = wx.FileDialog(self, 'የዕቅድ ፋይል ምረጥ',
                            wildcard='JSON/CSV/TSV (*.json;*.csv;*.tsv)|*.json;*.csv;*.tsv',
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        path = dlg.GetPath()
        dlg.Destroy()
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                text = f.read()
            ext = Path(path).suffix.lower()[1:]
            self.plan = self.plugin._planning_import_text(text, ext)
            self.rows = self.plan['rows']
            self.next_edit = 0
            self.populate(self.plan)
            self.commit()
            self.say(f"ዕቅዱ ተጫነ። {len(self.rows)} ቀናት።")
        except Exception as e:
            self.say(f'ስህተት፦ {e}')

    def export(self, fmt):
        if not self.plan:
            self.say('መጀመሪያ ዕቅድ ያስሉ።')
            return
        self.commit()
        self.plugin._export_file(self.plugin._planning_export_text(self.plan, fmt),
                                  f"{self.plugin._safe_filename(self.plan['name'])}.{fmt}",
                                  self.plugin._mime(fmt), self)

    def export_ical(self, event=None):
        if not self.plan:
            self.say('መጀመሪያ ዕቅድ ያስሉ።')
            return
        self.commit()
        self.plugin._export_file(self.plugin._build_plan_ical(self.plan),
                                  f"{self.plugin._safe_filename(self.plan['name'])}.ics",
                                  'text/calendar', self)

    def show_page(self, event=None):
        if not self.rows:
            self.say("መጀመሪያ ዕቅድ ያስሉ።")
            return
        self.commit()
        self.action = 'page'
        self.EndModal(wx.ID_OK)


# ============================================================
# AGENDA — launcher + add-event dialog
# ============================================================
class AddAgendaEventDialog(wx.Dialog):
    def __init__(self, parent, plugin, ey, em, ed):
        super().__init__(parent, title="የግል ክንውን ጨምር")
        self.plugin = plugin
        h = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
        self.title = h.addLabeledControl("ስም፦", wx.TextCtrl)
        self.details = h.addLabeledControl("ዝርዝር፦", wx.TextCtrl)
        self.y, self.m, self.d = _add_date_fields(h, "የክንውን ")
        h.addItem(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        _set_date_fields(self.y, self.m, self.d, ey, em, ed)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.SetSizerAndFit(h.sizer)
        self.CentreOnScreen()
        self.title.SetFocus()

    def date(self):
        return _get_date_fields(self.y, self.m, self.d)

    def on_ok(self, event):
        if not self.title.GetValue().strip():
            wx.MessageBox("ስም ማስገባት ያስፈልጋል።", "ስህተት", wx.OK | wx.ICON_ERROR, self)
            self.title.SetFocus()
            return
        d = self.date()
        limit = self.plugin.get_month_length(d['ey'], d['em'])
        if d['ed'] > limit:
            wx.MessageBox(f"{self.plugin.get_month_name(d['em'])} {limit} ቀናት ብቻ አሉት።",
                          "ስህተት", wx.OK | wx.ICON_ERROR, self)
            self.d.SetFocus()
            return
        event.Skip()


class AgendaDialog(wx.Dialog):
    def __init__(self, parent, plugin):
        super().__init__(parent, title="አጀንዳ")
        self.plugin = plugin
        self.action = None
        self.show_done = False
        self.day_date = None
        h = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        h.addItem(wx.StaticText(
            self, label="«አጀንዳ አሳይ» አጀንዳውን በአሳሽ መስኮት ይከፍታል። በርዕስ ለመዘዋወር H፣ ለሠንጠረዥ T ይጠቀሙ።"))

        self.showdone = wx.CheckBox(self, label="የተጠናቀቁና የተዘለሉትን አሳይ")
        self.showdone.SetValue(False)
        h.addItem(self.showdone)

        h.addItem(_button_row(self, [
            ("&አጀንዳ አሳይ", self.show_agenda_page),
            ("&የቀን አጀንዳ", self.show_day_agenda),
            ("የግል ክንውን &ጨምር", self.add_event),
        ]))
        h.addItem(_button_row(self, [
            ("የተግባር &ሁኔታ ቀይር", self.change_status),
            ("አንድ ክንውን አ&ጥፋ", self.delete_event),
            ("ሁሉንም ክንውኖች አጥፋ", self.clear_events),
        ]))

        export_row = _button_row(self, [
            ("ወደ CSV ላክ", lambda e: self.export('csv')),
            ("ወደ TSV ላክ", lambda e: self.export('tsv')),
            ("ወደ JSON ላክ", lambda e: self.export('json')),
            ("ወደ Markdown ላክ", lambda e: self.export('md')),
            ("ወደ HTML ላክ", lambda e: self.export('html')),
            ("ወደ iCal ላክ", self.export_ical),
        ])
        close = wx.Button(self, wx.ID_CANCEL, label="&ዝጋ")
        export_row.Add(close, 0, wx.ALL, 2)
        h.addItem(export_row)

        self.SetSizerAndFit(h.sizer)
        self.CentreOnScreen()

    def show_agenda_page(self, event=None):
        if not self.plugin._agenda_items(self.showdone.GetValue()):
            ui.message("ምንም የአጀንዳ ውሂብ የለም። የግል ክንውን ይጨምሩ ወይም ዕቅድ ያስቀምጡ።")
            return
        self.show_done = self.showdone.GetValue()
        self.action = 'page'
        self.EndModal(wx.ID_OK)

    def show_day_agenda(self, event=None):
        ey, em, ed = self.plugin.get_ethiopian_date()
        dlg = DateChoiceDialog(self, self.plugin, "የቀን አጀንዳ", ey, em, ed)
        if dlg.ShowModal() == wx.ID_OK:
            self.day_date = dlg.date()
            dlg.Destroy()
            self.action = 'day'
            self.EndModal(wx.ID_OK)
            return
        dlg.Destroy()

    def add_event(self, event):
        ey, em, ed = self.plugin.get_ethiopian_date()
        dlg = AddAgendaEventDialog(self, self.plugin, ey, em, ed)
        if dlg.ShowModal() == wx.ID_OK:
            title = dlg.title.GetValue().strip()
            self.plugin.add_agenda_event(dlg.date(), title, dlg.details.GetValue().strip())
            ui.message(f"የግል ክንውን ተመዝግቧል፦ {title}")
        dlg.Destroy()

    def change_status(self, event=None):
        tasks = [i for i in self.plugin._agenda_items(True) if i['type'] == 'task']
        if not tasks:
            ui.message("ምንም የዕቅድ ተግባር የለም።")
            return
        choices = [f"{n}. {eth_date_label(self.plugin, t['date'])} — {t['title'] or 'ያለ ስም'} "
                   f"({t['planName']}) — {plan_status_label(t['status'])}"
                   for n, t in enumerate(tasks, 1)]
        today = self.plugin.ethiopian_to_jdn(*self.plugin.get_ethiopian_date())
        start = next((n for n, t in enumerate(tasks)
                      if t['jdn'] >= today and t['status'] not in ('done', 'skipped')), 0)
        pick = wx.SingleChoiceDialog(self, 'ሁኔታውን የሚቀይሩት ተግባር ይምረጡ፣', 'የተግባር ሁኔታ ቀይር', choices)
        pick.SetSelection(start)
        if pick.ShowModal() != wx.ID_OK:
            pick.Destroy()
            return
        task = tasks[pick.GetSelection()]
        pick.Destroy()
        status = wx.SingleChoiceDialog(self, 'አዲሱን ሁኔታ ይምረጡ፣', 'ሁኔታ',
                                        [PLAN_STATUS_LABELS[k] for k in PLAN_STATUS_KEYS])
        current = task['status'] if task['status'] in PLAN_STATUS_KEYS else 'planned'
        status.SetSelection(PLAN_STATUS_KEYS.index(current))
        if status.ShowModal() == wx.ID_OK:
            key = PLAN_STATUS_KEYS[status.GetSelection()]
            if self.plugin._set_task_status(task['planId'], task['rowId'], key):
                ui.message(f"ሁኔታው ተቀይሯል፦ {plan_status_label(key)}")
            else:
                ui.message("ተግባሩ አልተገኘም።")
        status.Destroy()

    def delete_event(self, event=None):
        events = sorted(self.plugin._load_events(),
                        key=lambda e: self.plugin.ethiopian_to_jdn(**e['date']))
        if not events:
            ui.message("ምንም የግል ክንውን አልተመዘገበም።")
            return
        choices = [f"{eth_date_label(self.plugin, e['date'])} — {e.get('title', '')}" for e in events]
        pick = wx.SingleChoiceDialog(self, 'የሚያጠፉትን ክንውን ይምረጡ፣', 'አንድ ክንውን አጥፋ', choices)
        if pick.ShowModal() != wx.ID_OK:
            pick.Destroy()
            return
        chosen = events[pick.GetSelection()]
        pick.Destroy()
        confirm = wx.MessageDialog(self, f"«{chosen.get('title', '')}» ማጥፋት ይፈልጋሉ?", "አረጋግጥ",
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.plugin._delete_event(chosen.get('id'))
            ui.message("ክንውኑ ጠፍቷል።")
        confirm.Destroy()

    def clear_events(self, event):
        if not self.plugin._load_events():
            ui.message("ምንም የግል ክንውን አልተመዘገበም።")
            return
        dlg = wx.MessageDialog(
            self, "ሁሉንም የግል ክንውኖች ማጥፋት ይፈልጋሉ?", "አረጋግጥ",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )
        if dlg.ShowModal() == wx.ID_YES:
            self.plugin._save_events([])
            ui.message("ሁሉንም የግል ክንውኖች ጠፍተዋል።")
        dlg.Destroy()

    def export(self, fmt):
        items = self.plugin._agenda_items(True)
        if not items:
            ui.message("ምንም የአጀንዳ ውሂብ የለም።")
            return
        self.plugin._export_file(
            self.plugin._agenda_export_text(items, fmt),
            f'agenda.{fmt}', self.plugin._mime(fmt), self
        )

    def export_ical(self, event=None):
        items = self.plugin._agenda_items(self.showdone.GetValue())
        if not items:
            ui.message("ምንም የአጀንዳ ውሂብ የለም።")
            return
        self.plugin._export_file(
            self.plugin._build_agenda_ical(items),
            'agenda.ics', 'text/calendar', self
        )


# ============================================================
# GITSAWE MIXIN (port of gitsawe.js + bible-lookup.js)
# ============================================================
class GitsaweMixin:
    """
    Direct port of the web app's gitsawe.js and bible-lookup.js.
    """

    GITSAWE_MONTH_INDEX_MAP = {
        1: "መስከረም", 2: "ጥቅምት", 3: "ኅዳር", 4: "ታኅሣሥ",
        5: "ጥር", 6: "የካቲት", 7: "መጋቢት", 8: "ሚያዝያ",
        9: "ግንቦት", 10: "ሰኔ", 11: "ሐምሌ", 12: "ነሐሴ", 13: "ጳጉሜን"
    }

    AMHARIC_GEEZ_DIGITS = ["zero", "፩", "፪", "፫", "፬", "፭", "፮", "፯", "፰", "፱", "፲"]

    def number_to_geez(self, n):
        if 1 <= n <= 10:
            return self.AMHARIC_GEEZ_DIGITS[n]
        if 10 < n < 20:
            return "፲" + self.AMHARIC_GEEZ_DIGITS[n % 10]
        if 20 <= n < 30:
            return "፳" if n == 20 else "፳" + self.AMHARIC_GEEZ_DIGITS[n % 10]
        if n >= 30:
            return "፴" if n == 30 else "፴" + self.AMHARIC_GEEZ_DIGITS[n % 10]
        return str(n)

    def _gitsawe_paths(self):
        base = os.path.dirname(__file__)
        return {
            "master":      os.path.join(base, "gitsawe-master.json"),
            "structure":   os.path.join(base, "gitsawe-structure.json"),
            "bible":       os.path.join(base, "80-weahadu.json"),
            "corrections": os.path.join(base, "gitsawe-corrections.json"),
        }

    def load_gitsawe(self):
        if getattr(self, "_gitsawe_master_data", None) is not None:
            return self._gitsawe_master_data, self._gitsawe_structure_data
        paths = self._gitsawe_paths()
        try:
            with open(paths["master"], "r", encoding="utf-8") as f:
                self._gitsawe_master_data = json.load(f)
        except Exception as e:
            logHandler.log.error(f"Gitsawe master load failed: {e}")
            self._gitsawe_master_data = None
        try:
            with open(paths["structure"], "r", encoding="utf-8") as f:
                self._gitsawe_structure_data = json.load(f)
        except Exception as e:
            logHandler.log.error(f"Gitsawe structure load failed: {e}")
            self._gitsawe_structure_data = None
        self._build_gitsawe_index()
        return self._gitsawe_master_data, self._gitsawe_structure_data

    def _build_gitsawe_index(self):
        if getattr(self, "_gitsawe_day_map", None) is not None:
            return
        self._gitsawe_day_map = {}
        master = getattr(self, "_gitsawe_master_data", None)
        if not master:
            return
        parts = master.get("parts") or []
        if not parts:
            return
        part1 = parts[0]
        for season in part1.get("seasons", []) or []:
            for m in season.get("months", []) or []:
                m_idx = m.get("index")
                if m_idx is None:
                    continue
                for idx, d in enumerate(m.get("days", []) or []):
                    day_num = idx + 1
                    self._gitsawe_day_map[f"{m_idx}-{day_num}"] = d

    def get_day_reading(self, month_index, day_index):
        if getattr(self, "_gitsawe_day_map", None) is None:
            self.load_gitsawe()
        key = f"{month_index}-{day_index}"
        if key in self._gitsawe_day_map:
            return self._gitsawe_day_map[key]
        master = getattr(self, "_gitsawe_master_data", None)
        if not master:
            return None
        parts = master.get("parts") or []
        if not parts:
            return None
        for season in (parts[0].get("seasons") or []):
            for m in (season.get("months") or []):
                if m.get("index") == month_index:
                    days = m.get("days") or []
                    if 0 <= day_index - 1 < len(days):
                        return days[day_index - 1]
        return None

    def search_gitsawe(self, query):
        if not query:
            return []
        master = getattr(self, "_gitsawe_master_data", None)
        if master is None:
            self.load_gitsawe()
            master = getattr(self, "_gitsawe_master_data", None)
        if not master or not master.get("parts"):
            return []
        q = str(query).strip().lower()
        if not q:
            return []
        results = []
        part1 = master["parts"][0]
        for season in part1.get("seasons", []) or []:
            for m in season.get("months", []) or []:
                for d_idx, d in enumerate(m.get("days", []) or []):
                    day_num = d_idx + 1
                    matched = False
                    match_text = []

                    if d.get("commemoration") and q in d["commemoration"].lower():
                        matched = True
                        match_text.append(f"ተዝካር: {d['commemoration']}")

                    services = d.get("services") or {}
                    for srv_key in ("ዘነግህ", "ዘቅዳሴ", "ዘሠርክ"):
                        srv = services.get(srv_key)
                        if not srv:
                            continue
                        msb = srv.get("ምስባክ")
                        if msb:
                            book_ch = f"{msb.get('book') or ''} {msb.get('chapter_verse') or ''}".lower()
                            verses_text = " ".join(msb.get("verses") or []).lower()
                            if q in book_ch or q in verses_text:
                                matched = True
                                match_text.append(f"{srv_key} ምስባክ: {msb.get('book') or ''} {msb.get('chapter_verse') or ''}")
                        wng = srv.get("ወንጌል")
                        if wng:
                            book_ch = f"{wng.get('book') or ''} {wng.get('chapter_verse') or ''}".lower()
                            incipit = (wng.get("incipit") or "").lower()
                            if q in book_ch or q in incipit:
                                matched = True
                                match_text.append(f"{srv_key} ወንጌል: {wng.get('book') or ''} {wng.get('chapter_verse') or ''} ({wng.get('incipit') or ''})")
                        for ep in (srv.get("epistles_and_acts") or []):
                            ep_text = f"{ep.get('reading_type') or ''} {ep.get('chapter_verse') or ''} {ep.get('incipit') or ''}".lower()
                            if q in ep_text:
                                matched = True
                                match_text.append(f"{srv_key} ንባብ: {ep.get('reading_type') or ''} {ep.get('chapter_verse') or ''}")

                    if matched:
                        results.append({
                            "month_index": m.get("index"),
                            "month_name": m.get("month"),
                            "day_index": day_num,
                            "day_geez": d.get("day_number") or self.number_to_geez(day_num),
                            "commemoration": d.get("commemoration", ""),
                            "matches": match_text,
                            "reading": d,
                        })
        return results

    @staticmethod
    def _present(value):
        return value is not None and value is not False and value != 0 and value != ""

    def format_reading_sections(self, day_reading, options=None):
        options = options or {}
        blocks = []
        if not day_reading:
            return [{"kind": "empty", "text": "ለዚህ ቀን የትምህርትና የመዝሙር ግጻዌ መረጃ አልተገኘም።"}]

        em = options.get("month", "")
        ed = options.get("day", "")

        if day_reading.get("commemoration"):
            blocks.append({"kind": "commemoration", "text": day_reading["commemoration"]})

        srv = day_reading.get("services") or {}
        ref_counter = 0

        def render_service(title, slot_key, service_data):
            nonlocal ref_counter
            if not self._present(service_data):
                return
            blocks.append({"kind": "service_header", "text": title})

            msb = service_data.get("ምስባክ")
            if self._present(msb):
                ref_id = f"gitsawe-ref-{ref_counter}"
                ref_counter += 1
                blocks.append({
                    "kind": "mesbak_header",
                    "badge": "ምስባክ",
                    "book": msb.get("book") or "መዝሙር",
                    "cv": msb.get("chapter_verse") or "",
                    "psalm_masoretic": msb.get("psalm_masoretic"),
                    "verses": msb.get("verses") or [],
                    "ref_id": ref_id,
                    "book_raw": msb.get("book") or "",
                    "cv_raw": msb.get("chapter_verse") or "",
                    "context": "psalm",
                    "month": em, "day": ed, "slot": slot_key, "role": "mesbak",
                })

            epistles = service_data.get("epistles_and_acts") or []
            if epistles:
                blocks.append({"kind": "epistles_header", "text": "መልእክታትና ግብረ ሐዋርያት"})
                for ep_idx, ep in enumerate(epistles):
                    ref_id = f"gitsawe-ref-{ref_counter}"
                    ref_counter += 1
                    blocks.append({
                        "kind": "epistle",
                        "reading_type": ep.get("reading_type") or "",
                        "cv": ep.get("chapter_verse") or "",
                        "incipit": ep.get("incipit"),
                        "ref_id": ref_id,
                        "book_raw": ep.get("reading_type") or "",
                        "cv_raw": ep.get("chapter_verse") or "",
                        "context": "epistle",
                        "month": em, "day": ed, "slot": slot_key, "role": f"ep{ep_idx}",
                    })

            wng = service_data.get("ወንጌል")
            if self._present(wng):
                ref_id = f"gitsawe-ref-{ref_counter}"
                ref_counter += 1
                blocks.append({
                    "kind": "gospel",
                    "badge": "ወንጌል",
                    "book": wng.get("book") or "",
                    "cv": wng.get("chapter_verse") or "",
                    "incipit": wng.get("incipit"),
                    "ref_id": ref_id,
                    "book_raw": wng.get("book") or "",
                    "cv_raw": wng.get("chapter_verse") or "",
                    "context": "gospel",
                    "month": em, "day": ed, "slot": slot_key, "role": "gospel",
                })

            kidassie = service_data.get("ቅዳሴ")
            if kidassie:
                blocks.append({"kind": "anaphora", "badge": "ቅዳሴ", "text": kidassie})

        if self._present(srv.get("ዘነግህ")):
            render_service("ዘነግህ (Morning Reading)", "ዘነግህ", srv["ዘነግህ"])
        if self._present(srv.get("ዘቅዳሴ")):
            render_service("ዘቅዳሴ (Eucharistic Liturgy Readings)", "ዘቅዳሴ", srv["ዘቅዳሴ"])
        if self._present(srv.get("ዘሠርክ")):
            render_service("ዘሠርክ (Evening Reading)", "ዘሠርክ", srv["ዘሠርክ"])

        return blocks

    def format_gitsawe_plain(self, em, ed, day_reading):
        blocks = self.format_reading_sections(day_reading, {"month": em, "day": ed})
        lines = []
        for blk in blocks:
            k = blk.get("kind")
            if k == "commemoration":
                lines.append(f"  መታሰቢያ: {blk['text']}")
            elif k == "service_header":
                lines.append(f"  {blk['text']}")
            elif k == "mesbak_header":
                lines.append(f"    ምስባክ: {blk['book']} {blk['cv']}")
            elif k == "epistles_header":
                lines.append(f"    {blk['text']}")
            elif k == "epistle":
                lines.append(f"      {blk['reading_type']}: {blk['cv']}")
            elif k == "gospel":
                lines.append(f"    ወንጌል: {blk['book']} {blk['cv']}")
            elif k == "anaphora":
                lines.append(f"    ቅዳሴ: {blk['text']}")
            elif k == "empty":
                lines.append(f"  {blk['text']}")
        return lines

    # ==========================================================
    # BIBLE LOOKUP
    # ==========================================================
    GEEZ_VALUES = {
        "፩": 1, "፪": 2, "፫": 3, "፬": 4, "፭": 5, "፮": 6, "፯": 7, "፰": 8, "፱": 9,
        "፲": 10, "፳": 20, "፴": 30, "፵": 40, "፶": 50, "፷": 60, "፸": 70, "፹": 80, "፺": 90,
        "፻": 100, "፼": 10000,
    }

    def geez_to_number(self, s):
        if not s:
            return None
        total = 0
        current = 0
        for ch in s:
            v = self.GEEZ_VALUES.get(ch)
            if v is None:
                continue
            if v >= 100:
                if current == 0:
                    current = 1
                current *= v
                total += current
                current = 0
            else:
                current += v
        total += current
        return total if total > 0 else None

    _GEEZ_RUN = "[\u1369-\u137C]+"
    _CV_RE = re.compile(
        "(?:ም[^\u1369-\u137C]*)?(" + _GEEZ_RUN + ")[^\u1369-\u137Cቍ]*ቍ[^\u1369-\u137Cፍ]*(" + _GEEZ_RUN + ")"
        "(?:[\\s\\-\u2013\u2014\u2212.\u2027]*(" + _GEEZ_RUN + "|ፍ\\S*))?"
    )

    def parse_chapter_verse(self, s):
        if not s:
            return None
        m = self._CV_RE.search(s)
        if not m:
            return None
        chapter = self.geez_to_number(m.group(1))
        vstart = self.geez_to_number(m.group(2))
        if vstart is None:
            return None
        g3 = m.group(3)
        if not g3:
            vend = vstart
        elif g3.startswith("ፍ"):
            vend = "END"
        else:
            vend = self.geez_to_number(g3)
        return {"chapter": chapter, "vstart": vstart, "vend": vend}

    _JUNK_RE = re.compile("[·፡.,\\-\u2013\u2014\u2027‧\\s]+")
    _GEEZ_ORD = {"፩": 1, "፪": 2, "፫": 3}

    _ROOT_TABLE = [
        (["መዝ", "መዝሙር"], 28),
        (["ማቴ"], 55),
        (["ማር"], 56),
        (["ሉቃ"], 57),
        (["ሮሜ"], 60),
        (["ገላ", "ጌላ"], 63),
        (["ኤፌ", "ፌሶን"], 64),
        (["ፊልጵ", "ፈልጽስ"], 65),
        (["ፊልሞ"], 72),
        (["ቆላ", "ቈላ", "ቴላስይስ", "ቄላስይስ"], 66),
        (["ቲቶ"], 71),
        (["ዕብራ", "ዕብ"], 73),
        (["ያዕ"], 79),
        (["ይሁዳ"], 80),
        (["ሐዋ"], 59),
        (["ራእ", "ራዕየ"], 81),
    ]

    _ROOT_TABLE_ORDINAL = {
        "ቆሮ": {1: 61, 2: 62},
        "ተሰ": {1: 67, 2: 68},
        "ተሰሎ": {1: 67, 2: 68},
        "ተሰሎን": {1: 67, 2: 68},
        "ጢሞ": {1: 69, 2: 70},
        "ጴጥ": {1: 74, 2: 75},
        "ጴጥሮ": {1: 74, 2: 75},
        "ጴጥር": {1: 74, 2: 75},
        "ጴጥሮስ": {1: 74, 2: 75},
        "ዮሐ": {"gospel": 58, 1: 76, 2: 77, 3: 78},
        "ዮሐን": {1: 76, 2: 77, 3: 78},
        "ዮሐንስ": {"gospel": 58, 1: 76, 2: 77, 3: 78},
    }

    def _normalize_book_token(self, tok):
        if not tok:
            return {"root": None, "ordinal": None}
        t = self._JUNK_RE.sub(" ", tok).strip()
        parts = [p for p in t.split(" ") if p]
        changed = True
        while changed and parts:
            changed = False
            if parts and parts[0] == "ዓዲ":
                parts = parts[1:]
                changed = True
            if len(parts) > 1 and parts[0] in ("ግብረ", "ግብ") and parts[1] in ("ሐዋ", "ሐዋርያት"):
                parts = ["ሐዋ"] + parts[2:]
                changed = True
            if parts and parts[0] == "ዘቅዳሴ":
                parts = parts[1:]
                changed = True
        if not parts:
            return {"root": None, "ordinal": None}
        ordinal = None
        root_tokens = []
        for p in parts:
            if p in self._GEEZ_ORD:
                ordinal = self._GEEZ_ORD[p]
            elif p in ("1", "2", "3"):
                ordinal = int(p)
            else:
                root_tokens.append(p)
        root = root_tokens[0] if root_tokens else None
        if root and root.startswith("ዘ") and len(root) > 3:
            root = root[1:]
        return {"root": root, "ordinal": ordinal}

    def resolve_book(self, tok, context=None):
        norm = self._normalize_book_token(tok)
        root = norm["root"]
        ordinal = norm["ordinal"]
        if not root:
            return None
        for roots, bn in self._ROOT_TABLE:
            for r in roots:
                if root.startswith(r) or r.startswith(root):
                    return bn
        for r, table in self._ROOT_TABLE_ORDINAL.items():
            if root.startswith(r) or r.startswith(root):
                if ordinal is not None and ordinal in table:
                    return table[ordinal]
                if context == "gospel" and "gospel" in table:
                    return table["gospel"]
                return None
        return None

    def load_bible(self):
        if getattr(self, "_bible_data", None) is not None:
            return self._bible_data
        path = self._gitsawe_paths()["bible"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._bible_data = json.load(f)
            self._bible_by_number = {b["book_number"]: b for b in self._bible_data}
        except Exception as e:
            logHandler.log.error(f"Bible load failed: {e}")
            self._bible_data = []
            self._bible_by_number = {}
        return self._bible_data

    def load_corrections(self):
        if getattr(self, "_gitsawe_corrections", None) is not None:
            return self._gitsawe_corrections
        path = self._gitsawe_paths()["corrections"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._gitsawe_corrections = json.load(f)
        except Exception:
            self._gitsawe_corrections = {}
        return self._gitsawe_corrections

    def get_verses(self, book_number, chapter, vstart, vend):
        if getattr(self, "_bible_by_number", None) is None:
            self.load_bible()
        book = self._bible_by_number.get(book_number)
        if not book or not chapter:
            return None
        chapter_obj = None
        for c in book.get("chapters", []):
            if c.get("chapter") == chapter:
                chapter_obj = c
                break
        if not chapter_obj:
            return None
        all_verses = []
        for sec in chapter_obj.get("sections", []) or []:
            for v in sec.get("verses", []) or []:
                all_verses.append(v)
        if vend == "END":
            end = float("inf")
        else:
            end = vend if vend is not None else vstart
        matched = [v for v in all_verses if vstart <= v.get("verse", 0) <= end]
        if not matched:
            return None
        return {
            "book_name_am": book.get("book_name_am"),
            "book_short_name_am": book.get("book_short_name_am"),
            "chapter": chapter,
            "verses": matched,
        }

    def resolve_and_fetch(self, book_token, chapter_verse_str, context=None, ref=None):
        cv = self.parse_chapter_verse(chapter_verse_str)
        master_bn = self.resolve_book(book_token, context)
        master_ok = bool(cv and cv.get("chapter") and master_bn)

        if ref:
            self.load_corrections()
            key = f"{ref.get('month')}-{ref.get('day')}-{ref.get('slot')}-{ref.get('role')}"
            c = (self._gitsawe_corrections or {}).get(key)
            if c and (not master_ok or (master_bn == c.get("bn") and cv.get("chapter") == c.get("sc"))):
                vend = c.get("ev") if c.get("sc") == c.get("ec") else "END"
                result = self.get_verses(c["bn"], c["sc"], c["sv"], vend)
                if result:
                    result["corrected"] = True
                    return result

        if not master_ok:
            return None
        return self.get_verses(master_bn, cv["chapter"], cv["vstart"], cv["vend"])


# ============================================================
# PLANNING / AGENDA MIXIN
# ============================================================
class PlanningAgendaMixin:
    def _planning_paths(self):
        return (os.path.join(config.getUserDefaultConfigPath(), 'ethiopian_calendar_plans.json'),
                os.path.join(config.getUserDefaultConfigPath(), 'ethiopian_calendar_agenda_events.json'))

    def _load_plans(self):
        try:
            p, _ = self._planning_paths()
            with open(p, 'r', encoding='utf-8') as f:
                v = json.load(f)
            return v if isinstance(v, list) else []
        except Exception:
            return []

    def _save_plans(self, plans):
        try:
            p, _ = self._planning_paths()
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(plans, f, ensure_ascii=False, indent=2)
        except Exception:
            logHandler.log.error('Planning save failed', exc_info=True)

    def _load_events(self):
        try:
            _, p = self._planning_paths()
            with open(p, 'r', encoding='utf-8') as f:
                v = json.load(f)
            return v if isinstance(v, list) else []
        except Exception:
            return []

    def _save_events(self, events):
        try:
            _, p = self._planning_paths()
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
        except Exception:
            logHandler.log.error('Agenda save failed', exc_info=True)

    def _delete_event(self, event_id):
        self._save_events([e for e in self._load_events() if str(e.get('id')) != str(event_id)])

    def _set_task_status(self, plan_id, row_id, status):
        plans = self._load_plans()
        found = False
        for p in plans:
            if str(p.get('id')) != str(plan_id):
                continue
            for r in p.get('rows', []):
                if str(r.get('id')) == str(row_id):
                    r['status'] = status
                    found = True
        if not found:
            return False
        self._save_plans(plans)
        draft = getattr(self, 'planning_draft', None)
        if draft and str(draft.get('id')) == str(plan_id):
            for r in draft.get('rows', []):
                if str(r.get('id')) == str(row_id):
                    r['status'] = status
        return True

    def _planning_add_months(self, d, n):
        total = d['ey'] * 13 + (d['em'] - 1) + n
        ey = total // 13
        em = total % 13 + 1
        return {'ey': ey, 'em': em, 'ed': min(d['ed'], self.get_month_length(ey, em))}

    def _planning_add_years(self, d, n):
        ey = d['ey'] + n
        return {'ey': ey, 'em': d['em'], 'ed': min(d['ed'], self.get_month_length(ey, d['em']))}

    def _planning_add_unit(self, d, n, u):
        if u in ('day', 'week'):
            days = n if u == 'day' else n * 7
            y, m, day = self.jdn_to_ethiopian(self.ethiopian_to_jdn(**d) + days)
            return {'ey': y, 'em': m, 'ed': day}
        if u == 'month':
            return self._planning_add_months(d, n)
        if u == 'year':
            return self._planning_add_years(d, n)
        raise ValueError('Unsupported interval unit.')

    def _season_matches(self, info, family, season_id):
        if family in (None, '', 'all', 'none') or season_id in (None, '', 'all'):
            return True
        label = dict(PLAN_SEASON_CATALOGS.get(family, [])).get(season_id)
        if label is None:
            return False
        if family == 'climatic':
            return info['climatic'] == label
        if family == 'fasting':
            return info['fasting'] == label if season_id == 'none' else label in info['fasting']
        if family == 'liturgical':
            return info['liturgical'] == label
        if family == 'lent-week':
            return info['greatLentWeek'] == label
        return False

    def generate_plan(self, name, start, period_value, period_unit, interval_value, interval_unit,
                      family='all', season_id='all', end=None):
        if start['ed'] > self.get_month_length(start['ey'], start['em']):
            raise ValueError('የመጀመሪያ ቀን ልክ አይደለም።')
        if period_unit == 'custom':
            if not end or end['ed'] > self.get_month_length(end['ey'], end['em']):
                raise ValueError('የመጨረሻ ቀን ልክ አይደለም።')
            end_j = self.ethiopian_to_jdn(**end) + 1
            if end_j <= self.ethiopian_to_jdn(**start):
                raise ValueError('የመጨረሻ ቀን ከመጀመሪያ ቀን በፊት ነው።')
        else:
            end_j = self.ethiopian_to_jdn(**self._planning_add_unit(start, period_value, period_unit))
        rows = []
        cur = dict(start)
        guard = 0
        while self.ethiopian_to_jdn(**cur) < end_j and guard < 5000:
            info = self._season_info(cur)
            if self._season_matches(info, family, season_id):
                rows.append({'id': f"{cur['ey']}-{cur['em']}-{cur['ed']}", 'date': dict(cur),
                             'season': info, 'title': '', 'details': '', 'status': 'planned'})
            nxt = self._planning_add_unit(cur, interval_value, interval_unit)
            if self.ethiopian_to_jdn(**nxt) <= self.ethiopian_to_jdn(**cur):
                raise ValueError('የክፍሉ ጊዜ ዕቅዱን አያራምድም።')
            cur = nxt
            guard += 1
        if guard >= 5000:
            raise ValueError('ዕቅዱ በጣም ትልቅ ነው።')
        plan = {'id': datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
                'name': (name or '').strip() or 'Ethiopian Plan', 'start': dict(start),
                'periodMode': 'date-range' if period_unit == 'custom' else 'duration',
                'periodValue': period_value, 'periodUnit': period_unit,
                'intervalValue': interval_value, 'intervalUnit': interval_unit,
                'seasonCategory': 'all' if family == 'none' else family,
                'seasonId': 'all' if family == 'none' else season_id, 'rows': rows}
        if period_unit == 'custom':
            plan['endDate'] = dict(end)
        return plan

    def add_agenda_event(self, date, title, details=''):
        title = (title or '').strip()
        if not title:
            raise ValueError('ስም ማስገባት ያስፈልጋል።')
        if not (1 <= date['em'] <= 13) or not (1 <= date['ed'] <= self.get_month_length(date['ey'], date['em'])):
            raise ValueError('የተሳሳተ ቀን።')
        events = self._load_events()
        event = {'id': datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'), 'date': dict(date),
                 'title': title, 'details': (details or '').strip()}
        events.append(event)
        self._save_events(events)
        return event

    def _season_info(self, d):
        meta = self.calculate_bahre_hasab(d['ey'])
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
        wk = self.get_great_lent_week(self.ethiopian_day_of_year(d['em'], d['ed']), feasts)
        return {
            'climatic': self.get_climatic_season(d['em'], d['ed']),
            'fasting': self.get_fasting_season(d['ey'], d['em'], d['ed'], meta, feasts),
            'liturgical': self.get_liturgical_season(d['ey'], d['em'], d['ed'], meta, feasts),
            'greatLentWeek': self.get_great_lent_week_name(wk) if wk else ''
        }

    @staticmethod
    def _date_label(d):
        return f"{d['ey']}-{d['em']:02d}-{d['ed']:02d}"

    @staticmethod
    def _csv_field(value, specials):
        s = '' if value is None else str(value)
        if any(c in s for c in specials):
            return '"' + s.replace('"', '""') + '"'
        return s

    @staticmethod
    def _tsv_field(value):
        s = '' if value is None else str(value)
        return s.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')

    @staticmethod
    def _md_field(value):
        return ('' if value is None else str(value)).replace('|', '\\|')

    @staticmethod
    def _html_field(value):
        s = '' if value is None else str(value)
        return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                .replace('"', '&quot;').replace("'", '&#39;'))

    def _planning_export_text(self, p, fmt):
        rows = p.get('rows', [])
        label = self._date_label
        season = lambda r, k: (r.get('season') or {}).get(k, '')
        head = ['Ethiopian Date', 'Climatic Season', 'Fasting Season', 'Liturgical Season',
                'Great Lent Week', 'Title', 'Details', 'Status']
        cells = [[label(r['date']), season(r, 'climatic'), season(r, 'fasting'), season(r, 'liturgical'),
                  season(r, 'greatLentWeek'), r.get('title'), r.get('details'), r.get('status')] for r in rows]
        meta_head = ['Planning Mode', 'Planning Start', 'Planning End', 'Planning Period',
                     'Planning Interval', 'Season Filter']
        meta = [p.get('periodMode') or 'duration', label(p['start']),
                label(p['endDate']) if p.get('endDate') else '',
                f"{p.get('periodValue')} {p.get('periodUnit')}",
                f"{p.get('intervalValue')} {p.get('intervalUnit')}", p.get('seasonId') or 'all']
        name = p.get('name') or 'Ethiopian Plan'
        season_header = (f"Season Filter: {p.get('seasonId')}"
                         if p.get('seasonCategory') and p.get('seasonCategory') != 'all' else 'Season Filter: All')
        if p.get('periodMode') == 'date-range':
            period_header = f"Planning Range: {label(p['start'])} through {label(p['endDate'])}"
        else:
            period_header = f"Planning Period: {p.get('periodValue')} {p.get('periodUnit')}(s)"

        if fmt == 'json':
            return json.dumps(p, ensure_ascii=False, indent=2)
        if fmt == 'csv':
            esc = lambda v: self._csv_field(v, ',"\n\r')
            return '\n'.join([','.join(meta_head), ','.join(esc(v) for v in meta), '', ','.join(head)]
                             + [','.join(esc(v) for v in row) for row in cells])
        if fmt == 'tsv':
            return '\n'.join(['\t'.join(meta_head), '\t'.join(self._tsv_field(v) for v in meta), '',
                              '\t'.join(head)]
                             + ['\t'.join(self._tsv_field(v) for v in row) for row in cells])
        if fmt == 'md':
            return '\n'.join([f"# {name}", period_header, season_header, '',
                              '| ' + ' | '.join(head) + ' |', '|' + '|'.join(['---'] * len(head)) + '|']
                             + ['| ' + ' | '.join(self._md_field(v) for v in row) + ' |' for row in cells])
        if fmt == 'html':
            esc = self._html_field
            return ('<!doctype html><html lang="am"><head><meta charset="utf-8"><title>' + esc(name) + '</title>'
                    '<style>body{font-family:system-ui,sans-serif}table{border-collapse:collapse;width:100%}'
                    'th,td{border:1px solid #999;padding:.5rem;text-align:left;vertical-align:top}</style></head>'
                    '<body><main><h1>' + esc(name) + '</h1><p>' + esc(period_header) + '</p><p>'
                    + esc(season_header) + '</p><table><caption>' + esc(name) + '</caption><thead><tr>'
                    + ''.join('<th scope="col" lang="en">' + esc(x) + '</th>' for x in head)
                    + '</tr></thead><tbody>'
                    + ''.join('<tr>' + ''.join(('<th scope="row">' if i == 0 else '<td>') + esc(x)
                                               + ('</th>' if i == 0 else '</td>') for i, x in enumerate(row)) + '</tr>'
                              for row in cells)
                    + '</tbody></table></main></body></html>')
        raise ValueError(f'Unsupported export format: {fmt}')

    @staticmethod
    def _parse_delimited(text, delimiter):
        rows, row, field, quoted = [], [], '', False
        i, n = 0, len(text)
        while i < n:
            c = text[i]
            nxt = text[i + 1] if i + 1 < n else None
            if quoted:
                if c == '"' and nxt == '"':
                    field += '"'
                    i += 1
                elif c == '"':
                    quoted = False
                else:
                    field += c
            elif c == '"':
                quoted = True
            elif c == delimiter:
                row.append(field)
                field = ''
            elif c == '\n':
                row.append(field)
                rows.append(row)
                row, field = [], ''
            elif c != '\r':
                field += c
            i += 1
        if field != '' or row:
            row.append(field)
            rows.append(row)
        return rows

    def _planning_import_text(self, text, fmt):
        stamp = 'imported-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        if fmt == 'json':
            p = json.loads(text)
            if not isinstance(p, dict) or not p.get('start') or not isinstance(p.get('rows'), list):
                raise ValueError('Invalid planning JSON.')
            p['start'] = self._parse_planning_date(self._date_label(p['start']))
            if p.get('endDate'):
                p['endDate'] = self._parse_planning_date(self._date_label(p['endDate']))
            rows = []
            for r in p['rows']:
                row = dict(r)
                row['date'] = self._parse_planning_date(self._date_label(r['date']))
                row['title'] = str(r.get('title') or '')
                row['details'] = str(r.get('details') or '')
                row['status'] = r.get('status') or 'planned'
                rows.append(row)
            p['rows'] = rows
            p['id'] = stamp
            return p
        rows = self._parse_delimited(text, '\t' if fmt == 'tsv' else ',')
        header = next((i for i, r in enumerate(rows) if any(str(x).strip() == 'Ethiopian Date' for x in r)), -1)
        if header < 0 or len(rows) < header + 2:
            raise ValueError('Missing planning table.')
        h = [str(x).strip() for x in rows[header]]
        idx = lambda name: h.index(name) if name in h else -1
        di = idx('Ethiopian Date')
        if di < 0:
            raise ValueError('Missing Ethiopian Date column.')
        meta = rows[1] if len(rows) > 1 else []
        get = lambda i: meta[i] if 0 <= i < len(meta) else ''
        start = self._parse_planning_date(get(1))
        end = self._parse_planning_date(get(2)) if get(2) else None

        def pair(value):
            parts = str(value or '1 day').split()
            try:
                num = float(parts[0]) if parts else 0
            except ValueError:
                num = 0
            return (int(num) if num == int(num) and num else 1), (parts[1] if len(parts) > 1 else 'day')

        pv, pu = pair(get(3))
        iv, iu = pair(get(4))
        p = {'id': stamp, 'name': 'Imported Ethiopian Plan', 'periodMode': get(0) or 'duration',
             'start': start, 'periodValue': pv, 'periodUnit': pu, 'intervalValue': iv, 'intervalUnit': iu,
             'seasonCategory': 'all', 'seasonId': get(5) or 'all', 'rows': []}
        if end:
            p['endDate'] = end
            p['periodUnit'] = 'custom'
            p['endExclusive'] = self._planning_end_exclusive(end)

        def cell(r, name):
            i = idx(name)
            return (r[i] if 0 <= i < len(r) else '') or ''

        for r in rows[header + 1:]:
            if di >= len(r) or not r[di]:
                continue
            d = self._parse_planning_date(r[di])
            p['rows'].append({
                'id': f"{d['ey']}-{d['em']}-{d['ed']}", 'date': d,
                'season': {'climatic': cell(r, 'Climatic Season'), 'fasting': cell(r, 'Fasting Season'),
                           'liturgical': cell(r, 'Liturgical Season'),
                           'greatLentWeek': cell(r, 'Great Lent Week')},
                'title': cell(r, 'Title'), 'details': cell(r, 'Details'),
                'status': cell(r, 'Status') or 'planned'})
        if not p['rows']:
            raise ValueError('No planning rows found.')
        return p

    def _planning_end_exclusive(self, end):
        y, m, d = self.jdn_to_ethiopian(self.ethiopian_to_jdn(end['ey'], end['em'], end['ed']) + 1)
        return {'ey': y, 'em': m, 'ed': d}

    def _parse_planning_date(self, s):
        import re as _re
        m = _re.match(r'^(\d+)-(\d{1,2})-(\d{1,2})$', str(s or '').strip())
        if not m:
            raise ValueError('Invalid Ethiopian date.')
        d = {'ey': int(m.group(1)), 'em': int(m.group(2)), 'ed': int(m.group(3))}
        if d['em'] < 1 or d['em'] > 13 or d['ed'] < 1 or d['ed'] > self.get_month_length(d['ey'], d['em']):
            raise ValueError('Invalid Ethiopian date.')
        return d

    def _safe_filename(self, s):
        return ''.join(c if c.isalnum() or c in '_-' else '_' for c in str(s)) or 'export'

    def _mime(self, fmt):
        return {'json': 'application/json', 'csv': 'text/csv', 'tsv': 'text/tab-separated-values',
                'md': 'text/markdown', 'html': 'text/html'}.get(fmt, 'text/plain')

    def _export_file(self, text, default, mime, parent=None):
        dlg = wx.FileDialog(parent or gui.mainFrame, 'ፋይል ያስቀምጡ', defaultFile=default,
                            wildcard='All files|*.*', style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                with open(dlg.GetPath(), 'w', encoding='utf-8-sig', newline='') as f:
                    f.write(text)
                ui.message(f"{default} ተቀምጧል።")
            except Exception as e:
                ui.message(f'ስህተት፦ {e}')
        dlg.Destroy()

    def _ics_escape(self, s):
        return str(s or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n').replace('\r', '')

    def _ics_date(self, g):
        return g.strftime('%Y%m%d')

    def _ics_fold(self, line):
        out, cur, size = [], '', 0
        for ch in line:
            n = len(ch.encode('utf-8'))
            limit = 75 if not out else 74
            if size + n > limit:
                out.append(cur)
                cur, size = ch, n
            else:
                cur += ch
                size += n
        out.append(cur)
        return '\r\n '.join(out)

    def _vevent(self, uid, summary, start_g, end_g, description=''):
        now = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        lines = ['BEGIN:VEVENT', f'UID:{uid}', f'DTSTAMP:{now}',
                 f'DTSTART;VALUE=DATE:{self._ics_date(start_g)}',
                 f'DTEND;VALUE=DATE:{self._ics_date(end_g)}',
                 f'SUMMARY:{self._ics_escape(summary)}']
        if description:
            lines.append(f'DESCRIPTION:{self._ics_escape(description)}')
        lines.append('END:VEVENT')
        return lines

    def _calendar(self, vevents, name):
        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Ethiopian Calendar and Bahire Hasab//EN',
                 'CALSCALE:GREGORIAN', f'X-WR-CALNAME:{self._ics_escape(name)}']
        for ev in vevents:
            lines += ev
        lines.append('END:VCALENDAR')
        return '\r\n'.join(self._ics_fold(l) for l in lines) + '\r\n'

    def _short_date_label(self, d):
        try:
            weekday = WEEKDAYS[self.eth_to_gregorian(d['ey'], d['em'], d['ed']).weekday()]
            return f"{weekday}፣ {self.get_month_name(d['em'])} {d['ed']}"
        except Exception:
            return f"{self.get_month_name(d['em'])} {d['ed']}"

    def _season_description(self, si):
        parts = []
        if si.get('climatic'):
            parts.append(f"የአየር ወቅት፦ {si['climatic']}")
        if si.get('fasting'):
            parts.append(f"የጾም ወቅት፦ {si['fasting']}")
        if si.get('liturgical'):
            parts.append(f"የቤተክርስቲያን ዘመን፦ {si['liturgical']}")
        if si.get('greatLentWeek'):
            parts.append(f"የዐቢይ ጾም ሳምንት፦ {si['greatLentWeek']}")
        return parts

    def _build_plan_ical(self, plan):
        vevents = []
        for r in plan.get('rows', []):
            d = r['date']
            try:
                g = self.eth_to_gregorian(d['ey'], d['em'], d['ed'])
            except Exception:
                continue
            desc = []
            if r.get('details'):
                desc.append(r['details'])
            desc += self._season_description(r.get('season') or self._season_info(d))
            if r.get('status'):
                desc.append('ሁኔታ፦ ' + plan_status_label(r['status']))
            desc.append(self._short_date_label(d))
            uid = f"plan-{plan.get('id') or 'p'}-{r.get('id') or self._date_label(d)}@ethio-calendar"
            summary = r.get('title') or plan.get('name') or 'Planned Event'
            vevents += [self._vevent(uid, summary, g, g + datetime.timedelta(days=1), '\n'.join(desc))]
        return self._calendar(vevents, plan.get('name') or 'የዕቅድ ቀናት')

    def _build_agenda_ical(self, items):
        vevents = []
        for it in items:
            d = it['date']
            try:
                g = self.eth_to_gregorian(d['ey'], d['em'], d['ed'])
            except Exception:
                continue
            is_event = it['type'] == 'event'
            desc = []
            if it.get('details'):
                desc.append(it['details'])
            if it.get('planName'):
                desc.append('የተግባር ዝርዝር፦ ' + it['planName'])
            if it.get('status'):
                desc.append('ሁኔታ፦ ' + plan_status_label(it['status']))
            desc += self._season_description(it)
            desc.append(self._short_date_label(d))
            uid = f"agenda-{'ev' if is_event else 'task'}-{it.get('eventId') or it.get('rowId') or it['jdn']}@ethio-calendar"
            summary = it.get('title') or ('ክንውን' if is_event else 'የተግባር ዝርዝር')
            vevents += [self._vevent(uid, summary, g, g + datetime.timedelta(days=1), '\n'.join(desc))]
        return self._calendar(vevents, 'የተግባር ዝርዝር')

    def _agenda_items(self, show_done=True, by_title=True):
        out = []
        for p in self._load_plans():
            for r in p.get('rows', []):
                if not show_done and r.get('status') in ('done', 'skipped'):
                    continue
                d = r['date']
                si = self._season_info(d)
                out.append({'id': r.get('id'), 'rowId': r.get('id'), 'planId': p.get('id'),
                            'jdn': self.ethiopian_to_jdn(d['ey'], d['em'], d['ed']),
                            'date': d, 'type': 'task',
                            'planName': p.get('name') or 'Ethiopian Plan', 'climatic': si['climatic'],
                            'fasting': si['fasting'], 'liturgical': si['liturgical'],
                            'greatLentWeek': si['greatLentWeek'], 'title': r.get('title', ''),
                            'details': r.get('details', ''), 'status': r.get('status', 'planned')})
        for e in self._load_events():
            d = e.get('date')
            if not d:
                continue
            si = self._season_info(d)
            out.append({'id': e.get('id'), 'eventId': e.get('id'),
                        'jdn': self.ethiopian_to_jdn(d['ey'], d['em'], d['ed']),
                        'date': d, 'type': 'event', 'planName': '',
                        'climatic': si['climatic'], 'fasting': si['fasting'],
                        'liturgical': si['liturgical'], 'greatLentWeek': si['greatLentWeek'],
                        'title': e.get('title', ''), 'details': e.get('details', ''), 'status': ''})
        out.sort(key=lambda x: (x['jdn'], (x.get('planName') or '').casefold(),
                                (x.get('title') or '').casefold() if by_title else ''))
        return out

    def _agenda_buckets(self, show_done=True):
        items = self._agenda_items(show_done, by_title=False)
        ey, em, ed = self.get_ethiopian_date()
        today = self.ethiopian_to_jdn(ey, em, ed)
        return {'overdue': [i for i in items if i['jdn'] < today],
                'today': [i for i in items if i['jdn'] == today],
                'upcoming': [i for i in items if i['jdn'] > today]}

    def show_plan_page(self, plan, columns=None):
        rows = plan.get('rows', [])
        name = plan.get('name') or 'Ethiopian Plan'
        self.show_html(f"{name} — {len(rows)} ቀናት", render_plan_html(self, plan, columns))
        ui.message(f"ዕቅዱ ተከፍቷል። {len(rows)} ቀናት። በርዕስ ለመዘዋወር H፣ ለሠንጠረዥ T ይጠቀሙ።")

    def show_agenda_page(self, show_done=True):
        buckets = self._agenda_buckets(show_done)
        total = sum(len(v) for v in buckets.values())
        if not total:
            ui.message("ምንም የአጀንዳ ውሂብ የለም። የግል ክንውን ይጨምሩ ወይም ዕቅድ ያስቀምጡ።")
            return
        self.show_html(f"አጀንዳ — {total}", render_agenda_html(self, buckets))
        ui.message(f"አጀንዳው {total} ውሂብ ይዟል። በርዕስ ለመዘዋወር H፣ ለሠንጠረዥ T ይጠቀሙ።")

    def _day_agenda_data(self, ey, em, ed):
        target = self.eth_to_gregorian(ey, em, ed)
        holidays = []
        table = self.get_fdre_holidays(ey)
        for key, label in (("celebrated", "የተከበረ ብሔራዊ በዓል"), ("memorial", "የመታሰቢያ ቀን"),
                           ("religious", "የሃይማኖት በዓል")):
            for h in table[key]:
                if h["gregorian"] == target:
                    holidays.append(f"{h['name_am']} ({h['name_en']})፣ {label}")
        annual, monthly = self.split_synax_entries(self.get_synaxarium_by_date(em, ed))
        gitsawe = []
        try:
            self.load_gitsawe()
            reading = self.get_day_reading(em, ed)
        except Exception:
            reading = None
        if reading:
            if reading.get("commemoration"):
                gitsawe.append(f"የዕለቱ መታሰቢያ፦ {reading['commemoration']}")
            morning = (reading.get("services") or {}).get("ዘነግህ") or {}
            msb = morning.get("ምስባክ")
            if msb:
                gitsawe.append(f"ምስባክ፦ {(msb.get('book') or '')} {(msb.get('chapter_verse') or '')}".strip())
            wng = morning.get("ወንጌል")
            if wng:
                gitsawe.append(f"ወንጌል፦ {(wng.get('book') or '')} {(wng.get('chapter_verse') or '')}".strip())
        si = self._season_info({"ey": ey, "em": em, "ed": ed})
        season = [("የአየር ወቅት", si["climatic"]), ("የጾም ወቅት", si["fasting"]),
                  ("የቤተክርስቲያን ዘመን", si["liturgical"])]
        if si["greatLentWeek"]:
            season.append(("የዐቢይ ጾም ሳምንት", si["greatLentWeek"]))
        events = [e for e in self._load_events()
                  if (e.get("date") or {}) == {"ey": ey, "em": em, "ed": ed}]
        return {"holidays": holidays, "synax_annual": annual, "synax_monthly": monthly,
                "gitsawe": gitsawe, "season": season, "events": events}

    def show_day_agenda_page(self, ey, em, ed):
        html = render_day_agenda_html(self, ey, em, ed, self._day_agenda_data(ey, em, ed))
        title = eth_date_label(self, {"ey": ey, "em": em, "ed": ed})
        self.show_html(f"የቀን አጀንዳ — {title}", html)
        ui.message(f"የቀን አጀንዳ፦ {title}። በርዕስ ለመዘዋወር H ይጠቀሙ።")

    def _agenda_export_text(self, items, fmt):
        head = ['Date', 'Ethiopian Date', 'Type', 'Plan', 'Climatic Season', 'Fasting Season',
                'Liturgical Season', 'Great Lent Week', 'Title', 'Details', 'Status']
        rows = [[self._date_label(x['date']), f"{x['date']['ey']}-{x['date']['em']}-{x['date']['ed']}",
                 x['type'], x['planName'], x['climatic'], x['fasting'], x['liturgical'],
                 x['greatLentWeek'], x['title'], x['details'], x['status']] for x in items]
        if fmt in ('csv', 'tsv'):
            delimiter = '\t' if fmt == 'tsv' else ','
            esc = lambda v: self._csv_field(v, '",\n\r\t')
            return '\n'.join(delimiter.join(esc(v) for v in row) for row in [head] + rows)
        if fmt == 'json':
            return json.dumps([{'date': f"{x['date']['ey']}-{x['date']['em']}-{x['date']['ed']}",
                                'ethiopianDate': {'ey': x['date']['ey'], 'em': x['date']['em'], 'ed': x['date']['ed']},
                                'type': x['type'], 'plan': x['planName'],
                                'season': {'climatic': x['climatic'], 'fasting': x['fasting'],
                                           'liturgical': x['liturgical'], 'greatLentWeek': x['greatLentWeek']},
                                'title': x['title'], 'details': x['details'], 'status': x['status']}
                               for x in items], ensure_ascii=False, indent=2)
        if fmt == 'md':
            esc = lambda v: ('' if v is None else str(v)).replace('|', '\\|').replace('\n', '<br>')
            return ('# Agenda\n\n| ' + ' | '.join(head) + ' |\n|' + '|'.join(['---'] * len(head)) + '|\n'
                    + '\n'.join('| ' + ' | '.join(esc(v) for v in row) + ' |' for row in rows))
        if fmt == 'html':
            esc = lambda v: ('' if v is None else str(v)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            return ('<!doctype html><html lang="am"><head><meta charset="utf-8"><title>Agenda</title></head>'
                    '<body><main><h1>Agenda</h1><table><caption>Agenda</caption><thead><tr>'
                    + ''.join('<th scope="col" lang="en">' + esc(h) + '</th>' for h in head)
                    + '</tr></thead><tbody>'
                    + ''.join('<tr>' + ''.join(('<th scope="row">' if i == 0 else '<td>') + esc(v)
                                               + ('</th>' if i == 0 else '</td>') for i, v in enumerate(row)) + '</tr>'
                              for row in rows)
                    + '</tbody></table></main></body></html>')
        raise ValueError(f'Unsupported agenda export format: {fmt}')


# ============================================================
# GLOBAL PLUGIN CLASS
# ============================================================
class GlobalPlugin(GitsaweMixin, PlanningAgendaMixin, globalPluginHandler.GlobalPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_path = os.path.join(os.path.dirname(__file__), "synaxarium_feasts.json")
        self.periodic_data_path = os.path.join(config.getUserDefaultConfigPath(), "ethiopian_bh_periodic_data.json")
        self.settings_path = os.path.join(config.getUserDefaultConfigPath(), "ethiopian_bh_settings.json")
        self.synax_data = None
        logHandler.log.info("Ethiopian Calendar add-on initialized")

        settings = self.load_settings()
        self.shortcuts_enabled = settings.get("shortcuts_enabled", True)
        self.shortcut_settings = settings.get("shortcuts", {})

        self.mainMenu = None
        self.addonMenuItem = None
        self.shortcutsMenuItem = None
        self.shortcutSettingsMenuItem = None
        self._menuBuildAttempts = 0
        self._menuBuildCancelled = False
        if not globalVars.appArgs.secure:
            try:
                wx.CallAfter(self._scheduleMainMenuBuild)
            except Exception:
                logHandler.log.error("Ethiopian Calendar: failed to schedule NVDA menu build", exc_info=True)

    def terminate(self, *args, **kwargs):
        self._menuBuildCancelled = True
        try:
            if self.addonMenuParent and self.addonMenuItem:
                self.addonMenuParent.Remove(self.addonMenuItem.Id)
        except Exception:
            pass
        super().terminate(*args, **kwargs)

    # ============================================================
    # SHORTCUT SETTINGS MANAGEMENT
    # ============================================================
    def load_settings(self):
        default = {"shortcuts_enabled": True, "shortcuts": {}}
        try:
            if not os.path.exists(self.settings_path):
                return default
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data.setdefault("shortcuts_enabled", True)
            data.setdefault("shortcuts", {})
            return data
        except Exception:
            return default

    def load_shortcut_settings(self):
        settings = self.load_settings()
        return settings.get("shortcuts", {})

    def save_settings(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "shortcuts_enabled": self.shortcuts_enabled,
                    "shortcuts": self.shortcut_settings
                }, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def is_shortcut_enabled(self, script_id):
        if script_id not in self.shortcut_settings:
            return SHORTCUT_REGISTRY.get(script_id, {}).get("default", True)
        return self.shortcut_settings.get(script_id, True)

    def _addMenuItem(self, menu, label, handler):
        item = menu.Append(wx.ID_ANY, label)
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU,
                                        lambda evt, h=handler: wx.CallAfter(h, None), item)
        return item

    def _onToggleShortcuts(self, evt):
        self.shortcuts_enabled = not self.shortcuts_enabled
        self.save_settings()
        if self.shortcutsMenuItem:
            self.shortcutsMenuItem.Check(self.shortcuts_enabled)
        ui.message(
            "የቁልፍ ሰሌዳ አቋራጭ መንገዶች ነቅተዋል።" if self.shortcuts_enabled
            else "የቁልፍ ሰሌዳ አቋራጭ መንገዶች ጠፍተዋል፤ ከምናሌው ብቻ መጠቀም ይችላሉ።"
        )

    def _onOpenShortcutSettings(self, evt):
        wx.CallAfter(self._showShortcutSettingsDialog)

    def _showShortcutSettingsDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = ShortcutSettingsDialog(gui.mainFrame, self)
            if dlg.ShowModal() == wx.ID_OK:
                new_settings = dlg.get_results()
                self.shortcut_settings = new_settings
                self.save_settings()
                self.shortcuts_enabled = dlg.globalCheckbox.GetValue()
                if self.shortcutsMenuItem:
                    self.shortcutsMenuItem.Check(self.shortcuts_enabled)
                ui.message("የአቋራጭ መንገዶች ቅንብሮች ተቀይረዋል።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    # ============================================================
    # MENU BUILD
    # ============================================================
    def _scheduleMainMenuBuild(self):
        if getattr(self, "_menuBuildCancelled", False):
            return
        self._menuBuildAttempts = 0
        wx.CallLater(250, self._retryMainMenuBuild)

    def _retryMainMenuBuild(self):
        if getattr(self, "_menuBuildCancelled", False):
            return
        try:
            if self._buildMainMenu():
                return
        except Exception:
            logHandler.log.error(
                "Ethiopian Calendar: failed while installing the NVDA menu",
                exc_info=True,
            )
        attempts = getattr(self, "_menuBuildAttempts", 0) + 1
        self._menuBuildAttempts = attempts
        if attempts < 120:
            wx.CallLater(250, self._retryMainMenuBuild)
        else:
            logHandler.log.warning(
                "Ethiopian Calendar: could not locate NVDA's Exit item after "
                "30 seconds; the Ethiopian Calendar menu was not installed."
            )

    def _findExitMenu(self, menu):
        try:
            items = menu.GetMenuItems()
        except Exception:
            return None
        for index, item in enumerate(items):
            try:
                if item.GetId() == wx.ID_EXIT:
                    return menu, index
                label = item.GetItemLabelText().replace("&", "").strip().lower()
                if label in {"exit", "ውጣ"} or label.startswith("exit "):
                    return menu, index
                submenu = item.GetSubMenu()
                if submenu:
                    found = self._findExitMenu(submenu)
                    if found:
                        return found
            except Exception:
                continue
        return None

    def _findExistingAddonMenu(self, menu):
        try:
            for item in menu.GetMenuItems():
                if item.GetItemLabelText().replace("&", "").strip() == "የኢትዮጵያ ካላንደር":
                    return menu, item
                submenu = item.GetSubMenu()
                if submenu:
                    found = self._findExistingAddonMenu(submenu)
                    if found:
                        return found
        except Exception:
            pass
        return None

    def _buildMainMenu(self):
        tray = getattr(gui.mainFrame, "sysTrayIcon", None)
        if tray is None:
            return False
        menu = getattr(tray, "menu", None)
        if menu is None:
            return False
        self.mainMenu = menu

        exit_info = self._findExitMenu(menu)
        if not exit_info:
            return False
        parent_menu, exit_pos = exit_info

        existing = self._findExistingAddonMenu(menu)
        if existing:
            existing_parent, existing_item = existing
            try:
                existing_index = existing_parent.FindItem(existing_item.GetId())
                if existing_parent is parent_menu and existing_index == exit_pos - 1:
                    self.addonMenuItem = existing_item
                    self.addonMenuParent = existing_parent
                    return True
                existing_parent.Remove(existing_item.GetId())
            except Exception:
                pass

        ethMenu = wx.Menu()
        self._addMenuItem(ethMenu, "የዛሬ ሙሉ መረጃ (ባሕረ ሐሳብ)\tCtrl+Shift+E", self.script_fullInfo)
        self._addMenuItem(ethMenu, "የዛሬ ሙሉ መረጃ በመስኮት\tCtrl+Shift+F", self.script_fullDateHtml)
        self._addMenuItem(ethMenu, "ብሔራዊ በዓላት\tCtrl+Shift+A", self.script_fdreHolidays)
        self._addMenuItem(ethMenu, "የዓመቱን በዓላት ወደ iCal ላክ\tCtrl+Alt+H", self.script_holidaysIcal)
        self._addMenuItem(ethMenu, "የኢትዮጵያ ሰዓት\tCtrl+Shift+T", self.script_ethiopianLocalTime)
        self._addMenuItem(ethMenu, "የኬክሮስ ሰዓት\tCtrl+Shift+Q", self.script_kekrosTime)
        self._addMenuItem(ethMenu, "ቀኑን ኮፒ አድርግ\tCtrl+Shift+C", self.script_copyDate)
        self._addMenuItem(ethMenu, "ቀጣይ በዓላትና አጽዋማት\tCtrl+Shift+U", self.script_upcomingEvent)
        self._addMenuItem(ethMenu, "የዘንድሮ ተንቀሳቃሽ በዓላት\tCtrl+Shift+M", self.script_movableFeasts)
        self._addMenuItem(ethMenu, "የዛሬ ዓመታዊ በዓላት\tCtrl+Shift+S", self.script_readSynaxarium)
        self._addMenuItem(ethMenu, "የዛሬ ወርኃዊ በዓላት\tCtrl+Shift+W", self.script_readMonthlyFeasts)
        self._addMenuItem(ethMenu, "በስንክሳር ውስጥ ፈልግ\tCtrl+Shift+K", self.script_searchSynaxarium)
        self._addMenuItem(ethMenu, "ዕቅድ አዘጋጅ\tCtrl+Alt+Y", self.script_planning)
        self._addMenuItem(ethMenu, "አጀንዳ\tCtrl+Alt+A", self.script_agenda)
        self._addMenuItem(ethMenu, "አጀንዳ በመስኮት\tCtrl+Shift+Alt+A", self.script_agendaPage)
        self._addMenuItem(ethMenu, "የቀን አጀንዳ\tCtrl+Alt+D", self.script_dayAgenda)
        self._addMenuItem(ethMenu, "በስንክሳር በቀን ፈልግ\tCtrl+Shift+Alt+S", self.script_synaxariumByDate)
        self._addMenuItem(ethMenu, "የዓመቱ ሙሉ መረጃ\tCtrl+Shift+Y", self.script_yearlyFeasts)
        self._addMenuItem(ethMenu, "የኢትዮጵያ ቀን ፈልግ\tCtrl+Shift+D", self.script_searchDate)
        self._addMenuItem(ethMenu, "የግሪጎሪያን ቀን ቀይር\tCtrl+Shift+G", self.script_searchGregorianDate)

        islMenu = wx.Menu()
        self._addMenuItem(islMenu, "የዛሬ ሂጅሪ መረጃ\tCtrl+Shift+I", self.script_islamicInfo)
        self._addMenuItem(islMenu, "ሙሉ ሂጅሪ መረጃ በመስኮት\tCtrl+Alt+I", self.script_islamicFullHtml)
        self._addMenuItem(islMenu, "ሂጅሪ ቀን ፈልግ\tCtrl+Shift+H", self.script_searchIslamicDate)
        self._addMenuItem(islMenu, "ሂጅሪ ቀን ኮፒ አድርግ\tCtrl+Shift+B", self.script_copyIslamicDate)

        hebMenu = wx.Menu()
        self._addMenuItem(hebMenu, "የዕብራውያን ቀን ፈልግ\tCtrl+Shift+L", self.script_searchHebrewDate)

        perMenu = wx.Menu()
        self._addMenuItem(perMenu, "የወር አበባ ማቀናበሪያ\tCtrl+Alt+P", self.script_periodicSettings)
        self._addMenuItem(perMenu, "የወር አበባ ሁኔታ\tCtrl+Shift+P", self.script_announcePeriodic)
        self._addMenuItem(perMenu, "የወር አበባ መረጃ አጥፋ\tCtrl+Alt+Shift+P", self.script_clearPeriodicData)
        self._addMenuItem(perMenu, "የእርግዝና እና የወሊድ ጊዜ መገመቻ\tCtrl+Alt+N", self.script_calculatePregnancy)
        self._addMenuItem(perMenu, "ዕድሜ ማስያ\tCtrl+Shift+N", self.script_calculateAge)

        gitMenu = wx.Menu()
        self._addMenuItem(gitMenu, "የዛሬ ግጻዌ (የቤተክርስቲያን ንባቦች)\tCtrl+Shift+R", self.script_gitsaweReadings)
        self._addMenuItem(gitMenu, "በግጻዌ ውስጥ ፈልግ\tCtrl+Alt+R", self.script_gitsaweSearch)
        self._addMenuItem(gitMenu, "በግጻዌ በቀን ፈልግ", self.script_gitsaweByDate)
        self._addMenuItem(gitMenu, "የግጻዌ መጽሐፍ ማውጫ\tCtrl+Alt+S", self.script_gitsaweStructure)

        rootMenu = wx.Menu()
        rootMenu.AppendSubMenu(ethMenu, "የኢትዮጵያ ቀን አቆጣጠር")
        rootMenu.AppendSubMenu(gitMenu, "ግጻዌ")
        rootMenu.AppendSubMenu(islMenu, "የእስልምና ቀን አቆጣጠር")
        rootMenu.AppendSubMenu(hebMenu, "የዕብራውያን ቀን አቆጣጠር")
        rootMenu.AppendSubMenu(perMenu, "የወር አበባ፣ እርግዝና እና ዕድሜ")
        rootMenu.AppendSeparator()

        self.shortcutsMenuItem = rootMenu.AppendCheckItem(wx.ID_ANY, "የቁልፍ ሰሌዳ አቋራጭ መንገዶች ንቁ ናቸው")
        self.shortcutsMenuItem.Check(self.shortcuts_enabled)
        tray.Bind(wx.EVT_MENU, self._onToggleShortcuts, self.shortcutsMenuItem)
        self.shortcutSettingsMenuItem = rootMenu.Append(wx.ID_ANY, "የአቋራጭ መንገዶች ቅንብሮች...")
        tray.Bind(wx.EVT_MENU, self._onOpenShortcutSettings, self.shortcutSettingsMenuItem)

        menuItem = wx.MenuItem(parent_menu, wx.ID_ANY, "የኢትዮጵያ ካላንደር", subMenu=rootMenu)
        parent_menu.Insert(exit_pos, menuItem)
        self.addonMenuItem = menuItem
        self.addonMenuParent = parent_menu
        self._menuBuildAttempts = 0
        logHandler.log.info("Ethiopian Calendar: menu installed immediately before NVDA Exit")
        return True

    # ============================================================
    # DATA LOADING
    # ============================================================
    def load_data(self):
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            return {}
        return {}

    def get_synax_data(self):
        if self.synax_data is None:
            self.synax_data = self.load_data()
        return self.synax_data

    def split_synax_entries(self, entries):
        annual = [e for e in entries if not e.startswith(MONTHLY_FEAST_PREFIX)]
        monthly = [e[len(MONTHLY_FEAST_PREFIX):] for e in entries if e.startswith(MONTHLY_FEAST_PREFIX)]
        return annual, monthly

    def find_synaxarium_matches(self, query):
        query = (query or "").strip()
        if not query:
            return []
        synax_data = self.get_synax_data()
        month_index = {name: idx for idx, name in enumerate(MONTHS)}
        results = []
        for month_name, days in synax_data.items():
            for day_str, entries in days.items():
                try:
                    day_num = int(day_str)
                except ValueError:
                    continue
                for entry in entries:
                    if query in entry:
                        results.append((month_name, day_num, entry))
        results.sort(key=lambda r: (month_index.get(r[0], 99), r[1]))
        return results

    def get_synaxarium_by_date(self, em, ed):
        if em < 1 or em > 13:
            return []
        try:
            month_name = MONTHS[em]
            synax_data = self.get_synax_data()
            if month_name in synax_data and str(ed) in synax_data[month_name]:
                return synax_data[month_name][str(ed)]
            return []
        except (IndexError, KeyError):
            return []

    def load_periodic_data(self):
        default = {"periods": [], "cycle_len": 28, "period_len": 5}
        try:
            if not os.path.exists(self.periodic_data_path):
                return default
            with open(self.periodic_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return default

        if "periods" not in data:
            migrated = {"periods": [], "cycle_len": data.get("cycle_len", 28),
                        "period_len": data.get("period_len", 5)}
            if "ey" in data and "em" in data and "ed" in data:
                try:
                    g_date = self.eth_to_gregorian(data["ey"], data["em"], data["ed"])
                    migrated["periods"] = [g_date.isoformat()]
                except Exception:
                    pass
            data = migrated

        data.setdefault("periods", [])
        data.setdefault("cycle_len", 28)
        data.setdefault("period_len", 5)
        return data

    def save_periodic_data(self, data):
        try:
            with open(self.periodic_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def get_month_name(self, em):
        if 1 <= em < len(MONTHS):
            return MONTHS[em]
        return "ያልታወቀ ወር"

    def match_month_name(self, text):
        raw = (text or "").strip()
        if len(raw) < 2:
            return None
        normalized_input_am = normalize_amharic(raw)
        normalized_input_en = raw.lower()

        matches = set()
        for idx in range(1, len(MONTHS)):
            am_candidates = [MONTHS[idx]] + MONTH_NAME_EXTRA_ALIASES.get(idx, [])
            for candidate in am_candidates:
                normalized_candidate = normalize_amharic(candidate)
                if (normalized_candidate == normalized_input_am or
                        normalized_candidate.startswith(normalized_input_am) or
                        normalized_input_am.startswith(normalized_candidate)):
                    matches.add(idx)
                    break

            en_candidates = [ENGLISH_MONTHS[idx]] + ENGLISH_MONTH_EXTRA_ALIASES.get(idx, [])
            for candidate in en_candidates:
                normalized_candidate = candidate.lower()
                if (normalized_candidate == normalized_input_en or
                        normalized_candidate.startswith(normalized_input_en) or
                        normalized_input_en.startswith(normalized_candidate)):
                    matches.add(idx)
                    break

        if len(matches) == 1:
            return matches.pop()
        return None

    def get_zodiac_sign(self, gm, gd):
        signs = [
            (1, 20, "ካፕሪኮርን (Capricorn) ♑", "አኳሪየስ (Aquarius) ♒"),
            (2, 19, "አኳሪየስ (Aquarius) ♒", "ፓይሰስ (Pisces) ♓"),
            (3, 21, "ፓይሰስ (Pisces) ♓", "አሪየስ (Aries) ♈"),
            (4, 20, "አሪየስ (Aries) ♈", "ታውረስ (Taurus) ♉"),
            (5, 21, "ታውረስ (Taurus) ♉", "ጀሚናይ (Gemini) ♊"),
            (6, 21, "ጀሚናይ (Gemini) ♊", "ካንሰር (Cancer) ♋"),
            (7, 23, "ካንሰር (Cancer) ♋", "ሊዮ (Leo) ♌"),
            (8, 23, "ሊዮ (Leo) ♌", "ቨርጎ (Virgo) ♍"),
            (9, 23, "ቨርጎ (Virgo) ♍", "ሊብራ (Libra) ♎"),
            (10, 23, "ሊብራ (Libra) ♎", "ስኮርፒዮ (Scorpio) ♏"),
            (11, 22, "ስኮርፒዮ (Scorpio) ♏", "ሳጂታሪየስ (Sagittarius) ♐"),
            (12, 22, "ሳጂታሪየስ (Sagittarius) ♐", "ካፕሪኮርን (Capricorn) ♑"),
        ]
        month_idx = gm - 1
        cutoff_day = signs[month_idx][1]
        if gd < cutoff_day:
            return signs[month_idx][2]
        return signs[month_idx][3]

    def get_awde_negest_sign(self, gm, gd):
        signs = [
            (1, 20, "ጀዲ (መሬት) — ንስር", "ደለዊ (ነፋስ) — በሬ"),
            (2, 19, "ደለዊ (ነፋስ) — በሬ", "ሑት (ውሃ) — ከይሲ"),
            (3, 21, "ሑት (ውሃ) — ከይሲ", "ሐመል (እሳት) — ድብ"),
            (4, 20, "ሐመል (እሳት) — ድብ", "ሠውር (መሬት) — ዝንጀሮ"),
            (5, 21, "ሠውር (መሬት) — ዝንጀሮ", "ገውዝ (ነፋስ) — ዓጋዘን"),
            (6, 21, "ገውዝ (ነፋስ) — ዓጋዘን", "ሸርጣን (ውሃ) — ቀበሮ"),
            (7, 23, "ሸርጣን (ውሃ) — ቀበሮ", "አሰድ (እሳት) — አንበሳ"),
            (8, 23, "አሰድ (እሳት) — አንበሳ", "ሰንቡላ (መሬት) — ጉጉት"),
            (9, 23, "ሰንቡላ (መሬት) — ጉጉት", "ሚዛን (ነፋስ) — ተኩላ"),
            (10, 23, "ሚዛን (ነፋስ) — ተኩላ", "ዓቅራብ (ውሃ) — ነብር"),
            (11, 22, "ዓቅራብ (ውሃ) — ነብር", "ቀውስ (እሳት) — ጅብ"),
            (12, 22, "ቀውስ (እሳት) — ጅብ", "ጀዲ (መሬት) — ንስር"),
        ]
        month_idx = gm - 1
        cutoff_day = signs[month_idx][1]
        if gd < cutoff_day:
            return signs[month_idx][2]
        return signs[month_idx][3]

    # ============================================================
    # ASTRONOMICAL FEATURES
    # ============================================================
    def get_moon_phase_text(self, age):
        if age == 30 or age < 2:
            return "🌑 አዲስ ጨረቃ (New Moon)"
        if age < 7:
            return "🌒 እየሞላ የሚሄድ (Waxing Crescent)"
        if 7 <= age <= 8:
            return "🌓 ግማሽ ጨረቃ (First Quarter)"
        if age < 14:
            return "🌔 እየሞላ የሚሄድ (Waxing Gibbous)"
        if 14 <= age <= 16:
            return "🌕 ሙሉ ጨረቃ (Full Moon)"
        if age < 22:
            return "🌖 እየጎደለ የሚሄድ (Waning Gibbous)"
        if 22 <= age <= 23:
            return "🌗 የመጨረሻ ሩብ (Last Quarter)"
        return "🌘 እየጎደለ የሚሄድ (Waning Crescent)"

    def get_addis_sun_times(self, g_date):
        start = datetime.date(g_date.year - 1, 12, 31)
        day_of_year = (g_date - start).days
        offset_minutes = 25 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        rise_min = round(15 - offset_minutes)
        set_min = round(15 + offset_minutes)
        rise_hr = 6
        set_hr = 18

        if rise_min >= 60:
            rise_hr += 1
            rise_min -= 60
        if rise_min < 0:
            rise_hr -= 1
            rise_min += 60

        if set_min >= 60:
            set_hr += 1
            set_min -= 60
        if set_min < 0:
            set_hr -= 1
            set_min += 60

        eth_rise_hr = rise_hr - 6
        if eth_rise_hr <= 0:
            eth_rise_hr += 12
        eth_set_hr = set_hr - 18
        if eth_set_hr <= 0:
            eth_set_hr += 12

        return f"{eth_rise_hr:02d}:{rise_min:02d} ጠዋት", f"{eth_set_hr:02d}:{set_min:02d} ማታ"

    # ============================================================
    # ETHIOPIAN CALENDAR CORE
    # ============================================================
    def ethiopian_to_jdn(self, ey, em, ed):
        return 1724221 + (ey - 1) * 365 + (ey // 4) + (em - 1) * 30 + (ed - 1)

    def jdn_to_ethiopian(self, jdn):
        r = jdn - 1724221
        cycles = r // 1461
        remainder = r % 1461
        if remainder < 365:
            year_in_cycle = 0
            day_of_year = remainder
        elif remainder < 730:
            year_in_cycle = 1
            day_of_year = remainder - 365
        elif remainder < 1096:
            year_in_cycle = 2
            day_of_year = remainder - 730
        else:
            year_in_cycle = 3
            day_of_year = remainder - 1096
        ey = cycles * 4 + year_in_cycle + 1
        em = (day_of_year // 30) + 1
        ed = (day_of_year % 30) + 1
        return ey, em, ed

    def get_month_length(self, ey, em):
        if em == 13:
            return 6 if ey % 4 == 3 else 5
        return 30

    def eth_to_gregorian(self, ey, em, ed):
        jdn = self.ethiopian_to_jdn(ey, em, ed)
        return self.jdn_to_gregorian(jdn)

    def gregorian_to_ethiopian(self, g_year, g_month, g_day):
        jdn = self.gregorian_to_jdn(g_year, g_month, g_day)
        return self.jdn_to_ethiopian(jdn)

    # ============================================================
    # JULIAN CALENDAR CORE
    # ============================================================
    def jdn_to_julian(self, jdn):
        b = jdn + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        day = b - d - int(30.6001 * e)
        month = e - 1 if e < 14 else e - 13
        year = c - 4716 if month > 2 else c - 4715
        return year, month, day

    def julian_to_jdn(self, y, m, d):
        if m < 3:
            y -= 1
            m += 12
        return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d - 1524

    def get_ethiopian_date(self):
        now = datetime.datetime.now()
        return self.gregorian_to_ethiopian(now.year, now.month, now.day)

    def get_weekday_name(self):
        now = datetime.datetime.now()
        return WEEKDAYS[now.weekday()]

    def format_eth_label(self, g_date):
        eth_y, eth_m, eth_d = self.gregorian_to_ethiopian(g_date.year, g_date.month, g_date.day)
        return f"{self.get_month_name(eth_m)} {eth_d} ቀን {eth_y} ዓ.ም"

    def format_12h(self, dt, with_seconds=False):
        hour = dt.hour % 12
        if hour == 0:
            hour = 12
        period = "AM" if dt.hour < 12 else "PM"
        if with_seconds:
            return f"{hour:02d}:{dt.minute:02d}:{dt.second:02d} {period}"
        return f"{hour:02d}:{dt.minute:02d} {period}"

    # ============================================================
    # ISLAMIC CALENDAR CORE
    # ============================================================
    def gregorian_to_jdn(self, gy, gm, gd):
        a = (14 - gm) // 12
        y = gy + 4800 - a
        m = gm + 12 * a - 3
        return gd + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045

    def jdn_to_gregorian(self, jdn):
        l = jdn + 68569
        n = (4 * l) // 146097
        l = l - (146097 * n + 3) // 4
        i = (4000 * (l + 1)) // 1461001
        l = l - (1461 * i) // 4 + 31
        j = (80 * l) // 2447
        d = l - (2447 * j) // 80
        l = j // 11
        m = j + 2 - 12 * l
        y = 100 * (n - 49) + i + l
        return datetime.date(int(y), int(m), int(d))

    def jdn_to_islamic(self, jdn):
        l = jdn - ISLAMIC_EPOCH + 10632
        n = (l - 1) // 10631
        l = l - 10631 * n + 354
        j = (((10985 - l) // 5316) * ((50 * l) // 17719)) + ((l // 5670) * ((43 * l) // 15238))
        l = l - (((30 - j) // 15) * ((17719 * j) // 50)) - ((j // 16) * ((15238 * j) // 43)) + 29
        islamic_month = (24 * l) // 709
        islamic_day = l - ((709 * islamic_month) // 24)
        islamic_year = 30 * n + j - 30
        return islamic_year, islamic_month, islamic_day

    def gregorian_to_islamic(self, gy, gm, gd):
        jdn = self.gregorian_to_jdn(gy, gm, gd)
        return self.jdn_to_islamic(jdn)

    def get_islamic_date(self):
        now = datetime.datetime.now()
        return self.gregorian_to_islamic(now.year, now.month, now.day)

    def get_islamic_month_name(self, im):
        if 1 <= im < len(ISLAMIC_MONTHS):
            return ISLAMIC_MONTHS[im]
        return "ያልታወቀ ወር (Unknown month)"

    def is_islamic_leap(self, iy):
        return (11 * iy + 14) % 30 < 11

    def get_islamic_month_length(self, iy, im):
        if im == 12:
            return 30 if self.is_islamic_leap(iy) else 29
        return 30 if im % 2 == 1 else 29

    def islamic_to_jdn(self, iy, im, id_):
        month_days = ((59 * (im - 1)) + 1) // 2
        return int(id_ + month_days + (iy - 1) * 354 + ((3 + 11 * iy) // 30) + ISLAMIC_EPOCH - 1)

    def islamic_to_gregorian(self, iy, im, id_):
        jdn = self.islamic_to_jdn(iy, im, id_)
        return self.jdn_to_gregorian(jdn)

    def get_islamic_weekday(self, iy, im, id_):
        g_date = self.islamic_to_gregorian(iy, im, id_)
        return WEEKDAYS[g_date.weekday()]

    def get_islamic_event(self, iy, im, id_):
        events = []
        if im == 1 and id_ == 10:
            events.append("ዓሹራ (Ashura)")
        if im == 3 and id_ == 12:
            events.append("መውሊድ (Mawlid)")
        if im == 7 and id_ == 27:
            events.append("እስራ ወሚዕራጅ (Isra and Mi'raj)")
        if im == 9:
            if id_ >= 21:
                events.append("የረመዳን መጨረሻዎቹ 10 ቀናት (last 10 days of Ramadan)")
            events.append("ረመዳን (Ramadan)")
        if im == 10 and id_ == 1:
            events.append("ዒድ አልፊጥር (Eid al-Fitr)")
        if im == 12:
            if id_ == 9:
                events.append("የዐረፋ ቀን (Day of Arafah)")
            elif id_ == 10:
                events.append("ዒድ አልአድሐ (Eid al-Adha)")
            if id_ <= 10:
                events.append("የሐጅ ወቅት (Hajj season)")
        return events

    # ============================================================
    # HEBREW CALENDAR CORE
    # ============================================================
    def hebrew_leap(self, year):
        return ((7 * year + 1) % 19) < 7

    def hebrew_delay1(self, year):
        months = (235 * year - 234) // 19
        parts = 12084 + (13753 * months)
        day = (months * 29) + (parts // 25920)
        if (3 * (day + 1)) % 7 < 3:
            day += 1
        return day

    def hebrew_delay2(self, year):
        d1 = self.hebrew_delay1(year)
        d2 = self.hebrew_delay1(year + 1)
        if (d2 - d1) == 356:
            return 2
        if (d2 - d1) == 382:
            return 1
        return 0

    def hebrew_first_of_year(self, year):
        return HEBREW_EPOCH + self.hebrew_delay1(year) + self.hebrew_delay2(year)

    def hebrew_month_length(self, year, month):
        is_leap = self.hebrew_leap(year)
        length = self.hebrew_first_of_year(year + 1) - self.hebrew_first_of_year(year)
        is_complete = length in (355, 385)
        is_deficient = length in (353, 383)

        if month == 1:
            return 30
        if month == 2:
            return 30 if is_complete else 29
        if month == 3:
            return 29 if is_deficient else 30
        if month == 4:
            return 29
        if month == 5:
            return 30
        if month == 6:
            return 30 if is_leap else 29

        m_after = month - 7 if is_leap else month - 6
        if is_leap and month == 7:
            return 29
        if m_after == 1:
            return 30
        if m_after == 2:
            return 29
        if m_after == 3:
            return 30
        if m_after == 4:
            return 29
        if m_after == 5:
            return 30
        if m_after == 6:
            return 29
        return 0

    def hebrew_to_jdn(self, y, m, d):
        jdn = self.hebrew_first_of_year(y)
        for i in range(1, m):
            jdn += self.hebrew_month_length(y, i)
        return jdn + d - 1

    def jdn_to_hebrew(self, jdn):
        y = int((jdn - HEBREW_EPOCH) / 365.2468) + 1
        while jdn >= self.hebrew_first_of_year(y + 1):
            y += 1
        while jdn < self.hebrew_first_of_year(y):
            y -= 1
        day_of_year = jdn - self.hebrew_first_of_year(y) + 1
        m = 1
        while True:
            length = self.hebrew_month_length(y, m)
            if day_of_year <= length:
                break
            day_of_year -= length
            m += 1
        return y, m, day_of_year

    def get_hebrew_month_name(self, hm, is_leap):
        names_leap = ["", "ቲሽሪ (Tishrei)", "ቼሽቫን (Cheshvan)", "ኪስሌቭ (Kislev)", "ቴቤት (Tevet)",
                      "ሼቫት (Shevat)", "አዳር 1 (Adar I)", "አዳር 2 (Adar II)", "ኒሳን (Nisan)",
                      "ኢያር (Iyar)", "ሲቫን (Sivan)", "ታሙዝ (Tammuz)", "አቭ (Av)", "ኤሉል (Elul)"]
        names_reg = ["", "ቲሽሪ (Tishrei)", "ቼሽቫን (Cheshvan)", "ኪስሌቭ (Kislev)", "ቴቤት (Tevet)",
                     "ሼቫት (Shevat)", "አዳር (Adar)", "ኒሳን (Nisan)", "ኢያር (Iyar)", "ሲቫን (Sivan)",
                     "ታሙዝ (Tammuz)", "አቭ (Av)", "ኤሉል (Elul)"]
        return names_leap[hm] if is_leap else names_reg[hm]

    def get_hebrew_event(self, hy, hm, hd, is_leap):
        ev = []
        if hm == 1 and hd == 1:
            ev.append("ሮሽ ሃሻና (Rosh Hashanah)")
        if hm == 1 and hd == 10:
            ev.append("ዮም ኪፑር (Yom Kippur)")
        if hm == 1 and hd == 15:
            ev.append("የዳስ በዓል (Sukkot)")
        if hm == 1 and hd == 22:
            ev.append("ሸሚኒ አጼሬት (Shemini Atzeret)")
        if hm == 3 and hd == 25:
            ev.append("ሃኑካ (Hanukkah)")
        if hm == 5 and hd == 15:
            ev.append("ቱ ቢሽቫት (Tu BiShvat)")
        if is_leap and hm == 6 and hd == 14:
            ev.append("ፉሪም ካታን (Purim Katan)")
        if (not is_leap and hm == 6 and hd == 14) or (is_leap and hm == 7 and hd == 14):
            ev.append("ፉሪም (Purim)")
        if (not is_leap and hm == 7 and hd == 15) or (is_leap and hm == 8 and hd == 15):
            ev.append("ፋሲካ (Passover)")
        if (not is_leap and hm == 8 and hd == 18) or (is_leap and hm == 9 and hd == 18):
            ev.append("ላግ ባኦሜር (Lag BaOmer)")
        if (not is_leap and hm == 9 and hd == 6) or (is_leap and hm == 10 and hd == 6):
            ev.append("ሻቩኦት (Shavuot)")
        if (not is_leap and hm == 11 and hd == 9) or (is_leap and hm == 12 and hd == 9):
            ev.append("ቲሻ ባአቭ (Tisha B'Av)")
        return ev

    # ============================================================
    # BAHRE HASAB, FEASTS, SEASONS
    # ============================================================
    def _zero_to_thirty(self, val):
        return 30 if val == 0 else val

    def calculate_bahre_hasab(self, et_year):
        amete_alem = et_year + 5500
        wengelawi_idx = amete_alem % 4
        wengelawi_map = {1: 'ማቴዎስ', 2: 'ማርቆስ', 3: 'ሉቃስ', 0: 'ዮሐንስ'}
        medeb = amete_alem % 19
        wenber = 18 if medeb == 0 else medeb - 1
        abekte = self._zero_to_thirty((wenber * 11) % 30)
        metqe = self._zero_to_thirty((wenber * 19) % 30)
        tinte_qemer = (amete_alem + (amete_alem // 4)) % 7
        tinte_qemer_map = {0: 'ሰኞ', 1: 'ማክሰኞ', 2: 'ረቡዕ', 3: 'ሐሙስ', 4: 'ዓርብ', 5: 'ቅዳሜ', 6: 'እሁድ'}
        m_month_idx = 0 if metqe > 14 else 1
        m_weekday = (tinte_qemer + (m_month_idx * 2) + (metqe - 1)) % 7
        tewsak_map = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 8, 6: 7}
        mebaja_hamer_tewsak = tewsak_map[m_weekday]
        mebaja_hamer = mebaja_hamer_tewsak + metqe
        return {
            "AmeteAlem": amete_alem,
            "Wengelawi": wengelawi_map[wengelawi_idx],
            "Medeb": medeb,
            "Wenber": wenber,
            "Abekte": abekte,
            "Metqe": metqe,
            "TinteQemer": tinte_qemer_map[tinte_qemer],
            "MebajaHamer": mebaja_hamer,
            "Tewsak": mebaja_hamer_tewsak
        }

    def get_serqe_chereka(self, abekte, em, ed):
        chereka = (abekte + (em - 1) + ed) % 30
        return 30 if chereka == 0 else chereka

    def get_great_lent_week(self, day_num, feasts):
        if "abiy" not in feasts:
            return None
        abiy_day = (feasts["abiy"]["m"] - 1) * 30 + feasts["abiy"]["d"]
        first_sunday = abiy_day - 1
        if day_num < first_sunday:
            return None
        week_index = (day_num - first_sunday) // 7
        if week_index < 0 or week_index > 7:
            return None
        return GREAT_LENT_WEEK_KEYS[week_index]

    def get_great_lent_week_name(self, week_key):
        week_names = {
            "lent_week_1": "ዘወረደ (Zewerede)",
            "lent_week_2": "ቅድስት (Qidist)",
            "lent_week_3": "ምኵራብ (Mikurab)",
            "lent_week_4": "መጻጉዕ (Metsagu)",
            "lent_week_5": "ደብረ ዘይት (Debre Zeyit)",
            "lent_week_6": "ገብር ኄር (Gebre Hier)",
            "lent_week_7": "ኒቆዲሞስ (Nikodimos)",
            "lent_week_8": "ሆሳዕና (Hosanna)"
        }
        return week_names.get(week_key, week_key)

    def calculate_movable_feasts(self, mebaja_hamer, metqe):
        feasts_offsets = {
            "nenewe": 0, "abiy": 14, "debre_zeyit": 41,
            "hosanna": 62, "siklet": 67, "tensae": 69,
            "rikbe_kahnat": 93, "erget": 108, "parakletos": 118,
            "hawaryat": 119, "dihnet": 121
        }
        base_m_idx = 5 if metqe > 14 else 6
        results = {}
        for name, offset in feasts_offsets.items():
            total_days = mebaja_hamer + offset
            m_idx = base_m_idx
            day = total_days
            while day > 30:
                day -= 30
                m_idx += 1
            if m_idx > 13:
                m_idx -= 13
            results[name] = {"m": m_idx, "d": day}
        return results

    def ethiopian_day_of_year(self, em, ed):
        return ((em - 1) * 30) + ed

    def feast_to_day_number(self, feast_date):
        parts = feast_date.split()
        if len(parts) != 2:
            return 0
        month_name, day = parts
        try:
            for idx, name in enumerate(MONTHS):
                if name == month_name:
                    return ((idx - 1) * 30) + int(day)
            return 0
        except (ValueError, IndexError):
            return 0

    def day_of_year_to_month_day(self, day_number):
        em = ((day_number - 1) // 30) + 1
        ed = ((day_number - 1) % 30) + 1
        return em, ed

    def get_named_events_for_year(self, ey):
        meta = self.calculate_bahre_hasab(ey)
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
        events = [
            (1, "እንቁጣጣሽ (አዲስ ዓመት)"),
            (17, "የመስቀል በዓል"),
            (75, "ጾመ ነቢያት ይጀምራል"),
            (130, "ጾመ ገሀድ (የጥምቀት ዋዜማ)"),
            (131, "ጥምቀት"),
            (331, "ጾመ ፍልሰታ ይጀምራል"),
            (345, "ፍልሰታ ለማርያም"),
        ]
        genna_day = 28 if ey % 4 == 0 else 29
        events.append((90 + genna_day, "ገና (ልደት)"))
        for name, date_obj in feasts.items():
            display_name = self.get_feast_display_name(name)
            day_number = (date_obj["m"] - 1) * 30 + date_obj["d"]
            events.append((day_number, display_name))
        events.sort(key=lambda e: e[0])
        return events

    def get_feast_display_name(self, internal_key):
        feast_names = {
            "nenewe": "ጾመ ነነዌ",
            "abiy": "ዐቢይ ጾም",
            "debre_zeyit": "ደብረ ዘይት",
            "hosanna": "ሆሳዕና",
            "siklet": "ስቅለት",
            "tensae": "ትንሣኤ",
            "rikbe_kahnat": "ርክበ ካህናት",
            "erget": "ዕርገት",
            "parakletos": "ጰራቅሊጦስ",
            "hawaryat": "ጾመ ሐዋርያት",
            "dihnet": "ጾመ ድኅነት"
        }
        return feast_names.get(internal_key, internal_key)

    def get_next_events(self, ey, em, ed, max_events=5):
        today_jdn = self.ethiopian_to_jdn(ey, em, ed)
        candidates = []
        for year in (ey, ey + 1):
            for day_number, label in self.get_named_events_for_year(year):
                t_em, t_ed = self.day_of_year_to_month_day(day_number)
                t_jdn = self.ethiopian_to_jdn(year, t_em, t_ed)
                if t_jdn > today_jdn:
                    candidates.append((t_jdn - today_jdn, year, t_em, t_ed, label))
        candidates.sort(key=lambda c: c[0])
        return candidates[:max_events]

    def get_fasting_progress(self, ey, em, ed, meta=None, feasts=None):
        if meta is None:
            meta = self.calculate_bahre_hasab(ey)
        if feasts is None:
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

        current_day = self.ethiopian_day_of_year(em, ed)
        nenewe_day = (feasts["nenewe"]["m"] - 1) * 30 + feasts["nenewe"]["d"]
        abiy_day = (feasts["abiy"]["m"] - 1) * 30 + feasts["abiy"]["d"]
        tensae_day = (feasts["tensae"]["m"] - 1) * 30 + feasts["tensae"]["d"]
        hawariat_day = (feasts["hawaryat"]["m"] - 1) * 30 + feasts["hawaryat"]["d"]

        ranges = [
            ("ጾመ ነነዌ", nenewe_day, nenewe_day + 2),
            ("ዐቢይ ጾም", abiy_day, tensae_day - 1),
            ("ጾመ ነቢያት", 75, (118 if ey % 4 == 0 else 119) - 1),
            ("ጾመ ሐዋርያት", hawariat_day, 305),
            ("ጾመ ፍልሰታ", 331, 345),
        ]

        for name, start, end in ranges:
            if start and end and start <= current_day <= end:
                return name, current_day - start + 1, end - start + 1
        return None

    def get_climatic_season(self, em, ed):
        current_day = self.ethiopian_day_of_year(em, ed)
        if 26 <= current_day <= 115:
            return "መፀው (Autumn)"
        elif 116 <= current_day <= 205:
            return "በጋ (Summer)"
        elif 206 <= current_day <= 295:
            return "በልግ (Spring)"
        else:
            return "ክረምት (Winter)"

    def get_liturgical_season(self, ey, em, ed, meta=None, feasts=None):
        if meta is None:
            meta = self.calculate_bahre_hasab(ey)
        if feasts is None:
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

        current_day = self.ethiopian_day_of_year(em, ed)
        nenewe_day = (feasts["nenewe"]["m"] - 1) * 30 + feasts["nenewe"]["d"]
        abiy_day = (feasts["abiy"]["m"] - 1) * 30 + feasts["abiy"]["d"]
        hosanna_day = (feasts["hosanna"]["m"] - 1) * 30 + feasts["hosanna"]["d"]
        tensae_day = (feasts["tensae"]["m"] - 1) * 30 + feasts["tensae"]["d"]
        erget_day = (feasts["erget"]["m"] - 1) * 30 + feasts["erget"]["d"]
        pentecost_day = (feasts["parakletos"]["m"] - 1) * 30 + feasts["parakletos"]["d"]

        if 1 <= current_day <= 7:
            return "ዘመነ ዮሐንስ"
        elif current_day == 8:
            return "ዘካርያስ"
        elif 9 <= current_day <= 15:
            return "ዘመነ ፍሬ"
        elif 16 <= current_day <= 25:
            return "ዘመነ መስቀል"
        elif 26 <= current_day <= 65:
            return "ዘመነ ጽጌ"
        elif 66 <= current_day <= 96:
            return "ዘመነ አስተምሕሮ"
        elif 97 <= current_day <= 103:
            return "ዘመነ ስብከት"
        elif 104 <= current_day <= 110:
            return "ዘመነ ብርሃን"
        elif 111 <= current_day <= 116:
            return "ዘመነ ኖላዊ"
        elif current_day == 117:
            return "ዘመነ መርዓዊ"
        elif current_day == 118:
            return "አማኑኤል"
        elif 119 <= current_day <= 126:
            return "ዘመነ ልደት"
        elif 127 <= current_day <= 129:
            return "ናዝሬት"
        elif current_day == 130:
            return "ገሐድ"
        elif 131 <= current_day < nenewe_day:
            return "ዘመነ ጥምቀት"
        elif nenewe_day <= current_day < nenewe_day + 3:
            return "ዘመነ ነነዌ"
        elif nenewe_day + 3 <= current_day < abiy_day:
            return "ዘመነ መርዓዊ"
        elif abiy_day <= current_day < tensae_day:
            return "ዘመነ ጾም"
        elif tensae_day <= current_day < erget_day:
            return "ዘመነ ትንሣኤ"
        elif erget_day <= current_day < pentecost_day:
            return "ዘመነ ዕርገት"
        elif pentecost_day <= current_day <= 286:
            return "ዘመነ ጰራቅሊጦስ"
        elif 287 <= current_day <= 295:
            return "ዘመነ አስተምሕሮ"
        elif 296 <= current_day <= 318:
            return "ደመና፣ ዘርዕ፣ ዝናም"
        elif 319 <= current_day <= 339:
            return "መብረቅ፣ ባሕር"
        elif 340 <= current_day <= 357:
            return "ዐይነ ኵሉ፣ ዕጕለ ቋዓት"
        else:
            return "ጎሕ፣ ነግሕ"

    def get_fasting_season(self, ey, em, ed, meta=None, feasts=None):
        if meta is None:
            meta = self.calculate_bahre_hasab(ey)
        if feasts is None:
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

        current_day = self.ethiopian_day_of_year(em, ed)
        genna_day = 118 if ey % 4 == 0 else 119
        nenewe_day = (feasts["nenewe"]["m"] - 1) * 30 + feasts["nenewe"]["d"]
        abiy_day = (feasts["abiy"]["m"] - 1) * 30 + feasts["abiy"]["d"]
        tensae_day = (feasts["tensae"]["m"] - 1) * 30 + feasts["tensae"]["d"]
        hawariat_day = (feasts["hawaryat"]["m"] - 1) * 30 + feasts["hawaryat"]["d"]
        pentecost_day = (feasts["parakletos"]["m"] - 1) * 30 + feasts["parakletos"]["d"]

        if current_day in (genna_day, 131):
            return "በዓል (አይጾምም)"
        if abiy_day and tensae_day and abiy_day <= current_day < tensae_day:
            result = "ዐቢይ ጾም"
            week_key = self.get_great_lent_week(current_day, feasts)
            if week_key:
                result += f" ({self.get_great_lent_week_name(week_key)})"
            return result
        if 75 <= current_day < genna_day:
            return "ጾመ ነቢያት"
        if 331 <= current_day <= 345:
            return "ጾመ ፍልሰታ"
        if hawariat_day and hawariat_day <= current_day <= 305:
            return "ጾመ ሐዋርያት"
        if nenewe_day and nenewe_day <= current_day < nenewe_day + 3:
            return "ጾመ ነነዌ"
        if tensae_day and pentecost_day and tensae_day <= current_day <= pentecost_day:
            return "ኀምሳ ዕለት (Pentecost)"
        if current_day == 130:
            return "ጾመ ገሀድ (የጥምቀት ዋዜማ)"
        try:
            g_date = self.eth_to_gregorian(ey, em, ed)
            weekday = WEEKDAYS[g_date.weekday()]
            if weekday in ["ረቡዕ", "ዓርብ"]:
                return "ጾመ ድኅነት (የረቡዕ እና ዓርብ ጾም)"
        except (ValueError, OverflowError):
            pass
        return "የአጽዋም ዘመን አይደለም"

    # ============================================================
    # GITSAWE (LEGACY gitsawe_data.json support)
    # ============================================================
    def load_gitsawe_data(self):
        gitsawe_path = os.path.join(os.path.dirname(__file__), "gitsawe_data.json")
        try:
            if os.path.exists(gitsawe_path):
                with open(gitsawe_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logHandler.log.error(f"Ethiopian Calendar: failed to load Gitsawe data: {e}")
        return {"daily": [], "seasonal": [], "monthly": [], "months": [], "feasts": [], "subFeasts": [], "mahlets": []}

    def find_gitsawe_entry(self, gitsawe_data, ey, em, ed, feasts):
        day_num = self.ethiopian_day_of_year(em, ed)

        lent_week_key = self.get_great_lent_week(day_num, feasts)
        if lent_week_key:
            week_num = int(lent_week_key.replace("lent_week_", ""))
            season_key = f"{week_num:02d}-abiyTsom"
            for entry in gitsawe_data.get("seasonal", []):
                if entry.get("date") == season_key:
                    return entry

        if "nenewe" in feasts:
            nenewe_day = (feasts["nenewe"]["m"] - 1) * 30 + feasts["nenewe"]["d"]
            if day_num == nenewe_day:
                for entry in gitsawe_data.get("seasonal", []):
                    if entry.get("date") == "01-neneweTsom":
                        return entry

        if em == 4:
            gena_key = None
            if 7 <= ed <= 13:
                gena_key = "02-genaTsom"
            elif 14 <= ed <= 20:
                gena_key = "03-genaTsom"
            elif 21 <= ed <= 27:
                gena_key = "04-genaTsom"
            if gena_key:
                for entry in gitsawe_data.get("seasonal", []):
                    if entry.get("date") == gena_key:
                        return entry

        date_key = f"{ed:02d}-{em:02d}"
        for entry in gitsawe_data.get("daily", []):
            if entry.get("date") == date_key:
                return entry
        return None

    def format_gitsawe_readings(self, entry):
        if not entry:
            return "ለዛሬ የተመዘገበ ግጻዌ የለም።"

        html = f"<h2>📖 {entry.get('title', 'የዕለቱ ግጻዌ')}</h2>"

        if "negh" in entry:
            html += "<h3>ነግህ (የጠዋት ጸሎት)</h3>"
            negh = entry["negh"]
            if "msbak" in negh and negh["msbak"]:
                html += self._format_reading_section("መስበቅ", negh["msbak"])
            if "wengel" in negh and negh["wengel"]:
                html += self._format_reading_section("ወንጌል", negh["wengel"])
            if "firstDeacon" in negh and negh["firstDeacon"]:
                html += self._format_reading_section("የመጀመሪያ ንባብ (ዲቁና)", negh["firstDeacon"])
            if "secondDeacon" in negh and negh["secondDeacon"]:
                html += self._format_reading_section("ሁለተኛ ንባብ (ዲቁና)", negh["secondDeacon"])

        if "kidassie" in entry:
            html += "<h3>ቅዳሴ (Divine Liturgy)</h3>"
            kidassie = entry["kidassie"]
            if "msbak" in kidassie and kidassie["msbak"]:
                html += self._format_reading_section("መስበቅ", kidassie["msbak"])
            if "wengel" in kidassie and kidassie["wengel"]:
                html += self._format_reading_section("ወንጌል", kidassie["wengel"])
            if "secondKahn" in kidassie and kidassie["secondKahn"]:
                html += self._format_reading_section("ንባብ (ካህን)", kidassie["secondKahn"])
            if "kidassie" in kidassie and kidassie["kidassie"]:
                html += self._format_reading_section("የቅዳሴው ጸሎት", kidassie["kidassie"])

        return html

    def _format_reading_section(self, label, items):
        if not items:
            return ""
        html = f"<h4>{label}</h4><ul>"
        for item in items:
            if not item:
                continue
            verse = item.get("verse", {})
            text = item.get("text", {}).get("amharic", "")
            if not text:
                continue
            citation = ""
            if verse.get("bookTitle"):
                citation = verse["bookTitle"]
                if verse.get("chapter"):
                    citation += f" {verse['chapter']}"
                    if verse.get("start") is not None:
                        citation += f":{verse['start']}"
                        if verse.get("end") is not None and verse["end"] != verse["start"]:
                            citation += f"-{verse['end']}"
            if citation:
                html += f"<li><strong>{citation}</strong> — {text}</li>"
            else:
                html += f"<li>{text}</li>"
        html += "</ul>"
        return html

    # ============================================================
    # HTML BUILDERS
    # ============================================================
    def build_yearly_html(self, ey, today_context=None):
        meta = self.calculate_bahre_hasab(ey)
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

        html = ""
        if today_context:
            weekday, cur_em, cur_ed, cur_ey, chereka, zodiac, awde_negest = today_context
            fasting = self.get_fasting_season(cur_ey, cur_em, cur_ed, meta, feasts)
            liturgical = self.get_liturgical_season(cur_ey, cur_em, cur_ed, meta, feasts)
            climatic = self.get_climatic_season(cur_em, cur_ed)
            month_name = self.get_month_name(cur_em)

            html += f"<p>ዛሬ {weekday}፣ {month_name} {cur_ed} ቀን {cur_ey} ዓ.ም። የዕለቱ ሰርቀ ጨረቃ፦ {chereka}</p>"
            html += f"<p><strong>ወቅት፦</strong> {climatic}</p>"
            html += f"<p><strong>የአጽዋም ዘመን፦</strong> {fasting}</p>"
            html += f"<p><strong>የቤተክርስቲያን ዘመን፦</strong> {liturgical}</p>"
            html += f"<p><strong>የኮከብ ቆጠራ (Zodiac)፦</strong> {zodiac}</p>"
            html += f"<p><strong>በዓውደ ነገሥት፦</strong> {awde_negest}</p>"

        html += f"<h1>የ{ey} ዓ.ም የባሕረ ሐሳብ መረጃ</h1><ul>"
        html += f"<li><strong>ዓመተ ዓለም፦</strong> {meta['AmeteAlem']}</li>"
        html += f"<li><strong>ወንጌላዊ፦</strong> {meta['Wengelawi']}</li>"
        html += f"<li><strong>ጥንተ ቀመር፦</strong> {meta['TinteQemer']}</li>"
        html += f"<li><strong>መደብ፦</strong> {meta['Medeb']}</li>"
        html += f"<li><strong>ወንበር፦</strong> {meta['Wenber']}</li>"
        html += f"<li><strong>መጥቅዕ፦</strong> {meta['Metqe']}</li>"
        html += f"<li><strong>አበቅቴ፦</strong> {meta['Abekte']}</li>"
        html += f"<li><strong>መባጃ ሐመር፦</strong> {meta['MebajaHamer']}</li>"
        html += f"<li><strong>ተውሳክ፦</strong> {meta['Tewsak']}</li>"
        html += "</ul>"

        html += "<h2>የዐመቱ ተንቀሳቃሽ በዓላትና አጽዋማት</h2><ul>"
        for name, date_obj in feasts.items():
            display_name = self.get_feast_display_name(name)
            html += f"<li><strong>{display_name}:</strong> {self.get_month_name(date_obj['m'])} {date_obj['d']}</li>"
        html += "</ul>"

        return html, meta, feasts

    def show_html(self, title, html):
        full_html = f"<html><head><meta charset='utf-8'></head><body style=\"font-family: 'Nyala', 'Kefa', 'Abyssinica SIL', 'Visual Geez Unicode', sans-serif;\">{html}</body></html>"
        wx.CallAfter(ui.browseableMessage, full_html, title, isHtml=True)

    def build_islamic_html(self, iy, im, id_, g_date=None, ey=None, em=None, ed=None):
        if g_date is not None:
            weekday = WEEKDAYS[g_date.weekday()]
        else:
            weekday = self.get_islamic_weekday(iy, im, id_)
        month_name = self.get_islamic_month_name(im)
        events = self.get_islamic_event(iy, im, id_)
        html = f"<h1>{weekday}፣ {month_name} {id_} ቀን {iy} ዓ.ሂ (Hijri)</h1>"
        if g_date:
            html += f"<p>ተመጣጣኝ የግሪጎሪያን ቀን፦ {g_date.strftime('%Y-%m-%d')}</p>"
        if ey is not None:
            html += f"<p>ተመጣጣኝ የኢትዮጵያ ቀን፦ {self.get_month_name(em)} {ed} ቀን {ey} ዓ.ም</p>"
        html += "<h2>ወቅታዊ መረጃ</h2><ul>"
        if events:
            for ev in events:
                html += f"<li>{ev}</li>"
        else:
            html += "<li>የተለየ የጾም ወይም የሐጅ ወቅት አይደለም።</li>"
        html += f"<li>ዓመቱ {'ሰበቅ (ልዩ) ዓመት' if self.is_islamic_leap(iy) else 'መደበኛ ዓመት'} ነው።</li></ul>"
        html += "<p><em>ማሳሰቢያ፦ ይህ በሒሳብ ስሌት ላይ የተመሠረተ ሂሳባዊ ቀን ሲሆን ከትክክለኛ የጨረቃ ምልከታ ጋር በ1-2 ቀናት ሊለያይ ይችላል።</em></p>"
        return html

    def build_islamic_year_html(self, iy):
        is_leap = self.is_islamic_leap(iy)
        year_start = self.islamic_to_gregorian(iy, 1, 1)
        year_end = self.islamic_to_gregorian(iy, 12, self.get_islamic_month_length(iy, 12))
        html = f"<h2>{iy} ዓ.ሂ ሙሉ ዓመት መረጃ</h2><p>ከ{year_start.strftime('%Y-%m-%d')} ({self.format_eth_label(year_start)}) እስከ {year_end.strftime('%Y-%m-%d')} ({self.format_eth_label(year_end)}) ({'ሰበቅ ዓመት' if is_leap else 'መደበኛ ዓመት'})</p><h3>ወራት</h3><ul>"
        for im in range(1, 13):
            length = self.get_islamic_month_length(iy, im)
            start = self.islamic_to_gregorian(iy, im, 1)
            end = self.islamic_to_gregorian(iy, im, length)
            html += f"<li>{self.get_islamic_month_name(im)}፦ {WEEKDAYS[start.weekday()]}፣ {start.strftime('%Y-%m-%d')} ({self.format_eth_label(start)}) - {WEEKDAYS[end.weekday()]}፣ {end.strftime('%Y-%m-%d')} ({self.format_eth_label(end)}) ({length} ቀናት)</li>"
        html += "</ul><h3>ዋና ዋና ዕለታት</h3><ul>"
        key_events = [(1, 10, "ዓሹራ (Ashura)"), (3, 12, "መውሊድ (Mawlid)"),
                      (7, 27, "እስራ ወሚዕራጅ (Isra and Mi'raj)"), (9, 1, "የረመዳን መጀመሪያ"),
                      (9, 21, "የረመዳን መጨረሻዎቹ 10 ቀናት ይጀምራሉ"), (10, 1, "ዒድ አልፈጥር"),
                      (12, 9, "የዐረፋ ቀን"), (12, 10, "ዒድ አልአድሐ")]
        for im, id_, label in key_events:
            g_date = self.islamic_to_gregorian(iy, im, id_)
            html += f"<li>{label}፦ {g_date.strftime('%Y-%m-%d')} ({WEEKDAYS[g_date.weekday()]}) — {self.format_eth_label(g_date)}</li>"
        html += "</ul>"
        return html

    # ============================================================
    # FDRE HOLIDAYS
    # ============================================================
    def get_islamic_occurrences_in_range(self, target_month, target_day, g_start, g_end):
        iy_start, _, _ = self.gregorian_to_islamic(g_start.year, g_start.month, g_start.day)
        iy_end, _, _ = self.gregorian_to_islamic(g_end.year, g_end.month, g_end.day)
        occurrences = set()
        for iy in range(iy_start - 1, iy_end + 2):
            try:
                g_date = self.islamic_to_gregorian(iy, target_month, target_day)
            except Exception:
                continue
            if g_start <= g_date <= g_end:
                occurrences.add(g_date)
        return sorted(occurrences)

    def get_fdre_holidays(self, ey):
        window_start = self.eth_to_gregorian(ey, 1, 1)
        window_end = self.eth_to_gregorian(ey + 1, 1, 1) - datetime.timedelta(days=1)
        g_year_start = window_start.year

        def entry(name_am, name_en, g_date, closed, note="", hid=""):
            return {
                "id": hid, "name_am": name_am, "name_en": name_en, "gregorian": g_date,
                "weekday": WEEKDAYS[g_date.weekday()],
                "ethiopian_label": self.format_eth_label(g_date), "closed": closed, "note": note,
            }

        celebrated = [
            entry("እንቁጣጣሽ (አዲስ ዓመት)", "New Year", window_start, True, hid="hol_enkutatash"),
            entry("የዓድዋ ድል በዓል", "Adwa Victory Day", self.eth_to_gregorian(ey, 6, 23), True, hid="hol_adwa"),
            entry("የዓለም የሠራተኞች ቀን", "International Workers' Day",
                  datetime.date(g_year_start + 1, 5, 1), True, hid="hol_labor"),
            entry("የአርበኞች ድል በዓል", "Ethiopian Patriots' Victory Day",
                  self.eth_to_gregorian(ey, 8, 27), True, hid="hol_patriots"),
        ]

        memorial = [
            entry("የብሔሮች፣ ብሔረሰቦችና ሕዝቦች ቀን", "Nations, Nationalities and Peoples' Day",
                  self.eth_to_gregorian(ey, 3, 29), False, hid="hol_nations_day"),
            entry("የሰማዕታት መታሰቢያ ቀን", "Ethiopian Martyrs' Day",
                  self.eth_to_gregorian(ey, 6, 12), False, hid="hol_martyrs_day"),
        ]

        meta = self.calculate_bahre_hasab(ey)
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
        siklet_day = (feasts["siklet"]["m"] - 1) * 30 + feasts["siklet"]["d"]
        tensae_day = (feasts["tensae"]["m"] - 1) * 30 + feasts["tensae"]["d"]

        def day_number_to_gregorian(day_number):
            em = ((day_number - 1) // 30) + 1
            ed = ((day_number - 1) % 30) + 1
            return self.eth_to_gregorian(ey, em, ed)

        genna_day = 28 if ey % 4 == 0 else 29
        religious = [
            entry("የመስቀል በዓል", "Meskel", self.eth_to_gregorian(ey, 1, 17), True, hid="hol_meskel"),
            entry("ገና (ልደት)", "Christmas", self.eth_to_gregorian(ey, 4, genna_day), True, hid="hol_genna"),
            entry("ጥምቀት", "Epiphany", self.eth_to_gregorian(ey, 5, 11), True, hid="hol_timkat"),
        ]
        if siklet_day:
            religious.append(entry("ስቅለት", "Good Friday", day_number_to_gregorian(siklet_day), True, hid="fest_siklet"))
        if tensae_day:
            religious.append(entry("ትንሣኤ (ፋሲካ)", "Easter", day_number_to_gregorian(tensae_day), True, hid="fest_tensae"))

        islamic_note = "ቀኑ ሂሳባዊ ነው፣ ከጨረቃ ምልከታ ጋር ሊለያይ ይችላል።"
        for occ in self.get_islamic_occurrences_in_range(3, 12, window_start, window_end):
            religious.append(entry("መውሊድ", "Mawlid", occ, True, note=islamic_note, hid="hol_mawlid"))
        for occ in self.get_islamic_occurrences_in_range(10, 1, window_start, window_end):
            religious.append(entry("ዒድ አልፈጥር", "Eid al-Fitr", occ, True, note=islamic_note, hid="hol_eid_fitr"))
        for occ in self.get_islamic_occurrences_in_range(12, 10, window_start, window_end):
            religious.append(entry("ዒድ አልአድሐ (አረፋ)", "Eid al-Adha", occ, True, note=islamic_note, hid="hol_eid_adha"))

        cultural_note = "ባህላዊና ሃይማኖታዊ በዓል።"
        religious.append(entry("ቡሄ (ደብረ ታቦር)", "Buhe (Debre Tabor)", self.eth_to_gregorian(ey, 12, 13), None,
                               note=cultural_note, hid="hol_buhe"))
        religious.append(entry("አሸንዳ", "Ashenda", self.eth_to_gregorian(ey, 12, 16), None,
                               note=cultural_note, hid="hol_ashenda"))
        start_j = self.gregorian_to_jdn(window_start.year, window_start.month, window_start.day)
        end_j = self.gregorian_to_jdn(window_end.year, window_end.month, window_end.day) + 1
        heb_start = tuple(self.jdn_to_hebrew(start_j))[0]
        heb_end = tuple(self.jdn_to_hebrew(end_j))[0]
        for hy in range(heb_start - 1, heb_end + 2):
            j = self.hebrew_to_jdn(hy, 2, 29)
            if start_j <= j < end_j:
                religious.append(entry("ስግድ", "Sigd", self.jdn_to_gregorian(j), None,
                                       note="የቤተ እስራኤል በዓል፤ ቀኑ በዕብራውያን የቀን አቆጣጠር ሂሳብ የተሰላ ነው።", hid="hol_sigd"))

        celebrated.sort(key=lambda h: h["gregorian"])
        memorial.sort(key=lambda h: h["gregorian"])
        religious.sort(key=lambda h: h["gregorian"])
        return {"celebrated": celebrated, "memorial": memorial, "religious": religious}

    @staticmethod
    def _holiday_status(h):
        if h.get("closed") is None:
            return ""
        return "ተቋማት ይዘጋሉ" if h["closed"] else "ተቋማት ክፍት ናቸው"

    def get_fasting_periods(self, ey):
        meta = self.calculate_bahre_hasab(ey)
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
        day = lambda k: (feasts[k]['m'] - 1) * 30 + feasts[k]['d']
        f_nenewe, f_abiy, f_tensae, f_haw = day('nenewe'), day('abiy'), day('tensae'), day('hawaryat')
        ranges = [("fast_nenewe", "ጾመ ነነዌ", f_nenewe, 3), ("fast_abiy", "ዐቢይ ጾም", f_abiy, f_tensae - f_abiy),
                  ("fast_nebiyat", "ጾመ ነቢያት", 75, (118 if ey % 4 == 0 else 119) - 75), ("fast_hawaryat", "ጾመ ሐዋርያት", f_haw, 305 - f_haw + 1),
                  ("fast_filseta", "ጾመ ፍልሰታ", 331, 15)]
        out = []
        for fid, name, start, length in ranges:
            s_em, s_ed = self.day_of_year_to_month_day(start)
            e_em, e_ed = self.day_of_year_to_month_day(start + length - 1)
            out.append({'id': fid, 'name': name, 'start': self.eth_to_gregorian(ey, s_em, s_ed),
                        'end': self.eth_to_gregorian(ey, e_em, e_ed)})
        return out

    def get_movable_feasts_list(self, ey):
        meta = self.calculate_bahre_hasab(ey)
        feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
        out = []
        for key, d in feasts.items():
            fid = ('fast_' if key in ('nenewe', 'abiy', 'hawaryat', 'dihnet') else 'fest_') + key
            out.append(((d['m'] - 1) * 30 + d['d'], {'id': fid, 'name': self.get_feast_display_name(key),
                                                   'gregorian': self.eth_to_gregorian(ey, d['m'], d['d'])}))
        out.sort(key=lambda x: x[0])
        return [o for _, o in out]

    def build_year_ical(self, ey):
        one = datetime.timedelta(days=1)
        vevents = []
        used = set()

        def add(base, summary, start, end, note=''):
            uid = f"{base}-{ey}@ethio-calendar"
            if uid in used:
                uid = f"{base}-start-{ey}@ethio-calendar"
            used.add(uid)
            vevents.append(self._vevent(uid, summary, start, end, note))

        table = self.get_fdre_holidays(ey)
        holiday_ids = set()
        for key in ('celebrated', 'memorial', 'religious'):
            for h in table[key]:
                holiday_ids.add(h['id'])
                add(h['id'], h['name_am'], h['gregorian'], h['gregorian'] + one, h.get('note') or '')
        for f in self.get_fasting_periods(ey):
            add(f['id'], f['name'], f['start'], f['end'] + one)
        for m in self.get_movable_feasts_list(ey):
            if m['id'] not in holiday_ids:
                add(m['id'], m['name'], m['gregorian'], m['gregorian'] + one)
        return self._calendar(vevents, f"የ{ey} ዓ.ም ብሔራዊ በዓላትና መታሰቢያ ቀናት")

    def get_todays_fdre_holiday(self, ey, em, ed):
        holidays = self.get_fdre_holidays(ey)
        today_g = self.eth_to_gregorian(ey, em, ed)
        categories = (("celebrated", "የተከበረ ብሔራዊ በዓል"),
                      ("memorial", "የመታሰቢያ ቀን"),
                      ("religious", "የሃይማኖት በዓል"))
        for key, label in categories:
            for h in holidays[key]:
                if h["gregorian"] == today_g:
                    return label, h
        return None, None

    def build_fdre_holidays_html(self, ey):
        holidays = self.get_fdre_holidays(ey)
        parts = ["<main lang='am'>", f"<h1>የ{ey} ዓ.ም ብሔራዊ በዓላት</h1>"]

        def render_section(title, items):
            section = f"<h2>{title}</h2><ul>"
            for h in items:
                status = self._holiday_status(h)
                status_html = f" {status}።" if status else ""
                note_html = f" {h['note']}" if h.get("note") else ""
                section += (f"<li><strong>{h['name_am']}</strong> ({h['name_en']})፦ {h['weekday']}፣ "
                            f"{h['gregorian'].strftime('%Y-%m-%d')} ({h['ethiopian_label']})።{status_html}{note_html}</li>")
            return section + "</ul>"

        parts.append(render_section("የተከበሩ ብሔራዊ በዓላት", holidays["celebrated"]))
        parts.append(render_section("የመታሰቢያ ቀናት", holidays["memorial"]))
        parts.append(render_section("የሃይማኖት በዓላት", holidays["religious"]))

        parts.append("<h2>የአጽዋማት ወቅቶች</h2><ul>")
        for f in self.get_fasting_periods(ey):
            s_y, s_m, s_d = self.gregorian_to_ethiopian(f["start"].year, f["start"].month, f["start"].day)
            e_y, e_m, e_d = self.gregorian_to_ethiopian(f["end"].year, f["end"].month, f["end"].day)
            parts.append(f"<li><strong>{f['name']}</strong>፦ {self.get_month_name(s_m)} {s_d} – "
                         f"{self.get_month_name(e_m)} {e_d} ({f['start'].strftime('%Y-%m-%d')} – "
                         f"{f['end'].strftime('%Y-%m-%d')})</li>")
        parts.append("</ul>")

        parts.append("<h2>ተንቀሳቃሽ በዓላት</h2><ul>")
        for m in self.get_movable_feasts_list(ey):
            g = m["gregorian"]
            _, e_m, e_d = self.gregorian_to_ethiopian(g.year, g.month, g.day)
            parts.append(f"<li><strong>{m['name']}</strong>፦ {WEEKDAYS[g.weekday()]}፣ "
                         f"{self.get_month_name(e_m)} {e_d} ({g.strftime('%Y-%m-%d')})</li>")
        parts.append("</ul></main>")
        return "".join(parts)

    # ============================================================
    # SYNAXARIUM BY DATE
    # ============================================================
    @scriptHandler.script(description="Search Synaxarium by specific Ethiopian date.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+alt+s")
    @guarded_by_shortcut_setting("synaxariumByDate")
    def script_synaxariumByDate(self, gesture):
        wx.CallAfter(self._showSynaxariumByDateDialog)

    def _showSynaxariumByDateDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            ey, em, ed = self.get_ethiopian_date()
            dlg = SynaxariumByDateDialog(gui.mainFrame, year=ey, month=em, day=ed)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_synaxarium_by_date(
                    dlg.yearCtrl.GetValue(),
                    dlg.monthCtrl.GetValue(),
                    dlg.dayCtrl.GetValue()
                )
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_synaxarium_by_date(self, year_str, month_str, day_str):
        year_str = (year_str or "").strip()
        month_str = (month_str or "").strip()
        day_str = (day_str or "").strip()

        cur_ey, cur_em, cur_ed = self.get_ethiopian_date()

        try:
            ey = int(year_str) if year_str else cur_ey
        except ValueError:
            ui.message("እባክዎ ትክክለኛ ዓመት ቁጥር ያስገቡ።")
            return

        if month_str:
            try:
                em = int(month_str)
            except ValueError:
                em = self.match_month_name(month_str)
                if em is None:
                    ui.message("እባክዎ ትክክለኛ የወር ቁጥር ወይም ስም ያስገቡ።")
                    return
        else:
            em = cur_em

        try:
            ed = int(day_str) if day_str else cur_ed
        except ValueError:
            ui.message("እባክዎ ትክክለኛ ቀን ቁጥር ያስገቡ።")
            return

        if em < 1 or em > 13:
            ui.message("ወር ከ1 እስከ 13 ብቻ መሆን አለበት።")
            return

        month_length = self.get_month_length(ey, em)
        if ed < 1 or ed > month_length:
            ui.message(f"ለ{self.get_month_name(em)} ቀን ከ1 እስከ {month_length} ብቻ መሆን አለበት።")
            return

        entries = self.get_synaxarium_by_date(em, ed)

        if entries:
            annual, monthly = self.split_synax_entries(entries)
            html = f"<h1>የ{self.get_month_name(em)} {ed} ቀን {ey} ዓ.ም የስንክሳር በዓላት</h1>"

            if annual:
                html += "<h2>ዓመታዊ በዓላት</h2><ul>"
                for feast in annual:
                    html += f"<li>{feast}</li>"
                html += "</ul>"

            if monthly:
                html += "<h2>ወርኃዊ በዓላት</h2><ul>"
                for feast in monthly:
                    html += f"<li>{feast}</li>"
                html += "</ul>"

            if not annual and not monthly:
                html += "<p>ለዚህ ቀን ምንም የተመዘገበ በዓል የለም።</p>"

            self.show_html(f"የ{self.get_month_name(em)} {ed}, {ey} ስንክሳር", html)
            msg = f"ለ{self.get_month_name(em)} {ed} ቀን {ey} ዓ.ም {len(entries)} የስንክሳር በዓላት ተገኝተዋል።"
            ui.message(msg)
        else:
            ui.message(f"ለ{self.get_month_name(em)} {ed} ቀን {ey} ዓ.ም የተመዘገበ የስንክሳር በዓል የለም።")

    # ============================================================
    # GITSAWE READINGS SCRIPT — HTML page, not dialog
    # ============================================================
    @scriptHandler.script(
        description="Displays the Gitsawe (daily church readings) for today.",
        category="Ethiopian Calendar", gesture="kb:control+shift+r"
    )
    @guarded_by_shortcut_setting("gitsaweReadings")
    def script_gitsaweReadings(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            self.load_gitsawe()
            reading = self.get_day_reading(em, ed)
            if not reading:
                ui.message("ለዛሬ የተመዘገበ ግጻዌ የለም።")
                return
            self._open_gitsawe_page(em, ed, reading)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    def _open_gitsawe_page(self, em, ed, reading):
        """Render the day's readings as a navigable HTML page."""
        blocks = self.format_reading_sections(reading, {"month": em, "day": ed})
        title = f"የ{self.get_month_name(em)} {ed} ቀን ግጻዌ"
        html = render_gitsawe_html(
            self, blocks, title, em, ed,
            reading.get("commemoration", "")
        )
        ui.message(f"{title}። በርዕስ ለመዘዋወር H ይጠቀሙ።")
        self.show_html(title, html)

    @scriptHandler.script(
        description="Search the integrated Gitsawe dataset.",
        category="Ethiopian Calendar", gesture="kb:control+alt+r"
    )
    @guarded_by_shortcut_setting("gitsaweSearch")
    def script_gitsaweSearch(self, gesture):
        wx.CallAfter(self._show_gitsawe_search)

    def _show_gitsawe_search(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = GitsaweSearchDialog(gui.mainFrame, self)
            if dlg.ShowModal() == wx.ID_OK:
                q = dlg.query.GetValue().strip()
                results = self.search_gitsawe(q)
                if not results:
                    ui.message("ምንም የግጻዌ ውጤት አልተገኘም።")
                else:
                    resultDlg = GitsaweSearchResultsDialog(gui.mainFrame, self, q, results)
                    resultDlg.ShowModal()
                    resultDlg.Destroy()
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    @scriptHandler.script(description="Open the Ethiopian planning workspace.",
                          category="Ethiopian Calendar", gesture="kb:control+alt+y")
    @guarded_by_shortcut_setting("planning")
    def script_planning(self, gesture):
        gui.mainFrame.prePopup()
        dlg = PlanningDialog(gui.mainFrame, self)
        try:
            dlg.ShowModal()
            action, plan = dlg.action, dlg.plan
        finally:
            dlg.Destroy()
            gui.mainFrame.postPopup()
        if action == 'page' and plan:
            self.show_plan_page(plan, getattr(self, 'planning_columns', None))

    @scriptHandler.script(description="Open the integrated Ethiopian agenda.",
                          category="Ethiopian Calendar", gesture="kb:control+alt+a")
    @guarded_by_shortcut_setting("agenda")
    def script_agenda(self, gesture):
        gui.mainFrame.prePopup()
        dlg = AgendaDialog(gui.mainFrame, self)
        try:
            dlg.ShowModal()
            action, show_done, day_date = dlg.action, dlg.show_done, dlg.day_date
        finally:
            dlg.Destroy()
            gui.mainFrame.postPopup()
        if action == 'page':
            self.show_agenda_page(show_done)
        elif action == 'day' and day_date:
            self.show_day_agenda_page(*day_date)

    @scriptHandler.script(description="Show the agenda as a navigable HTML page.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+alt+a")
    @guarded_by_shortcut_setting("agendaPage")
    def script_agendaPage(self, gesture):
        try:
            self.show_agenda_page(True)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    # ============================================================
    # ETHIOPIAN CALENDAR SCRIPTS
    # ============================================================
    @scriptHandler.script(
        description="Show the agenda, holidays, Synaxarium, Gitsawe and season info for a chosen Ethiopian date.",
        category="Ethiopian Calendar", gesture="kb:control+alt+d"
    )
    @guarded_by_shortcut_setting("dayAgenda")
    def script_dayAgenda(self, gesture):
        wx.CallAfter(self._show_day_agenda_dialog)

    def _show_day_agenda_dialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        chosen = None
        try:
            ey, em, ed = self.get_ethiopian_date()
            dlg = DateChoiceDialog(gui.mainFrame, self, "የቀን አጀንዳ", ey, em, ed)
            if dlg.ShowModal() == wx.ID_OK:
                chosen = dlg.date()
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg is not None:
                dlg.Destroy()
            gui.mainFrame.postPopup()
        if chosen:
            try:
                self.show_day_agenda_page(*chosen)
            except Exception as e:
                ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(
        description="Search the Gitsawe readings by a chosen Ethiopian month and day.",
        category="Ethiopian Calendar"
    )
    @guarded_by_shortcut_setting("gitsaweByDate")
    def script_gitsaweByDate(self, gesture):
        wx.CallAfter(self._show_gitsawe_by_date)

    def _show_gitsawe_by_date(self):
        gui.mainFrame.prePopup()
        dlg = None
        chosen = None
        try:
            ey, em, ed = self.get_ethiopian_date()
            dlg = DateChoiceDialog(gui.mainFrame, self, "በግጻዌ በቀን ፈልግ", ey, em, ed, with_year=False)
            if dlg.ShowModal() == wx.ID_OK:
                chosen = dlg.date()
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg is not None:
                dlg.Destroy()
            gui.mainFrame.postPopup()
        if chosen:
            try:
                _, em, ed = chosen
                self.load_gitsawe()
                reading = self.get_day_reading(em, ed)
                if not reading:
                    ui.message("ለዚህ ቀን የግጻዌ መረጃ አልተገኘም።")
                    return
                self._open_gitsawe_page(em, ed, reading)
            except Exception as e:
                ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(
        description="Show the table of contents of the Gitsawe book.",
        category="Ethiopian Calendar", gesture="kb:control+alt+s"
    )
    @guarded_by_shortcut_setting("gitsaweStructure")
    def script_gitsaweStructure(self, gesture):
        try:
            _, structure = self.load_gitsawe()
            if not structure or not structure.get("parts"):
                ui.message("የግጻዌ መረጃ መጫን አልተቻለም።")
                return
            title = (structure.get("book") or {}).get("title") or "የመጽሐፉ ማውጫ"
            self.show_html(title, render_gitsawe_structure_html(structure))
            ui.message(f"{title}። በርዕስ ለመዘዋወር H ይጠቀሙ።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(
        description="Export this year's holidays, fasting periods and movable feasts as an iCal file.",
        category="Ethiopian Calendar", gesture="kb:control+alt+h"
    )
    @guarded_by_shortcut_setting("holidaysIcal")
    def script_holidaysIcal(self, gesture):
        wx.CallAfter(self._export_year_ical)

    def _export_year_ical(self):
        try:
            ey, _, _ = self.get_ethiopian_date()
            self._export_file(self.build_year_ical(ey), f"ethiopian-calendar-{ey}.ics", "text/calendar")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces whether today is an FDRE public holiday and shows the full year's holiday calendar in a window.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+a")
    @guarded_by_shortcut_setting("fdreHolidays")
    def script_fdreHolidays(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            weekday = self.get_weekday_name()
            month_name = self.get_month_name(em)

            category_label, holiday = self.get_todays_fdre_holiday(ey, em, ed)
            if holiday:
                status = self._holiday_status(holiday)
                msg = f"ዛሬ {weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም {category_label} ነው፦ {holiday['name_am']} ({holiday['name_en']})። " + (f"{status}። " if status else "")
            else:
                msg = f"ዛሬ {weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም ብሔራዊ በዓል አይደለም። "
            msg += "ሙሉ ዝርዝሩ በመስኮቱ ውስጥ ይታያል።"
            ui.message(msg)

            html = self.build_fdre_holidays_html(ey)
            self.show_html(f"የ{ey} ዓ.ም ብሔራዊ በዓላት", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces the current Ethiopian date, weekday, and full Bahre Hasab.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+e")
    @guarded_by_shortcut_setting("fullInfo")
    def script_fullInfo(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            weekday = self.get_weekday_name()
            now = datetime.datetime.now()
            meta = self.calculate_bahre_hasab(ey)
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
            chereka = self.get_serqe_chereka(meta['Abekte'], em, ed)
            fasting = self.get_fasting_season(ey, em, ed, meta, feasts)
            liturgical = self.get_liturgical_season(ey, em, ed, meta, feasts)
            climatic = self.get_climatic_season(em, ed)
            zodiac = self.get_zodiac_sign(now.month, now.day)
            awde_negest = self.get_awde_negest_sign(now.month, now.day)
            month_name = self.get_month_name(em)

            msg = (
                f"ዛሬ {weekday}፣ {month_name} {ed} ቀን {ey} ዓመተ ምሕረት ነው። "
                f"ዓመተ ዓለም {meta['AmeteAlem']}። ዘመነ {meta['Wengelawi']}። "
                f"መጥቅዕ {meta['Metqe']}። አበቅቴ {meta['Abekte']}። "
                f"መባጃ ሐመር {meta['MebajaHamer']}። የዛሬው ሰርቀ ጨረቃ (የጨረቃ ዕድሜ) {chereka} ነው። "
                f"ወቅት፦ {climatic}። "
                f"የአጽዋም ዘመን፦ {fasting}። "
                f"የቤተክርስቲያን ዘመን፦ {liturgical}። "
                f"የኮከብ ቆጠራ፦ {zodiac}። "
                f"በዓውደ ነገሥት፦ {awde_negest}።"
            )
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces the current time in Ethiopian local (Habesha) time.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+t")
    @guarded_by_shortcut_setting("ethiopianLocalTime")
    def script_ethiopianLocalTime(self, gesture):
        try:
            now = datetime.datetime.now()
            std_hour = now.hour
            eth_hour = (std_hour - 6) % 12
            if eth_hour == 0:
                eth_hour = 12
            if std_hour < 6:
                period = "ሌሊት"
            elif std_hour < 12:
                period = "ጠዋት"
            elif std_hour < 18:
                period = "ከሰዓት በኋላ"
            else:
                period = "ማታ"
            msg = f"የኢትዮጵያ ሰዓት፦ {eth_hour} ሰዓት ከ{now.minute:02d} ደቂቃ {period}። (መደበኛ ሰዓት {self.format_12h(now)})"
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces the current time of day using the Bahire Hasab kekros system.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+q")
    @guarded_by_shortcut_setting("kekrosTime")
    def script_kekrosTime(self, gesture):
        try:
            now = datetime.datetime.now()
            day_start = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if now < day_start:
                day_start -= datetime.timedelta(days=1)
            elapsed_seconds = int((now - day_start).total_seconds())
            kekros = elapsed_seconds // 1440
            remainder = elapsed_seconds % 1440
            kaelit = remainder // 24
            msg = f"በባሕረ ሐሳብ አቆጣጠር፦ ከዛሬው የኢትዮጵያ ቀን መጀመሪያ (ንጋት 12 ሰዓት) ጀምሮ {kekros} ኬክሮስ ከ{kaelit} ካልዒት አልፏል። (መደበኛ ሰዓት {self.format_12h(now, with_seconds=True)})"
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Copies the current Ethiopian date and Bahre Hasab to the clipboard.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+c")
    @guarded_by_shortcut_setting("copyDate")
    def script_copyDate(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            weekday = self.get_weekday_name()
            meta = self.calculate_bahre_hasab(ey)
            month_name = self.get_month_name(em)

            msg = f"{weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም። ዘመነ {meta['Wengelawi']}።"
            if api.copyToClip(msg):
                ui.message("ቀኑ ኮፒ ተደርጓል (Copied to clipboard)")
            else:
                ui.message("ኮፒ ማድረግ አልተቻለም (Failed to copy)")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Displays the full current date in a virtual window.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+f")
    @guarded_by_shortcut_setting("fullDateHtml")
    def script_fullDateHtml(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            weekday = self.get_weekday_name()
            meta = self.calculate_bahre_hasab(ey)
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
            chereka = self.get_serqe_chereka(meta['Abekte'], em, ed)
            fasting = self.get_fasting_season(ey, em, ed, meta, feasts)
            liturgical = self.get_liturgical_season(ey, em, ed, meta, feasts)
            climatic = self.get_climatic_season(em, ed)
            now = datetime.datetime.now()
            month_name = self.get_month_name(em)

            moon_phase = self.get_moon_phase_text(chereka)
            sun_rise, sun_set = self.get_addis_sun_times(now.date())
            jdn = self.gregorian_to_jdn(now.year, now.month, now.day)
            jy, jm, jd = self.jdn_to_julian(jdn)
            hy, hm, hd = self.jdn_to_hebrew(jdn)
            is_heb_leap = self.hebrew_leap(hy)
            heb_month_name = self.get_hebrew_month_name(hm, is_heb_leap)

            html = f"<h1>{weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም</h1>"
            html += f"<p>ተመጣጣኝ የግሪጎሪያን ቀን፦ {now.strftime('%Y-%m-%d')}</p>"
            html += f"<p>ተመጣጣኝ የጁሊያን ቀን፦ {jy}-{jm:02d}-{jd:02d}</p>"
            html += f"<p>ተመጣጣኝ የዕብራውያን ቀን፦ {heb_month_name} {hd} ቀን {hy}</p>"

            html += "<h2>የወቅቱ መረጃ</h2><ul>"
            html += f"<li><strong>ወቅት (Season)፦</strong> {climatic}</li>"
            html += f"<li><strong>የአጽዋም ዘመን፦</strong> {fasting}</li>"
            html += f"<li><strong>የቤተክርስቲያን ዘመን፦</strong> {liturgical}</li>"
            html += f"<li><strong>የኮከብ ቆጠራ (Zodiac)፦</strong> {self.get_zodiac_sign(now.month, now.day)}</li>"
            html += f"<li><strong>በዓውደ ነገሥት፦</strong> {self.get_awde_negest_sign(now.month, now.day)}</li>"
            html += "</ul>"

            html += "<h2>የባሕረ ሐሳብ መረጃ</h2><ul>"
            html += f"<li><strong>ዓመተ ዓለም፦</strong> {meta['AmeteAlem']}</li>"
            html += f"<li><strong>ወንጌላዊ፦</strong> {meta['Wengelawi']}</li>"
            html += f"<li><strong>ጥንተ ቀመር፦</strong> {meta['TinteQemer']}</li>"
            html += f"<li><strong>መደብ፦</strong> {meta['Medeb']}</li>"
            html += f"<li><strong>ወንበር፦</strong> {meta['Wenber']}</li>"
            html += f"<li><strong>መጥቅዕ፦</strong> {meta['Metqe']}</li>"
            html += f"<li><strong>አበቅቴ፦</strong> {meta['Abekte']}</li>"
            html += f"<li><strong>መባጃ ሐመር፦</strong> {meta['MebajaHamer']}</li>"
            html += f"<li><strong>ተውሳክ፦</strong> {meta['Tewsak']}</li>"
            html += f"<li><strong>የዕለቱ ሰርቀ ጨረቃ፦</strong> {chereka} ({moon_phase})</li>"
            html += f"<li><strong>ፀሐይ መውጫ/መግቢያ (አዲስ አበባ)፦</strong> መውጫ {sun_rise} | መግቢያ {sun_set}</li>"
            html += "</ul>"

            synax_data = self.get_synax_data()
            synax_feasts = synax_data.get(month_name, {}).get(str(ed), [])
            annual, monthly = self.split_synax_entries(synax_feasts)
            if annual:
                html += "<h2>ዓመታዊ በዓላት</h2><ul>"
                for f in annual:
                    html += f"<li>{f}</li>"
                html += "</ul>"
            if monthly:
                html += "<h2>ወርኃዊ በዓላት</h2><ul>"
                for f in monthly:
                    html += f"<li>{f}</li>"
                html += "</ul>"

            self.show_html(f"{weekday}፣ {month_name} {ed}, {ey} ሙሉ መረጃ", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces progress through the current fast and upcoming events.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+u")
    @guarded_by_shortcut_setting("upcomingEvent")
    def script_upcomingEvent(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            meta = self.calculate_bahre_hasab(ey)
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

            progress = self.get_fasting_progress(ey, em, ed, meta, feasts)
            upcoming = self.get_next_events(ey, em, ed)

            msg = ""
            if progress:
                p_name, p_index, p_total = progress
                msg += f"በአሁኑ ሰዓት በ{p_name} ውስጥ ነዎት፤ ቀን {p_index} ከ{p_total}። "

            if not upcoming:
                ui.message(msg + "ቀጣይ በዓል ወይም ጾም መረጃ አልተገኘም።")
                return

            days_left, f_year, f_em, f_ed, f_label = upcoming[0]
            month_name = self.get_month_name(f_em)
            msg += f"ቀጣዩ፦ {f_label}፣ {month_name} {f_ed} ቀን {f_year} ዓ.ም። ከዛሬ ጀምሮ በ{days_left} ቀናት ውስጥ ይሆናል።"
            ui.message(msg)

            html = "<h1>ቀጣይ በዓላትና አጽዋማት</h1>"
            if progress:
                p_name, p_index, p_total = progress
                html += f"<p><strong>የአሁኑ ጾም፦</strong> {p_name}፣ ቀን {p_index} ከ{p_total}</p>"
            html += "<ul>"
            for days_left, y, m, d, label in upcoming:
                html += f"<li>{label}፦ {self.get_month_name(m)} {d} ቀን {y} ዓ.ም (በ{days_left} ቀናት ውስጥ)</li>"
            html += "</ul>"
            self.show_html("ቀጣይ በዓላትና አጽዋማት", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces the movable feasts and fasts for the current Ethiopian year.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+m")
    @guarded_by_shortcut_setting("movableFeasts")
    def script_movableFeasts(self, gesture):
        try:
            ey, _, _ = self.get_ethiopian_date()
            meta = self.calculate_bahre_hasab(ey)
            feasts = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])

            parts = []
            for name, date_obj in feasts.items():
                display_name = self.get_feast_display_name(name)
                parts.append(f"{display_name} {self.get_month_name(date_obj['m'])} {date_obj['d']}")
            msg = f"የ{ey} ዓ.ም ተንቀሳቃሽ በዓላትና አጽዋማት፦ " + "፣ ".join(parts)
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Announces the annual Synaxarium feasts for the current day.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+s")
    @guarded_by_shortcut_setting("readSynaxarium")
    def script_readSynaxarium(self, gesture):
        try:
            _, em, ed = self.get_ethiopian_date()
            month_name = self.get_month_name(em)
            synax_data = self.get_synax_data()
            synax_feasts = synax_data.get(month_name, {}).get(str(ed), [])
            annual, _monthly = self.split_synax_entries(synax_feasts)
            if annual:
                msg = "የዛሬ ዓመታዊ በዓላት፦ " + "፣ ".join(map(str, annual))
                ui.message(msg)
            else:
                ui.message("ለዛሬ የተመዘገበ ዓመታዊ በዓል የለም።")
        except Exception as e:
            ui.message("የበዓላት መረጃ ማንበብ አልተቻለም።")

    @scriptHandler.script(description="Announces the recurring monthly feasts for the current day.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+w")
    @guarded_by_shortcut_setting("readMonthlyFeasts")
    def script_readMonthlyFeasts(self, gesture):
        try:
            _, em, ed = self.get_ethiopian_date()
            month_name = self.get_month_name(em)
            synax_data = self.get_synax_data()
            synax_feasts = synax_data.get(month_name, {}).get(str(ed), [])
            _annual, monthly = self.split_synax_entries(synax_feasts)
            if monthly:
                msg = "የዛሬ ወርኃዊ በዓላት፦ " + "፣ ".join(map(str, monthly))
                ui.message(msg)
            else:
                ui.message("ለዛሬ የተመዘገበ ወርኃዊ በዓል የለም።")
        except Exception as e:
            ui.message("የበዓላት መረጃ ማንበብ አልተቻለም።")

    @scriptHandler.script(description="Opens a dialog to search the Synaxarium.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+k")
    @guarded_by_shortcut_setting("searchSynaxarium")
    def script_searchSynaxarium(self, gesture):
        wx.CallAfter(self._showSynaxariumSearchDialog)

    def _showSynaxariumSearchDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = SynaxariumSearchDialog(gui.mainFrame)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_synaxarium_search(dlg.queryCtrl.GetValue())
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_synaxarium_search(self, query):
        query = (query or "").strip()
        if not query:
            ui.message("እባክዎ የፍለጋ ቃል ያስገቡ።")
            return
        matches = self.find_synaxarium_matches(query)
        if not matches:
            ui.message(f"'{query}' የሚል ምንም ውጤት አልተገኘም።")
            return

        ui.message(f"'{query}' በ{len(matches)} ቦታዎች ተገኝቷል። ዝርዝሩ በመስኮቱ ውስጥ ይታያል።")
        html = f"<h1>የ'{query}' ፍለጋ ውጤት ({len(matches)} ውጤቶች)</h1><ul>"
        for month_name, day_num, entry in matches:
            html += f"<li>{month_name} {day_num}፦ {entry}</li>"
        html += "</ul>"
        self.show_html(f"'{query}' ፍለጋ ውጤት", html)

    @scriptHandler.script(description="Displays the yearly Bahre Hasab and Movable Feasts in a virtual window.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+y")
    @guarded_by_shortcut_setting("yearlyFeasts")
    def script_yearlyFeasts(self, gesture):
        try:
            ey, em, ed = self.get_ethiopian_date()
            weekday = self.get_weekday_name()
            now = datetime.datetime.now()
            meta = self.calculate_bahre_hasab(ey)
            chereka = self.get_serqe_chereka(meta['Abekte'], em, ed)
            zodiac = self.get_zodiac_sign(now.month, now.day)
            awde_negest = self.get_awde_negest_sign(now.month, now.day)

            html, meta, feasts = self.build_yearly_html(
                ey, today_context=(weekday, em, ed, ey, chereka, zodiac, awde_negest))
            self.show_html(f"የ{ey} መረጃ", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    # ============================================================
    # ISLAMIC SCRIPTS
    # ============================================================
    @scriptHandler.script(description="Announces the current Islamic (Hijri) date, weekday, and season context.",
                          category="Islamic Calendar", gesture="kb:control+shift+i")
    @guarded_by_shortcut_setting("islamicInfo")
    def script_islamicInfo(self, gesture):
        try:
            iy, im, id_ = self.get_islamic_date()
            weekday = self.get_islamic_weekday(iy, im, id_)
            month_name = self.get_islamic_month_name(im)
            events = self.get_islamic_event(iy, im, id_)

            msg = f"ዛሬ {weekday}፣ {month_name} {id_} ቀን {iy} ዓ.ሂ (Hijri) ነው። "
            if events:
                msg += "ወቅታዊ መረጃ፦ " + "፣ ".join(events) + "። "
            msg += "ማሳሰቢያ፦ ይህ በሒሳብ ስሌት ላይ የተመሠረተ ሂሳባዊ ቀን ሲሆን ከጨረቃ ምልከታ ጋር በ1-2 ቀናት ሊለያይ ይችላል።"
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Copies the current Islamic (Hijri) date to the clipboard.",
                          category="Islamic Calendar", gesture="kb:control+shift+b")
    @guarded_by_shortcut_setting("copyIslamicDate")
    def script_copyIslamicDate(self, gesture):
        try:
            iy, im, id_ = self.get_islamic_date()
            weekday = self.get_islamic_weekday(iy, im, id_)
            month_name = self.get_islamic_month_name(im)

            msg = f"{weekday}፣ {month_name} {id_} ቀን {iy} ዓ.ሂ"

            if api.copyToClip(msg):
                ui.message("የሂጅሪ ቀኑ ኮፒ ተደርጓል (Copied to clipboard)")
            else:
                ui.message("ኮፒ ማድረግ አልተቻለም (Failed to copy)")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Displays the current Islamic date and full year breakdown.",
                          category="Islamic Calendar", gesture="kb:control+alt+i")
    @guarded_by_shortcut_setting("islamicFullHtml")
    def script_islamicFullHtml(self, gesture):
        try:
            now = datetime.datetime.now()
            iy, im, id_ = self.get_islamic_date()
            g_date = now.date()
            ey, em, ed = self.get_ethiopian_date()

            html = self.build_islamic_html(iy, im, id_, g_date=g_date, ey=ey, em=em, ed=ed)
            html += self.build_islamic_year_html(iy)
            month_name = self.get_islamic_month_name(im)
            self.show_html(f"{month_name} {id_}, {iy} ዓ.ሂ ሙሉ መረጃ", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Opens a dialog to convert a Hijri date.",
                          category="Islamic Calendar", gesture="kb:control+shift+h")
    @guarded_by_shortcut_setting("searchIslamicDate")
    def script_searchIslamicDate(self, gesture):
        wx.CallAfter(self._showIslamicSearchDialog)

    def _showIslamicSearchDialog(self, year="", month="", day=""):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = IslamicSearchDialog(gui.mainFrame, year, month, day)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_islamic_search(
                    dlg.yearCtrl.GetValue(),
                    dlg.monthCtrl.GetValue(),
                    dlg.dayCtrl.GetValue()
                )
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_islamic_search(self, year_str, month_str, day_str):
        year_str = (year_str or "").strip()
        month_str = (month_str or "").strip()
        day_str = (day_str or "").strip()

        if not year_str or not month_str or not day_str:
            ui.message("እባክዎ ሁሉንም ሳጥኖች (ዓመት፣ ወር፣ ቀን) ያሟሉ።")
            return
        try:
            iy = int(year_str)
            im = int(month_str)
            id_ = int(day_str)
        except ValueError:
            ui.message("እባክዎ ትክክለኛ ቁጥሮች ያስገቡ።")
            return

        if iy < 1 or iy > 9999:
            ui.message("እባክዎ ዓመቱ ከ1 እስከ 9999 መሆን አለበት።")
            return
        if im < 1 or im > 12:
            ui.message("ወር ከ1 እስከ 12 ብቻ መሆን አለበት።")
            return

        try:
            month_length = self.get_islamic_month_length(iy, im)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
            return

        if id_ < 1 or id_ > month_length:
            ui.message(f"ለ{self.get_islamic_month_name(im)} ቀን ከ1 እስከ {month_length} ብቻ መሆን አለበት።")
            return

        try:
            g_date = self.islamic_to_gregorian(iy, im, id_)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
            return

        try:
            ey, em, ed = self.gregorian_to_ethiopian(g_date.year, g_date.month, g_date.day)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
            return

        weekday = self.get_islamic_weekday(iy, im, id_)
        month_name = self.get_islamic_month_name(im)
        eth_month_name = self.get_month_name(em)
        events = self.get_islamic_event(iy, im, id_)

        html = self.build_islamic_html(iy, im, id_, g_date=g_date, ey=ey, em=em, ed=ed)
        self.show_html(f"{month_name} {id_}, {iy} ዓ.ሂ ፍለጋ ውጤት", html)

        msg = f"{weekday}፣ {month_name} {id_} ቀን {iy} ዓ.ሂ (Hijri)። ተመጣጣኝ የግሪጎሪያን ቀን፦ {g_date.strftime('%Y-%m-%d')}። ተመጣጣኝ የኢትዮጵያ ቀን፦ {eth_month_name} {ed} ቀን {ey} ዓ.ም። "
        if events:
            msg += "ወቅታዊ መረጃ፦ " + "፣ ".join(events) + "። "
        ui.message(msg)

    # ============================================================
    # HEBREW SEARCH
    # ============================================================
    @scriptHandler.script(description="Opens a dialog to convert a Hebrew date.",
                          category="Hebrew Calendar", gesture="kb:control+shift+l")
    @guarded_by_shortcut_setting("searchHebrewDate")
    def script_searchHebrewDate(self, gesture):
        wx.CallAfter(self._showHebrewSearchDialog)

    def _showHebrewSearchDialog(self, year="", month="", day=""):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = HebrewSearchDialog(gui.mainFrame)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_hebrew_search(dlg.yearCtrl.GetValue(),
                                           dlg.monthCtrl.GetValue(),
                                           dlg.dayCtrl.GetValue())
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_hebrew_search(self, year_str, month_str, day_str):
        try:
            hy = int((year_str or "").strip())
            hm = int((month_str or "").strip())
            hd = int((day_str or "").strip())
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የቁጥር እሴቶችን ያስገቡ።")
            return

        try:
            jdn = self.hebrew_to_jdn(hy, hm, hd)
            g_date = self.jdn_to_gregorian(jdn)
            ey, em, ed = self.gregorian_to_ethiopian(g_date.year, g_date.month, g_date.day)
            self.show_full_date_search_result(ey, em, ed)
        except Exception as e:
            ui.message(f"የዕብራውያን ቀን ስሌት ስህተት፦ {e}")

    # ============================================================
    # PERIODIC SCRIPTS
    # ============================================================
    @scriptHandler.script(description="Opens a dialog to log a period start date and set cycle length.",
                          category="Periodic Calendar", gesture="kb:control+alt+p")
    @guarded_by_shortcut_setting("periodicSettings")
    def script_periodicSettings(self, gesture):
        wx.CallAfter(self._showPeriodicDialog)

    def _showPeriodicDialog(self):
        data = self.load_periodic_data()
        ey, em, ed = self.get_ethiopian_date()
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = PeriodicSettingsDialog(
                gui.mainFrame, year=ey, month=em, day=ed,
                cycle_len=data.get("cycle_len", 28), period_len=data.get("period_len", 5)
            )
            if dlg.ShowModal() == wx.ID_OK:
                self.process_periodic_settings(
                    dlg.yearCtrl.GetValue(), dlg.monthCtrl.GetValue(), dlg.dayCtrl.GetValue(),
                    dlg.cycleCtrl.GetValue(), dlg.periodCtrl.GetValue()
                )
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_periodic_settings(self, ey_str, em_str, ed_str, cycle_str, period_str):
        ey_str = (ey_str or "").strip()
        em_str = (em_str or "").strip()
        ed_str = (ed_str or "").strip()
        cycle_str = (cycle_str or "").strip()
        period_str = (period_str or "").strip()

        if not ey_str or not em_str or not ed_str:
            ui.message("እባክዎ ዓመት፣ ወር እና ቀን ያስገቡ።")
            return
        try:
            ey = int(ey_str); em = int(em_str); ed = int(ed_str)
        except ValueError:
            ui.message("እባክዎ ትክክለኛ ዓመት፣ ወር እና ቀን ቁጥሮች ያስገቡ።")
            return

        if ey < 1 or ey > 9999:
            ui.message("እባክዎ ዓመቱ ከ1 እስከ 9999 መሆን አለበት።")
            return
        if em < 1 or em > 13:
            ui.message("ወር ከ1 እስከ 13 ብቻ መሆን አለበት።")
            return

        try:
            month_length = self.get_month_length(ey, em)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
            return

        if ed < 1 or ed > month_length:
            ui.message(f"ለ{self.get_month_name(em)} ቀን ከ1 እስከ {month_length} ብቻ መሆን አለበት።")
            return

        try:
            cycle_len = int(cycle_str) if cycle_str else 28
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የዑደት ርዝመት ቁጥር ያስገቡ።")
            return
        if cycle_len < 15 or cycle_len > 60:
            ui.message("የዑደት ርዝመት ከ15 እስከ 60 ቀናት መካከል መሆን አለበት።")
            return

        try:
            period_len = int(period_str) if period_str else 5
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የወር አበባ ቆይታ ቁጥር ያስገቡ።")
            return
        if period_len < 1 or period_len > 15:
            ui.message("የወር አበባ ቆይታ ከ1 እስከ 15 ቀናት መካከል መሆን አለበት።")
            return

        try:
            g_date = self.eth_to_gregorian(ey, em, ed)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
            return

        if g_date > datetime.date.today():
            ui.message("የገባው ቀን ወደፊት ስለሆነ እባክዎ ያለፈ ቀን ያስገቡ።")
            return

        data = self.load_periodic_data()
        iso_date = g_date.isoformat()
        if iso_date not in data["periods"]:
            data["periods"].append(iso_date)
            data["periods"].sort()
        data["cycle_len"] = cycle_len
        data["period_len"] = period_len
        self.save_periodic_data(data)

        weekday = WEEKDAYS[g_date.weekday()]
        ui.message(f"{weekday}፣ {self.format_eth_label(g_date)} ({g_date.strftime('%Y-%m-%d')}) ተመዝግቧል።")

    @scriptHandler.script(description="Announces current menstrual cycle status.",
                          category="Periodic Calendar", gesture="kb:control+shift+p")
    @guarded_by_shortcut_setting("announcePeriodic")
    def script_announcePeriodic(self, gesture):
        try:
            data = self.load_periodic_data()
            periods = sorted(datetime.date.fromisoformat(d) for d in data.get("periods", []))
            if not periods:
                ui.message("የወር አበባ ዑደት መረጃ አልተገኘም። እባክዎ Control+Alt+P ተጭነው ያስመዝግቡ።")
                return

            cycle_len = data.get("cycle_len", 28)
            period_len = data.get("period_len", 5)
            last = periods[-1]
            today = datetime.date.today()

            cycle_day = (today - last).days + 1
            next_period_start = last + datetime.timedelta(days=cycle_len)
            days_until_next = (next_period_start - today).days

            ovulation_date = next_period_start - datetime.timedelta(days=14)
            fertile_start = ovulation_date - datetime.timedelta(days=5)
            fertile_end = ovulation_date + datetime.timedelta(days=1)

            if cycle_day <= period_len:
                status = "በወር አበባ ጊዜ ውስጥ ነዎት።"
            elif fertile_start <= today <= fertile_end:
                status = "በመራቢያ (የልጅ መውለጃ) ጊዜ ውስጥ ነዎት።"
            else:
                status = "በተለመደው የዑደት ቀናት ውስጥ ነዎት።"

            if days_until_next >= 0:
                next_msg = f"ቀጣዩ የወር አበባ የሚመጣው በ{days_until_next} ቀናት ውስጥ ነው። "
            else:
                next_msg = f"የሚጠበቀው ቀን ካለፈ {abs(days_until_next)} ቀናት ሆኖታል። "

            msg = f"የዑደት ቀን {cycle_day}። " + next_msg + status + " ሙሉ መረጃውን በመስኮቱ ውስጥ ይመልከቱ።"
            ui.message(msg)

            html = "<h1>የወር አበባ ዑደት መረጃ (Periodic Tracker)</h1>"
            html += f"<p><strong>የዑደትዎ ርዝመት፦</strong> {cycle_len} ቀናት</p>"
            html += f"<p><strong>የወር አበባ የሚቆይበት ጊዜ፦</strong> {period_len} ቀናት</p>"
            html += f"<p><strong>የመጨረሻው የተመዘገበ ቀን፦</strong> {WEEKDAYS[last.weekday()]}፣ {last.strftime('%Y-%m-%d')} ({self.format_eth_label(last)})</p>"
            html += f"<p><strong>የአሁኑ ዑደት ሁኔታ፦</strong> {status} (የዑደት ቀን {cycle_day})</p>"
            html += "<h2>የቀጣይ ዑደት ትንበያ</h2><ul>"
            html += f"<li><strong>ቀጣይ የወር አበባ የሚጀምርበት ግምታዊ ቀን፦</strong> {WEEKDAYS[next_period_start.weekday()]}፣ {next_period_start.strftime('%Y-%m-%d')} ({self.format_eth_label(next_period_start)})</li>"
            html += f"<li><strong>የመራቢያ ጊዜ (Fertile Window)፦</strong> {fertile_start.strftime('%Y-%m-%d')} ({self.format_eth_label(fertile_start)}) - {fertile_end.strftime('%Y-%m-%d')} ({self.format_eth_label(fertile_end)})</li>"
            html += f"<li><strong>የእንቁላል መውረጃ ግምታዊ ቀን (Ovulation)፦</strong> {ovulation_date.strftime('%Y-%m-%d')} ({self.format_eth_label(ovulation_date)})</li></ul>"

            if len(periods) >= 2:
                intervals = [(periods[i] - periods[i - 1]).days for i in range(1, len(periods))]
                avg_actual_cycle = sum(intervals) / len(intervals)
                html += f"<p><strong>ከተመዘገበው ታሪክ የተሰላ አማካይ ዑደት ርዝመት፦</strong> {avg_actual_cycle:.1f} ቀናት (ከ{len(intervals)} ዑደቶች)</p>"

            html += "<h2>የተመዘገቡ ቀናት</h2><ul>"
            for p in reversed(periods[-12:]):
                html += f"<li>{WEEKDAYS[p.weekday()]}፣ {p.strftime('%Y-%m-%d')} ({self.format_eth_label(p)})</li>"
            html += "</ul><p><em>ማሳሰቢያ፦ ይህ ትንበያ በአማካይ ስሌት ላይ የተመሠረተ ግምት ብቻ ሲሆን፣ የሕክምና ማረጋገጫ ሆኖ አያገለግልም።</em></p>"
            self.show_html("የወር አበባ ዑደት መረጃ", html)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Clears all saved menstrual cycle tracking data.",
                          category="Periodic Calendar", gesture="kb:control+alt+shift+p")
    @guarded_by_shortcut_setting("clearPeriodicData")
    def script_clearPeriodicData(self, gesture):
        try:
            self.save_periodic_data({"periods": [], "cycle_len": 28, "period_len": 5})
            ui.message("የወር አበባ ዑደት መረጃ በሙሉ ተሰርዟል (Periodic data cleared)።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    # ============================================================
    # PREGNANCY AND AGE CALCULATORS
    # ============================================================
    @scriptHandler.script(description="Calculates estimated due date, gestation, and trimester.",
                          category="Periodic Calendar", gesture="kb:control+alt+n")
    @guarded_by_shortcut_setting("calculatePregnancy")
    def script_calculatePregnancy(self, gesture):
        wx.CallAfter(self._showPregnancyDialog)

    def _showPregnancyDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = PregnancyCalculatorDialog(gui.mainFrame)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_pregnancy_calc(dlg.yearCtrl.GetValue(),
                                            dlg.monthCtrl.GetValue(),
                                            dlg.dayCtrl.GetValue())
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_pregnancy_calc(self, y_str, m_str, d_str):
        try:
            y = int((y_str or "").strip())
            m = int((m_str or "").strip())
            d = int((d_str or "").strip())
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የቁጥር እሴቶችን ያስገቡ።")
            return

        if m < 1 or m > 13:
            ui.message("ወር ከ1 እስከ 13 ብቻ መሆን አለበት።")
            return
        if abs(y) > 200000:
            ui.message("የተሳሳተ ዓመት።")
            return

        try:
            month_length = self.get_month_length(y, m)
            if d < 1 or d > month_length:
                ui.message("የተሳሳተ ቀን።")
                return

            lmp_jdn = self.ethiopian_to_jdn(y, m, d)
            edd_jdn = lmp_jdn + 280
            edd_ey, edd_em, edd_ed = self.jdn_to_ethiopian(edd_jdn)
            edd_greg = self.jdn_to_gregorian(edd_jdn)

            now = datetime.date.today()
            now_jdn = self.gregorian_to_jdn(now.year, now.month, now.day)
            elapsed = now_jdn - lmp_jdn

            if elapsed < 0:
                gestation = "-"
                trimester = "-"
            elif elapsed > 300:
                gestation = "አልፏል / ተወልዷል (Post-term)"
                trimester = "-"
            else:
                weeks = elapsed // 7
                days = elapsed % 7
                gestation = f"{weeks} ሳምንታት እና {days} ቀናት"
                if weeks < 13:
                    trimester = "1ኛ (First) Trimester"
                elif weeks < 27:
                    trimester = "2ኛ (Second) Trimester"
                else:
                    trimester = "3ኛ (Third) Trimester"

            html = f"<h3>የእርግዝና እና የወሊድ ጊዜ መገመቻ</h3>"
            html += f"<p><strong>የሚጠበቀው የወሊድ ቀን (EDD):</strong> {self.get_month_name(edd_em)} {edd_ed}, {edd_ey} ({edd_greg.strftime('%Y-%m-%d')})</p>"
            html += f"<p><strong>የእርግዝናው ዕድሜ:</strong> {gestation}</p>"
            html += f"<p><strong>የእርግዝና ደረጃ:</strong> {trimester}</p>"

            self.show_html("የወሊድ ጊዜ መገመቻ ውጤት", html)
            ui.message(f"የሚጠበቀው የወሊድ ቀን፦ {self.get_month_name(edd_em)} {edd_ed}፣ {edd_ey} ዓ.ም። ዝርዝሩ በመስኮቱ ውስጥ ይታያል።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    @scriptHandler.script(description="Calculates exact age in years, months, and days.",
                          category="Periodic Calendar", gesture="kb:control+shift+n")
    @guarded_by_shortcut_setting("calculateAge")
    def script_calculateAge(self, gesture):
        wx.CallAfter(self._showAgeDialog)

    def _showAgeDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = AgeCalculatorDialog(gui.mainFrame)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_age_calc(dlg.yearCtrl.GetValue(),
                                      dlg.monthCtrl.GetValue(),
                                      dlg.dayCtrl.GetValue())
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_age_calc(self, y_str, m_str, d_str):
        try:
            bY = int((y_str or "").strip())
            bM = int((m_str or "").strip())
            bD = int((d_str or "").strip())
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የቁጥር እሴቶችን ያስገቡ።")
            return

        try:
            if bM < 1 or bM > 13 or bD < 1 or bD > self.get_month_length(bY, bM):
                ui.message("የተሳሳተ ቀን።")
                return

            now = datetime.date.today()
            cY, cM, cD = self.gregorian_to_ethiopian(now.year, now.month, now.day)

            b_jdn = self.ethiopian_to_jdn(bY, bM, bD)
            c_jdn = self.ethiopian_to_jdn(cY, cM, cD)

            if b_jdn > c_jdn:
                ui.message("የትውልድ ቀን ወደፊት ሊሆን አይችልም።")
                return

            years = cY - bY
            anniv_day = min(bD, self.get_month_length(bY + years, bM))
            anniv_jdn = self.ethiopian_to_jdn(bY + years, bM, anniv_day)

            if anniv_jdn > c_jdn:
                years -= 1
                anniv_day = min(bD, self.get_month_length(bY + years, bM))
                anniv_jdn = self.ethiopian_to_jdn(bY + years, bM, anniv_day)

            months = 0
            curY = bY + years
            curM = bM
            cur_jdn = anniv_jdn

            for _ in range(13):
                nextM = curM + 1
                nextY = curY
                if nextM > 13:
                    nextM = 1
                    nextY += 1
                next_day = min(bD, self.get_month_length(nextY, nextM))
                next_jdn = self.ethiopian_to_jdn(nextY, nextM, next_day)
                if next_jdn > c_jdn:
                    break
                months += 1
                curY = nextY
                curM = nextM
                cur_jdn = next_jdn

            b_greg = self.eth_to_gregorian(bY, bM, bD)
            zodiac = self.get_zodiac_sign(b_greg.month, b_greg.day)
            awde = self.get_awde_negest_sign(b_greg.month, b_greg.day)

            html = f"<h3>ትክክለኛ ዕድሜ ማስያ</h3>"
            html += f"<p><strong>{years} ዓመታት፣ {months} ወራት፣ {c_jdn - cur_jdn} ቀናት</strong></p>"
            html += f"<p>ጠቅላላ የኑሮ ቀናት: {c_jdn - b_jdn}</p>"
            html += f"<p><strong>የኮከብ ቆጠራ (Zodiac):</strong> {zodiac}</p>"
            html += f"<p><strong>በዓውደ ነገሥት:</strong> {awde}</p>"

            self.show_html("ዕድሜ ማስያ ውጤት", html)
            ui.message(f"ዕድሜዎ፦ {years} ዓመት ከ{months} ወር ከ{c_jdn - cur_jdn} ቀን ነው። ዝርዝሩ በመስኮቱ ውስጥ ይታያል።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    # ============================================================
    # DATE SEARCH AND CONVERTER SCRIPTS
    # ============================================================
    @scriptHandler.script(description="Opens a dialog to search date, weekday, Bahre Hasab, and feast information.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+d")
    @guarded_by_shortcut_setting("searchDate")
    def script_searchDate(self, gesture):
        wx.CallAfter(self._showSearchDialog)

    def _showSearchDialog(self, year="", month="", day=""):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = DateSearchDialog(gui.mainFrame, year, month, day)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_date_search(
                    dlg.yearCtrl.GetValue(), dlg.monthCtrl.GetValue(), dlg.dayCtrl.GetValue()
                )
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_date_search(self, year_str, month_str, day_str):
        year_str = (year_str or "").strip()
        month_str = (month_str or "").strip()
        day_str = (day_str or "").strip()

        cur_ey, cur_em, cur_ed = self.get_ethiopian_date()

        ey = None
        if year_str:
            try:
                ey = int(year_str)
            except ValueError:
                ui.message("እባክዎ ትክክለኛ ዓመት ቁጥር ያስገቡ።")
                return
            if ey < 1 or ey > 9999:
                ui.message("እባክዎ ዓመቱ ከ1 እስከ 9999 መሆን አለበት።")
                return

        em = None
        if month_str:
            try:
                em = int(month_str)
            except ValueError:
                matched_month = self.match_month_name(month_str)
                if matched_month is None:
                    ui.message("እባክዎ ትክክለኛ የወር ቁጥር ወይም ስም ያስገቡ (ለምሳሌ 3 ወይም ኅዳር ወይም ህዳ ወይም Hidar)።")
                    return
                em = matched_month
            if em < 1 or em > 13:
                ui.message("ወር ከ1 እስከ 13 ብቻ መሆን አለበት።")
                return

        ed = None
        if day_str:
            try:
                ed = int(day_str)
            except ValueError:
                ui.message("እባክዎ ትክክለኛ ቀን ቁጥር ያስገቡ።")
                return

        if ed is not None:
            use_ey = ey if ey is not None else cur_ey
            use_em = em if em is not None else cur_em
            try:
                month_length = self.get_month_length(use_ey, use_em)
            except Exception as e:
                ui.message(f"ስህተት፦ {e}")
                return

            if ed < 1 or ed > month_length:
                ui.message(f"ለ{self.get_month_name(use_em)} ቀን ከ1 እስከ {month_length} ብቻ መሆን አለበት።")
                return
            self.show_full_date_search_result(use_ey, use_em, ed)
            return

        if em is not None:
            use_ey = ey if ey is not None else cur_ey
            self.show_month_search_result(use_ey, em)
            return

        use_ey = ey if ey is not None else cur_ey
        self.show_yearly_search_result(use_ey)

    @scriptHandler.script(description="Opens a dialog to convert a Gregorian date into an Ethiopian date.",
                          category="Ethiopian Calendar", gesture="kb:control+shift+g")
    @guarded_by_shortcut_setting("searchGregorianDate")
    def script_searchGregorianDate(self, gesture):
        wx.CallAfter(self._showGregorianSearchDialog)

    def _showGregorianSearchDialog(self):
        gui.mainFrame.prePopup()
        dlg = None
        try:
            dlg = GregorianSearchDialog(gui.mainFrame)
            if dlg.ShowModal() == wx.ID_OK:
                self.process_gregorian_search(
                    dlg.yearCtrl.GetValue(), dlg.monthCtrl.GetValue(), dlg.dayCtrl.GetValue()
                )
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")
        finally:
            if dlg:
                dlg.Destroy()
            gui.mainFrame.postPopup()

    def process_gregorian_search(self, year_str, month_str, day_str):
        year_str = (year_str or "").strip()
        month_str = (month_str or "").strip()
        day_str = (day_str or "").strip()

        if not year_str or not month_str or not day_str:
            ui.message("እባክዎ ሁሉንም ሳጥኖች (ዓመት፣ ወር፣ ቀን) ያሟሉ::")
            return
        try:
            gy = int(year_str); gm = int(month_str); gd = int(day_str)
        except ValueError:
            ui.message("እባክዎ ትክክለኛ የቁጥር እሴቶችን ያስገቡ።")
            return

        try:
            target_g_date = datetime.date(gy, gm, gd)
        except ValueError:
            ui.message("የተሳሳተ የግሪጎሪያን ቀን አስገብተዋል። እባክዎ ያረጋግጡ።")
            return

        ey, em, ed = self.gregorian_to_ethiopian(gy, gm, gd)
        self.show_full_date_search_result(ey, em, ed)

    def show_yearly_search_result(self, ey):
        try:
            html, meta, feasts = self.build_yearly_html(ey)
            self.show_html(f"የ{ey} ዓ.ም መረጃ (ፍለጋ)", html)
            ui.message(f"የ{ey} ዓ.ም መረጃ ተገኝቷል፤ በመስኮቱ ውስጥ ይመልከቱ።")
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    def show_month_search_result(self, ey, em):
        try:
            month_name = self.get_month_name(em)
            month_length = self.get_month_length(ey, em)
            meta = self.calculate_bahre_hasab(ey)
            feasts_this_year = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
            synax_data = self.get_synax_data()

            month_start_g = self.eth_to_gregorian(ey, em, 1)
            month_end_g = self.eth_to_gregorian(ey, em, month_length)

            start_day_num = self.ethiopian_day_of_year(em, 1)
            end_day_num = self.ethiopian_day_of_year(em, month_length)

            month_movable = []
            for name, date_obj in feasts_this_year.items():
                dnum = (date_obj["m"] - 1) * 30 + date_obj["d"]
                if dnum and start_day_num <= dnum <= end_day_num:
                    display_name = self.get_feast_display_name(name)
                    month_movable.append((dnum, display_name))
            month_movable.sort()

            holidays = self.get_fdre_holidays(ey)
            month_holidays = []
            for category_key, category_label in (
                ("celebrated", "የተከበረ ብሔራዊ በዓል"),
                ("memorial", "የመታሰቢያ ቀን"),
                ("religious", "የሃይማኖት በዓል"),
            ):
                for h in holidays[category_key]:
                    h_ey, h_em, h_ed = self.gregorian_to_ethiopian(
                        h['gregorian'].year, h['gregorian'].month, h['gregorian'].day
                    )
                    if h_ey == ey and h_em == em:
                        month_holidays.append((h_ed, h['name_am'], category_label))
            month_holidays.sort()

            season_segments = []
            current_seg = None
            for d in range(1, month_length + 1):
                fasting = self.get_fasting_season(ey, em, d, meta, feasts_this_year)
                liturgical = self.get_liturgical_season(ey, em, d, meta, feasts_this_year)
                key = (fasting, liturgical)
                if current_seg and current_seg[2] == key:
                    current_seg = (current_seg[0], d, key)
                else:
                    if current_seg:
                        season_segments.append(current_seg)
                    current_seg = (d, d, key)
            if current_seg:
                season_segments.append(current_seg)

            html = f"<h1>{month_name} {ey} ዓ.ም</h1>"
            html += f"<p>ከ{month_start_g.strftime('%Y-%m-%d')} እስከ {month_end_g.strftime('%Y-%m-%d')} ({month_length} ቀናት)</p>"

            html += "<h2>የወቅትና የአጽዋም ለውጦች</h2><ul>"
            for seg_start, seg_end, (fasting, liturgical) in season_segments:
                range_label = f"ቀን {seg_start}" if seg_start == seg_end else f"ከቀን {seg_start} - {seg_end}"
                html += f"<li>{range_label}፦ የአጽዋም ዘመን፦ {fasting}፤ የቤተክርስቲያን ዘመን፦ {liturgical}</li>"
            html += "</ul>"

            if month_movable:
                html += "<h2>በዚህ ወር ውስጥ ያሉ ተንቀሳቃሽ በዓላት</h2><ul>"
                for dnum, name in month_movable:
                    em_d, ed_d = self.day_of_year_to_month_day(dnum)
                    html += f"<li>{self.get_month_name(em_d)} {ed_d}፦ {name}</li>"
                html += "</ul>"

            if month_holidays:
                html += "<h2>በዚህ ወር ውስጥ ያሉ ብሔራዊ በዓላት</h2><ul>"
                for ed_, name_am, category_label in month_holidays:
                    html += f"<li>{month_name} {ed_}፦ {name_am} ({category_label})</li>"
                html += "</ul>"

            html += "<h2>የዕለት ዝርዝር</h2><ul>"
            for d in range(1, month_length + 1):
                g_date = self.eth_to_gregorian(ey, em, d)
                weekday = WEEKDAYS[g_date.weekday()]
                entries = synax_data.get(month_name, {}).get(str(d), [])
                annual, _monthly = self.split_synax_entries(entries)
                html += f"<li>{weekday}፣ {month_name} {d} ({g_date.strftime('%Y-%m-%d')})"
                if annual:
                    html += "፦ " + "፣ ".join(annual)
                html += "</li>"
            html += "</ul>"

            self.show_html(f"{month_name} {ey} ዓ.ም መረጃ (ፍለጋ)", html)

            msg = f"{month_name} {ey} ዓ.ም፦ ከ{month_start_g.strftime('%Y-%m-%d')} እስከ {month_end_g.strftime('%Y-%m-%d')}፣ {month_length} ቀናት። "
            if month_movable:
                msg += "ተንቀሳቃሽ በዓላት፦ " + "፣ ".join(name for _, name in month_movable) + "። "
            if month_holidays:
                msg += "ብሔራዊ በዓላት፦ " + "፣ ".join(name_am for _, name_am, _ in month_holidays) + "። "
            msg += "ዝርዝሩ በመስኮቱ ውስጥ ይታያል።"
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")

    def show_full_date_search_result(self, ey, em, ed):
        try:
            g_date = self.eth_to_gregorian(ey, em, ed)
            weekday = WEEKDAYS[g_date.weekday()]
            meta = self.calculate_bahre_hasab(ey)
            feasts_this_year = self.calculate_movable_feasts(meta['MebajaHamer'], meta['Metqe'])
            chereka = self.get_serqe_chereka(meta['Abekte'], em, ed)
            fasting = self.get_fasting_season(ey, em, ed, meta, feasts_this_year)
            liturgical = self.get_liturgical_season(ey, em, ed, meta, feasts_this_year)
            climatic = self.get_climatic_season(em, ed)
            zodiac = self.get_zodiac_sign(g_date.month, g_date.day)
            awde_negest = self.get_awde_negest_sign(g_date.month, g_date.day)
            month_name = self.get_month_name(em)

            moon_phase = self.get_moon_phase_text(chereka)
            sun_rise, sun_set = self.get_addis_sun_times(g_date)

            jdn = self.gregorian_to_jdn(g_date.year, g_date.month, g_date.day)
            jy, jm, jd = self.jdn_to_julian(jdn)
            hy, hm, hd = self.jdn_to_hebrew(jdn)
            is_heb_leap = self.hebrew_leap(hy)
            heb_month_name = self.get_hebrew_month_name(hm, is_heb_leap)
            heb_events = self.get_hebrew_event(hy, hm, hd, is_heb_leap)

            target_label = f"{month_name} {ed}"
            matched_movable = []
            for name, date_obj in feasts_this_year.items():
                if f"{self.get_month_name(date_obj['m'])} {date_obj['d']}" == target_label:
                    matched_movable.append(self.get_feast_display_name(name))

            html = f"<h1>{weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም</h1>"
            html += f"<p>ተመጣጣኝ የግሪጎሪያን ቀን፦ {g_date.strftime('%Y-%m-%d')}</p>"
            html += f"<p>ተመጣጣኝ የጁሊያን ቀን፦ {jy}-{jm:02d}-{jd:02d}</p>"
            html += f"<p>ተመጣጣኝ የዕብራውያን ቀን፦ {heb_month_name} {hd} ቀን {hy}</p>"

            html += "<h2>የወቅቱ መረጃ</h2><ul>"
            html += f"<li><strong>ወቅት (Season)፦</strong> {climatic}</li>"
            html += f"<li><strong>የአጽዋም ዘመን፦</strong> {fasting}</li>"
            html += f"<li><strong>የቤተክርስቲያን ዘመን፦</strong> {liturgical}</li>"
            html += f"<li><strong>የኮከብ ቆጠራ (Zodiac)፦</strong> {zodiac}</li>"
            html += f"<li><strong>በዓውደ ነገሥት፦</strong> {awde_negest}</li>"
            if heb_events:
                html += f"<li><strong>የዕብራውያን በዓል፦</strong> {', '.join(heb_events)}</li>"
            html += "</ul>"

            html += "<h2>የባሕረ ሐሳብ መረጃ</h2><ul>"
            html += f"<li><strong>ዓመተ ዓለም፦</strong> {meta['AmeteAlem']}</li>"
            html += f"<li><strong>ወንጌላዊ፦</strong> {meta['Wengelawi']}</li>"
            html += f"<li><strong>ጥንተ ቀመር፦</strong> {meta['TinteQemer']}</li>"
            html += f"<li><strong>መደብ፦</strong> {meta['Medeb']}</li>"
            html += f"<li><strong>ወንበር፦</strong> {meta['Wenber']}</li>"
            html += f"<li><strong>መጥቅዕ፦</strong> {meta['Metqe']}</li>"
            html += f"<li><strong>አበቅቴ፦</strong> {meta['Abekte']}</li>"
            html += f"<li><strong>መባጃ ሐመር፦</strong> {meta['MebajaHamer']}</li>"
            html += f"<li><strong>ተውሳክ፦</strong> {meta['Tewsak']}</li>"
            html += f"<li><strong>የዕለቱ ሰርቀ ጨረቃ፦</strong> {chereka} ({moon_phase})</li>"
            html += f"<li><strong>ፀሐይ መውጫ/መግቢያ (አዲስ አበባ)፦</strong> መውጫ {sun_rise} | መግቢያ {sun_set}</li>"
            html += "</ul>"

            if matched_movable:
                html += "<h2>ተንቀሳቃሽ በዓል፦</h2><ul>"
                for name in matched_movable:
                    html += f"<li>{name}</li>"
                html += "</ul>"

            synax_data = self.get_synax_data()
            synax_feasts = synax_data.get(month_name, {}).get(str(ed), [])
            annual, monthly = self.split_synax_entries(synax_feasts)
            if annual:
                html += "<h2>ዓመታዊ በዓላት</h2><ul>"
                for f in annual:
                    html += f"<li>{f}</li>"
                html += "</ul>"
            if monthly:
                html += "<h2>ወርኃዊ በዓላት</h2><ul>"
                for f in monthly:
                    html += f"<li>{f}</li>"
                html += "</ul>"

            html += f"<h2>የ{ey} ዓ.ም ተንቀሳቃሽ በዓላትና አጽዋማት</h2><ul>"
            for name, date_obj in feasts_this_year.items():
                display_name = self.get_feast_display_name(name)
                html += f"<li><strong>{display_name}:</strong> {self.get_month_name(date_obj['m'])} {date_obj['d']}</li>"
            html += "</ul>"

            self.show_html(f"{month_name} {ed}, {ey} ፍለጋ ውጤት", html)

            msg = f"{weekday}፣ {month_name} {ed} ቀን {ey} ዓ.ም። የጨረቃ ዕድሜ {chereka} ነው። "
            msg += f"ወቅት፦ {climatic}። የአጽዋም ዘመን፦ {fasting}። የቤተክርስቲያን ዘመን፦ {liturgical}። የኮከብ ቆጠራ፦ {zodiac}። በዓውደ ነገሥት፦ {awde_negest}።"
            if matched_movable:
                msg += " የተንከሳቃሽ በዓል፦ " + "፣ ".join(matched_movable) + "።"
            ui.message(msg)
        except Exception as e:
            ui.message(f"ስህተት፦ {e}")