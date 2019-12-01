from django.views.generic import FormView
from menu_proposal.forms import ProposalForm


class MenuProposalView(FormView):
    """
    献立提案入力フォーム
    """
    form_class = ProposalForm
    template_name = "Proposal/form.html"
