# %%


dt0 = DlgText('dt0', text='Hi!', edges=[{'to_id': 'dt1'}])
dt1 = DlgText('dt1', edges=[{'to_id': 'dr1'}], text='H ow are you!')
dr1 = DlgResponse('dr1', [{'to_id': 'dt2', 'text': 'Fyne'}, {
                  'to_id': 'dt3', 'text': 'Bad'}, {
    'to_id': 'dt3', 'text': 'Ok', 'condition': True}])
dt2 = DlgText('dt2', text='Gewd!', edges=[{'to_id': 'db1'}])
dt3 = DlgText('dt3', [{'to_id': 'dt0'}], text='Try again!')

db1 = DlgBranch('db1', edges=[{'to_id': 'dt0', 'condition': True}, {
                'to_id': 'dt1', 'condition': False}])

#%%
dg = {n.to_id: n for n in (dt0, dt1, dr1, dt2, dt3, db1)
      }
dg['0'] = dt0

# %%


class System():

    def __init__(self, handlers: List = None):
        self.handlers = handlers or []

    def _gethandler(self, handler):
        if hasattr(handler, 'process'):
            return handler.process

        return handler

    def process(self, event, context=None):
        context = context or self
        return reduce(lambda event, handler: self._gethandler(handler)(event, context), self.handlers, event)


def hndlr1(event, context):
    print(event)
    print(context)
    return event


def hndlr2(event, context):

    event['text'] = 'Processed ' + event['text']
    return event


subsys = System([hndlr2, hndlr1])
