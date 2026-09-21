# Ethiopian Bahre Hasab and Calendar — NVDA Add-on

An NVDA screen reader add-on that provides comprehensive Ethiopian calendar
information, along with the Bahre Hasab (the traditional Ethiopian
computational calendar), daily church readings, and several related tools.

The add-on is designed for accessibility first: every result is presented as a
navigable HTML page using headings, lists, and tables, so NVDA users can move
around quickly with **H**, **T**, and **L** and use the Elements List with
**NVDA+F7**.

## Features

### Ethiopian Calendar
- Current Ethiopian date, weekday, and Bahre Hasab
- Bahre Hasab detail: Amete Alem, Wengelawi, Tinte Qemer, Medeb, Wenber,
  Metqe, Abekte, Mebaja Hamer, Tewsak
- Movable feasts and fasts — Nineveh, Great Lent, Hosanna, Crucifixion,
  Resurrection, Ascension, Pentecost, Apostles' Fast, Fast of Salvation
- Great Lent weekly names — Zewerede, Qidist, Mikurab, Metsagu,
  Debre Zeyit, Gebre Hier, Nikodimos, Hosanna
- Fasting seasons, liturgical seasons, and climatic seasons
- Lunar age (Serqe Chereka) and moon phase
- Zodiac signs and Awde Negest signs
- Conversion between Ethiopian, Gregorian, Hebrew, Hijri, and Julian calendars
- Ethiopian local time and Bahre Hasab *kekros* time
- Yearly summary page

### Gitsawe (Daily Church Readings)
- The three services — Morning (ዘነግህ), Eucharist (ዘቅዳሴ), Evening (ዘሠርክ)
- Psalms, epistles, Acts, and Gospel citations with the full Bible passage
  inlined for every citation
- Search across the Gitsawe dataset by book, incitement, or commemoration

### Synaxarium
- Annual and monthly feasts of saints
- Lookup by Ethiopian date
- Free-text search across the entire Synaxarium

### National (FDRE) Holidays
- Celebrated national holidays, memorial days, and religious holidays
- Islamic holidays (Mawlid, Eid al-Fitr, Eid al-Adha) with an accuracy note

### Islamic (Hijri) Calendar
- Current Hijri date and weekday
- Hijri events — Ashura, Mawlid, Isra and Mi'raj, Ramadan,
  Eid al-Fitr, Eid al-Adha, Hajj season
- Full year breakdown with month lengths
- Conversion between Hijri and Ethiopian/Gregorian dates

### Hebrew Calendar
- Hebrew date conversion
- Hebrew holidays — Rosh Hashanah, Yom Kippur, Sukkot, Hanukkah,
  Purim, Passover, Shavuot, and more

### Planning and Agenda
- Ethiopian planning workspace with climate / fasting / liturgical
  season filtering
- Full agenda page with tasks and personal events
- Export to CSV, TSV, JSON, Markdown, HTML, and iCal
- Import plans from CSV, TSV, or JSON

### Health Tools
- Menstrual cycle tracker with ovulation and fertile window prediction
- Pregnancy due-date calculator
- Exact age calculator in Ethiopian years, months, and days

### Search and Conversion
- Ethiopian date search (by year, month, and day)
- Gregorian to Ethiopian conversion
- Hijri to Ethiopian/Gregorian conversion
- Hebrew to Ethiopian/Gregorian conversion
- Synaxarium and Gitsawe search

### Accessibility
- Fully navigable HTML output for every report
- Per-shortcut enable / disable settings
- Amharic and English interface

## Installation

### From the NVDA Add-on Store (recommended)
1. In NVDA, open the NVDA menu with **NVDA+N**.
2. Choose **Tools → Add-on Store**.
3. Search for *Ethiopian* or *Bahre*.
4. Select the add-on and click **Install**.
5. Restart NVDA when prompted.

### From a release file
1. Download the latest `.nvda-addon` file from the
   [Releases page](https://github.com/mesiworkisha-glitch/ethiopian-bahre-hasab/releases).
2. In File Explorer, focus the file and press **Enter**, or double-click it.
3. NVDA will ask whether to install the add-on. Confirm.
4. Restart NVDA when prompted.

## Shortcuts

All shortcuts can be disabled individually from the add-on's menu under
**NVDA menu → Ethiopian Calendar → Shortcut settings**.

### Ethiopian Calendar
| Shortcut | Action |
|---|---|
| `Ctrl+Shift+E` | Announce current Ethiopian date and full Bahre Hasab |
| `Ctrl+Shift+F` | Show full date information in a window |
| `Ctrl+Shift+A` | Show national holidays and today's holiday status |
| `Ctrl+Shift+T` | Announce Ethiopian local time |
| `Ctrl+Shift+Q` | Announce Bahre Hasab *kekros* time |
| `Ctrl+Shift+C` | Copy the current Ethiopian date to the clipboard |
| `Ctrl+Shift+U` | Announce progress through the current fast and upcoming events |
| `Ctrl+Shift+M` | Announce the year's movable feasts |
| `Ctrl+Shift+S` | Announce today's annual Synaxarium feasts |
| `Ctrl+Shift+W` | Announce today's monthly feasts |
| `Ctrl+Shift+K` | Search the Synaxarium |
| `Ctrl+Shift+Alt+S` | Search Synaxarium by Ethiopian date |
| `Ctrl+Shift+Y` | Show the full year's Bahre Hasab and movable feasts |
| `Ctrl+Shift+D` | Search an Ethiopian date |
| `Ctrl+Shift+G` | Convert a Gregorian date to Ethiopian |

### Gitsawe
| Shortcut | Action |
|---|---|
| `Ctrl+Shift+R` | Show today's Gitsawe readings |
| `Ctrl+Alt+R` | Search the Gitsawe dataset |

### Islamic Calendar
| Shortcut | Action |
|---|---|
| `Ctrl+Shift+I` | Announce current Hijri date |
| `Ctrl+Alt+I` | Show full Hijri year information |
| `Ctrl+Shift+H` | Convert a Hijri date |
| `Ctrl+Shift+B` | Copy the current Hijri date |

### Hebrew Calendar
| Shortcut | Action |
|---|---|
| `Ctrl+Shift+L` | Convert a Hebrew date |

### Planning and Agenda
| Shortcut | Action |
|---|---|
| `Ctrl+Alt+Y` | Open the planning workspace |
| `Ctrl+Alt+A` | Open the agenda launcher |
| `Ctrl+Shift+Alt+A` | Show the agenda as an HTML page |

### Health Tools
| Shortcut | Action |
|---|---|
| `Ctrl+Alt+P` | Configure menstrual cycle settings |
| `Ctrl+Shift+P` | Announce current cycle status |
| `Ctrl+Alt+Shift+P` | Clear all menstrual cycle data |
| `Ctrl+Alt+N` | Calculate pregnancy due date |
| `Ctrl+Shift+N` | Calculate age |

## Requirements

- NVDA 2019.3 or later

## Data files

The add-on uses several data files bundled inside the package:
- `synaxarium_feasts.json` — the Synaxarium of saints
- `gitsawe-master.json` — the daily Gitsawe dataset
- `gitsawe-structure.json` — the structural layout of the Gitsawe
- `gitsawe-corrections.json` — verse-range corrections for citations
- `80-weahadu.json` — the Ethiopian Bible text used for inlined passages

## Reporting issues

Please report bugs or request features at:
https://github.com/mesiworkisha-glitch/ethiopian-bahre-hasab/issues

When reporting a bug, please include:
- NVDA version
- The add-on version
- Steps to reproduce the problem
- The exact message NVDA announced, if any

## License

This add-on is released under the **GNU General Public License v2.0**.
See the [LICENSE](LICENSE) file for details.

## Author

**Meseret Worku Alemu**
- GitHub: [@mesiworkisha-glitch](https://github.com/mesiworkisha-glitch)