# Yol haritası (özet)

Durum bilgisi `pyproject.toml` sürümü ve git tarihçesi ile doğrulanmalıdır; aşağısı **niyet** belgesidir.

## Tamamlanan (v0.1 çekirdeği)

- Paket yapısı: `wraith_protocol`, `wraith_core`, `wraith_cli`, `wraith_api` (iskele).
- RGB komutu (`0x07`), CRC, `ConnectionManager`, CLI `set-color` / `status`.
- pytest birim testleri + işaretli integration testi.
- macOS hidapi yükleme sorunları için ctypes tabanlı çözüm ve `Device` API uyumu.

## Faz 2 — HTTP API (tetikleyici: CLI başka makinede doğrulandıktan sonra)

- `wraith_api/app.py` (FastAPI) veya eşdeğeri.
- Önerilen uçlar: `POST /set-rgb`, `GET /status`.
- **Zorunlu mimari kural (tekrar):** HTTP route’ları veya handler’ları **`wraith_protocol` içinden doğrudan import etmez** (`lighting`, `packet`, `crc` dahil). Tek yazım ve kilit yolu **`wraith_core`** (`ConnectionManager.set_rgb` vb.) üzerinden gider — CLI ile aynı model ([02-architecture-and-data-flow.md](02-architecture-and-data-flow.md)).

## Faz 3 — Analog ve ilgili API (tetikleyici: RE ile komut byte’ları doğrulandı)

- `analog.py` gövdelerinin doldurulması.
- İstenirse: `POST /set-actuation`, `POST /set-rapid-trigger` (yalnızca doğrulandıktan sonra).

## Bilinçli olarak bu repoda tutulmayanlar

- **SOCD / Snap Tap** yazılım simülasyonu (ayrı spike).
- **Next.js** paneli (API kararlılığı sonrası).
- **Analog WebSocket akışı** (önce okunabilir analog kaynak).

## Katkı verenlere not

- Yeni komut: [08-reverse-engineering-sources.md](08-reverse-engineering-sources.md) checklist’i + [11-command-map.md](11-command-map.md) güncellemesi.
- Büyük DLL diff’lerini PR’da gerekmedikçe taşımayın; referans dosya zaten var.
