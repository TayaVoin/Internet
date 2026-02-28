# Имитация базы данных (в памяти)
devices_db = []
id_counter = 1

def get_all_devices():
    return devices_db

def get_device_by_id(device_id: int):
    return next((d for d in devices_db if d["id"] == device_id), None)

def create_device_in_db(device_data):
    global id_counter
    new_device = {
        "id": id_counter,
        **device_data
    }
    devices_db.append(new_device)
    id_counter += 1
    return new_device

def clear_db():
    global devices_db, id_counter
    devices_db.clear()
    id_counter = 1