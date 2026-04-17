import flet as ft
import flet.canvas as cv
import math
import sqlite3
from datetime import datetime
import os

# --- CONFIGURAZIONE DATABASE ---
##DB_NAME = "cantina_digitale.db"
##
##def init_db():
##    conn = sqlite3.connect(DB_NAME)
##    cursor = conn.cursor()
##    cursor.execute('''
##    CREATE TABLE IF NOT EXISTS assaggi (
##    id INTEGER PRIMARY KEY AUTOINCREMENT,
##    nome TEXT, produttore TEXT, annata TEXT, note TEXT,
##    morbidezza REAL, profumo REAL, acidita REAL,
##    effervescenza REAL, alcolicita REAL, tannicita REAL,
##    data TEXT
##    )
##    ''')
##    conn.commit()
##    conn.close()

# --- LOGICA MATEMATICA RADAR ---
def get_radar_path_elements(params, cx, cy, max_radius, angles):
    points = []
    for i in range(len(params)):
        # Dividiamo per 10 perché lo slider ora è 1-10 ma il raggio del grafico è normalizzato 0-1
        val_normalizzato = params[i] / 10
        x = cx + (max_radius * val_normalizzato) * math.cos(angles[i])
        y = cy + (max_radius * val_normalizzato) * math.sin(angles[i])
        points.append(cv.Path.MoveTo(x, y) if i == 0 else cv.Path.LineTo(x, y))
    points.append(cv.Path.Close())
    return points

# --- APPLICAZIONE PRINCIPALE ---
def main(page: ft.Page):
    try:
        # --- LOGICA PER IL PERCORSO DEL DATABASE ---
        # Se l'app gira su Android/iOS, usiamo la cartella dati sicura
        # Se gira su PC, crea il file nella cartella del progetto
        if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
##            db_dir = page.storage.get("db_path") # Prova a recuperare un percorso salvato
            db_dir = os.getenv("HOME") if os.getenv("HOME") else "."
            db_path = os.path.join(db_dir, "cantina_digitale.db")
        else:
            db_path = "cantina_digitale.db"
                
        db_path = os.path.join(db_dir, "cantina_digitale.db")
##        else:
##            # Percorso standard per Windows/Mac/Linux durante lo sviluppo
##            db_path = "cantina_digitale.db"
            
        def init_db():
            conn = sqlite3.connect(db_path) # Usiamo db_path invece del nome fisso
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assaggi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, produttore TEXT, annata TEXT, note TEXT,
            morbidezza REAL, profumo REAL, acidita REAL,
            effervescenza REAL, alcolicita REAL, tannicita REAL,
            data TEXT
            )
            ''')
            conn.commit()
            conn.close()
            
        WINE_DEEP_GRADIENT = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#1a0000", "#4a0404", "#2a0000"],
            stops=[0.0, 0.5, 1.0]
        )

        WINE_SHINE_GRADIENT = ft.RadialGradient(
            center=ft.Alignment.TOP_LEFT,
            radius=1.2,
            colors=[ft.Colors.with_opacity(0.15, ft.Colors.WHITE), ft.Colors.with_opacity(0.0, ft.Colors.TRANSPARENT)],
        )

        page.theme_mode = ft.ThemeMode.LIGHT
        page.scroll = ft.ScrollMode.ADAPTIVE  
        init_db()

        banner = ft.Image(src="/banner.png", width=page.width, height=200, fit="cover")
        banner2 = ft.Image(src="/banner2.png", width=page.width, height=200, fit="cover")
        banner3 = ft.Image(src="/banner_home.png", width=page.width, height=200, fit="cover")

        LABELS = ["Morbidezza", "Profumo", "Acidità", "Efferv.", "Tannicità", "Alcol"]
        OFFSET = 4 * (math.pi / 180) 
        ANGLES = [
            (270 * math.pi/180) - OFFSET, (270 * math.pi/180) + OFFSET,
            (30 * math.pi/180) - OFFSET, (30 * math.pi/180) + OFFSET,
            (150 * math.pi/180) - OFFSET, (150 * math.pi/180) + OFFSET
        ]

        # --- STATO DELL'INSERIMENTO (Ora scala 1-10, default 5) ---
        current_params = [5.0] * 6
        f_nome = ft.TextField(label="Nome Vino", expand=True, color=ft.Colors.WHITE, label_style=ft.TextStyle(color=ft.Colors.WHITE, weight="bold"), border_color=ft.Colors.RED_800)
        f_produttore = ft.TextField(label="Produttore", expand=True, color=ft.Colors.WHITE, label_style=ft.TextStyle(color=ft.Colors.WHITE, weight="bold"), border_color=ft.Colors.RED_800)
        f_annata = ft.TextField(
            label="Annata", 
            color=ft.Colors.WHITE, 
            label_style=ft.TextStyle(color=ft.Colors.WHITE, weight="bold"), 
            border_color=ft.Colors.RED_800,
            # Restrizioni:
            keyboard_type=ft.KeyboardType.NUMBER, # Apre il tastierino numerico
            max_length=4,                         # Massimo 4 cifre
            input_filter=ft.InputFilter(
                allow=True, 
                regex_string=r"[0-9]",            # Permette solo numeri da 0 a 9
                replacement_string=""
            ),
            counter_style=ft.TextStyle(color=ft.Colors.WHITE70, size=10) # Stile del contatore 0/4
        )
        f_note = ft.TextField(label="Note di degustazione", multiline=True, min_lines=2, color=ft.Colors.WHITE, label_style=ft.TextStyle(color=ft.Colors.WHITE, weight="bold"), border_color=ft.Colors.RED_800)
        val_texts = [] 

        chart_path = cv.Path([], paint=ft.Paint(color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE), style=ft.PaintingStyle.FILL))

        def build_canvas(cx, cy, r, interactive=True):
            shapes = [
                cv.Circle(cx, cy, r, paint=ft.Paint(color=ft.Colors.GREY_400, style=ft.PaintingStyle.STROKE)),
                cv.Circle(cx, cy, r*0.8, paint=ft.Paint(color=ft.Colors.GREY_400, style=ft.PaintingStyle.STROKE)),
                cv.Circle(cx, cy, r*0.6, paint=ft.Paint(color=ft.Colors.GREY_400, style=ft.PaintingStyle.STROKE)),
                cv.Circle(cx, cy, r*0.4, paint=ft.Paint(color=ft.Colors.GREY_400, style=ft.PaintingStyle.STROKE)),
                cv.Circle(cx, cy, r*0.2, paint=ft.Paint(color=ft.Colors.GREY_400, style=ft.PaintingStyle.STROKE)),
                cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) + 50 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) + 50 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) + 74 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) + 74 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) + 168 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) + 168 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) + 192 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) + 192 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) - 50 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) - 50 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Line(cx, cy, cx + r * math.cos((270 * math.pi/180) - 74 * (math.pi / 180)), cy + r * math.sin((270 * math.pi/180) - 74 * (math.pi / 180)), paint=ft.Paint(color=ft.Colors.GREY_400)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) + 50 * (math.pi / 180)) - 12, cy + (r + 15) * math.sin((270 * math.pi/180) + 50 * (math.pi / 180)), "Succulenza", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) + 74 * (math.pi / 180)) - 16, cy + (r + 15) * math.sin((270 * math.pi/180) + 72 * (math.pi / 180)), "Untuoso", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) + 168 * (math.pi / 180)) - 5, cy + (r + 4) * math.sin((270 * math.pi/180) + 168 * (math.pi / 180)), "Aromatico", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) + 192 * (math.pi / 180)) - 30, cy + (r + 4) * math.sin((270 * math.pi/180) + 192 * (math.pi / 180)), "Saporito", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) - 50 * (math.pi / 180)) - 15, cy + (r + 15) * math.sin((270 * math.pi/180) - 50 * (math.pi / 180)), "Grasso", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            cv.Text(cx + (r + 20) * math.cos((270 * math.pi/180) - 68 * (math.pi / 180)) - 12, cy + (r + 15) * math.sin((270 * math.pi/180) - 72 * (math.pi / 180)), "Dolce", ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)),
            ]
            # (Linee e testi del canvas rimangono invariati...)
            for i in range(6):
                rx, ry = cx + r * math.cos(ANGLES[i]), cy + r * math.sin(ANGLES[i])
                shapes.append(cv.Line(cx, cy, rx, ry, paint=ft.Paint(color=ft.Colors.GREY_400)))
                # Etichette abbreviate sul grafico
                if i == 5:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) - 12, cy + (r + 15) * math.sin(ANGLES[i]) - 10
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))
                elif i == 4:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) - 32, cy + (r + 15) * math.sin(ANGLES[i]) - 10
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))
                elif i == 3:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) - 10, cy + (r + 15) * math.sin(ANGLES[i]) - 10
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))
                elif i == 2:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) - 14, cy + (r + 15) * math.sin(ANGLES[i]) - 10
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))
                elif i == 0:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) - 60, cy + (r + 15) * math.sin(ANGLES[i])
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))
                else:
                    tx, ty = cx + (r + 20) * math.cos(ANGLES[i]) + 3, cy + (r + 15) * math.sin(ANGLES[i])
                    shapes.append(cv.Text(tx, ty, LABELS[i].upper(), ft.TextStyle(size=9, weight="bold", color=ft.Colors.WHITE)))

            if interactive: shapes.append(chart_path)
            return cv.Canvas(shapes, width=cx*2, height=cy*2)

        main_canvas = build_canvas(160, 160, 120)

        def update_main_chart():
            chart_path.elements = get_radar_path_elements(current_params, 160, 160, 120, ANGLES)
            main_canvas.update()

        def on_slider_change(e, idx):
            val = round(float(e.control.value), 1)
            current_params[idx] = val
            val_texts[idx].value = f"{val:.1f}" # Mostra numero invece di %
            val_texts[idx].update()
            update_main_chart()

        def salva_degustazione(e):
            if not f_nome.value or not f_produttore.value or len(f_annata.value) < 4:
                # Mostra un errore se l'annata non è di 4 cifre
                page.snack_bar = ft.SnackBar(
                    ft.Text("Inserisci un'annata valida di 4 cifre (es. 2022)"),
                    bgcolor=ft.Colors.ORANGE_800
                )
                page.snack_bar.open = True
                page.update()
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO assaggi (nome, produttore, annata, note, morbidezza, profumo,
            acidita, effervescenza, alcolicita, tannicita, data)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (f_nome.value, f_produttore.value, f_annata.value, f_note.value,
            *current_params, datetime.now().strftime("%d/%m/%Y %H:%M")))
            conn.commit()
            conn.close()

            # Reset a 5 (metà della nuova scala)
            for i in range(len(current_params)):
                current_params[i] = 5
            
            f_nome.value = f_produttore.value = f_annata.value = f_note.value = ""
            page.go("/history")

        def mostra_dettaglio(item):
            wine_id = item[0]  # ID univoco dal DB
            # Convertiamo i valori (indici 5-10) in float per calcoli e visualizzazione
            valori = [float(x) for x in item[5:11]] 
            cx, cy, r = 100, 100, 70
            
            # --- 1. LOGICA DI CANCELLAZIONE CON REFRESH ---
            def cancella_vino(e):
                def conferma_cancellazione(ev):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM assaggi WHERE id = ?", (wine_id,))
                    conn.commit()
                    conn.close()
                    
                    dlg.open = False
                    bs.open = False
                    
                    # Feedback all'utente
                    page.snack_bar = ft.SnackBar(ft.Text(f"'{item[1]}' rimosso dalla cantina"), bgcolor=ft.Colors.GREEN_700)
                    page.snack_bar.open = True
                    
                    # Refresh della lista: forziamo la rotta e ricostruiamo la vista
                    page.route = "/history"
                    route_change()
                    page.update()

                dlg = ft.AlertDialog(
                    title=ft.Text("Conferma"),
                    content=ft.Text(f"Vuoi eliminare '{item[1]}'?"),
                    actions=[
                        ft.TextButton("Annulla", on_click=lambda _: setattr(dlg, "open", False) or page.update()),
                        ft.TextButton("Elimina", on_click=conferma_cancellazione, icon=ft.Icons.DELETE, icon_color="red"),
                    ],
                )
                page.overlay.append(dlg)
                dlg.open = True
                page.update()

            # --- 2. COSTRUZIONE GRAFICO RADAR (Fedele all'originale) ---
            path_storia = cv.Path(
                get_radar_path_elements(valori, cx, cy, r, ANGLES),
                paint=ft.Paint(color=ft.Colors.with_opacity(0.5, ft.Colors.RED_700), style=ft.PaintingStyle.FILL)
            )

            grid_shapes = [
                cv.Circle(cx, cy, r, paint=ft.Paint(color=ft.Colors.GREY_400, style="stroke", stroke_width=0.5)),
                cv.Circle(cx, cy, r*0.8, paint=ft.Paint(color=ft.Colors.GREY_400, style="stroke", stroke_width=0.5)),
                cv.Circle(cx, cy, r*0.6, paint=ft.Paint(color=ft.Colors.GREY_400, style="stroke", stroke_width=0.5)),
                cv.Circle(cx, cy, r*0.4, paint=ft.Paint(color=ft.Colors.GREY_400, style="stroke", stroke_width=0.5)),
                cv.Circle(cx, cy, r*0.2, paint=ft.Paint(color=ft.Colors.GREY_400, style="stroke", stroke_width=0.5)),
            ]

            for i in range(6):
                rx, ry = cx + r * math.cos(ANGLES[i]), cy + r * math.sin(ANGLES[i])
                grid_shapes.append(cv.Line(cx, cy, rx, ry, paint=ft.Paint(color=ft.Colors.GREY_400, stroke_width=0.5)))
                # Etichette abbreviate per non affollare il grafico piccolo
                tx, ty = cx + (r + 15) * math.cos(ANGLES[i]) - 10, cy + (r + 10) * math.sin(ANGLES[i])
                grid_shapes.append(cv.Text(tx, ty, LABELS[i][:3], ft.TextStyle(size=8, color=ft.Colors.GREY_700)))

            grid_shapes.append(path_storia)

            # --- 3. COLONNA PARAMETRI (Sinistra del grafico) ---
            colonna_valori = ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row([
                            ft.Text(LABELS[i], size=11, color=ft.Colors.GREY_800),
                            ft.Text(f"{valori[i]:.1f}", size=12, weight="bold", color=ft.Colors.RED_900)
                        ], alignment="spaceBetween"),
                        width=130,
                        padding=ft.padding.symmetric(vertical=2)
                    ) for i in range(6)
                ],
                spacing=2,
                alignment="center"
            )

            def close_bs(e):
                bs.open = False
                page.update()
                
            # --- 4. ASSEMBLAGGIO BOTTOMSHEET ---
            bs = ft.BottomSheet(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Testata: Info Vino + Cestino
                            ft.ListTile(
                                title=ft.Text(item[1], weight="bold", size=22), 
                                subtitle=ft.Text(f"{item[2]} • {item[3]}", size=16),
                                trailing=ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_700,
                                    on_click=cancella_vino
                                )
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_300),
                            
                            # Sezione Centrale: Valori numerici + Grafico Radar
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(content=colonna_valori, padding=10),
                                    ft.Container(
                                        cv.Canvas(grid_shapes, width=200, height=200), 
                                        alignment=ft.Alignment.CENTER,
                                        expand=True
                                    )
                                ], alignment="center", vertical_alignment="center"),
                                padding=10
                            ),

                            # Sezione Note e Data
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Note di degustazione:", weight="bold", size=16, color=ft.Colors.RED_900),
                                    ft.Text(f"{item[4]}" if item[4] and item[4].strip() else "Nessuna nota inserita.", size=15),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=14, color=ft.Colors.GREY_500),
                                        ft.Text(f"Degustato il: {item[11]}", size=12, color=ft.Colors.GREY_500),
                                    ], spacing=5),
                                ], spacing=10),
                                padding=20
                            ),
                            
                            # Bottone Chiudi
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "Chiudi", on_click=close_bs, bgcolor=ft.Colors.RED_900, color="white", width=200
                                ),
                                alignment=ft.Alignment.CENTER, padding=ft.padding.only(bottom=20)
                            ),
                            ft.Container(height=10) # Buffer finale
                        ],
                        tight=True,
                        scroll=ft.ScrollMode.ADAPTIVE,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    padding=10,
                    height=page.height * 0.8, 
                    border_radius=ft.BorderRadius.only(top_left=30, top_right=30)
                )
            )
            page.overlay.append(bs)
            bs.open = True
            page.update()

        def route_change(e=None):
            page.views.clear()

            if page.route == "/home" or page.route == "/":
                page.views.append(
                    ft.View(route="/home", padding=0, controls=[
                        ft.Stack([
                            ft.Container(gradient=WINE_DEEP_GRADIENT, expand=True),
                            ft.Container(gradient=WINE_SHINE_GRADIENT, expand=True),
                            ft.Column([
                                ft.Text("My Wine Diary", size=40, weight="bold", color=ft.Colors.WHITE, italic=True),
                                banner3,
                                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                                ft.Button("Nuova Degustazione", icon=ft.Icons.ADD, on_click=lambda _: page.go("/nuova"), width=280, height=60, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE)),
                                ft.Button("La mia Cantina", icon=ft.Icons.WINE_BAR, on_click=lambda _: page.go("/history"), width=280, height=60, style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE10, color=ft.Colors.WHITE)),
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
                        ], expand=True)
                    ])
                )

            elif page.route == "/nuova":
                val_texts.clear()
                sliders = []
                for i in range(6):
                    # Testo predefinito "5"
                    t = ft.Text("5", weight="bold", color=ft.Colors.WHITE)
                    val_texts.append(t)
                    sliders.append(ft.Column([
                        ft.Row([ft.Text(LABELS[i], size=12, color=ft.Colors.WHITE), t], alignment="spaceBetween"),
                        ft.Slider(
                            min=1.0, 
                            max=10.0,
                            divisions=18, # Crea step interi (1, 2, 3...)
                            value=5.0, 
                            on_change=lambda e, i=i: on_slider_change(e, i)
                        )
                    ], spacing=0))

                main_content = ft.Container(
                    content=ft.Column([
                        banner,
                        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color=ft.Colors.WHITE, on_click=lambda _: page.go("/home")), ft.Text("Nuova Degustazione", size=24, weight="bold", color=ft.Colors.WHITE)], alignment="start"),
                        ft.Card(content=ft.Container(content=ft.Column([f_nome, f_produttore, f_annata, f_note], spacing=10), padding=15), bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.TRANSPARENT), elevation=0),
                        ft.Divider(height=20, color=ft.Colors.WHITE24),
                        ft.Text("Profilo Sensoriale", size=20, weight="bold", color=ft.Colors.WHITE),
                        ft.Card(content=ft.Container(content=ft.ResponsiveRow([ft.Container(ft.Column(sliders), col={"xs": 12, "md": 5}, padding=10), ft.Container(main_canvas, col={"xs": 12, "md": 7}, alignment=ft.Alignment.CENTER)]), padding=10), bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.TRANSPARENT), elevation=0),
                        ft.Button("Salva Degustazione", icon=ft.Icons.SAVE, on_click=salva_degustazione, width=float("inf"), height=55, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10)))
                    ], scroll="adaptive", spacing=10),
                    expand=True, padding=20
                )

                page.views.append(
                    ft.View(route="/nuova", padding=0, controls=[
                        ft.Stack([ft.Container(gradient=WINE_DEEP_GRADIENT, expand=True), ft.Container(gradient=WINE_SHINE_GRADIENT, expand=True), main_content], expand=True)
                    ])
                )

            elif page.route == "/history":
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assaggi ORDER BY id DESC")
                rows = cursor.fetchall()
                conn.close()

                # Funzione interna per creare i titoli della lista con la data
                def build_history_tiles():
                    tiles = []
                    for r in rows:
                        # r[1] = Nome, r[2] = Produttore, r[3] = Annata, r[11] = Data
                        tiles.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.WINE_BAR, color=ft.Colors.WHITE),
                                title=ft.Text(r[1], color=ft.Colors.WHITE, weight="bold"),
                                subtitle=ft.Column([
                                    ft.Text(f"{r[2]} ({r[3]})", color=ft.Colors.WHITE70, size=13),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=12, color=ft.Colors.WHITE54),
                                        ft.Text(f"Degustato il: {r[11]}", color=ft.Colors.WHITE54, size=11),
                                    ], spacing=5)
                                ], spacing=2),
                                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.WHITE54),
                                on_click=lambda e, r=r: mostra_dettaglio(r),
                            )
                        )
                    return tiles

                history_list = ft.ListView(
                    controls=build_history_tiles(),
                    expand=True, 
                    spacing=10, 
                    padding=20
                )

                page.views.append(
                    ft.View(route="/history", padding=0, controls=[
                        ft.Stack([
                            ft.Container(gradient=WINE_DEEP_GRADIENT, expand=True),
                            ft.Container(gradient=WINE_SHINE_GRADIENT, expand=True),
                            ft.Column([
                                banner2,
                                ft.Container(
                                    content=ft.Row([
                                        ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color=ft.Colors.WHITE, on_click=lambda _: page.go("/home")), 
                                        ft.Text("La mia Cantina", size=24, weight="bold", color=ft.Colors.WHITE), 
                                        ft.IconButton(ft.Icons.ADD, on_click=lambda _: page.go("/nuova"), bgcolor=ft.Colors.RED_900, icon_color=ft.Colors.WHITE)
                                    ], alignment="spaceBetween"), 
                                    padding=ft.Padding.only(top=10, left=10, right=10, bottom=10)
                                ),
                                ft.Container(
                                    content=ft.Text("Nessun vino in cantina", color=ft.Colors.WHITE54) if not rows else history_list, 
                                    expand=True
                                )
                            ])
                        ], expand=True)
                    ])
                )
            
            page.update()
            if page.route == "/nuova": update_main_chart()

        async def view_pop(e):
            if e.view is not None:
                page.views.remove(e.view)
                top_view = page.views[-1]
                page.go(top_view.route)

        page.on_route_change = route_change
        page.on_pop_view = view_pop
        route_change()
    except Exception as e:
        page.add(ft.Text(f"Errore critico: {e}", color=ft.Colors.RED))
        page.update()

ft.run(main=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")
