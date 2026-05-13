# Depo yapısı

Aşağıdaki ağaç, **mantıksal** düzeni gösterir; `__pycache__`, `.venv`, `*.egg-info` gibi üretilmiş dosyalar `.gitignore` ile dışlanır.

```text
wraith/                          # repo kökü (çalışma dizini adı farklı olabilir)
├── pyproject.toml               # proje adı, bağımlılıklar, pytest, konsol script
├── README.md                    # hızlı kurulum + docs’a işaret (önerilir)
├── .gitignore
├── docs/                        # bu dokümantasyon
├── wraith_protocol/             # saf protokol: bayt, CRC, aydınlatma
│   ├── __init__.py              # analog dışa verilmez (bilinçli)
│   ├── crc.py
│   ├── packet.py
│   ├── lighting.py
│   └── analog.py                # yalnızca imza + NotImplementedError
├── wraith_core/                 # HID oturumu, kilit, yeniden bağlanma
│   ├── __init__.py
│   ├── exceptions.py
│   └── connection_manager.py
├── wraith_cli/                  # `wraith` konsol komutu
│   ├── __init__.py
│   └── main.py
├── wraith_api/                  # Faz 2: FastAPI iskeleti (şimdilik boş not)
│   └── __init__.py
├── tests/
│   ├── test_crc.py
│   ├── test_lighting.py
│   └── test_integration.py      # @pytest.mark.integration
├── examples/
│   └── w75_demo.py              # eski monolit demo davranışının SDK ile gösterimi
└── dec_software/
    └── witmodSdk.dll.c          # decompile edilmiş C dökümü (çok büyük dosya)
```

## Kökte artık olmayanlar

Eski tek dosyalı **`w75.py`** kaldırıldı. Davranış **`examples/w75_demo.py`** ve **`wraith`** CLI ile sürdürülür. Böylece:

- Paket import yolları net kalır.
- “Script mi kütüphane mi” karışıklığı azalır.

## `dec_software/witmodSdk.dll.c`

- **Ne:** Windows tarafı SDK’nın **decompile edilmiş metni** — **üretim kaynak kodu değildir**; satıcı veya derleyici çıktısı olarak doğrulanabilir bir kaynak ağacı değildir.
- **Ne için:** Komut kodları, buffer düzeni, CRC vb. **ipuçları**; her iddia ayrı kanıt ister ([11-command-map.md](11-command-map.md)).
- **Dikkat:** On binlerce satır; tam okuma yerine **hedefli arama** (komut byte’ı, sabit stringler) daha verimli.
- **Lisans / hukuk:** Kendi hukuk danışmanınıza danışın; tersine mühendislik ürünü **çalıştırılabilir SDK olarak dağıtılmaz**; yalnızca referans hammaddesi.
