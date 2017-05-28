#!/usr/bin/env python3
"""
usage:
json2html.py in_filename.json out_filename.html

This renders an HTML file using instance data in the .json
which was previously generated with federation2json.py

"""


import json, string
import sys, os, re
import time
from bs4 import BeautifulSoup, CData # because sites do weird HTML

theDate = time.asctime()
head = """
<h1>Described Instance List</h1>
<h4>As of %s</h4>

<p>This is a list of Mastodon instances with descriptions and contact information. It also contains preview links, so that you can better decide which instance to join.</p>

<p>Please note that some instances may contain offensive content!</p>
""" % theDate

languageMap = {
"ab":"Abkhaz", "aa":"Afar", "af":"Afrikaans", "ak":"Akan", "sq":"Albanian", "am":"Amharic",
"ar":"Arabic", "an":"Aragonese", "hy":"Armenian", "as":"Assamese", "av":"Avaric",
"ae":"Avestan", "ay":"Aymara", "az":"Azerbaijani", "bm":"Bambara", "ba":"Bashkir",
"eu":"Basque", "be":"Belarusian", "bn":"Bengali,", "bh":"Bihari", "bi":"Bislama",
"bs":"Bosnian", "br":"Breton", "bg":"Bulgarian", "my":"Burmese", "ca":"Catalan", 
"ch":"Chamorro", "ce":"Chechen", "ny":"Chichewa,", "zh":"Chinese", "cv":"Chuvash", 
"kw":"Cornish", "co":"Corsican", "cr":"Cree", "hr":"Croatian", "cs":"Czech", 
"da":"Danish", "dv":"Divehi,", "nl":"Dutch", "dz":"Dzongkha", "en":"English", 
"eo":"Esperanto", "et":"Estonian", "ee":"Ewe", "fo":"Faroese", "fj":"Fijian", 
"fi":"Finnish", "fr":"French", "ff":"Fula,", "gl":"Galician", "ka":"Georgian", 
"de":"German", "el":"Greek", "gn":"Guaraní", "gu":"Gujarati", "ht":"Haitian,", "ha":"Hausa",
 "he":"Hebrew", "hz":"Herero", "hi":"Hindi", "ho":"Hiri", "hu":"Hungarian", 
 "ia":"Interlingua", "id":"Indonesian", "ie":"Interlingue", "ga":"Irish", "ig":"Igbo", 
 "ik":"Inupiaq", "io":"Ido", "is":"Icelandic", "it":"Italian", "iu":"Inuktitut", 
 "ja":"Japanese", "jv":"Javanese", "kl":"Kalaallisut,", "kn":"Kannada", "kr":"Kanuri", 
 "ks":"Kashmiri", "kk":"Kazakh", "km":"Khmer", "ki":"Kikuyu,", "rw":"Kinyarwanda", 
 "ky":"Kyrgyz", "kv":"Komi", "kg":"Kongo", "ko":"Korean", "ku":"Kurdish", "kj":"Kwanyama", 
 "la":"Latin", "lb":"Luxembourgish,", "lg":"Ganda", "li":"Limburgish,", "ln":"Lingala", 
 "lo":"Lao", "lt":"Lithuanian", "lu":"Luba-Katanga", "lv":"Latvian", "gv":"Manx", 
 "mk":"Macedonian", "mg":"Malagasy", "ms":"Malay", "ml":"Malayalam", "mt":"Maltese", 
 "mi":"Māori", "mr":"Marathi", "mh":"Marshallese", "mn":"Mongolian", "na":"Nauruan", 
 "nv":"Navajo,", "nd":"Northern", "ne":"Nepali", "ng":"Ndonga", "nb":"Norwegian", 
 "nn":"Norwegian", "no":"Norwegian", "ii":"Nuosu", "nr":"Southern", "oc":"Occitan", 
 "oj":"Ojibwe,", "cu":"Old", "om":"Oromo", "or":"Oriya", "os":"Ossetian,", 
 "pa":"(Eastern)", "pi":"Pāli", "fa":"Persian", "pl":"Polish", "ps":"Pashto,", 
 "pt":"Portuguese", "qu":"Quechua", "rm":"Romansh", "rn":"Kirundi", "ro":"Romanian", 
 "ru":"Russian", "sa":"Sanskrit", "sc":"Sardinian", "sd":"Sindhi", "se":"Northern", 
 "sm":"Samoan", "sg":"Sango", "sr":"Serbian", "gd":"Scottish", "sn":"Shona", 
 "si":"Sinhalese,", "sk":"Slovak", "sl":"Slovene", "so":"Somali", "st":"Southern", 
 "es":"Spanish", "su":"Sundanese", "sw":"Swahili", "ss":"Swati", "sv":"Swedish", 
 "ta":"Tamil", "te":"Telugu", "tg":"Tajik", "th":"Thai", "ti":"Tigrinya", "bo":"Tibetan", 
 "tk":"Turkmen", "tl":"Tagalog", "tn":"Tswana", "to":"Tonga", "tr":"Turkish", 
 "ts":"Tsonga", "tt":"Tatar", "tw":"Twi", "ty":"Tahitian", "ug":"Uyghur", 
 "uk":"Ukrainian", "ur":"Urdu", "uz":"Uzbek", "ve":"Venda", "vi":"Vietnamese", 
 "vo":"Volapük", "wa":"Walloon", "cy":"Welsh", "wo":"Wolof", "fy":"Western", "xh":"Xhosa", 
 "yi":"Yiddish", "yo":"Yoruba", "za":"Zhuang,", "zu":"Zulu"
 }
 
def eprint(*args, **kwargs):
    """just like print() but for stderr"""
    print(*args, file=sys.stderr, **kwargs)

def purifyText(string: str) -> str:
    " lots of room for improvement "
    s = re.sub(r'<', '&lt;', string )
    s = re.sub(r'>', '&gt;', string)
    s = re.sub(r'"', '&quot;', string)
    return s

def purify(string: str) -> str:
    s = re.sub(r'<[^>]*script[^>]*>', '', string)
    return s
       
def NameHead(inst) -> str:
    """
    given an instance dictionary, return a heading HTML that contatins
    the name of the instance and a preview link at mastoview
    """
    inst['previewlink'] = "http://www.unmung.com/mastoview?url=%s&view=local" % inst['domain']
    
    if 'title' not in inst:
        inst['title'] = inst['name']
        
    out = string.Template("""
    <h2 class="instance-head">${title}</h2>
    """
    ).substitute(inst)

    return out

def JoinHead(inst: dict) ->str:
    inst['previewlink'] = "http://www.unmung.com/mastoview?url=%s&view=local" % inst['domain']

    out = string.Template("""
    <h4 class="instance-head">${name}</h4>
    <p class="instance-clicks"> <a href="${url}" target="_blank">about</a></p>
    <p class="instance-clicks"><a href="${previewlink}" target="_blank">preview</a></p>
    <p class="instance-clicks"><a href="https://${domain}" target="_blank">join</a></p>
    """
    ).substitute(inst)
    return out
    
def Tagline(i: dict) -> str:
    """
    given an instance dictionary, return markdown of its short description
    or long description if we must...
    """
    if 'tagline' in i.keys():
        out =  processDescription(i['tagline'])
    else:
        if 'nameplate' in i.keys():
            out =  processDescription(i['nameplate']) # fallback if parsed wrong
        else:
            out = "no description\n\n"

    return out

def str2int2str(thing):
    """
    given a string of a possible integer,
    return a nice looking version like 34,395
    or just use the string if something goes wrong
    """
    i = 0
    try:
        i = int(thing)
        return format (i, ',d')
    except:
        return thing

def Users(i: dict) -> str:
    """
    given a instance dictionary, return markdown paragraph showing some
    general stats like | users: 20 | toots: 5,3894 | connections: 338 |
    """
    out = ""
    if 'users' in i.keys():
        u = str2int2str(i['users'])
        out = out + " Users: %s " % u
    if 'statuses' in i.keys():
        s = str2int2str(i['statuses'])
        out = out + "⋅ Toots: %s " % s
    if 'connections' in i.keys():
        c = str2int2str(i['connections'])
        out = out + "⋅ Connections: %s " % c
    if 'language' in i.keys():
        if i['language'].strip() in languageMap:
            out = out + "⋅ Language: %s " % languageMap[i['language'].strip()]
    out = "<div class='stats'>\n" + out + "</div>\n\n"
    return out

def processDescription(text):
    # text could be plain text or html.
    # if it has an html tag, we presume it's html, otherwise, text.
    
        
    s = BeautifulSoup(text, "html.parser")
    
    if len(s.findAll()) == 0:
        temp = purifyText(text)
        regex=re.compile(r'\n([^\n]+)\n')
        return regex.sub(r'<p>\1</p>', temp)
    else:
        
        # remove CData crap
        for cd in s.findAll(text=True):
            if isinstance(cd, CData):
                cd.replaceWith('')

        # remove scripts
        while s.script != None: s.script.decompose()

        while s.embed != None: s.embed.decompose()
        
        s = s.prettify()

        # remove repetitive </br> cuz damn
        s = re.sub(r'(\s*</br>\n?)+', '</br>', s)
        return s    

def TootSample(i: dict, limit: int=10) -> str:
    """
    given an instance dictionary, generate HTML
    with a toot sample
    """
    if 'tootSample' not in i:
        return ""
    
    if len(i['tootSample']) == 0:
        return ""
        
    out = ""
    
    #build an "avvi wall"
    avviWall = ""
    for toot in i['tootSample'][:20]:
        avvi = toot['account']['avatar']
        tootURL = toot['url']
        s = BeautifulSoup(toot['content'], 'html.parser')
        if s.script != None:
            s.script.decompose()
        content= purifyText(s.get_text())
        
        avviWall = avviWall + string.Template("""
        <div class="avvi-wall-avvi"><a href="${tootURL}"><img data-original="${avvi}" width=30 height=30 title="${content}" class="avvi-image lazy"/></a></div>
        """).substitute(locals())

    return '<div class="avvi-wall"> %s </div>' %  avviWall
    
def TootSampleOld(i: dict, limit: int=10) -> str:
    """
    given an instance dictionary, generate HTML
    with a toot sample
    """
    if 'tootSample' not in i:
        return ""
    
    if len(i['tootSample']) == 0:
        return ""
        
    out = ""
    
    #build an "avvi wall"
    avviWall = ""
    for toot in i['tootSample'][:5]:
        avvi = toot['account']['avatar_static']
        tootURL = toot['url']
        avviWall = avviWall + string.Template("""
        <div class="avvi-wall-avvi"><a href="${tootURL}"><img data-original="${avvi}" width=30 height=30 class="lazy"/></a></div>
        """).substitute(locals())

    out = out + '<div class="avvi-wall"> %s </div>' % avviWall

    out = out + '<div class="toot-disclosure"><details><summary> TootSample... </summary>' 
        
    # five toots max
    for toot in i['tootSample'][:5]:
        #skip sensitive media
        if toot['sensitive'] or len(toot['spoiler_text']) > 0:
            continue
            
        avvi = toot['account']['avatar_static']
        content = toot['content']
        attachments = toot['media_attachments']
        tootURL = toot['url']
        mediaDIV = ""
        #FIXME: need to support different types of media:
        for m in attachments:
            if m['type'] == 'image':
                mediaDIV = '<div class="toot-media"><a href="%s"><img class="media-image lazy" src="%s"/></a></div>' % (m['url'], m['preview_url'])
                break
            
        out = out + string.Template("""
        <div class="toot">
            <div class="toot-avvi"><a href="${tootURL}"><img data-original="${avvi}" width=30 height=30 class='lazy' /></a></div>
            <div class="toot-content">${content}</div>
            ${mediaDIV}
        </div>
        """).substitute(locals())

    return '<div class="toot-group">' + out + '</div></details></div>'

        
        
def Description(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown for the long description
    """
    if 'description' not in i.keys():
        return ""

    out = ""
    if len(i['description']) > 500:
        out = out + "<details><summary>More Info...</summary>%s</details>" % processDescription(i['description'])
    else:
        out = out + processDescription(i['description']) 
    return out 

def Email(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown (with linke) for the email
    or "not available" if it doesn't exist
    """
    if 'email' in i.keys():
        out = 'Email: <a href="mailto:%s">%s</a>' % (i['email'], i['email'])
    else:
        out = "Email: Not Available\n\n"
    return "<p>" + out + "</p>"

def Admin(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown for the admin (of assumed form @gargron)
    in a handy link that can be clicked on an HTML page
    to read the admin's profile.
    """
    if 'admin' in i.keys():
        out = 'Admin: <a href="https://%s/%s">%s@%s</a>\n' % (i['name'], i['admin'], i['admin'], i['name'] )
        return out
    else:
        out = "Admin: Not Available\n\n"
    return "<p>" + out + "</p>"

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print ("usage: json2html.py input.json output.md")
        sys.exit(1)

    InFile = open(sys.argv[1])

    instances = json.loads(InFile.read())
    InFile.close()

    instances = sorted(instances, key=lambda u: 100.0-u['uptime'])

    chunkFile = os.path.dirname(os.path.realpath(__file__)) + "/style-chunk.html"

    f = open(chunkFile)
    chunkText = f.read()
    f.close
    
    OutFile = open(sys.argv[2], "w+")

    OutFile.write(chunkText)
    OutFile.write(head)
    for i in instances:
        eprint("Generating HTML for: %s" % i['name'])
        if i['reachable']:
            if 'openRegistrations' in i.keys() and i['openRegistrations']:
                OutFile.write('<div class="instance-chunk">\n')
                
                OutFile.write('<div class="instance-left">\n')
                OutFile.write(purify(TootSample(i)))
                OutFile.write(purify(JoinHead(i)))
                OutFile.write('</div>\n')

                OutFile.write('<div class="instance-right">\n')
                
                OutFile.write('<div class="description-head">\n')
                OutFile.write(purify(NameHead(i)))
                OutFile.write('</div>\n')
                
                OutFile.write('<div class="description-body">\n')
                OutFile.write(purify(Users(i)))
                OutFile.write('<div class="description-short">\n')
                OutFile.write(purify(Tagline(i)))
                OutFile.write('</div>\n')
                
                OutFile.write('<div class="description-long">\n')
                OutFile.write(Description(i))
                OutFile.write('</div>\n')

                OutFile.write('<div class="contact-details">\n')
                OutFile.write(purify(Email(i)))
                OutFile.write(purify(Admin(i)))
                OutFile.write('</div>\n') #contact
                OutFile.write('</div>\n') #body
                OutFile.write('</div>\n') #right
                OutFile.write('</div>\n') #chunk

    OutFile.close()
    
    f = open(sys.argv[2], "r")
    html = f.read()
    f.close()
    
    html = re.sub(r'<script[^<]+</script>', "", html)
    
    s = BeautifulSoup(html, "html.parser")
    
    if s.div != None:
        for x in s.find_all("div", class_="avvi-wall"):
            x.clear()
    
    s = str(s)
    f = open (sys.argv[2] + "-min.html", "w")
    f.write(s)
    f.close()
    