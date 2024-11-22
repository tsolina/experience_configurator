from application.application import Application
from application.eval_selected import EvalSelected
import experience as exp

class GetAppliedMaterial:
    def __init__(self, parent):
        self.application: Application = parent.application
        self._process_selection()

    def _check_look(self, evaluate:EvalSelected):
        found = False

        for name, look_object in self.application.active_project.look_actors.items():
            if look_object.actor.path == evaluate.path:
                self.application.status_message = f"current look: {look_object.look_active}"
                found = True
                break

        if not found:
            self.application.error_message = "no look on selected object"

    def _evaluate_selection(self, sel: exp.Selection):
        if not sel.count():
            self._error_callback("selection empty")
            return

        evaluate = EvalSelected(sel.first().value())
        self.application.look_file.ready(lambda look: self._check_look(evaluate))

    def _error_callback(self, msg):
        self.application.error_message = msg

    def _process_selection(self):
        self.application.selection(lambda _sel: self._evaluate_selection(_sel), self._error_callback)

"""
Public Class CGetAppliedMaterial
    Public Sub New()
        App.Selection(Sub(_sel)
                          _sel.CountEx(Sub()
                                           Dim eS As New CEvalSelected(_sel.First.Value)

                                           App.LookFile.Ready(Sub(look)
                                                                  Dim found As Boolean = False

                                                                  App.Model.ActiveProject.LookActors.ForEach(Sub(oLook)
                                                                                                                 If found Then Exit Sub
                                                                                                                 If oLook.Actor.Path = eS.Path Then
                                                                                                                     App.StatusMessage = "current look: " & oLook.LookActive
                                                                                                                     found = True
                                                                                                                 End If
                                                                                                             End Sub)

                                                                  If found = False Then
                                                                      App.ErrorMessage = "no look on selected object"
                                                                  End If
                                                              End Sub)

                                       End Sub, Sub(msg) App.ErrorMessage = msg)
                      End Sub, Sub(msg) App.ErrorMessage = msg)
    End Sub
End Class
"""