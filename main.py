import requests
import tkinter as tk
from tkinter import ttk
import threading

# Listas de monedas y paginas
pages = ['bcv', 'enparalelovzla', 'italcambio']
monitors= ['usd', 'eur']

# Diccionario para transformar los nombres de las páginas
names = {
    'bcv': 'BCV', 
    'enparalelovzla': 'EnParaleloVzla', 
    'italcambio': 'Italcambio'
}

# Variables globales para almacenar precios de conversión 
conversion_rates = { 
    'usd': {}, 
    'eur': {} 
}

# Función para obtener datos de una página específica y moneda
def get_data(page, monitor):
    global connection_status
    url = f'https://pydolarve.org/api/v1/dollar?page={page}&monitor={monitor}'
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            return response.json()
        else:
            print(f'Error: {response.status_code}') 
            connection_status = False
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        connection_status = False 
        return None

# Función para mostrar datos
def show_data(): 
    global connection_status 
    connection_status = True
    # Limpiar los datos actuales en el árbol
    for item in tree.get_children(): 
        tree.delete(item)
        
    for page in pages:
        usd_price, eur_price, last_update = None, None, None
        if page == 'enparalelovzla':
            data = get_data(page, 'enparalelovzla')
            if data:
                usd_price = data['price']
                eur_price = ''
                last_update = data['last_update']
                conversion_rates['usd'][page] = usd_price
        else:
            for monitor in monitors:
                data = get_data(page, monitor)
                if data:
                    if monitor == 'usd':
                        usd_price = data['price']
                        conversion_rates['usd'][page] = usd_price
                    elif monitor == 'eur':
                        eur_price = data['price']
                        conversion_rates['eur'][page] = eur_price
                    last_update = data['last_update']
        
        # Transformar el nombre de la página antes de mostrarlo
        page_name = names.get(page, page)
        tree.insert('', 'end', text=page_name, values=(usd_price, eur_price, last_update))

    # Mostrar mensaje de error si no hay conexión
    if not connection_status: 
        label_status.config(text="No se pudo obtener datos. Verifique su conexión a internet.", fg="red")
    else: 
        label_status.config(text="Datos obtenidos exitosamente.", fg="green")
        root.after(3000, lambda: label_status.config(text=""))

# Función para realizar la conversión
def convert_currency():
    # Verificar si los campos están vacíos
    if not entry_amount.get().strip():
        label_result.config(text="Por favor, introduzca una cantidad válida.") 
        return
    if not combo_from.get().strip() or not combo_to.get().strip(): 
        label_result.config(text="Por favor, seleccione las monedas.") 
        return

    amount = float(entry_amount.get())
    page_key = combo_page.get()
    # Buscar la clave original en el diccionario names
    page = next(key for key, value in names.items() if value == page_key)
    from_currency = combo_from.get()
    to_currency = combo_to.get()

    if from_currency == to_currency: 
        label_result.config(text="Por favor, elija monedas diferentes para la conversión.") 
        return

    if from_currency == 'Bs':
        if to_currency == 'USD':
            converted_amount = amount / conversion_rates['usd'][page]
        elif to_currency == 'EUR' and page != 'enparalelovzla':
            converted_amount = amount / conversion_rates['eur'][page]
        else:
            label_result.config(text="No disponible la conversión de Bs a EUR para la página seleccionada.") 
            return
    elif from_currency == 'USD':
            converted_amount = amount * conversion_rates['usd'][page]
    elif from_currency == 'EUR' and page != 'enparalelovzla':
            converted_amount = amount * conversion_rates['eur'][page]
    else:
        label_result.config(text="No disponible la conversión de EUR a Bs para la página seleccionada.") 
        return

    label_result.config(text=f'Resultado: {converted_amount:.2f} {to_currency}', font=("Helvetica", 14, "bold"))

# Crear ventana de tkinter 
root = tk.Tk() 
root.title("Conversor de Monedas - Venezuela")

# Añadir el título principal 
title_label = tk.Label(root, text="Valor del Dólar y Euro en Venezuela", font=("Helvetica", 18, "bold")) 
title_label.pack(pady=10)

# Crear árbol de visualización 
tree = ttk.Treeview(root, height=5) 
tree['columns'] = ('usd_price', 'eur_price', 'last_update') 
tree.column('#0', width=150, minwidth=25, anchor=tk.CENTER) 
tree.column('usd_price', anchor=tk.CENTER, width=100)
tree.column('eur_price', anchor=tk.CENTER, width=100)  
tree.column('last_update', anchor=tk.CENTER, width=200)

tree.heading('#0', text='Página', anchor=tk.CENTER) 
tree.heading('usd_price', text='USD', anchor=tk.CENTER)
tree.heading('eur_price', text='EUR', anchor=tk.CENTER)
tree.heading('last_update', text='Fecha', anchor=tk.CENTER)

# Empaquetar el árbol 
tree.pack(pady=20) 

# Botón de actualizar datos 
button_update = tk.Button(root, text="Actualizar Datos", command=lambda: threading.Thread(target=show_data).start()) 
button_update.pack(pady=10)

# Seccion de conversion de moneda
frame_conversion = tk.Frame(root) 
frame_conversion.pack(pady=20)

label_title = tk.Label(frame_conversion, text="Conversor", font=("Helvetica", 16, "bold")) 
label_title.grid(row=0, column=0, columnspan=2, pady=10)

label_amount = tk.Label(frame_conversion, text="Cantidad:") 
label_amount.grid(row=1, column=0, padx=10)
entry_amount = tk.Entry(frame_conversion)
entry_amount.grid(row=1, column=1, padx=10)

label_page = tk.Label(frame_conversion, text="Página:") 
label_page.grid(row=2, column=0, padx=10)
combo_page = ttk.Combobox(frame_conversion, values=list(names.values()))
combo_page.grid(row=2, column=1, padx=10) 
combo_page.current(0) 

label_from = tk.Label(frame_conversion, text="De:") 
label_from.grid(row=3, column=0, padx=10) 
combo_from = ttk.Combobox(frame_conversion, values=['Bs', 'USD', 'EUR']) 
combo_from.grid(row=3, column=1, padx=10) 
combo_from.current(0)

label_to = tk.Label(frame_conversion, text="A:") 
label_to.grid(row=4, column=0, padx=10) 
combo_to = ttk.Combobox(frame_conversion, values=['USD', 'EUR']) 
combo_to.grid(row=4, column=1, padx=10) 
combo_to.current(0)

# Desactivar la opción de moneda repetida y conversiones inválidas
def update_currency_options(event): 
    selected_currency = combo_from.get()
    selected_page = combo_page.get()
    if selected_currency == 'Bs':
        if selected_page == 'EnParaleloVzla':
         combo_to['values'] = ['USD']
        else:
            combo_to['values'] = ['USD', 'EUR'] 
    else: 
        combo_to['values'] = ['Bs'] 
    if combo_to.get() == selected_currency or (combo_from.get() in ['USD', 'EUR'] and combo_to.get() in ['USD', 'EUR']): 
        combo_to.set('')

combo_from.bind('<<ComboboxSelected>>', update_currency_options)
combo_page.bind('<<ComboboxSelected>>', update_currency_options)
combo_from.set('Bs') 
combo_to.set('USD')

button_convert = tk.Button(frame_conversion, text="Convertir", command=convert_currency) 
button_convert.grid(row=5, column=0, columnspan=2, pady=10)

label_result = tk.Label(root, text="Resultado: ", font=("Helvetica", 14, "bold")) 
label_result.pack(pady=10)

# Etiqueta para mostrar el estado de la conexión
label_status = tk.Label(root, text="", font=("Helvetica", 12, "bold")) 
label_status.pack(pady=10)

# Mostrar datos 
show_data() 

# Ejecutar aplicación 
root.mainloop()
