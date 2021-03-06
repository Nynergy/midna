import json

ITEM_DIR = 'img/items/'

class Item:
    def __init__(self, name):
        self.name = name

    def next_state(self):
        # Base Item has no alternate states
        pass

    def prev_state(self):
        # Base Item has no alternate states
        pass

    def get_image_path(self):
        return f'{ITEM_DIR}{self.name}.png'

    def get_json_state(self):
        return { 'type': 'Item', 'name': self.name }

    def isDark(self):
        # Base Item can never be dark
        return False

class ProgressiveItem(Item):
    def __init__(self, states, current_state=0):
        self.states = states
        self.current_state = current_state
        super().__init__(states[self.current_state])

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
        return { 'type': 'ProgressiveItem', 'states': self.states, 'current_state': self.current_state }

    def isDark(self):
        return self.current_state == 0

class ToggleItem(ProgressiveItem):
    def __init__(self, name, current_state=0):
        super().__init__([name,name], current_state)
        self.name = name

    def get_json_state(self):
        return { 'type': 'ToggleItem', 'name': self.name, 'current_state': self.current_state }

class NumberedItem(Item):
    def __init__(self, name, max_num, current_num=0):
        super().__init__(name)
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
        return { 'type': 'NumberedItem', 'name': self.name, 'max_num': self.max_num, 'current_num': self.current_num }

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
         ToggleItem('galeboomerang'),
         ToggleItem('diababa'),
         NumberedItem('smallkey', 4)],
        [ToggleItem('ironboots'),
         ProgressiveItem(['bow','bow','bow_big','bow_giant']),
         ToggleItem('hawkeye'),
         ProgressiveItem(['bombbag', 'bombbag1', 'bombbag2', 'bombbag3', 'bombbag4']),
         ToggleItem('fyrus'),
         NumberedItem('smallkey', 3)],
        [ProgressiveItem(['clawshot','clawshot','clawshot_double']),
         ToggleItem('spinner'),
         ToggleItem('ballandchain'),
         ProgressiveItem(['dominionrod','dominionrod','dominionrod_powered']),
         ToggleItem('morpheel'),
         NumberedItem('smallkey', 3)],
        [ProgressiveItem(['wallet','wallet_big','wallet_giant']),
         ProgressiveItem(['shield_ordon','shield_ordon','shield_wooden','shield_hylian']),
         ProgressiveItem(['sword_wooden','sword_wooden','sword_ordon','sword_master','sword_light']),
         NumberedItem('bottle', 4),
         ToggleItem('stallord'),
         NumberedItem('smallkey', 5)],
        [Item('tunic'),
         ToggleItem('armor_zora'),
         ToggleItem('armor_magic'),
         ProgressiveItem(['pumpcheese_both','pumpcheese_pumpkin','pumpcheese_cheese','pumpcheese_both']),
         ToggleItem('blizzeta'),
         NumberedItem('smallkey', 4)],
        [ToggleItem('letter'),
         ToggleItem('invoice'),
         ToggleItem('woodenstatue'),
         ToggleItem('charm'),
         ToggleItem('armogohma'),
         NumberedItem('smallkey', 3)],
        [ProgressiveItem(['book','book','book1','book2','book3','book4','book5','book6']),
         ToggleItem('memo'),
         ToggleItem('sketch'),
         ToggleItem('horsecall'),
         ToggleItem('argorok'),
         NumberedItem('smallkey', 1)],
        [NumberedItem('bug', 24),
         NumberedItem('soul', 60),
         NumberedItem('heartpiece', 45),
         NumberedItem('heartcontainer', 8),
         ToggleItem('zant'),
         NumberedItem('smallkey', 7)],
        [NumberedItem('hiddenskill', 7),
         NumberedItem('greenrupee', 2),
         ToggleItem('vessel'),
         ToggleItem('shadowcrystal'),
         ToggleItem('ganondorf'),
         NumberedItem('smallkey', 3)]
    ]

    return default_items

def convertJSONtoItems(json_state):
    items = []
    for row in json_state:
        item_row = []
        for item_state in row:
            item_type = item_state['type']
            if item_type == 'Item':
                item = Item(item_state['name'])
            elif item_type == 'ProgressiveItem':
                item = ProgressiveItem(item_state['states'], item_state['current_state'])
            elif item_type == 'ToggleItem':
                item = ToggleItem(item_state['name'], item_state['current_state'])
            elif item_type == 'NumberedItem':
                item = NumberedItem(item_state['name'], item_state['max_num'], item_state['current_num'])
            else:
                print(f"Error: Item type {item_type} does not exist!")
                exit(1)
            item_row.append(item)
        items.append(item_row)

    return items
