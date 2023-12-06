import os


def save_info_to_file(user_id, info, name):
    file_name = f"user_{user_id}_{name}.txt"
    with open(file_name, 'w') as file:
        file.write(info)
    return file_name


def delete_file(filename):
    os.remove(filename)
