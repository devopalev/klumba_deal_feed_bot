import source.BitrixWorker as BW


def create_reclamation(deal_id, fullname):
    params_bp = {'TEMPLATE_ID': '801',
                 'DOCUMENT_ID': ['crm', 'CCrmDocumentDeal', f'DEAL_{deal_id}'],
                 'PARAMETERS': {'source_reclamation':
                                    f'Создано из telegram на основе опоздания заказа. Создатель: {fullname}'}}

    res = BW.send_request('bizproc.workflow.start', params=params_bp)
    print(res)
