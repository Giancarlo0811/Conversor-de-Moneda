import requests
import tkinter as tk
from tkinter import ttk

# Listas de monedas y paginas
pages = ['bcv', 'enparalelovzla', 'italcambio']
monitors= ['usd', 'eur']

# Función para obtener datos de una página específica y moneda
def get_data(page, monitor):
    url = f'https://pydolarve.org/api/v1/dollar?page={page}&monitor={monitor}'
    response = requests.get(url)
    if response.status_code == 200: 
        return response.json()
    else:
        print(f'Error: {response.status_code}') 
        return None

# Función para mostrar datos
def show_data(): 
    for page in pages:
        usd_price, eur_price, last_update = None, None, None
        if page == 'enparalelovzla':
            data = get_data(page, 'enparalelovzla')
            if data:
                usd_price = data['price']
                last_update = data['last_update']
        else:
            for monitor in monitors:
                data = get_data(page, monitor)
                if data:
                    if monitor == 'usd':
                        usd_price = data['price']
                    elif monitor == 'eur':
                        eur_price = data['price']
                    last_update = data['last_update']

        tree.insert('', 'end', text=page, values=(usd_price, eur_price, last_update))


# Crear ventana de tkinter 
root = tk.Tk() 
root.title("Precio del Dólar y Euro en Venezuela") 

# Crear árbol de visualización 
tree = ttk.Treeview(root) 
tree['columns'] = ('usd_price', 'eur_price', 'last_update') 
tree.column('#0', width=120, minwidth=25, anchor=tk.W) 
tree.column('usd_price', anchor=tk.CENTER, width=80)
tree.column('eur_price', anchor=tk.CENTER, width=80)  
tree.column('last_update', anchor=tk.W, width=150)

tree.heading('#0', text='Página', anchor=tk.W) 
tree.heading('usd_price', text='Precio Dólar', anchor=tk.CENTER)
tree.heading('eur_price', text='Precio Euro', anchor=tk.CENTER)
tree.heading('last_update', text='Última Actualización', anchor=tk.W)

# Mostrar datos 
show_data() 

# Empaquetar el árbol 
tree.pack(pady=20) 

# Ejecutar aplicación 
root.mainloop()