from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services import (
    get_active_profile_name,
    set_active_profile,
    get_profile,
    list_profiles,
    convert_quantity,
    remaining_quantities,
    upsert_table_item,
    delete_item_from_profile,
    add_group_to_profile,
    delete_group_from_profile,
)

router = Router()


@router.message(Command("start"))
@router.message(Command("help"))
async def start_handler(message: Message):
    profile = get_active_profile_name()
    text = (
        "Bot dieta attivo.\n\n"
        f"Profilo attuale: {profile}\n\n"
        "Comandi principali:\n"
        "/profilo A\n"
        "/profilo Y\n"
        "/tabella\n"
        "/converti 20 pane patate\n"
        "/residuo 20 pane\n\n"
        "Per la guida completa: /aiuto"
    )
    await message.answer(text)


@router.message(Command("aiuto"))
async def aiuto_handler(message: Message):
    profile = get_active_profile_name()
    text = (
        "Guida completa.\n\n"
        f"Profilo attuale: {profile}\n\n"
        "/profilo A  - imposta profilo A\n"
        "/profilo Y  - imposta profilo Y\n"
        "/tabella    - mostra la tabella del profilo attivo\n"
        "/modifica carboidrati pane 60 g  - aggiunge/aggiorna un alimento\n"
        "/elimina pane SI  - elimina un alimento (con conferma)\n"
        "/aggiungi-gruppo proteine  - crea un nuovo gruppo\n"
        "/elimina-gruppo proteine SI  - elimina un gruppo (con conferma)\n"
        "/converti 20 pane patate  - conversione tra alimenti dello stesso gruppo\n"
        "/residuo 20 pane  - calcola residuo quota nel gruppo"
    )
    await message.answer(text)


@router.message(Command("profilo"))
async def profilo_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 2:
        profiles = ", ".join(list_profiles())
        await message.answer(f"Uso: /profilo A\nProfili disponibili: {profiles}")
        return

    name = parts[1].strip().upper()
    if name not in list_profiles():
        await message.answer("Profilo non valido.")
        return

    set_active_profile(name)
    await message.answer(f"Profilo attivo impostato su {name}")


@router.message(Command("tabella"))
async def tabella_handler(message: Message):
    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)

    lines = [f"Tabella profilo {profile_name}:"]
    for group_name, group in profile["groups"].items():
        lines.append(f"\n[{group_name}]")
        for item_name, item in group["items"].items():
            lines.append(f"- {item_name}: {item['qty']} {item['unit']}")

    await message.answer("\n".join(lines))


@router.message(Command("modifica"))
async def modifica_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 5:
        await message.answer("Uso: /modifica <gruppo> <alimento> <qty> <unit>")
        return

    group_name = parts[1].lower()
    item_name = parts[2].lower()

    try:
        qty = float(parts[3].replace(",", "."))
    except ValueError:
        await message.answer("La quantità deve essere numerica.")
        return

    unit = parts[4].lower()

    profile_name = get_active_profile_name()
    result, error = upsert_table_item(profile_name, group_name, item_name, qty, unit)
    if error:
        await message.answer(error)
        return

    if result["created"]:
        await message.answer(
            f"Aggiunto {item_name} in [{group_name}] con {qty:.1f} {unit} (profilo {profile_name})."
        )
    else:
        await message.answer(
            f"Aggiornato {item_name} in [{group_name}] a {qty:.1f} {unit} (profilo {profile_name})."
        )


@router.message(Command("elimina"))
async def elimina_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer("Uso: /elimina <alimento> SI")
        return

    item_name = parts[1].lower()
    confirm = parts[2].upper()
    if confirm != "SI":
        await message.answer("Conferma richiesta. Usa: /elimina <alimento> SI")
        return
    profile_name = get_active_profile_name()

    result, error = delete_item_from_profile(profile_name, item_name)
    if error:
        await message.answer(error)
        return

    await message.answer(
        f"Eliminato {item_name} dal gruppo [{result['group']}] (profilo {profile_name})."
    )


@router.message(Command("aggiungi-gruppo"))
async def aggiungi_gruppo_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 2:
        await message.answer("Uso: /aggiungi-gruppo <nome>")
        return

    group_name = parts[1].lower()
    profile_name = get_active_profile_name()

    result, error = add_group_to_profile(profile_name, group_name)
    if error:
        await message.answer(error)
        return

    await message.answer(
        f"Gruppo [{result['group']}] creato (profilo {profile_name})."
    )


@router.message(Command("elimina-gruppo"))
async def elimina_gruppo_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer("Uso: /elimina-gruppo <nome> SI")
        return

    group_name = parts[1].lower()
    confirm = parts[2].upper()
    if confirm != "SI":
        await message.answer("Conferma richiesta. Usa: /elimina-gruppo <nome> SI")
        return
    profile_name = get_active_profile_name()

    result, error = delete_group_from_profile(profile_name, group_name)
    if error:
        await message.answer(error)
        return

    await message.answer(
        f"Gruppo [{result['group']}] eliminato (profilo {profile_name})."
    )


@router.message(Command("converti"))
async def converti_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 4:
        await message.answer("Uso: /converti 20 pane patate")
        return

    try:
        eaten_qty = float(parts[1].replace(",", "."))
    except ValueError:
        await message.answer("La quantità deve essere numerica.")
        return

    from_item = parts[2].lower()
    to_item = parts[3].lower()

    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)

    result, error = convert_quantity(profile, from_item, eaten_qty, to_item)
    if error:
        await message.answer(error)
        return

    await message.answer(
        f"{eaten_qty:.1f} {result['from_unit']} di {from_item} equivalgono a "
        f"{result['result']:.1f} {result['to_unit']} di {to_item} "
        f"(profilo {profile_name})."
    )


@router.message(Command("residuo"))
async def residuo_handler(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer("Uso: /residuo 20 pane")
        return

    try:
        eaten_qty = float(parts[1].replace(",", "."))
    except ValueError:
        await message.answer("La quantità deve essere numerica.")
        return

    source_item = parts[2].lower()

    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)

    result, error = remaining_quantities(profile, source_item, eaten_qty)
    if error:
        await message.answer(error)
        return

    lines = [
        f"Profilo {profile_name}",
        f"Gruppo: {result['group']}",
        f"Hai consumato il {result['ratio_consumed'] * 100:.1f}% della quota.",
        f"Ti resta il {result['ratio_remaining'] * 100:.1f}%.",
        "",
        "Puoi ancora mangiare:"
    ]

    for item_name, data in result["remaining"].items():
        lines.append(f"- {item_name}: {data['qty']:.1f} {data['unit']}")

    await message.answer("\n".join(lines))
