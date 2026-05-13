# Tasarım kararları ve bilinçli olarak yapılmayanlar

Bu bölüm bir “ADR özeti” gibi düşünülebilir: tartışılmış ve seçilmiş yönler. Protokol iddialarında kanıt etiketleri için [11-command-map.md](11-command-map.md) sözlüğüne bakın.

## CLI → core → protocol zorunluluğu

- **Karar:** CLI `wraith_protocol` import etmez.
- **Gerekçe:** Tek HID yazım kapısı, kilit, yeniden bağlanma tek yerde kalsın; aksi halde yarın eklenecek HTTP API ile çift yazım riski doğar.

## `crcmod` kaldırıldı

- **Karar:** CRC saf Python.
- **Gerekçe:** Tek doğruluk kaynağı, daha az bağımlılık, golden test ile legacy paketlere eşdeğerlik (**verified** davranışsal; SDK içi izolasyon yok — bkz. [03-wraith-protocol.md](03-wraith-protocol.md)).

## `w75.py` silindi, shim yok

- **Karar:** Kökte tek dosyalı script **kaldırıldı**; yerine paket + CLI + örnekler.
- **Gerekçe:** “Script mi paket mi” ikilemi; import yolu ve bakım. Davranış `examples/` + CLI’da.

## Bilinmeyen komut fuzzing yok

- **Karar:** Rastgele veya “sırayla dene” yaklaşımı yok.
- **Gerekçe:** Brick, profil bozulması veya garanti dışı donanım durumu riski. Ayrıntı: [08-reverse-engineering-sources.md](08-reverse-engineering-sources.md).

## Firmware / update / kalıcı profil yolları

- **Karar:** Bu repoda **expose edilmez**, CLI veya API ile tetiklenmez.
- **Gerekçe:** **unsafe** sonuçlar (kurtarılamaz durumlar dahil). DLL’de izler görülse bile kasıtlı olarak uygulanmaz ve dokümante edilse bile “kullanılabilir özellik” sayılmaz.

## `examples/` içinde assert yok

- **Karar:** Demo saf kalır; entegrasyon `tests/test_integration.py` + marker.
- **Gerekçe:** İki rolü aynı dosyada birleştirmek hem CI hem insan okuyucu için kafa karıştırıcıydı.

## `wraith_performance` / WebSocket / Next.js bu repoda yok

- **Karar:** v0.1 dışında bırakıldı veya sonraki faz.
- **Gerekçe:** SOCD Quartz/izin dünyası ayrı domain; WebSocket “analog veri” olmadan anlamsız; UI, API stabil olmadan erken.

## `analog.py` export edilmiyor

- **Karar:** Paket `__init__` dışına çıkmıyor.
- **Gerekçe:** Yanlışlıkla “hazır API” sanılmasını engellemek. Kök `README.md` içinde de **public API değildir** notu vardır.

## macOS `ctypes` yaması

- **Karar:** `import hid` sırasında geçici `LoadLibrary` yönlendirmesi.
- **Gerekçe:** Homebrew + PyPI `hid` kombinasyonunda kullanıcı deneyimi; `DYLD_*` ile herkese talimat dayatmaktan daha kontrollü (yine de “global patch” olduğu için dokümante edildi).

## `max_retries=None`

- **Karar:** Sınırsız yeniden denemeye izin.
- **Gerekçe:** Bazı ortamlarda sürekli bağlı kalma istenir; sınır isteyen `--max-retries` kullanır.

## Backoff tavanı 4 saniyede sabit

- **Karar:** 0.25 → … → 4 saniye sonra hep 4 saniye.
- **Gerekçe:** Agent’ın keyfi seçim yapmaması için planda sabitlendi; aşırı agresif / aşırı yavaş uçlardan kaçınma.
