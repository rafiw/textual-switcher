import os
import sys
import subprocess


BINDING_NAME = "textual-switcher"
CUSTOM_KEYB_PATH = ""
BINDING_LIST_PATH = ""
WM = ''
DEFAULT_DESKTOP = "gnome"

def set_paths():
    global BINDING_LIST_PATH
    global CUSTOM_KEYB_PATH
    global WM
    if WM == 'cinnamon':
        BINDING_LIST_PATH = "/org/cinnamon/desktop/keybindings/custom-list"
        CUSTOM_KEYB_PATH = "/org/cinnamon/desktop/keybindings/custom-keybindings"
    if WM in ('gnome', 'unity'):
        BINDING_LIST_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
        CUSTOM_KEYB_PATH = BINDING_LIST_PATH


def dconf_write(path, value):
    cmd = ["dconf", "write", path, value]
    print "Setting {} to {}".format(path, value)
    subprocess.check_output(cmd)


def dconf_read(path):
    cmd = ["dconf", "read", path]
    output = subprocess.check_output(cmd)
    return output


def get_binding_list():
    bindings = dconf_read(BINDING_LIST_PATH)
    bindings = bindings.strip()
    if not bindings:
        return []
    bindings = bindings[bindings.index("["):] # Deal with '@as'
    bindings = bindings[1:-1]
    bindings = bindings.replace("'", "")
    bindings = bindings.split(",")
    bindings = [binding.strip() for binding in bindings if binding.strip()]
    return bindings


def does_binding_exist(name):
    bindings = get_binding_list()
    names = [binding.strip(" /").split("/")[-1] for binding in bindings]
    return name in names


def set_binding(cmd, key_combination):
    new_binding_path = "{}/{}".format(CUSTOM_KEYB_PATH, BINDING_NAME)
    if does_binding_exist(BINDING_NAME):
        print "A key binding list-name entry already exists."
    else:
        bindings = get_binding_list()
        if WM == 'gnome':
            new_binding_path_with_slash = "{}/".format(new_binding_path)
            bindings.append(new_binding_path_with_slash)
        elif WM == 'cinnamon':
            bindings.append(new_binding_path)
        dconf_write(BINDING_LIST_PATH, str(bindings))

    print "Setting key bindings."
    binding_values = dict(name=BINDING_NAME,
                          binding=key_combination,
                          command=cmd)
    for name, value in binding_values.iteritems():
        binding_path = "{}/{}".format(new_binding_path, name)
        value = "'{}'".format(value)
        dconf_write(binding_path, value)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: python {} command binding".format(__file__)
        print "Example binding: <Primary><Alt>w"
        print sys.argv
        sys.exit(1)
    cmd = sys.argv[1]
    key_combination = sys.argv[2]
    wm = os.getenv("XDG_CURRENT_DESKTOP", DEFAULT_DESKTOP)
    if 'gnome' in wm.lower():
        WM = 'gnome'
    elif 'cinnamon' in wm.lower():
        WM = 'cinnamon'
    else:
        print "Unsupported desktop environment: {}".format(wm)
        sys.exit(1)
    set_paths()
    set_binding(cmd, key_combination)
