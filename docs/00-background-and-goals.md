# Arka plan ve hedefler

## Bu proje ne?

**wraith-w75**, Wraith **W75** ve **W75 Pro** (Hall effect / analog özellikli) klavyelerin **resmi Windows yazılımına (witmod / kapalı ekosistem)** dayanmadan, özellikle **macOS** üzerinde **vendor HID** kanalıyla kontrol edilmesi için geliştirilen **açık kaynaklı** bir Python paketidir.

v0.1’de somut olarak çalışan parça: **RGB / ışıklandırma** komutlarının doğru 64 baytlık HID raporu ve **CRC-16/XMODEM** ile cihaza gönderilmesi (**verified** — golden + test donanımı; CRC’nin SDK içi izolasyonu yok — bkz. [03-wraith-protocol.md](03-wraith-protocol.md)). Komut ve selector eşlemesi: [11-command-map.md](11-command-map.md).

## Neden var?

- Resmi uygulama **macOS’ta yok** veya sınırlı; kullanıcılar donanımı tam kullanamıyor.
- Protokol **belgelendirilmemiş**; Windows DLL ve cihaz davranışı üzerinden **tersine mühendislik** gerekiyor.
- Açık kaynak: topluluk aynı protokolü doğrulayabilir, genişletebilir, başka dillere port edebilir.

## Uzun vadede hedeflenen (henüz tamamlanmamış)

- Analog ayarlar (actuation, rapid trigger), pil, polling rate gibi **ek HID komutları** (DLL’den veya USB yakalama ile doğrulanmalı).
- **HTTP API** (ör. Next.js paneli) — `wraith_api` paketi için ayrılmış.
- **Snap Tap / SOCD** gibi davranışlar ayrı bir spike / repo olarak düşünülmüştü; bu repoda yok.

## Bu dokümantasyon kime?

- Repoyu ilk kez açan birine.
- Bir yıl sonra tekrar dönen sana.
- CI veya paketleme hatası ayıklayan birine.

Tarih ve sürüm: paket sürümü `pyproject.toml` içindeki `version` alanına bakın; bu metinler belirli bir commit anına göre yazılmış olabilir.
