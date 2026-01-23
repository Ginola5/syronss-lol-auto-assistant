# ⚡ LoL Auto Assistant

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

Modern, şık ve gelişmiş bir **League of Legends** otomasyon aracı. Maçları otomatik kabul eder, istediğiniz şampiyonu seçer veya yasaklar.

![UI Preview](https://img.shields.io/badge/UI-Modern%20Dark%20Theme-blueviolet)

## ✨ Özellikler

### 🎮 Temel Özellikler
- **Otomatik Kabul (Auto Accept):** Maç bulunduğunda otomatik kabul eder
  - Gecikme ayarı (0-10 saniye)
  - Ses bildirimi
- **Otomatik Seçim (Auto Pick):** Belirlediğiniz şampiyonu otomatik seçer
  - Çoklu şampiyon listesi desteği (öncelik sırasına göre)
- **Otomatik Yasaklama (Auto Ban):** Belirlediğiniz şampiyonu otomatik yasaklar
  - Çoklu şampiyon listesi desteği

### 🔥 Gelişmiş Özellikler
- **Spell Tracker:** Düşman summoner spell cooldown takibi
  - Hotkey desteği (Ctrl+1-5 ve Ctrl+6-0)
  - Gerçek zamanlı cooldown gösterimi
  - Spell hazır bildirim sesi
- **Sistem Tepsisi:** Arka planda çalışma
- **Çoklu Dil Desteği:** Türkçe ve İngilizce
- **İstatistikler:** Kabul edilen maç, seçilen/yasaklanan şampiyon sayısı
- **Ayar Kaydetme:** Otomatik ayar saklama

## 📋 Gereksinimler

- **Windows** İşletim Sistemi
- **Python 3.8+**
- League of Legends Client

## 🚀 Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/Syronss/syronss-lol-auto-assistant.git
cd syronss-lol-auto-assistant
```

2. Sanal ortam oluşturun (önerilir):
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

## 💻 Kullanım

Uygulamayı başlatmak için:
```bash
python src/main.py
```

### ⌨️ Hotkey'ler (Spell Tracker)

| Hotkey | İşlev |
|--------|-------|
| `Ctrl+1` | Top Flash kullanıldı |
| `Ctrl+2` | Jungle Flash kullanıldı |
| `Ctrl+3` | Mid Flash kullanıldı |
| `Ctrl+4` | ADC Flash kullanıldı |
| `Ctrl+5` | Support Flash kullanıldı |
| `Ctrl+6` | Top Spell2 kullanıldı |
| `Ctrl+7` | Jungle Spell2 kullanıldı |
| `Ctrl+8` | Mid Spell2 kullanıldı |
| `Ctrl+9` | ADC Spell2 kullanıldı |
| `Ctrl+0` | Support Spell2 kullanıldı |

## 📦 EXE Oluşturma

Tek dosya çalıştırılabilir (.exe) oluşturmak için:
```bash
pyinstaller --noconfirm --onefile --windowed --name "LoLAutoAssistant" --paths "src" --add-data "src;src" --hidden-import "customtkinter" src/main.py
```

## 📁 Proje Yapısı

```
syronss-lol-auto-assistant/
├── src/
│   ├── main.py           # Ana uygulama ve UI
│   ├── bot_logic.py      # Bot mantığı (auto accept/pick/ban)
│   ├── lcu_connector.py  # League Client API bağlantısı
│   ├── spell_tracker.py  # Düşman spell takibi
│   ├── languages.py      # Çoklu dil desteği
│   ├── settings.py       # Ayar yönetimi
│   ├── sounds.py         # Ses bildirimleri
│   └── utils.py          # Yardımcı fonksiyonlar
├── requirements.txt
├── LICENSE
└── README.md
```

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'e push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje [Apache License 2.0](LICENSE) altında lisanslanmıştır.

**Önemli:** Bu projeyi kullanarak türetilmiş çalışmalar oluşturursanız, orijinal projeye referans vermeniz **zorunludur**.

## 👨‍💻 Geliştirici

**Syronss**
- GitHub: [@Syronss](https://github.com/Syronss)
- Discord: `gorkemw.`

## ⚠️ Yasal Uyarı

Bu yazılım **Riot Games** tarafından onaylanmamıştır ve Riot Games'in veya League of Legends'ın yapımında veya yönetiminde resmi olarak yer alan herhangi birinin görüşlerini veya fikirlerini yansıtmaz. 

**League of Legends** ve **Riot Games**, Riot Games, Inc.'nin ticari markaları veya tescilli ticari markalarıdır.

Bu aracı kullanmak kendi sorumluluğunuzdadır. Hesap güvenliği konusunda dikkatli olun.

---

<p align="center">
  Made by <a href="https://github.com/Syronss">Syronss</a>
</p>
