# Diet Bot (Telegram)

Bot Telegram personale per calcoli di equivalenze alimentari tra profili fissi `A` e `Y`, con tabelle locali in JSON.

## Requisiti

- Python 3.10+
- Token bot Telegram (variabile `BOT_TOKEN` in `.env`)

## Avvio rapido

```bash
make setup
make run
```

Comando unico:

```bash
make start-diet-bot
```

## Comandi principali

- `/start` o `/help`
- `/aiuto` (guida completa)
- `/profilo <A|Y>`
- `/tabella`
- `/converti <qty> <from_food> <to_food>`
- `/residuo <qty> <food>`

## Gestione tabella

- `/modifica <gruppo> <alimento> <qty> <unit>` (aggiunge o aggiorna)
- `/elimina <alimento> SI` (conferma richiesta)
- `/aggiungi-gruppo <nome>`
- `/elimina-gruppo <nome> SI` (conferma richiesta)

## Struttura dati

I profili sono salvati in `data/profiles.json`. Il profilo attivo è salvato in `data/state.json`.

