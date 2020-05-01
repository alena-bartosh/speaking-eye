import re
import subprocess


def get_wm_class(xid: int) -> str:
    """Get WM_CLASS window attribute from the xprop utility"""
    process_result = subprocess.run(['xprop', '-id', f'{xid}', 'WM_CLASS'], stdout=subprocess.PIPE)
    xprop_output = process_result.stdout.decode('utf-8')

    wm_class_re = r'WM_CLASS\(STRING\) = "(.+)", "(.+)"$'
    search = re.search(wm_class_re, xprop_output)

    if not search:
        raise Exception(f'WM_CLASS does not found in [{xprop_output}]')

    return search.group(2)
