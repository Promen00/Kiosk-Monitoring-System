import psycopg2
from collections import defaultdict
from datetime import datetime, time as dt_time, timedelta
import tkinter as tk
from tkinter import messagebox, font as tkfont, ttk

# Database connection parameters
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres.mleafifpiappqhuhyucp',
    'password': 'Alyssa7719!!',
    'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
    'port': '5432'  # Assuming the default PostgreSQL port, change if different
}

# Flag to indicate if it is the first run
first_run = True

# Variable to track the current day
current_day = datetime.now().day

# Dictionary to track 10-peso vouchers (separate from the database)
manual_vouchers = {
    10: 0  # Key: amount (10 pesos), Value: count
}

# Function to update the voucher count
def update_voucher_count(show_message=False):
    global first_run
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        print("Connected to database.")
        
        # Fetch records only for the current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT amount FROM public.logs WHERE kiosk_name = 'Market1' AND date = %s", (current_date,))
        rows_market1 = cur.fetchall()
        
        cur.execute("SELECT amount FROM public.logs WHERE kiosk_name = 'SLTC' AND date = %s", (current_date,))
        rows_sltc = cur.fetchall()

        # Debug print statement
        print("Fetched rows for Market1 today:", rows_market1)
        print("Fetched rows for SLTC today:", rows_sltc)
        
        voucher_count_market1 = defaultdict(int)
        total_amount_market1 = 0
        for row in rows_market1:
            amount = row[0]
            voucher_count_market1[amount] += 1
            total_amount_market1 += amount
        
        voucher_count_sltc = defaultdict(int)
        total_amount_sltc = 0
        for row in rows_sltc:
            amount = row[0]
            voucher_count_sltc[amount] += 1
            total_amount_sltc += amount
        
        # Add the manually tracked 10-peso vouchers only to Market1
        if 10 in manual_vouchers:
            voucher_count_market1[10] += manual_vouchers[10]
            total_amount_market1 += 10 * manual_vouchers[10]
        
        # Debug print statement
        print("Voucher count for Market1 today:", voucher_count_market1)
        print("Voucher count for SLTC today:", voucher_count_sltc)
        
        # Update the label text with the latest counts
        count_text_market1 = "Market1:\nAmount\tCount\n"
        for amount in sorted(voucher_count_market1.keys()):  # Sort amounts for better readability
            count_text_market1 += f"{amount}\t{voucher_count_market1[amount]}\n"
        count_text_market1 += f"\nTotal Amount: {total_amount_market1}"
        
        count_text_sltc = "SLTC:\nAmount\tCount\n"
        for amount in sorted(voucher_count_sltc.keys()):  # Sort amounts for better readability
            count_text_sltc += f"{amount}\t{voucher_count_sltc[amount]}\n"
        count_text_sltc += f"\nTotal Amount: {total_amount_sltc}"
        
        print("Updated count text for Market1:", count_text_market1)
        print("Updated count text for SLTC:", count_text_sltc)
        
        count_label_market1.config(text=count_text_market1)
        count_label_sltc.config(text=count_text_sltc)

        # Display refresh message only if show_message is True and not the first run
        if show_message and not first_run:
            messagebox.showinfo("Refresh", "Records have been refreshed.")
        first_run = False
    except (Exception, psycopg2.DatabaseError) as error:
        print("Database error:", error)
        messagebox.showerror("Error", f"An error occurred: {error}")
    finally:
        if conn:
            cur.close()
            conn.close()
        print("Database connection closed.")

    # Schedule the next update
    root.after(30000, update_voucher_count)  # Schedule update_voucher_count to run again after 30 seconds

# Function to update the date and time
def update_time():
    global current_day
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H:%M:%S')
    time_label.config(text=f"Current Date and Time: {current_time}")

    # Check if the day has changed
    if now.day != current_day:
        print("New day detected. Resetting display...")
        current_day = now.day  # Update the current_day variable
        reset_display()  # Reset the display at the start of a new day

    root.after(1000, update_time)  # Schedule the function to run again after 1 second

# Function to reset the display (without affecting the database)
def reset_display():
    print("Resetting display for a new day...")
    # Reset the count and total amount, but keep the amounts visible
    count_label_market1.config(text="Market1:\nAmount\tCount\n5\t0\n10\t0\n15\t0\n\nTotal Amount: 0")
    count_label_sltc.config(text="SLTC:\nAmount\tCount\n5\t0\n10\t0\n15\t0\n\nTotal Amount: 0")
    # Reset the manual 10-peso voucher count
    manual_vouchers[10] = 0

# Function to add 10 pesos manually (separate from the database)
def add_10_pesos():
    # Increment the count for 10-peso vouchers
    manual_vouchers[10] += 1
    print(f"Added 10 pesos manually. Total 10-peso vouchers: {manual_vouchers[10]}")
    # Update the display
    update_voucher_count()

# Creating the main window
root = tk.Tk()
root.title("QBYFI Voucher Monitor")
root.geometry('600x500')  # Set the window size to 600x400 pixels
root.configure(bg='#f0f0f0')  # Set the background color

# Define custom fonts
title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
label_font = tkfont.Font(family="Helvetica", size=14)
count_font = tkfont.Font(family="Courier", size=12)

# Adding a title label
title_label = tk.Label(root, text="QBYFI Voucher Monitor", font=title_font, bg='#f0f0f0', fg='#333333')
title_label.pack(pady=10)

# Adding a button to add 10 pesos manually (only for Market1)
add_10_button = ttk.Button(root, text="Add 10 Pesos", command=add_10_pesos, style='Accent.TButton')
add_10_button.pack(pady=10)

# Adding a label to display the current date and time
time_label = tk.Label(root, text="", font=label_font, justify=tk.LEFT, bg='#f0f0f0', fg='#555555')
time_label.pack(pady=10)
update_time()

# Adding a label to display the voucher count for Market1
count_label_market1 = tk.Label(root, text="Market1:\nAmount\tCount\n5\t0\n10\t0\n15\t0\n\nTotal Amount: 0", font=count_font, justify=tk.LEFT, bg='#f0f0f0', fg='#333333')
count_label_market1.pack(pady=20)

# Adding a label to display the voucher count for SLTC
count_label_sltc = tk.Label(root, text="SLTC:\nAmount\tCount\n5\t0\n10\t0\n15\t0\n\nTotal Amount: 0", font=count_font, justify=tk.LEFT, bg='#f0f0f0', fg='#333333')
count_label_sltc.pack(pady=20)

# Configure ttk style for the buttons
style = ttk.Style()
style.configure('Accent.TButton', font=label_font, background='#4caf50', padding=15, borderwidth=3)
style.map('Accent.TButton', background=[('active', '#45a049')])

# Start the update loop
update_voucher_count()  # Initial call to start the update loop

# Running the application
root.mainloop()
