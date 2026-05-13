# wraith-w75 — dokümantasyon dizini

Bu klasör, projeyi **başka bir geliştiriciye veya gelecekteki kendinize** devredebilmeniz için yazılmıştır: ne var, ne işe yarar, neden böyle tasarlandı, hangi sorunlar bilinerek kabul edildi.

## Okuma sırası (önerilen)

| # | Dosya | İçerik |
|---|--------|--------|
| 1 | [00-background-and-goals.md](00-background-and-goals.md) | Proje amacı, kapsam, motivasyon |
| 2 | [01-repository-structure.md](01-repository-structure.md) | Klasör ağacı, her bileşen |
| 3 | [02-architecture-and-data-flow.md](02-architecture-and-data-flow.md) | Katmanlar, akış, neden CLI → core |
| 4 | [03-wraith-protocol.md](03-wraith-protocol.md) | Paket yapısı, CRC, RGB, analog taslak |
| 5 | [04-wraith-core.md](04-wraith-core.md) | ConnectionManager, istisnalar, yeniden bağlanma |
| 6 | [05-cli-examples-and-packaging.md](05-cli-examples-and-packaging.md) | `wraith` CLI, `pyproject`, örnekler |
| 7 | [06-testing-and-ci.md](06-testing-and-ci.md) | pytest, integration işareti, golden testler |
| 8 | [07-macos-hid-and-troubleshooting.md](07-macos-hid-and-troubleshooting.md) | hidapi, ctypes yaması, `Device` API, sık hatalar |
| 9 | [08-reverse-engineering-sources.md](08-reverse-engineering-sources.md) | DLL dökümü, protokol kanıtı |
| 10 | [09-decisions-and-non-goals.md](09-decisions-and-non-goals.md) | Mimari kararlar ve bilinçli olarak yapılmayanlar |
| 11 | [10-roadmap.md](10-roadmap.md) | Faz 2 API, Faz 3 analog, bilinmeyenler |
| 12 | [11-command-map.md](11-command-map.md) | Komut selector / internal id, kanıt seviyeleri, risk kuralları |
| 13 | [12-hardware-compatibility.md](12-hardware-compatibility.md) | `wraith debug` tanılama, macOS, issue çıktıları |

Kök dizindeki [README.md](../README.md) kısa kurulum ve komutlara odaklanır; derinlemesine açıklama buradadır.
