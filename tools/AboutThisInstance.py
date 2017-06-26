#!/usr/bin/env python3

from bs4 import BeautifulSoup, CData, FeatureNotFound   # pip3 install bs4
import requests                 # pip3 install requests

import sys, re, time
from json import JSONDecodeError

REQUEST_TIMEOUT=8.0
PARSER = 'html.parser' # most consistent & flexible parser IMO

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
    
def badException(e):
  return type(e) in [StopIteration, StopAsyncIteration, ArithmeticError, AssertionError, AttributeError, BufferError, EOFError, ImportError, ModuleNotFoundError, LookupError, MemoryError, NameError, OSError, ReferenceError, RuntimeError, SyntaxError, SystemError, TypeError, ValueError, Warning]

def theBetterGet(url):
  "get urls being wise to errors"
  r = None
  try:
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    if r.status_code == 200:
      return r, None
    else:
      return r, str(r.status_code) + " " + str(r.reason)
  except Exception as e: #FIXME!!!
    eprint("couldn't download '%s':\n%s" %(url, str(e)))
    if badException(e):
      raise e
    return r, str(e)

def default(dictionary: dict, key, default) -> dict:
    if key not in dictionary:
        dictionary[key] = default
    return dict

# add even more info to complete the data

def AddMore(i: dict):
    purifyList = ['description', 'tagline', 'title']
    neededList = ['users', 'connections', 'statuses', 'language', 'language_name' ]

    if i['reachable'] == False:
        return
    
    default(i, 'tootSample', [])
    default(i, 'name', i['domain'])
    default(i, 'title', i['name'])

    default(i, 'nameplate', "no description")
    default(i, 'tagline', i['nameplate'])
    default(i, 'description', i['tagline'])

    default(i, 'email', "")
    default(i, 'admin', "")
    default(i, 'version', None)
    default(i, 'error', None)


    if 'language' in i:
        if i['language']  not in languageMap:
            # attempt to get something useable:
            l = i['language'].split("-")[0]
            if l in languageMap:
                print ("changing langage %s to %s " % ( i['language'], l))
                i['language'] = l

        if i['language'] in languageMap:
            i['language_name'] = languageMap[i['language']]['english']
            i['language_name_native'] = languageMap[i['language']]['native']
        
    #replace required but missing with "?"
    for n in neededList:
        if n not in i:
            i[n] = None

    for field in purifyList:
        #i[field+"_raw"] = i[field] # bloats the file, so leave it out
        i[field] = purify(i[field], absoluteURL="https://" + i['domain']+"/")


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

  
def AboutThisInstance(domain: str, tootSample=True, updateDict=None) -> dict:
  d = {} # store all info in this dict
  if updateDict != None:
    d = updateDict  
  
  d['domain'] = domain
  aboutURL = "https://" + d['domain'] + "/about"
  aboutMoreURL = "https://" + d['domain'] + "/about/more"
  jsonURL = "https://%s/api/v1/instance.json" % d['domain']
  tootURL = "https://%s/api/v1/timelines/public?local=1" % d['domain']

  d['url'] = aboutMoreURL
  d['reachable'] = False
  d['last_check'] = time.time()

  r, d['error'] = theBetterGet(aboutURL)
  if d['error'] != None: return d, d['error']

  html = r.text

  # accepting registrations?
  if html.find('closed-registrations-message') >=0:
    d['open_registrations'] = False
  else:
    d['open_registrations'] = True
  
  # about/more info
  r, d['error'] = theBetterGet(aboutMoreURL)
  if d['error'] != None: return d, d['error']
  
  # I put this here because every instance needs an about/more IMO
  # to be an instance
  d['reachable'] = True

  aboutDict = ExtractAboutInfo(r.text)
  for key in aboutDict.keys():
      d[key] = aboutDict[key] 


  # extra info at the instance's json file
  r, d['error'] = theBetterGet(jsonURL)
  if d['error'] != None: return d, d['error']

  skipit = False
  try:
    j = r.json()
    for k,v in j.items():
      if k not in d:
        d[k] = v
  except JSONDecodeError: # dear modules naming custom exception classes I have to hunt down: fuckya
    pass
 
  if tootSample:
    # now we get a sample of the local toots at this moment.
    eprint("Getting toot sample from %s..." % tootURL)

    r, d['error'] = theBetterGet(tootURL)
    if d['error'] != None: return d, d['error']
  
    try:
      theDict = r.json()
      d['tootSample'] = theDict

      for toot in d['tootSample']:
        toot['avvi'] = toot['account']['avatar']
        toot['content_text'] = toText(toot['content'])
        toot['content_html'] = purify(toot['content'])

    except JSONDecodeError: 
      pass
    
  
  # this last bit cleans up and adds 
  # derivative information
  AddMore(d)
  return d, None

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
        #eprint("LANGUAGE: " + d['language'])
        if d['language']  not in languageMap:
            # attempt to get something useable:
            l = d['language'].split("-")[0]
            if l in languageMap:
                print ("changing langage %s to %s " % ( d['language'], l))
                d['language'] = l

        if d['language'] in languageMap:
            d['language_name'] = languageMap[d['language']]['english']
            d['language_name_native'] = languageMap[d['language']]['native']
        else:
            d['language_name'] = d['language']
            d['language_name_native'] = d['language']

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
            #eprint("admin:  ", d['admin'])
            break

    # admin email
    for ownerinfo in s.find_all("div", class_="contact-email"):
        scrub = ownerinfo.get_text()
        #eprint(scrub, "\n######email")
        res= re.findall(r'\b\w+@\w+.\w+', scrub)
        if len(res) > 0:
                d['email'] = res[0]
                #eprint("email: ", d['email'])
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
                    #eprint(sections[i] + ": " + str(d[sections[i]]))
            except TypeError:
                pass

    # convert to text
    if 'nameplate' in d.keys():
        d['nameplate'] = d['nameplate'].get_text()
    if 'description' in d.keys():
        d['description'] = d['description'].get_text()

    # used to keep extra laying about but now, meh, makes no difference
    if 'stuff' in d.keys():
        del d['stuff']

    return d
    
if __name__ == "__main__":
  print (AboutThisInstance(sys.argv[1], tootSample=False, updateDict=None))
  