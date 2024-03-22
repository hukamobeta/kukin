import os
import shutil
import json


from config import Config

DIRECTORY = os.path.abspath(Config.DIRECTORY)
CURR_DIR = []
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_user_credentials():
    try:
        with open(os.path.join(project_root, 'users.json'), 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_credentials(user_credentials):
    with open(os.path.join(project_root, 'users.json'), 'w') as file:
        json.dump(user_credentials, file, indent=4)


def check_and_update_quota(login, user_dir, file_size):
    user_credentials = load_user_credentials()
    user_info = user_credentials.get(login)
    if user_info and user_info["used"] + file_size <= user_info["quota"]:
        user_info["used"] += file_size
        save_user_credentials(user_credentials)
        return True
    return False

def showDIR(user_dir=None, login=None, is_admin=False, flags=None) -> str:
    """
    Показать содержимое директории.
    Аргументы user_dir, login, is_admin и flags принимаются, но не используются напрямую.
    """
    files = ""
    for file in os.listdir(user_dir):
        files += f'{file}\n'
    return files[:-1] if files != "" else 'Пустая директория'


def listUsers(user_dir=None, login=None, is_admin=False, flags=None) :
    if not is_admin:
        return "Доступ запрещен: только для администраторов."
    user_credentials = load_user_credentials()
    users_list = "\n".join(user_credentials.keys())
    return f"Список пользователей:\n{users_list}"


def createDIR(*names, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    for name in names:
        path_dir, error_dir = checkDir(name, check=False)
        if error_dir != '':
            return error_dir
        os.makedirs(path_dir)
        return "Директория создана"


def deleteDIR(*names,user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    for name in names:
        path_dir, error_dir = checkDir(name)
        if error_dir != '':
            return error_dir
        if "-r" in flags:
            shutil.rmtree(path_dir, ignore_errors=False, onerror=None)
            return "Директория удалена"
        elif len(os.listdir(path_dir)) == 0:
            shutil.rmtree(path_dir, ignore_errors=False, onerror=None)
            return "Директория удалена"
        else:
            return "Директория пустая!"


def moveToDir(directory, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    global CURR_DIR
    new_dir, error_dir = checkDir(directory)
    if error_dir != '':
        return error_dir
    CURR_DIR = new_dir[len(DIRECTORY) + 1:].split(Config.SEPARATOR_DIR)
    os.chdir(os.path.join(DIRECTORY, *CURR_DIR))
    return 'Перемещен в другую директорию'


def createFile(name, user_dir=None, login=None, is_admin=False, flags=None) :
    if user_dir is None or login is None:
        return "Ошибка: не указана рабочая директория или логин пользователя."
    path_file = os.path.join(user_dir, name)
    
    estimated_size = 1024    
    if not check_and_update_quota(login, user_dir, estimated_size):
        return "Превышена квота дискового пространства!"
    
    if os.path.exists(path_file):
        return "Файл уже существует!"
    
    with open(path_file, "w") as f:
        f.write("Новый файл создан.\n")
    
    if not is_admin:
        return "Доступ запрещен: только для администраторов."
    file_path = os.path.join(user_dir, name)
    try:
        with open(file_path, "w") as f:
            f.write("Содержимое файла")
        return "Файл успешно создан."
    except Exception as e:
        return f"Ошибка при создании файла: {e}"



def writeToFile(text, name, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    access = "w"
    if "-a" in flags:
        access = "a"
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    f = open(path_file, access)
    f.write(text + "\n")
    f.close()
    return "Добавили текст в файл"


def readFile(name, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    f = open(path_file, "r")
    res = ''
    for line in f:
        res += line.strip() + '\n'
    f.close()
    return res[:-1] if res != '' else ' '


def deleteFile(name, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    os.remove(path_file)
    return 'Файл удален'


def copyFile(name, new_dir, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    path_dir, error_dir = checkDir(new_dir, check=False)
    if error_dir != '':
        return error_dir
    shutil.copy(path_file, path_dir)
    return 'Файл скопирован в другую директорию'


def moveFile(name, new_dir, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    path_dir, error_dir = checkDir(new_dir, check=False)
    if error_dir != '':
        return error_dir
    shutil.move(path_file, path_dir)
    return 'Файл перемещен в другую директорию'


def renameFile(name, new_name, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path_file, error_file = checkFile(name)
    if error_file != '':
        return error_file
    path_dir, error_dir = checkDir(new_name, check=False)
    if error_dir != '':
        return error_dir
    os.rename(path_file, path_dir)
    return 'Файл переименован'


def uploadFile(name, text, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    with open(name, "w") as file:
        file.write(text)
        file.close()
    return 'Файл загружен'


def cd(current_dir, target_dir, user_dir, **kwargs):
    new_dir = os.path.normpath(os.path.join(current_dir, target_dir))
    if not new_dir.startswith(user_dir):
        return "Переход за пределы вашей директории запрещен.", current_dir
    if os.path.exists(new_dir) and os.path.isdir(new_dir):
        return f"Перешли в директорию: {new_dir[len(user_dir):]}", new_dir
    else:
        return "Указанная директория не существует.", current_dir

def pwd(current_dir, **kwargs):
    return current_dir

def checkDir(*paths, check=True, user_dir=None, login=None, is_admin=False, flags=None) -> str:
    path = os.path.abspath(os.path.join(DIRECTORY, *CURR_DIR, *paths))
    error = ''
    if check:
        if not os.path.exists(path):
            error += "Директории не существует!\n"
        if not os.path.isdir(path):
            error += "Пути не существует\n"
    if DIRECTORY != path[:len(DIRECTORY)]:
        error += "Выход за пределы рабочей директории!\n"
    return path, error[:-1]


def checkFile(*paths, check=True, user_dir=None, login=None, is_admin=False, flags=None)  -> str:
    path = os.path.abspath(os.path.join(DIRECTORY, *CURR_DIR, *paths))
    error = ''
    if check:
        if not os.path.exists(path):
            error += "Файла не существует!\n"
        if not os.path.isfile(path):
            error += "Путь не существует!\n"
    if DIRECTORY != path[:len(DIRECTORY)]:
        error += "Выход за пределы рабочей директории!\n"
    return path, error[:-1]

def ls(current_dir, **kwargs):
    try:
        items = os.listdir(current_dir)
        if not items:
            return "Директория пуста."
        return "\n".join(items)
    except Exception as e:
        return f"Ошибка: {e}"

def upload(file_name, file_content, current_dir, **kwargs):
    try:
        file_path = os.path.join(current_dir, file_name)
        with open(file_path, "wb") as file:
            file.write(file_content.encode('utf-8'))
        return "Файл успешно загружен."
    except Exception as e:
        return f"Ошибка при загрузке файла: {e}"
    
def download(file_name, current_dir, **kwargs):
    try:
        file_path = os.path.join(current_dir, file_name)
        if not os.path.exists(file_path):
            return "Файл не найден.", None
        with open(file_path, "rb") as file:
            file_content = file.read()
        return "Файл готов к скачиванию.", file_content
    except Exception as e:
        return f"Ошибка при скачивании файла: {e}", None