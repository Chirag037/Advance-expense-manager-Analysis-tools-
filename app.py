import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import List, Dict, Tuple

class FinanceTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Finance Tracker Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_widgets()
        self.load_data()
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('finance_tracker.db')
        self.cursor = self.conn.cursor()
        
        # Create transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                tags TEXT
            )
        ''')
        
        # Create budgets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                amount REAL NOT NULL,
                period TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Create main GUI widgets"""
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#34495e', foreground='white')
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_transactions_tab()
        self.create_budget_tab()
        self.create_analytics_tab()
        self.create_export_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with overview"""
        dashboard_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(dashboard_frame, text='Dashboard')
        
        # Title
        title_label = tk.Label(dashboard_frame, text="Financial Dashboard", 
                              font=('Arial', 20, 'bold'), bg='#34495e', fg='white')
        title_label.pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(dashboard_frame, bg='#34495e')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Balance cards
        self.balance_frame = tk.Frame(stats_frame, bg='#34495e')
        self.balance_frame.pack(fill='x')
        
        # Create balance cards
        self.create_balance_card(self.balance_frame, "Total Balance", "0.00", "#27ae60", 0)
        self.create_balance_card(self.balance_frame, "Monthly Income", "0.00", "#3498db", 1)
        self.create_balance_card(self.balance_frame, "Monthly Expenses", "0.00", "#e74c3c", 2)
        self.create_balance_card(self.balance_frame, "Savings Rate", "0%", "#f39c12", 3)
        
        # Recent transactions
        recent_frame = tk.LabelFrame(dashboard_frame, text="Recent Transactions", 
                                   font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        recent_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Recent transactions treeview
        columns = ('Date', 'Category', 'Description', 'Amount', 'Type')
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_balance_card(self, parent, title, value, color, column):
        """Create a balance display card"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        title_label = tk.Label(card, text=title, font=('Arial', 10, 'bold'), 
                              bg=color, fg='white')
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card, text=f"${value}", font=('Arial', 16, 'bold'), 
                              bg=color, fg='white')
        value_label.pack(pady=(0, 10))
        
        # Store reference for updating
        setattr(self, f"{title.lower().replace(' ', '_')}_label", value_label)
    
    def create_transactions_tab(self):
        """Create transactions management tab"""
        trans_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(trans_frame, text='Transactions')
        
        # Input frame
        input_frame = tk.LabelFrame(trans_frame, text="Add Transaction", 
                                   font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # Input fields
        fields = [
            ('Date:', 'date_entry'),
            ('Category:', 'category_combo'),
            ('Description:', 'desc_entry'),
            ('Amount:', 'amount_entry'),
            ('Type:', 'type_combo'),
            ('Tags:', 'tags_entry')
        ]
        
        for i, (label_text, attr_name) in enumerate(fields):
            tk.Label(input_frame, text=label_text, bg='#34495e', fg='white').grid(
                row=i//3, column=(i%3)*2, padx=5, pady=5, sticky='w')
            
            if 'combo' in attr_name:
                if 'category' in attr_name:
                    values = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                             'Healthcare', 'Shopping', 'Income', 'Investment', 'Other']
                else:  # type combo
                    values = ['Income', 'Expense']
                widget = ttk.Combobox(input_frame, values=values, width=15)
            else:
                widget = tk.Entry(input_frame, width=18, bg='white')
                if 'date' in attr_name:
                    widget.insert(0, datetime.now().strftime('%Y-%m-%d'))
            
            widget.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
            setattr(self, attr_name, widget)
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#34495e')
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        tk.Button(button_frame, text="Add Transaction", command=self.add_transaction,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(button_frame, text="Update Transaction", command=self.update_transaction,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete Transaction", command=self.delete_transaction,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Transactions list
        list_frame = tk.LabelFrame(trans_frame, text="Transaction History", 
                                  font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg='#34495e')
        search_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:", bg='#34495e', fg='white').pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_transactions)
        
        tk.Label(search_frame, text="Filter by Category:", bg='#34495e', fg='white').pack(side='left', padx=(20, 5))
        self.filter_combo = ttk.Combobox(search_frame, values=['All'] + 
                                        ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                                         'Healthcare', 'Shopping', 'Income', 'Investment', 'Other'],
                                        width=15)
        self.filter_combo.set('All')
        self.filter_combo.pack(side='left', padx=5)
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_transactions)
        
        # Transactions treeview
        columns = ('ID', 'Date', 'Category', 'Description', 'Amount', 'Type', 'Tags')
        self.trans_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.trans_tree.heading(col, text=col)
            if col == 'ID':
                self.trans_tree.column(col, width=50)
            elif col == 'Description':
                self.trans_tree.column(col, width=200)
            else:
                self.trans_tree.column(col, width=100)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self.on_transaction_select)
        
        trans_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=trans_scroll.set)
        
        self.trans_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        trans_scroll.pack(side='right', fill='y', pady=10)
    
    def create_budget_tab(self):
        """Create budget management tab"""
        budget_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(budget_frame, text='Budget')
        
        # Budget input
        input_frame = tk.LabelFrame(budget_frame, text="Set Budget", 
                                   font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        input_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(input_frame, text="Category:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        self.budget_category = ttk.Combobox(input_frame, values=['Food', 'Transportation', 'Entertainment', 
                                                                'Utilities', 'Healthcare', 'Shopping', 'Other'])
        self.budget_category.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Amount:", bg='#34495e', fg='white').grid(row=0, column=2, padx=5, pady=5)
        self.budget_amount = tk.Entry(input_frame, width=15)
        self.budget_amount.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(input_frame, text="Period:", bg='#34495e', fg='white').grid(row=0, column=4, padx=5, pady=5)
        self.budget_period = ttk.Combobox(input_frame, values=['Monthly', 'Weekly', 'Yearly'])
        self.budget_period.set('Monthly')
        self.budget_period.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(input_frame, text="Set Budget", command=self.set_budget,
                 bg='#27ae60', fg='white').grid(row=1, column=0, columnspan=6, pady=10)
        
        # Budget overview
        overview_frame = tk.LabelFrame(budget_frame, text="Budget Overview", 
                                      font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        overview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Budget treeview
        budget_columns = ('Category', 'Budget', 'Spent', 'Remaining', 'Period', 'Status')
        self.budget_tree = ttk.Treeview(overview_frame, columns=budget_columns, show='headings')
        
        for col in budget_columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=120)
        
        budget_scroll = ttk.Scrollbar(overview_frame, orient='vertical', command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=budget_scroll.set)
        
        self.budget_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        budget_scroll.pack(side='right', fill='y', pady=10)
    
    def create_analytics_tab(self):
        """Create analytics and charts tab"""
        analytics_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(analytics_frame, text='Analytics')
        
        # Chart controls
        controls_frame = tk.Frame(analytics_frame, bg='#34495e')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(controls_frame, text="Chart Type:", bg='#34495e', fg='white').pack(side='left', padx=5)
        self.chart_type = ttk.Combobox(controls_frame, values=['Expense by Category', 'Income vs Expenses', 
                                                              'Monthly Trends', 'Budget Analysis'])
        self.chart_type.set('Expense by Category')
        self.chart_type.pack(side='left', padx=5)
        
        tk.Button(controls_frame, text="Generate Chart", command=self.generate_chart,
                 bg='#3498db', fg='white').pack(side='left', padx=10)
        
        # Chart canvas
        self.chart_frame = tk.Frame(analytics_frame, bg='#34495e')
        self.chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    def create_export_tab(self):
        """Create data export/import tab"""
        export_frame = tk.Frame(self.notebook, bg='#34495e')
        self.notebook.add(export_frame, text='Export/Import')
        
        # Export section
        export_section = tk.LabelFrame(export_frame, text="Export Data", 
                                      font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        export_section.pack(fill='x', padx=20, pady=10)
        
        tk.Button(export_section, text="Export to CSV", command=self.export_csv,
                 bg='#27ae60', fg='white', width=20).pack(side='left', padx=10, pady=10)
        tk.Button(export_section, text="Export to JSON", command=self.export_json,
                 bg='#3498db', fg='white', width=20).pack(side='left', padx=10, pady=10)
        
        # Import section
        import_section = tk.LabelFrame(export_frame, text="Import Data", 
                                      font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        import_section.pack(fill='x', padx=20, pady=10)
        
        tk.Button(import_section, text="Import from CSV", command=self.import_csv,
                 bg='#e67e22', fg='white', width=20).pack(side='left', padx=10, pady=10)
        tk.Button(import_section, text="Import from JSON", command=self.import_json,
                 bg='#9b59b6', fg='white', width=20).pack(side='left', padx=10, pady=10)
        
        # Backup section
        backup_section = tk.LabelFrame(export_frame, text="Backup & Restore", 
                                      font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        backup_section.pack(fill='x', padx=20, pady=10)
        
        tk.Button(backup_section, text="Create Backup", command=self.create_backup,
                 bg='#1abc9c', fg='white', width=20).pack(side='left', padx=10, pady=10)
        tk.Button(backup_section, text="Restore Backup", command=self.restore_backup,
                 bg='#e74c3c', fg='white', width=20).pack(side='left', padx=10, pady=10)
    
    def add_transaction(self):
        """Add new transaction to database"""
        try:
            date = self.date_entry.get()
            category = self.category_combo.get()
            description = self.desc_entry.get()
            amount = float(self.amount_entry.get())
            trans_type = self.type_combo.get()
            tags = self.tags_entry.get()
            
            if not all([date, category, amount, trans_type]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            self.cursor.execute('''
                INSERT INTO transactions (date, category, description, amount, type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, category, description, amount, trans_type, tags))
            
            self.conn.commit()
            self.clear_transaction_fields()
            self.load_transactions()
            self.update_dashboard()
            messagebox.showinfo("Success", "Transaction added successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
    
    def update_transaction(self):
        """Update selected transaction"""
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to update")
            return
        
        try:
            item = self.trans_tree.item(selected[0])
            trans_id = item['values'][0]
            
            date = self.date_entry.get()
            category = self.category_combo.get()
            description = self.desc_entry.get()
            amount = float(self.amount_entry.get())
            trans_type = self.type_combo.get()
            tags = self.tags_entry.get()
            
            self.cursor.execute('''
                UPDATE transactions 
                SET date=?, category=?, description=?, amount=?, type=?, tags=?
                WHERE id=?
            ''', (date, category, description, amount, trans_type, tags, trans_id))
            
            self.conn.commit()
            self.clear_transaction_fields()
            self.load_transactions()
            self.update_dashboard()
            messagebox.showinfo("Success", "Transaction updated successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")
    
    def delete_transaction(self):
        """Delete selected transaction"""
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            try:
                item = self.trans_tree.item(selected[0])
                trans_id = item['values'][0]
                
                self.cursor.execute('DELETE FROM transactions WHERE id=?', (trans_id,))
                self.conn.commit()
                
                self.load_transactions()
                self.update_dashboard()
                messagebox.showinfo("Success", "Transaction deleted successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")
    
    def on_transaction_select(self, event):
        """Handle transaction selection"""
        selected = self.trans_tree.selection()
        if selected:
            item = self.trans_tree.item(selected[0])
            values = item['values']
            
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[1])
            self.category_combo.set(values[2])
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, values[3])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[4])
            self.type_combo.set(values[5])
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, values[6] if values[6] else '')
    
    def clear_transaction_fields(self):
        """Clear transaction input fields"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.category_combo.set('')
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.type_combo.set('')
        self.tags_entry.delete(0, tk.END)
    
    def search_transactions(self, event):
        """Search transactions by description"""
        search_term = self.search_entry.get().lower()
        self.load_transactions(search_term)
    
    def filter_transactions(self, event):
        """Filter transactions by category"""
        self.load_transactions()
    
    def load_transactions(self, search_term=''):
        """Load transactions into treeview"""
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        # Build query
        query = 'SELECT * FROM transactions WHERE 1=1'
        params = []
        
        if search_term:
            query += ' AND (description LIKE ? OR category LIKE ?)'
            params.extend([f'%{search_term}%', f'%{search_term}%'])
        
        filter_category = self.filter_combo.get() if hasattr(self, 'filter_combo') else 'All'
        if filter_category and filter_category != 'All':
            query += ' AND category = ?'
            params.append(filter_category)
        
        query += ' ORDER BY date DESC'
        
        self.cursor.execute(query, params)
        transactions = self.cursor.fetchall()
        
        for trans in transactions:
            self.trans_tree.insert('', 'end', values=trans)
        
        # Update recent transactions on dashboard
        self.update_recent_transactions(transactions[:10])
    
    def update_recent_transactions(self, transactions):
        """Update recent transactions display"""
        if hasattr(self, 'recent_tree'):
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            for trans in transactions:
                # Format: (ID, Date, Category, Description, Amount, Type, Tags)
                display_trans = (trans[1], trans[2], trans[3], f"${trans[4]:.2f}", trans[5])
                self.recent_tree.insert('', 'end', values=display_trans)
    
    def set_budget(self):
        """Set budget for category"""
        try:
            category = self.budget_category.get()
            amount = float(self.budget_amount.get())
            period = self.budget_period.get()
            
            if not all([category, amount, period]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO budgets (category, amount, period)
                VALUES (?, ?, ?)
            ''', (category, amount, period))
            
            self.conn.commit()
            self.load_budgets()
            messagebox.showinfo("Success", "Budget set successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set budget: {str(e)}")
    
    def load_budgets(self):
        """Load budgets and calculate spending"""
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        self.cursor.execute('SELECT * FROM budgets')
        budgets = self.cursor.fetchall()
        
        for budget in budgets:
            category, amount, period = budget[1], budget[2], budget[3]
            
            # Calculate spent amount for the period
            if period == 'Monthly':
                start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            elif period == 'Weekly':
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            else:  # Yearly
                start_date = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
            
            self.cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE category = ? AND type = 'Expense' AND date >= ?
            ''', (category, start_date))
            
            spent = self.cursor.fetchone()[0] or 0
            remaining = amount - spent
            status = "Over Budget" if remaining < 0 else f"{(remaining/amount)*100:.1f}% Left"
            
            self.budget_tree.insert('', 'end', values=(
                category, f"${amount:.2f}", f"${spent:.2f}", 
                f"${remaining:.2f}", period, status
            ))
    
    def generate_chart(self):
        """Generate selected chart"""
        chart_type = self.chart_type.get()
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#34495e')
        ax.set_facecolor('#2c3e50')
        
        if chart_type == 'Expense by Category':
            self.create_expense_pie_chart(ax)
        elif chart_type == 'Income vs Expenses':
            self.create_income_expense_chart(ax)
        elif chart_type == 'Monthly Trends':
            self.create_monthly_trends_chart(ax)
        elif chart_type == 'Budget Analysis':
            self.create_budget_analysis_chart(ax)
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_expense_pie_chart(self, ax):
        """Create expense by category pie chart"""
        self.cursor.execute('''
            SELECT category, SUM(amount) FROM transactions 
            WHERE type = 'Expense' 
            GROUP BY category
        ''')
        data = self.cursor.fetchall()
        
        if data:
            categories, amounts = zip(*data)
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('Expenses by Category', color='white', fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No expense data available', transform=ax.transAxes, 
                   ha='center', va='center', color='white', fontsize=12)
    
    def create_income_expense_chart(self, ax):
        """Create income vs expenses bar chart"""
        self.cursor.execute('''
            SELECT type, SUM(amount) FROM transactions 
            GROUP BY type
        ''')
        data = self.cursor.fetchall()
        
        if data:
            types, amounts = zip(*data)
            colors = ['#27ae60' if t == 'Income' else '#e74c3c' for t in types]
            
            bars = ax.bar(types, amounts, color=colors)
            ax.set_title('Income vs Expenses', color='white', fontsize=14, fontweight='bold')
            ax.set_ylabel('Amount ($)', color='white')
            ax.tick_params(colors='white')
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'${amount:.2f}', ha='center', va='bottom', color='white')
        else:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes, 
                   ha='center', va='center', color='white', fontsize=12)
    
    def create_monthly_trends_chart(self, ax):
        """Create monthly trends line chart"""
        self.cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, type, SUM(amount) 
            FROM transactions 
            GROUP BY month, type
            ORDER BY month
        ''')
        data = self.cursor.fetchall()
        
        if data:
            # Process data
            months = {}
            for month, trans_type, amount in data:
                if month not in months:
                    months[month] = {'Income': 0, 'Expense': 0}
                months[month][trans_type] = amount
            
            if months:
                month_labels = sorted(months.keys())
                income_data = [months[m]['Income'] for m in month_labels]
                expense_data = [months[m]['Expense'] for m in month_labels]
                
                ax.plot(month_labels, income_data, marker='o', label='Income', color='#27ae60', linewidth=2)
                ax.plot(month_labels, expense_data, marker='s', label='Expenses', color='#e74c3c', linewidth=2)
                
                ax.set_title('Monthly Trends', color='white', fontsize=14, fontweight='bold')
                ax.set_xlabel('Month', color='white')
                ax.set_ylabel('Amount ($)', color='white')
                ax.legend()
                ax.tick_params(colors='white')
                ax.grid(True, alpha=0.3)
                
                # Rotate x-axis labels for better readability
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes, 
                   ha='center', va='center', color='white', fontsize=12)
    
    def create_budget_analysis_chart(self, ax):
        """Create budget analysis chart"""
        self.cursor.execute('SELECT * FROM budgets')
        budgets = self.cursor.fetchall()
        
        if budgets:
            categories = []
            budget_amounts = []
            spent_amounts = []
            
            for budget in budgets:
                category, amount, period = budget[1], budget[2], budget[3]
                
                # Calculate spent amount for the period
                if period == 'Monthly':
                    start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
                elif period == 'Weekly':
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                else:  # Yearly
                    start_date = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
                
                self.cursor.execute('''
                    SELECT SUM(amount) FROM transactions 
                    WHERE category = ? AND type = 'Expense' AND date >= ?
                ''', (category, start_date))
                
                spent = self.cursor.fetchone()[0] or 0
                
                categories.append(category)
                budget_amounts.append(amount)
                spent_amounts.append(spent)
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, budget_amounts, width, label='Budget', color='#3498db', alpha=0.8)
            bars2 = ax.bar(x + width/2, spent_amounts, width, label='Spent', color='#e74c3c', alpha=0.8)
            
            ax.set_title('Budget vs Spending Analysis', color='white', fontsize=14, fontweight='bold')
            ax.set_xlabel('Categories', color='white')
            ax.set_ylabel('Amount ($)', color='white')
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            ax.tick_params(colors='white')
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'${height:.0f}', ha='center', va='bottom', color='white', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'No budget data available', transform=ax.transAxes, 
                   ha='center', va='center', color='white', fontsize=12)
    
    def export_csv(self):
        """Export transactions to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                self.cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
                transactions = self.cursor.fetchall()
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['ID', 'Date', 'Category', 'Description', 'Amount', 'Type', 'Tags'])
                    writer.writerows(transactions)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_json(self):
        """Export data to JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Export transactions
                self.cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
                transactions = self.cursor.fetchall()
                
                # Export budgets
                self.cursor.execute('SELECT * FROM budgets')
                budgets = self.cursor.fetchall()
                
                data = {
                    'transactions': [
                        {
                            'id': t[0], 'date': t[1], 'category': t[2], 
                            'description': t[3], 'amount': t[4], 'type': t[5], 'tags': t[6]
                        } for t in transactions
                    ],
                    'budgets': [
                        {
                            'id': b[0], 'category': b[1], 'amount': b[2], 'period': b[3]
                        } for b in budgets
                    ],
                    'export_date': datetime.now().isoformat()
                }
                
                with open(filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def import_csv(self):
        """Import transactions from CSV"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    imported_count = 0
                    
                    for row in reader:
                        # Skip if required fields are missing
                        if not all([row.get('Date'), row.get('Category'), 
                                   row.get('Amount'), row.get('Type')]):
                            continue
                        
                        self.cursor.execute('''
                            INSERT INTO transactions (date, category, description, amount, type, tags)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            row.get('Date', ''),
                            row.get('Category', ''),
                            row.get('Description', ''),
                            float(row.get('Amount', 0)),
                            row.get('Type', ''),
                            row.get('Tags', '')
                        ))
                        imported_count += 1
                    
                    self.conn.commit()
                    self.load_transactions()
                    self.update_dashboard()
                    messagebox.showinfo("Success", f"Imported {imported_count} transactions")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def import_json(self):
        """Import data from JSON"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as jsonfile:
                    data = json.load(jsonfile)
                
                imported_trans = 0
                imported_budgets = 0
                
                # Import transactions
                if 'transactions' in data:
                    for trans in data['transactions']:
                        if all([trans.get('date'), trans.get('category'), 
                               trans.get('amount'), trans.get('type')]):
                            self.cursor.execute('''
                                INSERT INTO transactions (date, category, description, amount, type, tags)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                trans.get('date', ''),
                                trans.get('category', ''),
                                trans.get('description', ''),
                                float(trans.get('amount', 0)),
                                trans.get('type', ''),
                                trans.get('tags', '')
                            ))
                            imported_trans += 1
                
                # Import budgets
                if 'budgets' in data:
                    for budget in data['budgets']:
                        if all([budget.get('category'), budget.get('amount'), budget.get('period')]):
                            self.cursor.execute('''
                                INSERT OR REPLACE INTO budgets (category, amount, period)
                                VALUES (?, ?, ?)
                            ''', (
                                budget.get('category', ''),
                                float(budget.get('amount', 0)),
                                budget.get('period', '')
                            ))
                            imported_budgets += 1
                
                self.conn.commit()
                self.load_transactions()
                self.load_budgets()
                self.update_dashboard()
                messagebox.showinfo("Success", 
                                  f"Imported {imported_trans} transactions and {imported_budgets} budgets")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import JSON: {str(e)}")
    
    def create_backup(self):
        """Create database backup"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if filename:
                # Create backup by copying database
                backup_conn = sqlite3.connect(filename)
                self.conn.backup(backup_conn)
                backup_conn.close()
                messagebox.showinfo("Success", f"Backup created: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")
    
    def restore_backup(self):
        """Restore from database backup"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if filename:
                if messagebox.askyesno("Confirm", 
                                     "This will replace all current data. Are you sure?"):
                    self.conn.close()
                    
                    # Replace current database with backup
                    import shutil
                    shutil.copy2(filename, 'finance_tracker.db')
                    
                    # Reconnect to database
                    self.conn = sqlite3.connect('finance_tracker.db')
                    self.cursor = self.conn.cursor()
                    
                    # Refresh all data
                    self.load_data()
                    messagebox.showinfo("Success", "Database restored successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")
    
    def load_data(self):
        """Load all data and refresh displays"""
        self.load_transactions()
        self.load_budgets()
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update dashboard statistics"""
        try:
            # Calculate total balance
            self.cursor.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) - 
                    SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as balance
                FROM transactions
            ''')
            balance = self.cursor.fetchone()[0] or 0
            
            # Calculate monthly income
            current_month = datetime.now().strftime('%Y-%m')
            self.cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE type = 'Income' AND strftime('%Y-%m', date) = ?
            ''', (current_month,))
            monthly_income = self.cursor.fetchone()[0] or 0
            
            # Calculate monthly expenses
            self.cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE type = 'Expense' AND strftime('%Y-%m', date) = ?
            ''', (current_month,))
            monthly_expenses = self.cursor.fetchone()[0] or 0
            
            # Calculate savings rate
            savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
            
            # Update dashboard labels
            if hasattr(self, 'total_balance_label'):
                self.total_balance_label.config(text=f"${balance:.2f}")
            if hasattr(self, 'monthly_income_label'):
                self.monthly_income_label.config(text=f"${monthly_income:.2f}")
            if hasattr(self, 'monthly_expenses_label'):
                self.monthly_expenses_label.config(text=f"${monthly_expenses:.2f}")
            if hasattr(self, 'savings_rate_label'):
                self.savings_rate_label.config(text=f"{savings_rate:.1f}%")
                
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    # Install required packages reminder
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Required packages not installed. Please run:")
        print("pip install matplotlib numpy")
        exit(1)
    
    app = FinanceTracker()
    app.run()