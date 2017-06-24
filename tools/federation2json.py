#!/usr/bin/env python3

"""
usage:
federation2json.py out_filename.json

This will scrape all instances known at https://instances.mastodon.xyz/instances.json
for about info and contact info, and put the results in a
.json of your choosing.

"""
#shorten run time when testing. You can also set the environ variable "TEST"
TEST_ONLY = False

"""
Randomize to spread out the load of many people using tool at once.
There's not much I can do about the Mastodon.xyz GET, but I can at least
reduce the pinging of an individual server to 100/20min or approx
surge of 10 hits in a minute if 100 crazy people run buildall.sh at the exact same time
"""
RANDOMIZE = True
THREADS_MAX = 1 # jack it up to 50 for faster download
DEFAULT_MASTER = 'https://instances.mastodon.xyz/instances.json'
#DEFAULT_MASTER = 'https://upsided.github.io/instances.json'
REQUEST_TIMEOUT = 20.0

from bs4 import BeautifulSoup, CData, FeatureNotFound   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os, re
import random
import json
import time
import threading, queue

PARSER = 'lxml' # not much difference IMO, but nerds like it, so
PARSER = 'html.parser' # Actually there is a difference: lxml deletes my data

H5PARSER = 'html5lib' # "html5lib" advertises as a complete and lenient parser that produces valid HTML5

try:
    s = BeautifulSoup("Test", PARSER)
except FeatureNotFound:
    eprint("Couldn't find '%s', using builtin parser for HTML" % PARSER)
    PARSER = 'html.parser' 

try:
    s = BeautifulSoup("Test", H5PARSER)
except FeatureNotFound:
    eprint("Couldn't find '%s', using builtin parser for HTML 5" % H5PARSER)
    H5PARSER = 'html.parser' 
    
languageMap = {'de': {'english': 'German', 'native': 'Deutsch'},
 'en': {'english': 'English', 'native': 'English'},
 'es': {'english': 'Spanish', 'native': 'Español'},
 'fr': {'english': 'French', 'native': 'Français'},
 'it': {'english': 'Italian', 'native': 'Italiano'},
 'nl': {'english': 'Dutch', 'native': 'Nederlands'},
 'ja': {'english': 'Japanese', 'native': '日本語'},
 'pl': {'english': 'Polish', 'native': 'Polski'},
 'ru': {'english': 'Russian', 'native': 'Русский'},
 'ceb': {'english': 'Sinugboanong Binisaya', 'native': 'Sinugboanong Binisaya'},
 'sv': {'english': 'Swedish', 'native': 'Svenska'},
 'vi': {'english': 'Vietnamese', 'native': 'Tiếng Việt'},
 'war': {'english': 'Winaray', 'native': 'Winaray'},
 'ar': {'english': 'Arabic', 'native': 'العربية'},
 'az': {'english': 'Azerbaijani', 'native': 'Azərbaycanca'},
 'bg': {'english': 'Bulgarian', 'native': 'Български'},
 'nan': {'english': 'Bân-lâm-gú', 'native': 'Bân-lâm-gú'},
 'be': {'english': 'Belarusian', 'native': 'Беларуская'},
 'ca': {'english': 'Catalan', 'native': 'Català'},
 'cs': {'english': 'Czech', 'native': 'Čeština'},
 'da': {'english': 'Danish', 'native': 'Dansk'},
 'et': {'english': 'Estonian', 'native': 'Eesti'},
 'el': {'english': 'Greek', 'native': 'Ελληνικά'},
 'eo': {'english': 'Esperanto', 'native': 'Esperanto'},
 'eu': {'english': 'Basque', 'native': 'Euskara'},
 'fa': {'english': 'Persian (Farsi)', 'native': 'فارسی'},
 'gl': {'english': 'Galician', 'native': 'Galego'},
 'ko': {'english': 'Korean', 'native': '한국어'},
 'hy': {'english': 'Armenian', 'native': 'Հայերեն'},
 'hi': {'english': 'Hindi', 'native': 'हिन्दी'},
 'hr': {'english': 'Croatian', 'native': 'Hrvatski'},
 'id': {'english': 'Indonesian', 'native': 'Bahasa Indonesia'},
 'he': {'english': 'Hebrew', 'native': 'עברית'},
 'ka': {'english': 'Georgian', 'native': 'ქართული'},
 'la': {'english': 'Latin', 'native': 'Latina'},
 'lt': {'english': 'Lithuanian', 'native': 'Lietuvių'},
 'hu': {'english': 'Hungarian', 'native': 'Magyar'},
 'ms': {'english': 'Malay', 'native': 'Bahasa Melayu'},
 'min': {'english': 'Bahaso Minangkabau', 'native': 'Bahaso Minangkabau'},
 'no': {'english': 'Norwegian', 'native': 'Norsk'},
 'nb': {'english': 'Norwegian Bokmål', 'native': 'Bokmål'},
 'nn': {'english': 'Norwegian Nynorsk', 'native': 'Nynorsk'},
 'ce': {'english': 'Chechen', 'native': 'Нохчийн'},
 'uz': {'english': 'Uzbek', 'native': 'Oʻzbekcha/Ўзбекча'},
 'pt': {'english': 'Portuguese', 'native': 'Português'},
 'kk': {'english': 'Kazakh', 'native': 'Қазақша/Qazaqşa/قازاقشا'},
 'ro': {'english': 'Romanian', 'native': 'Română'},
 'sk': {'english': 'Slovak', 'native': 'Slovenčina'},
 'sl': {'english': 'Slovene', 'native': 'Slovenščina'},
 'sr': {'english': 'Serbian', 'native': 'Српски/Srpski'},
 'sh': {'english': 'Srpskohrvatski/Српскохрватски', 'native': 'Srpskohrvatski/Српскохрватски'},
 'fi': {'english': 'Finnish', 'native': 'Suomi'},
 'th': {'english': 'Thai', 'native': 'ภาษาไทย'},
 'tr': {'english': 'Turkish', 'native': 'Türkçe'},
 'uk': {'english': 'Ukrainian', 'native': 'Українська'},
 'ur': {'english': 'Urdu', 'native': 'اردو'},
 'vo': {'english': 'Volapük', 'native': 'Volapük'},
 'zh': {'english': 'Chinese', 'native': '中文'},
 'af': {'english': 'Afrikaans', 'native': 'Afrikaans'},
 'gsw': {'english': 'Alemannisch', 'native': 'Alemannisch'},
 'am': {'english': 'Amharic', 'native': 'አማርኛ'},
 'an': {'english': 'Aragonese', 'native': 'Aragonés'},
 'ast': {'english': 'Asturianu', 'native': 'Asturianu'},
 'bn': {'english': 'Bengali', 'native': 'বাংলা'},
 'map-x-bms': {'english': 'Basa Banyumasan', 'native': 'Basa Banyumasan'},
 'ba': {'english': 'Bashkir', 'native': 'Башҡортса'},
 'bpy': {'english': 'বিষ্ণুপ্রিয়া মণিপুরী', 'native': 'বিষ্ণুপ্রিয়া মণিপুরী'},
 'bar': {'english': 'Boarisch', 'native': 'Boarisch'},
 'bs': {'english': 'Bosnian', 'native': 'Bosanski'},
 'br': {'english': 'Breton', 'native': 'Brezhoneg'},
 'cv': {'english': 'Chuvash', 'native': 'Чӑвашла'},
 'fo': {'english': 'Faroese', 'native': 'Føroyskt'},
 'fy': {'english': 'Western Frisian', 'native': 'Frysk'},
 'ga': {'english': 'Irish', 'native': 'Gaeilge'},
 'gd': {'english': 'Scottish Gaelic', 'native': 'Gàidhlig'},
 'gu': {'english': 'Gujarati', 'native': 'ગુજરાતી'},
 'hsb': {'english': 'Hornjoserbsce', 'native': 'Hornjoserbsce'},
 'io': {'english': 'Ido', 'native': 'Ido'},
 'ilo': {'english': 'Ilokano', 'native': 'Ilokano'},
 'ia': {'english': 'Interlingua', 'native': 'Interlingua'},
 'os': {'english': 'Ossetian', 'native': 'Ирон æвзаг'},
 'is': {'english': 'Icelandic', 'native': 'Íslenska'},
 'jv': {'english': 'Javanese', 'native': 'Basa Jawa'},
 'kn': {'english': 'Kannada', 'native': 'ಕನ್ನಡ'},
 'ht': {'english': 'Haitian', 'native': 'Kreyòl Ayisyen'},
 'ku': {'english': 'Kurdish', 'native': 'Kurdî'},
 'ckb': {'english': 'کوردیی ناوەندی', 'native': 'کوردیی ناوەندی'},
 'ky': {'english': 'Kyrgyz', 'native': 'Кыргызча'},
 'mjr': {'english': 'Кырык Мары', 'native': 'Кырык Мары'},
 'lv': {'english': 'Latvian', 'native': 'Latviešu'},
 'lb': {'english': 'Luxembourgish', 'native': 'Lëtzebuergesch'},
 'li': {'english': 'Limburgish', 'native': 'Limburgs'},
 'lmo': {'english': 'Lumbaart', 'native': 'Lumbaart'},
 'mai': {'english': 'मैथिली', 'native': 'मैथिली'},
 'mk': {'english': 'Macedonian', 'native': 'Македонски'},
 'mg': {'english': 'Malagasy', 'native': 'Malagasy'},
 'ml': {'english': 'Malayalam', 'native': 'മലയാളം'},
 'mr': {'english': 'Marathi (Marāṭhī)', 'native': 'मराठी'},
 'arz': {'english': 'مصرى', 'native': 'مصرى'},
 'mzn': {'english': 'مازِرونی', 'native': 'مازِرونی'},
 'mn': {'english': 'Mongolian', 'native': 'Монгол'},
 'my': {'english': 'Burmese', 'native': 'မြန်မာဘာသာ'},
 'new': {'english': 'नेपाल भाषा', 'native': 'नेपाल भाषा'},
 'ne': {'english': 'Nepali', 'native': 'नेपाली'},
 'nap': {'english': 'Nnapulitano', 'native': 'Nnapulitano'},
 'oc': {'english': 'Occitan', 'native': 'Occitan'},
 'or': {'english': 'Oriya', 'native': 'ଓଡି଼ଆ'},
 'pa': {'english': '(Eastern) Punjabi', 'native': 'ਪੰਜਾਬੀ (ਗੁਰਮੁਖੀ)'},
 'pnb': {'english': 'پنجابی (شاہ مکھی)', 'native': 'پنجابی (شاہ مکھی)'},
 'pms': {'english': 'Piemontèis', 'native': 'Piemontèis'},
 'nds': {'english': 'Plattdüütsch', 'native': 'Plattdüütsch'},
 'qu': {'english': 'Quechua', 'native': 'Runa Simi'},
 'cy': {'english': 'Welsh', 'native': 'Cymraeg'},
 'sa': {'english': 'Sanskrit (Saṁskṛta)', 'native': 'संस्कृतम्'},
 'sah': {'english': 'Саха Тыла', 'native': 'Саха Тыла'},
 'sco': {'english': 'Scots', 'native': 'Scots'},
 'sq': {'english': 'Albanian', 'native': 'Shqip'},
 'scn': {'english': 'Sicilianu', 'native': 'Sicilianu'},
 'si': {'english': 'Sinhalese', 'native': 'සිංහල'},
 'su': {'english': 'Sundanese', 'native': 'Basa Sunda'},
 'sw': {'english': 'Swahili', 'native': 'Kiswahili'},
 'tl': {'english': 'Tagalog', 'native': 'Tagalog'},
 'ta': {'english': 'Tamil', 'native': 'தமிழ்'},
 'tt': {'english': 'Tatar', 'native': 'Татарча/Tatarça'},
 'te': {'english': 'Telugu', 'native': 'తెలుగు'},
 'tg': {'english': 'Tajik', 'native': 'Тоҷикӣ'},
 'azb': {'english': 'تۆرکجه', 'native': 'تۆرکجه'},
 'bug': {'english': 'ᨅᨔ ᨕᨙᨁᨗ/Basa Ugi', 'native': 'ᨅᨔ ᨕᨙᨁᨗ/Basa Ugi'},
 'vec': {'english': 'Vèneto', 'native': 'Vèneto'},
 'wa': {'english': 'Walloon', 'native': 'Walon'},
 'yi': {'english': 'Yiddish', 'native': 'ייִדיש'},
 'yo': {'english': 'Yoruba', 'native': 'Yorùbá'},
 'yue': {'english': '粵語', 'native': '粵語'},
 'sgs': {'english': 'Žemaitėška', 'native': 'Žemaitėška'},
 'ace': {'english': 'Bahsa Acèh', 'native': 'Bahsa Acèh'},
 'kbd': {'english': 'Адыгэбзэ', 'native': 'Адыгэбзэ'},
 'ang': {'english': 'Ænglisc', 'native': 'Ænglisc'},
 'ab': {'english': 'Abkhaz', 'native': 'Аҧсуа'},
 'roa-rup': {'english': 'Armãneashce', 'native': 'Armãneashce'},
 'frp': {'english': 'Arpitan', 'native': 'Arpitan'},
 'arc': {'english': 'ܐܬܘܪܝܐ', 'native': 'ܐܬܘܪܝܐ'},
 'gn': {'english': 'Guaraní', 'native': 'Avañe’ẽ'},
 'av': {'english': 'Avaric', 'native': 'Авар'},
 'ay': {'english': 'Aymara', 'native': 'Aymar'},
 'bjn': {'english': 'Bahasa Banjar', 'native': 'Bahasa Banjar'},
 'bh': {'english': 'Bihari', 'native': 'भोजपुरी'},
 'bcl': {'english': 'Bikol Central', 'native': 'Bikol Central'},
 'bi': {'english': 'Bislama', 'native': 'Bislama'},
 'bo': {'english': 'Tibetan Standard', 'native': 'བོད་ཡིག'},
 'bxr': {'english': 'Буряад', 'native': 'Буряад'},
 'cbk-x-zam': {'english': 'Chavacano de Zamboanga', 'native': 'Chavacano de Zamboanga'},
 'co': {'english': 'Corsican', 'native': 'Corsu'},
 'za': {'english': 'Zhuang', 'native': 'Cuengh'},
 'pdc': {'english': 'Deitsch', 'native': 'Deitsch'},
 'dv': {'english': 'Divehi', 'native': 'ދިވެހިބަސް'},
 'nv': {'english': 'Navajo', 'native': 'Diné Bizaad'},
 'dsb': {'english': 'Dolnoserbski', 'native': 'Dolnoserbski'},
 'roa-x-eml': {'english': 'Emigliàn–Rumagnòl', 'native': 'Emigliàn–Rumagnòl'},
 'myv': {'english': 'Эрзянь', 'native': 'Эрзянь'},
 'ext': {'english': 'Estremeñu', 'native': 'Estremeñu'},
 'hif': {'english': 'Fiji Hindi', 'native': 'Fiji Hindi'},
 'fur': {'english': 'Furlan', 'native': 'Furlan'},
 'gv': {'english': 'Manx', 'native': 'Gaelg'},
 'gag': {'english': 'Gagauz', 'native': 'Gagauz'},
 'ki': {'english': 'Kikuyu', 'native': 'Gĩkũyũ'},
 'glk': {'english': 'گیلکی', 'native': 'گیلکی'},
 'gan': {'english': '贛語', 'native': '贛語'},
 'hak': {'english': 'Hak-kâ-fa/客家話', 'native': 'Hak-kâ-fa/客家話'},
 'xal': {'english': 'Хальмг', 'native': 'Хальмг'},
 'ha': {'english': 'Hausa', 'native': 'Hausa'},
 'haw': {'english': 'ʻŌlelo Hawaiʻi', 'native': 'ʻŌlelo Hawaiʻi'},
 'ig': {'english': 'Igbo', 'native': 'Igbo'},
 'ie': {'english': 'Interlingue', 'native': 'Interlingue'},
 'kl': {'english': 'Kalaallisut', 'native': 'Kalaallisut'},
 'pam': {'english': 'Kapampangan', 'native': 'Kapampangan'},
 'csb': {'english': 'Kaszëbsczi', 'native': 'Kaszëbsczi'},
 'kw': {'english': 'Cornish', 'native': 'Kernewek'},
 'km': {'english': 'Khmer', 'native': 'ភាសាខ្មែរ'},
 'rw': {'english': 'Kinyarwanda', 'native': 'Kinyarwanda'},
 'kv': {'english': 'Komi', 'native': 'Коми'},
 'kg': {'english': 'Kongo', 'native': 'Kongo'},
 'gom': {'english': 'Konknni', 'native': 'कोंकणी'},
 'lo': {'english': 'Lao', 'native': 'ພາສາລາວ'},
 'lad': {'english': 'Dzhudezmo', 'native': 'Dzhudezmo'},
 'lbe': {'english': 'Лакку', 'native': 'Лакку'},
 'lez': {'english': 'Лезги', 'native': 'Лезги'},
 'lij': {'english': 'Líguru', 'native': 'Líguru'},
 'ln': {'english': 'Lingala', 'native': 'Lingála'},
 'jbo': {'english': 'lojban', 'native': 'lojban'},
 'lrc': {'english': 'لۊری شومالی', 'native': 'لۊری شومالی'},
 'lg': {'english': 'Ganda', 'native': 'Luganda'},
 'mt': {'english': 'Maltese', 'native': 'Malti'},
 'lzh': {'english': '文言', 'native': '文言'},
 'ty': {'english': 'Tahitian', 'native': 'Reo Mā’ohi'},
 'mi': {'english': 'Māori', 'native': 'Māori'},
 'xmf': {'english': 'მარგალური', 'native': 'მარგალური'},
 'cdo': {'english': 'Mìng-dĕ̤ng-ngṳ̄', 'native': 'Mìng-dĕ̤ng-ngṳ̄'},
 'mwl': {'english': 'Mirandés', 'native': 'Mirandés'},
 'mdf': {'english': 'Мокшень', 'native': 'Мокшень'},
 'nah': {'english': 'Nāhuatlahtōlli', 'native': 'Nāhuatlahtōlli'},
 'na': {'english': 'Nauruan', 'native': 'Dorerin Naoero'},
 'nds-nl': {'english': 'Nedersaksisch', 'native': 'Nedersaksisch'},
 'frr': {'english': 'Nordfriisk', 'native': 'Nordfriisk'},
 'roa-x-nrm': {'english': 'Nouormand', 'native': 'Nouormand'},
 'nov': {'english': 'Novial', 'native': 'Novial'},
 'mhr': {'english': 'Олык Марий', 'native': 'Олык Марий'},
 'as': {'english': 'Assamese', 'native': 'অসমীযা়'},
 'pi': {'english': 'Pāli', 'native': 'पाऴि'},
 'pag': {'english': 'Pangasinán', 'native': 'Pangasinán'},
 'pap': {'english': 'Papiamentu', 'native': 'Papiamentu'},
 'ps': {'english': 'Pashto', 'native': 'پښتو'},
 'koi': {'english': 'Перем Коми', 'native': 'Перем Коми'},
 'pfl': {'english': 'Pfälzisch', 'native': 'Pfälzisch'},
 'pcd': {'english': 'Picard', 'native': 'Picard'},
 'krc': {'english': 'Къарачай–Малкъар', 'native': 'Къарачай–Малкъар'},
 'kaa': {'english': 'Qaraqalpaqsha', 'native': 'Qaraqalpaqsha'},
 'crh': {'english': 'Qırımtatarca', 'native': 'Qırımtatarca'},
 'ksh': {'english': 'Ripoarisch', 'native': 'Ripoarisch'},
 'rm': {'english': 'Romansh', 'native': 'Rumantsch'},
 'rue': {'english': 'Русиньскый Язык', 'native': 'Русиньскый Язык'},
 'se': {'english': 'Northern Sami', 'native': 'Sámegiella'},
 'sc': {'english': 'Sardinian', 'native': 'Sardu'},
 'stq': {'english': 'Seeltersk', 'native': 'Seeltersk'},
 'nso': {'english': 'Sesotho sa Leboa', 'native': 'Sesotho sa Leboa'},
 'sn': {'english': 'Shona', 'native': 'ChiShona'},
 'sd': {'english': 'Sindhi', 'native': 'سنڌي'},
 'szl': {'english': 'Ślůnski', 'native': 'Ślůnski'},
 'so': {'english': 'Somali', 'native': 'Soomaaliga'},
 'srn': {'english': 'Sranantongo', 'native': 'Sranantongo'},
 'kab': {'english': 'Taqbaylit', 'native': 'Taqbaylit'},
 'roa': {'english': 'Tarandíne', 'native': 'Tarandíne'},
 'tet': {'english': 'Tetun', 'native': 'Tetun'},
 'tpi': {'english': 'Tok Pisin', 'native': 'Tok Pisin'},
 'to': {'english': 'Tonga', 'native': 'faka Tonga'},
 'tk': {'english': 'Turkmen', 'native': 'Türkmençe'},
 'tyv': {'english': 'Тыва дыл', 'native': 'Тыва дыл'},
 'udm': {'english': 'Удмурт', 'native': 'Удмурт'},
 'ug': {'english': 'Uyghur', 'native': 'ئۇيغۇرچه'},
 'vep': {'english': 'Vepsän', 'native': 'Vepsän'},
 'fiu-vro': {'english': 'Võro', 'native': 'Võro'},
 'vls': {'english': 'West-Vlams', 'native': 'West-Vlams'},
 'wo': {'english': 'Wolof', 'native': 'Wolof'},
 'wuu': {'english': '吳語', 'native': '吳語'},
 'diq': {'english': 'Zazaki', 'native': 'Zazaki'},
 'zea': {'english': 'Zeêuws', 'native': 'Zeêuws'},
 'ak': {'english': 'Akan', 'native': 'Akan'},
 'bm': {'english': 'Bambara', 'native': 'Bamanankan'},
 'ch': {'english': 'Chamorro', 'native': 'Chamoru'},
 'ny': {'english': 'Chichewa', 'native': 'Chichewa'},
 'ee': {'english': 'Ewe', 'native': 'Eʋegbe'},
 'ff': {'english': 'Fula', 'native': 'Fulfulde'},
 'got': {'english': '𐌲𐌿𐍄𐌹𐍃𐌺', 'native': '𐌲𐌿𐍄𐌹𐍃𐌺'},
 'iu': {'english': 'Inuktitut', 'native': 'ᐃᓄᒃᑎᑐᑦ'},
 'ik': {'english': 'Inupiaq', 'native': 'Iñupiak'},
 'ks': {'english': 'Kashmiri', 'native': 'كشميري'},
 'ltg': {'english': 'Latgaļu', 'native': 'Latgaļu'},
 'ro-Cyrl': {'english': 'Молдовеняскэ', 'native': 'Молдовеняскэ'},
 'fj': {'english': 'Fijian', 'native': 'Na Vosa Vaka-Viti'},
 'cr': {'english': 'Cree', 'native': 'ᓀᐦᐃᔭᐍᐏᐣ'},
 'pih': {'english': 'Norfuk/Pitkern', 'native': 'Norfuk/Pitkern'},
 'om': {'english': 'Oromo', 'native': 'Afaan Oromoo'},
 'pnt': {'english': 'Ποντιακά', 'native': 'Ποντιακά'},
 'dz': {'english': 'Dzongkha', 'native': 'རྫོང་ཁ'},
 'rmy': {'english': 'Romani', 'native': 'Romani'},
 'rn': {'english': 'Kirundi', 'native': 'Kirundi'},
 'sm': {'english': 'Samoan', 'native': 'Gagana Sāmoa'},
 'sg': {'english': 'Sango', 'native': 'Sängö'},
 'st': {'english': 'Southern Sotho', 'native': 'Sesotho'},
 'tn': {'english': 'Tswana', 'native': 'Setswana'},
 'cu': {'english': 'Old Church Slavonic', 'native': 'Словѣ́ньскъ'},
 'ss': {'english': 'Swati', 'native': 'SiSwati'},
 'ti': {'english': 'Tigrinya', 'native': 'ትግርኛ'},
 'chr': {'english': 'ᏣᎳᎩ', 'native': 'ᏣᎳᎩ'},
 'chy': {'english': 'Tsėhesenėstsestotse', 'native': 'Tsėhesenėstsestotse'},
 've': {'english': 'Venda', 'native': 'Tshivenḓa'},
 'ts': {'english': 'Tsonga', 'native': 'Xitsonga'},
 'tum': {'english': 'chiTumbuka', 'native': 'chiTumbuka'},
 'tw': {'english': 'Twi', 'native': 'Twi'},
 'xh': {'english': 'Xhosa', 'native': 'isiXhosa'},
 'zu': {'english': 'Zulu', 'native': 'isiZulu'}}
 

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def default(dictionary: dict, key, default) -> dict:
    if key not in dictionary:
        dictionary[key] = default
    return dict

# munging purifies the fields so they can be used in html and stuff
# without much mod
def munge(instanceList: list, tootLimit=None) -> list:
    purifyList = ['description', 'tagline', 'title']
    neededList = ['users', 'connections', 'statuses', 'language', 'language_name' ]
    copy = []
    for i in instanceList:
        if i['reachable'] == False:
            continue
        
        default(i, 'tootSample', [])
        default(i, 'name', i['domain'])
        default(i, 'title', i['name'])

        default(i, 'nameplate', "no description")
        default(i, 'tagline', i['nameplate'])
        default(i, 'description', i['tagline'])

        default(i, 'email', "")
        default(i, 'admin', "")
    
        if 'language' in i:
            if i['language']  not in languageMap:
                # attempt to get something useable:
                l = i['language'].split("-")[0]
                if l in languageMap:
                    print ("changing langage %s to %s ", i['language'], l)
                    i['language'] = l

            if i['language'] in languageMap:
                i['language_name'] = languageMap[i['language']]['english']
                i['language_name_native'] = languageMap[i['language']]['native']
            
        #replace required but missing with "?"
        for n in neededList:
            if n not in i:
                i[n] = "?" #FIXME: this is bad for SQL and just in general icky
        
        # class tags for filtering
        i['class_tags'] = []
        
        if tootLimit != None:
            i['tootSample'] = i['tootSample'][:tootLimit]
            
        for toot in i['tootSample']:
            toot['avvi'] = toot['account']['avatar']
            toot['content_text'] = toText(toot['content'])
            toot['content_html'] = purify(toot['content'])

        for field in purifyList:
            i[field+"_raw"] = i[field]
            i[field] = purify(i[field], absoluteURL="https://" + i['domain']+"/")
        copy.append(i)
    return copy            

def purifyText(sometext: str) -> str:
    " lots of room for improvement "
    s = re.sub(r'<[^>]*script[^>]*>', '', sometext)
    s = re.sub(r'<', '&lt;', s)
    s = re.sub(r'>', '&gt;', s)
    s = re.sub(r'"', '&quot;', s)
    return s

Newline2Para=re.compile(r'\n([^\n]+)\n')
def purify(sometext: str, absoluteURL=None) -> str:

    if type(sometext) != str: return ""
    
    s = re.sub(r'<script[^<]+</script>', "", sometext)
    s = re.sub(r'<style[^<]+</style>', "", s)

    s = BeautifulSoup(s, PARSER)
    if len(s.findAll()) == 0:
        s =  purifyText(s.get_text())
        return Newline2Para.sub(r'<p>\1</p>', s)
    
        # remove CData crap
    for cd in s.findAll(text=True):
        if isinstance(cd, CData):
            cd.replaceWith('')

    # remove scripts
    while s.script != None: s.script.decompose()
    while s.style != None: s.style.decompose()

    while s.embed != None: s.embed.decompose()
    
    if absoluteURL!= None:
        for link in s.find_all('a', href=True):
            # stuff with colon is absolute (not always true, but screw it,
            # I'm not writing a map of all protocol handlers
            if link['href'].find(':') < 0:
                eprint ("Absolutifying URL %s" % (link['href']) )
                l = link['href'].strip().lstrip('./').lstrip('/')
                link['href'] = absoluteURL + l
                eprint ("absolutified to %s " %  link['href'] )

        for img in s.find_all('img', src=True):
            if img['src'].find(':') < 0:
                eprint ("Absolutifying URL %s" % (img['src']) )
                l = img['src'].strip().lstrip('./').lstrip('/')
                img['src'] = absoluteURL + l
                eprint ("absolutified to %s " %  img['src'] )
                
    s = s.prettify()

    # remove repetitive </br> cuz damn
    #s = re.sub(r'(\s*</?br/?>\n?)+', '<br>', s)
    return s    

def toText(someText: str) -> str:
    s = BeautifulSoup(someText, PARSER)
    s = s.get_text()
    return purifyText(s)            


def PullInstanceList(url=None, filename=None):
    """
    Download json from https://instances.mastodon.xyz/instances.json
    and return it as a dict

    Alternatively, crash with sys.exit(-1)
    """
    if url == None:
        url = DEFAULT_MASTER
    
    if filename != None:
        # get the json from the file
        f = open(filename)
        s = f.read()
        return json.loads(s)
        
    r = requests.get(url)
    r.raise_for_status()

    if r.status_code != 200:
        eprint("Deciding not to download instances.mastodon.xyz because of strange status code " + str(r.status_code))
        sys.exit(-1) #prob should be an exception but hey
    else:
        return r.json()

def ExtractAboutInfo(html: str) -> dict:
    """
    Parse the passed HTML of an instance's about page, and extract as much
    info as feasible, returning a dict with keys like:

    'nameplate'     -- name plus short description
    'title_onpage'    -- name of instance on about page
    'tagline'       -- the short description
    'admin'         -- admin contact in form @Gargron, if any
    'email'         -- email contact if any
    'stuff'         -- extra junk that might not have parsed in contact area
    'language'      -- declared language in html doc (not reliable)
    """

    s = BeautifulSoup(html, "html.parser")
    d = {}
    found = False
    panels = []

    # language
    theH = s.find('html')
    if theH != None and 'lang' in theH.attrs:
        d['language'] = theH.attrs['lang']
        eprint("LANGUAGE: " + d['language'])

    # contact info
    for div in s.find_all('div'):
        if 'class' in div.attrs:
            for c in div['class']: #can have multiple classes
                if c == u'panel':
                    #eprint ("PANEL###")
                    #eprint (div.prettify())
                    panels.append(div)

    #admin handle
    for ownerinfo in s.find_all("div", class_="owner"):
        scrub = ownerinfo.get_text()
        #eprint(scrub, "\n######admin")
        res =  re.findall(r'\B@\w+', scrub)
        if len(res) > 0:
            d['admin'] = res[0]
            eprint("admin:  ", d['admin'])
            break

    # admin email
    for ownerinfo in s.find_all("div", class_="contact-email"):
        scrub = ownerinfo.get_text()
        #eprint(scrub, "\n######email")
        res= re.findall(r'\b\w+@\w+.\w+', scrub)
        if len(res) > 0:
                d['email'] = res[0]
                eprint("email: ", d['email'])
                if len(d['email']) == 0:
                    del d['email']

    todict = [u'nameplate', u'description',  u'stuff' ]
    todict = todict[0:len(panels)]
    x=0
    for item in todict:
        d[item] = panels[x]
        x=x+1

    if u'nameplate' in d.keys():
        string = d[u'nameplate']
        try:
            d[u'title_onpage'] = string.h2.prettify()
            d[u'tagline'] = string.p.prettify()
        except AttributeError:
            pass

    #user counts
    stats = s.find("div", class_="information-board")
    #print(stats)
    if stats != None:
        sections = stats.find_all("div", class_="section")
        sectionList = []
        for piece in sections:
            text = re.sub(',', "", str(piece))
            #print ("#####html", text)
            res = re.findall(r'>(\d+)<', text)
            #print("RES:", res)
            if len(res) > 0:
                sectionList.append(res[0].strip('><'))
            
    
        if len(sectionList) == 3:
            sections = ['users', 'statuses', 'connections']
            try:
                for i in range(3):
                    d[sections[i]] = int(sectionList[i])
                    eprint(sections[i] + ": " + str(d[sections[i]]))
            except TypeError:
                pass

    # convert to text
    if 'nameplate' in d.keys():
        d['nameplate'] = d['nameplate'].get_text()
    if 'description' in d.keys():
        d['description'] = d['description'].get_text()
    if 'stuff' in d.keys():
        d['stuff'] = d['stuff'].get_text()

    return d
    
def grabInfo(instance: dict) -> dict:
        d = {}

        for key in instance.keys():
            d[key] = instance[key]
        
        #fix bad vernacular at .xyz
        if 'name' in d:
            if  d['name'] != None:
                d['domain'] = d['name']
            del d['name']

        # the openRegistrations field at .xyz is unreliable
        # so check the join page for text 'closed-registrations-message'
        # and presume this means registrations are closed, otherwise open
        url = "https://" + d['domain'] + "/about"
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                if 'error' in d: del d['error'] # we succeded, so woot!
                if r.text.find('closed-registrations-message') >= 0:
                    d['openRegistrations'] = False
                else: #FIXME need some extra check for valid form
                    d['openRegistrations'] = True
                
                eprint("%s registrations open: %s" % (d['domain'], d['openRegistrations']))

        except Exception as e: # FIXME: bad but how many request/urllib exceptions must I account for? Unknown...
            eprint ("Couldn't download " + url + "(%s)" % str(e))

        
        url = "https://" + d['domain'] + "/about/more"

        eprint ("Downloading \"" + url + "\"...")

        r  = False # check for failure
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            if 'error' in d: del d['error'] # we succeded, so woot!
            
        except Exception as e: # FIXME: bad but how many request/urllib exceptions must I account for? Unknown...
            eprint ("Couldn't download " + url + "(%s)" % str(e))
            d['error'] = str(e)

        # add more info scraped from HTML and such        
        if r != False and r.status_code == 200:
            aboutDict = ExtractAboutInfo(r.text)
            for key in aboutDict.keys():
                d[key] = aboutDict[key]
            d['url'] = url
            d['html'] = r.text
            d['reachable'] = True
        else:
            d['reachable'] = False

        d['lastCheck'] = time.time()
        if not d['reachable']:
            # test for gnusocial
            url = "https://%s/main/public" % d['domain']
            try:
                r = requests.get(url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    d['isGnuSocial'] = True
                else:
                    d['isGnuSocial'] = False
                
            except Exception as e:    
                 eprint ("couldn't determine Gnu Social for " + url + "(%s)" % str(e))
                 d['isGnuSocial'] = False
        else:
            d['isGnuSocial'] = False
         
        if d['reachable']:
            # try to get the json at the instance itself.
            # this contains:
            #   short description
            #   contact email
            #   and other stuff

            url = "https://%s/api/v1/instance.json" % d['domain']

            try:
                r = requests.get(url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    theDict = json.loads(r.text)
                    #eprint(theDict)
                    if 'description' in theDict:
                        if len(theDict['description']) > 0:
                            d['tagline'] = theDict['description']
                        del theDict['description'] #prevent overwriting below
                    
                    if 'email' in theDict:
                        if len(theDict['email']) > 0:
                            d['email'] = theDict['email']
                        del theDict['email']
                    
                    # so the extra stuff, add it only
                    # if it's not in my list already
                    # because I dunno if there's a name conflict
                    for k,v in theDict.items():
                        if k not in d and len(v) > 0:
                            d[k] = v
            
            except Exception as e: # so many exception types, hard to do anything but this
              eprint ("Skipping extra JSON info for " + url + "(%s)" % str(e))
          
            # now we get a sample of the local toots at this moment.
            url = "https://%s/api/v1/timelines/public?local=1" % d['domain']
            eprint("Getting toot sample from %s..." % url)
            
            try:
                r = requests.get(url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    theDict = json.loads(r.text)
                    d['tootSample'] = theDict
            except Exception as e:
                eprint("Skipping toot sample for %s (%s)" % (url, str(e)) )
            
          
        # WHEW!
        return d


class workerThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        eprint( "Starting " + self.name)
        process_data(self.name, self.q)
        eprint ("Exiting " + self.name)

def process_data(threadName, q):
    global exitFlag
    while not exitFlag:
        i= None
        queueLock.acquire()
        if not workQueue.empty():
            i = q.get()
            #eprint ("%s processing %s" % (threadName, i['name']))
            queueLock.release()
            d = grabInfo(i)
            #eprint ("%s done processing %s" % (threadName, d['domain']))

            queueLock.acquire()
            #eprint("%s appending %s" % (threadName, d['domain']))
            aboutInstances.append(d)
            queueLock.release()
        else:
            queueLock.release()



def DoItAll(instances):
    # Create new threads
    global exitFlag
    global queueLock
    global workQueue
    global aboutInstances
    global threadList

    exitFlag = False
    queueLock = threading.Lock()
    workQueue = queue.Queue(THREADS_MAX*3)
    aboutInstances = []
    threadList = []
    
    threads = []

    for t in range(THREADS_MAX):
        threadList.append('Thread-' + str(t))



    threadID = 1
    for tName in threadList:
        thread = workerThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Fill the queue
    for i in instances:
        if 'domain' in i:
            default(i, 'name', i['domain'])
        eprint("Adding %s" % i['name'])
        #queueLock.acquire()
        workQueue.put(i)
        #queueLock.release()
    eprint ("Done adding work")
    # Wait for queue to empty
    while not workQueue.empty():
        #eprint("Queue still has work...")
        time.sleep(2)
        pass

    # Notify threads it's time to exit
    eprint("Setting exit flag...")
    exitFlag = True

    # Wait for all threads to complete
    for t in threads:
        t.join()

domainCheck = re.compile(r'^[a-z0-9]+\.?([a-z0-9-]+\.?)*\.[a-z0-9]+$')
def deleteShittyDomains(data):
  result = []
  for item in data:
    if 'domain' not in item and 'name' in item:
      item['domain'] = item['name']
      
    if 'domain' in item:
      item['domain'] = item['domain'].lower()
      item['domain'] = item['domain'].strip()
      item['domain'] = item['domain'].rstrip('/')
      
      parts = item['domain'].split('.')
      if len(parts) < 2:
        eprint("removing shitty domain ", item['domain'])
        continue
      
      if len (parts[-1]) < 2:
        eprint("removing shitty domain ", item['domain'])
        continue
      if False: 
        if len (parts[-2]) < 2: # this is not always true (there are 1 letter domains in some countries...)
          eprint("removing shitty domain ", item['domain'])
          continue    

      if domainCheck.match(item['domain']):
        result.append(item)
      else:
        eprint("removing shitty domain ", item['domain'])

  return result
# I'm doing it the easy/breakbable way.
# 1. Download instance list from Mastodon.xyz.
# 2. Download about pages of all instances, parse this, and merge it.
# 3. Dump all of this into the .json output file

# it requires about 30 minutes of uninterrupted run.
# But, this keeps the code sane, so :shrug:

if __name__ == "__main__":
    if 'TEST' in os.environ and os.environ['TEST']:
        TEST_ONLY=True

    if 'THREADS' in os.environ:
        THREADS_MAX=int(os.environ['THREADS'])
        
    # if a .json file is specified, redownload info from
    # all those instances and create an updated version
    # this can help with bashing mastodon.xyz & gets a minor speed boost
    jsonFile = None
    if 'JSON_FILE' in os.environ:
        jsonFile = os.environ['JSON_FILE']
        eprint("Using the data in '%s'...." % jsonFile)
        
    filenameOut = "described_instances.json"
    if len(sys.argv) > 1:
        filenameOut = sys.argv[1]

    # Download the starter list 
    json_data = PullInstanceList(filename=jsonFile)

    if RANDOMIZE:
        random.shuffle(json_data)
    
    json_data = deleteShittyDomains(json_data)
        
    if TEST_ONLY:
        random.shuffle(json_data)
        json_data = json_data[0:10]

    # discover and store various info for each instance
    # place it in global "aboutInstances"

    DoItAll(json_data)

    eprint ("munging safe versions...")
    aboutInstances = munge(aboutInstances)
    # write the JSON output 

    f = open(filenameOut, "w")
    f.write(json.dumps(aboutInstances, indent=4, separators=(',', ': ')))
    f.close()

    # print out the fields we find
    # this is useful in deciding the SCHEMA
    # (but is bad for *using* as schema, since it's downloaded from net
    fields = {}
    for i in aboutInstances:
        for k,v in i.items():
            fields[k] = v
    
    eprint("FIELDS FOUND:")
    for k in fields:
        eprint(k)

