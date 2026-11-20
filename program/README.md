# Variant 16 — Operational video-stream analysis (СМО)

**Formula:** `ИБ  ИЗ2  ПЗ1  Д1ОЗ1  Д1ОО3  Д2П2  Д2Б2  ОР1  ОД1`

Cameras continuously send frames to GPU nodes. Waiting frames sit in a **ring buffer**. On overflow the **oldest** frame is dropped. Free GPUs take the **newest** waiting frame (LIFO) and are chosen **round-robin**.

## Requirements

Python **3.9+**, standard library only — nothing to install.

## Run

```bash
cd program

python main.py                          # automatic, auto-determine N
python main.py --requests 3000          # automatic, fixed N
python main.py --step                   # step-by-step (Enter after each event)
python main.py --step --requests 20

python main.py --sources 4 --devices 3 --buffer 8 \
               --arrival-mean 6 --service-mean 5 --requests 5000
```


## Disciplines

| Code | Implementation |
|------|----------------|
| ИБ | `Source` never stops generating |
| ИЗ2 | `UniformLaw` |
| ПЗ1 | `ExponentialLaw` |
| Д1ОЗ1 | `Buffer.find_free_by_ring` + write pointer |
| Д1ОО3 | `Buffer.evict_oldest` |
| Д2П2 | `DevicePool.find_free_by_ring` + pointer |
| Д2Б2 | `Buffer.extract_lifo` |
| ОР1 | `StatisticsCollector.print_tables` |
| ОД1 | `ui/step_mode.py` prints sources / buffer / devices |
