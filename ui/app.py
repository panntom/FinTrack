import tkinter as tk
from tkinter import ttk, messagebox
from logic.finance_manager import FinanceManager
from logic.forecaster import Forecaster
from models.income import Income
from models.expense import Expense
from models.recurring_bill import RecurringBill


# ══════════════════════════════════════════════════════════════════
# COLOUR PALETTE & STYLE CONSTANTS
# ══════════════════════════════════════════════════════════════════

BG_DARK   = "#1e1e2e"   # Main background (dark navy)
BG_PANEL  = "#2a2a3e"   # Panel/card background
ACCENT    = "#7c3aed"   # Purple accent
GREEN     = "#22c55e"   # Positive values
RED       = "#ef4444"   # Negative/warning
YELLOW    = "#f59e0b"   # Warning/caution
TEXT_MAIN = "#e2e8f0"   # Main text (light)
TEXT_SUB  = "#94a3b8"   # Subtitle/muted text
FONT_H1   = ("Segoe UI", 18, "bold")
FONT_H2   = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MONO = ("Courier New", 10)


# ══════════════════════════════════════════════════════════════════
# HELPER: STATUS BAR
# ══════════════════════════════════════════════════════════════════

class StatusBar(tk.Frame):
    """
    A status bar at the bottom of the screen.
    Always tells the user what the system is doing.
    Nielsen Heuristic #1: Visibility of System Status.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG_PANEL, pady=4)
        self.__label = tk.Label(
            self, text="Ready.", font=FONT_BODY,
            bg=BG_PANEL, fg=TEXT_SUB, anchor="w"
        )
        self.__label.pack(side="left", padx=10)

    def set(self, message: str, colour: str = TEXT_SUB):
        """Update the status bar message."""
        self.__label.config(text=message, fg=colour)
        self.__label.update_idletasks()


# ══════════════════════════════════════════════════════════════════
# ADD TRANSACTION DIALOG
# ══════════════════════════════════════════════════════════════════

class AddTransactionDialog(tk.Toplevel):
    """
    A modal dialog window for adding a new transaction.
    Shows/hides fields depending on the transaction type selected.

    Nielsen Heuristics applied:
      #5 - Error Prevention: validates before accepting
      #9 - Help users recognise errors: clear error messages
    """

    def __init__(self, parent, manager: FinanceManager, on_success):
        super().__init__(parent)
        self.title("Add New Transaction")
        self.geometry("480x520")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        # Make this window modal (blocks the main window)
        self.grab_set()
        self.transient(parent)

        self.__manager = manager
        self.__on_success = on_success   # Callback to refresh main window

        self.__build_ui()

    def __build_ui(self):
        """Build all the widgets in the dialog."""

        # ── Title ─────────────────────────────────────────────
        tk.Label(
            self, text="New Transaction", font=FONT_H1,
            bg=BG_DARK, fg=TEXT_MAIN
        ).pack(pady=(20, 5))

        # ── Type selector ──────────────────────────────────────
        type_frame = tk.Frame(self, bg=BG_DARK)
        type_frame.pack(pady=5)

        tk.Label(
            type_frame, text="Transaction Type:",
            font=FONT_BODY, bg=BG_DARK, fg=TEXT_SUB
        ).pack(side="left", padx=5)

        self.__type_var = tk.StringVar(value="Income")
        type_menu = ttk.Combobox(
            type_frame, textvariable=self.__type_var,
            values=["Income", "Expense", "Recurring Bill"],
            state="readonly", width=18
        )
        type_menu.pack(side="left", padx=5)
        type_menu.bind("<<ComboboxSelected>>", self.__on_type_change)

        # ── Shared fields frame ────────────────────────────────
        shared_frame = tk.LabelFrame(
            self, text="Details", font=FONT_BODY,
            bg=BG_DARK, fg=TEXT_SUB, padx=10, pady=8
        )
        shared_frame.pack(fill="x", padx=20, pady=10)

        # Amount
        tk.Label(shared_frame, text="Amount (£):", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=4)
        self.__amount_var = tk.StringVar()
        tk.Entry(shared_frame, textvariable=self.__amount_var,
                 width=25, font=FONT_BODY).grid(row=0, column=1, padx=5)

        # Description
        tk.Label(shared_frame, text="Description:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=4)
        self.__desc_var = tk.StringVar()
        tk.Entry(shared_frame, textvariable=self.__desc_var,
                 width=25, font=FONT_BODY).grid(row=1, column=1, padx=5)

        # Date
        tk.Label(shared_frame, text="Date (DD/MM/YYYY):", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=2, column=0, sticky="w", pady=4)
        self.__date_var = tk.StringVar()

        # Pre-fill today's date as a convenience (Error Prevention)
        from datetime import datetime
        self.__date_var.set(datetime.today().strftime("%d/%m/%Y"))
        tk.Entry(shared_frame, textvariable=self.__date_var,
                 width=25, font=FONT_BODY).grid(row=2, column=1, padx=5)

        # ── Dynamic fields frame ───────────────────────────────
        # This frame changes based on transaction type
        self.__dynamic_frame = tk.LabelFrame(
            self, text="Type-specific Details", font=FONT_BODY,
            bg=BG_DARK, fg=TEXT_SUB, padx=10, pady=8
        )
        self.__dynamic_frame.pack(fill="x", padx=20, pady=5)

        # All dynamic field variables
        self.__source_var    = tk.StringVar()
        self.__taxable_var   = tk.BooleanVar(value=True)
        self.__category_var  = tk.StringVar(value="Food")
        self.__importance_var = tk.StringVar(value="Need")
        self.__frequency_var = tk.StringVar(value="monthly")
        self.__due_date_var  = tk.StringVar()

        # Build the initial dynamic fields (Income by default)
        self.__build_income_fields()

        # ── Error message label ────────────────────────────────
        self.__error_label = tk.Label(
            self, text="", font=FONT_BODY,
            bg=BG_DARK, fg=RED, wraplength=400
        )
        self.__error_label.pack(pady=4)

        # ── Save button ────────────────────────────────────────
        tk.Button(
            self, text="💾  Save Transaction",
            font=FONT_H2, bg=ACCENT, fg="white",
            relief="flat", padx=20, pady=8,
            cursor="hand2",
            command=self.__save
        ).pack(pady=10)

    # ── Dynamic field builders ─────────────────────────────────

    def __clear_dynamic_frame(self):
        """Remove all widgets from the dynamic frame."""
        for widget in self.__dynamic_frame.winfo_children():
            widget.destroy()

    def __on_type_change(self, event=None):
        """Rebuild dynamic fields when type dropdown changes."""
        self.__clear_dynamic_frame()
        selected = self.__type_var.get()
        if selected == "Income":
            self.__build_income_fields()
        elif selected == "Expense":
            self.__build_expense_fields()
        else:
            self.__build_recurring_fields()

    def __build_income_fields(self):
        """Fields specific to Income transactions."""
        tk.Label(self.__dynamic_frame, text="Source:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(self.__dynamic_frame, textvariable=self.__source_var,
                 width=22, font=FONT_BODY).grid(row=0, column=1, padx=5)

        tk.Label(self.__dynamic_frame, text="Taxable:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=4)
        tk.Checkbutton(
            self.__dynamic_frame, variable=self.__taxable_var,
            bg=BG_DARK, fg=TEXT_MAIN,
            activebackground=BG_DARK, selectcolor=BG_PANEL
        ).grid(row=1, column=1, sticky="w", padx=5)

    def __build_expense_fields(self):
        """Fields specific to Expense transactions."""
        tk.Label(self.__dynamic_frame, text="Category:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(
            self.__dynamic_frame, textvariable=self.__category_var,
            values=["Food", "Transport", "Housing", "Entertainment",
                    "Health", "Clothing", "Education", "Other"],
            state="readonly", width=20
        ).grid(row=0, column=1, padx=5)

        tk.Label(self.__dynamic_frame, text="Importance:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=4)

        imp_frame = tk.Frame(self.__dynamic_frame, bg=BG_DARK)
        imp_frame.grid(row=1, column=1, sticky="w")
        tk.Radiobutton(imp_frame, text="Need", variable=self.__importance_var,
                       value="Need", bg=BG_DARK, fg=TEXT_MAIN,
                       activebackground=BG_DARK, selectcolor=BG_PANEL
                       ).pack(side="left")
        tk.Radiobutton(imp_frame, text="Want", variable=self.__importance_var,
                       value="Want", bg=BG_DARK, fg=TEXT_MAIN,
                       activebackground=BG_DARK, selectcolor=BG_PANEL
                       ).pack(side="left")

    def __build_recurring_fields(self):
        """Fields specific to RecurringBill transactions."""
        tk.Label(self.__dynamic_frame, text="Frequency:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(
            self.__dynamic_frame, textvariable=self.__frequency_var,
            values=["weekly", "monthly", "yearly"],
            state="readonly", width=20
        ).grid(row=0, column=1, padx=5)

        tk.Label(self.__dynamic_frame, text="Next Due (DD/MM/YYYY):", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(self.__dynamic_frame, textvariable=self.__due_date_var,
                 width=22, font=FONT_BODY).grid(row=1, column=1, padx=5)

    # ── Save logic ─────────────────────────────────────────────

    def __show_error(self, msg: str):
        """Display an error message inside the dialog."""
        self.__error_label.config(text=f"⚠ {msg}")

    def __save(self):
        """
        Validate inputs and save transaction.
        Shows specific error messages rather than crashing.
        """
        self.__error_label.config(text="")   # Clear previous errors

        tx_type  = self.__type_var.get()
        amount   = self.__amount_var.get().strip()
        desc     = self.__desc_var.get().strip()
        date_str = self.__date_var.get().strip()

        # ── Validate shared fields first ───────────────────────
        if not amount:
            self.__show_error("Amount cannot be empty.")
            return
        if not desc:
            self.__show_error("Description cannot be empty.")
            return

        # ── Create the right object ────────────────────────────
        try:
            if tx_type == "Income":
                source = self.__source_var.get().strip()
                if not source:
                    self.__show_error("Source cannot be empty for Income.")
                    return
                transaction = Income(
                    amount=amount, description=desc,
                    source=source, is_taxable=self.__taxable_var.get(),
                    date=date_str if date_str else None
                )

            elif tx_type == "Expense":
                transaction = Expense(
                    amount=amount, description=desc,
                    category=self.__category_var.get(),
                    importance=self.__importance_var.get(),
                    date=date_str if date_str else None
                )

                # ── Budget alert check ─────────────────────────
                alert = self.__manager.check_budget_alert(
                    self.__category_var.get()
                )
                if alert["has_budget"]:
                    new_total = alert["spent"] + float(amount)
                    if new_total > alert["limit"]:
                        over = round(new_total - alert["limit"], 2)
                        proceed = messagebox.askyesno(
                            "⚠ Budget Alert",
                            f"This expense will exceed your "
                            f"{self.__category_var.get()} budget by £{over}!\n\n"
                            f"Budget: £{alert['limit']:.2f}\n"
                            f"Already spent: £{alert['spent']:.2f}\n"
                            f"This expense: £{float(amount):.2f}\n\n"
                            "Do you still want to add it?"
                        )
                        if not proceed:
                            return

            else:  # Recurring Bill
                due_date = self.__due_date_var.get().strip()
                if not due_date:
                    self.__show_error("Next due date cannot be empty.")
                    return
                transaction = RecurringBill(
                    amount=amount, description=desc,
                    frequency=self.__frequency_var.get(),
                    next_due_date=due_date,
                    date=date_str if date_str else None
                )

            # ── All good — save it ─────────────────────────────
            self.__manager.add_transaction(transaction)
            self.__on_success()   # Refresh the main window
            self.destroy()        # Close dialog

        except ValueError as e:
            # Show the validation error from our model setters
            self.__show_error(str(e))


# ══════════════════════════════════════════════════════════════════
# MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════

class FinTrackApp(tk.Tk):
    """
    The main application window.
    Uses a tab-based layout with:
      - Tab 1: Dashboard (balance summary + transaction list)
      - Tab 2: Reports (needs vs wants + category histogram)
      - Tab 3: Forecast (30-day projection)
      - Tab 4: Budgets (set/view budget limits)
    """

    def __init__(self):
        super().__init__()
        self.title("FinTrack — Personal Finance Manager")
        self.geometry("900x650")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Core logic objects
        self.__manager   = FinanceManager()
        self.__forecaster = Forecaster(self.__manager)

        self.__build_ui()
        self.__refresh_dashboard()

    # ── UI Builder ─────────────────────────────────────────────

    def __build_ui(self):
        """Build the main window layout."""

        # Header bar
        header = tk.Frame(self, bg=ACCENT, pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="💰 FinTrack", font=("Segoe UI", 22, "bold"),
            bg=ACCENT, fg="white"
        ).pack(side="left", padx=20)
        tk.Label(
            header, text="Personal Finance & Budget Forecaster",
            font=("Segoe UI", 11), bg=ACCENT, fg="#ddd6fe"
        ).pack(side="left")

        # Tab notebook
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TNotebook", background=BG_DARK, borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=BG_PANEL, foreground=TEXT_SUB,
            padding=[14, 6], font=FONT_BODY
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT)],
            foreground=[("selected", "white")]
        )

        self.__notebook = ttk.Notebook(self)
        self.__notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # Create the four tabs
        self.__tab_dashboard = tk.Frame(self.__notebook, bg=BG_DARK)
        self.__tab_reports   = tk.Frame(self.__notebook, bg=BG_DARK)
        self.__tab_forecast  = tk.Frame(self.__notebook, bg=BG_DARK)
        self.__tab_budgets   = tk.Frame(self.__notebook, bg=BG_DARK)

        self.__notebook.add(self.__tab_dashboard, text="  📊 Dashboard  ")
        self.__notebook.add(self.__tab_reports,   text="  📈 Reports  ")
        self.__notebook.add(self.__tab_forecast,  text="  🔮 Forecast  ")
        self.__notebook.add(self.__tab_budgets,   text="  🎯 Budgets  ")

        # Build each tab's content
        self.__build_dashboard_tab()
        self.__build_reports_tab()
        self.__build_forecast_tab()
        self.__build_budgets_tab()

        # Status bar at the very bottom
        self.__status = StatusBar(self)
        self.__status.pack(fill="x", side="bottom")

        # Bind tab change to refresh content
        self.__notebook.bind("<<NotebookTabChanged>>", self.__on_tab_change)

    # ── DASHBOARD TAB ──────────────────────────────────────────

    def __build_dashboard_tab(self):
        """Build the dashboard: summary cards + transaction list."""
        tab = self.__tab_dashboard

        # Summary cards row
        cards_frame = tk.Frame(tab, bg=BG_DARK)
        cards_frame.pack(fill="x", padx=20, pady=15)

        self.__income_label  = self.__make_card(cards_frame, "Total Income", "£0.00", GREEN)
        self.__expense_label = self.__make_card(cards_frame, "Total Expenses", "£0.00", RED)
        self.__balance_label = self.__make_card(cards_frame, "Balance", "£0.00", ACCENT)

        # Buttons row
        btn_frame = tk.Frame(tab, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(
            btn_frame, text="➕  Add Transaction",
            font=FONT_BODY, bg=GREEN, fg="white",
            relief="flat", padx=12, pady=6,
            cursor="hand2",
            command=self.__open_add_dialog
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🗑  Delete Selected",
            font=FONT_BODY, bg=RED, fg="white",
            relief="flat", padx=12, pady=6,
            cursor="hand2",
            command=self.__delete_selected
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🔄  Refresh",
            font=FONT_BODY, bg=BG_PANEL, fg=TEXT_MAIN,
            relief="flat", padx=12, pady=6,
            cursor="hand2",
            command=self.__refresh_dashboard
        ).pack(side="left", padx=5)

        # Transaction list (Treeview table)
        list_frame = tk.Frame(tab, bg=BG_DARK)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "date", "type", "description", "amount")
        self.__tree = ttk.Treeview(
            list_frame, columns=columns,
            show="headings", height=16
        )

        # Column headers
        self.__tree.heading("id",          text="ID")
        self.__tree.heading("date",        text="Date")
        self.__tree.heading("type",        text="Type")
        self.__tree.heading("description", text="Description")
        self.__tree.heading("amount",      text="Amount (£)")

        # Column widths
        self.__tree.column("id",          width=80,  anchor="center")
        self.__tree.column("date",        width=100, anchor="center")
        self.__tree.column("type",        width=120, anchor="center")
        self.__tree.column("description", width=280)
        self.__tree.column("amount",      width=100, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical",
            command=self.__tree.yview
        )
        self.__tree.configure(yscrollcommand=scrollbar.set)

        self.__tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def __make_card(self, parent, title, value, colour):
        """Helper to create a summary card widget."""
        card = tk.Frame(parent, bg=BG_PANEL, padx=20, pady=12,
                        relief="flat", bd=0)
        card.pack(side="left", expand=True, fill="both", padx=8)

        tk.Label(card, text=title, font=FONT_BODY,
                 bg=BG_PANEL, fg=TEXT_SUB).pack()
        label = tk.Label(card, text=value, font=("Segoe UI", 18, "bold"),
                         bg=BG_PANEL, fg=colour)
        label.pack()
        return label   # Return so we can update the value later

    def __refresh_dashboard(self):
        """Reload all data and update the dashboard display."""
        self.__status.set("Refreshing dashboard...", YELLOW)

        # Update summary cards
        income  = self.__manager.get_total_income()
        expense = self.__manager.get_total_expenses()
        balance = self.__manager.get_current_balance()

        self.__income_label.config(text=f"£{income:.2f}")
        self.__expense_label.config(text=f"£{expense:.2f}")

        bal_colour = GREEN if balance >= 0 else RED
        self.__balance_label.config(
            text=f"£{balance:.2f}", fg=bal_colour
        )

        # Update transaction list
        self.__tree.delete(*self.__tree.get_children())   # Clear existing

        for t in self.__manager.get_all_transactions():
            t_type = type(t).__name__
            if t_type == "RecurringBill":
                t_type = "Recurring"

            # Colour expenses red, income green
            tag = "income" if t_type == "Income" else (
                  "expense" if t_type == "Expense" else "recurring")

            self.__tree.insert("", "end", values=(
                t.get_id(),
                t.get_date(),
                t_type,
                t.get_description(),
                f"£{t.get_amount():.2f}",
            ), tags=(tag,))

        # Row colours
        self.__tree.tag_configure("income",    foreground=GREEN)
        self.__tree.tag_configure("expense",   foreground=RED)
        self.__tree.tag_configure("recurring", foreground=YELLOW)

        # Check for upcoming bills
        upcoming = self.__forecaster.get_upcoming_bills(days=7)
        if upcoming:
            names = ", ".join(b.get_description() for b in upcoming)
            self.__status.set(
                f"⚠ Bills due within 7 days: {names}", YELLOW
            )
        else:
            self.__status.set("✓ Dashboard loaded successfully.", GREEN)

    def __open_add_dialog(self):
        """Open the Add Transaction dialog."""
        AddTransactionDialog(self, self.__manager, self.__refresh_dashboard)

    def __delete_selected(self):
        """Delete the selected transaction from the list."""
        selected = self.__tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a transaction to delete."
            )
            return

        item = self.__tree.item(selected[0])
        tx_id = item["values"][0]
        desc  = item["values"][3]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n'{desc}' (ID: {tx_id})?"
        )
        if confirm:
            self.__status.set("Deleting transaction...", YELLOW)
            success = self.__manager.delete_transaction(tx_id)
            if success:
                self.__refresh_dashboard()
                self.__status.set(
                    f"✓ Transaction '{desc}' deleted.", GREEN
                )
            else:
                messagebox.showerror("Error", "Transaction not found.")

    # ── Tab change handler ──────────────────────────────────────

    def __on_tab_change(self, event):
        """Refresh the appropriate tab when user switches to it."""
        tab_index = self.__notebook.index("current")
        if tab_index == 1:
            self.__refresh_reports()
        elif tab_index == 2:
            self.__refresh_forecast()
        elif tab_index == 3:
            self.__refresh_budgets()

    # ── REPORTS TAB (built by Bob in Bước 7) ───────────────────

    def __build_reports_tab(self):
        """Placeholder — Bob will fill this in Bước 7."""
        self.__reports_content = tk.Frame(self.__tab_reports, bg=BG_DARK)
        self.__reports_content.pack(fill="both", expand=True)

    def __refresh_reports(self):
        """Placeholder — Bob will fill this in Bước 7."""
        pass

    # ── FORECAST TAB (built by Bob in Bước 7) ──────────────────

    def __build_forecast_tab(self):
        """Placeholder — Bob will fill this in Bước 7."""
        self.__forecast_content = tk.Frame(self.__tab_forecast, bg=BG_DARK)
        self.__forecast_content.pack(fill="both", expand=True)

    def __refresh_forecast(self):
        """Placeholder — Bob will fill this in Bước 7."""
        pass

    # ── BUDGETS TAB ────────────────────────────────────────────

    def __build_budgets_tab(self):
        """Build the budget management tab."""
        tab = self.__tab_budgets

        tk.Label(
            tab, text="🎯 Budget Manager", font=FONT_H1,
            bg=BG_DARK, fg=TEXT_MAIN
        ).pack(pady=15)

        # Set budget form
        form = tk.LabelFrame(
            tab, text="Set Category Budget", font=FONT_BODY,
            bg=BG_DARK, fg=TEXT_SUB, padx=15, pady=10
        )
        form.pack(fill="x", padx=30, pady=10)

        tk.Label(form, text="Category:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=5)
        self.__budget_cat_var = tk.StringVar(value="Food")
        ttk.Combobox(
            form, textvariable=self.__budget_cat_var,
            values=["Food", "Transport", "Housing", "Entertainment",
                    "Health", "Clothing", "Education", "Other"],
            state="readonly", width=20
        ).grid(row=0, column=1, padx=10)

        tk.Label(form, text="Limit (£):", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=5)
        self.__budget_limit_var = tk.StringVar()
        tk.Entry(form, textvariable=self.__budget_limit_var,
                 width=22, font=FONT_BODY).grid(row=1, column=1, padx=10)

        self.__budget_error_label = tk.Label(
            form, text="", font=FONT_BODY, bg=BG_DARK, fg=RED
        )
        self.__budget_error_label.grid(row=2, column=0, columnspan=2)

        tk.Button(
            form, text="💾 Save Budget",
            font=FONT_BODY, bg=ACCENT, fg="white",
            relief="flat", padx=10, pady=5,
            cursor="hand2",
            command=self.__save_budget
        ).grid(row=3, column=0, columnspan=2, pady=8)

        # Budget overview (will be populated in refresh)
        tk.Label(
            tab, text="Current Budgets:", font=FONT_H2,
            bg=BG_DARK, fg=TEXT_MAIN
        ).pack(pady=(10, 0))

        self.__budget_display = tk.Frame(tab, bg=BG_DARK)
        self.__budget_display.pack(fill="both", expand=True, padx=30, pady=5)

    def __save_budget(self):
        """Save a budget limit for a category."""
        self.__budget_error_label.config(text="")
        category = self.__budget_cat_var.get()
        limit    = self.__budget_limit_var.get().strip()

        if not limit:
            self.__budget_error_label.config(text="⚠ Please enter a limit.")
            return
        try:
            self.__manager.set_budget(category, limit)
            self.__status.set(
                f"✓ Budget saved: {category} = £{float(limit):.2f}", GREEN
            )
            self.__refresh_budgets()
        except ValueError as e:
            self.__budget_error_label.config(text=f"⚠ {e}")

    def __refresh_budgets(self):
        """Refresh the budget overview display."""
        # Clear existing display
        for widget in self.__budget_display.winfo_children():
            widget.destroy()

        budgets = self.__manager.get_budgets()
        if not budgets:
            tk.Label(
                self.__budget_display,
                text="No budgets set yet. Use the form above to add one.",
                font=FONT_BODY, bg=BG_DARK, fg=TEXT_SUB
            ).pack(pady=20)
            return

        for category, limit in budgets.items():
            alert = self.__manager.check_budget_alert(category)
            spent   = alert["spent"]
            percent = alert["percent_used"]
            over    = alert["over_budget"]

            row = tk.Frame(self.__budget_display, bg=BG_PANEL,
                           padx=15, pady=8)
            row.pack(fill="x", pady=4)

            # Category name
            tk.Label(row, text=category, font=FONT_H2,
                     bg=BG_PANEL, fg=TEXT_MAIN, width=14, anchor="w"
                     ).pack(side="left")

            # Text info
            colour = RED if over else (YELLOW if percent > 80 else GREEN)
            tk.Label(
                row,
                text=f"£{spent:.2f} / £{limit:.2f}  ({percent:.0f}%)",
                font=FONT_BODY, bg=BG_PANEL, fg=colour
            ).pack(side="left", padx=10)

            # Progress bar using Canvas
            bar_bg = tk.Canvas(row, height=14, width=200,
                               bg=BG_DARK, highlightthickness=0)
            bar_bg.pack(side="left", padx=10)

            fill_w = min(int(200 * percent / 100), 200)
            bar_bg.create_rectangle(
                0, 0, fill_w, 14,
                fill=colour, outline=""
            )

            if over:
                tk.Label(row, text="⚠ OVER BUDGET",
                         font=("Segoe UI", 9, "bold"),
                         bg=BG_PANEL, fg=RED).pack(side="left")