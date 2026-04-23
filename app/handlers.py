import shlex

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

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


def split_command_text(text: str) -> list[str] | None:
    try:
        return shlex.split(text)
    except ValueError:
        return None


def build_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Profilo A", callback_data="set_profile:A"),
                InlineKeyboardButton(text="Profilo Y", callback_data="set_profile:Y"),
            ],
            [
                InlineKeyboardButton(text="Tabella", callback_data="show_tabella"),
                InlineKeyboardButton(text="Aiuto", callback_data="show_aiuto"),
            ],
            [
                InlineKeyboardButton(text="Converti", callback_data="show_converti"),
                InlineKeyboardButton(text="Residuo", callback_data="show_residuo"),
            ],
        ]
    )


def build_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/profilo A"), KeyboardButton(text="/profilo Y")],
            [KeyboardButton(text="/tabella"), KeyboardButton(text="/aiuto")],
            [KeyboardButton(text="/converti 20 pane patate")],
            [KeyboardButton(text="/residuo 20 pane")],
            [KeyboardButton(text="/modifica")],
            [KeyboardButton(text="/elimina")],
            [KeyboardButton(text="/crea")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Scegli un comando",
    )


def build_start_text(profile: str) -> str:
    return (
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


def build_aiuto_text(profile: str) -> str:
    return (
        "Guida completa.\n\n"
        f"Profilo attuale: {profile}\n\n"
        "/profilo A  - imposta profilo A\n"
        "/profilo Y  - imposta profilo Y\n"
        "/tabella    - mostra la tabella del profilo attivo\n"
        "/modifica proteine legumi secchi 50 g  - aggiunge/aggiorna un alimento\n"
        '/converti 20 "legumi secchi" "legumi cotti"  - usa virgolette per nomi con spazi\n'
        "/elimina legumi secchi SI  - elimina un alimento (con conferma)\n"
        "/aggiungi-gruppo proteine  - crea un nuovo gruppo\n"
        "/elimina-gruppo proteine SI  - elimina un gruppo (con conferma)\n"
        "/residuo 20 pane  - calcola residuo quota nel gruppo"
    )


def build_tabella_text(profile_name: str, profile: dict) -> str:
    lines = [f"Tabella profilo {profile_name}:"]
    for group_name, group in profile["groups"].items():
        lines.append(f"\n[{group_name}]")
        for item_name, item in group["items"].items():
            lines.append(f"- {item_name}: {item['qty']} {item['unit']}")
    return "\n".join(lines)


@router.message(Command("start"))
@router.message(Command("help"))
async def start_handler(message: Message):
    profile = get_active_profile_name()
    text = build_start_text(profile)
    await message.answer(text, reply_markup=build_reply_keyboard())
    await message.answer("Scelte rapide:", reply_markup=build_main_keyboard())


@router.message(Command("aiuto"))
async def aiuto_handler(message: Message):
    profile = get_active_profile_name()
    text = build_aiuto_text(profile)
    await message.answer(text, reply_markup=build_reply_keyboard())
    await message.answer("Scelte rapide:", reply_markup=build_main_keyboard())


@router.message(Command("profilo"))
async def profilo_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) != 2:
        profiles = ", ".join(list_profiles())
        await message.answer(
            f"Uso: /profilo A\nProfili disponibili: {profiles}",
            reply_markup=build_reply_keyboard(),
        )
        return

    name = parts[1].strip().upper()
    if name not in list_profiles():
        await message.answer("Profilo non valido.", reply_markup=build_reply_keyboard())
        return

    set_active_profile(name)
    await message.answer(
        f"Profilo attivo impostato su {name}",
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("tabella"))
async def tabella_handler(message: Message):
    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)
    await message.answer(
        build_tabella_text(profile_name, profile),
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("modifica"))
async def modifica_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) < 5:
        await message.answer(
            "Uso: /modifica <gruppo> <alimento> <qty> <unit>",
            reply_markup=build_reply_keyboard(),
        )
        return

    group_name = parts[1].lower()
    item_name = " ".join(parts[2:-2]).strip().lower()

    if not item_name:
        await message.answer(
            "Il nome dell'alimento non può essere vuoto.",
            reply_markup=build_reply_keyboard(),
        )
        return

    try:
        qty = float(parts[-2].replace(",", "."))
    except ValueError:
        await message.answer(
            "La quantità deve essere numerica.",
            reply_markup=build_reply_keyboard(),
        )
        return

    unit = parts[-1].lower()

    profile_name = get_active_profile_name()
    result, error = upsert_table_item(profile_name, group_name, item_name, qty, unit)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
        return

    if result["created"]:
        await message.answer(
            f"Aggiunto {item_name} in [{group_name}] con {qty:.1f} {unit} (profilo {profile_name}).",
            reply_markup=build_reply_keyboard(),
        )
    else:
        await message.answer(
            f"Aggiornato {item_name} in [{group_name}] a {qty:.1f} {unit} (profilo {profile_name}).",
            reply_markup=build_reply_keyboard(),
        )


@router.message(Command("elimina"))
async def elimina_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) < 3:
        await message.answer(
            "Uso: /elimina <alimento> SI",
            reply_markup=build_reply_keyboard(),
        )
        return

    item_name = " ".join(parts[1:-1]).strip().lower()
    confirm = parts[-1].upper()

    if not item_name:
        await message.answer(
            "Il nome dell'alimento non può essere vuoto.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if confirm != "SI":
        await message.answer(
            "Conferma richiesta. Usa: /elimina <alimento> SI",
            reply_markup=build_reply_keyboard(),
        )
        return
    profile_name = get_active_profile_name()

    result, error = delete_item_from_profile(profile_name, item_name)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
        return

    await message.answer(
        f"Eliminato {item_name} dal gruppo [{result['group']}] (profilo {profile_name}).",
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("aggiungi-gruppo"))
async def aggiungi_gruppo_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) < 2:
        await message.answer(
            "Uso: /aggiungi-gruppo <nome>",
            reply_markup=build_reply_keyboard(),
        )
        return

    group_name = " ".join(parts[1:]).strip().lower()

    if not group_name:
        await message.answer(
            "Il nome del gruppo non può essere vuoto.",
            reply_markup=build_reply_keyboard(),
        )
        return

    profile_name = get_active_profile_name()

    result, error = add_group_to_profile(profile_name, group_name)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
        return

    await message.answer(
        f"Gruppo [{result['group']}] creato (profilo {profile_name}).",
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("elimina-gruppo"))
async def elimina_gruppo_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) < 3:
        await message.answer(
            "Uso: /elimina-gruppo <nome> SI",
            reply_markup=build_reply_keyboard(),
        )
        return

    group_name = " ".join(parts[1:-1]).strip().lower()
    confirm = parts[-1].upper()

    if not group_name:
        await message.answer(
            "Il nome del gruppo non può essere vuoto.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if confirm != "SI":
        await message.answer(
            "Conferma richiesta. Usa: /elimina-gruppo <nome> SI",
            reply_markup=build_reply_keyboard(),
        )
        return
    profile_name = get_active_profile_name()

    result, error = delete_group_from_profile(profile_name, group_name)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
        return

    await message.answer(
        f"Gruppo [{result['group']}] eliminato (profilo {profile_name}).",
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("converti"))
async def converti_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) != 4:
        await message.answer(
            'Uso: /converti 20 pane patate\nPer nomi con spazi usa le virgolette: /converti 20 "legumi secchi" "legumi cotti"',
            reply_markup=build_reply_keyboard(),
        )
        return

    try:
        eaten_qty = float(parts[1].replace(",", "."))
    except ValueError:
        await message.answer(
            "La quantità deve essere numerica.",
            reply_markup=build_reply_keyboard(),
        )
        return

    from_item = parts[2].lower()
    to_item = parts[3].lower()

    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)

    result, error = convert_quantity(profile, from_item, eaten_qty, to_item)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
        return

    await message.answer(
        f"{eaten_qty:.1f} {result['from_unit']} di {from_item} equivalgono a "
        f"{result['result']:.1f} {result['to_unit']} di {to_item} "
        f"(profilo {profile_name}).",
        reply_markup=build_reply_keyboard(),
    )


@router.message(Command("residuo"))
async def residuo_handler(message: Message):
    parts = split_command_text(message.text)

    if not parts:
        await message.answer(
            "Comando non valido. Controlla virgolette e sintassi.",
            reply_markup=build_reply_keyboard(),
        )
        return

    if len(parts) < 3:
        await message.answer(
            "Uso: /residuo 20 pane",
            reply_markup=build_reply_keyboard(),
        )
        return

    try:
        eaten_qty = float(parts[1].replace(",", "."))
    except ValueError:
        await message.answer(
            "La quantità deve essere numerica.",
            reply_markup=build_reply_keyboard(),
        )
        return

    source_item = " ".join(parts[2:]).strip().lower()

    if not source_item:
        await message.answer(
            "Il nome dell'alimento non può essere vuoto.",
            reply_markup=build_reply_keyboard(),
        )
        return

    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)

    result, error = remaining_quantities(profile, source_item, eaten_qty)
    if error:
        await message.answer(error, reply_markup=build_reply_keyboard())
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

    await message.answer("\n".join(lines), reply_markup=build_reply_keyboard())


@router.callback_query(F.data == "show_aiuto")
async def show_aiuto_callback(callback: CallbackQuery):
    profile = get_active_profile_name()
    await callback.message.answer(build_aiuto_text(profile), reply_markup=build_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "show_tabella")
async def show_tabella_callback(callback: CallbackQuery):
    profile_name = get_active_profile_name()
    profile = get_profile(profile_name)
    await callback.message.answer(build_tabella_text(profile_name, profile))
    await callback.answer()


@router.callback_query(F.data == "show_converti")
async def show_converti_callback(callback: CallbackQuery):
    await callback.message.answer(
        'Uso: /converti 20 pane patate\nPer nomi con spazi usa le virgolette: /converti 20 "legumi secchi" "legumi cotti"'
    )
    await callback.answer()


@router.callback_query(F.data == "show_residuo")
async def show_residuo_callback(callback: CallbackQuery):
    await callback.message.answer("Uso: /residuo 20 pane")
    await callback.answer()


@router.callback_query(F.data.startswith("set_profile:"))
async def set_profile_callback(callback: CallbackQuery):
    name = callback.data.split(":", 1)[1].upper()
    if name not in list_profiles():
        await callback.answer("Profilo non valido.", show_alert=True)
        return
    set_active_profile(name)
    await callback.message.answer(f"Profilo attivo impostato su {name}")
    await callback.answer()
