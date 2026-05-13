# Command map

Bu dosya, Wraith W75 / W75 Pro protokolünde tespit edilen **command selector** ve **internal command id** eşleşmelerini izler. Ayrıntılı kanıt seviyesi tanımları aşağıdadır; tablodaki **Durum** sütunu bu şemayı kullanır.

## Kanıt seviyeleri

| Seviye | Anlam |
|--------|--------|
| `verified` | Cihazda denenmiş ve beklenen davranış görülmüş |
| `observed` | DLL veya USB capture içinde görülmüş |
| `inferred` | Kod akışından çıkarılmış ama cihazda denenmemiş |
| `hypothesis` | Güçlü tahmin |
| `unsafe` | Denenmemeli veya firmware / profil riski var |

## Bilinen komutlar

| Selector | Alternative selector | Internal cmd | Alan | Durum | Risk | Kaynak | Not |
|----------|----------------------|----------------|------|--------|------|--------|-----|
| `0x06` | `0x6A` | `0x07` | lighting | verified | safe | legacy + device + SDK wrapper | RGB kontrolü; Python v0.1 doğrudan internal `0x07` üretir |
| `0x1C` | `0x80` | `0x40` | unknown | observed | unknown | SDK wrapper | Cihazda denenmedi |
| `0x1D` | `0x81` | `0x41` | unknown | observed | unknown | SDK wrapper | Cihazda denenmedi |
| `0x1E` | `0x82` | `0x42` | unknown | observed | unknown | SDK wrapper | Cihazda denenmedi |

**Report id `0x06` / “col06”:** Windows SDK tarafında bazı yollarda görülebilir (**observed**); bu repodaki varsayılan yol **report id `0x01`** ve golden paketlerle hizalıdır — `0x06` **varsayılan Python yolu değildir**.

## Kurallar

- `unsafe` veya riski `unknown` olan komutlar **cihazda kasıtlı olarak denenmez**.
- **Firmware / update / kalıcı profil yazımı** yolları bu repoda expose edilmez; ilgili komutlar dokümante edilse bile uygulanmaz (bkz. [09-decisions-and-non-goals.md](09-decisions-and-non-goals.md)).
- **Bilinmeyen command id fuzzing yok:** rastgele veya sırayla “deneme” yapılmaz.
- Yeni komut eklemek için [08-reverse-engineering-sources.md](08-reverse-engineering-sources.md) içindeki doğrulama checklist’i zorunludur.

## İlgili dokümanlar

- Normalizasyon tablosunun protokol notu: [03-wraith-protocol.md](03-wraith-protocol.md) (`SDK command normalization`).
- Windows yazım sarmalayıcısı notu: [08-reverse-engineering-sources.md](08-reverse-engineering-sources.md).
