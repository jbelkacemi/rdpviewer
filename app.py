import ctypes
import subprocess

import eel
import wmi


def hideConsole():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)


hideConsole()


def command(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = p.communicate()
    return out


def get_full_name(name):
    c = wmi.WMI()
    wql = f'SELECT FullName FROM Win32_UserAccount WHERE name="{name}"'
    fullname = c.query(wql)
    full_name = name
    if len(fullname) > 0:
        full_name = fullname[0].FullName
    else:
        full_name = name
    return full_name


def get_ignore_user():
    try:
        with open("ignoreuser") as f:
            lines = f.read().splitlines()
        lines = [i for i in lines if i]
        return lines
    except:
        return ""


def parsedata(data_out, computer):
    # convertir datso tipo string a lista seprando con saltos de linea
    data_to_list = data_out.split("\n")
    # eliminar el primer index de la lista que no es necesario
    del data_to_list[0]
    # eliminar los elementos vacios de la lista
    try:
        data_to_list.remove("")
    except:
        pass
    user_ignored = get_ignore_user()
    list_data = list()
    for i in data_to_list:
        i_to_list = i.split()

        if not i_to_list[0].lower() in list(map(str.lower, user_ignored)):
            if len(i_to_list) == 7:
                dict_data = {"id": i_to_list[2], "name": i_to_list[0], "state": i_to_list[3],
                             "inactivity": i_to_list[4],
                             "logon": i_to_list[5] + " " + i_to_list[6], "computer": computer,
                             "fullname": get_full_name(i_to_list[0])}
                list_data.append(dict_data)
            elif len(i_to_list) == 6:
                dict_data = {"id": i_to_list[1], "name": i_to_list[0], "state": i_to_list[2],
                             "inactivity": i_to_list[3],
                             "logon": i_to_list[4] + " " + i_to_list[5], "computer": computer,
                             "fullname": get_full_name(i_to_list[0])}
                list_data.append(dict_data)
    return list_data


def main():
    with open("servers") as f:
        lines = f.read().splitlines()
    lines = [i for i in lines if i]
    all_data_user = []
    for line in lines:
        cmd = f"query user /SERVER:{line}"
        output_command = command(cmd)
        if "ESTADO" in output_command:
            all_data_user += parsedata(output_command, line)

    return all_data_user


def connect(id, computer):
    cmd = f"mstsc /shadow:{id} /admin /noconsentprompt /v:{computer}"
    command(cmd)


eel.init('web')


@eel.expose
def bingR():
    return main()


@eel.expose  # Expose this function to Javascript
def connection(id, computer):
    connect(id, computer)


eel.start('index.html', mode='chrome', size=(900, 700), position=(50, 50), host='localhost')
