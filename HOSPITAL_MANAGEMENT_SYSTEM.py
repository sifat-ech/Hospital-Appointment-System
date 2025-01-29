import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3

def create_database():
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL UNIQUE,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            UNIQUE (doctor_name, appointment_date, time_slot)
        )
    ''')
    conn.commit()
    conn.close()

create_database()

root = tk.Tk()
root.title("Hospital Appointment Management System")

# Custom style configuration
style = ttk.Style()
style.configure('TFrame')
style.configure('TLabel', font=('Arial', 12, 'bold'))
style.configure('TEntry', font=('Arial', 12))
style.configure('TButton', font=('Arial', 12, 'bold'))
style.configure('TCombobox', font=('Arial', 12))
style.configure('Treeview', font=('Arial', 12))
style.map('TButton', background=[('active', '#006400')])

# Variables to hold entry data
patient_name_var = tk.StringVar()
patient_id_var = tk.StringVar()
doctor_name_var = tk.StringVar()
appointment_date_var = tk.StringVar()
time_slot_var = tk.StringVar()
search_var = tk.StringVar()

# Header frame
header_frame = ttk.Frame(root)
header_frame.pack(pady=10)
ttk.Label(header_frame, text="Hospital Appointment Management System", font=('Arial', 16, 'bold')).pack()

# Input frame
input_frame = ttk.Frame(root)
input_frame.pack(pady=10, padx=20, fill='x')

# Labels and Entry fields
ttk.Label(input_frame, text="Patient Name:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
ttk.Entry(input_frame, textvariable=patient_name_var).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Patient ID:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
ttk.Entry(input_frame, textvariable=patient_id_var).grid(row=1, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Doctor Name:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
ttk.Entry(input_frame, textvariable=doctor_name_var).grid(row=2, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Appointment Date:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
DateEntry(input_frame, textvariable=appointment_date_var, date_pattern='yyyy-mm-dd').grid(row=3, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Time Slot:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
time_slots = ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM",
              "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM"]
time_slot_combobox = ttk.Combobox(input_frame, textvariable=time_slot_var, values=time_slots)
time_slot_combobox.grid(row=4, column=1, padx=5, pady=5)

# Button frame
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Add Appointment button
def add_appointment():
    patient_name = patient_name_var.get()
    patient_id = patient_id_var.get()
    doctor_name = doctor_name_var.get()
    appointment_date = appointment_date_var.get()
    time_slot = time_slot_var.get()
    
    if not patient_name or not doctor_name or not appointment_date or not time_slot:
        messagebox.showerror("Error", "All fields are required.")
        return
    
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    
    # Check if patient_id already exists
    cursor.execute("SELECT * FROM appointments WHERE patient_id=?", (patient_id,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Patient ID already exists. Cannot add another appointment.")
        conn.close()
        return
    
    # Check if the doctor is already booked at the same time and date
    cursor.execute("SELECT * FROM appointments WHERE doctor_name=? AND appointment_date=? AND time_slot=?", (doctor_name, appointment_date, time_slot))
    if cursor.fetchone():
        messagebox.showerror("Error", "Doctor is already booked at this time on the selected date.")
        conn.close()
        return
    
    # Proceed to insert the new appointment
    try:
        cursor.execute('''
            INSERT INTO appointments (patient_id, patient_name, doctor_name, appointment_date, time_slot)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, patient_name, doctor_name, appointment_date, time_slot))
        conn.commit()
        messagebox.showinfo("Success", "Appointment added successfully.")
        clear_fields()
    except sqlite3.IntegrityError as e:
        messagebox.showerror("Database Error", "An error occurred: " + str(e))
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", "An error occurred: " + str(e))
    finally:
        conn.close()

ttk.Button(button_frame, text="Add Appointment", command=add_appointment).grid(row=0, column=0, padx=10)

# Clear Fields button
def clear_fields():
    patient_name_var.set('')
    patient_id_var.set('')
    doctor_name_var.set('')
    appointment_date_var.set('')
    time_slot_var.set('')

ttk.Button(button_frame, text="Clear Fields", command=clear_fields).grid(row=0, column=1, padx=10)

# Show Appointments button
def show_appointments():
    appointments_window = tk.Toplevel(root)
    appointments_window.title("Appointments")
    
    tree = ttk.Treeview(appointments_window, columns=("Patient Name", "Patient ID", "Doctor Name", "Appointment Date", "Time Slot"), show="headings")
    tree.heading("Patient Name", text="Patient Name")
    tree.heading("Patient ID", text="Patient ID")
    tree.heading("Doctor Name", text="Doctor Name")
    tree.heading("Appointment Date", text="Appointment Date")
    tree.heading("Time Slot", text="Time Slot")
    tree.pack(pady=10)
    
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", iid=row[0], values=(row[2], row[1], row[3], row[4], row[5]))
    conn.close()
    
    def delete_appointment():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an appointment to delete.")
            return
        appointment_id = tree.item(selected_item, 'iid')
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this appointment?")
        if confirm:
            conn = sqlite3.connect('hospital_data.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE appointment_id=?", (appointment_id,))
            conn.commit()
            conn.close()
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Appointment deleted successfully.")
    
    ttk.Button(appointments_window, text="Delete Appointment", command=delete_appointment).pack(pady=5)

ttk.Button(button_frame, text="Show Appointments", command=show_appointments).grid(row=0, column=2, padx=10)

# Cancel Appointment button
def cancel_appointment():
    patient_id = patient_id_var.get()
    appointment_date = appointment_date_var.get()
    time_slot = time_slot_var.get()
    
    if not patient_id or not appointment_date or not time_slot:
        messagebox.showerror("Error", "Patient ID, Appointment Date, and Time Slot are required for cancellation.")
        return
    
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE patient_id=? AND appointment_date=? AND time_slot=?", (patient_id, appointment_date, time_slot))
    if cursor.fetchone():
        cursor.execute("DELETE FROM appointments WHERE patient_id=? AND appointment_date=? AND time_slot=?", (patient_id, appointment_date, time_slot))
        conn.commit()
        messagebox.showinfo("Success", "Appointment canceled successfully.")
        clear_fields()
    else:
        messagebox.showerror("Error", "No appointment found for this Patient ID, Date, and Time Slot.")
    conn.close()

ttk.Button(button_frame, text="Cancel Appointment", command=cancel_appointment).grid(row=0, column=3, padx=10)

# Search frame
search_frame = ttk.Frame(root)
search_frame.pack(pady=10, padx=20, fill='x')

ttk.Label(search_frame, text="Search by Doctor Name or Appointment Date:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='e', padx=5, pady=5)
search_entry = ttk.Entry(search_frame, textvariable=search_var)
search_entry.grid(row=0, column=1, padx=5, pady=5)

def search_appointments():
    search_term = search_var.get()
    if not search_term:
        messagebox.showerror("Error", "Please enter a Doctor Name or Appointment Date to search.")
        return
    
    search_window = tk.Toplevel(root)
    search_window.title("Search Results")
    
    tree = ttk.Treeview(search_window, columns=("Patient Name", "Patient ID", "Doctor Name", "Appointment Date", "Time Slot"), show="headings")
    tree.heading("Patient Name", text="Patient Name")
    tree.heading("Patient ID", text="Patient ID")
    tree.heading("Doctor Name", text="Doctor Name")
    tree.heading("Appointment Date", text="Appointment Date")
    tree.heading("Time Slot", text="Time Slot")
    tree.pack(pady=10)
    
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE doctor_name LIKE ? OR appointment_date LIKE ?", ('%'+search_term+'%', '%'+search_term+'%'))
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            tree.insert("", "end", values=(row[2], row[1], row[3], row[4], row[5]))
    else:
        messagebox.showinfo("Info", "No results found.")
    conn.close()

ttk.Button(search_frame, text="Search", command=search_appointments).grid(row=0, column=2, padx=10)

root.mainloop()