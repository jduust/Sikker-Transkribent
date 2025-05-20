# 🔐 Sikker-Transkribent

**Sikker-Transkribent** er en lokal, GDPR-venlig løsning til automatisk transkribering og diarisation (hvem sagde hvad hvornår?) af lydfiler – helt uden cloud eller dataoverførsel. Systemet er bygget til dansk tale og kører udelukkende lokalt på din egen maskine.

---

## 🛡️ Hvorfor denne løsning?

I mange professionelle og offentlige sammenhænge er cloud-baserede løsninger som OpenAI, Whisper via web eller Google Speech ikke acceptable pga. GDPR og datasikkerhedskrav.

**Sikker-Transkribent** sikrer:

- 📁 **Lokal databehandling** – intet sendes til internettet
- 🇩🇰 **Støtte for dansk sprog**
- 🔍 **Automatisk talegenkendelse og taleridentifikation (diarisation)**
- 🧾 **Output i flere formater**: `.txt`, `.srt`, og en kombineret lyd+subtitle video (`.mp4`)
- ✅ **Ingen afhængighed af API-nøgler eller online tjenester**

---

## 🧰 Teknologier og komponenter

| Komponent        | Funktion                          |
|------------------|-----------------------------------|
| `faster-whisper` | Hurtig og præcis transkription    |
| `resemblyzer`    | Taler-diarisation vha. stemmeprint |
| `moviepy`        | Kombinerer lyd og undertekster til video |
| `ffmpeg`         | Eksternt værktøj til mediebehandling (kræves) |

---

## 🚀 Installation

### 1. Opsæt Python-miljø (Windows/macOS/Linux)

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 2. Sørg for opdateret `pip`

```bash
python -m pip install --upgrade pip
```

### 3. Kræver: C++ 14.3+ compiler

Hvis du bruger Windows og ikke allerede har det:

* Installer [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* Sørg for at vælge **C++ build tools** under installationen

### 4. Installer afhængigheder

```bash
pip install -r requirements.txt
```

**`requirements.txt` bør indeholde:**

```txt
faster-whisper
resemblyzer
numpy
scipy
moviepy
pydub
tqdm
```

---

## 📂 Brug

1. Læg dine lydfiler filer i mappen `input/`
2. Kør scriptet:

```bash
python transcriber.py
```

3. Output genereres i `output/` som:

   * En `.srt` (undertekst)
   * En `.txt` (rå transkription)
   * En `.mp4` (lydfil + undertekster lagt over som video)

---

## 🧪 Eksempel

**Eksempel på transkriberet tekst:**

```
[00:00:03 - 00:00:07] Speaker 1: Hej og velkommen til mødet.
[00:00:08 - 00:00:11] Speaker 2: Tak – lad os gå i gang.
```

**Video output:**

* Du får en `.mp4`-fil hvor undertekster vises synkront med lyden.

---

## 🧾 GDPR-sikkerhed og datasikkerhed

Denne løsning er udviklet med fuld fokus på **databeskyttelse og overholdelse af GDPR**:

* Der sendes **ingen data til internettet**
* Ingen brug af cloud-tjenester eller API-kald
* Kan afvikles **offline** uden adgang til eksterne netværk
* Giver brugeren fuld kontrol over følsomme lyddata

Dette gør løsningen egnet til:

* Kommunale og statslige institutioner
* Sundhedsvæsen, retsvæsen, forskning
* Virksomheder med compliance-krav

---

## 🛠️ Øvrige noter

* Whisper large-v3 modellen kræver ca. 6–8 GB RAM for 1 times lyd

---

## 📄 Licens

Dette projekt er open source – brug det, udvid det, del det med omtanke.

---

**Udviklet med omhu i Danmark – for dig, der tager privatliv alvorligt.**