import json

ITEM_DIR = 'img/items/'

class Item:
    def __init__(self, name, itemText=''):
        self.name = name
        self.itemText = itemText

    def next_state(self):
        # Base Item has no alternate states
        pass

    def prev_state(self):
        # Base Item has no alternate states
        pass

    def get_image_path(self):
        return f'{ITEM_DIR}{self.name}.png'

    def get_json_state(self):
        return { 'type': 'Item', 'name': self.name, 'itemText': self.itemText }

    def isDark(self):
        # Base Item can never be dark
        return False

class ProgressiveItem(Item):
    def __init__(self, states, current_state=0, itemText=''):
        self.states = states
        self.current_state = current_state
        super().__init__(states[self.current_state], itemText)

    def next_state(self):
        self.current_state = (self.current_state + 1) % len(self.states)

    def prev_state(self):
        if self.current_state == 0:
            self.current_state = len(self.states) - 1
        else:
            self.current_state -= 1

    def get_image_path(self):
        return f'{ITEM_DIR}{self.states[self.current_state]}.png'

    def get_json_state(self):
        return {
                'type': 'ProgressiveItem',
                'states': self.states,
                'current_state': self.current_state,
                'itemText': self.itemText
               }

    def isDark(self):
        return self.current_state == 0

class ToggleItem(ProgressiveItem):
    def __init__(self, name, current_state=0, itemText=''):
        super().__init__([name,name], current_state, itemText)
        self.name = name

    def get_json_state(self):
        return {
                'type': 'ToggleItem',
                'name': self.name,
                'current_state': self.current_state,
                'itemText': self.itemText
               }

class NumberedItem(Item):
    def __init__(self, name, max_num, current_num=0, itemText=''):
        super().__init__(name, itemText)
        self.max_num = max_num
        self.current_num = current_num

    def next_state(self):
        self.current_num = (self.current_num + 1) % (self.max_num + 1)

    def prev_state(self):
        if self.current_num == 0:
            self.current_num = self.max_num
        else:
            self.current_num -= 1

    def get_image_path(self):
        return f'{ITEM_DIR}{self.name}.png'

    def isNotMaxed(self):
        return self.current_num != self.max_num

    def get_json_state(self):
        return {
                'type': 'NumberedItem',
                'name': self.name,
                'max_num': self.max_num,
                'current_num': self.current_num,
                'itemText': self.itemText
               }

    def isDark(self):
        return self.current_num == 0

def getDefaultItems():
    try:
        with open('template.json') as infile:
            tracker_state = json.load(infile)
            state_items = tracker_state['items']
            default_items = convertJSONtoItems(state_items)

        return default_items
    except FileNotFoundError:
        # If there is no template file, fall back to this set of defaults
        return getHardcodedDefaults()

def getHardcodedDefaults():
    default_items = [
        [ProgressiveItem(['fishingrod','fishingrod','fishingrod_earing']),
         ToggleItem('slingshot'),
         ToggleItem('lantern'),
         NumberedItem('smallkey', 4, itemText='Forest'),
         ToggleItem('bosskey', itemText='Forest'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Forest')],
        [ToggleItem('galeboomerang'),
         ToggleItem('ironboots'),
         ProgressiveItem(['bow','bow','bow_big','bow_giant']),
         NumberedItem('smallkey', 3, itemText='Goron'),
         ProgressiveItem(['goronbosskey', 'goronkeyshard1', 'goronkeyshard2', 'goronbosskey'], itemText='Goron'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Goron')],
        [ToggleItem('hawkeye'),
         ProgressiveItem(['bombbag', 'bombbag1', 'bombbag2', 'bombbag3']),
         ToggleItem('giantbombbag'),
         NumberedItem('smallkey', 3, itemText='Lakebed'),
         ToggleItem('bosskey', itemText='Lakebed'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Lakebed')],
        [ProgressiveItem(['clawshot','clawshot','clawshot_double']),
         ToggleItem('spinner'),
         ToggleItem('ballandchain'),
         NumberedItem('smallkey', 5, itemText='Arbiters'),
         ToggleItem('bosskey', itemText='Arbiters'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Arbiters')],
        [ProgressiveItem(['dominionrod','dominionrod','dominionrod_powered']),
         ToggleItem('horsecall'),
         NumberedItem('bottle', 4),
         NumberedItem('smallkey', 4, itemText='Snowpeak'),
         ToggleItem('bedroomkey', itemText='Snowpeak'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Snowpeak')],
        [ToggleItem('memo'),
         ToggleItem('sketch'),
         ProgressiveItem(['book','book','book1','book2','book3','book4','book5','book6']),
         NumberedItem('smallkey', 3, itemText='Time'),
         ToggleItem('bosskey', itemText='Time'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Time')],
        [NumberedItem('hiddenskill', 7),
         ProgressiveItem(['sword_wooden','sword_wooden','sword_ordon','sword_master','sword_light']),
         ProgressiveItem(['shield_ordon','shield_ordon','shield_wooden','shield_hylian']),
         NumberedItem('smallkey', 1, itemText='City'),
         ToggleItem('bosskey', itemText='City'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='City')],
        [ProgressiveItem(['wallet','wallet_big','wallet_giant']),
         ToggleItem('armor_zora'),
         ToggleItem('armor_magic'),
         NumberedItem('smallkey', 7, itemText='Twilight'),
         ToggleItem('bosskey', itemText='Twilight'),
         ProgressiveItem(['questionmark', 'questionmark', 'fusedshadow', 'mirrorshard'], itemText='Twilight')],
        [ToggleItem('shadowcrystal'),
         NumberedItem('soul', 60),
         NumberedItem('bug', 24),
         NumberedItem('smallkey', 3, itemText='Hyrule'),
         ToggleItem('bosskey', itemText='Hyrule'),
         NumberedItem('greenrupee', 2)]
    ]

    return default_items

def convertJSONtoItems(json_state):
    items = []
    for row in json_state:
        item_row = []
        for item_state in row:
            item_type = item_state['type']
            if item_type == 'Item':
                item = Item(item_state['name'], item_state['itemText'])
            elif item_type == 'ProgressiveItem':
                item = ProgressiveItem(
                        item_state['states'],
                        item_state['current_state'],
                        item_state['itemText']
                )
            elif item_type == 'ToggleItem':
                item = ToggleItem(
                        item_state['name'],
                        item_state['current_state'],
                        item_state['itemText']
                )
            elif item_type == 'NumberedItem':
                item = NumberedItem(
                        item_state['name'],
                        item_state['max_num'],
                        item_state['current_num'],
                        item_state['itemText']
                )
            else:
                print(f"Error: Item type {item_type} does not exist!")
                exit(1)
            item_row.append(item)
        items.append(item_row)

    return items
