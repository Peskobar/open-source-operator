from plugins import Plugin

class SamplePlugin(Plugin):
    def register_actions(self):
        return {"echo": lambda x: x}

def register():
    return SamplePlugin()
