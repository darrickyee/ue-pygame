from typing import Any
from ...classes import EcsGameSystem
from .fsm import Dialogue


class DialogueSystem(EcsGameSystem):

    @property
    def actions(self):
        return {'SELECT_OPTION': self._select,
                'START_DIALOGUE': self._start}

    def _on_view(self, dlgview: dict):
        self._context.update('/dialogue', dlgview)

    def _start(self, data: dict[str, Any]):
        dlg_id = data.get('dlg_id', None)
        if dlg_id:
            dlg = self._locals['dialogue'] = Dialogue(G, self._context.state)
            self._on_view(dlg.view())
            self._locals['subscription'] = dlg.views.subscribe(self._on_view)

    def _select(self, option):
        if currdlg := self._locals.get('dialogue', None):
            currdlg.send(option)
            if self._locals['dialogue'].state is None:
                self._stop()

    def _stop(self):
        self._on_view({'speaker': '', 'text': '', 'responses': []})
        if 'subscription' in self._locals:
            self._locals['subscription'].dispose()
            del self._locals['subscription']

        try:
            del self._locals['dialogue']
        except KeyError:
            pass
