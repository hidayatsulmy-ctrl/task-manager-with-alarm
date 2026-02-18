import flet as ft
import datetime
import threading
import time


def main(page: ft.Page):
    page.title = "Smart Task Manager"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 500
    page.window_height = 700

    # ================= STORAGE =================
    tasks_data = page.client_storage.get("tasks") or []

    def save_tasks():
        page.client_storage.set("tasks", tasks_data)

    # ================= LANGUAGE =================
    current_lang = {"code": "id"}

    translations = {
        "id": {
            "title": "Manajer Tugas Pintar",
            "add_task": "Tambah tugas...",
            "search": "Cari tugas...",
            "total": "Total",
            "done": "Selesai",
        },
        "en": {
            "title": "Smart Task Manager",
            "add_task": "Add task...",
            "search": "Search task...",
            "total": "Total",
            "done": "Completed",
        }
    }

    def t(key):
        return translations[current_lang["code"]][key]

    # ================= UI PLACEHOLDERS =================
    new_task = ft.TextField()
    search_field = ft.TextField()
    stats_text = ft.Text()
    tasks_view = ft.Column()

    # ================= AUDIO =================
    alarm_sound = ft.Audio(
        src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg",
        autoplay=False,
    )
    page.overlay.append(alarm_sound)

    # ================= TASK LOGIC =================
    def update_stats():
        total = len(tasks_data)
        done = len([task for task in tasks_data if task["done"]])
        stats_text.value = f"{t('total')}: {total} | {t('done')}: {done}"
        page.update()

    def toggle_task(e, task):
        task["done"] = e.control.value
        save_tasks()
        update_stats()

    def delete_task(e, task):
        tasks_data.remove(task)
        save_tasks()
        refresh_tasks()

    def add_task(e):
        if new_task.value.strip():
            alarm_time = None
            if date_picker.value and time_picker.value:
                dt = datetime.datetime.combine(
                    date_picker.value,
                    time_picker.value
                )
                alarm_time = dt.strftime("%Y-%m-%d %H:%M")

            tasks_data.append({
                "text": new_task.value,
                "done": False,
                "alarm": alarm_time
            })

            new_task.value = ""
            save_tasks()
            refresh_tasks()

    def refresh_tasks():
        tasks_view.controls.clear()
        search_value = search_field.value.lower()

        for task in tasks_data:
            if search_value in task["text"].lower():

                alarm_label = ""
                if task["alarm"]:
                    alarm_label = f"\n⏰ {task['alarm']}"

                tasks_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Row([
                                ft.Checkbox(
                                    value=task["done"],
                                    label=task["text"] + alarm_label,
                                    expand=True,
                                    on_change=lambda e, t=task: toggle_task(e, t)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color="red",
                                    on_click=lambda e, t=task: delete_task(e, t)
                                )
                            ])
                        )
                    )
                )

        update_stats()
        page.update()

    # ================= ALARM ENGINE =================
    def alarm_checker():
        while True:
            now = datetime.datetime.now()

            for task in tasks_data:
                if task["alarm"] and not task["done"]:
                    alarm_time = datetime.datetime.strptime(
                        task["alarm"], "%Y-%m-%d %H:%M"
                    )

                    if now >= alarm_time:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"⏰ {task['text']}"),
                            open=True
                        )
                        alarm_sound.play()
                        task["alarm"] = None
                        save_tasks()
                        page.update()

            time.sleep(10)

    threading.Thread(target=alarm_checker, daemon=True).start()

    # ================= THEME =================
    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.update()

    # ================= LANGUAGE =================
    def change_language(e):
        current_lang["code"] = lang_dropdown.value
        show_app()

    # ================= MAIN UI =================
    def show_app():
        page.clean()

        page.add(
            ft.Row([
                ft.Text(t("title"), size=24, weight="bold"),
                ft.IconButton(icon=ft.icons.DARK_MODE, on_click=toggle_theme),
                lang_dropdown := ft.Dropdown(
                    width=120,
                    value=current_lang["code"],
                    options=[
                        ft.dropdown.Option("id", "Indonesia"),
                        ft.dropdown.Option("en", "English"),
                    ],
                    on_change=change_language
                )
            ], alignment="spaceBetween"),

            ft.Divider(),

            ft.Row([
                new_task,
                ft.IconButton(
                    icon=ft.icons.CALENDAR_MONTH,
                    on_click=lambda e: page.open(date_picker)
                ),
                ft.IconButton(
                    icon=ft.icons.ACCESS_TIME,
                    on_click=lambda e: page.open(time_picker)
                ),
                ft.IconButton(icon=ft.icons.ADD, on_click=add_task)
            ]),

            search_field,
            stats_text,
            ft.Divider(),
            tasks_view
        )

        new_task.hint_text = t("add_task")
        new_task.expand = True
        new_task.on_submit = add_task

        search_field.hint_text = t("search")
        search_field.on_change = lambda e: refresh_tasks()

        refresh_tasks()

    # ================= PICKERS =================
    date_picker = ft.DatePicker()
    time_picker = ft.TimePicker()
    page.overlay.append(date_picker)
    page.overlay.append(time_picker)

    # ================= START =================
    show_app()


ft.app(target=main)

print("\nTipe data variabel 'nama_peserta' adalah:", type(nama_peserta))