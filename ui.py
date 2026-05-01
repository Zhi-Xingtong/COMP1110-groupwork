from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.file_io import load_customer_groups, load_restaurant_settings
from app.models import CustomerGroup, QueueRule, Table
from app.ui_state import InteractiveQueueState, UiSnapshot


BG_ROOT = "#111315"
BG_SIDEBAR = "#171a1f"
BG_PANEL = "#1d2127"
BG_PANEL_SOFT = "#222831"
BG_CANVAS = "#14181d"
ACCENT_GOLD = "#c6a56b"
ACCENT_GOLD_SOFT = "#9f8354"
TEXT_PRIMARY = "#f5f1e8"
TEXT_SECONDARY = "#b8b0a3"
TEXT_MUTED = "#7d8491"
LINE = "#2c323b"
SUCCESS = "#2a9d8f"
WARNING = "#f4a261"
DANGER = "#e76f51"
INFO = "#5dade2"
QUEUE_COLORS = ["#d4a373", "#84a59d", "#9a8c98", "#90be6d", "#f28482"]


@dataclass(frozen=True)
class SourceOption:
    path: Path
    label: str
    relative_path: str
    detail: str

    @property
    def choice_label(self) -> str:
        return f"{self.label}  [{self.relative_path}]"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _safe_read_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _friendly_name(path: str | Path, prefix: str) -> str:
    stem = Path(path).stem
    if stem.startswith(prefix):
        stem = stem[len(prefix) :]
    else:
        stem = stem.replace("_settings_", "_").replace("_arrivals_", "_")
    return stem.replace("_", " ").strip() or Path(path).stem.replace("_", " ")


def _setting_name(path: str | Path) -> str:
    return _friendly_name(path, "settings_")


def _arrival_name(path: str | Path) -> str:
    return _friendly_name(path, "arrivals_")


def _queue_range_text(rule: QueueRule) -> str:
    return f"{rule.min_size}-{rule.max_size}" if rule.max_size is not None else f"{rule.min_size}+"


def _source_category(path: Path) -> int:
    relative = _relative_path(path)
    if relative.startswith("case_studies"):
        return 0
    if relative.startswith("sample_data"):
        return 1
    return 2


def _build_setting_option(path: Path, payload: dict) -> SourceOption:
    queues = payload.get("queues") or []
    tables = payload.get("tables") or []
    reserved = sum(1 for table in tables if isinstance(table, dict) and bool(table.get("reserved", False)))
    restaurant_name = str(payload.get("restaurant_name", "")).strip() or _setting_name(path)
    detail = f"{len(queues)} queues | {len(tables)} tables | {reserved} reserved"
    return SourceOption(
        path=path,
        label=restaurant_name,
        relative_path=_relative_path(path),
        detail=detail,
    )


def _build_arrival_option(path: Path, payload: dict) -> SourceOption:
    groups = payload.get("groups") or []
    scenario_name = str(payload.get("scenario_name", "")).strip() or _arrival_name(path)
    latest_arrival = max(
        (
            int(group.get("arrival_time", 0))
            for group in groups
            if isinstance(group, dict)
        ),
        default=0,
    )
    detail = f"{len(groups)} groups | last arrival t={latest_arrival}"
    return SourceOption(
        path=path,
        label=scenario_name,
        relative_path=_relative_path(path),
        detail=detail,
    )


def _discover_source_options() -> tuple[list[SourceOption], list[SourceOption]]:
    settings: list[SourceOption] = []
    arrivals: list[SourceOption] = []
    for path in sorted(
        _repo_root().rglob("*.json"),
        key=lambda item: (_source_category(item), _relative_path(item).lower()),
    ):
        payload = _safe_read_json(path)
        if payload is None:
            continue
        if isinstance(payload.get("queues"), list) and isinstance(payload.get("tables"), list):
            settings.append(_build_setting_option(path, payload))
        elif isinstance(payload.get("groups"), list):
            arrivals.append(_build_arrival_option(path, payload))
    return settings, arrivals


def _table_mix_summary(tables: list[Table]) -> str:
    walk_in_tables = [table for table in tables if not table.reserved]
    reserved_count = sum(1 for table in tables if table.reserved)
    visible_tables = ", ".join(f"{table.table_id}:{table.capacity}" for table in walk_in_tables[:4])
    if len(walk_in_tables) > 4:
        visible_tables = f"{visible_tables}, +{len(walk_in_tables) - 4} more"
    if not visible_tables:
        visible_tables = "No walk-in tables"
    return f"{len(walk_in_tables)} walk-in | {reserved_count} reserved | {visible_tables}"


class QueueVisualizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.repo_root = _repo_root()
        self.root.title("Restaurant Queue Visualizer")
        self.root.geometry("1380x820")
        self.root.minsize(1180, 720)
        self.root.configure(bg=BG_ROOT)
        self._configure_styles()

        (
            restaurant_name,
            service_threshold,
            turnover_duration,
            queue_rules,
            tables,
        ) = self._load_default_layout()
        self.restaurant_name = restaurant_name
        self.service_threshold = service_threshold
        self.settings_path = str(self.repo_root / "sample_data" / "restaurant_settings.json")
        self.scenario_name = "Manual Session"
        self.arrivals_path = ""
        self.state = InteractiveQueueState(queue_rules, tables, turnover_duration=turnover_duration)

        self.group_size_var = tk.IntVar(value=2)
        self.dining_duration_var = tk.IntVar(value=30)
        self.advance_minutes_var = tk.IntVar(value=5)
        self.batch_count_var = tk.IntVar(value=1)
        self.remove_queue_var = tk.StringVar(value=queue_rules[0].name)
        self.setting_choice_var = tk.StringVar()
        self.arrival_choice_var = tk.StringVar()
        self.auto_running = False
        self.auto_delay_ms = 800
        self._auto_job: str | None = None

        self.header_title_var = tk.StringVar()
        self.header_subtitle_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.data_status_var = tk.StringVar()
        self.library_status_var = tk.StringVar()
        self.group_size_label_var = tk.StringVar()
        self.dining_duration_label_var = tk.StringVar()
        self.advance_minutes_label_var = tk.StringVar()
        self.batch_count_label_var = tk.StringVar()
        self.layout_summary_var = tk.StringVar()
        self.queue_fronts_var = tk.StringVar()
        self.arrival_preview_var = tk.StringVar()
        self.auto_status_var = tk.StringVar()

        self.setting_options_by_label: dict[str, SourceOption] = {}
        self.arrival_options_by_label: dict[str, SourceOption] = {}

        self._build_layout()
        self._reload_source_library(focus_setting=self.settings_path)
        self._update_header_text()
        self._refresh()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Dark.TCombobox",
            fieldbackground=BG_PANEL_SOFT,
            background=BG_PANEL_SOFT,
            foreground=TEXT_PRIMARY,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            arrowcolor=ACCENT_GOLD,
            padding=6,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", BG_PANEL_SOFT)],
            foreground=[("readonly", TEXT_PRIMARY)],
            selectbackground=[("readonly", BG_PANEL_SOFT)],
            selectforeground=[("readonly", TEXT_PRIMARY)],
        )
        style.configure(
            "Accent.Horizontal.TScrollbar",
            background=BG_PANEL_SOFT,
            troughcolor=BG_PANEL,
            bordercolor=BG_PANEL,
            arrowcolor=ACCENT_GOLD,
            lightcolor=BG_PANEL_SOFT,
            darkcolor=BG_PANEL_SOFT,
        )
        style.configure(
            "Accent.Vertical.TScrollbar",
            background=BG_PANEL_SOFT,
            troughcolor=BG_PANEL,
            bordercolor=BG_PANEL,
            arrowcolor=ACCENT_GOLD,
            lightcolor=BG_PANEL_SOFT,
            darkcolor=BG_PANEL_SOFT,
        )

    def _load_default_layout(self) -> tuple[str, int, int, list[QueueRule], list[Table]]:
        default_settings_path = self.repo_root / "sample_data" / "restaurant_settings.json"
        restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(
            default_settings_path
        )
        self.root.title(f"Restaurant Queue Visualizer - {restaurant_name}")
        return restaurant_name, service_threshold, turnover_duration, queue_rules, tables

    def _format_source_name(self, path: str) -> str:
        if not path:
            return "not loaded"
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (self.repo_root / candidate).resolve()
        return _relative_path(candidate)

    def _update_header_text(self) -> None:
        self.header_title_var.set(self.restaurant_name)
        self.header_subtitle_var.set(
            " | ".join(
                [
                    f"Scenario: {self.scenario_name}",
                    f"Settings: {self._format_source_name(self.settings_path)}",
                    f"Turnover: {self.state.turnover_duration} min",
                    f"Threshold: {self.service_threshold} min",
                ]
            )
        )

    def _matches_option_path(self, option_path: Path, target: str | None) -> bool:
        if not target:
            return False
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (self.repo_root / target_path).resolve()
        try:
            return option_path.resolve() == target_path.resolve()
        except OSError:
            return str(option_path) == str(target_path)

    def _select_option(self, variable: tk.StringVar, options: dict[str, SourceOption], focus_path: str | None) -> None:
        for label, option in options.items():
            if self._matches_option_path(option.path, focus_path):
                variable.set(label)
                return
        if options:
            variable.set(next(iter(options)))
        else:
            variable.set("")

    def _reload_source_library(
        self,
        focus_setting: str | None = None,
        focus_arrival: str | None = None,
    ) -> None:
        setting_options, arrival_options = _discover_source_options()
        self.setting_options_by_label = {option.choice_label: option for option in setting_options}
        self.arrival_options_by_label = {option.choice_label: option for option in arrival_options}

        self.setting_picker.configure(values=list(self.setting_options_by_label))
        self.arrival_picker.configure(values=list(self.arrival_options_by_label))
        self._select_option(self.setting_choice_var, self.setting_options_by_label, focus_setting or self.settings_path)
        self._select_option(self.arrival_choice_var, self.arrival_options_by_label, focus_arrival or self.arrivals_path)

        self.library_status_var.set(
            f"Bundled library: {len(setting_options)} settings JSON file(s), {len(arrival_options)} arrival JSON file(s)."
        )

    def _apply_layout(
        self,
        restaurant_name: str,
        service_threshold: int,
        queue_rules: list[QueueRule],
        tables: list[Table],
        turnover_duration: int,
        settings_path: str,
    ) -> None:
        self._stop_auto_play()
        self.restaurant_name = restaurant_name
        self.service_threshold = service_threshold
        self.settings_path = settings_path
        self.scenario_name = "Manual Session"
        self.arrivals_path = ""
        self.state = InteractiveQueueState(queue_rules, tables, turnover_duration=turnover_duration)
        self.remove_queue_var.set(queue_rules[0].name)
        self.root.title(f"Restaurant Queue Visualizer - {restaurant_name}")
        self._replace_input_controls(self.form_frame)
        self._update_header_text()

    def _create_card(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str,
        *,
        fill: str = tk.X,
        expand: bool = False,
        padx: int | tuple[int, int] = 18,
        pady: tuple[int, int] = (0, 0),
    ) -> tk.Frame:
        card = tk.Frame(parent, bg=BG_PANEL, highlightthickness=1, highlightbackground=LINE)
        card.pack(fill=fill, expand=expand, padx=padx, pady=pady)
        tk.Label(
            card,
            text=title,
            font=("Segoe UI Semibold", 13, "bold"),
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(
            card,
            text=subtitle,
            wraplength=280,
            justify=tk.LEFT,
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=(0, 10))
        body = tk.Frame(card, bg=BG_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        return body

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, bg=BG_ROOT)
        container.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        left_panel = tk.Frame(container, bg=BG_SIDEBAR, width=360, highlightthickness=1, highlightbackground=LINE)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        left_panel.pack_propagate(False)

        center_panel = tk.Frame(container, bg=BG_ROOT)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        hero = tk.Frame(left_panel, bg=BG_SIDEBAR)
        hero.pack(fill=tk.X, padx=18, pady=(18, 8))
        tk.Label(
            hero,
            text="LUNA DINING",
            font=("Segoe UI Semibold", 22, "bold"),
            bg=BG_SIDEBAR,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w")
        tk.Label(
            hero,
            text="Interactive Queue Studio",
            font=("Segoe UI", 10),
            bg=BG_SIDEBAR,
            fg=ACCENT_GOLD,
        ).pack(anchor="w", pady=(2, 0))
        tk.Frame(hero, bg=ACCENT_GOLD, height=2, width=120).pack(anchor="w", pady=(12, 0))

        library_body = self._create_card(
            left_panel,
            "Data Library",
            "Load bundled case studies and sample files without browsing folders.",
            pady=(10, 0),
        )
        tk.Label(
            library_body,
            text="Restaurant settings",
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))
        self.setting_picker = ttk.Combobox(
            library_body,
            textvariable=self.setting_choice_var,
            state="readonly",
            style="Dark.TCombobox",
        )
        self.setting_picker.pack(fill=tk.X)
        setting_buttons = tk.Frame(library_body, bg=BG_PANEL)
        setting_buttons.pack(fill=tk.X, pady=(8, 12))
        tk.Button(
            setting_buttons,
            text="Quick Load",
            command=self._handle_load_selected_setting,
            bg="#255f85",
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            font=("Segoe UI Semibold", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Button(
            setting_buttons,
            text="Browse...",
            command=self._handle_load_settings,
            bg=BG_PANEL_SOFT,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            font=("Segoe UI Semibold", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            library_body,
            text="Arrival scenarios",
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))
        self.arrival_picker = ttk.Combobox(
            library_body,
            textvariable=self.arrival_choice_var,
            state="readonly",
            style="Dark.TCombobox",
        )
        self.arrival_picker.pack(fill=tk.X)
        arrival_buttons = tk.Frame(library_body, bg=BG_PANEL)
        arrival_buttons.pack(fill=tk.X, pady=(8, 12))
        tk.Button(
            arrival_buttons,
            text="Quick Load",
            command=self._handle_load_selected_arrival,
            bg="#3d6b35",
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            font=("Segoe UI Semibold", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Button(
            arrival_buttons,
            text="Browse...",
            command=self._handle_load_arrivals,
            bg=BG_PANEL_SOFT,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            font=("Segoe UI Semibold", 9),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            library_body,
            textvariable=self.data_status_var,
            wraplength=285,
            justify=tk.LEFT,
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Label(
            library_body,
            textvariable=self.library_status_var,
            wraplength=285,
            justify=tk.LEFT,
            bg=BG_PANEL,
            fg=ACCENT_GOLD,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(8, 0))

        form_body = self._create_card(
            left_panel,
            "Interactive Controls",
            "Adjust manual arrivals, remove queue heads, or advance time for the live demo.",
            pady=(10, 0),
        )
        self.form_frame = tk.Frame(form_body, bg=BG_PANEL)
        self.form_frame.pack(fill=tk.X)
        self._replace_input_controls(self.form_frame)

        button_frame = tk.Frame(left_panel, bg=BG_SIDEBAR)
        button_frame.pack(fill=tk.X, padx=18, pady=16)
        self._add_button(button_frame, "Add Group", self._handle_add_group, "#2f7d32")
        self._add_button(button_frame, "Remove Front", self._handle_remove_front, "#8d5524")
        self._add_button(button_frame, "Seat Waiting Groups", self._handle_seat_groups, "#006d77")
        self._add_button(button_frame, "Advance Time", self._handle_advance_time, "#3d405b")
        self._add_button(button_frame, "Start / Stop Auto Play", self._handle_toggle_auto, "#6d597a")
        self._add_button(button_frame, "Reset Demo", self._handle_reset, "#7f1d1d")

        summary_body = self._create_card(
            left_panel,
            "Session Snapshot",
            "A compact operational summary for the current run.",
            pady=(0, 12),
        )
        tk.Label(
            summary_body,
            textvariable=self.status_var,
            justify=tk.LEFT,
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Consolas", 10),
        ).pack(anchor="w")

        notes_body = self._create_card(
            left_panel,
            "Layout Notes",
            "Queue rules and table mix are shown here for quick reference.",
            pady=(0, 12),
        )
        tk.Label(
            notes_body,
            textvariable=self.layout_summary_var,
            justify=tk.LEFT,
            wraplength=285,
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        log_body = self._create_card(
            left_panel,
            "Event Log",
            "Recent actions from the session, including manual actions and auto-play.",
            fill=tk.BOTH,
            expand=True,
            pady=(0, 18),
        )
        self.log_text = tk.Text(
            log_body,
            height=14,
            wrap="word",
            state="disabled",
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            relief=tk.FLAT,
            insertbackground=TEXT_PRIMARY,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        top_header = tk.Frame(center_panel, bg=BG_ROOT)
        top_header.pack(fill=tk.X, pady=(2, 12))
        tk.Label(
            top_header,
            textvariable=self.header_title_var,
            font=("Segoe UI Semibold", 26, "bold"),
            bg=BG_ROOT,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w")
        tk.Label(
            top_header,
            textvariable=self.header_subtitle_var,
            font=("Segoe UI", 10),
            bg=BG_ROOT,
            fg=TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        self.stats_frame = tk.Frame(center_panel, bg=BG_ROOT)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))

        queue_card = tk.Frame(center_panel, bg=BG_PANEL, highlightthickness=1, highlightbackground=LINE)
        queue_card.pack(fill=tk.BOTH, expand=True)
        queue_header = tk.Frame(queue_card, bg=BG_PANEL)
        queue_header.pack(fill=tk.X, padx=14, pady=(12, 4))
        tk.Label(
            queue_header,
            text="Queue Floor",
            font=("Segoe UI Semibold", 16, "bold"),
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)
        tk.Label(
            queue_header,
            textvariable=self.auto_status_var,
            font=("Segoe UI Semibold", 10),
            bg=BG_PANEL,
            fg=ACCENT_GOLD,
        ).pack(side=tk.RIGHT)
        tk.Label(
            queue_card,
            text="Scrollable live queue lanes. Front groups are highlighted in gold.",
            font=("Segoe UI", 9),
            bg=BG_PANEL,
            fg=TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 10))
        queue_canvas_frame = tk.Frame(queue_card, bg=BG_PANEL)
        queue_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        self.queue_canvas = tk.Canvas(
            queue_canvas_frame,
            bg=BG_CANVAS,
            highlightthickness=0,
            height=390,
            xscrollincrement=12,
            yscrollincrement=12,
        )
        queue_x_scroll = ttk.Scrollbar(
            queue_canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.queue_canvas.xview,
            style="Accent.Horizontal.TScrollbar",
        )
        queue_y_scroll = ttk.Scrollbar(
            queue_canvas_frame,
            orient=tk.VERTICAL,
            command=self.queue_canvas.yview,
            style="Accent.Vertical.TScrollbar",
        )
        self.queue_canvas.configure(
            xscrollcommand=queue_x_scroll.set,
            yscrollcommand=queue_y_scroll.set,
        )
        self.queue_canvas.grid(row=0, column=0, sticky="nsew")
        queue_y_scroll.grid(row=0, column=1, sticky="ns")
        queue_x_scroll.grid(row=1, column=0, sticky="ew")
        queue_canvas_frame.grid_columnconfigure(0, weight=1)
        queue_canvas_frame.grid_rowconfigure(0, weight=1)

        bottom_row = tk.Frame(center_panel, bg=BG_ROOT)
        bottom_row.pack(fill=tk.BOTH, expand=False, pady=(12, 0))

        tables_card = tk.Frame(bottom_row, bg=BG_PANEL, highlightthickness=1, highlightbackground=LINE)
        tables_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        tables_header = tk.Frame(tables_card, bg=BG_PANEL)
        tables_header.pack(fill=tk.X, padx=14, pady=(12, 4))
        tk.Label(
            tables_header,
            text="Dining Area",
            font=("Segoe UI Semibold", 16, "bold"),
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)
        tk.Label(
            tables_header,
            text="Blue = available | Coral = occupied",
            font=("Segoe UI", 9),
            bg=BG_PANEL,
            fg=TEXT_MUTED,
        ).pack(side=tk.RIGHT)
        table_canvas_frame = tk.Frame(tables_card, bg=BG_PANEL)
        table_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        self.table_canvas = tk.Canvas(
            table_canvas_frame,
            bg=BG_CANVAS,
            highlightthickness=0,
            height=250,
            xscrollincrement=12,
        )
        table_x_scroll = ttk.Scrollbar(
            table_canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.table_canvas.xview,
            style="Accent.Horizontal.TScrollbar",
        )
        self.table_canvas.configure(xscrollcommand=table_x_scroll.set)
        self.table_canvas.grid(row=0, column=0, sticky="nsew")
        table_x_scroll.grid(row=1, column=0, sticky="ew")
        table_canvas_frame.grid_columnconfigure(0, weight=1)
        table_canvas_frame.grid_rowconfigure(0, weight=1)

        insights_card = tk.Frame(bottom_row, bg=BG_PANEL, width=320, highlightthickness=1, highlightbackground=LINE)
        insights_card.pack(side=tk.LEFT, fill=tk.Y)
        insights_card.pack_propagate(False)
        tk.Label(
            insights_card,
            text="Live Insights",
            font=("Segoe UI Semibold", 14, "bold"),
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", padx=14, pady=(14, 4))
        tk.Label(
            insights_card,
            text="Queue heads and upcoming arrivals update whenever the state changes.",
            wraplength=290,
            justify=tk.LEFT,
            font=("Segoe UI", 9),
            bg=BG_PANEL,
            fg=TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 12))
        tk.Label(
            insights_card,
            text="Queue Fronts",
            font=("Segoe UI Semibold", 10),
            bg=BG_PANEL,
            fg=ACCENT_GOLD,
        ).pack(anchor="w", padx=14)
        tk.Label(
            insights_card,
            textvariable=self.queue_fronts_var,
            wraplength=290,
            justify=tk.LEFT,
            font=("Segoe UI", 9),
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
        ).pack(anchor="w", padx=14, pady=(6, 14))
        tk.Label(
            insights_card,
            text="Next Scheduled Arrivals",
            font=("Segoe UI Semibold", 10),
            bg=BG_PANEL,
            fg=ACCENT_GOLD,
        ).pack(anchor="w", padx=14)
        tk.Label(
            insights_card,
            textvariable=self.arrival_preview_var,
            wraplength=290,
            justify=tk.LEFT,
            font=("Segoe UI", 9),
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
        ).pack(anchor="w", padx=14, pady=(6, 0))

    def _add_scale(
        self,
        parent: tk.Widget,
        title: str,
        variable: tk.IntVar,
        from_: int,
        to: int,
        label_var: tk.StringVar,
        command,
    ) -> None:
        frame = tk.Frame(parent, bg=BG_PANEL)
        frame.pack(fill=tk.X, pady=(8, 4))
        header = tk.Frame(frame, bg=BG_PANEL)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=title,
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            anchor="w",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT)
        tk.Label(
            header,
            textvariable=label_var,
            bg=BG_PANEL,
            fg=ACCENT_GOLD,
            anchor="e",
            font=("Segoe UI Semibold", 9),
        ).pack(side=tk.RIGHT)
        tk.Scale(
            frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=command,
            showvalue=False,
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            troughcolor=BG_PANEL_SOFT,
            activebackground=ACCENT_GOLD,
            highlightthickness=0,
            bd=0,
        ).pack(fill=tk.X)

    def _add_button(self, parent: tk.Widget, text: str, command, color: str) -> None:
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=TEXT_PRIMARY,
            activebackground=color,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            font=("Segoe UI Semibold", 10),
            bd=0,
        ).pack(fill=tk.X, pady=4)

    def _replace_input_controls(self, form: tk.Widget) -> None:
        for child in list(form.winfo_children()):
            child.destroy()

        max_capacity = max(table.capacity for table in self.state.tables)
        self.group_size_var.set(min(self.group_size_var.get(), max_capacity))
        current_queue = self.remove_queue_var.get()
        queue_names = list(self.state.waiting.keys())
        self.remove_queue_var.set(current_queue if current_queue in queue_names else queue_names[0])

        tk.Label(
            form,
            text=f"Max walk-in table capacity: {max_capacity}",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 8))

        self._add_scale(
            form,
            "Group size",
            self.group_size_var,
            1,
            max_capacity,
            self.group_size_label_var,
            lambda _value: self._update_scale_labels(),
        )
        self._add_scale(
            form,
            "Dining duration",
            self.dining_duration_var,
            10,
            120,
            self.dining_duration_label_var,
            lambda _value: self._update_scale_labels(),
        )
        self._add_scale(
            form,
            "Advance minutes",
            self.advance_minutes_var,
            1,
            30,
            self.advance_minutes_label_var,
            lambda _value: self._update_scale_labels(),
        )
        self._add_scale(
            form,
            "Batch groups",
            self.batch_count_var,
            1,
            5,
            self.batch_count_label_var,
            lambda _value: self._update_scale_labels(),
        )

        tk.Label(
            form,
            text="Remove from queue",
            bg=BG_PANEL,
            fg=TEXT_SECONDARY,
            anchor="w",
            font=("Segoe UI", 9),
        ).pack(fill=tk.X, pady=(14, 4))
        remove_box = ttk.Combobox(
            form,
            textvariable=self.remove_queue_var,
            values=queue_names,
            state="readonly",
            style="Dark.TCombobox",
        )
        remove_box.pack(fill=tk.X)
        self._update_scale_labels()

    def _update_scale_labels(self) -> None:
        self.group_size_label_var.set(f"{self.group_size_var.get()} people")
        self.dining_duration_label_var.set(f"{self.dining_duration_var.get()} min")
        self.advance_minutes_label_var.set(f"{self.advance_minutes_var.get()} min / step")
        self.batch_count_label_var.set(f"{self.batch_count_var.get()} group(s)")

    def _selected_option(self, options: dict[str, SourceOption], choice: str) -> SourceOption | None:
        return options.get(choice)

    def _initial_dir(self, path: str) -> str:
        if path:
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = (self.repo_root / candidate).resolve()
            if candidate.exists():
                return str(candidate.parent)
        return str(self.repo_root)

    def _load_settings_from_path(self, path: str) -> None:
        restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(path)
        self._apply_layout(
            restaurant_name,
            service_threshold,
            queue_rules,
            tables,
            turnover_duration,
            path,
        )
        self.state.log_messages.append(f"Loaded settings from {self._format_source_name(path)}")
        self._reload_source_library(focus_setting=path)
        self._refresh()

    def _load_arrivals_from_path(self, path: str) -> None:
        scenario_name, groups = load_customer_groups(path)
        self._stop_auto_play()
        self.state.load_scenario(groups, scenario_name=scenario_name)
        self.scenario_name = scenario_name
        self.arrivals_path = path
        self._update_header_text()
        self.state.log_messages.append(f"Loaded arrivals from {self._format_source_name(path)}")
        self._reload_source_library(focus_arrival=path)
        self._refresh()

    def _handle_load_selected_setting(self) -> None:
        option = self._selected_option(self.setting_options_by_label, self.setting_choice_var.get())
        if option is None:
            messagebox.showinfo("Settings Library", "Choose a bundled settings file first.")
            return
        try:
            self._load_settings_from_path(str(option.path))
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Load Settings Error", str(error))

    def _handle_load_selected_arrival(self) -> None:
        option = self._selected_option(self.arrival_options_by_label, self.arrival_choice_var.get())
        if option is None:
            messagebox.showinfo("Arrival Library", "Choose a bundled arrival file first.")
            return
        try:
            self._load_arrivals_from_path(str(option.path))
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Load Arrivals Error", str(error))

    def _handle_add_group(self) -> None:
        try:
            for _ in range(self.batch_count_var.get()):
                self.state.add_group(self.group_size_var.get(), self.dining_duration_var.get())
            self.scenario_name = self.state.scenario_name or "Manual Session"
            self._refresh()
        except ValueError as error:
            messagebox.showerror("Add Group Error", str(error))

    def _handle_load_settings(self) -> None:
        path = filedialog.askopenfilename(
            title="Select restaurant settings JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self._initial_dir(self.settings_path),
        )
        if not path:
            return

        try:
            self._load_settings_from_path(path)
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Load Settings Error", str(error))

    def _handle_load_arrivals(self) -> None:
        path = filedialog.askopenfilename(
            title="Select customer arrivals JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self._initial_dir(self.arrivals_path),
        )
        if not path:
            return

        try:
            self._load_arrivals_from_path(path)
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Load Arrivals Error", str(error))

    def _handle_remove_front(self) -> None:
        try:
            self.state.remove_front_batch(self.remove_queue_var.get(), self.batch_count_var.get())
            self._refresh()
        except ValueError as error:
            messagebox.showerror("Remove Error", str(error))

    def _handle_seat_groups(self) -> None:
        self.state.seat_waiting_groups()
        self._refresh()

    def _handle_advance_time(self) -> None:
        try:
            self.state.advance_time(self.advance_minutes_var.get())
            self._refresh()
        except ValueError as error:
            messagebox.showerror("Advance Time Error", str(error))

    def _handle_reset(self) -> None:
        self._stop_auto_play()
        self.state.reset()
        self.scenario_name = self.state.scenario_name or "Manual Session"
        self._refresh()

    def _handle_toggle_auto(self) -> None:
        if self.auto_running:
            self.state.log_messages.append("Auto play paused")
            self._stop_auto_play()
            self._refresh()
            return

        if not self.state.has_active_session():
            self.state.log_messages.append("Auto play is idle because there is no pending activity yet")
            self._refresh()
            return

        self.auto_running = True
        self.state.log_messages.append("Auto play started")
        self._run_auto_step()

    def _run_auto_step(self) -> None:
        if not self.auto_running:
            return

        self.state.seat_waiting_groups()
        if self.state.has_active_session():
            self.state.advance_time(self.advance_minutes_var.get())
            self.state.seat_waiting_groups()

        if not self.state.has_active_session():
            self.state.log_messages.append("Auto play stopped: no more pending arrivals or occupied tables")
            self._stop_auto_play()
            self._refresh()
            return

        self._refresh()
        self._auto_job = self.root.after(self.auto_delay_ms, self._run_auto_step)

    def _stop_auto_play(self) -> None:
        self.auto_running = False
        if self._auto_job is not None:
            self.root.after_cancel(self._auto_job)
            self._auto_job = None

    def _format_layout_summary(self) -> str:
        queue_summary = ", ".join(
            f"{rule.name} ({_queue_range_text(rule)})"
            for rule in self.state.queue_rules
        )
        table_summary = _table_mix_summary(self.state.tables)
        return "\n".join(
            [
                f"Queue rules: {queue_summary}",
                f"Table mix : {table_summary}",
                f"Turnover  : {self.state.turnover_duration} min",
                f"Threshold : {self.service_threshold} min",
            ]
        )

    def _format_queue_fronts(self) -> str:
        lines: list[str] = []
        for queue_name, group in self.state.queue_fronts().items():
            if group is None:
                lines.append(f"{queue_name}: empty")
                continue
            wait_time = max(self.state.current_time - group.arrival_time, 0)
            lines.append(
                f"{queue_name}: {group.group_id} | {group.group_size}p | wait {wait_time} min"
            )
        if not lines:
            return "No queues are configured."
        return "\n".join(lines)

    def _format_arrival_preview(self) -> str:
        arrivals = self.state.preview_pending_arrivals(limit=6)
        if not arrivals:
            return "No scheduled arrivals waiting to be released."

        lines = [
            f"t={group.arrival_time:>3}  {group.group_id:<5} {group.group_size}p / {group.dining_duration}m"
            for group in arrivals
        ]
        remaining = len(self.state.pending_arrivals) - len(arrivals)
        if remaining > 0:
            lines.append(f"... and {remaining} more arrival(s)")
        return "\n".join(lines)

    def _refresh(self) -> None:
        snapshot = self.state.snapshot()
        self.scenario_name = self.state.scenario_name or self.scenario_name or "Manual Session"
        self._update_header_text()

        self.data_status_var.set(
            "\n".join(
                [
                    f"Loaded settings: {self._format_source_name(self.settings_path)}",
                    f"Loaded arrivals: {self._format_source_name(self.arrivals_path)}",
                    "Tip: use Quick Load for bundled files or Browse... for custom JSON input.",
                ]
            )
        )
        self.auto_status_var.set("Auto play: RUNNING" if self.auto_running else "Auto play: PAUSED")
        self.status_var.set(
            "\n".join(
                [
                    f"Restaurant   : {self.restaurant_name}",
                    f"Scenario     : {self.scenario_name}",
                    f"Current time : t={snapshot.current_time}",
                    f"Waiting grp. : {snapshot.waiting_groups}",
                    f"Waiting ppl  : {snapshot.waiting_people}",
                    f"Pending arr. : {snapshot.pending_arrivals}",
                    f"Next arrival : {'t=' + str(snapshot.next_arrival_time) if snapshot.next_arrival_time is not None else '--'}",
                    f"Groups seated: {snapshot.seated_groups}",
                    f"Busy tables  : {snapshot.active_tables}/{len(self.state.tables)}",
                    f"Avg wait now : {snapshot.average_waiting_time:.1f} min",
                    f"Auto play    : {'running' if self.auto_running else 'paused'}",
                ]
            )
        )
        self.layout_summary_var.set(self._format_layout_summary())
        self.queue_fronts_var.set(self._format_queue_fronts())
        self.arrival_preview_var.set(self._format_arrival_preview())
        self._render_log()
        self._render_stats(snapshot)
        self._render_queues()
        self._render_tables()

    def _render_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        lines = self.state.log_messages[-18:] if self.state.log_messages else ["No actions yet."]
        self.log_text.insert(tk.END, "\n".join(lines))
        self.log_text.configure(state="disabled")

    def _render_stats(self, snapshot: UiSnapshot) -> None:
        for child in list(self.stats_frame.winfo_children()):
            child.destroy()

        cards = [
            ("Waiting Groups", str(snapshot.waiting_groups), "Groups currently in line", "#264653"),
            ("Waiting People", str(snapshot.waiting_people), "Guests currently queued", "#1d3557"),
            (
                "Next Arrival",
                f"t={snapshot.next_arrival_time}" if snapshot.next_arrival_time is not None else "--",
                "Scheduled scenario release",
                "#5b5f97",
            ),
            ("Seated Groups", str(snapshot.seated_groups), "Groups already served", "#7f5539"),
            (
                "Busy Tables",
                f"{snapshot.active_tables}/{len(self.state.tables)}",
                "Tables in service or turnover",
                "#6d597a",
            ),
            (
                "Current Utilization",
                f"{snapshot.current_table_utilization:.1f}%",
                "Live occupancy rate",
                "#2a9d8f",
            ),
            (
                "Cumulative Utilization",
                f"{snapshot.cumulative_table_utilization:.1f}%",
                "Since t=0",
                "#3a5a40",
            ),
            (
                "Mode",
                "AUTO" if self.auto_running else "MANUAL",
                "Session control state",
                "#725752",
            ),
        ]

        for column in range(4):
            self.stats_frame.grid_columnconfigure(column, weight=1)

        for index, (title, value, caption, color) in enumerate(cards):
            row = index // 4
            column = index % 4
            card = tk.Frame(
                self.stats_frame,
                bg=color,
                height=88,
                highlightthickness=1,
                highlightbackground="#000000",
            )
            card.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)
            card.grid_propagate(False)
            tk.Label(
                card,
                text=title,
                bg=color,
                fg="#dfe7ef",
                font=("Segoe UI", 9),
            ).pack(anchor="w", padx=12, pady=(12, 4))
            tk.Label(
                card,
                text=value,
                bg=color,
                fg=TEXT_PRIMARY,
                font=("Segoe UI Semibold", 16, "bold"),
            ).pack(anchor="w", padx=12)
            tk.Label(
                card,
                text=caption,
                bg=color,
                fg="#dfe7ef",
                font=("Segoe UI", 8),
            ).pack(anchor="w", padx=12, pady=(4, 0))

    def _render_queues(self) -> None:
        canvas = self.queue_canvas
        canvas.delete("all")
        canvas.update_idletasks()

        queue_items = list(self.state.waiting.items())
        max_groups = max((len(groups) for _, groups in queue_items), default=0)
        lane_height = 112
        content_width = max(canvas.winfo_width(), 920, 320 + max_groups * 104 + 220)
        content_height = max(canvas.winfo_height(), 140 + len(queue_items) * lane_height)

        canvas.create_rectangle(22, 22, content_width - 22, 92, fill="#171b20", outline=LINE)
        canvas.create_text(
            42,
            42,
            text="Entrance",
            anchor="w",
            font=("Segoe UI Semibold", 13, "bold"),
            fill=ACCENT_GOLD,
        )
        canvas.create_text(
            42,
            66,
            text=f"Current time t={self.state.current_time} | Waiting groups: {sum(len(groups) for groups in self.state.waiting.values())}",
            anchor="w",
            font=("Segoe UI", 9),
            fill=TEXT_MUTED,
        )
        canvas.create_text(
            content_width - 250,
            42,
            text="Host Stand",
            anchor="w",
            font=("Segoe UI Semibold", 12, "bold"),
            fill=TEXT_PRIMARY,
        )
        canvas.create_text(
            content_width - 250,
            66,
            text="Use Seat Waiting Groups to place any eligible front party.",
            anchor="w",
            font=("Segoe UI", 9),
            fill=TEXT_MUTED,
        )
        self._draw_host(canvas, content_width - 300, 58)

        queue_rule_map = {rule.name: rule for rule in self.state.queue_rules}
        for index, (queue_name, groups) in enumerate(queue_items):
            y = 118 + index * lane_height
            color = QUEUE_COLORS[index % len(QUEUE_COLORS)]
            canvas.create_rectangle(24, y, content_width - 24, y + 82, fill="#181d23", outline=LINE)
            canvas.create_rectangle(24, y, 34, y + 82, fill=color, outline="")
            canvas.create_text(
                48,
                y + 24,
                text=queue_name,
                anchor="w",
                font=("Segoe UI Semibold", 12, "bold"),
                fill=TEXT_PRIMARY,
            )
            canvas.create_text(
                48,
                y + 48,
                text=f"Party size {_queue_range_text(queue_rule_map[queue_name])}",
                anchor="w",
                font=("Segoe UI", 9),
                fill=TEXT_MUTED,
            )
            canvas.create_text(
                content_width - 180,
                y + 24,
                text=f"{len(groups)} waiting",
                anchor="w",
                font=("Segoe UI", 9),
                fill=ACCENT_GOLD,
            )
            canvas.create_line(242, y + 42, content_width - 54, y + 42, fill="#3a404a", width=2, dash=(10, 8))
            canvas.create_polygon(
                content_width - 68,
                y + 35,
                content_width - 40,
                y + 42,
                content_width - 68,
                y + 49,
                fill=ACCENT_GOLD_SOFT,
                outline=ACCENT_GOLD_SOFT,
            )

            if not groups:
                canvas.create_text(
                    276,
                    y + 42,
                    text="Queue empty. Scheduled arrivals or manual groups will appear here.",
                    anchor="w",
                    font=("Segoe UI", 9),
                    fill=TEXT_MUTED,
                )
                continue

            for group_index, group in enumerate(groups):
                x1 = 258 + group_index * 104
                x2 = x1 + 88
                y1 = y + 16
                y2 = y + 68
                wait_time = max(self.state.current_time - group.arrival_time, 0)
                is_front = group_index == 0
                outline = ACCENT_GOLD if is_front else BG_CANVAS
                width = 2 if is_front else 1
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline, width=width)
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 14,
                    text=group.group_id,
                    font=("Segoe UI Semibold", 9, "bold"),
                    fill="#1f2933",
                )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 31,
                    text=f"{group.group_size} people",
                    font=("Segoe UI", 8),
                    fill="#1f2933",
                )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 47,
                    text=f"wait {wait_time}m",
                    font=("Segoe UI", 8),
                    fill="#1f2933",
                )
                if is_front:
                    canvas.create_text(
                        (x1 + x2) / 2,
                        y2 + 10,
                        text="front",
                        font=("Segoe UI", 8, "bold"),
                        fill=ACCENT_GOLD,
                    )

        canvas.configure(scrollregion=(0, 0, content_width, content_height))

    def _render_tables(self) -> None:
        canvas = self.table_canvas
        canvas.delete("all")
        canvas.update_idletasks()

        card_width = 188
        card_height = 144
        gap = 18
        content_width = max(canvas.winfo_width(), 70 + len(self.state.tables) * (card_width + gap))
        content_height = max(canvas.winfo_height(), 220)
        start_x = 26
        start_y = 34

        for index, table in enumerate(self.state.tables):
            x1 = start_x + index * (card_width + gap)
            y1 = start_y
            x2 = x1 + card_width
            y2 = y1 + card_height
            busy = not table.is_available
            fill = DANGER if busy else INFO
            canvas.create_rectangle(x1, y1, x2, y2, fill="#181d23", outline=LINE)
            canvas.create_text(
                x1 + 16,
                y1 + 18,
                text=table.table_id,
                anchor="w",
                font=("Segoe UI Semibold", 12, "bold"),
                fill=TEXT_PRIMARY,
            )
            canvas.create_text(
                x2 - 16,
                y1 + 18,
                text=f"{table.capacity} seats",
                anchor="e",
                font=("Segoe UI", 9),
                fill=TEXT_MUTED,
            )
            canvas.create_oval(x1 + 28, y1 + 34, x2 - 28, y1 + 102, fill=fill, outline="")
            if busy:
                diners = min(max(table.capacity // 2, 1), 3)
                for diner_index in range(diners):
                    offset = -32 + diner_index * 28
                    self._draw_person(
                        canvas,
                        (x1 + x2) / 2 + offset,
                        y1 + 76,
                        scale=0.72,
                        body="#f4f1de",
                        accent="#3d405b",
                        mood="sit",
                    )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 123,
                    text=f"Occupied by {table.occupied_by}",
                    anchor="center",
                    font=("Segoe UI", 9),
                    fill=TEXT_SECONDARY,
                )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 138,
                    text=f"Free at t={table.occupied_until}",
                    anchor="center",
                    font=("Segoe UI", 9),
                    fill=TEXT_MUTED,
                )
            else:
                self._draw_person(
                    canvas,
                    (x1 + x2) / 2,
                    y1 + 78,
                    scale=0.75,
                    body="#dbeafe",
                    accent="#1d3557",
                    mood="welcome",
                )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y1 + 123,
                    text="Available now",
                    anchor="center",
                    font=("Segoe UI", 10, "bold"),
                    fill=TEXT_PRIMARY,
                )
            canvas.create_rectangle(x1 + 14, y2 - 12, x2 - 14, y2 - 6, fill=fill, outline="")

        canvas.configure(scrollregion=(0, 0, content_width, content_height))

    def _draw_person(
        self,
        canvas: tk.Canvas,
        center_x: float,
        center_y: float,
        scale: float,
        body: str,
        accent: str,
        mood: str = "idle",
    ) -> None:
        head_r = 8 * scale
        body_h = 18 * scale
        body_w = 18 * scale
        leg_h = 10 * scale
        arm_y = center_y - 1 * scale

        canvas.create_oval(
            center_x - head_r,
            center_y - 20 * scale,
            center_x + head_r,
            center_y - 4 * scale,
            fill=accent,
            outline="",
        )
        canvas.create_oval(
            center_x - body_w / 2,
            center_y - 2 * scale,
            center_x + body_w / 2,
            center_y + body_h,
            fill=body,
            outline="",
        )

        if mood == "walk":
            left_arm = (-10 * scale, -3 * scale, -2 * scale, 6 * scale)
            right_arm = (8 * scale, -2 * scale, 14 * scale, 4 * scale)
            left_leg = (-5 * scale, body_h, -12 * scale, body_h + leg_h)
            right_leg = (4 * scale, body_h, 10 * scale, body_h + leg_h - 3 * scale)
        elif mood == "sit":
            left_arm = (-10 * scale, -1 * scale, -3 * scale, 3 * scale)
            right_arm = (10 * scale, -1 * scale, 3 * scale, 3 * scale)
            left_leg = (-5 * scale, body_h, -1 * scale, body_h + 4 * scale)
            right_leg = (5 * scale, body_h, 1 * scale, body_h + 4 * scale)
        elif mood == "welcome":
            left_arm = (-10 * scale, -2 * scale, -14 * scale, -8 * scale)
            right_arm = (10 * scale, -2 * scale, 14 * scale, -8 * scale)
            left_leg = (-4 * scale, body_h, -7 * scale, body_h + leg_h)
            right_leg = (4 * scale, body_h, 7 * scale, body_h + leg_h)
        else:
            left_arm = (-10 * scale, -2 * scale, -14 * scale, 4 * scale)
            right_arm = (10 * scale, -2 * scale, 14 * scale, 4 * scale)
            left_leg = (-4 * scale, body_h, -7 * scale, body_h + leg_h)
            right_leg = (4 * scale, body_h, 7 * scale, body_h + leg_h)

        canvas.create_line(
            center_x + left_arm[0],
            arm_y + left_arm[1],
            center_x + left_arm[2],
            arm_y + left_arm[3],
            fill=body,
            width=max(2, int(3 * scale)),
            capstyle=tk.ROUND,
        )
        canvas.create_line(
            center_x + right_arm[0],
            arm_y + right_arm[1],
            center_x + right_arm[2],
            arm_y + right_arm[3],
            fill=body,
            width=max(2, int(3 * scale)),
            capstyle=tk.ROUND,
        )
        canvas.create_line(
            center_x + left_leg[0],
            center_y + left_leg[1],
            center_x + left_leg[2],
            center_y + left_leg[3],
            fill=body,
            width=max(2, int(3 * scale)),
            capstyle=tk.ROUND,
        )
        canvas.create_line(
            center_x + right_leg[0],
            center_y + right_leg[1],
            center_x + right_leg[2],
            center_y + right_leg[3],
            fill=body,
            width=max(2, int(3 * scale)),
            capstyle=tk.ROUND,
        )

    def _draw_host(self, canvas: tk.Canvas, center_x: float, center_y: float) -> None:
        self._draw_person(
            canvas,
            center_x,
            center_y + 8,
            scale=1.0,
            body="#1f6f78",
            accent="#f4f1de",
            mood="welcome",
        )
        canvas.create_rectangle(center_x - 18, center_y + 12, center_x + 18, center_y + 16, fill=ACCENT_GOLD, outline="")
        canvas.create_text(
            center_x + 34,
            center_y + 6,
            text="Host",
            anchor="w",
            font=("Segoe UI", 9, "bold"),
            fill=TEXT_PRIMARY,
        )


def main() -> None:
    root = tk.Tk()
    app = QueueVisualizerApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
