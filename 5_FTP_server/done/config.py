class Config:
    DIRECTORY = "WorkDir"
    SEPARATOR_DIR = '\\'
    COMMANDS = {
        'ls': 'ls',
        'dir': 'showDIR',
        'cd': 'cd',
        'mkdir': 'createDIR',
        'rmdir': 'deleteDIR',
        'touch': 'createFile',
        'write': 'writeToFile',
        'cat': 'readFile',
        'rm': 'deleteFile',
        'cp': 'copyFile',
        'move': 'moveFile',
        'rename': 'renameFile',
        'pwd': 'pwd',
        'upload': 'upload',
        'download': 'download'
    }