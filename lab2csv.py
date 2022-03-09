from itertools import zip_longest
from os import getcwd
from os.path import exists
from sys import argv, exit
import logging
from webbrowser import open as wopen

from unidecode import unidecode
import PySimpleGUI as sg

import ctypes
import platform

def make_dpi_aware() -> None:
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

make_dpi_aware()

sg.theme('Reddit')
layout = [
    [
        sg.Input(key='load_lab', do_not_clear=False, enable_events=True, visible=False),
        sg.FileBrowse('Browse & Convert', file_types = (('LAB Files', '*.lab'), ('All files', '*')),
            initial_folder=getcwd(), button_color='green'),
        sg.Button('Quit', button_color='red')
    ],
    [sg.Multiline('', size=(50, 10), key='output', disabled=True, expand_x=True)],
    [sg.Text("Drag'n'Drop lab file onto this exe file should work too.")],
    [sg.Text('https://github.com/xtotdam/lab2csv', enable_events=True, key='github', font='Any 8', expand_x=True, justification='right', text_color='blue')],
]

def convert_infile_to_outfile(s):
    return s + '.csv'



def convert_lab_to_csv(infile:str, outfile:str, printfn) -> None:

    # Open & read
    printfn(f"Opening {infile}", t='blue')
    try:
        f = open(infile, 'r', encoding='utf16')
    except:
        try:
            f = open(infile, 'r', encoding='utf8')
        except:
            raise

    labfile = f.read()
    f.close()


    # Convert UTF16 -> ASCII
    labfile = unidecode(labfile, errors='replace')


    # Read this weird INI format
    splits = labfile.split('[')
    sections = list()
    for s in splits:
        try:
            name, contents = s.split(']')
            sections.append((name, contents.strip()))
        except ValueError:
            logging.warning(f'Cannot split "{s[:20]}"')

    printfn(f"Found {[x[0] for x in sections].count('vecteur')} columns with data")


    def normalize_points(points:str) -> 'List[float]':
        points = points.split('{')[-1][:-1]
        points = filter(bool, points.replace('\n', ' ').replace('\t', ' ').split(' '))
        points = list(map(float, points))
        return points


    # Parse 'vecteur' sections
    # Logic:
    # Single line must contain '='
    # Lines delimiter '\n' -> ';\n', this allowsc to split them later by ';' and not by '\n'
    # Later split and prepare for sorting
    data = list()
    for section in sections:
        if section[0] == 'vecteur':
            section_dict = dict()

            contents = section[1].split('\n')
            c1 = list()
            for c in contents:
                if '=' in c and '{' not in c:
                    c += ';'
                c1.append(c)
            c3 = ''.join(c1).replace('}', '};').split(';')
            for c in c3:
                try:
                    # print(c)
                    parts = [x.strip() for x in c.split('=')]
                    if parts[0] == 'points':
                        section_dict[parts[0]] = normalize_points(parts[1])
                    if parts[0] in ('oid', 'nom'):
                        section_dict[parts[0]] = parts[1].strip('"')
                except (ValueError, IndexError):
                    printfn(f'*** Error with section. Skip: {c}')

            section_dict['name'] = f'{section_dict["oid"]}_{section_dict["nom"]}'
            section_dict['sortname'] = (int(section_dict["oid"]), section_dict["name"])
            data.append(section_dict)

    columns = [x[1] for x in sorted([y['sortname'] for y in data], key=lambda x:x[0])]
    final_data = dict()
    for d in data:
        final_data[d['name']] = d['points']

    printfn('Columns:')
    for c in columns:
        printfn(f'  {c} (length {len(final_data[c])})')


    printfn(f'Writing into {outfile}', t='green')
    with open(outfile, 'w') as f:
        f.write(','.join(columns) + '\n')

        rows = map(list, zip_longest(*[final_data[n] for n in columns], fillvalue=''))
        for row in rows:
            f.write(','.join(map(str,row)) + '\n')


if __name__ == '__main__':
    if len(argv) > 1:

        def printfn(s, **kwargs):
            print(s)

        infile = argv[1]
        outfile = convert_infile_to_outfile(infile)
        convert_lab_to_csv(infile, outfile, printfn)
        exit()

    window = sg.Window('lab -> csv', layout, resizable=True, finalize=True)

    def printfn(s, **kwargs):
        window['output'].print(''.join(map(str, s)), **kwargs)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Quit'):
            break

        if event == 'github':
            wopen('https://github.com/xtotdam/lab2csv')

        if event == 'load_lab':
            infile = values['load_lab']
            outfile = convert_infile_to_outfile(infile)
            if exists(outfile):
                printfn(f'Error: {outfile} already exists!', t='red')
            else:
                try:
                    convert_lab_to_csv(infile, outfile, printfn)
                except Exception as e:
                    printfn(e)
