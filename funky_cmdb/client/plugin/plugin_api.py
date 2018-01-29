from plugin.linux import sysinfo


def WindowsSysInfo():
    from plugin.windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()


def LinuxSysInfo():
    return sysinfo.cillect()
