"""
Beat Cash — Module SEO
Générateur type beat : titres, descriptions, hashtags
Système de profils artistes sauvegardables
Avec ou sans IA (Anthropic Claude)
"""

import sys, json, re, random
from pathlib import Path

def _appdir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

CONFIG_FILE   = _appdir() / "seo_config.json"
PROFILES_FILE = _appdir() / "beat_profiles.json"

# ══════════════════════════════════════════════════════════════════════
# BANQUE DE HASHTAGS — ARTISTES TYPE BEAT
# ══════════════════════════════════════════════════════════════════════
ARTIST_TAGS = {
    "Gunna": [
        "#gunna","#gunnatypebeat","#wunna","#drip","#younggunna",
        "#pushinp","#slimeseason","#atl","#gunnatype","#droptopwop",
        "#trapmusic","#2025trap","#melodictrap","#trapbeats",
    ],
    "Drake": [
        "#drake","#draketypebeat","#6god","#ovosound","#toronto",
        "#drizzy","#champagnepapi","#rAndB","#drakevibes",
        "#mapleboyz","#darklanetype","#certifiedlovertypebeat",
    ],
    "Travis Scott": [
        "#travisscott","#travisscotttypebeat","#astroworld","#utopia",
        "#cactusjaketype","#psychedelic","#autotrap","#rodeobeat",
        "#cactusjack","#houstontrap","#texastypebeat",
    ],
    "Playboi Carti": [
        "#playboicarti","#cartitype","#whoopie","#opium","#carti",
        "#wholelotatype","#magnumopus","#cartitypebeat","#opiumbeat",
        "#wholettareddtype","#vampirerap","#dieatype",
    ],
    "Wifisfuneral": [
        "#wifisfuneral","#wifis","#snottype","#wifistypebeat",
        "#emorap","#cloudrap","#darkrap","#sadsounds",
        "#wifisfuneraltypebeat","#snotrap","#deepdepression",
    ],
    "Snot": [
        "#snot","#snottypebeat","#nimbusstype","#snotrap",
        "#emorap","#snotvibes","#fromthesofa","#cloudrap",
        "#snottype","#grunge","#altrap","#snotmusic",
    ],
    "JID": [
        "#jid","#jidtypebeat","#divinefeminine","#dreamvilletype",
        "#jidtype","#lyricalrap","#dreamville","#eastsidejid",
        "#jidraptype","#complexrap","#technicaltrap",
    ],
    "Future": [
        "#future","#futuretypebeat","#freebandz","#hendrix",
        "#futuretype","#pluto","#dirtybirdtype","#highoff","#feds",
        "#freebandztypebeat","#2025future","#melodictrap",
    ],
    "Lil Uzi Vert": [
        "#liluzivert","#uzitypebeat","#luv","#eternalatake",
        "#pinktype","#uzitype","#ravemusic","#liluzitypebeat",
        "#plutoxtrap","#21questions","#pinktape",
    ],
    "Ken Carson": [
        "#kencarson","#kentype","#opium","#kencarsontypebeat",
        "#xtype","#kencarsontype","#opiumrap","#carcrashdiet",
        "#darktrap","#altrap","#rockrap",
    ],
    "Destroy Lonely": [
        "#destroylonely","#destroytype","#opium","#iflonesomeness",
        "#destroylonelytypebeat","#darkmelody","#opiumtype",
        "#lonelytrap","#melodictype","#altrap",
    ],
    "Yeat": [
        "#yeat","#yeattypebeat","#2alivetype","#afterlyfe",
        "#yeattype","#pluggnb","#phonk","#iceage","#2alive",
        "#yeatvibes","#pluggnbtype","#bighomie",
    ],
    "Central Cee": [
        "#centralcee","#centralceetypebeat","#ukdrill","#ukrap",
        "#23type","#centraltype","#drilltype","#wildwest",
        "#ukstreettype","#centralceetype","#londontype",
    ],
    "Drill": [
        "#drillbeat","#drilltype","#ukdrill","#nydrill","#chicagodrill",
        "#drill2025","#drillmusic","#drillbeats","#darkdrill",
        "#trench","#drillrap","#streetbanger",
    ],
    "Trap": [
        "#trapbeat","#traptype","#trapmusic","#trap2025","#darkTrap",
        "#hardbanger","#trapbanger","#slimytrap","#hardtrap",
        "#southerntrap","#trapbeats","#traprap",
    ],
    "Phonk": [
        "#phonk","#phonkbeat","#phonktype","#memphisphonk","#drifterphonk",
        "#phonkmusic","#aggressivephonk","#darkphonk","#phonk2025",
        "#horrorphonk","#phonktrap",
    ],
}

# Tags de base communs à tous les beats
BASE_BEAT_TAGS = [
    "#typebeat","#freebeat","#freeforprofit","#beatmaker",
    "#producer","#beats","#hiphop","#rap","#freestylebeat",
    "#instrumentalrap","#beatstore","#newbeat","#2025",
    "#hardbeats","#darkbeats","#rapbeats","#trapbeats",
    "#beatsforsale","#exclusivebeat","#musicproducer",
]

# ══════════════════════════════════════════════════════════════════════
# BASE DE DONNÉES ARTISTES — pour génération automatique (sans API)
# ══════════════════════════════════════════════════════════════════════
ARTISTS_DB = {
    # ── TRAP ──────────────────────────────────────────────────────────
    "Gunna": {
        "genre": "Trap",
        "related": ["Young Thug", "Lil Baby", "Future", "Don Toliver"],
        "tags": ["#gunna","#gunnatypebeat","#wunna","#drip","#slimeseason","#atl"],
    },
    "Lil Baby": {
        "genre": "Trap",
        "related": ["Gunna", "Future", "42 Dugg", "Rylo Rodriguez"],
        "tags": ["#lilbaby","#lilbabytypebeat","#4pf","#babyvibes","#myturn"],
    },
    "Future": {
        "genre": "Trap",
        "related": ["Metro Boomin", "Lil Uzi Vert", "Young Thug", "Drake"],
        "tags": ["#future","#futuretypebeat","#freebandz","#pluto","#hendrix"],
    },
    "Young Thug": {
        "genre": "Trap",
        "related": ["Gunna", "Lil Duke", "Future", "Lil Baby"],
        "tags": ["#youngthug","#youngthugtypebeat","#slime","#ysl","#thugvibes"],
    },
    "21 Savage": {
        "genre": "Trap",
        "related": ["Metro Boomin", "Drake", "Young Nudy", "Offset"],
        "tags": ["#21savage","#21savagetypebeat","#metroboomin","#slaughtergang"],
    },
    "Metro Boomin": {
        "genre": "Trap",
        "related": ["21 Savage", "Future", "Don Toliver", "Offset"],
        "tags": ["#metroboomin","#metrotypbeat","#notallheroes","#superhero"],
    },
    "Don Toliver": {
        "genre": "Trap",
        "related": ["Travis Scott", "Gunna", "Drake", "The Weeknd"],
        "tags": ["#dontoliver","#dontolivertypebeat","#cactus","#stargazing"],
    },
    "Offset": {
        "genre": "Trap",
        "related": ["Metro Boomin", "21 Savage", "Young Thug", "Future"],
        "tags": ["#offset","#offsettypebeat","#migos","#culture","#saucegod"],
    },
    # ── MELODIC TRAP ──────────────────────────────────────────────────
    "Lil Uzi Vert": {
        "genre": "Melodic Trap",
        "related": ["Playboi Carti", "Ken Carson", "Destroy Lonely", "Yeat"],
        "tags": ["#liluzivert","#uzitypebeat","#eternalatake","#pinktape","#uzivibes"],
    },
    "Playboi Carti": {
        "genre": "Melodic Trap",
        "related": ["Lil Uzi Vert", "Ken Carson", "Destroy Lonely", "Pierre Bourne"],
        "tags": ["#playboicarti","#cartitypebeat","#opium","#wholelottared","#vampirerap"],
    },
    "Ken Carson": {
        "genre": "Melodic Trap",
        "related": ["Playboi Carti", "Destroy Lonely", "Homixide Gang", "Lil Uzi Vert"],
        "tags": ["#kencarson","#kencarsontypebeat","#opium","#xproject","#altrap"],
    },
    "Destroy Lonely": {
        "genre": "Melodic Trap",
        "related": ["Playboi Carti", "Ken Carson", "Homixide Gang"],
        "tags": ["#destroylonely","#destroytypebeat","#opium","#iflonesomeness","#darkmelody"],
    },
    "Yeat": {
        "genre": "Melodic Trap",
        "related": ["Lil Uzi Vert", "Playboi Carti", "Travis Scott"],
        "tags": ["#yeat","#yeattypebeat","#2alivetype","#pluggnb","#yeatvibes"],
    },
    "Pierre Bourne": {
        "genre": "Melodic Trap",
        "related": ["Playboi Carti", "Lil Uzi Vert", "Trippie Redd"],
        "tags": ["#pierrebourne","#pierretypebeat","#sossehouse","#pluto","#sossa"],
    },
    # ── EMO RAP ──────────────────────────────────────────────────────
    "Wifisfuneral": {
        "genre": "Emo Rap",
        "related": ["Snot", "Pouya", "Ghostemane", "Xavier Wulf"],
        "tags": ["#wifisfuneral","#wifistypebeat","#emorap","#cloudrap","#sadsounds"],
    },
    "Snot": {
        "genre": "Emo Rap",
        "related": ["Wifisfuneral", "Pouya", "Xavier Wulf", "Trippie Redd"],
        "tags": ["#snot","#snottypebeat","#nimbustype","#emorap","#altrap"],
    },
    "Pouya": {
        "genre": "Emo Rap",
        "related": ["Ghostemane", "Fat Nick", "Wifisfuneral", "Night Lovell"],
        "tags": ["#pouya","#pouyatypebeat","#undergroundrap","#darkrap"],
    },
    "Night Lovell": {
        "genre": "Emo Rap",
        "related": ["Pouya", "Xavier Wulf", "Eddy Baker"],
        "tags": ["#nightlovell","#nightlovelltype","#darktrap","#coldnightfall"],
    },
    # ── UK DRILL ──────────────────────────────────────────────────────
    "Central Cee": {
        "genre": "UK Drill",
        "related": ["Dave", "AJ Tracey", "Digga D", "Unknown T"],
        "tags": ["#centralcee","#centralceetypebeat","#ukdrill","#23type","#londontype"],
    },
    "Dave": {
        "genre": "UK Drill",
        "related": ["Central Cee", "Stormzy", "AJ Tracey", "Santan Dave"],
        "tags": ["#davetypebeat","#ukdrill","#psychodrama","#santan","#ukrap"],
    },
    "Digga D": {
        "genre": "UK Drill",
        "related": ["Central Cee", "Tion Wayne", "Unknown T"],
        "tags": ["#diggad","#diggadtypebeat","#ukdrill","#drilluk","#london"],
    },
    # ── BROOKLYN DRILL ────────────────────────────────────────────────
    "Pop Smoke": {
        "genre": "Brooklyn Drill",
        "related": ["Fivio Foreign", "Bizzy Banks", "Kay Flock", "50 Cent"],
        "tags": ["#popsmoke","#popsmoketype","#brooklyndrill","#woo","#nyc"],
    },
    "Fivio Foreign": {
        "genre": "Brooklyn Drill",
        "related": ["Pop Smoke", "Quavo", "Lil Tjay", "Kay Flock"],
        "tags": ["#fiviotyped","#fivioforeign","#brooklyndrill","#bop","#nydrill"],
    },
    "Lil Tjay": {
        "genre": "Brooklyn Drill",
        "related": ["A Boogie", "Pop Smoke", "Polo G", "Fivio Foreign"],
        "tags": ["#liltjay","#liltjaytypebeat","#nyrap","#tjayvibes","#bronx"],
    },
    # ── RAP ─────────────────────────────────────────────────────────
    "Drake": {
        "genre": "Rap",
        "related": ["21 Savage", "Future", "Travis Scott", "Lil Baby"],
        "tags": ["#drake","#draketypebeat","#ovo","#certified","#drakevibes"],
    },
    "Travis Scott": {
        "genre": "Rap",
        "related": ["Don Toliver", "Drake", "Kid Cudi", "Quavo"],
        "tags": ["#travisscott","#travisscotttypebeat","#cactusjack","#utopia","#astroworld"],
    },
    "JID": {
        "genre": "Rap",
        "related": ["J Cole", "Dreamville", "Kenny Mason", "Bas"],
        "tags": ["#jid","#jidtypebeat","#dreamville","#diCaprio","#jidvibes"],
    },
    "J Cole": {
        "genre": "Rap",
        "related": ["JID", "Dreamville", "Kendrick Lamar", "Bas"],
        "tags": ["#jcole","#jcoletypebeat","#dreamville","#4youreyes","#colevibes"],
    },
    "Kendrick Lamar": {
        "genre": "Rap",
        "related": ["J Cole", "SZA", "Baby Keem", "ScHoolboy Q"],
        "tags": ["#kendrick","#kendricktypebeat","#tde","#gkmc","#pgLang"],
    },
    "Baby Keem": {
        "genre": "Rap",
        "related": ["Kendrick Lamar", "Travis Scott", "Pink Siifu"],
        "tags": ["#babykeem","#babykeemtypebeat","#pglang","#melodic","#keemvibes"],
    },
    # ── R&B ──────────────────────────────────────────────────────────
    "The Weeknd": {
        "genre": "R&B",
        "related": ["Don Toliver", "Drake", "SZA", "H.E.R."],
        "tags": ["#theweeknd","#weekndtypebeat","#xo","#starboy","#weekndvibes"],
    },
    "SZA": {
        "genre": "R&B",
        "related": ["The Weeknd", "Kendrick Lamar", "H.E.R.", "Summer Walker"],
        "tags": ["#sza","#szatypebeat","#tde","#sos","#szavibes"],
    },
    "Bryson Tiller": {
        "genre": "R&B",
        "related": ["The Weeknd", "Drake", "Summer Walker", "6LACK"],
        "tags": ["#brysontiller","#trapsoul","#TRAPSOUL","#brysonvibes"],
    },
    # ── PHONK ────────────────────────────────────────────────────────
    "Ghostemane": {
        "genre": "Phonk",
        "related": ["Pouya", "Wifisfuneral", "City Morgue", "Night Lovell"],
        "tags": ["#ghostemane","#ghostemanetypebeat","#phonk","#industrial","#darkrap"],
    },
    "Kordhell": {
        "genre": "Phonk",
        "related": ["Ghostemane", "Sxmpra", "Memphis Cult"],
        "tags": ["#kordhell","#kordhelltype","#phonk","#aggressivephonk","#darkphonk"],
    },
    # ── AFROBEATS ────────────────────────────────────────────────────
    "Burna Boy": {
        "genre": "Afrobeats",
        "related": ["WizKid", "Davido", "Omah Lay", "Tems"],
        "tags": ["#burnaboy","#burnaboytype","#afrobeats","#african","#spaceship"],
    },
    "WizKid": {
        "genre": "Afrobeats",
        "related": ["Burna Boy", "Davido", "Drake", "Tems"],
        "tags": ["#wizkid","#wizkidtypebeat","#afrobeats","#essence","#starboy"],
    },
}

# ── Banque de noms de beats par genre ─────────────────────────────────
BEAT_NAMES = {
    "Trap": [
        "Ghost","Drip","Midas","Phantom","Eclipse","Blaze","Venom",
        "Warfare","Pressure","Chains","Reaper","Shadow","Crown",
        "Greed","Empire","Sins","Demons","Aura","Savage","Cement",
        "Hustle","Grind","Rich","Money","Cold","Ruthless",
    ],
    "Melodic Trap": [
        "Eternal","Void","Orbit","Neon","Afterglow","Levitate",
        "Portal","Dimension","Starfall","Vapor","Cosmic","Drift",
        "Ascend","Hollow","Mirror","Fragment","Signal","Echo",
        "Prism","Aurora","Zenith","Halo","Fade","Blur","Warp",
    ],
    "Emo Rap": [
        "Scars","Bleeding","Numb","Static","Isolation","Decay",
        "Hollow","Disconnected","Serotonin","Lithium","Vacant",
        "Tears","Fading","Broken","Empty","Lost","Crash","OD",
    ],
    "UK Drill": [
        "No Hook","Nightshift","Pressure","Exposure","Lurk",
        "OT","Block","Moving","Trapping","Splash","Opps","Trenches",
        "Mandem","Roads","Blem",
    ],
    "Brooklyn Drill": [
        "Woo","BP","Wave","Bando","Slide","Flex","Bag",
        "Block","Smoke","Ops","Deli","Concrete","Uptown",
    ],
    "Rap": [
        "Vision","Blueprint","Legacy","Truth","Wisdom","Crown",
        "Dynasty","Icon","Scholar","Canvas","Frequency",
        "Spectrum","Balance","Clarity","Flow","Bars","Cipher",
    ],
    "R&B": [
        "Midnight","Velvet","Silk","Devotion","Obsession","Desire",
        "Surrender","Tender","Honey","Satin","Warmth","Bliss",
        "Euphoria","Serenity","Intimate","Feel","Forever",
    ],
    "Phonk": [
        "Drift","Specter","Skull","Vapor","Reaper","Haunted",
        "Cursed","Static","Glitch","Dead City","Ghost Ride",
        "666","Mortuary","Overdrive","Revenant",
    ],
    "Afrobeats": [
        "Lagos","Sunshine","Dance","Vibe","Summer","Paradise",
        "Groove","Gold","Tropical","Fire","Jollof","Afro Love",
    ],
}

# Genres supplémentaires pour auto — fallback sur Trap
for _g in ("Melodic","Dark Trap","Psychedelic Trap","NY Rap","Trap Soul"):
    if _g not in BEAT_NAMES:
        BEAT_NAMES[_g] = BEAT_NAMES["Trap"]


# ══════════════════════════════════════════════════════════════════════
# GÉNÉRATION AUTOMATIQUE — 0 clé API nécessaire
# ══════════════════════════════════════════════════════════════════════

def generate_auto(genre=None, artist1_hint="", artist2_hint="",
                  free=True, contact="", channel="") -> dict:
    """
    Génère tout (titre, description, hashtags YT + IG) automatiquement.
    100 % algorithmique — aucune clé API requise.
    Chaque appel donne un résultat différent.
    """
    all_artists = list(ARTISTS_DB.keys())

    # ─ Choisir artiste 1 ──────────────────────────────────────────────
    if artist1_hint and artist1_hint.strip():
        a1 = artist1_hint.strip()
        a1_data = ARTISTS_DB.get(a1, {})
        if not genre:
            genre = a1_data.get("genre", "Trap")
    else:
        # Filtrer par genre si fourni
        if genre and genre != "Aléatoire":
            pool = [a for a, d in ARTISTS_DB.items()
                    if d.get("genre","").lower() == genre.lower()]
        else:
            pool = all_artists

        if not pool:
            pool = all_artists
        a1 = random.choice(pool)
        a1_data = ARTISTS_DB[a1]
        if not genre or genre == "Aléatoire":
            genre = a1_data.get("genre", "Trap")

    # ─ Choisir artiste 2 (60 % de chance) ───────────────────────────
    if artist2_hint and artist2_hint.strip():
        a2 = artist2_hint.strip()
    elif random.random() < 0.60:
        related = a1_data.get("related", [])
        candidates = [r for r in related if r != a1 and r in ARTISTS_DB]
        if not candidates:
            candidates = [r for r in related if r != a1]
        a2 = random.choice(candidates) if candidates else ""
    else:
        a2 = ""

    # ─ Nom du beat ───────────────────────────────────────────────────
    name_pool = BEAT_NAMES.get(genre)
    if not name_pool:
        name_pool = BEAT_NAMES.get("Trap", ["Wave"])
    beat_name = random.choice(name_pool)

    # ─ Construire le contenu ─────────────────────────────────────────
    title     = generate_beat_title(a1, beat_name, a2, free)
    tags_list = generate_beat_hashtags(a1, a2, genre, count=30)
    desc      = generate_beat_description(a1, beat_name, a2, genre,
                                           contact, free, channel)
    ig_cap    = generate_beat_ig_caption(a1, beat_name, a2, free)
    ig_tags   = format_ig_tags(tags_list)
    yt_tags   = format_yt_tags(tags_list)

    return {
        "yt_title":       title,
        "yt_tags":        yt_tags,
        "yt_description": desc,
        "ig_caption":     ig_cap,
        "ig_hashtags":    ig_tags,
        # méta — utilisées pour pre-fill le formulaire
        "artist1":        a1,
        "artist2":        a2,
        "beat_name":      beat_name,
        "genre":          genre,
    }


# ── Catégories YouTube (inchangé) ─────────────────────────────────────
HASHTAGS = {
    "Music": [
        "#music","#newmusic","#musician","#song","#beat","#producer",
        "#hiphop","#rnb","#trap","#rap","#beats","#beatmaker","#studio",
        "#recording","#artist","#soundcloud","#spotify","#playlist",
        "#vibes","#flow","#musicvideo","#newartist","#unsigned","#indie",
        "#underground","#freebeat","#typebeat","#lofi","#drill","#afrobeats",
    ],
    "Gaming": [
        "#gaming","#gamer","#gameplay","#videogames","#twitch","#ps5",
        "#xbox","#pcgaming","#streamer","#esports","#fps","#rpg",
        "#fortnite","#minecraft","#valorant","#cod","#gta","#lol",
        "#gamingcommunity","#livestream","#speedrun","#retrogaming",
        "#indiegame","#gamingsetup","#controller","#console","#steam",
    ],
    "People & Blogs": [
        "#vlog","#lifestyle","#daily","#motivation","#life","#youtube",
        "#content","#creator","#viral","#trending","#day","#routine",
        "#grwm","#aesthetic","#fyp","#foryou","#explore","#reels",
        "#instagood","#goodvibes","#mindset","#hustle","#success",
        "#entrepreneur","#blog","#blogging","#vlogger","#contentcreator",
    ],
    "Entertainment": [
        "#entertainment","#funny","#comedy","#viral","#trending","#meme",
        "#lol","#fun","#humor","#relatable","#reaction","#shorts",
        "#challenge","#prank","#skit","#parody","#highlight","#clip",
        "#satisfying","#amazing","#wow","#mustwatch","#fyp","#share",
    ],
    "Science & Tech": [
        "#tech","#technology","#science","#programming","#coding","#python",
        "#developer","#ai","#machinelearning","#startup","#innovation",
        "#gadgets","#review","#tutorial","#howto","#learntocode",
        "#javascript","#webdev","#software","#hardware","#cybersecurity",
    ],
    "Education": [
        "#education","#learning","#tutorial","#howto","#tips","#tricks",
        "#knowledge","#study","#school","#student","#teacher","#lesson",
        "#explainer","#elearning","#skill","#growth","#selfdevelopment",
        "#mindset","#reading","#books","#motivation",
    ],
    "Sports": [
        "#sports","#fitness","#gym","#workout","#training","#athlete",
        "#motivation","#health","#fit","#crossfit","#running","#soccer",
        "#basketball","#football","#tennis","#boxing","#mma","#cycling",
    ],
}

# ══════════════════════════════════════════════════════════════════════
# CONFIG & PROFILS
# ══════════════════════════════════════════════════════════════════════

def load_config():
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"api_key": ""}

def save_config(cfg):
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

def load_profiles() -> dict:
    """Retourne tous les profils sauvegardés."""
    if PROFILES_FILE.exists():
        try: return json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
        except: pass
    return {}

def save_profile(name: str, data: dict):
    """Sauvegarde ou écrase un profil."""
    profiles = load_profiles()
    profiles[name] = data
    PROFILES_FILE.write_text(
        json.dumps(profiles, indent=2, ensure_ascii=False), encoding="utf-8")

def delete_profile(name: str):
    """Supprime un profil."""
    profiles = load_profiles()
    profiles.pop(name, None)
    PROFILES_FILE.write_text(
        json.dumps(profiles, indent=2, ensure_ascii=False), encoding="utf-8")

def profile_names() -> list:
    return sorted(load_profiles().keys())

# ══════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR TYPE BEAT
# ══════════════════════════════════════════════════════════════════════

def generate_beat_title(artist1: str, beat_name: str,
                        artist2: str = "", free: bool = True) -> str:
    """[FREE] ARTIST1 X ARTIST2 TYPE BEAT "NAME" """
    prefix  = "[FREE] " if free else ""
    a1      = artist1.strip().upper()
    a2      = f" X {artist2.strip().upper()}" if artist2.strip() else ""
    name    = beat_name.strip().upper()
    return f'{prefix}{a1}{a2} TYPE BEAT "{name}"'


def generate_beat_hashtags(artist1: str, artist2: str = "",
                            genre: str = "Trap", custom: str = "",
                            count: int = 30) -> list:
    """
    Hashtags ciblés type beat.
    Ordre : custom → artiste1 → artiste2 → genre → base
    """
    tags = []

    # Custom en premier
    if custom:
        tags += [t.strip() for t in custom.split()
                 if t.strip().startswith("#")]

    # Tags artiste 1
    a1_slug = artist1.strip().lower().replace(" ", "")
    artist_pool = ARTIST_TAGS.get(artist1.strip(), [])
    if not artist_pool:
        artist_pool = [f"#{a1_slug}typebeat", f"#{a1_slug}type",
                       f"#{a1_slug}beat", f"#{a1_slug}"]
    for t in artist_pool:
        if t not in tags: tags.append(t)

    # Tags artiste 2
    if artist2.strip():
        a2_slug = artist2.strip().lower().replace(" ", "")
        artist2_pool = ARTIST_TAGS.get(artist2.strip(), [])
        if not artist2_pool:
            artist2_pool = [f"#{a2_slug}typebeat", f"#{a2_slug}type",
                            f"#{a2_slug}beat", f"#{a2_slug}"]
        for t in artist2_pool:
            if t not in tags: tags.append(t)

    # Tags genre
    genre_pool = ARTIST_TAGS.get(genre.strip(), [])
    g_slug = genre.strip().lower().replace(" ", "")
    if not genre_pool:
        genre_pool = [f"#{g_slug}beat", f"#{g_slug}type", f"#{g_slug}music"]
    for t in genre_pool:
        if t not in tags: tags.append(t)

    # Tags de base
    for t in BASE_BEAT_TAGS:
        if t not in tags: tags.append(t)

    return tags[:count]


def generate_beat_description(artist1: str, beat_name: str,
                               artist2: str = "", genre: str = "Trap",
                               contact: str = "", free: bool = True,
                               channel: str = "") -> str:
    """Description YouTube optimisée pour type beat."""
    title   = generate_beat_title(artist1, beat_name, artist2, free)
    a2_str  = f" x {artist2}" if artist2.strip() else ""
    tags    = generate_beat_hashtags(artist1, artist2, genre, count=25)
    tags_str = " ".join(tags)

    desc = f"{title}\n\n"

    if contact:
        desc += f"📧 Licensing / Contact : {contact}\n"

    sep = "─" * 44
    desc += (
        f"🎵 {artist1}{a2_str} Type Beat — {genre}\n"
        f"Free for non-profit use · Contact for exclusive licensing\n\n"
        f"{sep}\n\n"
        f"{tags_str}\n\n"
        f"{sep}\n"
        f"© {channel or beat_name} — All rights reserved"
    )
    return desc.strip()


def generate_beat_ig_caption(artist1: str, beat_name: str,
                              artist2: str = "", free: bool = True) -> str:
    """Légende Instagram courte et percutante."""
    a2 = f" x {artist2}" if artist2.strip() else ""
    prefix = "🆓 " if free else "🔥 "
    return (
        f'{prefix}{artist1}{a2} type beat — "{beat_name}"\n'
        f"#typebeat #freebeat #beatmaker #trap"
    )

# ══════════════════════════════════════════════════════════════════════
# GÉNÉRATION IA (Anthropic Claude)
# ══════════════════════════════════════════════════════════════════════

def generate_ai(title, category, platform="youtube", api_key="",
                language="fr", extra_context="",
                artist1="", artist2="", genre="", beat_name=""):
    """
    Génère SEO complet avec Claude AI.
    Prend en compte les infos type beat si fournies.
    """
    if not api_key:
        raise RuntimeError(
            "Aucune clé API Anthropic.\n"
            "Configure-la dans l'onglet SEO → IA.")
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("Package 'anthropic' manquant.\nLance installer.bat.")

    client   = anthropic.Anthropic(api_key=api_key)
    lang_note = "in English" if language == "en" else "en français"

    beat_ctx = ""
    if artist1:
        a2_str  = f" x {artist2}" if artist2 else ""
        beat_ctx = (
            f"C'est un TYPE BEAT : {artist1}{a2_str}"
            + (f", genre {genre}" if genre else "")
            + (f', nom du beat : "{beat_name}"' if beat_name else "")
            + ". Format titre : [FREE] ARTIST TYPE BEAT \"NAME\"."
        )

    if platform in ("youtube", "both"):
        yt_prompt = f"""Tu es un expert SEO YouTube spécialisé dans les type beats / instrumentales rap.
Réponds {lang_note}. {beat_ctx}
Vidéo : "{title}" — Catégorie : "{category}"
{f'Contexte : {extra_context}' if extra_context else ''}

Génère en JSON valide UNIQUEMENT (pas d'autre texte) :
{{
  "yt_title": "titre type beat accrocheur max 100 chars, format [FREE] ARTIST TYPE BEAT \\"NAME\\"",
  "yt_description": "description 200-300 mots : titre, infos licensing, tags naturels. PAS de conseils génériques, PAS de subscribe/like. Juste les infos essentielles + tags.",
  "yt_tags": "30 tags YouTube sans # séparés par virgule, du plus ciblé au plus large"
}}"""
        msg = client.messages.create(
            model="claude-haiku-4-5", max_tokens=1200,
            messages=[{"role":"user","content":yt_prompt}])
        yt_result = _parse_json(msg.content[0].text)
    else:
        yt_result = {}

    if platform in ("instagram", "both"):
        ig_prompt = f"""Tu es un expert marketing Instagram spécialisé beats/rap.
Réponds {lang_note}. {beat_ctx}
Beat : "{title}"

Génère en JSON valide UNIQUEMENT :
{{
  "ig_caption": "légende 80-150 chars percutante avec 1-2 emojis, pas de hashtags ici",
  "ig_hashtags": "30 hashtags Instagram ciblés type beat : artiste + genre + base, séparés par espace"
}}"""
        msg2 = client.messages.create(
            model="claude-haiku-4-5", max_tokens=600,
            messages=[{"role":"user","content":ig_prompt}])
        ig_result = _parse_json(msg2.content[0].text)
    else:
        ig_result = {}

    return {**yt_result, **ig_result}


def _parse_json(text):
    text  = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except: pass
    return {}

# ══════════════════════════════════════════════════════════════════════
# HELPERS FORMAT (conservés pour compatibilité)
# ══════════════════════════════════════════════════════════════════════

def get_hashtags(category="Music", custom="", count=30):
    bank  = HASHTAGS.get(category, HASHTAGS["Music"])
    extra = [t.strip() for t in custom.split() if t.strip().startswith("#")]
    merged = extra + [h for h in bank if h not in extra]
    return merged[:count]

def format_yt_tags(tags_list):
    return ", ".join(t.lstrip("#") for t in tags_list)

def format_ig_tags(tags_list):
    return " ".join(t if t.startswith("#") else f"#{t}" for t in tags_list)

def auto_description_yt(title, category, channel_name=""):
    """Fallback description sans IA."""
    return generate_beat_description(title, title, genre=category,
                                     channel=channel_name)

def auto_caption_ig(title, tags_list):
    tags = " ".join(tags_list[:4])
    return f"🔥 {title}\n\n{tags}"
