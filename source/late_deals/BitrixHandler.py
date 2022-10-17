import source.BitrixWorker as BW


def create_reclamation(deal_id, fullname):
    source_text = f'Создано из telegram на основе опоздания заказа {deal_id}. Создатель: {fullname}'
    params_bp = {'TEMPLATE_ID': '801',
                 'DOCUMENT_ID': ['crm', 'CCrmDocumentDeal', f'DEAL_{deal_id}'],
                 'PARAMETERS': {'source_reclamation': [source_text]}}

    res = BW.send_request('bizproc.workflow.start', params=params_bp)
    return bool(res)
